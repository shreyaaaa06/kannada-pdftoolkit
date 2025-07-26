import os
import uuid
import mimetypes
from werkzeug.utils import secure_filename
import config

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
            raise Exception(f"ZIP ರಚನೆ ವಿಫಲ: {str(e)}")
    
    def extract_zip_archive(self, zip_path, extract_to):
        """Extract ZIP archive"""
        try:
            import zipfile
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_to)
            
            return True
        except Exception as e:
            raise Exception(f"ZIP ಹೊರತೆಗೆಯುವಿಕೆ ವಿಫಲ: {str(e)}")
    
    def validate_file_size(self, file_path):
        """Check if file size is within limits"""
        try:
            file_size = os.path.getsize(file_path)
            return file_size <= self.config.MAX_CONTENT_LENGTH
        except:
            return False
    
    def get_file_mime_type(self, file_path):
        """Get MIME type of file"""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type
    
    def is_pdf_file(self, file_path):
        """Check if file is a PDF"""
        return self.get_file_mime_type(file_path) == 'application/pdf'
    
    def is_image_file(self, file_path):
        """Check if file is an image"""
        mime_type = self.get_file_mime_type(file_path)
        return mime_type and mime_type.startswith('image/')
    
    def is_word_file(self, file_path):
        """Check if file is a Word document"""
        mime_type = self.get_file_mime_type(file_path)
        return mime_type in [
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
    
    def generate_unique_filename(self, original_filename, session_id):
        """Generate unique filename to prevent conflicts"""
        name, ext = os.path.splitext(original_filename)
        unique_id = str(uuid.uuid4())[:8]
        return f"{session_id}_{name}_{unique_id}{ext}"
    
    def get_temp_file_path(self, filename, session_id):
        """Get temporary file path for processing"""
        temp_filename = self.generate_unique_filename(filename, session_id)
        return os.path.join(self.config.UPLOAD_FOLDER, temp_filename)
    
    def move_to_output(self, source_path, output_filename, session_id):
        """Move processed file to output directory"""
        try:
            import shutil
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                     f"{session_id}_{output_filename}")
            shutil.move(source_path, output_path)
            return output_path
        except Exception as e:
            raise Exception(f"ಫೈಲ್ ಸ್ಥಳಾಂತರ ವಿಫಲ: {str(e)}")
    
    def copy_file(self, source_path, destination_path):
        """Copy file from source to destination"""
        try:
            import shutil
            shutil.copy2(source_path, destination_path)
            return True
        except Exception as e:
            print(f"File copy error: {e}")
            return False
    
    def ensure_directory_exists(self, directory_path):
        """Ensure directory exists, create if not"""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Directory creation error: {e}")
            return False