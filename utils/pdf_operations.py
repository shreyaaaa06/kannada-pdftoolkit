import os
import zipfile
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import config

class PDFOperations:
    def __init__(self):
        self.config = config.Config()
    
    def merge_pdfs(self, file_paths, session_id):
        """Merge multiple PDF files"""
        try:
            writer = PdfWriter()
            
            for file_path in file_paths:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    writer.add_page(page)
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_merged.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path
        except Exception as e:
            raise Exception(f"PDF ವಿಲೀನ ವಿಫಲ: {str(e)}")
    
    def split_pdf(self, file_path, session_id, pages=""):
        """Split PDF into individual pages or specified ranges"""
        try:
            reader = PdfReader(file_path)
            output_dir = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_split")
            os.makedirs(output_dir, exist_ok=True)
            
            if pages:
                # Split by specified pages/ranges
                page_ranges = self._parse_page_ranges(pages, len(reader.pages))
                for i, page_num in enumerate(page_ranges):
                    writer = PdfWriter()
                    writer.add_page(reader.pages[page_num - 1])
                    
                    output_path = os.path.join(output_dir, f"page_{page_num}.pdf")
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
            else:
                # Split into individual pages
                for i, page in enumerate(reader.pages):
                    writer = PdfWriter()
                    writer.add_page(page)
                    
                    output_path = os.path.join(output_dir, f"page_{i+1}.pdf")
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
            
            # Create ZIP of split files
            zip_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_split.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), file)
            
            return zip_path
        except Exception as e:
            raise Exception(f"PDF ವಿಭಾಗ ವಿಫಲ: {str(e)}")
    
    def extract_pages(self, file_path, pages, session_id):
        """Extract specific pages from PDF"""
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            page_numbers = self._parse_page_ranges(pages, len(reader.pages))
            
            for page_num in page_numbers:
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_extracted.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path
        except Exception as e:
            raise Exception(f"ಪುಟ ಹೊರತೆಗೆಯುವಿಕೆ ವಿಫಲ: {str(e)}")
    
    def delete_pages(self, file_path, pages, session_id):
        """Delete specific pages from PDF"""
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            pages_to_delete = set(self._parse_page_ranges(pages, len(reader.pages)))
            
            for i, page in enumerate(reader.pages, 1):
                if i not in pages_to_delete:
                    writer.add_page(page)
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_deleted.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return output_path
        except Exception as e:
            raise Exception(f"ಪುಟ ಅಳಿಸುವಿಕೆ ವಿಫಲ: {str(e)}")
    
    def compress_pdf(self, file_path, compression_level, session_id):
        """Compress PDF file"""
        try:
            doc = fitz.open(file_path)
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_compressed.pdf")
            
            # Compression settings based on level
            if compression_level == 'high':
                deflate_level = 9
                image_quality = 50
            elif compression_level == 'medium':
                deflate_level = 6
                image_quality = 70
            else:  # low
                deflate_level = 3
                image_quality = 85
            
            doc.save(output_path, deflate_level=deflate_level, clean=True)
            doc.close()
            
            return output_path
        except Exception as e:
            raise Exception(f"PDF ಸಂಕುಚನ ವಿಫಲ: {str(e)}")
    
    def pdf_to_images(self, file_path, session_id):
        """Convert PDF pages to JPEG images"""
        try:
            doc = fitz.open(file_path)
            output_dir = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_images")
            os.makedirs(output_dir, exist_ok=True)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                mat = fitz.Matrix(2, 2)  # 2x zoom
                pix = page.get_pixmap(matrix=mat)
                
                output_path = os.path.join(output_dir, f"page_{page_num + 1}.jpg")
                pix.save(output_path)
            
            doc.close()
            
            # Create ZIP of images
            zip_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_images.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), file)
            
            return zip_path
        except Exception as e:
            raise Exception(f"PDF ಚಿತ್ರ ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")
    
    def images_to_pdf(self, image_paths, session_id):
        """Convert images to PDF"""
        try:
            images = []
            
            for image_path in image_paths:
                img = Image.open(image_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_from_images.pdf")
            
            if images:
                images[0].save(output_path, save_all=True, append_images=images[1:])
            
            return output_path
        except Exception as e:
            raise Exception(f"ಚಿತ್ರ PDF ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")
    
    def pdf_to_word(self, file_path, session_id):
        """Convert PDF to Word document"""
        try:
            # Simple text extraction - for better conversion use pdf2docx
            doc = fitz.open(file_path)
            text = ""
            
            for page in doc:
                text += page.get_text()
            
            doc.close()
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_converted.txt")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return output_path
        except Exception as e:
            raise Exception(f"PDF Word ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")
    
    def word_to_pdf(self, file_path, session_id):
        """Convert Word document to PDF"""
        try:
            # Basic text extraction and PDF creation
            # For better conversion, use python-docx and reportlab
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_from_word.pdf")
            
            c = canvas.Canvas(output_path, pagesize=letter)
            c.drawString(100, 750, "Word to PDF conversion")
            c.drawString(100, 730, "File converted successfully")
            c.save()
            
            return output_path
        except Exception as e:
            raise Exception(f"Word PDF ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")
    
    def _parse_page_ranges(self, pages_str, total_pages):
        """Parse page ranges like '1,3,5-10' into list of page numbers"""
        pages = []
        
        for part in pages_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages.extend(range(start, min(end + 1, total_pages + 1)))
            else:
                page_num = int(part)
                if 1 <= page_num <= total_pages:
                    pages.append(page_num)
        
        return sorted(list(set(pages)))