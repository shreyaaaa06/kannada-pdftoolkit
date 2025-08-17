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
import sys
import html
from flask import redirect, url_for
from utils.pdf_compare import PDFCompare
import unicodedata
from flask import Response
import requests
from weasyprint import HTML, CSS
from flask import make_response
import json




# Add this line after creating other instances
pdf_compare = PDFCompare()

# Add this to your app.py after other directory creation
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set UTF-8 encoding for the entire application
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

app = Flask(__name__)
# Add this right after app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'



@app.after_request  
def after_request(response):
    """Ensure UTF-8 encoding for all responses"""
    if response.content_type:
        if 'charset' not in response.content_type:
            if 'text/html' in response.content_type:
                response.content_type = 'text/html; charset=utf-8'
            elif 'application/json' in response.content_type:
                response.content_type = 'application/json; charset=utf-8'
    return response
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['PREVIEW_FOLDER'] = 'static/previews'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024



# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['PREVIEW_FOLDER'], exist_ok=True)
# Create temporary directory for comparison images
app.config['TEMP_FOLDER'] = 'static/temp'
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
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
        
        print(f"Pages parameter: '{pages}'")
        print(f"Compression: {compression}")
        
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
                
                result_path = pdf_ops.split_pdf(pdf_path, session_id, pages)
                
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
                
            # Replace your compression section in app.py with this:

            elif operation == 'compress':
                print("Processing compress operation")
                
                # Get compression parameters
                compression_level = request.form.get('compression', 'medium')
                target_size_mb = request.form.get('target_size_mb')
                
                # Convert target size to float if provided
                target_size = None
                if target_size_mb and target_size_mb.strip():
                    try:
                        target_size = float(target_size_mb)
                        print(f"Target size specified: {target_size}MB")
                    except (ValueError, TypeError):
                        target_size = None
                        print("Invalid target size, ignoring")
                
                # Get advanced options if provided
                image_quality = request.form.get('imageQuality')  # Note: matching HTML id
                image_dpi = request.form.get('imageDPI')
                remove_metadata = request.form.get('removeMetadata') == 'on'
                optimize_fonts = request.form.get('optimizeFonts') == 'on'
                
                # Convert string parameters to integers if provided and valid
                quality = None
                dpi = None
                
                if image_quality and image_quality.strip():
                    try:
                        quality = int(image_quality)
                        quality = max(10, min(100, quality))  # Clamp between 10-100
                        print(f"Image quality: {quality}")
                    except (ValueError, TypeError):
                        print("Invalid image quality, using default")
                
                if image_dpi and image_dpi.strip():
                    try:
                        dpi = int(image_dpi)
                        dpi = max(50, min(600, dpi))  # Clamp between 50-600
                        print(f"Image DPI: {dpi}")
                    except (ValueError, TypeError):
                        print("Invalid image DPI, using default")
                
                print(f"Compression settings: level={compression_level}, target={target_size}MB")
                print(f"Advanced options: quality={quality}, dpi={dpi}, remove_metadata={remove_metadata}, optimize_fonts={optimize_fonts}")
                
                # Use the enhanced compression method
                result_path = pdf_ops.compress_pdf_enhanced(
                    file_paths[0], 
                    compression_level, 
                    session_id,
                    target_size_mb=target_size,
                    image_quality=quality,
                    image_dpi=dpi,
                    remove_metadata=remove_metadata,
                    optimize_fonts=optimize_fonts
                )
                
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
            elif operation == 'compare':
                print("Processing compare operation")
                if len(file_paths) != 2:
                    return jsonify({'success': False, 'error': 'ಹೋಲಿಕೆಗಾಗಿ ನಿಖರವಾಗಿ 2 PDF ಫೈಲ್‌ಗಳು ಬೇಕು'})
                
                session.pop('comparison_data', None)
                session.pop('comparison_report_url', None)
                compare_type ='both'
                
                # CRITICAL FIX: Maintain upload order - don't sort by size
                # file_paths[0] should always be the first uploaded file (left side)
                # file_paths[1] should always be the second uploaded file (right side)
                pdf1_path = file_paths[0]  # First uploaded file - LEFT side
                pdf2_path = file_paths[1]  # Second uploaded file - RIGHT side
                
                print(f"Comparing: {pdf1_path} (LEFT) vs {pdf2_path} (RIGHT)")
                
                # Use the dedicated comparison class with maintained order
                comparison_results = pdf_compare.compare_pdfs_web(pdf1_path, pdf2_path, session_id, compare_type)
                
                if not comparison_results:
                    return jsonify({'success': False, 'error': 'ಹೋಲಿಕೆ ವಿಫಲವಾಗಿದೆ'})
                
                # Store comparison data in session for the results page
                session['comparison_summary'] = {
                    'file1_name': comparison_results['file1_name'],
                    'file2_name': comparison_results['file2_name'],
                    'file1_pages': comparison_results['file1_pages'],
                    'file2_pages': comparison_results['file2_pages'],
                    'total_text_changes': comparison_results['summary']['total_text_changes'],
                    'visual_diff_pages': comparison_results['summary']['visual_diff_pages'],
                    'session_id': session_id
                }

                # SAVE FULL DATA TO FILE INSTEAD OF SESSION
                import json
                comparison_file = os.path.join(app.config['OUTPUT_FOLDER'], f'{session_id}_comparison.json')
                with open(comparison_file, 'w', encoding='utf-8') as f:
                    json.dump(comparison_results, f, ensure_ascii=False, indent=2)

                session['comparison_report_url'] = comparison_results.get('report_path', '')
                session.modified = True

                # Return success with redirect to results page
                return jsonify({
                    'success': True,
                    'message': 'ಹೋಲಿಕೆ ಪೂರ್ಣಗೊಂಡಿದೆ!',
                    'redirect_url': '/compare-result',
                    'comparison_data': comparison_results
                })
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

