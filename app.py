from flask import Flask, request, render_template, jsonify, send_from_directory, send_file, session, url_for, redirect, flash
import os
import uuid
from werkzeug.utils import secure_filename
from utils.file_handler import FileHandler
from utils.pdf_operations import PDFOperations
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sorting-lock-toolkit-secret-key-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['PREVIEW_FOLDER'] = 'static/previews'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['PREVIEW_FOLDER'], exist_ok=True)

file_handler = FileHandler()
pdf_ops = PDFOperations()

@app.route('/')
def index():
    """Main page with sorting and lock tools"""
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
        
        result_path = None
        
        # Process operations
        try:
            if operation == 'sort':
                result_path = pdf_ops.sort_pdf_by_page_numbers(file_paths[0], session_id, pages)
                
            elif operation == 'protect':
                protection_options = {
                    'protection_password': request.form.get('protection_password', ''),
                    'confirm_password': request.form.get('confirm_password', ''),
                    'protection_level': request.form.get('protection_level', '128'),
                    'allow_printing': request.form.get('allow_printing') == 'true',
                    'allow_copying': request.form.get('allow_copying') == 'true',
                    'allow_modification': request.form.get('allow_modification') == 'true',
                    'allow_annotation': request.form.get('allow_annotation') == 'true',
                    'allow_form_filling': request.form.get('allow_form_filling') == 'true'
                }
                
                # Validate password
                if len(protection_options['protection_password']) < 6:
                    return jsonify({'success': False, 'error': 'ಪಾಸ್‌ವರ್ಡ್ ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳು ಇರಬೇಕು'})
                
                if protection_options['protection_password'] != protection_options['confirm_password']:
                    return jsonify({'success': False, 'error': 'ಪಾಸ್‌ವರ್ಡ್‌ಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ'})
                
                result = pdf_ops.protect_pdf(file_paths[0], session_id, protection_options)
                if result['success']:
                    result_path = result['output_path']
                    flash(result['message'], 'success')
                else:
                    return jsonify({'success': False, 'error': result['error']})
                
            elif operation == 'unlock':
                password = request.form.get('unlock_password', '')
                if not password:
                    return jsonify({'success': False, 'error': 'PDF ಅನ್‌ಲಾಕ್ ಮಾಡಲು ಪಾಸ್‌ವರ್ಡ್ ಅಗತ್ಯ'})
                
                result = pdf_ops.unlock_pdf(file_paths[0], session_id, password)
                if result['success']:
                    result_path = result['output_path']
                    flash(result['message'], 'success')
                else:
                    return jsonify({'success': False, 'error': result['error']})
                
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

@app.route('/check-encryption', methods=['POST'])
def check_encryption():
    """Check if uploaded PDF is password protected"""
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
        
        is_encrypted = pdf_ops.is_pdf_encrypted(temp_path)
        
        return jsonify({
            'success': True,
            'is_encrypted': is_encrypted,
            'message': 'PDF ಪಾಸ್‌ವರ್ಡ್ ರಕ್ಷಿತವಾಗಿದೆ' if is_encrypted else 'PDF ಪಾಸ್‌ವರ್ಡ್ ರಕ್ಷಿತವಾಗಿಲ್ಲ'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'ಎನ್‌ಕ್ರಿಪ್ಶನ್ ಪರಿಶೀಲನೆ ದೋಷ: {str(e)}'})

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
