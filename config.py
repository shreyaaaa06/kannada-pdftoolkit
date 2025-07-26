import os

class Config:
    def __init__(self):
        self.UPLOAD_FOLDER = 'uploads'
        self.OUTPUT_FOLDER = 'output'
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
        self.ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'docx', 'doc'}
        
        # Create directories if they don't exist
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)