import os
import mimetypes
from config import Config

config = Config()

def validate_file(file, operation):
    """Validate uploaded file based on operation type"""
    if not file or not file.filename:
        return False
    
    # Get file extension
    filename = file.filename.lower()
    file_ext = os.path.splitext(filename)[1][1:]  # Remove the dot
    
    # Define allowed extensions for each operation
    operation_requirements = {
        'merge': config.ALLOWED_EXTENSIONS['pdf'],
        'split': config.ALLOWED_EXTENSIONS['pdf'],
        'extract': config.ALLOWED_EXTENSIONS['pdf'],
        'delete': config.ALLOWED_EXTENSIONS['pdf'],
        'crop': config.ALLOWED_EXTENSIONS['pdf'],
        'rotate': config.ALLOWED_EXTENSIONS['pdf'],
        'compress': config.ALLOWED_EXTENSIONS['pdf'],
        'pdf_to_word': config.ALLOWED_EXTENSIONS['pdf'],
        'pdf_to_jpeg': config.ALLOWED_EXTENSIONS['pdf'],
        'word_to_pdf': config.ALLOWED_EXTENSIONS['word'],
        'jpeg_to_pdf': config.ALLOWED_EXTENSIONS['image']
    }
    
    # Check if operation is supported
    if operation not in operation_requirements:
        return False
    
    # Check if file extension is allowed for this operation
    allowed_extensions = operation_requirements[operation]
    return file_ext in allowed_extensions

def validate_file_size(file):
    """Check if file size is within limits"""
    try:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)  # Reset file pointer
        return size <= config.MAX_CONTENT_LENGTH
    except:
        return False

def validate_pages_input(pages_str, max_pages):
    """Validate page numbers/ranges input"""
    try:
        if not pages_str or not pages_str.strip():
            return False
        
        parts = pages_str.split(',')
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
    except:
        return False

def validate_rotation_angle(angle):
    """Validate rotation angle"""
    try:
        angle = int(angle)
        return angle in [90, 180, 270, -90, -180, -270]
    except:
        return False

def validate_crop_margins(left, top, right, bottom):
    """Validate crop margin values"""
    try:
        margins = [float(left), float(top), float(right), float(bottom)]
        return all(margin >= 0 for margin in margins)
    except:
        return False

def get_allowed_extensions(operation):
    """Get allowed file extensions for an operation"""
    operation_requirements = {
        'merge': config.ALLOWED_EXTENSIONS['pdf'],
        'split': config.ALLOWED_EXTENSIONS['pdf'],
        'extract': config.ALLOWED_EXTENSIONS['pdf'],
        'delete': config.ALLOWED_EXTENSIONS['pdf'],
        'crop': config.ALLOWED_EXTENSIONS['pdf'],
        'rotate': config.ALLOWED_EXTENSIONS['pdf'],
        'compress': config.ALLOWED_EXTENSIONS['pdf'],
        'pdf_to_word': config.ALLOWED_EXTENSIONS['pdf'],
        'pdf_to_jpeg': config.ALLOWED_EXTENSIONS['pdf'],
        'word_to_pdf': config.ALLOWED_EXTENSIONS['word'],
        'jpeg_to_pdf': config.ALLOWED_EXTENSIONS['image']
    }
    
    return operation_requirements.get(operation, set())

def is_safe_filename(filename):
    """Check if filename is safe (no path traversal, etc.)"""
    import re
    
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    
    # Check for valid characters
    safe_pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
    return safe_pattern.match(filename) is not None