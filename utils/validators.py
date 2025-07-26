import os
import mimetypes
from werkzeug.utils import secure_filename
import config

def validate_file(file, operation_type):
    """Validate uploaded file based on operation type"""
    if not file or not file.filename:
        return False
    
    config_obj = config.Config()
    
    # Check file size
    if hasattr(file, 'content_length') and file.content_length:
        if file.content_length > config_obj.MAX_CONTENT_LENGTH:
            return False
    
    # Get file extension
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    # Define allowed extensions for each operation
    operation_extensions = {
        'merge': ['pdf'],
        'split': ['pdf'],
        'extract': ['pdf'],
        'delete': ['pdf'],
        'crop': ['pdf'],
        'rotate': ['pdf'],
        'compress': ['pdf'],
        'pdf_to_word': ['pdf'],
        'word_to_pdf': ['doc', 'docx'],
        'pdf_to_jpeg': ['pdf'],
        'jpeg_to_pdf': ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
    }
    
    allowed_extensions = operation_extensions.get(operation_type, [])
    return file_ext in allowed_extensions

def validate_page_range(page_range, max_pages):
    """Validate page range string"""
    try:
        if not page_range.strip():
            return False
        
        parts = page_range.split(',')
        for part in parts:
            part = part.strip()
            
            if '-' in part:
                start, end = map(int, part.split('-'))
                if start < 1 or end > max_pages or start > end:
                    return False
            else:
                page_num = int(part)
                if page_num < 1 or page_num > max_pages:
                    return False
        
        return True
    except (ValueError, AttributeError):
        return False

def validate_crop_margins(left, top, right, bottom):
    """Validate crop margin values"""
    try:
        margins = [float(left), float(top), float(right), float(bottom)]
        
        # Check if all margins are non-negative
        if any(margin < 0 for margin in margins):
            return False
        
        # Check if margins don't exceed reasonable limits (in points)
        if any(margin > 500 for margin in margins):  # ~7 inches
            return False
        
        return True
    except (ValueError, TypeError):
        return False

def validate_rotation_angle(angle):
    """Validate rotation angle"""
    try:
        angle_int = int(angle)
        return angle_int in [90, 180, 270, -90, -180, -270]
    except (ValueError, TypeError):
        return False

def validate_compression_quality(quality):
    """Validate compression quality parameter"""
    valid_qualities = ['low', 'medium', 'high']
    return quality in valid_qualities

def validate_session_id(session_id):
    """Validate session ID format"""
    if not session_id:
        return False
    
    # Check if it's a valid UUID-like string
    import re
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(session_id))

def validate_filename(filename):
    """Validate filename for security"""
    if not filename:
        return False
    
    secured = secure_filename(filename)
    
    # Check for empty filename after securing
    if not secured:
        return False
    
    # Check filename length
    if len(secured) > 255:
        return False
    
    # Check for valid extension
    if '.' not in secured:
        return False
    
    return True

def validate_file_type_for_operation(file_path, operation):
    """Validate if file type is suitable for the operation"""
    if not os.path.exists(file_path):
        return False
    
    mime_type, _ = mimetypes.guess_type(file_path)
    
    operation_mime_types = {
        'merge': ['application/pdf'],
        'split': ['application/pdf'],
        'extract': ['application/pdf'],
        'delete': ['application/pdf'],
        'crop': ['application/pdf'],
        'rotate': ['application/pdf'],
        'compress': ['application/pdf'],
        'pdf_to_word': ['application/pdf'],
        'word_to_pdf': [
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ],
        'pdf_to_jpeg': ['application/pdf'],
        'jpeg_to_pdf': [
            'image/jpeg',
            'image/jpg',
            'image/png',
            'image/bmp',
            'image/tiff'
        ]
    }
    
    allowed_types = operation_mime_types.get(operation, [])
    return mime_type in allowed_types

def validate_multiple_files(files, operation):
    """Validate multiple files for batch operations"""
    if not files:
        return False
    
    # Operations that support multiple files
    multi_file_operations = ['merge', 'jpeg_to_pdf']
    
    if operation not in multi_file_operations and len(files) > 1:
        return False
    
    # Validate each file
    for file in files:
        if not validate_file(file, operation):
            return False
    
    return True

def validate_pdf_permissions(file_path):
    """Check if PDF has restrictions that might prevent operations"""
    try:
        from PyPDF2 import PdfReader
        
        reader = PdfReader(file_path)
        
        # Check if PDF is encrypted
        if reader.is_encrypted:
            return False, "PDF ಎನ್‌ಕ್ರಿಪ್ಟ್ ಮಾಡಲಾಗಿದೆ"  # PDF is encrypted
        
        # Check metadata for restrictions
        if reader.metadata and hasattr(reader.metadata, 'get'):
            # Some PDFs have permission flags
            pass
        
        return True, None
    
    except Exception as e:
        return False, f"PDF ಪರಿಶೀಲನೆ ವಿಫಲ: {str(e)}"

def sanitize_input(input_string):
    """Sanitize user input to prevent injection attacks"""
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    import re
    sanitized = re.sub(r'[<>"\';\\]', '', str(input_string))
    
    # Limit length
    return sanitized[:1000]

def validate_output_format(format_type):
    """Validate output format parameter"""
    valid_formats = ['pdf', 'docx', 'jpg', 'jpeg', 'png', 'zip']
    return format_type.lower() in valid_formats

def check_file_corruption(file_path):
    """Basic check for file corruption"""
    try:
        # Check if file exists and has content
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return False
        
        # Try to read file header
        with open(file_path, 'rb') as f:
            header = f.read(4)
            
            # Check PDF header
            if file_path.lower().endswith('.pdf'):
                return header.startswith(b'%PDF')
            
            # Check JPEG header
            elif file_path.lower().endswith(('.jpg', '.jpeg')):
                return header.startswith(b'\xff\xd8\xff')
            
            # Check PNG header
            elif file_path.lower().endswith('.png'):
                return header.startswith(b'\x89PNG')
        
        return True
    
    except Exception:
        return False

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)