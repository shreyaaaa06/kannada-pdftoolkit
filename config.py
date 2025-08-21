import os

class Config:
<<<<<<< HEAD
    def __init__(self):
        # Base directories
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.UPLOAD_FOLDER = os.path.join(self.BASE_DIR, 'uploads')
        self.OUTPUT_FOLDER = os.path.join(self.BASE_DIR, 'output')
        
        # File settings
        self.MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
        self.ALLOWED_EXTENSIONS = {
            'pdf': ['.pdf'],
            'word': ['.doc', '.docx'],
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        }
        
        # Create directories if they don't exist
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)
=======
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kannada-pdf-toolkit-secret-key-2024'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    OUTPUT_FOLDER = os.path.join(os.getcwd(), 'output')
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'pdf': {'pdf'},
        'image': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'},
        'word': {'doc', 'docx'}
    }
    
    # PDF processing settings
    PDF_DPI = 200
    PDF_QUALITY = 85
    
    # Font settings
    DEFAULT_FONT_PATH = os.path.join(os.getcwd(), 'static', 'fonts', 'NotoSansKannada-Regular.woff2')
    
    # Compression levels for PDF compression
    COMPRESSION_LEVELS = {
        'low': 0.9,
        'medium': 0.7,
        'high': 0.5
    }
    
    # Supported operations
    OPERATIONS = {
        'merge': 'ವಿಲೀನ',
        'split': 'ವಿಭಾಗ',
        'extract': 'ಹೊರತೆಗೆಯುವಿಕೆ',
        'delete': 'ಅಳಿಸುವಿಕೆ',
        'crop': 'ಕತ್ತರಿಸುವಿಕೆ',
        'rotate': 'ತಿರುಗಿಸುವಿಕೆ',
        'pdf_to_word': 'PDF ರಿಂದ Word',
        'word_to_pdf': 'Word ರಿಂದ PDF',
        'pdf_to_jpeg': 'PDF ರಿಂದ JPEG',
        'jpeg_to_pdf': 'JPEG ರಿಂದ PDF',
        'compress': 'ಸಂಕುಚನ'
    }
    
    # File cleanup settings
    CLEANUP_INTERVAL = 3600  # 1 hour in seconds
    MAX_FILE_AGE = 3600  # 1 hour in seconds
>>>>>>> 398496be4ed2d647ce6ea56bcc7a1557dcdca308
