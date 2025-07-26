from flask import Flask, request, render_template, jsonify, send_file, session
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
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

file_handler = FileHandler()
pdf_ops = PDFOperations()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_id = session['session_id']
        operation = request.form.get('operation')
        files = request.files.getlist('files')
        
        if not files or not operation:
            return jsonify({'success': False, 'error': 'ಫೈಲ್‌ಗಳು ಅಥವಾ ಕಾರ್ಯಾಚರಣೆ ಕಾಣೆಯಾಗಿದೆ'})
        
        # Save uploaded files
        file_paths = []
        for file in files:
            if file and file.filename:
                file_path = file_handler.save_uploaded_file(file, session_id)
                if file_path:
                    file_paths.append(file_path)
        
        if not file_paths:
            return jsonify({'success': False, 'error': 'ಯಾವುದೇ ಸರಿಯಾದ ಫೈಲ್‌ಗಳು ಅಪ್‌ಲೋಡ್ ಆಗಿಲ್ಲ'})
        
        # Get operation parameters
        pages = request.form.get('pages', '')
        compression = request.form.get('compression', 'medium')
        
        # Process based on operation
        result_path = None
        
        if operation == 'merge':
            result_path = pdf_ops.merge_pdfs(file_paths, session_id)
            
        elif operation == 'split':
            result_path = pdf_ops.split_pdf(file_paths[0], session_id, pages)
            
        elif operation == 'extract':
            result_path = pdf_ops.extract_pages(file_paths[0], pages, session_id)
            
        elif operation == 'delete':
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
        return jsonify({'success': False, 'error': f'ದೋಷ: {str(e)}'})

@app.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path) and filename.startswith(session_id):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'ಫೈಲ್ ಸಿಗಲಿಲ್ಲ'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)