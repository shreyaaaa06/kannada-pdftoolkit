from flask import Flask, request, render_template, jsonify, send_from_directory, send_file, session, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from utils.file_handler import FileHandler
from utils.pdf_operations import PDFOperations
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['PREVIEW_FOLDER'] = 'static/previews'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['PREVIEW_FOLDER'], exist_ok=True)

file_handler = FileHandler()
pdf_ops = PDFOperations()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content response for favicon

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
        
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_id = session['session_id']
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(temp_path)
        
        preview_data = pdf_ops.get_page_sorting_preview(temp_path, session_id)
        
        if preview_data:
            for preview in preview_data['previews']:
                if preview.get('thumbnail_path'):
                    preview['image_path'] = preview['thumbnail_path']
                else:
                    preview['image_path'] = None
            
            return jsonify({
                'success': True,
                'total_pages': preview_data['total_pages'],
                'previews': preview_data['previews']
            })
        else:
            return jsonify({'success': False, 'error': 'ಪೂರ್ವವೀಕ್ಷಣೆ ರಚನೆ ವಿಫಲವಾಗಿದೆ'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'ಪೂರ್ವವೀಕ್ಷಣೆ ದೋಷ: {str(e)}'})

@app.route('/generate-sort-preview', methods=['POST'])
def generate_sort_preview():
    """Generate sorting preview showing how pages will be sorted by number"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'ಯಾವುದೇ ಫೈಲ್ ಕಳುಹಿಸಲಾಗಿಲ್ಲ'})
        
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'success': False, 'error': 'ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ'})
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'PDF ಫೈಲ್ ಮಾತ್ರ ಬೆಂಬಲಿತ'})
        
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_id = session['session_id']
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(temp_path)
        
        preview_data = pdf_ops.get_page_sorting_preview(temp_path, session_id)
        
        if preview_data and 'error' not in preview_data:
            return jsonify({
                'success': True,
                'total_pages': preview_data['total_pages'],
                'previews': preview_data['previews'],
                'sorted_order': preview_data['sorted_order']
            })
        else:
            error_msg = preview_data.get('error', 'ಸಾರಿಸುವ ಪೂರ್ವವೀಕ್ಷಣೆ ರಚನೆ ವಿಫಲವಾಗಿದೆ')
            return jsonify({'success': False, 'error': error_msg})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'ಸಾರಿಸುವ ಪೂರ್ವವೀಕ್ಷಣೆ ದೋಷ: {str(e)}'})



@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
            session['processed_files'] = []
        
        session_id = session['session_id']
        operation = request.form.get('operation')
        use_previous = request.form.get('use_previous') == 'true'
        
        # Get files - from upload or previous results
        if use_previous and session.get('processed_files'):
            file_paths = [f['path'] for f in session['processed_files']]
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
        
        if not file_paths:
            return jsonify({'success': False, 'error': 'ಯಾವುದೇ ಸರಿಯಾದ ಫೈಲ್‌ಗಳು ಅಪ್‌ಲೋಡ್ ಆಗಿಲ್ಲ'})
        
        # Get operation parameters
        pages = request.form.get('pages', '') or request.form.get('selected_pages', '')
        compression = request.form.get('compression', 'medium')
        
        result_path = None
        
        # Process operations
        try:
            if operation == 'merge':
                result_path = pdf_ops.merge_pdfs(file_paths, session_id)
                
            elif operation == 'split':
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
                    
                    if total_pages < 2:
                        return jsonify({'success': False, 'error': 'ವಿಭಜನೆಗೆ ಕನಿಷ್ಠ 2 ಪುಟಗಳು ಬೇಕಾಗುತ್ತವೆ'})
                        
                except Exception as pdf_error:
                    return jsonify({'success': False, 'error': f'PDF ಫೈಲ್ ದೋಷಪೂರ್ಣ: {str(pdf_error)}'})
                
                result_path = pdf_ops.split_pdf(pdf_path, session_id, pages)
                
            elif operation == 'extract':
                if not pages:
                    return jsonify({'success': False, 'error': 'ಹೊರತೆಗೆಯಲು ಪುಟ ಸಂಖ್ಯೆಗಳನ್ನು ನಮೂದಿಸಿ'})
                result_path = pdf_ops.extract_pages(file_paths[0], pages, session_id)
                
            elif operation == 'delete':
                if not pages:
                    return jsonify({'success': False, 'error': 'ಅಳಿಸಲು ಪುಟ ಸಂಖ್ಯೆಗಳನ್ನು ನಮೂದಿಸಿ'})
                result_path = pdf_ops.delete_pages(file_paths[0], pages, session_id)
                
            elif operation == 'compress':
                result_path = pdf_ops.compress_pdf(file_paths[0], compression, session_id)
                
            elif operation == 'pdf_to_jpeg':
                result_path = pdf_ops.pdf_to_images(file_paths[0], session_id)
                
            elif operation == 'jpeg_to_pdf':
                result_path = pdf_ops.images_to_pdf(file_paths, session_id)
                
            elif operation == 'pdf_to_word':
                result_path = pdf_ops.pdf_to_word(file_paths[0], session_id)
                
            elif operation == 'word_to_pdf':
                result_path = pdf_ops.word_to_pdf(file_paths[0], session_id)
                
            elif operation == 'sort':
                result_path = pdf_ops.sort_pdf_by_page_numbers(file_paths[0], session_id, pages)
                
            elif operation == 'watermark':
                from utils.validators import validate_watermark_options
                
                watermark_options = {
                    'type': 'text' if request.form.get('watermark_text', '').strip() else 'image',
                    'text': request.form.get('watermark_text', ''),
                    'font_family': request.form.get('font_family', 'Helvetica'),
                    'font_size': int(request.form.get('font_size', 50)),
                    'color': request.form.get('font_color', '#000000'),
                    'opacity': float(request.form.get('opacity', 50)),
                    'rotation': float(request.form.get('rotation', 0)),
                    'position': request.form.get('position', 'center'),
                    'custom_x': request.form.get('custom_x'),
                    'custom_y': request.form.get('custom_y'),
                    'pages': request.form.get('selected_pages', 'all'),
                    'behind_content': request.form.get('layer_position', 'below') == 'below',
                    'repeat': request.form.get('repeat_watermark', 'false') == 'true',
                    'scale': float(request.form.get('scale', 20)) / 100.0
                }
                
                if not watermark_options['text'].strip() and watermark_options['type'] == 'text':
                    watermark_options['text'] = 'ವಾಟರ್‌ಮಾರ್ಕ್'
                
                if watermark_options['pages'] == 'custom':
                    custom_pages = request.form.get('custom_pages', '').strip()
                    if custom_pages:
                        watermark_options['pages'] = custom_pages
                    else:
                        return jsonify({'success': False, 'error': 'ನಿರ್ದಿಷ್ಟ ಪುಟ ಸಂಖ್ಯೆಗಳು ಅಗತ್ಯ'})
                
                if watermark_options['type'] == 'image':
                    if 'watermark_image' in request.files:
                        watermark_file = request.files['watermark_image']
                        if watermark_file and watermark_file.filename:
                            watermark_filename = secure_filename(watermark_file.filename)
                            watermark_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_watermark_{watermark_filename}")
                            watermark_file.save(watermark_path)
                            watermark_options['image_path'] = watermark_path
                        else:
                            return jsonify({'success': False, 'error': 'ವಾಟರ್‌ಮಾರ್ಕ್ ಚಿತ್ರ ಅಗತ್ಯ'})
                    else:
                        return jsonify({'success': False, 'error': 'ವಾಟರ್‌ಮಾರ್ಕ್ ಚಿತ್ರ ಅಗತ್ಯ'})
                
                is_valid, validation_message = validate_watermark_options(watermark_options)
                if not is_valid:
                    return jsonify({'success': False, 'error': f'ವಾಟರ್‌ಮಾರ್ಕ್ ಸೆಟ್ಟಿಂಗ್ ದೋಷ: {validation_message}'})
                
                result_path = pdf_ops.add_watermark(file_paths[0], session_id, watermark_options)
                
            else:
                return jsonify({'success': False, 'error': f'ಅಮಾನ್ಯ ಕಾರ್ಯಾಚರಣೆ: {operation}'})
                
        except Exception as op_error:
            return jsonify({'success': False, 'error': f'ಕಾರ್ಯಾಚರಣೆ ವಿಫಲ: {str(op_error)}'})
        
        if not result_path:
            return jsonify({'success': False, 'error': 'ಫೈಲ್ ಪ್ರಕ್ರಿಯೆ ವಿಫಲವಾಗಿದೆ - ಯಾವುದೇ ಫಲಿತಾಂಶ ಇಲ್ಲ'})
        
        if not os.path.exists(result_path):
            return jsonify({'success': False, 'error': f'ಫಲಿತಾಂಶ ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ: {result_path}'})
        
        if os.path.getsize(result_path) == 0:
            return jsonify({'success': False, 'error': 'ಖಾಲಿ ಫೈಲ್ ರಚಿಸಲಾಗಿದೆ'})
        
        filename = os.path.basename(result_path)
        
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
        return jsonify({'success': False, 'error': f'ದೋಷ: {str(e)}'})

@app.route('/process', methods=['POST'])
def process_files():
    """Alternative endpoint for processing files (matches main.js expectations)"""
    return upload_file()

@app.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        if os.path.exists(file_path) and filename.startswith(session_id):
            return send_file(file_path, as_attachment=True, download_name=filename)
        
        return jsonify({'error': 'ಫೈಲ್ ಸಿಗಲಿಲ್ಲ'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/thumbnails/<session_id>/<filename>')
def serve_thumbnail(session_id, filename):
    """Serve thumbnail images for PDF page previews"""
    try:
        thumbnails_dir = os.path.join(app.config['OUTPUT_FOLDER'], 'thumbnails', session_id)
        file_path = os.path.join(thumbnails_dir, filename)
        
        if os.path.exists(file_path):
            response = send_file(file_path, mimetype='image/png')
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        else:
            return jsonify({'error': 'ಥಮ್‌ನೇಲ್ ಸಿಗಲಿಲ್ಲ'}), 404
            
    except Exception as e:
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

