"""
TextUtils modules for comprehensive Kannada PDF conversion.
Handles digital PDFs, scanned PDFs, and legacy font documents with cloud integration.
"""

# Core modules - always available
from .legacy_kannada import (
    post_process_kannada_text,
    detect_legacy_encoding,
    is_kannada_text,
    normalize_unicode,
    convert_legacy_to_unicode,
    validate_kannada_output
)
from .unified_pdf_converter import UnifiedPDFConverter, convert_pdf_to_word, ocr_pdf_to_word
from .docx_builder import DocxBuilder

# Optional modules - may fail without proper setup
try:
    from .kannada_image_preprocessor import preprocess_kannada_image
except ImportError:
    preprocess_kannada_image = None

try:
    from .gcs_io import upload_to_gcs, download_from_gcs, signed_url
except ImportError:
    upload_to_gcs = None
    download_from_gcs = None
    signed_url = None

try:
    from .ocr_docai import docai_extract
except ImportError:
    docai_extract = None

try:
    from .ocr_vision import rasterize_pdf_to_images, vision_fulltext_on_image
except ImportError:
    rasterize_pdf_to_images = None
    vision_fulltext_on_image = None

__all__ = [
    # Core functionality
    "post_process_kannada_text",
    "detect_legacy_encoding", 
    "is_kannada_text",
    "normalize_unicode",
    "convert_legacy_to_unicode",
    "validate_kannada_output",
    "UnifiedPDFConverter",
    "convert_pdf_to_word",
    "ocr_pdf_to_word",
    "DocxBuilder",
    
    # Optional functionality
    "preprocess_kannada_image",
    "upload_to_gcs",
    "download_from_gcs", 
    "signed_url",
    "docai_extract",
    "rasterize_pdf_to_images",
    "vision_fulltext_on_image"
]
