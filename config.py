import os

class Config:
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