from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from utils.pdf_operations import PDFOperations
from utils.file_handler import FileHandler
from utils.validators import validate_file
from config import Config 

app = Flask(__name__)
app.config.from_object(Config) 

# Initialize utility classes
pdf_ops = PDFOperations()
file_handler = FileHandler()

@app.route('/')
def index():
    """Main page with all PDF operations"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file uploads"""
    if request.method == 'POST':
        operation = request.form.get('operation')
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            flash('ದಯವಿಟ್ಟು ಕನಿಷ್ಠ ಒಂದು ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ')  # Please select at least one file
            return redirect(url_for('index'))
        
        # Validate files
        valid_files = []
        for file in files:
            if validate_file(file, operation):
                valid_files.append(file)
        
        if not valid_files:
            flash('ಅಮಾನ್ಯ ಫೈಲ್ ಪ್ರಕಾರ')  # Invalid file type
            return redirect(url_for('index'))
        
        # Generate session ID for tracking
        session_id = str(uuid.uuid4())
        
        # Save uploaded files
        file_paths = []
        for file in valid_files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
            file.save(file_path)
            file_paths.append(file_path)
        
        # Process operation
        try:
            result = process_operation(operation, file_paths, request.form, session_id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': f'ಕಾರ್ಯಾಚರಣೆ ವಿಫಲವಾಗಿದೆ: {str(e)}'})
    
    return render_template('upload.html')

def process_operation(operation, file_paths, form_data, session_id):
    """Process the selected PDF operation"""
    
    operations = {
        'merge': pdf_ops.merge_pdfs,
        'split': pdf_ops.split_pdf,
        'extract': pdf_ops.extract_pages,
        'delete': pdf_ops.delete_pages,
        'crop': pdf_ops.crop_pages,
        'rotate': pdf_ops.rotate_pages,
        'pdf_to_word': pdf_ops.pdf_to_word,
        'word_to_pdf': pdf_ops.word_to_pdf,
        'pdf_to_jpeg': pdf_ops.pdf_to_jpeg,
        'jpeg_to_pdf': pdf_ops.jpeg_to_pdf,
        'compress': pdf_ops.compress_pdf
    }
    
    if operation not in operations:
        raise ValueError('ಅಮಾನ್ಯ ಕಾರ್ಯಾಚರಣೆ')  # Invalid operation
    
    # Prepare parameters based on operation
    params = {'files': file_paths, 'session_id': session_id}
    
    if operation in ['split', 'extract', 'delete']:
        pages = form_data.get('pages', '1')
        params['pages'] = pages
    
    if operation == 'rotate':
        angle = int(form_data.get('angle', 90))
        params['angle'] = angle
    
    if operation == 'crop':
        params.update({
            'left': float(form_data.get('left', 0)),
            'top': float(form_data.get('top', 0)),
            'right': float(form_data.get('right', 0)),
            'bottom': float(form_data.get('bottom', 0))
        })
    
    # Execute operation
    result_path = operations[operation](**params)
    
    # Generate download URL
    download_url = url_for('download_file', filename=os.path.basename(result_path))
    
    return {
        'success': True,
        'message': 'ಕಾರ್ಯಾಚರಣೆ ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ',  # Operation completed successfully
        'download_url': download_url,
        'filename': os.path.basename(result_path)
    }

@app.route('/download/<filename>')
def download_file(filename):
    """Handle file downloads"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ')  # File not found
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'ಡೌನ್‌ಲೋಡ್ ವಿಫಲವಾಗಿದೆ: {str(e)}')
        return redirect(url_for('index'))

@app.route('/api/progress/<session_id>')
def get_progress(session_id):
    """Get operation progress"""
    # This would connect to a progress tracking system
    # For now, returning a simple response
    return jsonify({'progress': 100, 'status': 'completed'})

@app.errorhandler(413)
def too_large(e):
    flash('ಫೈಲ್ ಗಾತ್ರ ತುಂಬಾ ದೊಡ್ಡದಾಗಿದೆ')  # File size too large
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# Cleanup function to remove old files
def cleanup_old_files():
    """Remove files older than 1 hour"""
    import time
    current_time = time.time()
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                if current_time - os.path.getctime(file_path) > 3600:  # 1 hour
                    os.remove(file_path)

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Start cleanup scheduler (in production, use Celery or similar)
    import threading
    import time
    
    def periodic_cleanup():
        while True:
            time.sleep(3600)  # Run every hour
            cleanup_old_files()
    
    cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
    cleanup_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)