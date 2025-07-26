import os
import zipfile
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import config
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document
import os
import platform
import subprocess
import shutil
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import os

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
        """Compress PDF file with debugging and error handling"""
        try:
            print(f"Compression requested: {compression_level}")  # Debug
            print(f"Input file: {file_path}")  # Debug
            print(f"Input file size: {os.path.getsize(file_path)} bytes")  # Debug
            
            # Check if input file exists and is readable
            if not os.path.exists(file_path):
                raise Exception("Input file does not exist")
            
            # Try to open with PyMuPDF first
            try:
                doc = fitz.open(file_path)
                print(f"PDF opened successfully, pages: {len(doc)}")  # Debug
            except Exception as e:
                raise Exception(f"Cannot open PDF with PyMuPDF: {str(e)}")
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_compressed.pdf")
            print(f"Output path: {output_path}")  # Debug
            
            # Enhanced compression settings
            if compression_level == 'high':
                print("Using HIGH compression settings")  # Debug
                # Most aggressive compression
                save_options = {
                    'garbage': 4,        # Remove all unused objects
                    'clean': True,       # Clean and optimize
                    'deflate': True,     # Compress streams
                    'deflate_images': True,  # Compress images
                    'deflate_fonts': True,   # Compress fonts
                    'linear': True,      # Optimize for web
                    'ascii': False,      # Don't force ASCII
                    'expand': 0,         # Don't expand
                    'pretty': False      # Don't pretty print
                }
                
            elif compression_level == 'medium':
                print("Using MEDIUM compression settings")  # Debug
                save_options = {
                    'garbage': 3,
                    'clean': True,
                    'deflate': True,
                    'deflate_images': True,
                    'deflate_fonts': False,
                    'linear': True,
                    'pretty': False
                }
                
            else:  # low
                print("Using LOW compression settings")  # Debug
                save_options = {
                    'garbage': 1,
                    'clean': True,
                    'deflate': True,
                    'deflate_images': False,
                    'deflate_fonts': False,
                    'linear': False,
                    'pretty': False
                }
            
            print(f"Save options: {save_options}")  # Debug
            
            # Try to save with compression
            try:
                doc.save(output_path, **save_options)
                print("PDF saved successfully")  # Debug
            except Exception as save_error:
                print(f"Save error: {save_error}")  # Debug
                # Try with minimal options for high compression
                if compression_level == 'high':
                    print("Trying fallback high compression...")  # Debug
                    doc.save(output_path, garbage=4, clean=True, deflate=True)
                else:
                    raise save_error
            
            doc.close()
            
            # Verify output file
            if not os.path.exists(output_path):
                raise Exception("Output file was not created")
            
            output_size = os.path.getsize(output_path)
            original_size = os.path.getsize(file_path)
            
            print(f"Original size: {original_size} bytes")  # Debug
            print(f"Compressed size: {output_size} bytes")  # Debug
            print(f"Compression ratio: {(1 - output_size/original_size)*100:.1f}%")  # Debug
            
            # If high compression didn't reduce size much, try image optimization
            if compression_level == 'high' and output_size > original_size * 0.8:
                print("Trying advanced image compression...")  # Debug
                try:
                    advanced_path = self._compress_with_image_optimization(file_path, session_id)
                    if os.path.exists(advanced_path):
                        advanced_size = os.path.getsize(advanced_path)
                        if advanced_size < output_size:
                            print(f"Advanced compression better: {advanced_size} bytes")  # Debug
                            os.remove(output_path)  # Remove the less compressed version
                            return advanced_path
                except Exception as adv_error:
                    print(f"Advanced compression failed: {adv_error}")  # Debug
            
            return output_path
            
        except Exception as e:
            print(f"Compression error: {str(e)}")  # Debug
            raise Exception(f"PDF ಸಂಕುಚನ ವಿಫಲ: {str(e)}")

    def _compress_with_image_optimization(self, file_path, session_id):
        """Advanced compression focusing on image optimization"""
        try:
            doc = fitz.open(file_path)
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_compressed_advanced.pdf")
            
            print(f"Starting advanced image compression...")  # Debug
            
            # Create a new document
            new_doc = fitz.open()
            
            for page_num in range(len(doc)):
                print(f"Processing page {page_num + 1}")  # Debug
                page = doc.load_page(page_num)
                
                # Get page as image and compress it
                mat = fitz.Matrix(1.0, 1.0)  # Keep original resolution
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to PIL Image for compression
                img_data = pix.tobytes("png")
                from PIL import Image
                import io
                
                pil_img = Image.open(io.BytesIO(img_data))
                
                # Compress image
                compressed_io = io.BytesIO()
                pil_img.save(compressed_io, format='JPEG', quality=60, optimize=True)
                compressed_io.seek(0)
                
                # Create new page with compressed image
                img_pdf = fitz.open("pdf", compressed_io.getvalue())
                new_doc.insert_pdf(img_pdf)
                img_pdf.close()
            
            doc.close()
            
            # Save the new compressed document
            new_doc.save(output_path, garbage=4, clean=True, deflate=True)
            new_doc.close()
            
            print(f"Advanced compression completed")  # Debug
            return output_path
            
        except Exception as e:
            print(f"Advanced compression error: {e}")  # Debug
            raise Exception(f"Advanced compression failed: {str(e)}")

    def _fallback_compression(self, file_path, session_id):
        """Fallback compression using PyPDF2"""
        try:
            print("Using PyPDF2 fallback compression...")  # Debug
            
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            # Process each page
            for page_num, page in enumerate(reader.pages):
                print(f"Compressing page {page_num + 1}")  # Debug
                
                # Compress the page
                page.compress_content_streams()
                writer.add_page(page)
            
            # Remove duplicate objects
            writer.remove_duplication()
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_compressed_fallback.pdf")
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print("PyPDF2 compression completed")  # Debug
            return output_path
            
        except Exception as e:
            print(f"Fallback compression error: {e}")  # Debug
            raise Exception(f"Fallback compression failed: {str(e)}")
    
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
        """Convert PDF to Word document - FIXED VERSION"""
        try:
            doc = fitz.open(file_path)
            
            # Create Word document
            word_doc = Document()
            
            # Add title
            title = word_doc.add_heading('PDF ನಿಂದ ಪರಿವರ್ತಿತ ದಾಖಲೆ', 0)
            
            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text.strip():  # Only add non-empty pages
                    # Add page header
                    word_doc.add_heading(f'ಪುಟ {page_num + 1}', level=2)
                    
                    # Split text into paragraphs and add them
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            word_doc.add_paragraph(para.strip())
                    
                    # Add page break except for last page
                    if page_num < len(doc) - 1:
                        word_doc.add_page_break()
            
            doc.close()
            
            # Save as .docx file
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_converted.docx")
            word_doc.save(output_path)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"PDF Word ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")
    
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
        # Replace your existing word_to_pdf method with this complete version:
    def word_to_pdf(self, file_path, session_id):
        """
        Enhanced Word document to PDF conversion with Kannada font support
        Tries multiple methods in order of reliability for Kannada text
        """
        try:
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_from_word.pdf")
        
        # Ensure input file exists
            if not os.path.exists(file_path):
                raise Exception(f"Input file not found: {file_path}")
        
        # Method 1: LibreOffice (Best for Kannada support)
            if self._convert_with_libreoffice(file_path, output_path):
                return output_path
        
        # Method 2: Windows COM (if on Windows and Word is available)
            if platform.system() == "Windows":
                try:
                    return self._word_to_pdf_windows_com(file_path, session_id)
                except Exception as e:
                    print(f"Windows COM method failed: {e}")
        
        # Method 3: docx2pdf (Simple but may have font issues)
            if self._convert_with_docx2pdf(file_path, output_path):
                return output_path
        
        # Method 4: Advanced python-docx + ReportLab with Kannada font support
            return self._word_to_pdf_advanced_kannada(file_path, session_id)
        
        except Exception as e:
            raise Exception(f"Word to PDF conversion failed: {str(e)}")

    def _convert_with_libreoffice(self, input_path, output_path):
        """
        LibreOffice conversion - Best method for Kannada documents
        Preserves fonts and formatting accurately
        """
        try:
            # Find LibreOffice installation
            libreoffice_cmd = self._find_libreoffice()
            if not libreoffice_cmd:
                return False
        
        # Prepare conversion command
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)
        
        # Convert using LibreOffice
            cmd = [
                libreoffice_cmd,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                input_path
            ]
        
        # Run conversion with proper encoding
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60,
                encoding='utf-8'
            )
        
        # LibreOffice creates PDF with same base name
            input_name = Path(input_path).stem
            generated_pdf = os.path.join(output_dir, f"{input_name}.pdf")
        
        # Move to expected output path if different
            if os.path.exists(generated_pdf):
                if generated_pdf != output_path:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    os.rename(generated_pdf, output_path)
                return True
        
            return False
        
        except Exception as e:
            print(f"LibreOffice conversion failed: {e}")
            return False

    def _find_libreoffice(self):
        """Find LibreOffice installation across different platforms"""
        # Try common command names first
        for cmd in ['soffice', 'libreoffice']:
            if shutil.which(cmd):
                return cmd
    
    # Platform-specific paths
        if platform.system() == "Windows":
            paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
                r"C:\Program Files\LibreOffice\program\soffice.com",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.com"
            ]
        elif platform.system() == "Darwin":  # macOS
            paths = [
                "/Applications/LibreOffice.app/Contents/MacOS/soffice",
                "/usr/local/bin/soffice"
            ]
        else:  # Linux
            paths = [
            "/usr/bin/soffice",
            "/usr/bin/libreoffice",
            "/snap/bin/libreoffice",
            "/usr/local/bin/soffice"
            ]
    
        for path in paths:
            if os.path.exists(path):
                return path
    
        return None

    def _convert_with_docx2pdf(self, input_path, output_path):
        """Simple docx2pdf conversion - fallback method"""
        try:
            from docx2pdf import convert
            convert(input_path, output_path)
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
        except ImportError:
            print("docx2pdf not installed. Install with: pip install docx2pdf")
            return False
        except Exception as e:
            print(f"docx2pdf conversion failed: {e}")
            return False

    def _word_to_pdf_windows_com(self, file_path, session_id):
        """Windows COM method with enhanced error handling"""
        try:
            import pythoncom
            import win32com.client
        
            pythoncom.CoInitialize()
        
            try:
            # Create Word application
                word = win32com.client.Dispatch("Word.Application")
                word.Visible = False
                word.DisplayAlerts = 0  # Disable alerts
            
            # Open document
                doc = word.Documents.Open(os.path.abspath(file_path))
            
            # Export as PDF with high quality settings
                output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_from_word.pdf")
                doc.ExportAsFixedFormat(
                    OutputFileName=os.path.abspath(output_path),
                    ExportFormat=17,  # PDF format
                    OpenAfterExport=False,
                    OptimizeFor=0,  # Print optimization
                    Range=0,  # Export entire document
                    Item=7,  # Export document contents
                    IncludeDocProps=True,
                    KeepIRM=True,
                    CreateBookmarks=0,
                    DocStructureTags=True,
                    BitmapMissingFonts=True,
                    UseDocumentImageQuality=False
                )
            
            # Close document and Word
                doc.Close()
                word.Quit()
            
                return output_path
            
            finally:
                try:
                    pythoncom.CoUninitialize()
                except:
                    pass
                
        except ImportError:
            raise Exception("pywin32 not installed. Install with: pip install pywin32")
        except Exception as e:
            raise Exception(f"Microsoft Word COM failed: {str(e)}")

    def _word_to_pdf_advanced_kannada(self, file_path, session_id):
        """
    Advanced conversion using python-docx + ReportLab with Kannada font support
     """
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.lib.pagesizes import letter, A4
            from docx import Document
            import html
        
        # Register Kannada fonts if available
            self._register_kannada_fonts()
        
        # Read Word document
            doc = Document(file_path)
        
        # Create PDF with proper page size
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_from_word.pdf")
            pdf_doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
            )
        
            story = []
            styles = getSampleStyleSheet()
        
        # Create custom styles with Kannada font support
            kannada_font = self._get_kannada_font_name()
        
        # Enhanced paragraph styles
            custom_styles = {
                'KannadaTitle': ParagraphStyle(
                'KannadaTitle',
                parent=styles['Title'],
                fontName=kannada_font,
                fontSize=18,
                spaceAfter=20,
                alignment=TA_CENTER
                ),
                'KannadaHeading1': ParagraphStyle(
                'KannadaHeading1',
                parent=styles['Heading1'],
                fontName=kannada_font,
                fontSize=16,
                spaceAfter=12,
                spaceBefore=12
                ),
                'KannadaHeading2': ParagraphStyle(
                'KannadaHeading2',
                parent=styles['Heading2'],
                fontName=kannada_font,
                fontSize=14,
                spaceAfter=10,
                spaceBefore=10
                ),
                'KannadaNormal': ParagraphStyle(
                'KannadaNormal',
                parent=styles['Normal'],
                fontName=kannada_font,
                fontSize=12,
                spaceAfter=6,
                alignment=TA_JUSTIFY
                )
            }
        
        # Process paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    # Clean and escape text
                    text = html.escape(para.text.strip())
                
                # Determine style based on Word style
                    if 'Title' in para.style.name:
                        style = custom_styles['KannadaTitle']
                    elif 'Heading 1' in para.style.name:
                        style = custom_styles['KannadaHeading1']
                    elif 'Heading 2' in para.style.name:
                        style = custom_styles['KannadaHeading2']
                    elif 'Heading' in para.style.name:
                        style = custom_styles['KannadaHeading2']
                    else:
                        style = custom_styles['KannadaNormal']
                
                # Create paragraph with proper encoding
                    try:
                        pdf_para = Paragraph(text, style)
                        story.append(pdf_para)
                        story.append(Spacer(1, 6))
                    except Exception as e:
                    # Fallback for problematic text
                        fallback_text = text.encode('ascii', 'ignore').decode('ascii')
                        if fallback_text.strip():
                            pdf_para = Paragraph(fallback_text, styles['Normal'])
                            story.append(pdf_para)
                            story.append(Spacer(1, 6))
        
        # Process tables
            for table in doc.tables:
                table_data = []
                for row in table.rows:
                    row_data = []
                    for cell in row.cells:
                        cell_text = html.escape(cell.text.strip())
                        row_data.append(cell_text)
                    table_data.append(row_data)
            
                if table_data:
                    # Create PDF table
                    pdf_table = Table(table_data, hAlign='LEFT')
                    pdf_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), kannada_font),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                
                    story.append(Spacer(1, 12))
                    story.append(pdf_table)
                    story.append(Spacer(1, 12))
        
        # Add default content if document is empty
            if not story:
                story.append(Paragraph("ದಾಖಲೆಯಲ್ಲಿ ಯಾವುದೇ ವಿಷಯ ಕಂಡುಬಂದಿಲ್ಲ", custom_styles['KannadaNormal']))
        
        # Build PDF
            pdf_doc.build(story)
        
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_path
            else:
                raise Exception("PDF generation failed - output file is empty or not created")
        
        except Exception as e:
            raise Exception(f"Advanced ReportLab conversion failed: {str(e)}")

    def _register_kannada_fonts(self):
        """Register Kannada fonts for ReportLab"""
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        
        # Common Kannada font paths
            font_paths = []
        
            if platform.system() == "Windows":
                font_paths = [
                "C:/Windows/Fonts/Noto Sans Kannada Regular.ttf",
                "C:/Windows/Fonts/tunga.ttf",
                "C:/Windows/Fonts/Kalimati.ttf"
             ]
            elif platform.system() == "Darwin":  # macOS
                font_paths = [
                "/System/Library/Fonts/Noto Sans Kannada.ttc",
                "/Library/Fonts/Noto Sans Kannada Regular.ttf"
                ]
            else:  # Linux
                font_paths = [
                "/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
            ]
        
        # Try to register available fonts
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('KannadaFont', font_path))
                        return
                    except Exception as e:
                        continue
        
        # If no Kannada font found, use default
            print("No Kannada fonts found, using default font")
        
        except Exception as e:
            print(f"Font registration failed: {e}")

    def _get_kannada_font_name(self):
        """Get the best available font name for Kannada text"""
        try:
            # Check if our custom Kannada font is registered
            return 'KannadaFont'
        except:
            # Fall back to Helvetica which handles Unicode reasonably
            return 'Helvetica'

