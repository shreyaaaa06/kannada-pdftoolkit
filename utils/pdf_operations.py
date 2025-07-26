import os
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance
import docx
from docx2pdf import convert as docx_to_pdf_convert
import fitz  # PyMuPDF for better PDF handling
import config

class PDFOperations:
    def __init__(self):
        self.config = config.Config()
        self.setup_fonts()
    
    def setup_fonts(self):
        """Setup Kannada fonts for PDF generation"""
        try:
            if os.path.exists(self.config.DEFAULT_FONT_PATH):
                pdfmetrics.registerFont(TTFont('Kannada', self.config.DEFAULT_FONT_PATH))
        except Exception as e:
            print(f"Font setup error: {e}")
    
    def merge_pdfs(self, files, session_id, **kwargs):
        """Merge multiple PDF files into one"""
        try:
            writer = PdfWriter()
            
            for file_path in files:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    writer.add_page(page)
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_merged.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path

        
        except Exception as e:
            raise Exception(f"PDF ನಿಂದ JPEG ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")
    
    def jpeg_to_pdf(self, files, session_id, **kwargs):
        """Convert JPEG images to PDF"""
        try:
            images = []
            for file_path in files:
                img = Image.open(file_path)
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                     f"{session_id}_images_to_pdf.pdf")
            
            # Save as PDF
            if images:
                images[0].save(output_path, save_all=True, append_images=images[1:])
            
            return output_path
        
        except Exception as e:
            raise Exception(f"JPEG ನಿಂದ PDF ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")
    
    def compress_pdf(self, files, session_id, quality='medium', **kwargs):
        """Compress PDF file to reduce size"""
        try:
            file_path = files[0]
            doc = fitz.open(file_path)
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                     f"{session_id}_compressed.pdf")
            
            # Compression settings
            compression_level = self.config.COMPRESSION_LEVELS.get(quality, 0.7)
            
            # Create new document with compression
            new_doc = fitz.open()
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get page as image and compress
                mat = fitz.Matrix(compression_level, compression_level)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("jpeg")
                
                # Create new page with compressed image
                img_rect = fitz.Rect(0, 0, pix.width / compression_level, 
                                   pix.height / compression_level)
                new_page = new_doc.new_page(width=img_rect.width, 
                                          height=img_rect.height)
                new_page.insert_image(img_rect, stream=img_data)
            
            new_doc.save(output_path, garbage=4, deflate=True)
            new_doc.close()
            doc.close()
            
            return output_path
        
        except Exception as e:
            raise Exception(f"PDF ಸಂಕುಚನ ವಿಫಲ: {str(e)}")
    
    def _parse_page_ranges(self, pages_str, total_pages):
        """Parse page range string like '1-3,5,7-9' into list of ranges"""
        ranges = []
        parts = pages_str.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                ranges.append(list(range(start-1, min(end, total_pages))))
            else:
                page_num = int(part) - 1
                if 0 <= page_num < total_pages:
                    ranges.append([page_num])
        
        return ranges
    
    def _parse_page_numbers(self, pages_str):
        """Parse page numbers string into list of integers"""
        pages = []
        parts = pages_str.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages.extend(range(start-1, end))
            else:
                pages.append(int(part) - 1)
        
        return sorted(set(pages))  # Remove duplicates and sort
    
    def get_pdf_info(self, file_path):
        """Get PDF information like page count, size, etc."""
        try:
            reader = PdfReader(file_path)
            info = {
                'pages': len(reader.pages),
                'title': reader.metadata.title if reader.metadata else 'Unknown',
                'author': reader.metadata.author if reader.metadata else 'Unknown',
                'size': os.path.getsize(file_path)
            }
            return info
        except Exception as e:
            return {'error': str(e)} 
        
        except Exception as e:
            raise Exception(f"PDF ವಿಲೀನ ವಿಫಲ: {str(e)}")
    
    def split_pdf(self, files, pages, session_id, **kwargs):
        """Split PDF into separate files based on page ranges"""
        try:
            file_path = files[0]  # Take first file for splitting
            reader = PdfReader(file_path)
            
            # Parse page ranges (e.g., "1-3,5,7-9")
            page_ranges = self._parse_page_ranges(pages, len(reader.pages))
            
            output_files = []
            for i, page_range in enumerate(page_ranges):
                writer = PdfWriter()
                
                for page_num in page_range:
                    if 0 <= page_num < len(reader.pages):
                        writer.add_page(reader.pages[page_num])
                
                output_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                         f"{session_id}_split_{i+1}.pdf")
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
            
            # If multiple files, create a zip
            if len(output_files) > 1:
                import zipfile
                zip_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_split_files.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file_path in output_files:
                        zipf.write(file_path, os.path.basename(file_path))
                        os.remove(file_path)  # Remove individual files
                return zip_path
            
            return output_files[0] if output_files else None
        
        except Exception as e:
            raise Exception(f"PDF ವಿಭಾಗ ವಿಫಲ: {str(e)}")
    
    def extract_pages(self, files, pages, session_id, **kwargs):
        """Extract specific pages from PDF"""
        try:
            file_path = files[0]
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            # Parse page numbers
            page_numbers = self._parse_page_numbers(pages)
            
            for page_num in page_numbers:
                if 0 <= page_num < len(reader.pages):
                    writer.add_page(reader.pages[page_num])
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                     f"{session_id}_extracted.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path
        
        except Exception as e:
            raise Exception(f"ಪುಟ ಹೊರತೆಗೆಯುವಿಕೆ ವಿಫಲ: {str(e)}")
    
    def delete_pages(self, files, pages, session_id, **kwargs):
        """Delete specific pages from PDF"""
        try:
            file_path = files[0]
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            # Parse page numbers to delete
            pages_to_delete = set(self._parse_page_numbers(pages))
            
            for i, page in enumerate(reader.pages):
                if i not in pages_to_delete:
                    writer.add_page(page)
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                     f"{session_id}_deleted_pages.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path
        
        except Exception as e:
            raise Exception(f"ಪುಟ ಅಳಿಸುವಿಕೆ ವಿಫಲ: {str(e)}")
    
    def crop_pages(self, files, session_id, left=0, top=0, right=0, bottom=0, **kwargs):
        """Crop pages with specified margins"""
        try:
            file_path = files[0]
            doc = fitz.open(file_path)
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                     f"{session_id}_cropped.pdf")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                rect = page.rect
                
                # Calculate new rectangle with margins
                new_rect = fitz.Rect(
                    rect.x0 + left,
                    rect.y0 + top,
                    rect.x1 - right,
                    rect.y1 - bottom
                )
                
                page.set_cropbox(new_rect)
            
            doc.save(output_path)
            doc.close()
            
            return output_path
        
        except Exception as e:
            raise Exception(f"ಪುಟ ಕತ್ತರಿಸುವಿಕೆ ವಿಫಲ: {str(e)}")
    
    def rotate_pages(self, files, session_id, angle=90, **kwargs):
        """Rotate all pages by specified angle"""
        try:
            file_path = files[0]
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                rotated_page = page.rotate(angle)
                writer.add_page(rotated_page)
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                     f"{session_id}_rotated.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path
        
        except Exception as e:
            raise Exception(f"ಪುಟ ತಿರುಗಿಸುವಿಕೆ ವಿಫಲ: {str(e)}")
    
    def pdf_to_word(self, files, session_id, **kwargs):
        """Convert PDF to Word document"""
        try:
            file_path = files[0]
            doc = fitz.open(file_path)
            
            # Create new Word document
            word_doc = docx.Document()
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Add page content to Word document
                if text.strip():
                    paragraph = word_doc.add_paragraph(text)
                    # Set font for Kannada support
                    for run in paragraph.runs:
                        run.font.name = 'Noto Sans Kannada'
                
                # Add page break except for last page
                if page_num < len(doc) - 1:
                    word_doc.add_page_break()
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                     f"{session_id}_converted.docx")
            word_doc.save(output_path)
            doc.close()
            
            return output_path
        
        except Exception as e:
            raise Exception(f"PDF ನಿಂದ Word ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")
    
    def word_to_pdf(self, files, session_id, **kwargs):
        """Convert Word document to PDF"""
        try:
            file_path = files[0]
            output_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                     f"{session_id}_converted.pdf")
            
            # Use docx2pdf for conversion
            docx_to_pdf_convert(file_path, output_path)
            
            return output_path
        
        except Exception as e:
            raise Exception(f"Word ನಿಂದ PDF ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")
    
    def pdf_to_jpeg(self, files, session_id, **kwargs):
        """Convert PDF pages to JPEG images"""
        try:
            file_path = files[0]
            
            # Convert PDF to images
            images = convert_from_path(file_path, 
                                     dpi=self.config.PDF_DPI,
                                     fmt='jpeg')
            
            output_files = []
            for i, image in enumerate(images):
                output_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                         f"{session_id}_page_{i+1}.jpg")
                image.save(output_path, 'JPEG', quality=self.config.PDF_QUALITY)
                output_files.append(output_path)
            
            # Create zip file if multiple images
            if len(output_files) > 1:
                import zipfile
                zip_path = os.path.join(self.config.OUTPUT_FOLDER, 
                                      f"{session_id}_images.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for file_path in output_files:
                        zipf.write(file_path, os.path.basename(file_path))
                        os.remove(file_path)
                return zip_path
            
            return output_files[0]  # return the single image path if only one
        except Exception as e:
            print(f"[ERROR] Failed to convert PDF to images: {str(e)}")
            return None 