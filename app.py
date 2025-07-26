from flask import Flask, render_template, request, send_file, jsonify, session, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter
import zipfile

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Ensure directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('output', exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        session_id = str(uuid.uuid4())[:8]
        operation = request.form.get('operation')
        files = request.files.getlist('files')
        
        if not operation:
            return jsonify({'success': False, 'error': 'ಕಾರ್ಯಾಚರಣೆ ಆಯ್ಕೆ ಮಾಡಿ'})
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({'success': False, 'error': 'ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ'})
        
        # Save uploaded files
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = f"uploads/{session_id}_{filename}"
                file.save(file_path)
                saved_files.append(file_path)
        
        if not saved_files:
            return jsonify({'success': False, 'error': 'ಯಾವುದೇ ಮಾನ್ಯ ಫೈಲ್‌ಗಳು ಕಂಡುಬಂದಿಲ್ಲ'})
        
        # Process files
        result_file = process_pdf(operation, saved_files, session_id, request.form)
        
        if result_file and os.path.exists(result_file):
            # Store in session for download
            session[f'file_{session_id}'] = result_file
            
            # Return success response
            return jsonify({
                'success': True,
                'message': 'ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ',
                'filename': os.path.basename(result_file),
                'download_url': f'/download/{session_id}',
                'session_id': session_id
            })
        else:
            return jsonify({'success': False, 'error': 'ಸಂಸ್ಕರಣೆಯಲ್ಲಿ ದೋಷ'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'ದೋಷ: {str(e)}'})
    finally:
        # Clean up uploaded files
        for f in saved_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

def process_pdf(operation, files, session_id, form_data):
    if operation == 'merge':
        writer = PdfWriter()
        for file_path in files:
            reader = PdfReader(file_path)
            for page in reader.pages:
                writer.add_page(page)
        
        output_path = f"output/{session_id}_merged.pdf"
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        return output_path
    
    elif operation == 'split':
        reader = PdfReader(files[0])
        pages = form_data.get('pages', '1-2').replace(' ', '').split(',')
        output_files = []
        
        for i, page_range in enumerate(pages):
            writer = PdfWriter()
            try:
                if '-' in page_range:
                    start, end = map(int, page_range.split('-'))
                    for p in range(start-1, min(end, len(reader.pages))):
                        if 0 <= p < len(reader.pages):
                            writer.add_page(reader.pages[p])
                else:
                    p = int(page_range) - 1
                    if 0 <= p < len(reader.pages):
                        writer.add_page(reader.pages[p])
                
                if len(writer.pages) > 0:  # Only save if has pages
                    output_path = f"output/{session_id}_split_{i+1}.pdf"
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    output_files.append(output_path)
            except ValueError:
                continue  # Skip invalid page numbers
        
        # Create zip if multiple files
        if len(output_files) > 1:
            zip_path = f"output/{session_id}_split.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in output_files:
                    zipf.write(file_path, os.path.basename(file_path))
                    os.remove(file_path)
            return zip_path
        return output_files[0] if output_files else None
    
    elif operation == 'extract':
        reader = PdfReader(files[0])
        writer = PdfWriter()
        pages_str = form_data.get('pages', '1').replace(' ', '')
        
        # Parse pages (supports ranges like 1-3,5,7-9)
        page_numbers = []
        for part in pages_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                page_numbers.extend(range(start-1, min(end, len(reader.pages))))
            else:
                page_numbers.append(int(part) - 1)
        
        for page_num in page_numbers:
            if 0 <= page_num < len(reader.pages):
                writer.add_page(reader.pages[page_num])
        
        output_path = f"output/{session_id}_extracted.pdf"
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        return output_path
    
    elif operation == 'delete':
        reader = PdfReader(files[0])
        writer = PdfWriter()
        pages_to_delete = set()
        pages_str = form_data.get('pages', '').replace(' ', '')
        
        # Parse pages to delete
        for part in pages_str.split(','):
            if part:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    pages_to_delete.update(range(start-1, min(end, len(reader.pages))))
                else:
                    pages_to_delete.add(int(part) - 1)
        
        # Add pages that are NOT in delete list
        for i, page in enumerate(reader.pages):
            if i not in pages_to_delete:
                writer.add_page(page)
        
        output_path = f"output/{session_id}_deleted.pdf"
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        return output_path
    
    elif operation == 'rotate':
        reader = PdfReader(files[0])
        writer = PdfWriter()
        angle = int(form_data.get('angle', 90))
        
        for page in reader.pages:
            writer.add_page(page.rotate(angle))
        
        output_path = f"output/{session_id}_rotated.pdf"
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        return output_path
    
    elif operation == 'compress':
        # Simple compression by reducing quality
        reader = PdfReader(files[0])
        writer = PdfWriter()
        
        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)
        
        output_path = f"output/{session_id}_compressed.pdf"
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        return output_path

@app.route('/download/<session_id>')
def download(session_id):
    result_file = session.get(f'file_{session_id}')
    
    if not result_file or not os.path.exists(result_file):
        return jsonify({'error': 'ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ'}), 404
    
    return send_file(result_file, as_attachment=True, download_name=os.path.basename(result_file))

@app.route('/cleanup/<session_id>')
def cleanup(session_id):
    """Clean up session files"""
    result_file = session.get(f'file_{session_id}')
    if result_file and os.path.exists(result_file):
        try:
            os.remove(result_file)
        except:
            pass
    
    # Remove from session
    session.pop(f'file_{session_id}', None)
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)