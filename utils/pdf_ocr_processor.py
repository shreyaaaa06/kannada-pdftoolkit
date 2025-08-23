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
        """FIXED: Setup Tesseract OCR for Kannada with proper configuration"""
        try:
            # Test if Tesseract is available
            pytesseract.get_tesseract_version()
            
            # CRITICAL FIX: Improved OCR configuration for Kannada
            # Use kan+eng for better results, with specific PSM mode
            self.ocr_config = '--oem 3 --psm 6 -l kan+eng -c preserve_interword_spaces=1'
            
            # Alternative configs to try if primary fails
            self.fallback_configs = [
                '--oem 3 --psm 3 -l kan+eng',  # Fully automatic page segmentation
                '--oem 3 --psm 1 -l kan+eng',  # Automatic page segmentation with OSD
                '--oem 3 --psm 6 -l kan',      # Kannada only
                '--oem 3 --psm 6 -l eng'       # English fallback
            ]
            
            print("✓ Tesseract OCR configured for Kannada with fallback options")
            
        except Exception as e:
            print(f"⚠ OCR setup warning: {e}")
            print("Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
            self.ocr_config = '--oem 3 --psm 6 -l eng'  # Fallback to English
            self.fallback_configs = []
    
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
        """ENHANCED: Better image preprocessing for Kannada OCR"""
        try:
            # Convert PIL to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # CRITICAL FIX: Better preprocessing for Kannada text
            # 1. Resize image for better OCR (optimal DPI around 300)
            height, width = gray.shape
            if width < 2000:  # Scale up small images
                scale_factor = 2000 / width
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # 2. Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # 3. Enhance contrast for better text recognition
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # 4. Apply adaptive threshold - CRITICAL for Kannada
            # Use Gaussian method which works better for complex scripts
            thresh = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 15, 4  # Increased block size and C value
            )
            
            # 5. Morphological operations to connect broken characters (common in Kannada)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL
            processed_image = Image.fromarray(processed)
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

    def extract_text_with_ocr(self, page):
        """FIXED: Extract text using OCR with multiple configuration attempts"""
        try:
            # First detect image regions
            image_regions = self.detect_image_regions(page)
            
            # Convert PDF page to image with higher resolution for better OCR
            pix = page.get_pixmap(matrix=fitz.Matrix(3.0, 3.0))  # Increased from 2.0 to 3.0
            img_data = pix.pil_tobytes(format="PNG")
            image = Image.open(io.BytesIO(img_data))
            
            # If there are images, mask them out before OCR
            if image_regions:
                processed_image = self.mask_image_regions(image, image_regions, page)
            else:
                processed_image = self.preprocess_image_for_ocr(image)
            
            # CRITICAL FIX: Try multiple OCR configurations
            text = None
            successful_config = None
            
            # Try primary configuration first
            try:
                text = pytesseract.image_to_string(processed_image, config=self.ocr_config)
                if text and len(text.strip()) > 0 and self.is_text_meaningful(text):
                    successful_config = self.ocr_config
                    print(f"✓ Primary OCR config successful")
                else:
                    text = None
            except Exception as e:
                print(f"Primary OCR config failed: {e}")
                text = None
            
            # Try fallback configurations if primary failed
            if not text and self.fallback_configs:
                for config in self.fallback_configs:
                    try:
                        fallback_text = pytesseract.image_to_string(processed_image, config=config)
                        if fallback_text and len(fallback_text.strip()) > 0 and self.is_text_meaningful(fallback_text):
                            text = fallback_text
                            successful_config = config
                            print(f"✓ Fallback OCR config successful: {config}")
                            break
                    except Exception as e:
                        print(f"Fallback config {config} failed: {e}")
                        continue
            
            if not text:
                print("⚠ All OCR configurations failed")
                return ""
            
            print(f"✓ OCR successful with config: {successful_config}")
            
            # CRITICAL FIX: Improved text cleaning
            cleaned_text = self.clean_ocr_text_fixed(text)
            
            # Add image placeholders AFTER cleaning
            if image_regions:
                for i, region in enumerate(image_regions):
                    cleaned_text += f"\n[ಚಿತ್ರ {i+1}: ಈ ಸ್ಥಳದಲ್ಲಿ ಚಿತ್ರವಿದೆ]\n"
            
            return cleaned_text if cleaned_text else ""
            
        except Exception as e:
            print(f"OCR extraction error: {e}")
            return ""
    
    def is_text_meaningful(self, text):
        """Check if OCR output contains meaningful content"""
        if not text or len(text.strip()) < 3:
            return False
        
        # Check for too many replacement characters (indicates poor OCR)
        replacement_chars = text.count('\ufffd') + text.count('�')
        if replacement_chars > len(text) * 0.1:  # More than 10% replacement chars
            return False
        
        # Check if we have some actual letters (not just punctuation)
        letters = sum(1 for char in text if char.isalpha() or '\u0c80' <= char <= '\u0cff')
        if letters < 3:
            return False
        
        return True
    
    def clean_ocr_text_fixed(self, text):
        """FIXED: Clean OCR text without corrupting Kannada characters"""
        try:
            if not text:
                return ""
            
            # CRITICAL FIX: Proper Unicode normalization first
            text = unicodedata.normalize('NFC', text)
            
            # STEP 1: CAREFUL character replacements - only fix obvious OCR mistakes
            # DO NOT replace Kannada characters that look similar to other characters
            ocr_corrections = {
                # Only replace clear OCR artifacts, not legitimate Kannada characters
                '।': '.',      # Devanagari danda to period
                '॥': '..',     # Double danda to double period
                # Remove obviously wrong characters that OCR produces
                '\ufffd': '',  # Unicode replacement character
                '\x00': '',    # Null bytes
                '\ufeff': '',  # BOM
            }
            
            for wrong, correct in ocr_corrections.items():
                text = text.replace(wrong, correct)
            
            # STEP 2: Clean up spacing without destroying structure
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Only remove excessive whitespace, preserve normal spacing
                cleaned_line = ' '.join(line.split())  # This normalizes spaces
                
                # Only add non-empty lines
                if cleaned_line.strip():
                    cleaned_lines.append(cleaned_line)
            
            result = '\n'.join(cleaned_lines)
            
            # STEP 3: Final cleanup - remove only excessive line breaks
            import re
            result = re.sub(r'\n{3,}', '\n\n', result)  # Max 2 consecutive newlines
            
            return result.strip()
            
        except Exception as e:
            print(f"FIXED text cleaning error: {e}")
            return text  # Return original if cleaning fails

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
                
                # Extract text using improved OCR
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
                        '�',       # Another replacement character
                        '□',       # Box characters
                    ]
                    
                    corruption_count = 0
                    for indicator in corruption_indicators:
                        corruption_count += text.count(indicator)
                    
                    # If more than 5% of characters are corruption indicators
                    if len(text) > 0 and corruption_count / len(text) > 0.05:
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

    def preprocess_pdf_if_needed(self, pdf_path, session_id):
        """Preprocess PDF with OCR if text is corrupted"""
        try:
            if self.is_pdf_text_corrupted(pdf_path):
                print(f"⚠ Detected corrupted Kannada text in: {os.path.basename(pdf_path)}")
                print("🔄 Processing with OCR to fix text encoding...")
                
                processed_pdf = self.create_searchable_pdf(pdf_path, session_id)
                if processed_pdf and os.path.exists(processed_pdf):
                    return processed_pdf
            
            return pdf_path  # Return original if no processing needed
            
        except Exception as e:
            print(f"Preprocessing error: {e}")
            return pdf_path  # Return original on error
