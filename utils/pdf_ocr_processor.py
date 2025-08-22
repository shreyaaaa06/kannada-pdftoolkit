import fitz  # PyMuPDF
import os
from PIL import Image
import pytesseract
import cv2
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import unicodedata
import urllib.request
import io

class PDFOCRProcessor:
    def __init__(self):
        self.setup_ocr()
        self.setup_fonts()
    
    def setup_ocr(self):
        """Setup Tesseract OCR for Kannada"""
        try:
            # Test if Tesseract is available
            pytesseract.get_tesseract_version()
            
            # Configure for Kannada
            self.ocr_config = '--oem 3 --psm 6 -l kan+eng'
            print("✓ Tesseract OCR configured for Kannada")
            
        except Exception as e:
            print(f"⚠ OCR setup warning: {e}")
            print("Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
            self.ocr_config = '--oem 3 --psm 6 -l eng'  # Fallback to English
    
    def setup_fonts(self):
        """Setup fonts for output PDF"""
        self.kannada_font = 'Helvetica'  # Default fallback
        
        font_paths = [
            os.path.join("static", "fonts", "NotoSansKannada-Regular.ttf"),
            "C:/Windows/Fonts/NotoSansKannada-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('KannadaFont', font_path))
                    self.kannada_font = 'KannadaFont'
                    print(f"✓ Registered Kannada font: {font_path}")
                    return
                except Exception as e:
                    continue
        
        # Download font if needed
        try:
            font_dir = os.path.join("static", "fonts")
            os.makedirs(font_dir, exist_ok=True)
            font_path = os.path.join(font_dir, "NotoSansKannada-Regular.ttf")
            
            if not os.path.exists(font_path):
                font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansKannada/NotoSansKannada-Regular.ttf"
                urllib.request.urlretrieve(font_url, font_path)
                
            pdfmetrics.registerFont(TTFont('KannadaFont', font_path))
            self.kannada_font = 'KannadaFont'
            print("✓ Downloaded and registered Kannada font")
            
        except Exception as e:
            print(f"Font setup error: {e}")
    
    def preprocess_image_for_ocr(self, image):
        """Enhance image for better OCR accuracy"""
        try:
            # Convert PIL to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive threshold for better text extraction
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Convert back to PIL
            processed_image = Image.fromarray(thresh)
            return processed_image
            
        except Exception as e:
            print(f"Image preprocessing error: {e}")
            return image  # Return original if processing fails
    
    def detect_image_regions(self, page):
        """Detect image regions in PDF page to avoid OCR on them"""
        try:
            image_regions = []
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image rectangle
                    image_rects = page.get_image_rects(img)
                    for rect in image_rects:
                        image_regions.append({
                            'rect': rect,
                            'type': 'image',
                            'index': img_index
                        })
                except Exception as e:
                    continue
                    
            return image_regions
        except Exception as e:
            print(f"Image detection error: {e}")
            return []

    # def extract_text_with_ocr(self, page):
    #     """Extract text using OCR but SKIP image regions"""
    #     try:
    #         # First detect image regions
    #         image_regions = self.detect_image_regions(page)
            
    #         # Convert PDF page to image
    #         pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    #         img_data = pix.pil_tobytes(format="PNG")
    #         image = Image.open(io.BytesIO(img_data))
            
    #         # If there are images, mask them out before OCR
    #         if image_regions:
    #             processed_image = self.mask_image_regions(image, image_regions, page)
    #         else:
    #             processed_image = self.preprocess_image_for_ocr(image)
            
    #         # Perform OCR on text-only regions
    #         text = pytesseract.image_to_string(processed_image, config=self.ocr_config)
            
    #         # Add image placeholders
    #         if image_regions:
    #             for i, region in enumerate(image_regions):
    #                 text += f"\n[ಚಿತ್ರ {i+1}: ಈ ಸ್ಥಳದಲ್ಲಿ ಚಿತ್ರವಿದೆ]\n"
            
    #         if text:
    #             text = unicodedata.normalize('NFC', text)
    #             text = text.replace('|', 'ಲ್')
    #             text = text.replace('ॐ', 'ಓಂ')
                
    #             # Clean OCR artifacts but preserve image placeholders
    #             lines = []
    #             for line in text.split('\n'):
    #                 cleaned_line = ' '.join(line.split())
    #                 if cleaned_line.strip():
    #                     lines.append(cleaned_line)
                
    #             return '\n'.join(lines)
            
    #         return ""
            
    #     except Exception as e:
    #         print(f"OCR extraction error: {e}")
    #         return ""

    def mask_image_regions(self, image, image_regions, page):
        """Mask out image regions to prevent OCR artifacts"""
        try:
            from PIL import ImageDraw
            
            # Create a copy of the image
            masked_image = image.copy()
            draw = ImageDraw.Draw(masked_image)
            
            # Get page dimensions
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            # Scale factor from PDF to image coordinates
            scale_x = image.width / page_width
            scale_y = image.height / page_height
            
            # Mask each image region with white rectangle
            for region in image_regions:
                rect = region['rect']
                
                # Convert PDF coordinates to image coordinates
                x0 = int(rect.x0 * scale_x)
                y0 = int(rect.y0 * scale_y)
                x1 = int(rect.x1 * scale_x)
                y1 = int(rect.y1 * scale_y)
                
                # Draw white rectangle over image region
                draw.rectangle([x0, y0, x1, y1], fill='white')
            
            return self.preprocess_image_for_ocr(masked_image)
            
        except Exception as e:
            print(f"Image masking error: {e}")
            return self.preprocess_image_for_ocr(image)
    
    def create_searchable_pdf(self, input_pdf_path, session_id):
        """Create a searchable PDF with proper Kannada text"""
        try:
            print(f"Creating searchable PDF for: {input_pdf_path}")
            
            # Open source PDF
            source_doc = fitz.open(input_pdf_path)
            
            # Create output path
            output_filename = f"{session_id}_searchable_{os.path.basename(input_pdf_path)}"
            output_path = os.path.join("output", output_filename)
            
            # Create new PDF with proper text
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Create style for Kannada text
            styles = getSampleStyleSheet()
            kannada_style = ParagraphStyle(
                'KannadaText',
                parent=styles['Normal'],
                fontName=self.kannada_font,
                fontSize=11,
                spaceAfter=12,
                encoding='utf-8'
            )
            
            # Process each page
            for page_num in range(len(source_doc)):
                page = source_doc[page_num]
                
                # Add page header
                page_title = f"ಪುಟ {page_num + 1}"
                story.append(Paragraph(page_title, styles['Heading2']))
                story.append(Spacer(1, 12))
                
                # Extract text using OCR
                extracted_text = self.extract_text_with_ocr(page)
                
                if extracted_text:
                    # Split into paragraphs and add each
                    paragraphs = extracted_text.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            # Ensure proper encoding
                            clean_para = para.strip()
                            try:
                                story.append(Paragraph(clean_para, kannada_style))
                            except Exception as para_error:
                                print(f"Paragraph error: {para_error}")
                                # Add as plain text if paragraph creation fails
                                story.append(Paragraph(f"[ಪಠ್ಯ ದೋಷ: {clean_para[:50]}...]", kannada_style))
                            
                            story.append(Spacer(1, 6))
                
                else:
                    story.append(Paragraph("ಈ ಪುಟದಲ್ಲಿ ಪಠ್ಯ ಕಂಡುಬಂದಿಲ್ಲ", kannada_style))
                
                # Add page break except for last page
                if page_num < len(source_doc) - 1:
                    story.append(Spacer(1, 20))
            
            # Build the PDF
            doc.build(story)
            source_doc.close()
            
            print(f"✓ Searchable PDF created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Searchable PDF creation error: {e}")
            return None
    
    def is_pdf_text_corrupted(self, pdf_path):
        """Check if PDF has corrupted Kannada text"""
        try:
            doc = fitz.open(pdf_path)
            
            # Sample first few pages
            pages_to_check = min(3, len(doc))
            
            for page_num in range(pages_to_check):
                page = doc[page_num]
                text = page.get_text()
                
                if text:
                    # Check for common signs of corrupted Kannada
                    corruption_indicators = [
                        '\ufffd',  # Replacement character
                        '?',       # Question marks in place of text
                        '□',       # Box characters
                        # Check for excessive spaces (sign of font mapping issues)
                        len(text.split()) > len(text.strip()) * 0.5
                    ]
                    
                    for indicator in corruption_indicators[:3]:  # Check first 3 indicators
                        if indicator in text:
                            doc.close()
                            return True
                    
                    # Check for minimal actual Kannada characters
                    kannada_chars = sum(1 for char in text if '\u0c80' <= char <= '\u0cff')
                    total_chars = len([c for c in text if c.isalnum()])
                    
                    if total_chars > 10 and kannada_chars / total_chars < 0.1:
                        doc.close()
                        return True
            
            doc.close()
            return False
            
        except Exception as e:
            print(f"Corruption check error: {e}")
            return True  # Assume corrupted if we can't check

# Usage example - Add this method to your PDFCompare class
    def preprocess_pdf_if_needed(self, pdf_path, session_id):
        """Preprocess PDF with OCR if text is corrupted"""
        try:
            ocr_processor = PDFOCRProcessor()
            
            if ocr_processor.is_pdf_text_corrupted(pdf_path):
                print(f"⚠ Detected corrupted Kannada text in: {os.path.basename(pdf_path)}")
                print("🔄 Processing with OCR to fix text encoding...")
                
                processed_pdf = ocr_processor.create_searchable_pdf(pdf_path, session_id)
                if processed_pdf and os.path.exists(processed_pdf):
                    return processed_pdf
            
            return pdf_path  # Return original if no processing needed
            
        except Exception as e:
            print(f"Preprocessing error: {e}")
            return pdf_path  # Return original on error
    
    def clean_ocr_text_advanced(self, text):
        """Advanced OCR text cleaning to handle bullet points and formatting"""
        try:
            if not text:
                return ""
            
            # Normalize Unicode
            text = unicodedata.normalize('NFC', text)
            
            # STEP 1: Fix common OCR mistakes for Kannada
            ocr_corrections = {
                '|': 'ಲ್',
                '॒': 'ೃ', 
                '॑': 'ೆ',
                'ॐ': 'ಓಂ',
                '।': '.',
                '॥': '..',
            }
            
            for wrong, correct in ocr_corrections.items():
                text = text.replace(wrong, correct)
            
            # STEP 2: Handle bullet points consistently
            import re
            
            # Replace various bullet point OCR artifacts with standard bullet
            bullet_artifacts = [
                r'[•▪▫◦‣⁃◾◽▸▹●○◯◉⦿⦾]',  # Unicode bullets
                r'[*\-+>→➤➢➣·°∙⋅∘]',        # ASCII bullets and arrows
                r'[❖❘⦿⦾✓✔☑▲►▶]',           # Special symbols
                r'\b[o0O]\s+',                     # OCR mistakes (o, 0, O as bullets)
                r'^\s*[|]\s+',                     # Pipe character as bullet
            ]
            
            for pattern in bullet_artifacts:
                text = re.sub(pattern, '• ', text, flags=re.MULTILINE)
            
            # STEP 3: Clean up numbered lists
            # Replace various numbering formats with bullets
            numbering_patterns = [
                (r'^\s*\d+[\.\)]\s+', '• '),           # 1. or 1)
                (r'^\s*[a-zA-Z][\.\)]\s+', '• '),      # a. or a)
                (r'^\s*[ivxIVX]+[\.\)]\s+', '• '),     # i. or I.
                (r'^\s*\(\d+\)\s+', '• '),             # (1)
                (r'^\s*\([a-zA-Z]\)\s+', '• '),        # (a)
                (r'^\s*\[\d+\]\s+', '• '),             # [1]
            ]
            
            for pattern, replacement in numbering_patterns:
                text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
            
            # STEP 4: Remove OCR noise around text
            # Remove standalone punctuation that's likely OCR noise
            text = re.sub(r'^\s*[^\w\u0C80-\u0CFF\s]+\s*$', '', text, flags=re.MULTILINE)
            
            # STEP 5: Clean up spacing
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Remove excessive whitespace
                cleaned_line = ' '.join(line.split())
                
                # Skip empty lines or lines with just punctuation
                if cleaned_line and not re.match(r'^[^\w\u0C80-\u0CFF]+$', cleaned_line):
                    cleaned_lines.append(cleaned_line)
            
            result = '\n'.join(cleaned_lines)
            
            # STEP 6: Final cleanup
            result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)  # Remove excessive line breaks
            result = re.sub(r'\s*•\s+', '• ', result)          # Standardize bullet spacing
            
            return result.strip()
            
        except Exception as e:
            print(f"Advanced OCR cleaning error: {e}")
            return text

    def extract_text_with_ocr(self, page):
        """FIXED: Extract text using OCR with better bullet point handling"""
        try:
            # Detect image regions first
            image_regions = self.detect_image_regions(page)
            
            # Convert PDF page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
            img_data = pix.pil_tobytes(format="PNG")
            image = Image.open(io.BytesIO(img_data))
            
            # Mask image regions if present
            if image_regions:
                processed_image = self.mask_image_regions(image, image_regions, page)
            else:
                processed_image = self.preprocess_image_for_ocr(image)
            
            # Perform OCR
            raw_text = pytesseract.image_to_string(processed_image, config=self.ocr_config)
            
            # CRITICAL: Use advanced cleaning instead of basic cleaning
            cleaned_text = self.clean_ocr_text_advanced(raw_text)
            
            # Add image placeholders AFTER cleaning
            if image_regions:
                for i, region in enumerate(image_regions):
                    cleaned_text += f"\n[ಚಿತ್ರ {i+1}: ಈ ಸ್ಥಳದಲ್ಲಿ ಚಿತ್ರವಿದೆ]\n"
            
            return cleaned_text if cleaned_text else ""
            
        except Exception as e:
            print(f"Fixed OCR extraction error: {e}")
            return ""
