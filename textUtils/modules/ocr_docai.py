import os
from typing import List, Dict, Any
try:
    from google.cloud import documentai
except ImportError:
    documentai = None
import logging

logger = logging.getLogger(__name__)

class Page:
    def __init__(self):
        self.blocks = []
        self.tables = []
        self.figures = []

class Block:
    def __init__(self, text: str, bbox: tuple = None):
        self.text = text
        self.bbox = bbox
        self.paragraphs = []

class Paragraph:
    def __init__(self, text: str, bbox: tuple = None):
        self.text = text
        self.bbox = bbox
        self.lines = []

class Line:
    def __init__(self, text: str, bbox: tuple = None):
        self.text = text
        self.bbox = bbox
        self.spans = []

class Span:
    def __init__(self, text: str, bbox: tuple = None, font_size: float = None):
        self.text = text
        self.bbox = bbox
        self.font_size = font_size

def docai_extract(pdf_bytes: bytes, language_hints: List[str]) -> List[Page]:
    """Extract structured content from PDF using Document AI OCR"""
    if documentai is None:
        raise ImportError("google-cloud-documentai package not installed. Run: pip install google-cloud-documentai")
    
    try:
        project_id = os.getenv("PROJECT_ID")
        location = os.getenv("LOCATION", "us")
        processor_id = os.getenv("DOC_AI_PROCESSOR_ID")
        
        if not all([project_id, processor_id]):
            raise ValueError("Missing Document AI configuration")
        
        client = documentai.DocumentProcessorServiceClient()
        name = client.processor_path(project=project_id, location=location, processor=processor_id)

        raw_document = documentai.RawDocument(content=pdf_bytes, mime_type="application/pdf")
        # Try to pass language hints if API supports it; fallback silently if not
        request = None
        try:
            ocr_cfg = documentai.OcrConfig(language_hints=language_hints or ["kn", "en"])  # type: ignore
            proc_opts = documentai.ProcessOptions(ocr_config=ocr_cfg)  # type: ignore
            request = documentai.ProcessRequest(name=name, raw_document=raw_document, process_options=proc_opts)
        except Exception:
            request = documentai.ProcessRequest(name=name, raw_document=raw_document)

        timeout_sec = float(os.getenv("DOCAI_TIMEOUT_SECONDS", "60"))
        logger.info(f"DocAI: calling process_document, bytes={len(pdf_bytes)}, timeout={timeout_sec}s, processor={processor_id}, location={location}")
        result = client.process_document(request=request, timeout=timeout_sec)
        doc = result.document
        
        pages = []
        for page_obj in doc.pages:
            page = Page()
            
            # Extract paragraphs as blocks
            for para in page_obj.paragraphs:
                if para.layout.text_anchor:
                    text_segments = para.layout.text_anchor.text_segments
                    para_text = ""
                    for segment in text_segments:
                        start_idx = segment.start_index or 0
                        end_idx = segment.end_index or len(doc.text)
                        para_text += doc.text[start_idx:end_idx]
                    
                    bbox = None
                    if para.layout.bounding_poly:
                        vertices = para.layout.bounding_poly.normalized_vertices
                        if vertices:
                            bbox = (
                                min(v.x for v in vertices),
                                min(v.y for v in vertices), 
                                max(v.x for v in vertices),
                                max(v.y for v in vertices)
                            )
                    
                    block = Block(para_text.strip(), bbox)
                    paragraph = Paragraph(para_text.strip(), bbox)
                    
                    # Estimate font size from bbox height; convert normalized coords to points if possible
                    font_size = 12.0
                    try:
                        if para.layout.bounding_poly and page_obj.dimension and page_obj.dimension.height and page_obj.dimension.unit == "POINTS":
                            # Use actual points if available
                            rect = para.layout.bounding_poly.normalized_vertices
                            if rect:
                                min_y = min(v.y for v in rect)
                                max_y = max(v.y for v in rect)
                                height_pts = (max_y - min_y) * page_obj.dimension.height
                                if height_pts > 1.0:
                                    font_size = max(8.0, min(28.0, height_pts * 0.85))
                        else:
                            # Fallback using normalized height * 72
                            vertices = para.layout.bounding_poly.normalized_vertices if para.layout.bounding_poly else []
                            if vertices:
                                height = max(v.y for v in vertices) - min(v.y for v in vertices)
                                if height > 0:
                                    font_size = max(8.0, min(28.0, height * 72))
                    except Exception:
                        pass

                    span = Span(para_text.strip(), bbox, float(font_size))
                    line = Line(para_text.strip(), bbox)
                    line.spans.append(span)
                    paragraph.lines.append(line)
                    block.paragraphs.append(paragraph)
                    page.blocks.append(block)
            
            # Extract tables
            for table in page_obj.tables:
                table_data = []
                for row in table.body_rows:
                    row_data = []
                    for cell in row.cells:
                        if cell.layout.text_anchor:
                            text_segments = cell.layout.text_anchor.text_segments
                            cell_text = ""
                            for segment in text_segments:
                                start_idx = segment.start_index or 0
                                end_idx = segment.end_index or len(doc.text)
                                cell_text += doc.text[start_idx:end_idx]
                            row_data.append(cell_text.strip())
                        else:
                            row_data.append("")
                    table_data.append(row_data)
                page.tables.append(table_data)
            
            pages.append(page)
        
        logger.info(f"Document AI extracted {len(pages)} pages")
        return pages
        
    except Exception as e:
        logger.error(f"Document AI extraction failed: {e}")
        raise

