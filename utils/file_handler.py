import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

class FileHandler:
    def __init__(self):
        self.allowed_extensions = {
            'pdf': ['.pdf'],
            'word': ['.doc', '.docx'],
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        }
        self.max_file_size = 1024 * 1024 * 1024  # 1GB
    
    def allowed_file(self, filename, file_type='all'):
        """Check if file has allowed extension"""
        if '.' not in filename:
            return False
        
        extension = '.' + filename.rsplit('.', 1)[1].lower()
        
        if file_type == 'all':
            all_extensions = []
            for ext_list in self.allowed_extensions.values():
                all_extensions.extend(ext_list)
            return extension in all_extensions
        
        return extension in self.allowed_extensions.get(file_type, [])
    
    def save_uploaded_file(self, file, session_id):
        """Save uploaded file and return path"""
        try:
            if not file or not file.filename:
                return None
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > self.max_file_size:
                raise Exception(f"ಫೈಲ್ ತುಂಬಾ ದೊಡ್ಡದಾಗಿದೆ: {file.filename}")
            
            # Check file type
            if not self.allowed_file(file.filename):
                raise Exception(f"ಬೆಂಬಲಿಸದ ಫೈಲ್ ಪ್ರಕಾರ: {file.filename}")
            
            # Generate secure filename
            filename = secure_filename(file.filename)
            if not filename:
                filename = f"file_{uuid.uuid4().hex[:8]}.pdf"
            
            # Add session prefix to avoid conflicts
            filename = f"{session_id}_{filename}"
            
            # Create upload directory if it doesn't exist
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            return file_path
            
        except Exception as e:
            print(f"Error saving file: {e}")
            raise Exception(f"ಫೈಲ್ ಉಳಿಸುವಲ್ಲಿ ದೋಷ: {str(e)}")
    
    def cleanup_old_files(self, max_age_hours=1):
        """Clean up old uploaded and output files"""
        try:
            import time
            
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            # Clean upload folder
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if os.path.exists(upload_folder):
                for filename in os.listdir(upload_folder):
                    file_path = os.path.join(upload_folder, filename)
                    if os.path.isfile(file_path):
                        file_age = current_time - os.path.getctime(file_path)
                        if file_age > max_age_seconds:
                            os.remove(file_path)
            
            # Clean output folder
            output_folder = current_app.config['OUTPUT_FOLDER']
            if os.path.exists(output_folder):
                for filename in os.listdir(output_folder):
                    file_path = os.path.join(output_folder, filename)
                    if os.path.isfile(file_path):
                        file_age = current_time - os.path.getctime(file_path)
                        if file_age > max_age_seconds:
                            os.remove(file_path)
                    elif os.path.isdir(file_path):
                        # Remove old directories too
                        dir_age = current_time - os.path.getctime(file_path)
                        if dir_age > max_age_seconds:
                            import shutil
                            shutil.rmtree(file_path)
                            
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def get_file_info(self, file_path):
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return None
            
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)
            extension = filename.split('.')[-1].lower() if '.' in filename else ''
            
            return {
                'filename': filename,
                'size': file_size,
                'extension': extension,
                'path': file_path
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None