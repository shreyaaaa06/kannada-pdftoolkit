import io
import os
from typing import List
try:
    from google.cloud import vision
except ImportError:
    vision = None
from PIL import Image
from pdf2image import convert_from_path
import logging

logger = logging.getLogger(__name__)

class LineSpan:
    def __init__(self, text: str, bbox: tuple = None, font_size: float = 12.0):
        self.text = text
        self.bbox = bbox
        self.font_size = font_size

def rasterize_pdf_to_images(local_pdf_path: str) -> List[Image.Image]:
    """Convert PDF pages to PIL Images"""
    try:
        dpi = int(os.getenv("OCR_RASTER_DPI", "300"))
        images = convert_from_path(local_pdf_path, dpi=dpi)
        logger.info(f"Rasterized {len(images)} pages at {dpi} DPI from {local_pdf_path}")
        return images
    except Exception as e:
        logger.error(f"PDF rasterization failed: {e}")
        raise

def vision_fulltext_on_image(pil_img: Image.Image, language_hints: List[str] = None) -> List[LineSpan]:
    """Extract text from image using Vision API DOCUMENT_TEXT_DETECTION"""
    if vision is None:
        raise ImportError("google-cloud-vision package not installed. Run: pip install google-cloud-vision")
    logger.info("Vision: starting rasterization and OCR")


    try:
        # Use explicit credentials if GOOGLE_APPLICATION_CREDENTIALS is relative
        from .path_utils import resolve_service_account_from_env
        creds_path = resolve_service_account_from_env()
        if creds_path:
            client = vision.ImageAnnotatorClient.from_service_account_file(creds_path)  # type: ignore
        else:
            client = vision.ImageAnnotatorClient()

        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        pil_img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        image = vision.Image(content=img_bytes)

        # Set language hints if provided
        image_context = None
        if language_hints:
            image_context = vision.ImageContext(language_hints=language_hints)

        timeout_sec = float(os.getenv("VISION_TIMEOUT_SECONDS", "60"))
        response = client.document_text_detection(image=image, image_context=image_context, timeout=timeout_sec)

        if response.error.message:
            raise Exception(f'Vision API error: {response.error.message}')

        line_spans = []

        # Extract text from full_text_annotation
        if response.full_text_annotation:
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        para_text = ""
                        para_bbox = None

                        for word in paragraph.words:
                            word_text = ''.join([symbol.text for symbol in word.symbols])
                            para_text += word_text + " "

                            # Get bounding box from first word
                            if para_bbox is None and word.bounding_box:
                                vertices = word.bounding_box.vertices
                                para_bbox = (
                                    min(v.x for v in vertices),
                                    min(v.y for v in vertices),
                                    max(v.x for v in vertices),
                                    max(v.y for v in vertices)
                                )

                        if para_text.strip():
                            # Estimate font size from bbox height
                            font_size = 12.0
                            if para_bbox:
                                height = para_bbox[3] - para_bbox[1]
                                if height > 0:
                                    font_size = max(8.0, min(20.0, height * 0.75))  # Rough conversion

                            line_spans.append(LineSpan(para_text.strip(), para_bbox, font_size))

        logger.info(f"Vision API extracted {len(line_spans)} text segments")
        return line_spans

    except Exception as e:
        logger.error(f"Vision API text extraction failed: {e}")
        raise

