import os
import zipfile
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import config
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document
import html
import platform
import subprocess
import shutil
from pathlib import Path
import io

class PDFOperations:
    def __init__(self):
        self.config = config.Config()
    
    def merge_pdfs(self, file_paths, session_id):
        """Merge multiple PDF files"""
        try:
            if not file_paths or len(file_paths) < 2:
                raise Exception("ವಿಲೀನಕ್ಕೆ ಕನಿಷ್ಠ 2 PDF ಫೈಲ್‌ಗಳು ಅಗತ್ಯ")
        
            valid_files = []
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    continue
                
                if os.path.getsize(file_path) == 0:
                    continue
            
                try:
                    reader = PdfReader(file_path)
                    if len(reader.pages) > 0:
                        valid_files.append(file_path)
                except Exception:
                    continue
        
            if len(valid_files) < 2:
                raise Exception("ವಿಲೀನಕ್ಕೆ ಕನಿಷ್ಠ 2 ಸರಿಯಾದ PDF ಫೈಲ್‌ಗಳು ಅಗತ್ಯ")
            
            writer = PdfWriter()
            
            for file_path in valid_files:
                try:
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        writer.add_page(page)
                except Exception as e:
                    continue
            
            output_filename = f"{session_id}_merged.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise Exception("ವಿಲೀನ ಫೈಲ್ ರಚನೆ ವಿಫಲವಾಗಿದೆ")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF ವಿಲೀನ ವಿಫಲ: {str(e)}")

    def split_pdf(self, file_path, session_id, pages=""):
        """Split PDF into separate files"""
        try:
            if not os.path.exists(file_path):
                raise Exception("PDF ಫೈಲ್ ಸಿಗಲಿಲ್ಲ")
            
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            
            if total_pages < 2:
                raise Exception("ವಿಭಜನೆಗೆ ಕನಿಷ್ಠ 2 ಪುಟಗಳು ಬೇಕಾಗುತ್ತವೆ")
            
            if pages:
                page_ranges = self._parse_page_ranges(pages, total_pages)
                
                output_filename = f"{session_id}_split.pdf"
                output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
                
                writer = PdfWriter()
                for page_num in page_ranges:
                    if 1 <= page_num <= total_pages:
                        writer.add_page(reader.pages[page_num - 1])
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                return output_path
            else:
                split_folder = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_split")
                os.makedirs(split_folder, exist_ok=True)
                
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    
                    page_filename = f"page_{i+1}.pdf"
                    page_path = os.path.join(split_folder, page_filename)
                    
                    with open(page_path, 'wb') as output_file:
                        writer.write(output_file)
                
                zip_filename = f"{session_id}_split.zip"
                zip_path = os.path.join(self.config.OUTPUT_FOLDER, zip_filename)
                
                with zipfile.ZipFile(zip_path, 'w') as zip_file:
                    for root, dirs, files in os.walk(split_folder):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zip_file.write(file_path, file)
                
                shutil.rmtree(split_folder)
                return zip_path
                
        except Exception as e:
            raise Exception(f"PDF ವಿಭಜನೆ ವಿಫಲ: {str(e)}")

    def _parse_page_ranges(self, pages_str, total_pages):
        """Parse page ranges like '1,3,5-10' into list of page numbers"""
        pages = []
        parts = pages_str.replace(' ', '').split(',')
        
        for part in parts:
            if '-' in part:
                start, end = part.split('-', 1)
                try:
                    start_num = int(start)
                    end_num = int(end)
                    pages.extend(range(start_num, end_num + 1))
                except ValueError:
                    continue
            else:
                try:
                    pages.append(int(part))
                except ValueError:
                    continue
        
        return [p for p in pages if 1 <= p <= total_pages]

    def extract_pages(self, file_path, pages, session_id):
        """Extract specific pages from PDF"""
        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            page_numbers = self._parse_page_ranges(pages, total_pages)
            
            if not page_numbers:
                raise Exception("ಸರಿಯಾದ ಪುಟ ಸಂಖ್ಯೆಗಳನ್ನು ನಮೂದಿಸಿ")
            
            writer = PdfWriter()
            for page_num in page_numbers:
                writer.add_page(reader.pages[page_num - 1])
            
            output_filename = f"{session_id}_extracted.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"ಪುಟ ಹೊರತೆಗೆಯುವಿಕೆ ವಿಫಲ: {str(e)}")

    def delete_pages(self, file_path, pages, session_id):
        """Delete specific pages from PDF"""
        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            pages_to_delete = set(self._parse_page_ranges(pages, total_pages))
            
            writer = PdfWriter()
            for i, page in enumerate(reader.pages):
                if (i + 1) not in pages_to_delete:
                    writer.add_page(page)
            
            output_filename = f"{session_id}_deleted.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"ಪುಟ ಅಳಿಸುವಿಕೆ ವಿಫಲ: {str(e)}")

    def compress_pdf(self, file_path, compression_level, session_id):
        """Compress PDF file"""
        try:
            output_filename = f"{session_id}_compressed.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            try:
                return self._compress_pymupdf(file_path, output_path, compression_level)
            except Exception:
                return self._compress_pypdf2(file_path, output_path, compression_level)
                
        except Exception as e:
            raise Exception(f"PDF ಸಂಕುಚನ ವಿಫಲ: {str(e)}")

    def _compress_pymupdf(self, input_path, output_path, level):
        """Compress PDF using PyMuPDF"""
        doc = fitz.open(input_path)
        
        deflate_level = {
            'low': 1,
            'medium': 6,
            'high': 9
        }.get(level, 6)
        
        doc.save(output_path, deflate=True, deflate_level=deflate_level, clean=True)
        doc.close()
        
        return output_path

    def _compress_pypdf2(self, input_path, output_path, level):
        """Compress PDF using PyPDF2"""
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path

    def pdf_to_images(self, file_path, session_id):
        """Convert PDF pages to JPEG images"""
        try:
            doc = fitz.open(file_path)
            images_folder = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_images")
            os.makedirs(images_folder, exist_ok=True)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                
                image_filename = f"page_{page_num + 1}.jpg"
                image_path = os.path.join(images_folder, image_filename)
                pix.save(image_path)
            
            doc.close()
            
            zip_filename = f"{session_id}_images.zip"
            zip_path = os.path.join(self.config.OUTPUT_FOLDER, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for root, dirs, files in os.walk(images_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zip_file.write(file_path, file)
            
            shutil.rmtree(images_folder)
            return zip_path
            
        except Exception as e:
            raise Exception(f"PDF ಚಿತ್ರ ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")

    def images_to_pdf(self, image_paths, session_id):
        """Convert images to PDF"""
        try:
            output_filename = f"{session_id}_from_images.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            images = []
            for image_path in image_paths:
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
            
            if images:
                images[0].save(output_path, save_all=True, append_images=images[1:])
            
            return output_path
            
        except Exception as e:
            raise Exception(f"ಚಿತ್ರ PDF ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")

    def pdf_to_word(self, file_path, session_id):
        """Convert PDF to Word document"""
        try:
            doc = fitz.open(file_path)
            word_doc = Document()
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if text.strip():
                    word_doc.add_paragraph(text)
                
                if page_num < len(doc) - 1:
                    word_doc.add_page_break()
            
            doc.close()
            
            output_filename = f"{session_id}_converted.docx"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            word_doc.save(output_path)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF Word ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")

    def word_to_pdf(self, file_path, session_id):
        """Convert Word document to PDF"""
        try:
            return self._simple_word_to_pdf(file_path, session_id)
        except Exception as e:
            raise Exception(f"Word PDF ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")

    def _simple_word_to_pdf(self, file_path, session_id):
        """Simple Word to PDF conversion"""
        doc = Document(file_path)
        
        output_filename = f"{session_id}_from_word.pdf"
        output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
        
        pdf_doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                p = Paragraph(html.escape(para.text), styles['Normal'])
                story.append(p)
                story.append(Spacer(1, 12))
        
        pdf_doc.build(story)
        return output_path

    def sort_pdf_by_page_numbers(self, file_path, session_id, pages=""):
        """Sort PDF pages by detected Kannada page numbers"""
        try:
            from .kannada_numeral_converter import KannadaNumeralConverter
            
            converter = KannadaNumeralConverter()
            doc = fitz.open(file_path)
            
            page_data = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                extracted_number = converter.extract_page_number_from_text(text)
                
                page_data.append({
                    'page': page,
                    'original_num': page_num + 1,
                    'extracted_num': extracted_number if extracted_number else page_num + 1
                })
            
            page_data.sort(key=lambda x: x['extracted_num'])
            
            output_filename = f"{session_id}_sortedbynum.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            new_doc = fitz.open()
            for data in page_data:
                new_doc.insert_pdf(doc, from_page=data['original_num']-1, to_page=data['original_num']-1)
            
            new_doc.save(output_path)
            new_doc.close()
            doc.close()
            
            return output_path
            
        except Exception as e:
            raise Exception(f"ಪುಟ ಸಾರಿಸುವಿಕೆ ವಿಫಲ: {str(e)}")

    def get_page_sorting_preview(self, file_path, session_id):
        """Generate preview for page sorting"""
        try:
            from .kannada_numeral_converter import KannadaNumeralConverter
            
            converter = KannadaNumeralConverter()
            doc = fitz.open(file_path)
            
            previews = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                extracted_number = converter.extract_page_number_from_text(text)
                
                thumbnail_path = self._generate_page_thumbnail(page, page_num + 1, session_id)
                
                previews.append({
                    'page_num': page_num + 1,
                    'extracted_number': extracted_number if extracted_number else page_num + 1,  # Fixed field name
                    'thumbnail_path': thumbnail_path
                })
            
            # Sort previews by extracted number to show the expected order
            sorted_previews = sorted(previews, key=lambda x: x['extracted_number'])  # Fixed field name
            
            # For the sorted_order, we need to return the sorted preview objects with proper field names
            sorted_order = []
            for preview in sorted_previews:
                sorted_order.append({
                    'page_num': preview['page_num'],
                    'extracted_number': preview['extracted_number'],  # This field name matches template
                    'thumbnail_path': preview['thumbnail_path']
                })
            
            doc.close()
            
            return {
                'total_pages': len(previews),
                'previews': previews,
                'sorted_order': sorted_order
            }
            
        except Exception as e:
            return {'error': f'ಪೂರ್ವವೀಕ್ಷಣೆ ರಚನೆ ವಿಫಲ: {str(e)}'}

    def _generate_page_thumbnail(self, page, page_num, session_id):
        """Generate a thumbnail image for a PDF page with automatic orientation detection"""
        try:
            import os
            from PIL import Image
            import io
            
            thumbnails_dir = os.path.join(self.config.OUTPUT_FOLDER, 'thumbnails', session_id)
            os.makedirs(thumbnails_dir, exist_ok=True)
            
            import time
            timestamp = int(time.time() * 1000)
            thumbnail_filename = f"page_{page_num}_{timestamp}.png"
            thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
            
            zoom = 1.5
            mat = fitz.Matrix(zoom, zoom)
            
            # Get page information
            page_rotation = page.rotation
            page_rect = page.rect
            
            # Get pixmap without pre-rotation
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Smart orientation detection
            needs_rotation = False
            rotation_angle = 0
            
            # First, handle explicit page rotation from PDF
            if page_rotation != 0:
                # Handle rotated pages by rotating them back to normal
                if page_rotation == 90:
                    rotation_angle = -90
                    needs_rotation = True
                elif page_rotation == 180:
                    rotation_angle = 180  
                    needs_rotation = True
                elif page_rotation == 270:
                    rotation_angle = 90
                    needs_rotation = True
            else:
                # For pages with 0 rotation, try to detect if they're upside down
                # This is a heuristic based on text analysis
                try:
                    text_content = page.get_text()
                    
                    # If page has text, try to determine orientation
                    if text_content and len(text_content.strip()) > 10:
                        # Get text blocks with position information
                        blocks = page.get_text("dict")
                        
                        # Analyze text orientation heuristics
                        # Check if most text appears to be in normal reading order
                        normal_text_indicators = 0
                        total_text_blocks = 0
                        
                        for block in blocks.get("blocks", []):
                            if "lines" in block:
                                total_text_blocks += 1
                                for line in block["lines"]:
                                    for span in line.get("spans", []):
                                        text = span.get("text", "").strip()
                                        if text:
                                            # Check for Kannada or English characters in normal positions
                                            # If y-coordinates increase downward, text is likely normal
                                            # This is a simplified heuristic
                                            if any(c.isalnum() or ord(c) >= 0x0c80 for c in text):
                                                normal_text_indicators += 1
                        
                        # If we have very few normal text indicators relative to total blocks,
                        # the page might be upside down
                        if total_text_blocks > 0 and normal_text_indicators < (total_text_blocks * 0.3):
                            rotation_angle = 180
                            needs_rotation = True
                        
                except Exception as text_analysis_error:
                    # If text analysis fails, use simple dimension heuristic
                    # Many scanned documents appear upside down when height > width
                    page_width = page_rect.width
                    page_height = page_rect.height
                    
                    # This is a last resort heuristic - don't rotate by default
                    # Let users manually rotate if needed
                    pass
            
            # Apply rotation if needed
            if needs_rotation and rotation_angle != 0:
                img = img.rotate(rotation_angle, expand=True)
            
            thumbnail_size = (150, 200)
            img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            
            img.save(thumbnail_path, "PNG", optimize=True)
            
            return f'/thumbnails/{session_id}/{thumbnail_filename}'
            
        except Exception as e:
            print(f"Thumbnail generation error: {str(e)}")
            return None

    def add_watermark(self, file_path, session_id, watermark_options):
        """Add watermark to PDF with comprehensive options"""
        try:
            from .validators import validate_watermark_options
            import re
            
            is_valid, message = validate_watermark_options(watermark_options)
            if not is_valid:
                raise Exception(message)
            
            output_filename = f"{session_id}_watermarked.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            # Determine which pages to apply watermark to
            pages_to_process = self._get_pages_to_process(watermark_options, total_pages)
            
            for page_num in pages_to_process:
                if page_num < total_pages:  # Safety check
                    page = doc[page_num]
                    
                    if watermark_options['type'] == 'text':
                        self._add_text_watermark(page, watermark_options)
                    else:
                        self._add_image_watermark(page, watermark_options)
            
            doc.save(output_path)
            doc.close()
            
            return {
                'success': True,
                'output_path': output_path,
                'filename': output_filename,
                'message': f'ವಾಟರ್‌ಮಾರ್ಕ್ ಯಶಸ್ವಿಯಾಗಿ ಸೇರಿಸಲಾಗಿದೆ - {len(pages_to_process)} ಪುಟಗಳಲ್ಲಿ'
            }
            
        except Exception as e:
            raise Exception(f"ವಾಟರ್‌ಮಾರ್ಕ್ ಸೇರಿಸುವಿಕೆ ವಿಫಲ: {str(e)}")

    def _get_pages_to_process(self, options, total_pages):
        """Determine which pages to apply watermark based on options"""
        pages_filter = options.get('watermark_pages', 'all')
        
        if pages_filter == 'all':
            return list(range(total_pages))
        elif pages_filter == 'odd':
            return [i for i in range(total_pages) if (i + 1) % 2 == 1]  # 1-based odd pages
        elif pages_filter == 'even':
            return [i for i in range(total_pages) if (i + 1) % 2 == 0]  # 1-based even pages
        elif pages_filter == 'custom':
            custom_pages = options.get('custom_pages', '')
            if custom_pages:
                return self._parse_watermark_page_ranges(custom_pages, total_pages)
            else:
                return list(range(total_pages))
        else:
            return list(range(total_pages))

    def _parse_watermark_page_ranges(self, pages_str, total_pages):
        """Parse page ranges like '1,3,5-10' into list of 0-based page indices"""
        pages = []
        parts = pages_str.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    # Convert to 0-based and ensure valid range
                    start = max(1, min(start, total_pages)) - 1
                    end = max(1, min(end, total_pages)) - 1
                    pages.extend(range(start, end + 1))
                except ValueError:
                    continue
            else:
                try:
                    page_num = int(part)
                    if 1 <= page_num <= total_pages:
                        pages.append(page_num - 1)  # Convert to 0-based
                except ValueError:
                    continue
        
        return sorted(list(set(pages)))  # Remove duplicates and sort

    def _add_text_watermark(self, page, options):
        """Add text watermark to page with enhanced features"""
        rect = page.rect
        text = options.get('text', 'ವಾಟರ್‌ಮಾರ್ಕ್')
        font_size = float(options.get('font_size', 50))
        rotation = float(options.get('rotation', 0))
        opacity = float(options.get('opacity', 50)) / 100.0
        color = options.get('color', '#000000')
        font_family = options.get('font_family', 'Helvetica')
        position = options.get('position', 'center')
        layer_position = options.get('layer_position', 'below')
        repeat_watermark = options.get('repeat_watermark', False)
        
        # Enhanced Kannada font support
        if self._is_kannada_text(text) or font_family == 'noto-sans-kannada':
            font_family = 'noto-sans-kannada'
        
        # Calculate positions
        positions = self._calculate_watermark_positions(rect, position, repeat_watermark, font_size, text)
        
        for x, y in positions:
            try:
                # Create watermark with opacity simulation (PyMuPDF doesn't support text opacity directly)
                if opacity < 1.0:
                    # For semi-transparent text, we'll use a lighter color
                    rgb_color = self._hex_to_rgb(color)
                    # Blend with white background to simulate opacity
                    adjusted_color = tuple(min(1.0, c + (1.0 - c) * (1.0 - opacity)) for c in rgb_color)
                else:
                    adjusted_color = self._hex_to_rgb(color)
                
                # Insert text with proper font handling
                if font_family == 'noto-sans-kannada':
                    # Try to use system Kannada fonts
                    for kannada_font in ['Noto Sans Kannada', 'Tunga', 'Kedage', 'Sampige']:
                        try:
                            page.insert_text(
                                (x, y),
                                text,
                                fontname=kannada_font,
                                fontsize=font_size,
                                color=adjusted_color,
                                rotate=rotation
                            )
                            break
                        except:
                            continue
                    else:
                        # Fallback to default font if no Kannada font works
                        page.insert_text(
                            (x, y),
                            text,
                            fontsize=font_size,
                            color=adjusted_color,
                            rotate=rotation
                        )
                else:
                    # Standard fonts
                    page.insert_text(
                        (x, y),
                        text,
                        fontname=font_family,
                        fontsize=font_size,
                        color=adjusted_color,
                        rotate=rotation
                    )
                    
            except Exception as e:
                print(f"Warning: Could not add watermark at position ({x}, {y}): {e}")
                # Try with default settings as fallback
                try:
                    page.insert_text(
                        (x, y),
                        text,
                        fontsize=font_size,
                        color=self._hex_to_rgb(color),
                        rotate=rotation
                    )
                except:
                    pass  # Skip this position if it fails completely

    def _is_kannada_text(self, text):
        """Check if text contains Kannada characters"""
        import re
        # Kannada Unicode range: U+0C80–U+0CFF
        kannada_pattern = re.compile(r'[\u0C80-\u0CFF]')
        return bool(kannada_pattern.search(text))

    def _calculate_watermark_positions(self, rect, position, repeat_watermark, font_size, text):
        """Calculate watermark positions based on options"""
        positions = []
        
        if repeat_watermark:
            # Create a grid of watermarks across the page
            spacing_x = font_size * len(text) * 0.6  # Approximate text width
            spacing_y = font_size * 1.5  # Line spacing
            
            for x in range(int(spacing_x/2), int(rect.width), int(spacing_x)):
                for y in range(int(spacing_y), int(rect.height), int(spacing_y)):
                    positions.append((x, y))
        else:
            # Single watermark at specified position
            if position == 'center':
                x, y = rect.width / 2, rect.height / 2
            elif position == 'top-left':
                x, y = 50, rect.height - 50
            elif position == 'top-center':
                x, y = rect.width / 2, rect.height - 50
            elif position == 'top-right':
                x, y = rect.width - 50, rect.height - 50
            elif position == 'middle-left':
                x, y = 50, rect.height / 2
            elif position == 'middle-right':
                x, y = rect.width - 50, rect.height / 2
            elif position == 'bottom-left':
                x, y = 50, 50
            elif position == 'bottom-center':
                x, y = rect.width / 2, 50
            elif position == 'bottom-right':
                x, y = rect.width - 50, 50
            else:
                x, y = rect.width / 2, rect.height / 2
            
            positions.append((x, y))
        
        return positions

    def _add_image_watermark(self, page, options):
        """Add image watermark to page with enhanced features"""
        if 'image_path' not in options or not os.path.exists(options['image_path']):
            return
        
        rect = page.rect
        position = options.get('position', 'center')
        image_scale = float(options.get('image_scale', 20)) / 100.0  # Convert percentage to decimal
        rotation = float(options.get('rotation', 0))
        repeat_watermark = options.get('repeat_watermark', False)
        
        # Calculate image size based on scale
        base_size = min(rect.width, rect.height) * image_scale
        
        if repeat_watermark:
            # Create a grid of image watermarks
            spacing = base_size * 2
            positions = []
            for x in range(int(spacing/2), int(rect.width), int(spacing)):
                for y in range(int(spacing/2), int(rect.height), int(spacing)):
                    positions.append((x - base_size/2, y - base_size/2))
        else:
            # Single image watermark
            if position == 'center':
                x = rect.width / 2 - base_size / 2
                y = rect.height / 2 - base_size / 2
            elif position == 'top-left':
                x, y = 50, rect.height - 50 - base_size
            elif position == 'top-center':
                x = rect.width / 2 - base_size / 2
                y = rect.height - 50 - base_size
            elif position == 'top-right':
                x = rect.width - 50 - base_size
                y = rect.height - 50 - base_size
            elif position == 'middle-left':
                x = 50
                y = rect.height / 2 - base_size / 2
            elif position == 'middle-right':
                x = rect.width - 50 - base_size
                y = rect.height / 2 - base_size / 2
            elif position == 'bottom-left':
                x, y = 50, 50
            elif position == 'bottom-center':
                x = rect.width / 2 - base_size / 2
                y = 50
            elif position == 'bottom-right':
                x = rect.width - 50 - base_size
                y = 50
            else:
                x = rect.width / 2 - base_size / 2
                y = rect.height / 2 - base_size / 2
            
            positions = [(x, y)]
        
        # Insert images at calculated positions
        for x, y in positions:
            try:
                image_rect = fitz.Rect(x, y, x + base_size, y + base_size)
                
                # Note: PyMuPDF has limited rotation support for images
                # Rotation would need to be applied during image processing
                page.insert_image(image_rect, filename=options['image_path'])
                
            except Exception as e:
                print(f"Warning: Could not add image watermark at position ({x}, {y}): {e}")

    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))

    def protect_pdf(self, file_path, session_id, protection_options):
        """Protect PDF with password and permissions using PyPDF2 for better compatibility"""
        try:
            # Validate protection options
            password = protection_options.get('protection_password', '')
            if len(password) < 6:
                raise Exception('ಪಾಸ್‌ವರ್ಡ್ ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳು ಇರಬೇಕು')
            
            confirm_password = protection_options.get('confirm_password', '')
            if password != confirm_password:
                raise Exception('ಪಾಸ್‌ವರ್ಡ್‌ಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ')
            
            output_filename = f"{session_id}_protected.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            # Try PyPDF2 method first (more reliable for password protection)
            try:
                from PyPDF2 import PdfReader, PdfWriter
                
                # Read the source PDF
                reader = PdfReader(file_path)
                writer = PdfWriter()
                
                # Copy all pages
                for page in reader.pages:
                    writer.add_page(page)
                
                # Set password protection
                user_password = password
                owner_password = password
                
                # Apply encryption with password
                writer.encrypt(
                    user_password=user_password,
                    owner_password=owner_password,
                    use_128bit=True
                )
                
                # Save the protected PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                print(f"PyPDF2 method successful: {output_path}")
                
            except Exception as pypdf2_error:
                print(f"PyPDF2 method failed: {pypdf2_error}")
                
                # Fallback to PyMuPDF with minimal encryption
                doc = fitz.open(file_path)
                
                # Use only basic password protection without complex permissions
                doc.save(
                    output_path,
                    encryption=1,  # Use basic RC4 encryption for compatibility
                    owner_pw=password,
                    user_pw=password
                    # No permissions parameter to avoid corruption
                )
                doc.close()
                print(f"PyMuPDF fallback method used: {output_path}")
            
            # Verify the output file was created properly
            if not os.path.exists(output_path):
                raise Exception('ಔಟ್‌ಪುಟ್ ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ')
            
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise Exception('ಖಾಲಿ ಫೈಲ್ ರಚಿಸಲಾಗಿದೆ')
            
            print(f"Protected PDF created successfully: {file_size} bytes")
            
            return {
                'success': True,
                'output_path': output_path,
                'filename': output_filename,
                'message': f'PDF ಯಶಸ್ವಿಯಾಗಿ ರಕ್ಷಿಸಲಾಗಿದೆ - ಪಾಸ್‌ವರ್ಡ್ ಅಗತ್ಯ'
            }
            
        except Exception as e:
            print(f"Protection error: {str(e)}")
            return {'success': False, 'error': f'PDF ರಕ್ಷಣೆ ವಿಫಲ: {str(e)}'}
