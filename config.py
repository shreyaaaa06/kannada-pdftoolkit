import os
from datetime import timedelta

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kannada-pdf-toolkit-secret-key-2024'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    OUTPUT_FOLDER = os.path.join(os.getcwd(), 'output')
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'pdf': ['pdf'],
        'word': ['doc', 'docx'],
        'image': ['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
        'all': ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'bmp', 'tiff']
    }
    
    # PDF processing settings
    PDF_QUALITY = 85  # JPEG quality for PDF to image conversion
    PDF_DPI = 300     # DPI for PDF to image conversion
    MAX_PAGES_PER_OPERATION = 1000  # Maximum pages to process
    
    # Compression settings
    COMPRESSION_LEVELS = {
        'low': 0.9,      # 90% quality
        'medium': 0.7,   # 70% quality
        'high': 0.5      # 50% quality
    }
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Kannada font settings
    KANNADA_FONTS = [
        'Noto Sans Kannada',
        'Tunga',
        'Kedage',
        'Mallige'
    ]
    
    # Default font for PDF generation
    DEFAULT_FONT_PATH = os.path.join('static', 'fonts', 'NotoSansKannada-Regular.ttf')
    
    # Error messages in Kannada
    ERROR_MESSAGES = {
        'file_too_large': 'ಫೈಲ್ ಗಾತ್ರ ತುಂಬಾ ದೊಡ್ಡದಾಗಿದೆ',
        'invalid_file_type': 'ಅಮಾನ್ಯ ಫೈಲ್ ಪ್ರಕಾರ',
        'no_file_selected': 'ದಯವಿಟ್ಟು ಒಂದು ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ',
        'processing_error': 'ಪ್ರಕ್ರಿಯೆಯಲ್ಲಿ ದೋಷ ಸಂಭವಿಸಿದೆ',
        'file_not_found': 'ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ',
        'invalid_pages': 'ಅಮಾನ್ಯ ಪುಟ ಸಂಖ್ಯೆಗಳು',
        'operation_failed': 'ಕಾರ್ಯಾಚರಣೆ ವಿಫಲವಾಗಿದೆ'
    }
    
    # Success messages in Kannada
    SUCCESS_MESSAGES = {
        'merge_complete': 'PDF ಗಳನ್ನು ಯಶಸ್ವಿಯಾಗಿ ವಿಲೀನಗೊಳಿಸಲಾಗಿದೆ',
        'split_complete': 'PDF ಅನ್ನು ಯಶಸ್ವಿಯಾಗಿ ವಿಭಾಗಿಸಲಾಗಿದೆ',
        'extract_complete': 'ಪುಟಗಳನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಹೊರತೆಗೆಯಲಾಗಿದೆ',
        'delete_complete': 'ಪುಟಗಳನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಅಳಿಸಲಾಗಿದೆ',
        'crop_complete': 'ಪುಟಗಳನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಕತ್ತರಿಸಲಾಗಿದೆ',
        'rotate_complete': 'ಪುಟಗಳನ್ನು ಯಶಸ್ವಿಯಾಗಿ ತಿರುಗಿಸಲಾಗಿದೆ',
        'convert_complete': 'ಫೈಲ್ ಅನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಪರಿವರ್ತಿಸಲಾಗಿದೆ',
        'compress_complete': 'PDF ಅನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಸಂಕುಚಿತಗೊಳಿಸಲಾಗಿದೆ'
    }
    
    # UI text in Kannada
    UI_TEXT = {
        'app_title': 'ಕನ್ನಡ PDF ಉಪಕರಣಗಳು',
        'app_subtitle': 'ಸಂಪೂರ್ಣ PDF ಪ್ರಕ್ರಿಯೆ ಮಾಡುವ ಸೇವೆ',
        'select_operation': 'ಕಾರ್ಯಾಚರಣೆ ಆಯ್ಕೆ ಮಾಡಿ',
        'select_files': 'ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ',
        'process_files': 'ಫೈಲ್‌ಗಳನ್ನು ಪ್ರಕ್ರಿಯೆ ಮಾಡಿ',
        'download_result': 'ಫಲಿತಾಂಶ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ',
        'upload_area': 'ಫೈಲ್‌ಗಳನ್ನು ಇಲ್ಲಿ ಎಳೆಯಿರಿ ಅಥವಾ ಕ್ಲಿಕ್ ಮಾಡಿ',
        'supported_formats': 'ಬೆಂಬಲಿತ ಸ್ವರೂಪಗಳು'
    }

# Export the config class
Config = Config