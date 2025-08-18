from flask import Flask, request, render_template, jsonify, send_file, session, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from utils.file_handler import FileHandler
from utils.pdf_operations import PDFOperations
import config
import fitz  # PyMuPDF
from PIL import Image
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import traceback
import time
import os
import config

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')    

app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['PREVIEW_FOLDER'] = 'static/previews'
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['PREVIEW_FOLDER'], exist_ok=True)

file_handler = FileHandler()
pdf_ops = PDFOperations()

@app.route('/')
def index():
    # CRITICAL FIX: Clear session on main page load to ensure fresh start
    session.clear()
    return render_template('index.html')

@app.route('/generate-preview', methods=['POST'])
def generate_preview():
    """Generate page previews for PDF files"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'ಯಾವುದೇ ಫೈಲ್ ಕಳುಹಿಸಲಾಗಿಲ್ಲ'})
        
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'success': False, 'error': 'ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ'})
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'PDF ಫೈಲ್ ಮಾತ್ರ ಬೆಂಬಲಿತ'})
        
        # Generate session ID if not exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_id = session['session_id']
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(temp_path)
        
        # Generate page previews
        preview_data = pdf_ops.generate_page_previews(temp_path, session_id, app.config['PREVIEW_FOLDER'])
        
        if preview_data:
            # Convert file paths to URLs
            for preview in preview_data['previews']:
                preview_dir = f"previews/{session_id}"
                filename = f"page_{preview['page_num']}.png"
                preview['image_path'] = url_for('static', filename=f"{preview_dir}/{filename}")
            
            return jsonify({
                'success': True,
                'total_pages': preview_data['total_pages'],
                'previews': preview_data['previews']
            })
        else:
            return jsonify({'success': False, 'error': 'ಪೂರ್ವವೀಕ್ಷಣೆ ರಚನೆ ವಿಫಲವಾಗಿದೆ'})
            
    except Exception as e:
        print(f"Preview generation error: {str(e)}")
        return jsonify({'success': False, 'error': f'ಪೂರ್ವವೀಕ್ಷಣೆ ದೋಷ: {str(e)}'})

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # CRITICAL FIX: Always generate new session for each upload operation
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        session['processed_files'] = []  # Clear any previous files
        session.modified = True
        
        operation = request.form.get('operation')
        use_previous = request.form.get('use_previous') == 'true'
        
        print(f"=== DEBUG UPLOAD (NEW SESSION) ===")
        print(f"Operation: {operation}")
        print(f"New Session ID: {session_id}")
        print(f"Use previous: {use_previous}")
        print(f"Form data: {dict(request.form)}")
        
        # CRITICAL FIX: Never use previous files, always use fresh uploads
        files = request.files.getlist('files')
        if not files or all(not f.filename for f in files):
            return jsonify({'success': False, 'error': 'ಕನಿಷ್ಠ ಒಂದು ಫೈಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ'})
        
        file_paths = []
        
        for file in files:
            if file and file.filename:
                # ADD DEBUG PRINTS:
                print(f"=== FILENAME DEBUG ===")
                print(f"Original filename: '{file.filename}'")
                print(f"Original filename bytes: {file.filename.encode('utf-8')}")
                
                original_filename = secure_filename(file.filename)
                print(f"After secure_filename: '{original_filename}'")
                print(f"Has dot: {'.' in original_filename}")
                
                if not original_filename or '.' not in original_filename:
                    # If secure_filename stripped the extension, rebuild it
                    file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'docx'
                    original_filename = f"document.{file_ext}"
                    print(f"FIXED filename: '{original_filename}'")

                timestamp = str(int(time.time()))
                unique_filename = f"{session_id}_{timestamp}_{original_filename}"
                print(f"Final unique filename: '{unique_filename}'")
                print("=== END DEBUG ===")
                
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                try:
                    file.save(file_path)
                    print(f"Saved file: {file_path} (Size: {os.path.getsize(file_path)} bytes)")
                    
                    # Verify file was saved properly
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        file_paths.append(file_path)
                    else:
                        print(f"Warning: File save verification failed for {file_path}")
                        
                except Exception as save_error:
                    print(f"Error saving file {file.filename}: {save_error}")
                    continue
                finally:
                    # CRITICAL FIX: Properly close file stream
                    if hasattr(file, 'close'):
                        try:
                            file.close()
                        except:
                            pass
        
        if not file_paths:
            return jsonify({'success': False, 'error': 'ಯಾವುದೇ ಸರಿಯಾದ ಫೈಲ್‌ಗಳು ಅಪ್‌ಲೋಡ್ ಆಗಿಲ್ಲ'})
        
        # Get operation parameters
        pages = request.form.get('pages', '') or request.form.get('selected_pages', '')
        compression = request.form.get('compression', 'medium')
        
        # Get split-specific parameters
        split_method = request.form.get('split_method', 'pages')
        target_size_mb = request.form.get('target_size_mb', '10')
        pages_per_chunk = request.form.get('pages_per_chunk', '20')
        max_file_size = request.form.get('max_file_size', '1000')
        
        print(f"Processing {len(file_paths)} files for operation: {operation}")
        
        result_path = None
        
        # Process operations
        try:
            if operation == 'merge':
                print("Processing merge operation")
                result_path = pdf_ops.merge_pdfs(file_paths, session_id)
                
            elif operation == 'split':
                print("Processing split operation")
                if not file_paths:
                    return jsonify({'success': False, 'error': 'ವಿಭಜನೆಗಾಗಿ PDF ಫೈಲ್ ಅಗತ್ಯ'})
                
                # Validate PDF file exists and is readable
                pdf_path = file_paths[0]
                if not os.path.exists(pdf_path):
                    return jsonify({'success': False, 'error': 'PDF ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ'})
                
                # Check if PDF has multiple pages
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(pdf_path)
                    total_pages = len(reader.pages)
                    print(f"PDF has {total_pages} pages")
                    
                    if total_pages < 2:
                        return jsonify({'success': False, 'error': 'ವಿಭಜನೆಗೆ ಕನಿಷ್ಠ 2 ಪುಟಗಳು ಬೇಕಾಗುತ್ತವೆ'})
                        
                except Exception as pdf_error:
                    print(f"PDF validation error: {pdf_error}")
                    return jsonify({'success': False, 'error': f'PDF ಫೈಲ್ ದೋಷಪೂರ್ಣ: {str(pdf_error)}'})
                
                # Call split_pdf with proper parameters based on split method
                try:
                    target_size_mb_int = int(target_size_mb) if target_size_mb.isdigit() else 10
                    pages_per_chunk_int = int(pages_per_chunk) if pages_per_chunk.isdigit() else 20
                    max_file_size_int = int(max_file_size) if max_file_size.isdigit() else 1000
                except ValueError:
                    target_size_mb_int = 10
                    pages_per_chunk_int = 20
                    max_file_size_int = 1000
                
                result_path = pdf_ops.split_pdf(
                    pdf_path, 
                    session_id, 
                    pages=pages,
                    split_method=split_method,
                    target_size_mb=target_size_mb_int,
                    pages_per_chunk=pages_per_chunk_int,
                    max_file_size_mb=max_file_size_int
                )
                
            elif operation == 'extract':
                print("Processing extract operation")
                if not pages:
                    return jsonify({'success': False, 'error': 'ಹೊರತೆಗೆಯಲು ಪುಟ ಸಂಖ್ಯೆಗಳನ್ನು ನಮೂದಿಸಿ'})
                result_path = pdf_ops.extract_pages(file_paths[0], pages, session_id)

            elif operation == 'rotate':
                print("=== ROTATION OPERATION DEBUG ===")
                print(f"Raw form data: {dict(request.form)}")
                
                # Get and validate rotation parameters
                rotation_angle_raw = request.form.get('rotation_angle', '90')
                pages_param = request.form.get('pages', '')
                apply_to_all_raw = request.form.get('apply_to_all', 'false')
                
                print(f"rotation_angle (raw): '{rotation_angle_raw}' (type: {type(rotation_angle_raw)})")
                print(f"pages_param: '{pages_param}'")
                print(f"apply_to_all (raw): '{apply_to_all_raw}' (type: {type(apply_to_all_raw)})")
                
                # Convert and validate rotation angle
                try:
                    rotation_angle = int(rotation_angle_raw)
                    print(f"rotation_angle (converted): {rotation_angle} (type: {type(rotation_angle)})")
                except (ValueError, TypeError) as e:
                    print(f"Error converting rotation_angle: {e}")
                    rotation_angle = 90
                
                # Convert apply_to_all
                if isinstance(apply_to_all_raw, str):
                    apply_to_all = apply_to_all_raw.lower() in ['true', '1', 'yes', 'on']
                else:
                    apply_to_all = bool(apply_to_all_raw)
                
                print(f"apply_to_all (converted): {apply_to_all} (type: {type(apply_to_all)})")
                print(f"file_paths[0]: {file_paths[0] if file_paths else 'No files'}")
                print("=== CALLING ROTATE_PDF ===")
                
                result_path = pdf_ops.rotate_pdf(
                    file_paths[0], 
                    session_id, 
                    rotation_angle, 
                    pages_param, 
                    apply_to_all
                )
                
                print(f"Result path: {result_path}")
                print("=== ROTATION OPERATION COMPLETE ===")

            elif operation == 'delete':
                print("Processing delete operation")
                if not pages:
                    return jsonify({'success': False, 'error': 'ಅಳಿಸಲು ಪುಟ ಸಂಖ್ಯೆಗಳನ್ನು ನಮೂದಿಸಿ'})
                result_path = pdf_ops.delete_pages(file_paths[0], pages, session_id)
                
            elif operation == 'compress':
                print("Processing compress operation")
                result_path = pdf_ops.compress_pdf(file_paths[0], compression, session_id)
                
            elif operation == 'pdf_to_jpeg':
                print("Processing PDF to JPEG operation")
                result_path = pdf_ops.pdf_to_images(file_paths[0], session_id)
                
            elif operation == 'jpeg_to_pdf':
                print("Processing JPEG to PDF operation")
                result_path = pdf_ops.images_to_pdf(file_paths, session_id)
                
            elif operation == 'pdf_to_word':
                print("Processing PDF to Word operation")
                result_path = pdf_ops.pdf_to_word(file_paths[0], session_id)

            elif operation == 'word_to_pdf':
                print("=== PROCESSING WORD TO PDF OPERATION (FIXED) ===")
                print(f"File paths: {file_paths}")
                
                if not file_paths:
                    return jsonify({'success': False, 'error': 'Word ಫೈಲ್ ಅಗತ್ಯ'})
                
                word_file_path = file_paths[0]
                print(f"Processing Word file: {word_file_path}")
                
                # CRITICAL FIX: Validate file exists and has content
                if not os.path.exists(word_file_path):
                    return jsonify({'success': False, 'error': 'Word ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ'})
                
                file_size = os.path.getsize(word_file_path)
                if file_size == 0:
                    return jsonify({'success': False, 'error': 'ಖಾಲಿ Word ಫೈಲ್'})
                
                # Check file extension
                file_ext = os.path.splitext(word_file_path)[1].lower()
                if file_ext not in ['.doc', '.docx']:
                    return jsonify({'success': False, 'error': 'ಮಾನ್ಯವಾದ Word ಫೈಲ್ ಅಲ್ಲ (.doc ಅಥವಾ .docx ಬೇಕು)'})
                
                print(f"File validation passed - Extension: {file_ext}, Size: {file_size} bytes")
                
                # CRITICAL FIX: Call the conversion function with proper error handling
                try:
                    result_path = pdf_ops.word_to_pdf(word_file_path, session_id)
                    print(f"word_to_pdf returned: {result_path}")
                    
                    if result_path and os.path.exists(result_path):
                        result_size = os.path.getsize(result_path)
                        print(f"✓ Word to PDF conversion successful: {result_size} bytes")
                        
                        if result_size == 0:
                            print("✗ Result file is empty")
                            return jsonify({'success': False, 'error': 'ಪರಿವರ್ತನೆ ವಿಫಲ - ಖಾಲಿ PDF ರಚಿಸಲಾಗಿದೆ'})
                    else:
                        print("✗ Word to PDF conversion failed - no result file")
                        return jsonify({'success': False, 'error': 'Word to PDF ಪರಿವರ್ತನೆ ವಿಫಲವಾಗಿದೆ'})
                        
                except Exception as word_error:
                    print(f"✗ Word to PDF conversion error: {word_error}")
                    traceback.print_exc()
                    return jsonify({'success': False, 'error': f'Word to PDF ಪರಿವರ್ತನೆ ವಿಫಲ: {str(word_error)}'})
                
                print("=== WORD TO PDF OPERATION COMPLETE ===")
            
            else:
                return jsonify({'success': False, 'error': f'ಅಮಾನ್ಯ ಕಾರ್ಯಾಚರಣೆ: {operation}'})
                
        except Exception as op_error:
            print(f"Operation error: {str(op_error)}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'ಕಾರ್ಯಾಚರಣೆ ವಿಫಲ: {str(op_error)}'})
        
        # CRITICAL FIX: Clean up input files after successful processing
        try:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    try:
                        # Add small delay to ensure file handles are released
                        time.sleep(0.1)
                        os.remove(file_path)
                        print(f"Cleaned up input file: {file_path}")
                    except Exception as cleanup_error:
                        print(f"Warning: Could not clean up {file_path}: {cleanup_error}")
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")
        
        # Validate result
        if not result_path:
            return jsonify({'success': False, 'error': 'ಫೈಲ್ ಪ್ರಕ್ರಿಯೆ ವಿಫಲವಾಗಿದೆ - ಯಾವುದೇ ಫಲಿತಾಂಶ ಇಲ್ಲ'})
        
        if not os.path.exists(result_path):
            return jsonify({'success': False, 'error': f'ಫಲಿತಾಂಶ ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ: {result_path}'})
        
        result_size = os.path.getsize(result_path)
        if result_size == 0:
            return jsonify({'success': False, 'error': 'ಖಾಲಿ ಫೈಲ್ ರಚಿಸಲಾಗಿದೆ'})
        
        filename = os.path.basename(result_path)
        print(f"Success! Result file: {filename}, Size: {result_size} bytes")
        
        # Store result in session for potential chaining (but don't reuse)
        session['processed_files'] = [{
            'path': result_path,
            'filename': filename,
            'operation': operation
        }]
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'ಕಾರ್ಯಾಚರಣೆ ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ!',
            'download_url': f'/download/{session_id}/{filename}',
            'filename': filename,
            'can_chain': False  # CRITICAL FIX: Disable chaining to prevent reuse issues
        })

    except Exception as e:
        print(f"Upload error: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'ದೋಷ: {str(e)}'})

@app.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        print(f"Download request - Session: {session_id}, File: {filename}")
        print(f"Looking for file at: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path) and filename.startswith(session_id):
            print(f"Sending file: {file_path}, Size: {os.path.getsize(file_path)} bytes")
            return send_file(file_path, as_attachment=True, download_name=filename)
        
        print(f"File not found or invalid session")
        return jsonify({'error': 'ಫೈಲ್ ಸಿಗಲಿಲ್ಲ'}), 404
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset_session():
    """Reset session and clear processed files"""
    # CRITICAL FIX: Completely clear session and cleanup files
    old_session_id = session.get('session_id')
    
    # Clear all session data
    session.clear()
    
    # Generate new session ID
    session['session_id'] = str(uuid.uuid4())
    session['processed_files'] = []
    session.modified = True
    
    # Clean up old session files if they exist
    if old_session_id:
        cleanup_session_files(old_session_id)
    
    return jsonify({'success': True, 'message': 'ಅಧಿವೇಶನ ಮರುಹೊಂದಿಸಲಾಗಿದೆ'})

def cleanup_session_files(session_id):
    """Clean up all files associated with a session"""
    try:
        # Clean up preview files
        preview_dir = os.path.join(app.config['PREVIEW_FOLDER'], session_id)
        if os.path.exists(preview_dir):
            import shutil
            shutil.rmtree(preview_dir)
            print(f"Cleaned up preview directory: {preview_dir}")
        
        # Clean up uploaded files
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith(session_id):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    os.remove(file_path)
                    print(f"Cleaned up upload file: {file_path}")
                except Exception as e:
                    print(f"Could not remove upload file {file_path}: {e}")
        
        # Clean up output files for this session
        for filename in os.listdir(app.config['OUTPUT_FOLDER']):
            if filename.startswith(session_id):
                file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                try:
                    os.remove(file_path)
                    print(f"Cleaned up output file: {file_path}")
                except Exception as e:
                    print(f"Could not remove output file {file_path}: {e}")
        
    except Exception as e:
        print(f"Session cleanup error: {e}")

@app.route('/cleanup-session', methods=['POST'])
def cleanup_session():
    """Clean up session files and previews"""
    if 'session_id' not in session:
        return jsonify({'success': True})
    
    session_id = session['session_id']
    cleanup_session_files(session_id)
    
    return jsonify({'success': True})

@app.errorhandler(413)
def too_large(e):
    return jsonify({'success': False, 'error': 'ಫೈಲ್ ತುಂಬಾ ದೊಡ್ಡದಾಗಿದೆ. ಗರಿಷ್ಠ 100MB ಅನುಮತಿ'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'ವಿನಂತಿಸಿದ ಸಂಪನ್ಮೂಲ ಸಿಗಲಿಲ್ಲ'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'ಸರ್ವರ್ ದೋಷ ಸಂಭವಿಸಿದೆ'}), 500

# CRITICAL FIX: Enhanced cleanup function
def cleanup_old_files():
    """Clean up old files on server startup"""
    import time
    current_time = time.time()
    
    # Clean up files older than 1 hour (reduced from 24 hours)
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['PREVIEW_FOLDER']]:
        if not os.path.exists(folder):
            continue
            
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getctime(file_path) < current_time - 3600:  # 1 hour
                        os.remove(file_path)
                        print(f"Cleaned up old file: {file_path}")
                except Exception as e:
                    print(f"Could not clean up {file_path}: {e}")
                    continue
            
            # Remove empty directories
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        print(f"Removed empty directory: {dir_path}")
                except Exception as e:
                    print(f"Could not remove directory {dir_path}: {e}")
                    continue

if __name__ == '__main__':
    cleanup_old_files()
    app.run(debug=True)