@app.route('/process', methods=['POST'])
def process_files():
    """Alternative endpoint for processing files (matches main.js expectations)"""
    return upload_file()

@app.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        print(f"Download request - Session: {session_id}, File: {filename}")
        print(f"Looking for file at: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")

        if os.path.exists(file_path):
            # Serve HTML in-browser
            if filename.endswith('.html'):
                return send_file(file_path)
            else:
                return send_file(file_path, as_attachment=True, download_name=filename)

        print("File not found")
        return "ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ", 404

    except Exception as e:
        print(f"Download error: {str(e)}")
        return f"ದೋಷ: {str(e)}", 500

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

@app.route('/compare', methods=['POST'])
def compare_pdfs():
    try:
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({'error': 'ಎರಡು ಫೈಲ್‌ಗಳು ಅಗತ್ಯ'}), 400
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1.filename == '' or file2.filename == '':
            return jsonify({'error': 'ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ'}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Save uploaded files
        # Save uploaded files with identifiable names
        file1_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_file1_{file1.filename}")
        file2_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_file2_{file2.filename}")
        
        file1.save(file1_path)
        file2.save(file2_path)
        # Generate preview images for both PDFs
        preview_folder = app.config['PREVIEW_FOLDER']
        pdf_ops.generate_page_previews(file1_path, session_id, preview_folder)
        pdf_ops.generate_page_previews(file2_path, session_id, preview_folder)
        
        # Compare PDFs
        from utils.pdf_compare import PDFCompare
        pdf_compare = PDFCompare()
        
        comparison_data = pdf_compare.compare_pdfs_web(
            file1_path, file2_path, session_id, 'both'
        )
        
        if not comparison_data:
            return jsonify({'error': 'ಹೋಲಿಕೆ ವಿಫಲವಾಗಿದೆ'}), 500
        
        # Store session data
        session['comparison_data'] = comparison_data
        session['session_id'] = session_id
        
        # Redirect to the result page instead of rendering directly
        return redirect(url_for('compare_result'))
        
    except Exception as e:
        print(f"Compare error: {e}")
        return jsonify({'error': f'ದೋಷ: {str(e)}'}), 500
@app.route('/compare-result')
def compare_result():
    try:
        if 'session_id' not in session:
            return redirect(url_for('index'))
        
        session_id = session['session_id']
        
        # LOAD COMPARISON DATA FROM FILE INSTEAD OF SESSION
        comparison_file = os.path.join(app.config['OUTPUT_FOLDER'], f'{session_id}_comparison.json')
        
        if not os.path.exists(comparison_file):
            return redirect(url_for('index'))
        
        with open(comparison_file, 'r', encoding='utf-8') as f:
            comparison_data = json.load(f)
        
        # Rest of your existing code...
        def ensure_utf8(obj):
            if isinstance(obj, dict):
                return {k: ensure_utf8(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [ensure_utf8(item) for item in obj]
            elif isinstance(obj, str):
                return unicodedata.normalize('NFC', obj)
            else:
                return obj
        
        comparison_data = ensure_utf8(comparison_data)
        
        response = make_response(render_template('compare_result.html', 
                                               comparison_data=comparison_data))
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
        
    except Exception as e:
        print(f"Compare result error: {e}")
        return redirect(url_for('index'))

def generate_page_image(pdf_path, session_id, file_num, page_num):
    """Generate page image from PDF"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]  # PDF pages are 0-indexed
        
        # Generate high-quality image
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        
        # Save image
        output_dir = f"static/temp/{session_id}"
        os.makedirs(output_dir, exist_ok=True)
        image_path = os.path.join(output_dir, f"page_{page_num}_{file_num}.png")
        
        pix.save(image_path)
        doc.close()
        
        return image_path
    except Exception as e:
        print(f"Image generation error: {e}")
        return None 
@app.route('/pdf-page/<session_id>/<file_num>/<int:page_num>')
def serve_pdf_page(session_id, file_num, page_num):
    try:
        import glob
        
        # Find the uploaded PDF file
        if file_num == 'file1':
            file_pattern = f"{session_id}_file1_*"
        else:  # file2
            file_pattern = f"{session_id}_file2_*"
        
        matching_files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], file_pattern))
        
        if not matching_files:
            return "PDF file not found", 404
            
        pdf_path = matching_files[0]
        
        # Generate or get existing page image
        image_path = generate_page_image(pdf_path, session_id, file_num, page_num)
        
        if image_path and os.path.exists(image_path):
            return send_file(image_path)
        else:
            return "Page image not found", 404
            
    except Exception as e:
        print(f"Error serving page: {e}")
        return "Error", 500
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