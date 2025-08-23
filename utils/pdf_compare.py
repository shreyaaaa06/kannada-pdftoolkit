import fitz  # PyMuPDF
import difflib
import os
from PIL import Image, ImageDraw, ImageChops
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import green, red, blue, black
from reportlab.lib import colors
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import uuid
import json
import urllib.request
import unicodedata
import datetime  # Add this import for the enhanced report
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import re 


class PDFCompare:
    def __init__(self):
        self.kannada_font = 'KannadaFont'  # Default fallback
        self.setup_fonts()
    
    def setup_fonts(self):
        """FIXED: Simple and reliable font setup for Kannada"""
        try:
            print("Setting up fonts...")
            
            # Try local project font first (CHECK YOUR ACTUAL FONT FILE NAME)
            project_font_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                "static", "fonts", "NotoSansKannada-Regular.ttf"  # MAKE SURE THIS FILE EXISTS
            )
            
            if os.path.exists(project_font_path):
                try:
                    pdfmetrics.registerFont(TTFont('KannadaFont', project_font_path))
                    self.kannada_font = 'KannadaFont'
                    print(f"✓ Using project font: {project_font_path}")
                    return
                except Exception as e:
                    print(f"Project font failed: {e}")
            
            # Try to download font if local doesn't exist
            try:
                font_dir = os.path.dirname(project_font_path)
                os.makedirs(font_dir, exist_ok=True)
                
                # Download TTF font (not WOFF2)
                font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansKannada/NotoSansKannada-Regular.ttf"
                urllib.request.urlretrieve(font_url, project_font_path)
                
                if os.path.exists(project_font_path) and os.path.getsize(project_font_path) > 10000:
                    pdfmetrics.registerFont(TTFont('KannadaFont', project_font_path))
                    self.kannada_font = 'KannadaFont'
                    print("✓ Downloaded and registered font successfully")
                    return
            except Exception as e:
                print(f"Font download failed: {e}")
            
            # FINAL fallback - use Helvetica
            print("⚠ Using Helvetica - Kannada may not display perfectly")
            self.kannada_font = 'Helvetica'
            
        except Exception as e:
            print(f"Font setup error: {e}")
            self.kannada_font = 'Helvetica'

    def safe_text_extract(self, page):
        """Extract text with proper image handling"""
        try:
            # First try standard extraction
            text_dict = page.get_text("dict")
            text_parts = []
            
            # IMPROVED IMAGE DETECTION
            image_list = page.get_images(full=True)  # Add full=True for complete image info
            image_count = len(image_list)
            
            # ALSO CHECK FOR EMBEDDED IMAGES IN DIFFERENT FORMATS
            try:
                # Check for Form XObjects (which can be images)
                xobjects = page.get_text("dict").get("xobjects", [])
                for xobj in xobjects:
                    if xobj.get("type") == "image":
                        image_count += 1
            except:
                pass
            
            print(f"Page has {image_count} images detected")  # Debug info
            
            # Rest of your existing text extraction logic...
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        for span in line.get("spans", []):
                            span_text = span.get("text", "").strip()
                            if span_text:
                                line_text += span_text + " "
                        if line_text.strip():
                            text_parts.append(line_text.strip())
            
            # Add actual text
            if text_parts:
                full_text = "\n".join(text_parts)
                full_text = unicodedata.normalize('NFC', full_text)
                
                # Check if text is corrupted and needs OCR
                if self.is_kannada_text_broken(full_text):
                    print("⚠ Text is broken, using OCR with image masking...")
                    return self.extract_with_ocr_fallback(page)
                
                # Add image placeholders for ALL images found
                if image_count > 0:
                    for i in range(image_count):
                        full_text += f"\n[ಚಿತ್ರ {i+1}: ಈ ಸ್ಥಳದಲ್ಲಿ ಚಿತ್ರವಿದೆ]\n"
                
                return full_text
            
            # If no text found but images exist, create placeholder text
            if image_count > 0:
                image_text = ""
                for i in range(image_count):
                    image_text += f"[ಚಿತ್ರ {i+1}: ಈ ಸ್ಥಳದಲ್ಲಿ ಚಿತ್ರವಿದೆ]\n"
                return image_text
            
            # Try OCR as last resort
            return self.extract_with_ocr_fallback(page)
            
        except Exception as e:
            print(f"Text extraction error: {e}")
            return ""
    def compare_images_for_visual_diff(self, img1_path, img2_path):
        """Enhanced visual comparison with element-level detection"""
        try:
            from PIL import Image, ImageChops, ImageStat
            import numpy as np
            
            if not (img1_path and img2_path and os.path.exists(img1_path) and os.path.exists(img2_path)):
                return True  # If one image is missing, consider it different
            
            # Load images
            img1 = Image.open(img1_path)
            img2 = Image.open(img2_path)
            
            # Convert to same mode for comparison
            if img1.mode != img2.mode:
                img1 = img1.convert('RGB')
                img2 = img2.convert('RGB')
            
            # Resize to same dimensions if different
            if img1.size != img2.size:
                # If sizes are very different, it's definitely a difference
                size_diff_threshold = 0.1  # 10% difference in size
                size1 = img1.width * img1.height
                size2 = img2.width * img2.height
                
                if abs(size1 - size2) / max(size1, size2) > size_diff_threshold:
                    print(f"Significant size difference detected: {img1.size} vs {img2.size}")
                    return True
                
                # Resize to larger dimensions to avoid losing detail
                target_width = max(img1.width, img2.width)
                target_height = max(img1.height, img2.height)
                
                img1 = img1.resize((target_width, target_height), Image.Resampling.LANCZOS)
                img2 = img2.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Calculate pixel-level differences
            diff = ImageChops.difference(img1, img2)
            stat = ImageStat.Stat(diff)
            rms_diff = sum(stat.rms) / len(stat.rms)
            
            # More sensitive threshold for element detection
            diff_array = np.array(diff)
            
            if len(diff_array.shape) == 3:
                diff_magnitude = np.sqrt(np.sum(diff_array**2, axis=2))
            else:
                diff_magnitude = diff_array
            
            total_pixels = diff_magnitude.size
            # Lower threshold to catch smaller changes
            threshold = max(20, rms_diff * 0.3)
            significantly_different = np.count_nonzero(diff_magnitude > threshold)
            diff_percentage = (significantly_different / total_pixels) * 100
            
            print(f"Visual diff - RMS: {rms_diff:.2f}, Different pixels: {diff_percentage:.2f}%")
            
            # More sensitive detection - lower thresholds
            is_different = (rms_diff > 15.0) or (diff_percentage > 1.0)
            
            return is_different
            
        except Exception as e:
            print(f"Visual comparison error: {e}")
            return False
    def is_kannada_text_readable(self, text):
        """Check if extracted Kannada text is readable (not broken)"""
        if not text or len(text.strip()) < 3:
            return False
        
        # Check for broken character indicators
        broken_indicators = ['\ufffd', '□', '???', '��', '??' * 2]
        for indicator in broken_indicators:
            if indicator in text:
                return False
        
        # Check if we have reasonable Kannada content
        kannada_chars = sum(1 for char in text if '\u0c80' <= char <= '\u0cff')
        total_chars = len([c for c in text if c.isalnum()])
        
        if total_chars > 10:
            # If very few Kannada characters in a Kannada document, likely broken
            if kannada_chars / total_chars < 0.05:  # Less than 5% Kannada
                return False
        
        return True  # Text seems readable

    def is_kannada_text_broken(self, text):
        """Check if Kannada text is broken/corrupted"""
        if not text or len(text.strip()) < 3:
            return True
        
        # Check for broken character indicators
        broken_indicators = ['\ufffd', '□', '???', '��']
        for indicator in broken_indicators:
            if indicator in text:
                return True
        
        # Check if we have reasonable Kannada content
        kannada_chars = sum(1 for char in text if '\u0c80' <= char <= '\u0cff')
        total_chars = len([c for c in text if c.isalnum()])
        
        if total_chars > 10:
            # If less than 10% Kannada characters in Kannada PDF, probably broken
            if kannada_chars / total_chars < 0.1:
                return True
        
        return False

    def extract_with_ocr_fallback(self, page):
        """Use OCR ONLY when regular text extraction fails"""
        try:
            from utils.pdf_ocr_processor import PDFOCRProcessor
            ocr_processor = PDFOCRProcessor()
            ocr_text = ocr_processor.extract_text_with_ocr(page)
            
            if ocr_text and len(ocr_text.strip()) > 0:
                return self.clean_kannada_text(ocr_text)
            
            return ""
            
        except ImportError:
            print("⚠ OCR processor not available")
            return ""
        except Exception as e:
            print(f"OCR fallback failed: {e}")
            return ""

    

    def clean_kannada_text(self, text):
        """CRITICAL: Clean and normalize Kannada text properly"""
        try:
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            
            # CRITICAL: Don't escape HTML here - templates handle it
            text = unicodedata.normalize('NFC', text)
            
            # Remove only NULL bytes and BOM
            text = text.replace('\x00', '')
            text = text.replace('\ufeff', '')
            text = text.replace('\ufffd', '')
            
            # Fix line endings
            text = text.replace('\r\n', '\n').replace('\r', '\n')
            
            # DON'T over-clean - preserve Kannada structure
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                # Only remove excessive spaces, keep structure
                cleaned_line = ' '.join(line.split())
                cleaned_lines.append(cleaned_line)
            
            return '\n'.join(cleaned_lines)
            
        except Exception as e:
            print(f"Text cleaning error: {e}")
            return text if isinstance(text, str) else ""

    
    def compare_pdfs_web(self, pdf1_path, pdf2_path, session_id, compare_type='both'):
        """FIXED: Web-friendly PDF comparison with proper page handling"""
        try:
            print(f"Starting comparison: {pdf1_path} vs {pdf2_path}")
            
            doc1 = fitz.open(pdf1_path)
            doc2 = fitz.open(pdf2_path)
            
            # CRITICAL FIX: Maintain upload order - first uploaded stays as file1
            comparison_data = {
                'file1_name': os.path.basename(pdf1_path),
                'file2_name': os.path.basename(pdf2_path),
                'file1_pages': len(doc1),
                'file2_pages': len(doc2),
                'page_comparisons': [],
                'summary': {
                    'total_pages_compared': 0,
                    'total_text_changes': 0,
                    'visual_diff_pages': 0
                }
            }
            
            max_pages = max(len(doc1), len(doc2))
            comparison_data['summary']['total_pages_compared'] = max_pages
            
            # Create output directories
            output_dir = f"static/temp/{session_id}"
            os.makedirs(output_dir, exist_ok=True)
            
            total_text_changes = 0
            visual_diff_pages = 0
            
            # FIXED: Process each page properly
            for page_num in range(max_pages):
                page_comparison = {
                    'page_number': page_num + 1,
                    'has_page1': page_num < len(doc1),
                    'has_page2': page_num < len(doc2),
                    'has_visual_differences': False,
                    'text_changes': [],
                    'image1_url': None,
                    'image2_url': None,
                    'diff_image_url': None,
                    'page_status': 'both_exist'
                }
                
                # Set page status for template logic
                if page_num >= len(doc1):
                    page_comparison['page_status'] = 'only_in_file2'
                elif page_num >= len(doc2):
                    page_comparison['page_status'] = 'only_in_file1'
                else:
                    page_comparison['page_status'] = 'both_exist'
                
                comparison_data['page_comparisons'].append(page_comparison)
            
            # VISUAL COMPARISON - FIXED: Compare ALL pages, not just common ones
            if compare_type in ['visual', 'both']:
                actual_visual_differences = 0
                
                # CRITICAL FIX: Process ALL pages and count ALL differences
                for page_idx in range(max_pages):
                    try:
                        # Generate images for all pages that exist
                        img1_path = None
                        img2_path = None
                        
                        # Generate image for page1 if it exists
                        if page_idx < len(doc1):
                            page1 = doc1[page_idx]
                            img1_path = os.path.join(output_dir, f"page_{page_idx + 1}_file1.png")
                            pix1 = page1.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                            pix1.save(img1_path)
                            comparison_data['page_comparisons'][page_idx]['image1_url'] = f"/static/temp/{session_id}/page_{page_idx + 1}_file1.png"
                        
                        # Generate image for page2 if it exists
                        if page_idx < len(doc2):
                            page2 = doc2[page_idx]
                            img2_path = os.path.join(output_dir, f"page_{page_idx + 1}_file2.png")
                            pix2 = page2.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                            pix2.save(img2_path)
                            comparison_data['page_comparisons'][page_idx]['image2_url'] = f"/static/temp/{session_id}/page_{page_idx + 1}_file2.png"
                        
                        # FIXED: Count ALL page differences, not just visual changes
                        if page_idx < len(doc1) and page_idx < len(doc2):
                            # Both pages exist - check for visual differences
                            has_visual_diff = self.compare_images_for_visual_diff(img1_path, img2_path)
                            
                            if has_visual_diff:
                                actual_visual_differences += 1
                                comparison_data['page_comparisons'][page_idx]['has_visual_differences'] = True
                                
                                # Generate difference image
                                try:
                                    diff_img_path = os.path.join(output_dir, f"page_{page_idx + 1}_diff.png")
                                    self.create_difference_image(img1_path, img2_path, diff_img_path)
                                    if os.path.exists(diff_img_path):
                                        comparison_data['page_comparisons'][page_idx]['diff_image_url'] = f"/static/temp/{session_id}/page_{page_idx + 1}_diff.png"
                                except Exception as diff_error:
                                    print(f"Difference image creation failed: {diff_error}")
                        else:
                            # FIXED: Pages that exist in only one file are counted as differences
                            actual_visual_differences += 1
                            comparison_data['page_comparisons'][page_idx]['has_visual_differences'] = True

                        
                        # Create placeholder for missing pages
                        if page_idx >= len(doc1):
                            blank_img_path = os.path.join(output_dir, f"page_{page_idx + 1}_file1.png")
                            self.create_blank_page_image(blank_img_path, page_idx + 1)
                            comparison_data['page_comparisons'][page_idx]['image1_url'] = f"/static/temp/{session_id}/page_{page_idx + 1}_file1.png"
                        
                        if page_idx >= len(doc2):
                            blank_img_path = os.path.join(output_dir, f"page_{page_idx + 1}_file2.png")
                            self.create_blank_page_image(blank_img_path, page_idx + 1)
                            comparison_data['page_comparisons'][page_idx]['image2_url'] = f"/static/temp/{session_id}/page_{page_idx + 1}_file2.png"
                    
                    except Exception as page_error:
                        print(f"Error processing page {page_idx + 1}: {page_error}")
                
                visual_diff_pages = actual_visual_differences
            
            # TEXT COMPARISON - FIXED: Process ALL pages
            if compare_type in ['text', 'both']:
                for page_num in range(max_pages):
                    page_comparison = comparison_data['page_comparisons'][page_num]
                    
                    try:
                        text1 = ""
                        text2 = ""
                        
                        if page_num < len(doc1):
                            page1 = doc1[page_num]
                            text1 = self.safe_text_extract(page1)
                        
                        if page_num < len(doc2):
                            page2 = doc2[page_num]
                            text2 = self.safe_text_extract(page2)
                        
                        # Compare texts using difflib - works even if one text is empty
                        if text1 or text2:
                            meaningful_changes = self.compare_texts_intelligently(text1, text2)
                            
                            page_comparison['text_changes'] = meaningful_changes
                            total_text_changes += len(meaningful_changes)
                            
                            print(f"Page {page_num + 1}: Found {len(meaningful_changes)} meaningful changes")
                    
                    except Exception as text_error:
                        print(f"Text comparison error on page {page_num + 1}: {text_error}")

            
            # Update summary
            comparison_data['summary']['total_text_changes'] = total_text_changes
            comparison_data['summary']['visual_diff_pages'] = visual_diff_pages
            
            # Generate report
            try:
                report_path = self.generate_comparison_report_web(comparison_data, session_id)
                if report_path:
                    comparison_data['report_path'] = f"/download/{session_id}/{os.path.basename(report_path)}"
            except Exception as report_error:
                print(f"Report generation error: {report_error}")
                comparison_data['report_path'] = None
            
            doc1.close()
            doc2.close()
            
            print(f"Comparison completed: {total_text_changes} text changes, {visual_diff_pages} actual visual differences")
            return comparison_data
            
        except Exception as e:
            print(f"PDF comparison error: {e}")
            return None

    def create_difference_image(self, img1_path, img2_path, output_path):
        """Create a visual difference image highlighting changes"""
        try:
            from PIL import Image, ImageChops, ImageEnhance
            
            img1 = Image.open(img1_path).convert('RGB')
            img2 = Image.open(img2_path).convert('RGB')
            
            # Ensure same size
            if img1.size != img2.size:
                target_size = (max(img1.width, img2.width), max(img1.height, img2.height))
                img1 = img1.resize(target_size, Image.Resampling.LANCZOS)
                img2 = img2.resize(target_size, Image.Resampling.LANCZOS)
            
            # Create difference image
            diff = ImageChops.difference(img1, img2)
            
            # Enhance the difference to make it more visible
            enhancer = ImageEnhance.Contrast(diff)
            diff_enhanced = enhancer.enhance(3.0)
            
            # Convert to a more visible format
            diff_final = ImageChops.multiply(diff_enhanced, diff_enhanced)
            
            diff_final.save(output_path)
            print(f"✓ Created difference image: {output_path}")
            
        except Exception as e:
            print(f"Difference image creation error: {e}")
            raise

    def create_blank_page_image(self, output_path, page_num):
        """Create blank page image for missing pages"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            img_width, img_height = 600, 800
            image = Image.new('RGB', (img_width, img_height), (248, 248, 248))
            draw = ImageDraw.Draw(image)
            
            # Draw border
            draw.rectangle([10, 10, img_width-10, img_height-10], outline=(200, 200, 200), width=2)
            
            # Add text
            message = f"ಪುಟ {page_num}\n(ಈ ಫೈಲ್‌ನಲ್ಲಿ ಇಲ್ಲ)"
            
            try:
                font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), message, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = (img_width - text_width) // 2
                text_y = (img_height - text_height) // 2
                draw.text((text_x, text_y), message, fill=(150, 150, 150), font=font)
            except:
                draw.text((img_width//2 - 50, img_height//2), message, fill=(150, 150, 150))
            
            image.save(output_path, 'PNG')
            print(f"✓ Created blank page image: {output_path}")
            
        except Exception as e:
            print(f"Blank page image creation failed: {e}")
    def safe_text_extract_enhanced(self, page):
        """ENHANCED: Extract text with multiple fallback methods for corrupted Kannada"""
        try:
            # Method 1: Standard extraction
            text = self.safe_text_extract(page)  # Your existing method
            
            if text and self.is_text_readable(text):
                return text
            
            # Method 2: Try OCR if text seems corrupted
            print("⚠ Standard extraction failed, trying OCR...")
            try:
                from utils.pdf_ocr_processor import PDFOCRProcessor
                ocr_processor = PDFOCRProcessor()
                ocr_text = ocr_processor.extract_text_with_ocr(page)
                
                if ocr_text and len(ocr_text.strip()) > 0:
                    return self.clean_kannada_text(ocr_text)
                    
            except Exception as ocr_error:
                print(f"OCR extraction failed: {ocr_error}")
            
            # Method 3: Try raw text blocks
            try:
                text_dict = page.get_text("dict")
                raw_text_parts = []
                
                for block in text_dict.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                font_name = span.get("font", "").lower()
                                span_text = span.get("text", "")
                                
                                # Skip if font seems to be a symbol font
                                if any(keyword in font_name for keyword in ['symbol', 'wingding', 'dingbat']):
                                    continue
                                    
                                if span_text.strip():
                                    raw_text_parts.append(span_text)
                
                if raw_text_parts:
                    extracted_text = " ".join(raw_text_parts)
                    return self.clean_kannada_text(extracted_text)
                    
            except Exception as dict_error:
                print(f"Dictionary extraction failed: {dict_error}")
            
            return ""
            
        except Exception as e:
            print(f"Enhanced text extraction error: {e}")
            return ""

    def is_text_readable(self, text):
        """Check if extracted text is readable Kannada"""
        if not text or len(text.strip()) < 3:
            return False
        
        # Check for corruption indicators
        corruption_signs = ['\ufffd', '□', '??' * 3]  # 3 or more question marks
        for sign in corruption_signs:
            if sign in text:
                return False
        
        # Check for reasonable Kannada character ratio
        kannada_chars = sum(1 for char in text if '\u0c80' <= char <= '\u0cff')
        total_chars = len([c for c in text if c.isalnum()])
        
        if total_chars > 10 and kannada_chars > 0:
            return True
        
        # If mostly ASCII but has some recognizable words, might be transliterated
        if any(word in text.lower() for word in ['kannada', 'pdf', 'page', 'document']):
            return True
        
        return total_chars > 0  # At least some readable characters
    
    def generate_comparison_report_web(self, comparison_data, session_id):
        """Generate PDF report from HTML with proper Kannada support - FIXED VERSION"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            
            # First create HTML file
            html_path = f"output/{session_id}_comparison_report.html"
            pdf_path = f"output/{session_id}_comparison_report.pdf"
            
            # CRITICAL: Count both added and removed changes properly
            total_added = 0
            total_removed = 0
            
            for page_comp in comparison_data['page_comparisons']:
                for change in page_comp.get('text_changes', []):
                    if change['type'] == 'added':
                        total_added += 1
                    elif change['type'] == 'removed':
                        total_removed += 1
            
            print(f"DEBUG: Report will include {total_added} added changes and {total_removed} removed changes")
            
            # Create HTML content with embedded CSS for proper Kannada rendering
            html_content = f"""
    <!DOCTYPE html>
    <html lang="kn">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @font-face {{
                font-family: 'KannadaFont';
                src: url('https://fonts.googleapis.com/css2?family=Noto+Sans+Kannada:wght@400;600&display=swap');
            }}
            
            body {{
                font-family: 'KannadaFont', 'Noto Sans Kannada', Arial, sans-serif !important;
                margin: 20px;
                line-height: 1.6;
                color: #333;
                font-size: 14px;
            }}
            
            .header {{
                text-align: center;
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 30px;
                color: #8b7355;
                border-bottom: 2px solid #d4af37;
                padding-bottom: 10px;
            }}
            
            .summary-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
                font-size: 12px;
            }}
            
            .summary-table td {{
                padding: 10px;
                border: 1px solid #ddd;
                vertical-align: top;
            }}
            
            .summary-table .label {{
                background: #f5f1e8;
                font-weight: 600;
                width: 200px;
            }}
            
            .section-title {{
                font-size: 18px;
                font-weight: 600;
                margin: 30px 0 15px 0;
                color: #8b7355;
                border-bottom: 1px solid #d4af37;
                padding-bottom: 5px;
            }}
            
            .page-title {{
                font-weight: 600;
                margin: 20px 0 10px 0;
                color: #5d4037;
                font-size: 14px;
            }}
            
            .change-item {{
                margin: 8px 0;
                padding: 12px;
                border-left: 4px solid #ccc;
                background: #f9f9f9;
                font-size: 12px;
                line-height: 1.5;
                word-wrap: break-word;
                page-break-inside: avoid;
            }}
            
            .added {{
                border-left-color: #4caf50;
                background: #f1f8e9;
            }}
            
            .removed {{
                border-left-color: #f44336;
                background: #ffebee;
            }}
            
            .change-label {{
                font-weight: 600;
                display: inline-block;
                margin-bottom: 5px;
            }}
            
            .change-text {{
                display: block;
                margin-left: 10px;
            }}
            
            .no-changes {{
                text-align: center;
                color: #666;
                font-style: italic;
                padding: 20px;
            }}
            
            .footer {{
                margin-top: 40px;
                text-align: center;
                color: #666;
                font-size: 10px;
                border-top: 1px solid #ddd;
                padding-top: 10px;
            }}
            
            /* Print-specific styles */
            @media print {{
                body {{ margin: 0; }}
                .change-item {{ page-break-inside: avoid; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">PDF ಹೋಲಿಕೆ ವರದಿ</div>
        
        <table class="summary-table">
            <tr><td class="label">ಮೊದಲ ಫೈಲ್:</td><td>{comparison_data['file1_name']}</td></tr>
            <tr><td class="label">ಎರಡನೇ ಫೈಲ್:</td><td>{comparison_data['file2_name']}</td></tr>
            <tr><td class="label">ಮೊದಲ ಫೈಲ್‌ನ ಪುಟಗಳು:</td><td>{comparison_data['file1_pages']}</td></tr>
            <tr><td class="label">ಎರಡನೇ ಫೈಲ್‌ನ ಪುಟಗಳು:</td><td>{comparison_data['file2_pages']}</td></tr>
            <tr><td class="label">ಒಟ್ಟು ಪಠ್ಯ ಬದಲಾವಣೆಗಳು:</td><td>{comparison_data['summary']['total_text_changes']}</td></tr>
            <tr><td class="label">ಸೇರಿಸಲಾದ ಸಾಲುಗಳು:</td><td>{total_added}</td></tr>
            <tr><td class="label">ತೆಗೆದುಹಾಕಲಾದ ಸಾಲುಗಳು:</td><td>{total_removed}</td></tr>
        </table>
        
        <div class="section-title">ಪಠ್ಯ ವ್ಯತ್ಯಾಸಗಳು</div>
    """
            
            # CRITICAL: Process ALL changes, both added and removed
            if comparison_data['summary']['total_text_changes'] > 0:
                change_count = 0
                max_changes = 100  # Increase limit to capture more changes
                
                for page_comp in comparison_data['page_comparisons']:
                    if page_comp.get('text_changes') and change_count < max_changes:
                        html_content += f'<div class="page-title">ಪುಟ {page_comp["page_number"]}:</div>'
                        
                        # FIXED: Process ALL changes without limiting by type
                        for change in page_comp['text_changes']:
                            if change_count >= max_changes:
                                html_content += '<div class="change-item"><em>... ಇನ್ನಷ್ಟು ಬದಲಾವಣೆಗಳಿವೆ</em></div>'
                                break
                            
                            # Clean the text properly for HTML
                            change_text = self.clean_text_for_html(change['text'])
                            
                            if change['type'] == 'added':
                                html_content += f'''
                                <div class="change-item added">
                                    <span class="change-label">+ ಸೇರಿಸಲಾಗಿದೆ:</span>
                                    <span class="change-text">{change_text}</span>
                                </div>
                                '''
                                print(f"DEBUG: Added change #{change_count + 1}: {change_text[:50]}...")
                            elif change['type'] == 'removed':
                                html_content += f'''
                                <div class="change-item removed">
                                    <span class="change-label">- ತೆಗೆದುಹಾಕಲಾಗಿದೆ:</span>
                                    <span class="change-text">{change_text}</span>
                                </div>
                                '''
                                print(f"DEBUG: Removed change #{change_count + 1}: {change_text[:50]}...")
                            
                            change_count += 1
                        
                        if change_count >= max_changes:
                            break
                
                print(f"DEBUG: Total changes processed for report: {change_count}")
                
            else:
                html_content += '<div class="no-changes">ಯಾವುದೇ ಪಠ್ಯ ವ್ಯತ್ಯಾಸಗಳು ಕಂಡುಬಂದಿಲ್ಲ</div>'
            
            html_content += '''
        <div class="footer">
            ಈ ವರದಿಯನ್ನು ಕನ್ನಡ PDF ಉಪಕರಣಗಳಿಂದ ರಚಿಸಲಾಗಿದೆ
        </div>
    </body>
    </html>
    '''
            
            # Write HTML file
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✓ HTML report created: {html_path}")
            
            # Try to convert to PDF using multiple methods
            # Method 1: Try Playwright (best for Kannada)
            try:
                playwright_pdf = self.generate_pdf_with_playwright(html_path, pdf_path)
                if playwright_pdf and os.path.exists(playwright_pdf) and os.path.getsize(playwright_pdf) > 1000:
                    print(f"✓ PDF report generated with Playwright: {pdf_path}")
                    return pdf_path
            except Exception as e:
                print(f"⚠ Playwright failed: {e}")
            
            # Method 2: Try wkhtmltopdf
            try:
                import pdfkit
                options = {
                    'page-size': 'A4',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                    'encoding': "UTF-8",
                    'no-outline': None,
                    'enable-local-file-access': None,
                }
                
                pdfkit.from_file(html_path, pdf_path, options=options)
                
                if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
                    print(f"✓ PDF report generated with wkhtmltopdf: {pdf_path}")
                    return pdf_path
                    
            except ImportError:
                print("⚠ pdfkit not available")
            except Exception as e:
                print(f"⚠ wkhtmltopdf failed: {e}")
            
            # Method 3: Try WeasyPrint
            try:
                from weasyprint import HTML, CSS
                css = CSS(string='''
                    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Kannada:wght@400;600&display=swap');
                    body { font-family: 'Noto Sans Kannada', Arial, sans-serif !important; }
                ''')
                
                HTML(filename=html_path).write_pdf(pdf_path, stylesheets=[css])
                
                if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
                    print(f"✓ PDF generated using WeasyPrint: {pdf_path}")
                    return pdf_path
                    
            except ImportError:
                print("⚠ WeasyPrint not available")
            except Exception as e:
                print(f"⚠ WeasyPrint failed: {e}")
            
            # Fallback: Return HTML file
            print("⚠ PDF generation failed, returning HTML file")
            return html_path
            
        except Exception as e:
            print(f"Report generation error: {e}")
            # Generate simple text report as ultimate fallback
            return self.generate_enhanced_text_report(comparison_data, session_id)

    def clean_text_for_html(self, text):
        """Clean text for HTML display with proper Kannada handling"""
        try:
            if not text:
                return ""
            
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            
            text = str(text)
            
            # Normalize Unicode for Kannada
            text = unicodedata.normalize('NFC', text)
            
            # Remove only problematic characters
            text = text.replace('\x00', '')
            text = text.replace('\ufeff', '')
            text = text.replace('\ufffd', '[?]')
            
            # Basic HTML escaping for special characters (but preserve Kannada)
            text = text.replace('&', '&amp;')
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;')
            text = text.replace('"', '&quot;')
            
            # Clean whitespace but preserve line breaks
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                cleaned_line = ' '.join(line.split())
                if cleaned_line:
                    cleaned_lines.append(cleaned_line)
            
            result = '<br>'.join(cleaned_lines) if len(cleaned_lines) > 1 else ' '.join(cleaned_lines)
            
            # Limit length to prevent huge blocks
            if len(result) > 500:
                result = result[:497] + "..."
            
            return result
            
        except Exception as e:
            print(f"HTML text cleaning error: {e}")
            return "[ಪಠ್ಯ ಸ್ವಚ್ಛಗೊಳಿಸುವ ದೋಷ]"

    def convert_html_to_pdf_alternative(self, html_path, pdf_path):
        """Alternative HTML to PDF conversion method"""
        try:
            # Try using weasyprint if available
            from weasyprint import HTML, CSS
            
            # Custom CSS for better Kannada rendering
            css = CSS(string='''
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Kannada:wght@400;600&display=swap');
                body { font-family: 'Noto Sans Kannada', Arial, sans-serif; }
            ''')
            
            HTML(filename=html_path).write_pdf(pdf_path, stylesheets=[css])
            
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
                print(f"✓ PDF generated using WeasyPrint: {pdf_path}")
                return pdf_path
            else:
                print("⚠ WeasyPrint failed, returning HTML")
                return html_path
                
        except ImportError:
            print("⚠ WeasyPrint not available")
            return html_path
        except Exception as e:
            print(f"⚠ Alternative PDF conversion failed: {e}")
            return html_path
    
    def generate_enhanced_text_report(self, comparison_data, session_id):
        """Generate enhanced Unicode text report as PDF fallback"""
        try:
            report_path = f"output/{session_id}_comparison_report.txt"
            
            with open(report_path, 'w', encoding='utf-8', newline='') as f:
                # Write BOM for better Unicode support
                f.write('\ufeff')
                
                f.write("PDF ಹೋಲಿಕೆ ವರದಿ\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"ಮೊದಲ ಫೈಲ್: {comparison_data['file1_name']}\n")
                f.write(f"ಎರಡನೇ ಫೈಲ್: {comparison_data['file2_name']}\n")
                f.write(f"ಮೊದಲ ಫೈಲ್‌ನ ಪುಟಗಳು: {comparison_data['file1_pages']}\n")
                f.write(f"ಎರಡನೇ ಫೈಲ್‌ನ ಪುಟಗಳು: {comparison_data['file2_pages']}\n\n")
                
                f.write("ಸಾರಾಂಶ:\n")
                f.write("-" * 30 + "\n")
                f.write(f"ಹೋಲಿಸಿದ ಪುಟಗಳು: {comparison_data['summary']['total_pages_compared']}\n")
                f.write(f"ಪಠ್ಯ ಬದಲಾವಣೆಗಳು: {comparison_data['summary']['total_text_changes']}\n")
                f.write(f"ದೃಶ್ಯ ವ್ಯತ್ಯಾಸಗಳು: {comparison_data['summary']['visual_diff_pages']} ಪುಟಗಳಲ್ಲಿ\n\n")
                
                # Add sample text changes
                if comparison_data['summary']['total_text_changes'] > 0:
                    f.write("ಪಠ್ಯ ಬದಲಾವಣೆಗಳ ಮಾದರಿ:\n")
                    f.write("-" * 40 + "\n")
                    
                    change_count = 0
                    for page_comp in comparison_data['page_comparisons']:
                        if change_count >= 10:
                            f.write("... ಇನ್ನಷ್ಟು ಬದಲಾವಣೆಗಳಿವೆ\n")
                            break
                            
                        if page_comp['text_changes']:
                            f.write(f"\nಪುಟ {page_comp['page_number']}:\n")
                            
                            for change in page_comp['text_changes'][:3]:
                                if change_count >= 10:
                                    break
                                    
                                change_text = change['text'][:150]
                                if change['type'] == 'added':
                                    f.write(f"  + ಸೇರಿಸಲಾಗಿದೆ: {change_text}\n")
                                else:
                                    f.write(f"  - ತೆಗೆದುಹಾಕಲಾಗಿದೆ: {change_text}\n")
                                
                                change_count += 1
                
                f.write(f"\n\n" + "=" * 60 + "\n")
                f.write("ಈ ವರದಿಯನ್ನು ಕನ್ನಡ PDF ಉಪಕರಣಗಳಿಂದ ರಚಿಸಲಾಗಿದೆ\n")
                f.write(f"ರಚನೆ ದಿನಾಂಕ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"✓ Enhanced text report created: {report_path}")
            return report_path
            
        except Exception as e:
            print(f"Enhanced text report error: {e}")
            raise Exception(f"ವರದಿ ರಚನೆ ಸಂಪೂರ್ಣ ವಿಫಲ: {str(e)}")
    
    

    # Legacy methods for backward compatibility
    def compare_pdfs(self, pdf1_path, pdf2_path, session_id, compare_type='both'):
        """Legacy method - redirects to web version"""
        return self.compare_pdfs_web(pdf1_path, pdf2_path, session_id, compare_type)
    
    
    
    def generate_comparison_report(self, comparison_data, session_id):
        """Legacy report generation - redirects to web version"""
        return self.generate_comparison_report_web(comparison_data, session_id)
    
    def generate_enhanced_pdf_image(self, page, output_path, page_num):
        """Generate PDF page image with font substitution for better Kannada display"""
        try:
            # Method 1: Try standard rendering first
            try:
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # High resolution
                pix.save(output_path)
                
                # Check if image was created successfully
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    print(f"✓ Standard image generation successful for page {page_num}")
                    return output_path
            except Exception as std_error:
                print(f"Standard image generation failed: {std_error}")
            
            # Method 2: Try with font substitution
            try:
                # Create a font substitution map for better Kannada rendering
                fontlist = fitz.Font()  # Get available fonts
                
                # Set font substitution for common Kannada fonts
                page.set_fontsize(12)  # Ensure readable size
                
                # Try rendering with enhanced settings
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2.5, 2.5),  # Even higher resolution
                    alpha=False,  # No transparency
                    annots=True   # Include annotations
                )
                
                pix.save(output_path)
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    print(f"✓ Enhanced image generation successful for page {page_num}")
                    return output_path
                    
            except Exception as enh_error:
                print(f"Enhanced image generation failed: {enh_error}")
            
            # Method 3: OCR-based image generation (if OCR processor available)
            try:
                from utils.pdf_ocr_processor import PDFOCRProcessor
                
                ocr_processor = PDFOCRProcessor()
                
                # Extract text using OCR
                extracted_text = ocr_processor.extract_text_with_ocr(page)
                
                if extracted_text and len(extracted_text.strip()) > 0:
                    # Create a new image with properly rendered Kannada text
                    self.create_text_image_with_kannada(extracted_text, output_path, page_num)
                    
                    if os.path.exists(output_path):
                        print(f"✓ OCR-based image generation successful for page {page_num}")
                        return output_path
                        
            except ImportError:
                print("OCR processor not available for enhanced image generation")
            except Exception as ocr_error:
                print(f"OCR-based image generation failed: {ocr_error}")
            
            # Method 4: Fallback - create placeholder image with error message
            print(f"⚠ Creating fallback image for page {page_num}")
            self.create_fallback_image(output_path, page_num)
            
            return output_path if os.path.exists(output_path) else None
            
        except Exception as e:
            print(f"All image generation methods failed for page {page_num}: {e}")
            return None

    def create_text_image_with_kannada(self, text, output_path, page_num):
        """Create an image from text with proper Kannada font rendering"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            
            # Create a large image
            img_width, img_height = 800, 1200
            background_color = (255, 255, 255)  # White
            text_color = (0, 0, 0)  # Black
            
            image = Image.new('RGB', (img_width, img_height), background_color)
            draw = ImageDraw.Draw(image)
            
            # Try to load a Kannada font
            font_paths = [
                os.path.join("static", "fonts", "NotoSansKannada-Regular.ttf"),
                "/System/Library/Fonts/Supplemental/NotoSansKannada.ttc",  # macOS
                "C:/Windows/Fonts/NotoSansKannada-Regular.ttf",  # Windows
                "/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf",  # Linux
            ]
            
            font = None
            font_size = 14
            
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, font_size)
                        print(f"✓ Loaded Kannada font: {font_path}")
                        break
                except Exception as font_error:
                    continue
            
            # Fallback to default font if no Kannada font found
            if font is None:
                try:
                    font = ImageFont.load_default()
                    print("⚠ Using default font - Kannada may not display correctly")
                except:
                    font = None
            
            # Add title
            title_text = f"ಪುಟ {page_num}"
            title_y = 20
            
            if font:
                try:
                    # Get text dimensions for centering
                    bbox = draw.textbbox((0, 0), title_text, font=font)
                    title_width = bbox[2] - bbox[0]
                    title_x = (img_width - title_width) // 2
                    draw.text((title_x, title_y), title_text, fill=text_color, font=font)
                except:
                    draw.text((20, title_y), title_text, fill=text_color)
            
            # Process and draw main text
            content_y = 60
            line_height = 25
            margin = 30
            max_width = img_width - (2 * margin)
            
            # Split text into lines that fit the image width
            lines = []
            paragraphs = text.split('\n')
            
            for paragraph in paragraphs:
                if not paragraph.strip():
                    lines.append('')
                    continue
                    
                # Wrap text to fit image width
                if font:
                    # Calculate approximate characters per line
                    avg_char_width = 8  # Approximate for most fonts
                    chars_per_line = max_width // avg_char_width
                    wrapped_lines = textwrap.wrap(paragraph, width=chars_per_line)
                    lines.extend(wrapped_lines)
                else:
                    lines.append(paragraph)
            
            # Draw text lines
            current_y = content_y
            
            for line in lines:
                if current_y > img_height - 50:  # Stop if we're near the bottom
                    draw.text((margin, current_y), "... (ಇನ್ನಷ್ಟು ಪಠ್ಯ)", fill=text_color, font=font)
                    break
                    
                if line.strip():
                    if font:
                        try:
                            draw.text((margin, current_y), line, fill=text_color, font=font)
                        except Exception as draw_error:
                            # Fallback to simple text drawing
                            draw.text((margin, current_y), line, fill=text_color)
                    else:
                        draw.text((margin, current_y), line, fill=text_color)
                
                current_y += line_height
            
            # Add footer
            footer_text = "ಕನ್ನಡ PDF ಉಪಕರಣಗಳು"
            footer_y = img_height - 30
            
            if font:
                try:
                    bbox = draw.textbbox((0, 0), footer_text, font=font)
                    footer_width = bbox[2] - bbox[0]
                    footer_x = (img_width - footer_width) // 2
                    draw.text((footer_x, footer_y), footer_text, fill=(128, 128, 128), font=font)
                except:
                    draw.text((margin, footer_y), footer_text, fill=(128, 128, 128))
            
            # Save the image
            image.save(output_path, 'PNG', quality=95)
            print(f"✓ Created text-based image: {output_path}")
            
        except Exception as e:
            print(f"Text-based image creation failed: {e}")
            # Create a simple placeholder
            self.create_fallback_image(output_path, page_num)

    def create_fallback_image(self, output_path, page_num):
        """Create a fallback placeholder image"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            img_width, img_height = 600, 800
            image = Image.new('RGB', (img_width, img_height), (245, 245, 245))
            draw = ImageDraw.Draw(image)
            
            # Draw border
            draw.rectangle([10, 10, img_width-10, img_height-10], outline=(200, 200, 200), width=2)
            
            # Add text
            messages = [
                f"ಪುಟ {page_num}",
                "",
                "ಈ ಪುಟದ ವಿಷಯವನ್ನು",
                "ಪ್ರದರ್ಶಿಸಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ",
                "",
                "ಮೂಲ PDF ನಲ್ಲಿ ಫಾಂಟ್",
                "ಸಮಸ್ಯೆಗಳಿರಬಹುದು"
            ]
            
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            start_y = img_height // 2 - (len(messages) * 20) // 2
            
            for i, message in enumerate(messages):
                text_y = start_y + (i * 25)
                
                if font:
                    try:
                        bbox = draw.textbbox((0, 0), message, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_x = (img_width - text_width) // 2
                        draw.text((text_x, text_y), message, fill=(100, 100, 100), font=font)
                    except:
                        draw.text((50, text_y), message, fill=(100, 100, 100))
                else:
                    draw.text((50, text_y), message, fill=(100, 100, 100))
            
            image.save(output_path, 'PNG')
            print(f"✓ Created fallback image: {output_path}")
            
        except Exception as e:
            print(f"Fallback image creation failed: {e}")
            # Create minimal file to prevent errors
            try:
                with open(output_path, 'wb') as f:
                    f.write(b'')
            except:
                pass
    def generate_pdf_with_playwright(self, html_path, pdf_path):
        """Use browser to generate PDF (best Kannada support)"""
        try:
            # Install: pip install playwright
            # Run: playwright install chromium
            from playwright.sync_api import sync_playwright
        
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                
                # Load HTML file
                page.goto(f"file://{os.path.abspath(html_path)}")
                
                # Wait for fonts to load
                page.wait_for_timeout(3000)  # Increase wait time
                
                # Generate PDF with font embedding
                page.pdf(
                    path=pdf_path, 
                    format='A4',
                    print_background=True,  # Add this
                    prefer_css_page_size=True  # Add this
                )
                browser.close()
                
            return pdf_path
        except Exception as e:
            print(f"Playwright PDF error: {e}")
            return None
    
    def normalize_text_for_comparison(self, text):
        """CRITICAL FIX: Normalize text to handle bullet points and formatting consistently"""
        try:
            if not text:
                return ""
            
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            
            text = str(text)
            text = unicodedata.normalize('NFC', text)
            
            # STEP 1: Replace common bullet point variations with standard bullet
            bullet_patterns = [
                # Unicode bullet points
                '•', '◦', '‣', '⁃', '▪', '▫', '◾', '◽', '▸', '▹',
                # ASCII alternatives often seen in OCR
                '*', '-', '+', '>', '→', '➤', '➢', '➣',
                # Common OCR mistakes for bullets
                '·', '°', '∙', '⋅', '∘',
                # Random characters that OCR might produce
                '❖', '❘', '⦿', '⦾', '●', '○',
                # Dingbat characters
                '✓', '✔', '☑', '▲', '►', '▶',
            ]
            
            # Replace all bullet variations with standard bullet
            for pattern in bullet_patterns:
                text = text.replace(pattern, '•')
            
            # STEP 2: Handle numbered lists (1., 2., a., b., i., ii., etc.)
            import re
            
            # Replace numbered lists with generic marker
            # Matches patterns like "1.", "2)", "a.", "i)", "(1)", "[a]", etc.
            numbering_patterns = [
                r'\b\d+\.\s*',           # 1. 2. 3.
                r'\b\d+\)\s*',           # 1) 2) 3)
                r'\(\d+\)\s*',           # (1) (2) (3)
                r'\[\d+\]\s*',           # [1] [2] [3]
                r'\b[a-z]\.\s*',         # a. b. c.
                r'\b[a-z]\)\s*',         # a) b) c)
                r'\([a-z]\)\s*',         # (a) (b) (c)
                r'\b[ivx]+\.\s*',        # i. ii. iii. (Roman numerals)
                r'\b[ivx]+\)\s*',        # i) ii) iii)
                r'\b[IVX]+\.\s*',        # I. II. III.
                r'\b[IVX]+\)\s*',        # I) II) III)
            ]
            
            for pattern in numbering_patterns:
                text = re.sub(pattern, '• ', text, flags=re.IGNORECASE)
            
            # STEP 3: Clean up OCR artifacts around bullets
            # Remove extra spaces around bullets
            text = re.sub(r'\s*•\s+', '• ', text)
            text = re.sub(r'\n\s*•\s*', '\n• ', text)
            
            # STEP 4: Handle common OCR character substitutions
            ocr_fixes = {
                # Common Kannada OCR mistakes
                '|': 'ಲ್',
                '॒': 'ೃ',
                '॑': 'ೆ',
                'ॐ': 'ಓಂ',
                # Common punctuation OCR mistakes
                '"': '"',
                '"': '"',
                ''': "'",
                ''': "'",
                '…': '...',
                '–': '-',
                '—': '-',
                # Remove invisible characters
                '\u200b': '',  # Zero-width space
                '\u200c': '',  # Zero-width non-joiner
                '\u200d': '',  # Zero-width joiner
                '\ufeff': '',  # BOM
            }
            
            for wrong, correct in ocr_fixes.items():
                text = text.replace(wrong, correct)
            
            # STEP 5: Normalize whitespace
            lines = text.split('\n')
            normalized_lines = []
            
            for line in lines:
                # Remove excessive spaces but preserve structure
                cleaned_line = ' '.join(line.split())
                
                # Skip empty lines or lines with just bullets
                if cleaned_line and cleaned_line not in ['•', '• ']:
                    normalized_lines.append(cleaned_line)
            
            return '\n'.join(normalized_lines)
            
        except Exception as e:
            print(f"Text normalization error: {e}")
            return text if isinstance(text, str) else ""

    def compare_texts_intelligently(self, text1, text2):
        """SMART comparison that ignores formatting differences"""
        try:
            # Normalize both texts
            norm_text1 = self.normalize_text_for_comparison(text1)
            norm_text2 = self.normalize_text_for_comparison(text2)
            
            # Split into lines for comparison
            lines1 = norm_text1.split('\n')
            lines2 = norm_text2.split('\n')
            
            # Use difflib for intelligent comparison
            import difflib
            
            # Create detailed diff
            differ = difflib.unified_diff(
                lines1, lines2,
                lineterm='',
                n=1  # Reduced context for cleaner output
            )
            
            meaningful_changes = []
            
            for change in differ:
                # Skip diff headers
                if change.startswith('+++') or change.startswith('---') or change.startswith('@@'):
                    continue
                
                if len(change) <= 1:
                    continue
                    
                change_text = change[1:].strip()
                
                # CRITICAL: Filter out meaningless changes
                if self.is_meaningful_change(change_text):
                    if change.startswith('+'):
                        meaningful_changes.append({
                            'type': 'added',
                            'text': change_text
                        })
                    elif change.startswith('-'):
                        meaningful_changes.append({
                            'type': 'removed',
                            'text': change_text
                        })
            
            return meaningful_changes
            
        except Exception as e:
            print(f"Intelligent comparison error: {e}")
            return []

    def is_meaningful_change(self, text):
        """Determine if a text change is meaningful or just formatting noise"""
        try:
            if not text or len(text.strip()) < 2:
                return False
            
            # Filter out meaningless changes
            meaningless_patterns = [
                # Just bullets or list markers
                r'^[•\-\+\*]+\s*$',
                # Just numbers or letters (list numbering)
                r'^\d+[\.\)]*\s*$',
                r'^[a-zA-Z][\.\)]*\s*$',
                r'^[ivxIVX]+[\.\)]*\s*$',
                # Just punctuation
                r'^[\.\,\;\:\!\?\-\–\—\"\'\`\~]+$',
                # Just spaces or whitespace
                r'^\s+$',
                # Single characters that are likely OCR noise
                r'^[^\w\u0C80-\u0CFF]{1,2}$',  # Non-word chars except Kannada
                # Common OCR artifacts
                r'^[\|\]\[\(\)\{\}]+$',
            ]
            
            import re
            for pattern in meaningless_patterns:
                if re.match(pattern, text.strip()):
                    return False
            
            # Check if change is substantial enough
            # Must have at least 3 characters or contain Kannada/meaningful words
            if len(text.strip()) >= 3:
                return True
            
            # Check if it contains meaningful Kannada characters
            kannada_chars = sum(1 for char in text if '\u0c80' <= char <= '\u0cff')
            if kannada_chars > 0:
                return True
            
            # Check if it contains meaningful English words
            meaningful_words = ['the', 'and', 'or', 'is', 'are', 'was', 'were', 'have', 'has', 'had']
            if any(word in text.lower() for word in meaningful_words):
                return True
            
            return False
            
        except Exception as e:
            print(f"Meaningful change check error: {e}")
            return True  # Default to including if we can't determine
