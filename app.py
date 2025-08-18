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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['PREVIEW_FOLDER'] = 'static/previews'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  #1GB

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['PREVIEW_FOLDER'], exist_ok=True)

file_handler = FileHandler()
pdf_ops = PDFOperations()

@app.route('/')
def index():
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
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            session['processed_files'] = []
        
        session_id = session['session_id']
        operation = request.form.get('operation')
        use_previous = request.form.get('use_previous') == 'true'
        
        print(f"=== DEBUG UPLOAD ===")
        print(f"Operation: {operation}")
        print(f"Session ID: {session_id}")
        print(f"Use previous: {use_previous}")
        print(f"Form data: {dict(request.form)}")
        
        # Get files - from upload or previous results
        if use_previous and session.get('processed_files'):
            file_paths = [f['path'] for f in session['processed_files']]
            print(f"Using previous files: {file_paths}")
        else:
            files = request.files.getlist('files')
            if not files or all(not f.filename for f in files):
                return jsonify({'success': False, 'error': 'ಕನಿಷ್ಠ ಒಂದು ಫೈಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ'})
            
            file_paths = []
            for file in files:
                if file and file.filename:
                    file_path = file_handler.save_uploaded_file(file, session_id)
                    if file_path:
                        file_paths.append(file_path)
                        print(f"Saved file: {file_path}")
        
        if not file_paths:
            return jsonify({'success': False, 'error': 'ಯಾವುದೇ ಸರಿಯಾದ ಫೈಲ್‌ಗಳು ಅಪ್‌ಲೋಡ್ ಆಗಿಲ್ಲ'})
        
        # Get operation parameters
        pages = request.form.get('pages', '') or request.form.get('selected_pages', '')
        compression = request.form.get('compression', 'medium')
        
        # NEW: Get split-specific parameters
        split_method = request.form.get('split_method', 'pages')
        target_size_mb = request.form.get('target_size_mb', '10')
        pages_per_chunk = request.form.get('pages_per_chunk', '20')
        max_file_size = request.form.get('max_file_size', '100')
        
        print(f"Pages parameter: '{pages}'")
        print(f"Compression: {compression}")
        print(f"Split method: {split_method}")
        print(f"Target size MB: {target_size_mb}")
        print(f"Pages per chunk: {pages_per_chunk}")
        print(f"Max file size: {max_file_size}")
        
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
                
                # FIXED: Call split_pdf with proper parameters based on split method
                try:
                    target_size_mb_int = int(target_size_mb) if target_size_mb.isdigit() else 10
                    pages_per_chunk_int = int(pages_per_chunk) if pages_per_chunk.isdigit() else 20
                    max_file_size_int = int(max_file_size) if max_file_size.isdigit() else 100
                except ValueError:
                    target_size_mb_int = 10
                    pages_per_chunk_int = 20
                    max_file_size_int = 100
                
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
                print("Processing Word to PDF operation")
                result_path = pdf_ops.word_to_pdf(file_paths[0], session_id)
                
            else:
                return jsonify({'success': False, 'error': f'ಅಮಾನ್ಯ ಕಾರ್ಯಾಚರಣೆ: {operation}'})
                
        except Exception as op_error:
            print(f"Operation error: {str(op_error)}")
            return jsonify({'success': False, 'error': f'ಕಾರ್ಯಾಚರಣೆ ವಿಫಲ: {str(op_error)}'})
        
        # Validate result
        if not result_path:
            return jsonify({'success': False, 'error': 'ಫೈಲ್ ಪ್ರಕ್ರಿಯೆ ವಿಫಲವಾಗಿದೆ - ಯಾವುದೇ ಫಲಿತಾಂಶ ಇಲ್ಲ'})
        
        if not os.path.exists(result_path):
            return jsonify({'success': False, 'error': f'ಫಲಿತಾಂಶ ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ: {result_path}'})
        
        if os.path.getsize(result_path) == 0:
            return jsonify({'success': False, 'error': 'ಖಾಲಿ ಫೈಲ್ ರಚಿಸಲಾಗಿದೆ'})
        
        filename = os.path.basename(result_path)
        print(f"Success! Result file: {filename}, Size: {os.path.getsize(result_path)} bytes")
        
        # Store result in session for chaining
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
            'can_chain': True
        })
            
    except Exception as e:
        print(f"Upload error: {str(e)}")
        import traceback
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
    session.pop('processed_files', None)
    
    # Optional: Clean up old preview files for this session
    if 'session_id' in session:
        session_id = session['session_id']
        try:
            preview_dir = os.path.join(app.config['PREVIEW_FOLDER'], session_id)
            if os.path.exists(preview_dir):
                import shutil
                shutil.rmtree(preview_dir)
        except Exception as e:
            pass  # Ignore cleanup errors
    
    return jsonify({'success': True})

@app.route('/cleanup-session', methods=['POST'])
def cleanup_session():
    """Clean up session files and previews"""
    if 'session_id' not in session:
        return jsonify({'success': True})
    
    session_id = session['session_id']
    
    try:
        # Clean up preview files
        preview_dir = os.path.join(app.config['PREVIEW_FOLDER'], session_id)
        if os.path.exists(preview_dir):
            import shutil
            shutil.rmtree(preview_dir)
        
        # Clean up uploaded files
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith(session_id):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    os.remove(file_path)
                except:
                    pass
        
        # Clean up output files older than current session
        for filename in os.listdir(app.config['OUTPUT_FOLDER']):
            if filename.startswith(session_id):
                file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                try:
                    # Keep recent files, remove older ones
                    import time
                    if os.path.getctime(file_path) < time.time() - 3600:  # 1 hour old
                        os.remove(file_path)
                except:
                    pass
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.errorhandler(413)
def too_large(e):
    return jsonify({'success': False, 'error': 'ಫೈಲ್ ತುಂಬಾ ದೊಡ್ಡದಾಗಿದೆ. ಗರಿಷ್ಠ 100MB ಅನುಮತಿ'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'ವಿನಂತಿಸಿದ ಸಂಪನ್ಮೂಲ ಸಿಗಲಿಲ್ಲ'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'ಸರ್ವರ್ ದೋಷ ಸಂಭವಿಸಿದೆ'}), 500

# Cleanup old files on startup
def cleanup_old_files():
    """Clean up old files on server startup"""
    import time
    current_time = time.time()
    
    # Clean up files older than 24 hours
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['PREVIEW_FOLDER']]:
        if not os.path.exists(folder):
            continue
            
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getctime(file_path) < current_time - 86400:  # 24 hours
                        os.remove(file_path)
                except:
                    continue
            
            # Remove empty directories
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                except:
                    continue

if __name__ == '__main__':
    cleanup_old_files()
    app.run(debug=True)