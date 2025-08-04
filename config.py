import os

class Config:
    def __init__(self):
        # Base directories
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.UPLOAD_FOLDER = os.path.join(self.BASE_DIR, 'uploads')
        self.OUTPUT_FOLDER = os.path.join(self.BASE_DIR, 'output')
        
        # File settings
        self.MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB
        self.ALLOWED_EXTENSIONS = {
            'pdf': ['.pdf'],
            'word': ['.doc', '.docx'],
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        }
        
        # Create directories if they don't exist
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)