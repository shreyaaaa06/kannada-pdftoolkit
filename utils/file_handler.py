import os
import uuid
import time
import math
import mimetypes
import zipfile
import shutil
from werkzeug.utils import secure_filename
from flask import current_app

class FileHandler:
    def __init__(self):
        # Support both config methods for maximum compatibility
        try:
            import config
            self.config = config.Config()
            self.use_config_object = True
        except ImportError:
            self.use_config_object = False
        
        self.allowed_extensions = {
            'pdf': ['.pdf'],
            'word': ['.doc', '.docx'],
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        }
        self.max_file_size = 100 * 1024 * 1024  # 100MB
    
    def _get_upload_folder(self):
        """Get upload folder path with fallback support"""
        if self.use_config_object:
            return self.config.UPLOAD_FOLDER
        else:
            return current_app.config['UPLOAD_FOLDER']
    
    def _get_output_folder(self):
        """Get output folder path with fallback support"""
        if self.use_config_object:
            return self.config.OUTPUT_FOLDER
        else:
            return current_app.config['OUTPUT_FOLDER']
    
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
        """Save uploaded file and return file path"""
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
            
            # FIXED: Generate unique filename to handle Kannada/special characters
            original_filename = file.filename
            secure_name = secure_filename(original_filename)
            
            # If secure_filename removes everything (common with Kannada filenames)
            if not secure_name or len(secure_name) < 3:
                # Use original extension if available
                if '.' in original_filename:
                    extension = '.' + original_filename.rsplit('.', 1)[1].lower()
                else:
                    extension = '.pdf'
                secure_name = f"file_{uuid.uuid4().hex[:8]}{extension}"
            
            # CRITICAL FIX: Always add unique identifier to prevent conflicts
            unique_id = f"{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
            filename = f"{session_id}_{unique_id}_{secure_name}"
            
            # Create upload directory if it doesn't exist
            upload_folder = self._get_upload_folder()
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            return file_path
            
        except Exception as e:
            print(f"Error saving file: {e}")
            raise Exception(f"ಫೈಲ್ ಉಳಿಸುವಲ್ಲಿ ದೋಷ: {str(e)}")
    
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
        """Get file information with comprehensive details"""
        try:
            if not os.path.exists(file_path):
                return None
            
            file_stat = os.stat(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            file_size = file_stat.st_size
            filename = os.path.basename(file_path)
            extension = filename.split('.')[-1].lower() if '.' in filename else ''
            
            return {
                'filename': filename,
                'name': filename,  # Alias for compatibility
                'size': file_size,
                'size_formatted': self.format_file_size(file_size),
                'extension': extension,
                'mime_type': mime_type,
                'path': file_path,
                'modified': file_stat.st_mtime
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return {'error': str(e)}
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def cleanup_session_files(self, session_id):
        """Remove all files associated with a session"""
        try:
            folders_to_clean = [self._get_upload_folder(), self._get_output_folder()]
            
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
            archive_path = os.path.join(self._get_output_folder(), 
                                      f"{session_id}_{archive_name}.zip")
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        zipf.write(file_path, os.path.basename(file_path))
            
            return archive_path
        except Exception as e:
            print(f"Error creating ZIP archive: {e}")
            raise Exception(f"ZIP ಆರ್ಕೈವ್ ರಚನೆಯಲ್ಲಿ ದೋಷ: {str(e)}")
    
    def cleanup_old_files(self, max_age_hours=1):
        """Clean up old uploaded and output files"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            # Clean upload folder
            upload_folder = self._get_upload_folder()
            if os.path.exists(upload_folder):
                for filename in os.listdir(upload_folder):
                    file_path = os.path.join(upload_folder, filename)
                    if os.path.isfile(file_path):
                        file_age = current_time - os.path.getctime(file_path)
                        if file_age > max_age_seconds:
                            os.remove(file_path)
            
            # Clean output folder
            output_folder = self._get_output_folder()
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
                            shutil.rmtree(file_path)
                            
        except Exception as e:
            print(f"Cleanup error: {e}")