import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
import config
import os
import mimetypes

class FileHandler:
    def __init__(self):
        self.config = config.Config()
    
    def save_uploaded_file(self, file, session_id):
        """Save uploaded file and return file path"""
        try:
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Add session ID to prevent conflicts
                unique_filename = f"{session_id}_{filename}"
                file_path = os.path.join(self.config.UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                return file_path
            return None
        except Exception as e:
            raise Exception(f"ಫೈಲ್ ಉಳಿಸುವಿಕೆ ವಿಫಲ: {str(e)}")
    
    def save_multiple_files(self, files, session_id):
        """Save multiple uploaded files"""
        file_paths = []
        for file in files:
            if file and file.filename:
                file_path = self.save_uploaded_file(file, session_id)
                if file_path:
                    file_paths.append(file_path)
        return file_paths
    
    def get_file_info(self, file_path):
        """Get file information"""
        try:
            if os.path.exists(file_path):
                file_stat = os.stat(file_path)
                mime_type, _ = mimetypes.guess_type(file_path)
                
                return {
                    'name': os.path.basename(file_path),
                    'size': file_stat.st_size,
                    'size_formatted': self.format_file_size(file_stat.st_size),
                    'mime_type': mime_type,
                    'extension': os.path.splitext(file_path)[1].lower(),
                    'modified': file_stat.st_mtime
                }
            return None
        except Exception as e:
            return {'error': str(e)}
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def cleanup_session_files(self, session_id):
        """Remove all files associated with a session"""
        try:
            folders_to_clean = [self.config.UPLOAD_FOLDER, self.config.OUTPUT_FOLDER]
            
            for folder in folders_to_clean:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        if filename.startswith(session_id):
                            file_path = os.path.join(folder, filename)
                            if os.path.isfile(file_path):
                                os.remove(file_path)
            
            return True
        except Exception as e:
            print(f"Cleanup error: {e}")
            return False
    
    def create_zip_archive(self, file_paths, archive_name, session_id):
        """Create ZIP archive from multiple files"""
        try:
            import zipfile
            
            archive_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                      f"{session_id}_{archive_name}.zip")
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.basename(file_path))
            
            return archive_path
        except Exception as e:
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
            pass
    
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
            return None