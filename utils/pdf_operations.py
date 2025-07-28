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
import io

class PDFOperations:
    def __init__(self):
        self.config = config.Config()
    
    def merge_pdfs(self, file_paths, session_id):
        """Merge multiple PDF files - FIXED VERSION"""
        try:
            print(f"=== MERGE PDF DEBUG ===")
            print(f"Session ID: {session_id}")
            print(f"File paths: {file_paths}")
            print(f"Number of files: {len(file_paths)}")
        
        # Validate input
            if not file_paths or len(file_paths) < 2:
                raise Exception("ವಿಲೀನಕ್ಕೆ ಕನಿಷ್ಠ 2 PDF ಫೈಲ್‌ಗಳು ಅಗತ್ಯ")
        
        # Check if all files exist and are valid PDFs
            valid_files = []
            for i, file_path in enumerate(file_paths):
                print(f"Checking file {i+1}: {file_path}")
            
                if not os.path.exists(file_path):
                    print(f"File does not exist: {file_path}")
                    continue
                
                if os.path.getsize(file_path) == 0:
                    print(f"File is empty: {file_path}")
                    continue
            
            # Test if file is a valid PDF
                try:
                    test_reader = PdfReader(file_path)
                    if len(test_reader.pages) == 0:
                        print(f"PDF has no pages: {file_path}")
                        continue
                    print(f"Valid PDF with {len(test_reader.pages)} pages: {file_path}")
                    valid_files.append(file_path)
                except Exception as pdf_error:
                    print(f"Invalid PDF file {file_path}: {pdf_error}")
                    continue
        
            if len(valid_files) < 2:
                raise Exception(f"ವಿಲೀನಕ್ಕೆ ಕನಿಷ್ಠ 2 ಸರಿಯಾದ PDF ಫೈಲ್‌ಗಳು ಅಗತ್ಯ. ಸಿಕ್ಕಿದ್ದು: {len(valid_files)}")
        
            print(f"Valid files for merging: {len(valid_files)}")
        
        # Create PDF writer
            writer = PdfWriter()
            total_pages_added = 0
        
        # Process each valid PDF file
            for file_path in valid_files:
                try:
                    print(f"Processing file: {os.path.basename(file_path)}")
                    reader = PdfReader(file_path)
                    pages_in_file = len(reader.pages)
                    print(f"Pages in file: {pages_in_file}")
                
                # Add all pages from this PDF
                    for page_num, page in enumerate(reader.pages):
                        try:
                            writer.add_page(page)
                            total_pages_added += 1
                            print(f"Added page {page_num + 1} from {os.path.basename(file_path)}")
                        except Exception as page_error:
                            print(f"Error adding page {page_num + 1}: {page_error}")
                            continue
                        
                except Exception as file_error:
                    print(f"Error processing file {file_path}: {file_error}")
                    continue
        
            if total_pages_added == 0:
                raise Exception("ಯಾವುದೇ ಪುಟಗಳನ್ನು ವಿಲೀನ ಮಾಡಲಾಗಿಲ್ಲ")
        
            print(f"Total pages added to merged PDF: {total_pages_added}")
        
        # Create output path
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_merged.pdf")
            print(f"Output path: {output_path}")
        
        # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write the merged PDF
            try:
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                print(f"Merged PDF written successfully")
            except Exception as write_error:
                print(f"Error writing merged PDF: {write_error}")
                raise Exception(f"ವಿಲೀನ PDF ಬರೆಯುವಲ್ಲಿ ದೋಷ: {str(write_error)}")
        
        # Verify the output file
            if not os.path.exists(output_path):
                raise Exception("ವಿಲೀನ PDF ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ")
        
            output_size = os.path.getsize(output_path)
            if output_size == 0:
                raise Exception("ಖಾಲಿ ವಿಲೀನ PDF ರಚಿಸಲಾಗಿದೆ")
        
            print(f"Merged PDF size: {output_size} bytes")
        
        # Final validation - try to read the merged PDF
            try:
                validation_reader = PdfReader(output_path)
                merged_pages = len(validation_reader.pages)
                print(f"Validation: Merged PDF has {merged_pages} pages")
            
                if merged_pages == 0:
                    raise Exception("ವಿಲೀನ PDF ಯಲ್ಲಿ ಯಾವುದೇ ಪುಟಗಳಿಲ್ಲ")
                
            except Exception as validation_error:
                print(f"Validation error: {validation_error}")
                raise Exception(f"ವಿಲೀನ PDF ದೋಷಪೂರ್ಣ: {str(validation_error)}")
        
            print(f"=== MERGE SUCCESSFUL ===")
            print(f"Files merged: {len(valid_files)}")
            print(f"Total pages: {merged_pages}")
            print(f"Output file: {output_path}")
            print(f"=== END DEBUG ===")
        
            return output_path
        
        except Exception as e:
            print(f"Merge error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"PDF ವಿಲೀನ ವಿಫಲ: {str(e)}")
    
    def split_pdf(self, file_path, session_id, pages=""):
        """Split PDF based on user specification - CORRECTED VERSION"""
        try:
            print(f"=== SPLIT PDF DEBUG ===")
            print(f"File path: {file_path}")
            print(f"Session ID: {session_id}")
            print(f"Pages parameter: '{pages}'")

            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            print(f"Total pages in PDF: {total_pages}")
    
        # Handle edge case: single page PDF
            if total_pages == 1:
                raise Exception("ಒಂದೇ ಪುಟದ PDF ಅನ್ನು ವಿಭಜಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ")

            output_dir = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_split")
            os.makedirs(output_dir, exist_ok=True)
            print(f"Output directory: {output_dir}")

        # Parse the pages specification
            split_info = self._parse_split_specification(pages, total_pages)
            print(f"Split info: {split_info}")
        
            created_files = []

        # Create PDFs based on split type
            if split_info['type'] == 'single_split':
                # Split into two parts at specified point
                split_point = split_info['split_point']
            
            # First PDF: pages 1 to split_point
                print(f"Creating first PDF: pages 1 to {split_point}")
                writer1 = PdfWriter()
                for i in range(split_point):
                    writer1.add_page(reader.pages[i])
                    print(f"Added page {i+1} to first PDF")
        
                output_path1 = os.path.join(output_dir, f"part_1_pages_1_to_{split_point}.pdf")
                with open(output_path1, 'wb') as output_file:
                    writer1.write(output_file)
                created_files.append(output_path1)
                print(f"Created first part: {output_path1}")
            
            # Second PDF: pages split_point+1 to end
                print(f"Creating second PDF: pages {split_point+1} to {total_pages}")
                writer2 = PdfWriter()
                for i in range(split_point, total_pages):
                    writer2.add_page(reader.pages[i])
                    print(f"Added page {i+1} to second PDF")
        
                output_path2 = os.path.join(output_dir, f"part_2_pages_{split_point+1}_to_{total_pages}.pdf")
                with open(output_path2, 'wb') as output_file:
                    writer2.write(output_file)
                created_files.append(output_path2)
                print(f"Created second part: {output_path2}")
            
            elif split_info['type'] == 'extract_pages':
            # Extract specific pages
                pages_to_extract = split_info['pages']
                print(f"Extracting pages: {pages_to_extract}")
            
                writer = PdfWriter()
                for page_num in pages_to_extract:
                    if 1 <= page_num <= total_pages:
                        writer.add_page(reader.pages[page_num - 1])
                        print(f"Added page {page_num} to extracted PDF")
            
                page_range_str = f"{min(pages_to_extract)}_to_{max(pages_to_extract)}"
                if len(pages_to_extract) > 2:
                    page_range_str = f"selected_pages"
                
                output_path = os.path.join(output_dir, f"extracted_pages_{page_range_str}.pdf")
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                created_files.append(output_path)
                print(f"Created extracted pages: {output_path}")
            
            elif split_info['type'] == 'multiple_splits':
            # Split into multiple parts based on page ranges
                ranges = split_info['ranges']
                print(f"Creating multiple splits: {ranges}")
            
                for i, (start, end) in enumerate(ranges):
                    writer = PdfWriter()
                    for page_num in range(start, end + 1):
                        if 1 <= page_num <= total_pages:
                            writer.add_page(reader.pages[page_num - 1])
                            print(f"Added page {page_num} to part {i+1}")
                
                    output_path = os.path.join(output_dir, f"part_{i+1}_pages_{start}_to_{end}.pdf")
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    created_files.append(output_path)
                    print(f"Created part {i+1}: {output_path}")
        
        # Verify files were created and are valid
            for file_path in created_files:
                if not os.path.exists(file_path):
                    raise Exception(f"ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ: {os.path.basename(file_path)}")
                if os.path.getsize(file_path) == 0:
                    raise Exception(f"ಖಾಲಿ ಫೈಲ್ ರಚಿಸಲಾಗಿದೆ: {os.path.basename(file_path)}")
            
            # Test if PDF is readable
                try:
                    test_reader = PdfReader(file_path)
                    if len(test_reader.pages) == 0:
                        raise Exception(f"ಅಮಾನ್ಯ PDF ರಚಿಸಲಾಗಿದೆ: {os.path.basename(file_path)}")
                except Exception as e:
                    raise Exception(f"ದೋಷಪೂರ್ಣ PDF ರಚಿಸಲಾಗಿದೆ: {os.path.basename(file_path)} - {str(e)}")
        
            print(f"Total files created: {len(created_files)}")
            print(f"Created files: {created_files}")

        # Create ZIP of split files
            zip_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_split.zip")
            print(f"Creating ZIP at: {zip_path}")

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in created_files:
                    # Add file to zip with just the filename (not full path)
                    zipf.write(file_path, os.path.basename(file_path))
                    print(f"Added to ZIP: {os.path.basename(file_path)}")
        
        # Verify ZIP was created and has content
            if not os.path.exists(zip_path):
                raise Exception("ZIP ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ")
        
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zip_contents = zipf.namelist()
                print(f"ZIP contents: {zip_contents}")
                if not zip_contents:
                    raise Exception("ZIP ಫೈಲ್ ಖಾಲಿಯಾಗಿದೆ")
        
            print(f"ZIP created successfully. Size: {os.path.getsize(zip_path)} bytes")
            print(f"=== END DEBUG ===")
            return zip_path
        
        except Exception as e:
            print(f"Error in split_pdf: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"PDF ವಿಭಾಗ ವಿಫಲ: {str(e)}")

    def _parse_split_specification(self, pages, total_pages):
        """Parse the pages specification and determine split type - NEW METHOD"""
        try:
            if not pages or pages.strip() == "":
            # Default: split in middle
                split_point = max(1, total_pages // 2)
                return {
                'type': 'single_split',
                'split_point': split_point
                }
        
            pages_str = pages.strip()
            print(f"Parsing specification: '{pages_str}'")
        
        # Check if it's a simple number (split point)
            try:
                split_point = int(pages_str)
            # Validate split point
                if split_point < 1:
                    split_point = 1
                elif split_point >= total_pages:
                    split_point = total_pages - 1
            
                print(f"Simple split at page {split_point}")
                return {
                    'type': 'single_split',
                    'split_point': split_point
                }
            except ValueError:
                pass
        
        # Check for range notation like "1-5" or "3-8"
            if '-' in pages_str and ',' not in pages_str:
                parts = pages_str.split('-')
                if len(parts) == 2:
                    try:
                        start = int(parts[0].strip())
                        end = int(parts[1].strip())
                    
                    # Validate range
                        start = max(1, min(start, total_pages))
                        end = max(start, min(end, total_pages))
                    
                        print(f"Extract pages range: {start} to {end}")
                        return {
                        'type': 'extract_pages',
                        'pages': list(range(start, end + 1))
                        }
                    except ValueError:
                        pass
        
        # Check for comma-separated pages/ranges like "1,3,5-7,10"
            if ',' in pages_str:
                try:
                    page_numbers = self._parse_page_ranges(pages_str, total_pages)
                    if page_numbers:
                        print(f"Extract specific pages: {page_numbers}")
                        return {
                        'type': 'extract_pages',
                        'pages': page_numbers
                        }
                except:
                    pass
        
        # If all parsing fails, default to middle split
            split_point = max(1, total_pages // 2)
            print(f"Parsing failed, defaulting to middle split at page {split_point}")
            return {
                'type': 'single_split',
                'split_point': split_point
            }
        
        except Exception as e:
            print(f"Error in _parse_split_specification: {e}")
        # Default fallback
            return {
                'type': 'single_split',  
                'split_point': max(1, total_pages // 2)
            }

    def _parse_page_ranges(self, pages_str, total_pages):
        """Parse page ranges like '1,3,5-10' into list of page numbers - CORRECTED VERSION"""
        pages = []
    
        try:
            for part in pages_str.split(','):
                part = part.strip()
                if not part:
                    continue
                
                if '-' in part:
                # Handle range like "5-10"  
                    range_parts = part.split('-')
                    if len(range_parts) == 2:
                        start_str, end_str = range_parts
                        start = int(start_str.strip())
                        end = int(end_str.strip())
                
                    # Validate range
                        start = max(1, min(start, total_pages))
                        end = max(start, min(end, total_pages))
                
                        pages.extend(range(start, end + 1))
                else:
                # Handle single page
                    page_num = int(part)
                    if 1 <= page_num <= total_pages:
                        pages.append(page_num)

        # Remove duplicates and sort
            pages = sorted(list(set(pages)))
            print(f"Parsed page ranges: {pages}")
            return pages
        
        except Exception as e:
            print(f"Error in _parse_page_ranges: {e}")
            return []
    
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
    
        return sorted(list(set(pages)))  # This should be OUTSIDE the for loop
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
        """Generate thumbnail previews for PDF pages"""
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            session_preview_dir = os.path.join(preview_folder, session_id)
            os.makedirs(session_preview_dir, exist_ok=True)
        
        # Clean up existing previews
            for filename in os.listdir(session_preview_dir):
                if filename.startswith('page_') and filename.endswith('.png'):
                    try:
                        os.remove(os.path.join(session_preview_dir, filename))
                    except:
                        pass
        
            return self._generate_previews_pymupdf(pdf_path, session_id, session_preview_dir, max_pages)
            
        except Exception as e:
            print(f"Error generating PDF previews: {str(e)}")
            return None

    def _generate_previews_pymupdf(self, pdf_path, session_id, session_preview_dir, max_pages):
        """Generate previews using PyMuPDF"""
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        pages_to_process = min(total_pages, max_pages)
        previews = []
    
        for page_num in range(pages_to_process):
            try:
                page = doc[page_num]
                zoom = 1.2  # Reduced zoom for better performance
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
            
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
            
            # Resize to thumbnail
                thumbnail_size = (180, 240)  # Slightly smaller
                img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            
            # Create white background
                background = Image.new('RGB', thumbnail_size, 'white')
                x = (thumbnail_size[0] - img.width) // 2
                y = (thumbnail_size[1] - img.height) // 2
            
                if img.mode == 'RGBA':
                    background.paste(img, (x, y), img)
                else:
                    background.paste(img, (x, y))
            
                filename = f"page_{page_num + 1}.png"
                file_path = os.path.join(session_preview_dir, filename)
                background.save(file_path, "PNG", optimize=True)
            
            # Store relative path for URL generation
                previews.append({
                    'page_num': page_num + 1,
                'image_path': file_path,  # Keep full path for now
                'width': background.width,
                'height': background.height
                })
            
            except Exception as e:
                print(f"Error generating preview for page {page_num + 1}: {str(e)}")
                continue
    
        doc.close()
    
        return {
        'total_pages': total_pages,
        'previews': previews,
        'session_id': session_id
    }
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
    
    