# Additional utility function for batch conversion
    def convert_multiple_word_files(self, file_paths, session_id_prefix="batch"):
        """
        Convert multiple Word files to PDF
    Returns list of successful conversions
    """
        successful_conversions = []
        failed_conversions = []
    
        for i, file_path in enumerate(file_paths):
            try:
                session_id = f"{session_id_prefix}_{i+1}"
                output_path = self.word_to_pdf(file_path, session_id)
                successful_conversions.append({
                'input': file_path,
                'output': output_path,
                'status': 'success'
                })
            except Exception as e:
                failed_conversions.append({
                    'input': file_path,
                    'error': str(e),
                    'status': 'failed'
                })
    
        return {
            'successful': successful_conversions,
            'failed': failed_conversions,
            'total_processed': len(file_paths),
            'success_count': len(successful_conversions),
            'failure_count': len(failed_conversions)
        }

    # Add this method to your existing PDFOperations class in utils/pdf_operations.py



    def generate_page_previews(self, pdf_path, session_id, preview_folder, max_pages=50):
        """
    Generate thumbnail previews for PDF pages
    
    Args:
        pdf_path (str): Path to the PDF file
        session_id (str): Session identifier for organizing previews
        preview_folder (str): Base folder for storing preview images
        max_pages (int): Maximum number of pages to generate previews for
    
    Returns:
        dict: Preview data with page information and image paths
        """
        try:
        # Create session-specific preview directory
            session_preview_dir = os.path.join(preview_folder, session_id)
            os.makedirs(session_preview_dir, exist_ok=True)
        
        # Open the PDF
            pdf_document = fitz.open(pdf_path)
            total_pages = len(pdf_document)
        
        # Limit the number of pages for performance
            pages_to_process = min(total_pages, max_pages)
        
            previews = []
        
            for page_num in range(pages_to_process):
                try:
                # Get the page
                    page = pdf_document[page_num]
                
                # Set zoom factor for good quality thumbnails
                    zoom = 1.5  # Increase for higher quality, decrease for smaller files
                    mat = fitz.Matrix(zoom, zoom)
                
                # Render page as image
                    pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                
                # Resize to thumbnail size (maintain aspect ratio)
                    thumbnail_size = (200, 280)  # Width, Height
                    img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                
                # Save thumbnail
                    filename = f"page_{page_num + 1}.png"
                    file_path = os.path.join(session_preview_dir, filename)
                    img.save(file_path, "PNG", optimize=True)
                
                # Add to previews list
                    previews.append({
                        'page_num': page_num + 1,
                        'image_path': file_path,
                        'width': img.width,
                        'height': img.height
                    })
                
                except Exception as e:
                    print(f"Error generating preview for page {page_num + 1}: {str(e)}")
                    continue
        
            pdf_document.close()
        
            return {
                'total_pages': total_pages,
                'previews': previews,
                'session_id': session_id
            }
        
        except Exception as e:
            print(f"Error generating PDF previews: {str(e)}")
            return None

