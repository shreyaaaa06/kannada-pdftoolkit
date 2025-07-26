from flask import Flask, request, render_template, jsonify, send_file, session
import os
import uuid
import tempfile
import atexit
import threading
from werkzeug.utils import secure_filename
from utils.file_handler import FileHandler
from utils.pdf_operations import PDFOperations
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

file_handler = FileHandler()
pdf_ops = PDFOperations()

# FIXED: File cleanup system
def cleanup_old_files():
    """Clean up files older than 1 hour"""
    import time
    current_time = time.time()
    
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                # Delete files older than 1 hour
                if current_time - os.path.getctime(file_path) > 3600:
                    try:
                        os.remove(file_path)
                    except:
                        pass

def cleanup_session_files(session_id):
    """Clean up files for a specific session"""
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
        for filename in os.listdir(folder):
            if filename.startswith(session_id):
                try:
                    os.remove(os.path.join(folder, filename))
                except:
                    pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Generate session ID
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_id = session['session_id']
        operation = request.form.get('operation')
        
        # FIXED: Clean up previous session files first
        cleanup_session_files(session_id)
        
        # Get uploaded files
        files = request.files.getlist('files')
        
        if not operation:
            return jsonify({'success': False, 'error': 'ಕಾರ್ಯಾಚರಣೆ ಆಯ್ಕೆ ಮಾಡಿ'})
        
        if not files or all(not f.filename for f in files):
            return jsonify({'success': False, 'error': 'ಕನಿಷ್ಠ ಒಂದು ಫೈಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ'})
        
        # Save uploaded files
        file_paths = []
        for file in files:
            if file and file.filename:
                try:
                    file_path = file_handler.save_uploaded_file(file, session_id)
                    if file_path:
                        file_paths.append(file_path)
                except Exception as e:
                    print(f"Error saving file {file.filename}: {e}")
                    continue
        
        if not file_paths:
            return jsonify({'success': False, 'error': 'ಯಾವುದೇ ಸರಿಯಾದ ಫೈಲ್‌ಗಳು ಅಪ್‌ಲೋಡ್ ಆಗಿಲ್ಲ'})
        
        # Get operation parameters
        pages = request.form.get('pages', '')
        compression = request.form.get('compression', 'medium')
        
        # Process based on operation
        result_path = None
        
        try:
            if operation == 'merge':
                if len(file_paths) < 2:
                    return jsonify({'success': False, 'error': 'ವಿಲೀನಗೊಳಿಸಲು ಕನಿಷ್ಠ 2 PDF ಫೈಲ್‌ಗಳು ಬೇಕು'})
                result_path = pdf_ops.merge_pdfs(file_paths, session_id)
                
            elif operation == 'split':
                result_path = pdf_ops.split_pdf(file_paths[0], session_id, pages)
                
            elif operation == 'extract':
                if not pages:
                    return jsonify({'success': False, 'error': 'ಹೊರತೆಗೆಯಲು ಪುಟ ಸಂಖ್ಯೆಗಳನ್ನು ನೀಡಿ'})
                result_path = pdf_ops.extract_pages(file_paths[0], pages, session_id)
                
            elif operation == 'delete':
                if not pages:
                    return jsonify({'success': False, 'error': 'ಅಳಿಸಲು ಪುಟ ಸಂಖ್ಯೆಗಳನ್ನು ನೀಡಿ'})
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
            
            else:
                return jsonify({'success': False, 'error': 'ಅಮಾನ್ಯ ಕಾರ್ಯಾಚರಣೆ'})
        
        except Exception as e:
            print(f"Operation error: {e}")
            return jsonify({'success': False, 'error': f'ಕಾರ್ಯಾಚರಣೆ ವಿಫಲ: {str(e)}'})
        
        # FIXED: Clean up uploaded files after processing
        finally:
            for file_path in file_paths:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
        
        # Check if result file exists
        if result_path and os.path.exists(result_path):
            filename = os.path.basename(result_path)
            download_url = f'/download/{session_id}/{filename}'
            
            return jsonify({
                'success': True,
                'message': 'ಕಾರ್ಯಾಚರಣೆ ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ!',
                'download_url': download_url,
                'filename': filename
            })
        else:
            return jsonify({'success': False, 'error': 'ಫೈಲ್ ಪ್ರಕ್ರಿಯೆ ವಿಫಲವಾಗಿದೆ'})
            
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'success': False, 'error': f'ಅಪ್‌ಲೋಡ್ ದೋಷ: {str(e)}'})

@app.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path) and filename.startswith(session_id):
            # FIXED: Schedule file cleanup after download
            def cleanup_after_download():
                import time
                time.sleep(10)  # Wait 10 seconds after download
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
            
            # Start cleanup in background
            threading.Thread(target=cleanup_after_download).start()
            
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'ಫೈಲ್ ಸಿಗಲಿಲ್ಲ'}), 404
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({'error': str(e)}), 500

# FIXED: Add cleanup route for manual cleanup
@app.route('/cleanup', methods=['POST'])
def cleanup():
    try:
        session_id = session.get('session_id')
        if session_id:
            cleanup_session_files(session_id)
        return jsonify({'success': True})
    except:
        return jsonify({'success': False})

# FIXED: Periodic cleanup
import threading
import time

def periodic_cleanup():
    while True:
        time.sleep(1800)  # Run every 30 minutes
        cleanup_old_files()

# Start cleanup thread
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()

# Clean up on exit
atexit.register(cleanup_old_files)

if __name__ == '__main__':
    app.run(debug=True)