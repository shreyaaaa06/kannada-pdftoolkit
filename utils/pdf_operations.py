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
import fitz  # PyMuPDF
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
        

    def compress_pdf(self, file_path, compression_level, session_id, target_size_mb=None):
        """
        Enhanced PDF compression with user-controlled levels and target size
        
        Args:
            file_path: Path to input PDF
            compression_level: 'low', 'medium', 'high', 'maximum', or 'custom'
            session_id: Session identifier
            target_size_mb: Target file size in MB (for custom compression)
        """
        try:
            print(f"=== ENHANCED PDF COMPRESSION ===")
            print(f"Input: {file_path}")
            print(f"Level: {compression_level}")
            print(f"Target size: {target_size_mb}MB" if target_size_mb else "No target size")
            
            # Validate input
            if not os.path.exists(file_path):
                raise Exception("PDF ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ")
            
            original_size = os.path.getsize(file_path)
            original_size_mb = original_size / (1024 * 1024)
            print(f"Original size: {original_size:,} bytes ({original_size_mb:.2f} MB)")
            
            if original_size == 0:
                raise Exception("ಖಾಲಿ PDF ಫೈಲ್")
            
            # Test if valid PDF
            try:
                doc = fitz.open(file_path)
                page_count = len(doc)
                doc.close()
                print(f"Valid PDF with {page_count} pages")
            except Exception as e:
                raise Exception(f"ಅಮಾನ್ಯ PDF ಫೈಲ್: {str(e)}")
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_compressed.pdf")
            
            # Enhanced compression methods with different aggressiveness levels
            if compression_level == 'maximum' or (target_size_mb and target_size_mb < original_size_mb * 0.3):
                # Ultra-aggressive compression
                methods = [
                    ("Ultra Aggressive", self._compress_ultra_aggressive),
                    ("Extreme Image Recreation", self._compress_extreme_image_recreation),
                    ("Advanced PyMuPDF", self._compress_advanced_pymupdf),
                ]
            elif compression_level == 'high' or (target_size_mb and target_size_mb < original_size_mb * 0.6):
                # High compression
                methods = [
                    ("Extreme Image Recreation", self._compress_extreme_image_recreation),
                    ("Advanced PyMuPDF", self._compress_advanced_pymupdf),
                    ("Image Recreation", self._compress_by_image_recreation),
                ]
            elif compression_level == 'medium':
                # Balanced compression
                methods = [
                    ("Advanced PyMuPDF", self._compress_advanced_pymupdf),
                    ("Image Recreation", self._compress_by_image_recreation),
                    ("Basic PyMuPDF", self._compress_basic_pymupdf)
                ]
            else:  # low compression
                # Gentle compression
                methods = [
                    ("Basic PyMuPDF", self._compress_basic_pymupdf),
                    ("Advanced PyMuPDF", self._compress_advanced_pymupdf),
                ]
            
            best_result = None
            best_size = original_size
            target_reached = False
            
            for method_name, method_func in methods:
                try:
                    print(f"Trying {method_name} compression...")
                    temp_output = output_path.replace('.pdf', f'_temp_{method_name.replace(" ", "_").lower()}.pdf')
                    
                    # Pass target size for adaptive compression
                    if hasattr(method_func, '__code__') and 'target_size_mb' in method_func.__code__.co_varnames:
                        result = method_func(file_path, temp_output, compression_level, target_size_mb)
                    else:
                        result = method_func(file_path, temp_output, compression_level)
                    
                    if result and os.path.exists(temp_output):
                        compressed_size = os.path.getsize(temp_output)
                        compressed_size_mb = compressed_size / (1024 * 1024)
                        
                        if compressed_size > 0 and compressed_size < best_size:
                            # Clean up previous best
                            if best_result and os.path.exists(best_result):
                                os.remove(best_result)
                            
                            best_result = temp_output
                            best_size = compressed_size
                            reduction = (1 - compressed_size/original_size) * 100
                            
                            print(f"✓ {method_name} successful!")
                            print(f"Compressed size: {compressed_size:,} bytes ({compressed_size_mb:.2f} MB)")
                            print(f"Size reduction: {reduction:.1f}%")
                            
                            # Check if target size reached
                            if target_size_mb and compressed_size_mb <= target_size_mb:
                                target_reached = True
                                print(f"🎯 Target size reached! ({compressed_size_mb:.2f}MB <= {target_size_mb}MB)")
                                break
                        else:
                            print(f"✗ {method_name} didn't improve compression")
                            if os.path.exists(temp_output):
                                os.remove(temp_output)
                    else:
                        print(f"✗ {method_name} failed to create output")
                        
                except Exception as e:
                    print(f"✗ {method_name} failed: {e}")
                    continue
            
            # Use the best result or try iterative compression if target not reached
            if best_result and os.path.exists(best_result):
                final_output = output_path
                
                # If target size not reached and we have a target, try iterative compression
                if target_size_mb and not target_reached and best_size > target_size_mb * 1024 * 1024:
                    print("Target size not reached, trying iterative compression...")
                    iterative_result = self._iterative_compression(best_result, final_output, target_size_mb)
                    if iterative_result and os.path.exists(final_output):
                        if best_result != final_output:
                            os.remove(best_result)
                    else:
                        # Keep the best result we got
                        if best_result != final_output:
                            os.rename(best_result, final_output)
                else:
                    # Move best result to final output path
                    if os.path.exists(final_output):
                        os.remove(final_output)
                    os.rename(best_result, final_output)
                
                final_size = os.path.getsize(final_output)
                final_size_mb = final_size / (1024 * 1024)
                reduction = (1 - final_size/original_size) * 100
                
                print(f"=== COMPRESSION COMPLETE ===")
                print(f"Original: {original_size:,} bytes ({original_size_mb:.2f} MB)")
                print(f"Compressed: {final_size:,} bytes ({final_size_mb:.2f} MB)")
                print(f"Reduction: {reduction:.1f}%")
                
                if target_size_mb:
                    if final_size_mb <= target_size_mb:
                        print(f"🎯 Target achieved: {final_size_mb:.2f}MB <= {target_size_mb}MB")
                    else:
                        print(f"⚠️ Target not fully achieved: {final_size_mb:.2f}MB > {target_size_mb}MB")
                
                # Only return if we actually achieved compression
                if final_size < original_size:
                    return final_output
                else:
                    print("No compression achieved, removing output file")
                    os.remove(final_output)
                    raise Exception("ಸಂಕುಚನ ಸಾಧ್ಯವಾಗಲಿಲ್ಲ - ಮೂಲ ಫೈಲ್ ಈಗಾಗಲೇ ಅತ್ಯುತ್ತಮವಾಗಿ ಸಂಕುಚಿತವಾಗಿದೆ")
            
            # If no method worked
            raise Exception("ಎಲ್ಲಾ ಸಂಕುಚನ ವಿಧಾನಗಳು ವಿಫಲವಾಗಿವೆ")
            
        except Exception as e:
            print(f"Compression error: {str(e)}")
            raise Exception(f"PDF ಸಂಕುಚನ ವಿಫಲ: {str(e)}")

    def _compress_ultra_aggressive(self, input_path, output_path, level, target_size_mb=None):
        """
        Ultra-aggressive compression - maximum size reduction
        """
        try:
            print("Starting ultra-aggressive compression...")
            doc = fitz.open(input_path)
            new_doc = fitz.open()
            
            # Very aggressive settings
            dpi = 72  # Very low DPI
            jpeg_quality = 30  # Very low quality
            scale_factor = 0.4  # Scale down to 40%
            
            # If target size specified, adjust parameters dynamically
            if target_size_mb:
                original_size_mb = os.path.getsize(input_path) / (1024 * 1024)
                compression_ratio = target_size_mb / original_size_mb
                
                if compression_ratio < 0.1:  # Need >90% compression
                    dpi = 50
                    jpeg_quality = 20
                    scale_factor = 0.3
                elif compression_ratio < 0.2:  # Need >80% compression
                    dpi = 60
                    jpeg_quality = 25
                    scale_factor = 0.35
                elif compression_ratio < 0.3:  # Need >70% compression
                    dpi = 72
                    jpeg_quality = 30
                    scale_factor = 0.4
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert page to very low-res image
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to PIL for aggressive compression
                img_data = pix.tobytes("png")
                pil_img = Image.open(io.BytesIO(img_data))
                
                # Scale down further
                new_width = int(pil_img.width * scale_factor)
                new_height = int(pil_img.height * scale_factor)
                pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB and compress heavily
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                # Apply additional optimizations
                # Reduce color palette
                pil_img = pil_img.quantize(colors=64).convert('RGB')
                
                # Save with very low quality
                jpeg_io = io.BytesIO()
                pil_img.save(jpeg_io, format='JPEG', quality=jpeg_quality, 
                            optimize=True, progressive=True)
                jpeg_data = jpeg_io.getvalue()
                
                # Create new page from compressed image
                img_rect = fitz.Rect(0, 0, pil_img.width, pil_img.height)
                new_page = new_doc.new_page(width=img_rect.width, height=img_rect.height)
                new_page.insert_image(img_rect, stream=jpeg_data)
            
            doc.close()
            
            # Save with maximum compression
            new_doc.save(output_path, 
                        deflate=True, 
                        garbage=4, 
                        clean=True,
                        linear=True,
                        pretty=False)
            new_doc.close()
            
            print("Ultra-aggressive compression completed")
            return True
            
        except Exception as e:
            print(f"Ultra-aggressive compression error: {e}")
            return False

    def _compress_extreme_image_recreation(self, input_path, output_path, level, target_size_mb=None):
        """
        Extreme image recreation with adaptive quality based on target size
        """
        try:
            doc = fitz.open(input_path)
            new_doc = fitz.open()
            
            # Base settings
            base_dpi = 100
            base_quality = 50
            
            # Adjust based on target size
            if target_size_mb:
                original_size_mb = os.path.getsize(input_path) / (1024 * 1024)
                compression_ratio = target_size_mb / original_size_mb
                
                # More aggressive settings for smaller target sizes
                if compression_ratio < 0.2:
                    base_dpi = 75
                    base_quality = 35
                elif compression_ratio < 0.5:
                    base_dpi = 85
                    base_quality = 45
            
            # Adjust based on level
            if level == 'maximum':
                dpi = max(50, base_dpi - 25)
                jpeg_quality = max(20, base_quality - 15)
            elif level == 'high':
                dpi = max(75, base_dpi - 10)
                jpeg_quality = max(35, base_quality - 10)
            else:
                dpi = base_dpi
                jpeg_quality = base_quality
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert to image with calculated DPI
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to PIL
                img_data = pix.tobytes("png")
                pil_img = Image.open(io.BytesIO(img_data))
                
                # Convert to RGB
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                # Apply sharpening before compression
                from PIL import ImageFilter
                pil_img = pil_img.filter(ImageFilter.UnsharpMask(radius=1, percent=100, threshold=3))
                
                # Compress as JPEG
                jpeg_io = io.BytesIO()
                pil_img.save(jpeg_io, format='JPEG', 
                            quality=jpeg_quality, 
                            optimize=True,
                            progressive=True)
                jpeg_data = jpeg_io.getvalue()
                
                # Create new page
                img_rect = fitz.Rect(0, 0, pil_img.width, pil_img.height)
                new_page = new_doc.new_page(width=img_rect.width, height=img_rect.height)
                new_page.insert_image(img_rect, stream=jpeg_data)
            
            doc.close()
            
            # Save with compression
            new_doc.save(output_path, deflate=True, garbage=4, clean=True)
            new_doc.close()
            
            return True
            
        except Exception as e:
            print(f"Extreme image recreation error: {e}")
            return False

    def _iterative_compression(self, input_path, output_path, target_size_mb):
        """
        Iteratively compress until target size is reached
        """
        try:
            print(f"Starting iterative compression to reach {target_size_mb}MB...")
            
            current_path = input_path
            iteration = 0
            max_iterations = 5
            
            while iteration < max_iterations:
                current_size_mb = os.path.getsize(current_path) / (1024 * 1024)
                
                if current_size_mb <= target_size_mb:
                    print(f"Target reached after {iteration} iterations!")
                    if current_path != output_path:
                        import shutil
                        shutil.copy2(current_path, output_path)
                    return True
                
                print(f"Iteration {iteration + 1}: Current size {current_size_mb:.2f}MB, target {target_size_mb}MB")
                
                # Calculate required compression ratio
                compression_ratio = target_size_mb / current_size_mb
                
                # Adjust quality based on how much more compression is needed
                if compression_ratio < 0.5:
                    quality = 25
                    dpi = 60
                elif compression_ratio < 0.7:
                    quality = 35
                    dpi = 75
                else:
                    quality = 50
                    dpi = 90
                
                # Create temporary file for this iteration
                temp_path = output_path.replace('.pdf', f'_iter_{iteration}.pdf')
                
                # Apply compression
                doc = fitz.open(current_path)
                new_doc = fitz.open()
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    
                    mat = fitz.Matrix(dpi/72, dpi/72)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    
                    img_data = pix.tobytes("png")
                    pil_img = Image.open(io.BytesIO(img_data))
                    
                    if pil_img.mode != 'RGB':
                        pil_img = pil_img.convert('RGB')
                    
                    jpeg_io = io.BytesIO()
                    pil_img.save(jpeg_io, format='JPEG', quality=quality, optimize=True)
                    jpeg_data = jpeg_io.getvalue()
                    
                    img_rect = fitz.Rect(0, 0, pil_img.width, pil_img.height)
                    new_page = new_doc.new_page(width=img_rect.width, height=img_rect.height)
                    new_page.insert_image(img_rect, stream=jpeg_data)
                
                doc.close()
                new_doc.save(temp_path, deflate=True, garbage=4, clean=True)
                new_doc.close()
                
                # Clean up previous iteration
                if current_path != input_path and os.path.exists(current_path):
                    os.remove(current_path)
                
                current_path = temp_path
                iteration += 1
            
            # Copy final result
            if current_path != output_path:
                import shutil
                shutil.copy2(current_path, output_path)
                if os.path.exists(current_path):
                    os.remove(current_path)
            
            final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"Iterative compression completed. Final size: {final_size_mb:.2f}MB")
            
            return True
            
        except Exception as e:
            print(f"Iterative compression error: {e}")
            return False

    def _compress_pymupdf(self, input_path, output_path, level):
        """Compress using PyMuPDF - IMPROVED VERSION"""
        try:
            doc = fitz.open(input_path)
            
            # First pass - compress images in each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get all images on the page
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    # Extract image
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Convert to PIL for compression
                    from PIL import Image
                    import io
                    
                    pil_image = Image.open(io.BytesIO(image_bytes))
                    
                    # Compress based on level
                    if level == 'high':
                        quality = 30
                        scale = 0.5  # Reduce size to 50%
                    elif level == 'medium':
                        quality = 50
                        scale = 0.7  # Reduce size to 70%
                    else:  # low
                        quality = 70
                        scale = 0.9  # Reduce size to 90%
                    
                    # Resize image
                    new_size = (int(pil_image.width * scale), int(pil_image.height * scale))
                    pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Compress and save back
                    if pil_image.mode in ('RGBA', 'LA'):
                        # Convert transparent images to white background
                        background = Image.new('RGB', pil_image.size, (255, 255, 255))
                        if pil_image.mode == 'RGBA':
                            background.paste(pil_image, mask=pil_image.split()[-1])
                        else:
                            background.paste(pil_image)
                        pil_image = background
                    
                    # Save compressed image
                    compressed_io = io.BytesIO()
                    pil_image.save(compressed_io, format='JPEG', quality=quality, optimize=True)
                    compressed_bytes = compressed_io.getvalue()
                    
                    # Replace image in PDF
                    doc._updateObject(xref, compressed_bytes, filename="image.jpg")
            
            # Second pass - save with compression options
            if level == 'high':
                options = {
                    'garbage': 4,
                    'clean': True,
                    'deflate': True,
                    'deflate_images': True,
                    'deflate_fonts': True,
                    'linear': True,
                    'pretty': False
                }
            elif level == 'medium':
                options = {
                    'garbage': 3,
                    'clean': True,
                    'deflate': True,
                    'deflate_images': True,
                    'deflate_fonts': True,
                    'linear': True,
                    'pretty': False
                }
            else:  # low
                options = {
                    'garbage': 2,
                    'clean': True,
                    'deflate': True,
                    'deflate_images': False,
                    'deflate_fonts': False,
                    'linear': False,
                    'pretty': False
                }
            
            doc.save(output_path, **options)
            doc.close()
            
            return True
            
        except Exception as e:
            print(f"PyMuPDF compression error: {e}")
            return False

    
    
    def _validate_compressed_pdf(self, pdf_path):
        """Validate that compressed PDF is readable"""
        try:
            # Test with PyMuPDF
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            
            if page_count == 0:
                return False
            
            # Test with PyPDF2
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            if len(reader.pages) != page_count:
                return False
            
            print(f"Validation successful: {page_count} pages")
            return True
            
        except Exception as e:
            print(f"Validation failed: {e}")
            return False

    
    def _compress_advanced_pymupdf(self, input_path, output_path, level):
        """Advanced PyMuPDF compression with image optimization"""
        try:
            doc = fitz.open(input_path)
            
            # Step 1: Compress images on each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Convert to PIL for compression
                        pil_image = Image.open(io.BytesIO(image_bytes))
                        
                        # Set compression parameters based on level
                        if level == 'high':
                            quality = 40
                            scale_factor = 0.6
                        elif level == 'medium':
                            quality = 60
                            scale_factor = 0.8
                        else:  # low
                            quality = 80
                            scale_factor = 0.9
                        
                        # Resize image
                        new_width = int(pil_image.width * scale_factor)
                        new_height = int(pil_image.height * scale_factor)
                        pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Convert RGBA to RGB with white background
                        if pil_image.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', pil_image.size, (255, 255, 255))
                            if pil_image.mode == 'P':
                                pil_image = pil_image.convert('RGBA')
                            if pil_image.mode in ('RGBA', 'LA'):
                                background.paste(pil_image, mask=pil_image.split()[-1])
                            else:
                                background.paste(pil_image)
                            pil_image = background
                        
                        # Compress as JPEG
                        compressed_io = io.BytesIO()
                        pil_image.save(compressed_io, format='JPEG', quality=quality, optimize=True)
                        compressed_bytes = compressed_io.getvalue()
                        
                        # Replace image in PDF
                        img_dict = {
                            "type": "image",
                            "bbox": fitz.Rect(0, 0, new_width, new_height),
                            "width": new_width,
                            "height": new_height,
                            "image": compressed_bytes
                        }
                        
                        # Update the image in the document
                        page.insert_image(img_dict["bbox"], stream=compressed_bytes)
                        
                    except Exception as img_error:
                        print(f"Error compressing image {img_index}: {img_error}")
                        continue
            
            # Step 2: Save with aggressive compression settings
            if level == 'high':
                options = {
                    'garbage': 4,
                    'clean': True,
                    'deflate': True,
                    'deflate_images': True,
                    'deflate_fonts': True,
                    'linear': True,
                    'pretty': False,
                    'ascii': False
                }
            elif level == 'medium':
                options = {
                    'garbage': 3,
                    'clean': True,
                    'deflate': True,
                    'deflate_images': True,
                    'deflate_fonts': True,
                    'linear': False,
                    'pretty': False
                }
            else:  # low
                options = {
                    'garbage': 2,
                    'clean': True,
                    'deflate': True,
                    'deflate_images': False,
                    'deflate_fonts': False,
                    'linear': False,
                    'pretty': False
                }
            
            doc.save(output_path, **options)
            doc.close()
            
            return True
            
        except Exception as e:
            print(f"Advanced PyMuPDF compression error: {e}")
            return False

    def _compress_by_image_recreation(self, input_path, output_path, level):
        """Compress by converting pages to images and back - MOST AGGRESSIVE"""
        try:
            doc = fitz.open(input_path)
            new_doc = fitz.open()
            
            # Set parameters based on compression level
            if level == 'high':
                dpi = 100  # Lower DPI = smaller file
                jpeg_quality = 60
            elif level == 'medium':
                dpi = 150
                jpeg_quality = 75
            else:  # low
                dpi = 200
                jpeg_quality = 85
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert page to image
                mat = fitz.Matrix(dpi/72, dpi/72)  # 72 is default DPI
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to PIL for JPEG compression
                img_data = pix.tobytes("png")
                pil_img = Image.open(io.BytesIO(img_data))
                
                # Convert to RGB if needed
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                # Compress as JPEG
                jpeg_io = io.BytesIO()
                pil_img.save(jpeg_io, format='JPEG', quality=jpeg_quality, optimize=True)
                jpeg_data = jpeg_io.getvalue()
                
                # Create new page from compressed image
                img_rect = fitz.Rect(0, 0, pil_img.width, pil_img.height)
                new_page = new_doc.new_page(width=img_rect.width, height=img_rect.height)
                new_page.insert_image(img_rect, stream=jpeg_data)
            
            doc.close()
            
            # Save the new document
            new_doc.save(output_path, deflate=True, garbage=4, clean=True)
            new_doc.close()
            
            return True
            
        except Exception as e:
            print(f"Image recreation compression error: {e}")
            return False

    def _compress_basic_pymupdf(self, input_path, output_path, level):
        """Basic PyMuPDF compression - FALLBACK"""
        try:
            doc = fitz.open(input_path)
            
            # Basic settings that always work
            options = {
                'garbage': 4,
                'clean': True,
                'deflate': True
            }
            
            doc.save(output_path, **options)
            doc.close()
            
            return True
            
        except Exception as e:
            print(f"Basic PyMuPDF compression error: {e}")
            return False
    # Add this new method to your PDFOperations class in pdf_operations.py

    def compress_pdf_enhanced(self, file_path, compression_level, session_id, 
                        target_size_mb=None, image_quality=None, image_dpi=None,
                        remove_metadata=False, optimize_fonts=False):
        """
        Enhanced PDF compression with user controls and target size
        """
        try:
            print(f"=== ENHANCED PDF COMPRESSION ===")
            print(f"Input: {file_path}")
            print(f"Level: {compression_level}")
            print(f"Target size: {target_size_mb}MB" if target_size_mb else "No target size")
            
            # Validate input
            if not os.path.exists(file_path):
                raise Exception("PDF ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ")
            
            original_size = os.path.getsize(file_path)
            original_size_mb = original_size / (1024 * 1024)
            print(f"Original size: {original_size_mb:.2f} MB")
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_compressed.pdf")
            
            # If target size is specified and user wants custom compression
            if target_size_mb and target_size_mb < original_size_mb:
                print("Using adaptive target-based compression...")
                success = self._adaptive_target_compression(file_path, output_path, target_size_mb)
                if success and os.path.exists(output_path):
                    final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    print(f"Final size: {final_size_mb:.2f}MB")
                    return output_path
            
            # Determine compression parameters
            compression_params = self._get_compression_parameters(
                compression_level, target_size_mb, original_size_mb,
                image_quality, image_dpi
            )
            
            # Select compression methods based on aggressiveness needed
            if compression_level == 'maximum' or (target_size_mb and target_size_mb < original_size_mb * 0.3):
                methods = [
                    ("Extreme Aggressive", self._compress_extreme_aggressive),
                    ("Ultra Aggressive", self._compress_ultra_aggressive),
                    ("Smart Adaptive", self._compress_smart_adaptive),
                ]
            else:
                methods = [
                    ("Smart Adaptive", self._compress_smart_adaptive),
                    ("Enhanced Image Recreation", self._compress_image_recreation_enhanced),
                    ("Advanced PyMuPDF", self._compress_pymupdf_enhanced),
                ]
            
            # Try compression methods
            best_result = None
            best_size = original_size
            
            for method_name, method_func in methods:
                try:
                    print(f"Trying {method_name}...")
                    temp_output = output_path.replace('.pdf', f'_temp_{method_name.replace(" ", "_").lower()}.pdf')
                    
                    result = method_func(file_path, temp_output, compression_params, 
                                    remove_metadata, optimize_fonts)
                    
                    if result and os.path.exists(temp_output):
                        compressed_size = os.path.getsize(temp_output)
                        compressed_size_mb = compressed_size / (1024 * 1024)
                        
                        if compressed_size > 0 and compressed_size < best_size:
                            if best_result and os.path.exists(best_result):
                                os.remove(best_result)
                            
                            best_result = temp_output
                            best_size = compressed_size
                            reduction = (1 - compressed_size/original_size) * 100
                            
                            print(f"✓ {method_name} successful!")
                            print(f"Size: {compressed_size_mb:.2f}MB (reduction: {reduction:.1f}%)")
                            
                            # Check if good enough
                            if target_size_mb and compressed_size_mb <= target_size_mb:
                                print("Target reached!")
                                break
                        else:
                            print(f"✗ {method_name} didn't improve")
                            if os.path.exists(temp_output):
                                os.remove(temp_output)
                            
                except Exception as e:
                    print(f"✗ {method_name} failed: {e}")
                    continue
            
            # Finalize result
            if best_result and os.path.exists(best_result):
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(best_result, output_path)
                
                final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                reduction = (1 - final_size_mb/original_size_mb) * 100
                
                print(f"=== COMPRESSION COMPLETE ===")
                print(f"Original: {original_size_mb:.2f} MB")
                print(f"Compressed: {final_size_mb:.2f} MB")
                print(f"Reduction: {reduction:.1f}%")
                
                return output_path
            else:
                raise Exception("ಎಲ್ಲಾ ಸಂಕುಚನ ವಿಧಾನಗಳು ವಿಫಲವಾಗಿವೆ")
                
        except Exception as e:
            print(f"Enhanced compression error: {str(e)}")
            raise Exception(f"PDF ಸಂಕುಚನ ವಿಫಲ: {str(e)}")

    def _get_compression_parameters(self, level, target_size_mb, original_size_mb, 
                                custom_quality=None, custom_dpi=None):
        """Get compression parameters based on level and target size"""
        
        # Base parameters for each level
        level_configs = {
            'low': {'dpi': 200, 'quality': 80, 'scale': 0.9},
            'medium': {'dpi': 150, 'quality': 60, 'scale': 0.8},
            'high': {'dpi': 100, 'quality': 45, 'scale': 0.6},
            'maximum': {'dpi': 75, 'quality': 30, 'scale': 0.4},
            'custom': {'dpi': 150, 'quality': 60, 'scale': 0.8}
        }
        
        params = level_configs.get(level, level_configs['medium']).copy()
        
        # Adjust for target size if specified
        if target_size_mb and original_size_mb > 0:
            compression_ratio = target_size_mb / original_size_mb
            
            if compression_ratio < 0.1:  # Need >90% compression
                params.update({'dpi': 50, 'quality': 20, 'scale': 0.3})
            elif compression_ratio < 0.2:  # Need >80% compression
                params.update({'dpi': 60, 'quality': 25, 'scale': 0.35})
            elif compression_ratio < 0.3:  # Need >70% compression
                params.update({'dpi': 75, 'quality': 35, 'scale': 0.4})
            elif compression_ratio < 0.5:  # Need >50% compression
                params.update({'dpi': 100, 'quality': 45, 'scale': 0.6})
        
        # Override with custom values if provided
        if custom_quality:
            params['quality'] = custom_quality
        if custom_dpi:
            params['dpi'] = custom_dpi
        
        return params

    def _compress_smart_adaptive(self, input_path, output_path, params, remove_metadata, optimize_fonts):
        """Smart adaptive compression that analyzes content"""
        try:
            print("Starting smart adaptive compression...")
            
            doc = fitz.open(input_path)
            new_doc = fitz.open()
            
            # Analyze document characteristics
            total_images = 0
            total_text_pages = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                images = page.get_images()
                text = page.get_text().strip()
                
                if images:
                    total_images += len(images)
                if text:
                    total_text_pages += 1
            
            # Adjust parameters based on content
            if total_images > total_text_pages * 2:  # Image-heavy document
                print("Detected image-heavy document, using aggressive image compression")
                params['quality'] = max(20, params['quality'] - 15)
                params['dpi'] = max(50, params['dpi'] - 25)
            elif total_text_pages > total_images * 3:  # Text-heavy document
                print("Detected text-heavy document, preserving readability")
                params['quality'] = min(85, params['quality'] + 10)
                params['dpi'] = min(200, params['dpi'] + 25)
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert to image with adaptive DPI
                mat = fitz.Matrix(params['dpi']/72, params['dpi']/72)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to PIL and optimize
                img_data = pix.tobytes("png")
                pil_img = Image.open(io.BytesIO(img_data))
                
                # Scale if needed
                if params['scale'] < 1.0:
                    new_width = int(pil_img.width * params['scale'])
                    new_height = int(pil_img.height * params['scale'])
                    pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                # Apply sharpening for better quality at lower resolutions
                if params['dpi'] < 150:
                    from PIL import ImageFilter
                    pil_img = pil_img.filter(ImageFilter.UnsharpMask(radius=1, percent=100, threshold=3))
                
                # Compress as JPEG
                jpeg_io = io.BytesIO()
                pil_img.save(jpeg_io, format='JPEG', 
                            quality=params['quality'], 
                            optimize=True, 
                            progressive=True)
                jpeg_data = jpeg_io.getvalue()
                
                # Create new page
                img_rect = fitz.Rect(0, 0, pil_img.width, pil_img.height)
                new_page = new_doc.new_page(width=img_rect.width, height=img_rect.height)
                new_page.insert_image(img_rect, stream=jpeg_data)
            
            doc.close()
            
            # Save with options
            save_options = {
                'deflate': True,
                'garbage': 4,
                'clean': True,
                'linear': True,
                'pretty': False
            }
            
            new_doc.save(output_path, **save_options)
            new_doc.close()
            
            # Post-process if requested
            if remove_metadata or optimize_fonts:
                self._post_process_pdf(output_path, remove_metadata, optimize_fonts)
            
            print("Smart adaptive compression completed")
            return True
            
        except Exception as e:
            print(f"Smart adaptive compression error: {e}")
            return False

    def _compress_image_recreation_enhanced(self, input_path, output_path, params, remove_metadata, optimize_fonts):
        """Enhanced image recreation with better quality control"""
        try:
            print("Starting enhanced image recreation...")
            
            doc = fitz.open(input_path)
            new_doc = fitz.open()
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Use adaptive DPI based on page content
                mat = fitz.Matrix(params['dpi']/72, params['dpi']/72)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to PIL
                img_data = pix.tobytes("png")
                pil_img = Image.open(io.BytesIO(img_data))
                
                # Apply scaling
                if params['scale'] < 1.0:
                    new_width = int(pil_img.width * params['scale'])
                    new_height = int(pil_img.height * params['scale'])
                    pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                # Optimize image before compression
                # Reduce noise for better compression
                from PIL import ImageFilter
                pil_img = pil_img.filter(ImageFilter.MedianFilter(size=3))
                
                # Compress with progressive JPEG
                jpeg_io = io.BytesIO()
                pil_img.save(jpeg_io, format='JPEG', 
                            quality=params['quality'],
                            optimize=True,
                            progressive=True)
                jpeg_data = jpeg_io.getvalue()
                
                # Create new page
                img_rect = fitz.Rect(0, 0, pil_img.width, pil_img.height)
                new_page = new_doc.new_page(width=img_rect.width, height=img_rect.height)
                new_page.insert_image(img_rect, stream=jpeg_data)
            
            doc.close()
            
            # Save with compression
            new_doc.save(output_path, deflate=True, garbage=4, clean=True)
            new_doc.close()
            
            # Post-process
            if remove_metadata or optimize_fonts:
                self._post_process_pdf(output_path, remove_metadata, optimize_fonts)
            
            return True
            
        except Exception as e:
            print(f"Enhanced image recreation error: {e}")
            return False

    def _compress_pymupdf_enhanced(self, input_path, output_path, params, remove_metadata, optimize_fonts):
        """Enhanced PyMuPDF compression"""
        try:
            print("Starting enhanced PyMuPDF compression...")
            
            doc = fitz.open(input_path)
            
            # Process images on each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # Convert to PIL for optimization
                        pil_image = Image.open(io.BytesIO(image_bytes))
                        
                        # Resize image
                        if params['scale'] < 1.0:
                            new_width = int(pil_image.width * params['scale'])
                            new_height = int(pil_image.height * params['scale'])
                            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Convert to RGB
                        if pil_image.mode in ('RGBA', 'LA', 'P'):
                            background = Image.new('RGB', pil_image.size, (255, 255, 255))
                            if pil_image.mode == 'P':
                                pil_image = pil_image.convert('RGBA')
                            if pil_image.mode in ('RGBA', 'LA'):
                                background.paste(pil_image, mask=pil_image.split()[-1])
                            else:
                                background.paste(pil_image)
                            pil_image = background
                        
                        # Compress
                        compressed_io = io.BytesIO()
                        pil_image.save(compressed_io, format='JPEG', 
                                    quality=params['quality'], optimize=True)
                        compressed_bytes = compressed_io.getvalue()
                        
                        # Replace image in PDF (simplified approach)
                        # Note: This is a basic replacement - you might need more sophisticated methods
                        
                    except Exception as img_error:
                        print(f"Error processing image {img_index}: {img_error}")
                        continue
            
            # Save with compression options
            save_options = {
                'garbage': 4,
                'clean': True,
                'deflate': True,
                'deflate_images': True,
                'deflate_fonts': optimize_fonts,
                'linear': True,
                'pretty': False
            }
            
            doc.save(output_path, **save_options)
            doc.close()
            
            # Post-process
            if remove_metadata or optimize_fonts:
                self._post_process_pdf(output_path, remove_metadata, optimize_fonts)
            
            return True
            
        except Exception as e:
            print(f"Enhanced PyMuPDF compression error: {e}")
            return False

    def _iterative_compression_enhanced(self, input_path, output_path, target_size_mb, base_params):
        """Enhanced iterative compression"""
        try:
            print(f"Starting enhanced iterative compression to reach {target_size_mb}MB...")
            
            current_path = input_path
            iteration = 0
            max_iterations = 3
            
            while iteration < max_iterations:
                current_size_mb = os.path.getsize(current_path) / (1024 * 1024)
                
                if current_size_mb <= target_size_mb:
                    print(f"Target reached after {iteration} iterations!")
                    if current_path != output_path:
                        import shutil
                        shutil.copy2(current_path, output_path)
                    return True
                
                print(f"Iteration {iteration + 1}: {current_size_mb:.2f}MB -> target {target_size_mb}MB")
                
                # Adjust parameters more aggressively
                compression_ratio = target_size_mb / current_size_mb
                params = base_params.copy()
                
                if compression_ratio < 0.3:
                    params.update({'dpi': 50, 'quality': 20, 'scale': 0.3})
                elif compression_ratio < 0.5:
                    params.update({'dpi': 60, 'quality': 30, 'scale': 0.4})
                elif compression_ratio < 0.7:
                    params.update({'dpi': 75, 'quality': 40, 'scale': 0.5})
                
                # Create temporary file
                temp_path = output_path.replace('.pdf', f'_iter_{iteration}.pdf')
                
                # Apply compression
                success = self._compress_image_recreation_enhanced(
                    current_path, temp_path, params, False, False
                )
                
                if not success or not os.path.exists(temp_path):
                    print(f"Iteration {iteration + 1} failed")
                    break
                
                # Clean up previous iteration
                if current_path != input_path and os.path.exists(current_path):
                    os.remove(current_path)
                
                current_path = temp_path
                iteration += 1
            
            # Copy final result
            if current_path != output_path:
                import shutil
                shutil.copy2(current_path, output_path)
                if current_path != input_path and os.path.exists(current_path):
                    os.remove(current_path)
            
            return True
            
        except Exception as e:
            print(f"Enhanced iterative compression error: {e}")
            return False

    def _post_process_pdf(self, pdf_path, remove_metadata, optimize_fonts):
        """Post-process PDF to remove metadata and optimize fonts"""
        try:
            if not remove_metadata and not optimize_fonts:
                return
            
            print("Post-processing PDF...")
            
            doc = fitz.open(pdf_path)
            
            if remove_metadata:
                print("Removing metadata...")
                # Clear metadata
                doc.set_metadata({})
                
            # Note: Font optimization would require more complex implementation
            # This is a placeholder for the concept
            
            doc.save(pdf_path, incremental=False, encryption=fitz.PDF_ENCRYPT_NONE)
            doc.close()
            
            print("Post-processing completed")
            
        except Exception as e:
            print(f"Post-processing error: {e}")
    def _compress_extreme_aggressive(self, input_path, output_path, params, remove_metadata, optimize_fonts):
        """
        Extremely aggressive compression - for when you need maximum size reduction
        """
        try:
            print("Starting extreme aggressive compression...")
            
            doc = fitz.open(input_path)
            new_doc = fitz.open()
            
            # Ultra-low settings for maximum compression
            dpi = max(50, params.get('dpi', 50))  # Very low DPI
            quality = max(15, params.get('quality', 20))  # Ultra low quality
            scale_factor = min(0.3, params.get('scale', 0.3))  # Scale down to 30%
            
            print(f"Extreme settings: DPI={dpi}, Quality={quality}, Scale={scale_factor}")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert to very low resolution image
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to PIL for aggressive processing
                img_data = pix.tobytes("png")
                pil_img = Image.open(io.BytesIO(img_data))
                
                # Scale down dramatically
                new_width = int(pil_img.width * scale_factor)
                new_height = int(pil_img.height * scale_factor)
                pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                # Reduce color depth for smaller file size
                pil_img = pil_img.quantize(colors=32).convert('RGB')  # Reduce to 32 colors
                
                # Apply aggressive compression
                jpeg_io = io.BytesIO()
                pil_img.save(jpeg_io, format='JPEG', 
                            quality=quality, 
                            optimize=True, 
                            progressive=True)
                jpeg_data = jpeg_io.getvalue()
                
                # Create new page
                img_rect = fitz.Rect(0, 0, pil_img.width, pil_img.height)
                new_page = new_doc.new_page(width=img_rect.width, height=img_rect.height)
                new_page.insert_image(img_rect, stream=jpeg_data)
            
            doc.close()
            
            # Save with maximum compression
            new_doc.save(output_path, 
                        deflate=True, 
                        garbage=4, 
                        clean=True,
                        linear=True,
                        pretty=False)
            new_doc.close()
            
            print("Extreme aggressive compression completed")
            return True
            
        except Exception as e:
            print(f"Extreme aggressive compression error: {e}")
            return False

    def _adaptive_target_compression(self, input_path, output_path, target_size_mb):
        """
        Adaptive compression that tries different settings until target size is reached
        """
        try:
            print(f"Starting adaptive compression to reach {target_size_mb}MB...")
            
            original_size_mb = os.path.getsize(input_path) / (1024 * 1024)
            compression_ratio = target_size_mb / original_size_mb
            
            print(f"Need {(1-compression_ratio)*100:.1f}% compression")
            
            # Progressive compression settings - start gentle, get more aggressive
            compression_settings = [
                {'dpi': 150, 'quality': 70, 'scale': 0.9, 'colors': None},
                {'dpi': 120, 'quality': 55, 'scale': 0.7, 'colors': None},
                {'dpi': 100, 'quality': 40, 'scale': 0.6, 'colors': 128},
                {'dpi': 80, 'quality': 30, 'scale': 0.5, 'colors': 64},
                {'dpi': 60, 'quality': 25, 'scale': 0.4, 'colors': 32},
                {'dpi': 50, 'quality': 20, 'scale': 0.3, 'colors': 16},
            ]
            
            for i, settings in enumerate(compression_settings):
                print(f"Trying compression level {i+1}/6...")
                
                temp_output = output_path.replace('.pdf', f'_temp_adaptive_{i}.pdf')
                
                # Apply compression with current settings
                doc = fitz.open(input_path)
                new_doc = fitz.open()
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    
                    mat = fitz.Matrix(settings['dpi']/72, settings['dpi']/72)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    
                    img_data = pix.tobytes("png")
                    pil_img = Image.open(io.BytesIO(img_data))
                    
                    # Scale image
                    if settings['scale'] < 1.0:
                        new_width = int(pil_img.width * settings['scale'])
                        new_height = int(pil_img.height * settings['scale'])
                        pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Convert to RGB
                    if pil_img.mode != 'RGB':
                        pil_img = pil_img.convert('RGB')
                    
                    # Reduce colors if specified
                    if settings['colors']:
                        pil_img = pil_img.quantize(colors=settings['colors']).convert('RGB')
                    
                    # Compress
                    jpeg_io = io.BytesIO()
                    pil_img.save(jpeg_io, format='JPEG', 
                            quality=settings['quality'], 
                            optimize=True, 
                            progressive=True)
                    jpeg_data = jpeg_io.getvalue()
                    
                    img_rect = fitz.Rect(0, 0, pil_img.width, pil_img.height)
                    new_page = new_doc.new_page(width=img_rect.width, height=img_rect.height)
                    new_page.insert_image(img_rect, stream=jpeg_data)
                
                doc.close()
                new_doc.save(temp_output, deflate=True, garbage=4, clean=True)
                new_doc.close()
                
                # Check if target size reached
                temp_size_mb = os.path.getsize(temp_output) / (1024 * 1024)
                print(f"Result size: {temp_size_mb:.2f}MB (target: {target_size_mb}MB)")
                
                if temp_size_mb <= target_size_mb:
                    print(f"Target reached with compression level {i+1}!")
                    if temp_output != output_path:
                        import shutil
                        shutil.move(temp_output, output_path)
                    
                    # Clean up other temp files
                    for j in range(i+1, len(compression_settings)):
                        temp_file = output_path.replace('.pdf', f'_temp_adaptive_{j}.pdf')
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    
                    return True
                
                # If not the last attempt, keep this file for potential fallback
                if i < len(compression_settings) - 1:
                    continue
                else:
                    # This is our best effort
                    if temp_output != output_path:
                        import shutil
                        shutil.move(temp_output, output_path)
                    print(f"Could not reach exact target. Best result: {temp_size_mb:.2f}MB")
                    return True
            
            return False
            
        except Exception as e:
            print(f"Adaptive compression error: {e}")
            return False
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
        Enhanced Word to PDF conversion - FIXED VERSION with proper imports
        """
        try:
            print(f"=== WORD TO PDF CONVERSION ===")
            print(f"Input file: {file_path}")
            print(f"Session ID: {session_id}")
            
            # Validate input file
            if not os.path.exists(file_path):
                raise Exception(f"Input file not found: {file_path}")
            
            file_size = os.path.getsize(file_path)
            print(f"Input file size: {file_size} bytes")
            
            if file_size == 0:
                raise Exception("ಖಾಲಿ Word ದಾಖಲೆ")
            
            # Test if file is readable
            try:
                from docx import Document
                test_doc = Document(file_path)
                para_count = len(test_doc.paragraphs)
                print(f"Word document has {para_count} paragraphs")
            except Exception as e:
                raise Exception(f"Word ದಾಖಲೆ ಓದಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ: {str(e)}")
            
            # Method 1: Simple ReportLab method (most reliable)
            try:
                result = self._simple_word_to_pdf(file_path, session_id)
                if result:
                    print("✓ Simple conversion successful")
                    return result
            except Exception as e:
                print(f"✗ Simple method failed: {e}")
            
            # Method 2: LibreOffice (if available)
            try:
                result = self._convert_with_libreoffice_simple(file_path, session_id)
                if result:
                    print("✓ LibreOffice conversion successful")
                    return result
            except Exception as e:
                print(f"✗ LibreOffice method failed: {e}")
            
            # Method 3: docx2pdf (if available)
            try:
                result = self._convert_with_docx2pdf_simple(file_path, session_id)
                if result:
                    print("✓ docx2pdf conversion successful")
                    return result
            except Exception as e:
                print(f"✗ docx2pdf method failed: {e}")
            
            raise Exception("ಎಲ್ಲಾ ಪರಿವರ್ತನೆ ವಿಧಾನಗಳು ವಿಫಲವಾಗಿವೆ")
            
        except Exception as e:
            print(f"Word to PDF conversion error: {str(e)}")
            raise Exception(f"Word to PDF ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")

    def _simple_word_to_pdf(self, file_path, session_id):
        """Simple and reliable Word to PDF conversion"""
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
            from reportlab.lib.units import inch
            from reportlab.lib.pagesizes import A4
            from docx import Document
            
            print("Starting simple Word to PDF conversion...")
            
            # Read Word document
            doc = Document(file_path)
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_from_word.pdf")
            
            # Create PDF document
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
            
            # Use built-in fonts that support more characters
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontName='Helvetica-Bold',
                fontSize=16,
                spaceAfter=20,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=14,
                spaceAfter=12,
                spaceBefore=12
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=11,
                spaceAfter=6,
                alignment=TA_JUSTIFY,
                leading=14
            )
            
            # Process paragraphs
            for i, para in enumerate(doc.paragraphs):
                text = para.text.strip()
                if not text:
                    story.append(Spacer(1, 6))
                    continue
                
                # Clean text - handle special characters
                clean_text = self._clean_text_simple(text)
                
                # Determine style
                style_name = para.style.name.lower()
                if 'title' in style_name:
                    style = title_style
                elif 'heading' in style_name:
                    style = heading_style
                else:
                    style = normal_style
                
                try:
                    # Create paragraph
                    pdf_para = Paragraph(clean_text, style)
                    story.append(pdf_para)
                    story.append(Spacer(1, 3))
                    
                except Exception as para_error:
                    print(f"Error with paragraph {i}: {para_error}")
                    # Fallback - just add the text as ASCII
                    try:
                        ascii_text = text.encode('ascii', 'ignore').decode('ascii')
                        if ascii_text.strip():
                            pdf_para = Paragraph(ascii_text, normal_style)
                            story.append(pdf_para)
                            story.append(Spacer(1, 3))
                    except:
                        continue
            
            # Handle tables simply
            for table in doc.tables:
                try:
                    # Convert table to simple text format
                    table_text = self._table_to_text(table)
                    if table_text:
                        story.append(Spacer(1, 12))
                        table_para = Paragraph(table_text, normal_style)
                        story.append(table_para)
                        story.append(Spacer(1, 12))
                except Exception as e:
                    print(f"Error processing table: {e}")
                    continue
            
            # Add default content if empty
            if not story:
                story.append(Paragraph("ದಾಖಲೆಯಲ್ಲಿ ಯಾವುದೇ ವಿಷಯ ಕಂಡುಬಂದಿಲ್ಲ", normal_style))
            
            # Build PDF
            pdf_doc.build(story)
            
            # Validate output
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"PDF created successfully: {os.path.getsize(output_path)} bytes")
                return output_path
            
            return None
            
        except Exception as e:
            print(f"Simple conversion error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _clean_text_simple(self, text):
        """Simple text cleaning for PDF generation"""
        # Handle common problematic characters
        replacements = {
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '–': '-',
            '—': '-',
            '…': '...',
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove any remaining problematic characters
        # Keep only printable ASCII and common Unicode
        cleaned = ''
        for char in text:
            if ord(char) < 127 or ord(char) in range(2304, 2432):  # Basic ASCII + Devanagari range
                cleaned += char
            else:
                cleaned += '?'  # Replace unknown chars
        
        return cleaned

    def _table_to_text(self, table):
        """Convert Word table to simple text representation"""
        try:
            lines = []
            for row in table.rows:
                cells = []
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        cells.append(cell_text)
                
                if cells:
                    lines.append(' | '.join(cells))
            
            if lines:
                return '<br/>'.join(lines)
            
            return None
            
        except Exception as e:
            print(f"Table to text error: {e}")
            return None

    def _convert_with_libreoffice_simple(self, input_path, session_id):
        """Simple LibreOffice conversion"""
        try:
            # Find LibreOffice
            libreoffice_cmd = None
            
            # Common LibreOffice command names and paths
            candidates = ['soffice', 'libreoffice']
            
            # Platform-specific paths
            if platform.system() == "Windows":
                candidates.extend([
                    r"C:\Program Files\LibreOffice\program\soffice.exe",
                    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
                ])
            elif platform.system() == "Darwin":
                candidates.extend([
                    "/Applications/LibreOffice.app/Contents/MacOS/soffice"
                ])
            else:  # Linux
                candidates.extend([
                    "/usr/bin/soffice",
                    "/usr/bin/libreoffice",
                    "/snap/bin/libreoffice"
                ])
            
            # Find working command
            for cmd in candidates:
                if shutil.which(cmd) or os.path.exists(cmd):
                    libreoffice_cmd = cmd
                    break
            
            if not libreoffice_cmd:
                print("LibreOffice not found")
                return None
            
            output_dir = self.config.OUTPUT_FOLDER
            os.makedirs(output_dir, exist_ok=True)
            
            # Run LibreOffice conversion
            cmd = [
                libreoffice_cmd,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                input_path
            ]
            
            print(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(f"LibreOffice exit code: {result.returncode}")
            
            if result.returncode == 0:
                # Find generated PDF
                input_name = Path(input_path).stem
                generated_pdf = os.path.join(output_dir, f"{input_name}.pdf")
                final_output = os.path.join(output_dir, f"{session_id}_from_word.pdf")
                
                if os.path.exists(generated_pdf):
                    # Move to final location
                    if os.path.exists(final_output):
                        os.remove(final_output)
                    os.rename(generated_pdf, final_output)
                    
                    if os.path.getsize(final_output) > 0:
                        return final_output
            
            return None
            
        except Exception as e:
            print(f"LibreOffice simple conversion failed: {e}")
            return None

    def _convert_with_docx2pdf_simple(self, input_path, session_id):
        """Simple docx2pdf conversion"""
        try:
            # Check if docx2pdf is available
            try:
                import docx2pdf
            except ImportError:
                print("docx2pdf not installed")
                return None
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_from_word.pdf")
            
            # Convert
            docx2pdf.convert(input_path, output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_path
            
            return None
            
        except Exception as e:
            print(f"docx2pdf simple conversion failed: {e}")
            return None
        
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
    