# Alternative method using pdf2image if PyMuPDF is not available
    def generate_page_previews_pdf2image(self, pdf_path, session_id, preview_folder, max_pages=50):
        """
    Alternative method using pdf2image library
    Requires: pip install pdf2image
    Also requires poppler-utils (system dependency)
    """
        try:
            from pdf2image import convert_from_path
        
        # Create session-specific preview directory
            session_preview_dir = os.path.join(preview_folder, session_id)
            os.makedirs(session_preview_dir, exist_ok=True)
        
        # Convert PDF pages to images
        # Use first_page and last_page to limit conversion for performance
            images = convert_from_path(
                pdf_path,
            dpi=150,  # Lower DPI for thumbnails
            first_page=1,
            last_page=min(max_pages, self.get_pdf_page_count(pdf_path)),
            thread_count=2
        )
        
            previews = []
        
            for i, image in enumerate(images):
                try:
                    # Resize to thumbnail
                    thumbnail_size = (200, 280)
                    image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                
                # Save thumbnail
                    filename = f"page_{i + 1}.png"
                    file_path = os.path.join(session_preview_dir, filename)
                    image.save(file_path, "PNG", optimize=True)
                
                    previews.append({
                        'page_num': i + 1,
                        'image_path': file_path,
                        'width': image.width,
                        'height': image.height
                    })
                
                except Exception as e:
                    print(f"Error processing preview for page {i + 1}: {str(e)}")
                    continue
        
            total_pages = self.get_pdf_page_count(pdf_path)
        
            return {
                'total_pages': total_pages,
                'previews': previews,
                'session_id': session_id
            }
        
        except ImportError:
            print("pdf2image not installed. Please install: pip install pdf2image")
            return None
        except Exception as e:
            print(f"Error generating PDF previews with pdf2image: {str(e)}")
            return None

    def get_pdf_page_count(self, pdf_path):
        """Get the total number of pages in a PDF"""
        try:
            import fitz
            doc = fitz.open(pdf_path)
            count = len(doc)
            doc.close()
            return count
        except:
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(pdf_path)
                return len(reader.pages)
            except:
                return 0
    