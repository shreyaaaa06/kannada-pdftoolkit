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
import psutil
import gc
from datetime import datetime
import json
import tempfile
import os
import platform
import shutil
import subprocess
from pathlib import Path
import platform
import subprocess
import shutil
import os
from pathlib import Path
import threading
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
<<<<<<< HEAD

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
=======
    
    def split_pdf(self, file_path, session_id, pages="", split_method="pages", target_size_mb=10, pages_per_chunk=20, max_file_size_mb=500):
        """Enhanced PDF split function with proper split method handling"""
        try:
            print(f"=== ENHANCED PDF SPLIT DEBUG ===")
            print(f"File path: {file_path}")
            print(f"Session ID: {session_id}")
            print(f"Pages parameter: '{pages}'")
            print(f"Split method: '{split_method}'")
            print(f"Target size MB: {target_size_mb}")
            print(f"Pages per chunk: {pages_per_chunk}")
            print(f"Max file size: {max_file_size_mb}MB")
            print(f"Timestamp: {datetime.now()}")

            # ===== INPUT VALIDATION =====
            if not os.path.exists(file_path):
                raise Exception("PDF ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ")
            
            file_size_bytes = os.path.getsize(file_path)
            file_size_mb = file_size_bytes / (1024 * 1024)
            print(f"Input file size: {file_size_mb:.2f}MB ({file_size_bytes:,} bytes)")
            
            if file_size_bytes == 0:
                raise Exception("ಖಾಲಿ PDF ಫೈಲ್")
            
            if file_size_mb > max_file_size_mb:
                raise Exception(f"ಫೈಲ್ ತುಂಬಾ ದೊಡ್ಡದಾಗಿದೆ. ಗರಿಷ್ಠ ಗಾತ್ರ: {max_file_size_mb}MB")
            
            # Check available memory
            available_memory_mb = psutil.virtual_memory().available / (1024 * 1024)
            required_memory_mb = file_size_mb * 3
            print(f"Available memory: {available_memory_mb:.0f}MB, Required: {required_memory_mb:.0f}MB")
            
            if required_memory_mb > available_memory_mb:
                print("WARNING: Low memory detected, using memory-efficient processing")
            
            # ===== PDF VALIDATION =====
            print("Validating PDF structure...")
            reader = None
            total_pages = 0
            
            try:
                reader = PdfReader(file_path)
                total_pages = len(reader.pages)
                print(f"PDF validation successful: {total_pages} pages")
                
                if total_pages == 0:
                    raise Exception("PDF ಯಲ್ಲಿ ಯಾವುದೇ ಪುಟಗಳಿಲ್ಲ")
                
                if reader.is_encrypted:
                    raise Exception("ಎನ್‌ಕ್ರಿಪ್ಟ್ ಮಾಡಿದ PDF ಬೆಂಬಲಿತವಾಗಿಲ್ಲ")
                    
            except Exception as pdf_error:
                print(f"PyPDF2 validation failed: {pdf_error}")
                try:
                    doc = fitz.open(file_path)
                    total_pages = len(doc)
                    doc.close()
                    print(f"PyMuPDF validation successful: {total_pages} pages")
                    
                    if total_pages == 0:
                        raise Exception("PDF ಯಲ್ಲಿ ಯಾವುದೇ ಪುಟಗಳಿಲ್ಲ")
                        
                except Exception as fitz_error:
                    raise Exception(f"ಅಮಾನ್ಯ PDF ಫೈಲ್: {str(fitz_error)}")
            
            if total_pages == 1:
                raise Exception("ಒಂದೇ ಪುಟದ PDF ಅನ್ನು ವಿಭಜಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ")

            # ===== OUTPUT DIRECTORY SETUP =====
            temp_dir = tempfile.mkdtemp(prefix=f"pdf_split_{session_id}_")
            output_dir = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_split")
            
            try:
                os.makedirs(output_dir, exist_ok=True)
                print(f"Output directory: {output_dir}")
                print(f"Temp directory: {temp_dir}")
                
                # ===== DETERMINE SPLIT STRATEGY BASED ON METHOD =====
                print(f"Processing split method: {split_method}")
                
                created_files = []
                
                if split_method == "size":
                    print(f"Size-based splitting: target {target_size_mb}MB per file")
                    created_files = self._split_by_file_size(
                        file_path, temp_dir, target_size_mb, total_pages, session_id
                    )
                    
                elif split_method == "auto":
                    print(f"Auto chunking: {pages_per_chunk} pages per chunk")
                    created_files = self._auto_chunk_pdf(
                        file_path, temp_dir, pages_per_chunk, total_pages, session_id
                    )
                    
                elif split_method == "pages" or not split_method:
                    print("Page-based splitting")
                    if not pages or pages.strip() == "":
                        # Default: split in middle
                        split_point = max(1, total_pages // 2)
                        print(f"No pages specified, splitting at page {split_point}")
                        created_files = self._split_pdf_two_parts(
                            file_path, temp_dir, split_point, total_pages, session_id
                        )
                    else:
                        # Parse page specification
                        split_info = self._parse_split_specification_enhanced(pages, total_pages, file_size_mb, target_size_mb)
                        print(f"Split strategy: {split_info}")
                        
                        if split_info['type'] == 'single_split':
                            created_files = self._split_pdf_two_parts(
                                file_path, temp_dir, split_info['split_point'], total_pages, session_id
                            )
                        elif split_info['type'] == 'extract_pages':
                            created_files = self._extract_specific_pages(
                                file_path, temp_dir, split_info['pages'], session_id
                            )
                        elif split_info['type'] == 'multiple_splits':
                            created_files = self._split_multiple_ranges(
                                file_path, temp_dir, split_info['ranges'], session_id
                            )
                        elif split_info['type'] == 'auto_chunk':
                            created_files = self._auto_chunk_pdf(
                                file_path, temp_dir, split_info['pages_per_chunk'], total_pages, session_id
                            )
                        else:
                            # Fallback
                            split_point = max(1, total_pages // 2)
                            created_files = self._split_pdf_two_parts(
                                file_path, temp_dir, split_point, total_pages, session_id
                            )
                else:
                    raise Exception(f"ಅಮಾನ್ಯ ವಿಭಾಗ ವಿಧಾನ: {split_method}")
                
                # ===== VALIDATION AND CLEANUP =====
                print(f"Split operation completed. Files created: {len(created_files)}")
                
                validated_files = []
                total_output_size = 0
                
                for file_path_created in created_files:
                    try:
                        if not os.path.exists(file_path_created):
                            print(f"WARNING: File not found: {os.path.basename(file_path_created)}")
                            continue
                        
                        file_size = os.path.getsize(file_path_created)
                        if file_size == 0:
                            print(f"WARNING: Empty file: {os.path.basename(file_path_created)}")
                            continue
                        
                        try:
                            test_reader = PdfReader(file_path_created)
                            page_count = len(test_reader.pages)
                            if page_count == 0:
                                print(f"WARNING: PDF with no pages: {os.path.basename(file_path_created)}")
                                continue
                            print(f"✓ {os.path.basename(file_path_created)}: {page_count} pages, {file_size:,} bytes")
                            validated_files.append(file_path_created)
                            total_output_size += file_size
                            
                        except Exception as validation_error:
                            print(f"WARNING: Invalid PDF {os.path.basename(file_path_created)}: {validation_error}")
                            continue
                            
                    except Exception as file_error:
                        print(f"WARNING: Error validating {file_path_created}: {file_error}")
                        continue
                
                if not validated_files:
                    raise Exception("ಯಾವುದೇ ಸರಿಯಾದ PDF ಫೈಲ್‌ಗಳು ರಚಿಸಲಾಗಿಲ್ಲ")
                
                print(f"Validated files: {len(validated_files)}")
                print(f"Total output size: {total_output_size:,} bytes ({total_output_size/(1024*1024):.2f}MB)")
                
                # ===== CREATE OUTPUT ZIP =====
                zip_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_split.zip")
                print(f"Creating ZIP archive: {zip_path}")
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                    for i, file_path_to_zip in enumerate(validated_files):
                        try:
                            filename = os.path.basename(file_path_to_zip)
                            zipf.write(file_path_to_zip, filename)
                            print(f"Added to ZIP ({i+1}/{len(validated_files)}): {filename}")
                            
                        except Exception as zip_error:
                            print(f"ERROR: Failed to add {filename} to ZIP: {zip_error}")
                            continue
                
                # Validate ZIP file
                if not os.path.exists(zip_path):
                    raise Exception("ZIP ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ")
                
                zip_size = os.path.getsize(zip_path)
                if zip_size == 0:
                    raise Exception("ಖಾಲಿ ZIP ಫೈಲ್ ರಚಿಸಲಾಗಿದೆ")
                
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zipf:
                        zip_contents = zipf.namelist()
                        if not zip_contents:
                            raise Exception("ZIP ಫೈಲ್‌ನಲ್ಲಿ ಯಾವುದೇ ಫೈಲ್‌ಗಳಿಲ್ಲ")
                        print(f"ZIP verification successful: {len(zip_contents)} files")
                        
                except Exception as zip_verify_error:
                    raise Exception(f"ZIP ಫೈಲ್ ದೋಷಪೂರ್ಣ: {str(zip_verify_error)}")
                
                print(f"ZIP created successfully: {zip_size:,} bytes ({zip_size/(1024*1024):.2f}MB)")
                
                # ===== CLEANUP =====
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    print("Temporary files cleaned up")
                except Exception as cleanup_error:
                    print(f"WARNING: Cleanup failed: {cleanup_error}")
                
                if file_size_mb > 100:
                    gc.collect()
                    print("Memory cleanup performed")
                
                # ===== SUCCESS SUMMARY =====
                compression_ratio = (zip_size / total_output_size) * 100 if total_output_size > 0 else 100
                
                print(f"=== SPLIT OPERATION SUCCESSFUL ===")
                print(f"Input file: {file_size_mb:.2f}MB ({total_pages} pages)")
                print(f"Output files: {len(validated_files)} PDFs")
                print(f"ZIP file: {zip_size/(1024*1024):.2f}MB")
                print(f"Compression ratio: {compression_ratio:.1f}%")
                print(f"Output path: {zip_path}")
                print(f"=== END DEBUG ===")
                
                return zip_path
                
            except Exception as processing_error:
                try:
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
                raise processing_error
            
        except Exception as e:
            print(f"Enhanced split error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"PDF ವಿಭಾಗ ವಿಫಲ: {str(e)}")

    def _split_by_file_size(self, file_path, output_dir, target_size_mb, total_pages, session_id):
        """Split PDF based on target file size"""
        print(f"Starting size-based split: target {target_size_mb}MB per file")
        
        try:
            # Calculate approximate pages per chunk based on file size
            file_size_bytes = os.path.getsize(file_path)
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            # Estimate pages per chunk
            estimated_pages_per_chunk = max(1, int((target_size_mb / file_size_mb) * total_pages))
            print(f"Estimated pages per chunk: {estimated_pages_per_chunk}")
            
            created_files = []
            current_page = 1
            chunk_num = 1
            
            reader = PdfReader(file_path)
            
            while current_page <= total_pages:
                end_page = min(current_page + estimated_pages_per_chunk - 1, total_pages)
                
                writer = PdfWriter()
                pages_in_chunk = 0
                
                for page_num in range(current_page, end_page + 1):
                    if page_num <= len(reader.pages):
                        writer.add_page(reader.pages[page_num - 1])
                        pages_in_chunk += 1
                
                if pages_in_chunk > 0:
                    output_path = os.path.join(
                        output_dir, 
                        f"size_chunk_{chunk_num:03d}_pages_{current_page}_to_{end_page}.pdf"
                    )
                    
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    # Check actual file size
                    actual_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    created_files.append(output_path)
                    print(f"Created size chunk {chunk_num}: pages {current_page}-{end_page} ({pages_in_chunk} pages, {actual_size_mb:.2f}MB)")
                
                current_page = end_page + 1
                chunk_num += 1
                
                writer = None
                if chunk_num % 10 == 0:
                    gc.collect()
            
            return created_files
            
        except Exception as e:
            print(f"Size-based split error: {e}")
            raise Exception(f"ಗಾತ್ರದ ಆಧಾರದ ವಿಭಾಗ ವಿಫಲ: {str(e)}")
    
    def _parse_split_specification_enhanced(self, pages, total_pages, file_size_mb, chunk_size_mb):
        """Enhanced parsing with intelligent split strategy selection"""
        try:
            print(f"Parsing split specification with file size: {file_size_mb:.2f}MB")
            
            # For very large files, prefer chunking
            if file_size_mb > 200:
                pages_per_chunk = max(10, int((chunk_size_mb / file_size_mb) * total_pages))
                if not pages or pages.strip() == "":
                    print(f"Large file detected: auto-chunking with {pages_per_chunk} pages per chunk")
                    return {
                        'type': 'auto_chunk',
                        'pages_per_chunk': pages_per_chunk,
                        'reason': 'large_file_optimization'
                    }
            
            if not pages or pages.strip() == "":
                split_point = max(1, total_pages // 2)
                return {
                    'type': 'single_split',
                    'split_point': split_point,
                    'reason': 'default_middle_split'
                }
            
            pages_str = pages.strip().lower()
            
            # Handle special keywords
            if pages_str in ['auto', 'chunk', 'smart']:
                pages_per_chunk = max(10, min(50, total_pages // 5))
                return {
                    'type': 'auto_chunk',
                    'pages_per_chunk': pages_per_chunk,
                    'reason': 'user_requested_auto'
                }
            
            if pages_str in ['efficient', 'memory', 'large']:
                chunk_pages = max(20, min(100, total_pages // 10))
                return {
                    'type': 'memory_efficient_chunks',
                    'chunk_size': chunk_pages,
                    'reason': 'memory_efficient_requested'
                }
            
            # Original parsing logic
            try:
                split_point = int(pages_str)
                split_point = max(1, min(split_point, total_pages - 1))
                return {
                    'type': 'single_split',
                    'split_point': split_point,
                    'reason': 'user_specified_point'
                }
            except ValueError:
                pass
            
            # Range notation
            if '-' in pages_str and ',' not in pages_str:
                parts = pages_str.split('-')
                if len(parts) == 2:
                    try:
                        start = int(parts[0].strip())
                        end = int(parts[1].strip())
                        start = max(1, min(start, total_pages))
                        end = max(start, min(end, total_pages))
                        
                        return {
                            'type': 'extract_pages',
                            'pages': list(range(start, end + 1)),
                            'reason': 'user_specified_range'
                        }
                    except ValueError:
                        pass
            
            # Comma-separated pages/ranges
            if ',' in pages_str:
                try:
                    page_numbers = self._parse_page_ranges_enhanced(pages_str, total_pages)
                    if page_numbers:
                        return {
                            'type': 'extract_pages',
                            'pages': page_numbers,
                            'reason': 'user_specified_pages'
                        }
                except:
                    pass
            
            # Fallback
            split_point = max(1, total_pages // 2)
            return {
                'type': 'single_split',
                'split_point': split_point,
                'reason': 'fallback_middle_split'
            }
            
        except Exception as e:
            print(f"Parse specification error: {e}")
            return {
                'type': 'single_split',
                'split_point': max(1, total_pages // 2),
                'reason': 'error_fallback'
            }

    def _parse_page_ranges_enhanced(self, pages_str, total_pages):
        """Enhanced page range parsing with better error handling"""
        pages = set()
        
        try:
            parts = [part.strip() for part in pages_str.split(',') if part.strip()]
            
            for part in parts:
                if '-' in part:
                    range_parts = part.split('-', 1)
                    if len(range_parts) == 2:
                        try:
                            start = int(range_parts[0].strip())
                            end = int(range_parts[1].strip())
                            
                            start = max(1, min(start, total_pages))
                            end = max(start, min(end, total_pages))
                            
                            pages.update(range(start, end + 1))
                            
                        except ValueError:
                            print(f"Invalid range format: {part}")
                            continue
                else:
                    try:
                        page_num = int(part)
                        if 1 <= page_num <= total_pages:
                            pages.add(page_num)
                        else:
                            print(f"Page {page_num} out of range (1-{total_pages})")
                            
                    except ValueError:
                        print(f"Invalid page number: {part}")
                        continue
            
            result = sorted(list(pages))
            print(f"Parsed page ranges result: {len(result)} pages")
            return result
            
        except Exception as e:
            print(f"Enhanced page range parsing error: {e}")
            return []

    def _extract_pages_efficient(self, file_path, output_dir, page_numbers, filename_prefix, session_id):
        """Memory-efficient page extraction"""
        try:
            output_filename = f"{filename_prefix}_pages_{min(page_numbers)}_to_{max(page_numbers)}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            for page_num in page_numbers:
                if 1 <= page_num <= len(reader.pages):
                    page = reader.pages[page_num - 1]
                    writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            writer = None
            return output_path
            
        except Exception as e:
            print(f"Efficient page extraction error: {e}")
            return None

    def _split_pdf_two_parts(self, file_path, output_dir, split_point, total_pages, session_id):
        """Traditional two-part split with memory management"""
        created_files = []
        
        try:
            reader = PdfReader(file_path)
            
            # First part
            print(f"Creating first part: pages 1 to {split_point}")
            writer1 = PdfWriter()
            for i in range(split_point):
                writer1.add_page(reader.pages[i])
            
            output_path1 = os.path.join(output_dir, f"part_1_pages_1_to_{split_point}.pdf")
            with open(output_path1, 'wb') as output_file:
                writer1.write(output_file)
            created_files.append(output_path1)
            
            writer1 = None
            
            # Second part
            print(f"Creating second part: pages {split_point + 1} to {total_pages}")
            writer2 = PdfWriter()
            for i in range(split_point, total_pages):
                writer2.add_page(reader.pages[i])
            
            output_path2 = os.path.join(output_dir, f"part_2_pages_{split_point + 1}_to_{total_pages}.pdf")
            with open(output_path2, 'wb') as output_file:
                writer2.write(output_file)
            created_files.append(output_path2)
            
            return created_files
            
        except Exception as e:
            print(f"Two-part split error: {e}")
            raise Exception(f"ಎರಡು ಭಾಗಗಳ ವಿಭಾಗ ವಿಫಲ: {str(e)}")

    def _extract_specific_pages(self, file_path, output_dir, pages_to_extract, session_id):
        """Extract specific pages with validation"""
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            extracted_count = 0
            for page_num in pages_to_extract:
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
                    extracted_count += 1
            
            if extracted_count == 0:
                raise Exception("ಯಾವುದೇ ಸರಿಯಾದ ಪುಟಗಳು ಕಂಡುಬಂದಿಲ್ಲ")
            
            if len(pages_to_extract) <= 5:
                page_str = "_".join(map(str, pages_to_extract))
            else:
                page_str = f"{min(pages_to_extract)}_to_{max(pages_to_extract)}_and_others"
            
            output_path = os.path.join(output_dir, f"extracted_pages_{page_str}.pdf")
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"Extracted {extracted_count} pages to {os.path.basename(output_path)}")
            return [output_path]
            
        except Exception as e:
            print(f"Specific page extraction error: {e}")
            raise Exception(f"ನಿರ್ದಿಷ್ಟ ಪುಟಗಳ ಹೊರತೆಗೆಯುವಿಕೆ ವಿಫಲ: {str(e)}")

    def _split_multiple_ranges(self, file_path, output_dir, ranges, session_id):
        """Split into multiple ranges with memory management"""  
        created_files = []
        
        try:
            reader = PdfReader(file_path)
            
            for i, (start, end) in enumerate(ranges):
                writer = PdfWriter()
                pages_added = 0
                
                for page_num in range(start, end + 1):
                    if 1 <= page_num <= len(reader.pages):
                        writer.add_page(reader.pages[page_num - 1])
                        pages_added += 1
                
                if pages_added > 0:
                    output_path = os.path.join(output_dir, f"part_{i + 1}_pages_{start}_to_{end}.pdf")
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    created_files.append(output_path)
                    print(f"Created range {i + 1}: {pages_added} pages")
                
                writer = None
            
            return created_files
            
        except Exception as e:
            print(f"Multiple ranges split error: {e}")
            raise Exception(f"ಬಹು ವ್ಯಾಪ್ತಿ ವಿಭಾಗ ವಿಫಲ: {str(e)}")
    
    def _auto_chunk_pdf(self, file_path, output_dir, pages_per_chunk, total_pages, session_id):
            """Automatic chunking based on optimal chunk size"""
            print(f"Auto-chunking PDF: {pages_per_chunk} pages per chunk")
            
            created_files = []
            current_page = 1
            chunk_num = 1
            
            try:
                reader = PdfReader(file_path)
                
                while current_page <= total_pages:
                    end_page = min(current_page + pages_per_chunk - 1, total_pages)
                    
                    writer = PdfWriter()
                    pages_in_chunk = 0
                    
                    for page_num in range(current_page, end_page + 1):
                        if page_num <= len(reader.pages):
                            writer.add_page(reader.pages[page_num - 1])
                            pages_in_chunk += 1
                    
                    if pages_in_chunk > 0:
                        output_path = os.path.join(
                            output_dir, 
                            f"chunk_{chunk_num:03d}_pages_{current_page}_to_{end_page}.pdf"
                        )
                        
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                        
                        created_files.append(output_path)
                        print(f"Created chunk {chunk_num}: pages {current_page}-{end_page} ({pages_in_chunk} pages)")
                    
                    current_page = end_page + 1
                    chunk_num += 1
                    
                    writer = None
                    if chunk_num % 10 == 0:
                        gc.collect()
                
                return created_files
                
            except Exception as e:
                print(f"Auto-chunk error: {e}")
                raise Exception(f"ಸ್ವಯಂಚಾಲಿತ ಚಂಕಿಂಗ್ ವಿಫಲ: {str(e)}")
>>>>>>> 7755f4f7d2fb75faa5f9017e5bb4f5c1c9a17f1c

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
    
    def rotate_pdf(self, file_path, session_id, rotation_angle=90, pages="", apply_to_all=True):
        """Rotate PDF pages by specified angle"""
        try:
            print(f"=== PDF ROTATION DEBUG ===")
            print(f"File path: {file_path}")
            print(f"Session ID: {session_id}")
            print(f"Rotation angle: {rotation_angle}")
            print(f"Pages: {pages}")
            print(f"Apply to all: {apply_to_all}")
            
            # Validate input
            if not os.path.exists(file_path):
                raise Exception("PDF ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ")
            
            if rotation_angle not in [90, 180, 270, -90, -180, -270]:
                rotation_angle = 90  # Default to 90 degrees
            
            # Read PDF
            from PyPDF2 import PdfReader, PdfWriter
            import io
            
            # First pass: Read the original PDF into memory
            with open(file_path, 'rb') as original_file:
                original_data = original_file.read()
            
            reader = PdfReader(io.BytesIO(original_data))
            writer = PdfWriter()
            total_pages = len(reader.pages)
            
            if total_pages == 0:
                raise Exception("PDF ಯಲ್ಲಿ ಯಾವುದೇ ಪುಟಗಳಿಲ್ಲ")
            
            # Determine which pages to rotate
            if pages.strip():
                pages_to_rotate = self._parse_page_ranges_enhanced(pages, total_pages)
                print(f"Rotating specific pages: {pages_to_rotate}")
            else:
                pages_to_rotate = list(range(1, total_pages + 1))
                print(f"No specific pages - rotating all pages")
                        
            print(f"Pages to rotate: {pages_to_rotate}")
            
            # Process each page - create fresh reader for each page to avoid object sharing
            for page_num in range(1, total_pages + 1):
                if page_num in pages_to_rotate:
                    # Create a fresh reader for the page to be rotated
                    fresh_reader = PdfReader(io.BytesIO(original_data))
                    page = fresh_reader.pages[page_num - 1]
                    page.rotate(rotation_angle)
                    writer.add_page(page)
                    print(f"Rotated page {page_num} by {rotation_angle} degrees")
                else:
                    # Create a fresh reader for the non-rotated page
                    fresh_reader = PdfReader(io.BytesIO(original_data))
                    page = fresh_reader.pages[page_num - 1]
                    writer.add_page(page)
                    print(f"Added page {page_num} without rotation")
            
            # Create output path
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_rotated.pdf")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write rotated PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Validate output
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise Exception("ತಿರುಗಿಸಿದ PDF ರಚಿಸಲಾಗಿಲ್ಲ")
            
            print(f"=== ROTATION SUCCESSFUL ===")
            print(f"Output: {output_path}")
            print(f"Rotated {len(pages_to_rotate)} pages by {rotation_angle} degrees")
            
            return output_path
            
        except Exception as e:
            print(f"Rotation error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"PDF ತಿರುಗಿಸುವಿಕೆ ವಿಫಲ: {str(e)}")

    def _parse_page_ranges_enhanced(self, pages_str, total_pages):
        """Parse page ranges like '1,3,5-10' into list of page numbers"""
        try:
            pages = []
            parts = pages_str.split(',')
            
            for part in parts:
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    pages.extend(range(start, min(end + 1, total_pages + 1)))
                else:
                    page_num = int(part)
                    if 1 <= page_num <= total_pages:
                        pages.append(page_num)
            
            return list(set(pages))  # Remove duplicates
        except Exception as e:
            raise Exception(f"ಅಮಾನ್ಯ ಪುಟ ಸಂಖ್ಯೆಗಳು: {str(e)}")

    def generate_page_previews(self, pdf_path, session_id, preview_folder):
        """Generate page preview images for PDF - Updated to handle rotated pages"""
        try:
            # Create session-specific preview directory
            session_preview_dir = os.path.join(preview_folder, session_id)
            os.makedirs(session_preview_dir, exist_ok=True)
            
            # Open PDF with PyMuPDF for better image rendering
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            if total_pages == 0:
                return None
            
            previews = []
            
            # Generate preview for each page (limit to first 50 pages for performance)
            max_previews = min(total_pages, 50)
            
            for page_num in range(max_previews):
                try:
                    page = doc[page_num]
                    
                    # Create preview image
                    mat = fitz.Matrix(0.5, 0.5)  # Scale down for preview
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Convert to PIL Image
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Save preview image
                    preview_filename = f"page_{page_num + 1}.png"
                    preview_path = os.path.join(session_preview_dir, preview_filename)
                    img.save(preview_path, "PNG")
                    
                    previews.append({
                        'page_num': page_num + 1,
                        'image_path': preview_path
                    })
                    
                except Exception as page_error:
                    print(f"Error generating preview for page {page_num + 1}: {page_error}")
                    continue
            
            doc.close()
            
            return {
                'total_pages': total_pages,
                'previews': previews
            }
            
        except Exception as e:
            print(f"Preview generation error: {str(e)}")
        return None
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
<<<<<<< HEAD
        """Convert Word document to PDF"""
        try:
            return self._simple_word_to_pdf(file_path, session_id)
=======
        """
        Enhanced Word to PDF conversion - COMPLETE FIX with COM threading
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
            
            # Method 1: docx2pdf with proper COM threading
            try:
                result = self._convert_with_docx2pdf_threaded(file_path, session_id)
                if result:
                    print("✓ docx2pdf conversion successful")
                    return result
            except Exception as e:
                print(f"✗ docx2pdf method failed: {e}")
            
            # Method 2: LibreOffice (if available)
            try:
                result = self._convert_with_libreoffice_simple(file_path, session_id)
                if result:
                    print("✓ LibreOffice conversion successful")
                    return result
            except Exception as e:
                print(f"✗ LibreOffice method failed: {e}")
            
            # Method 3: Simple ReportLab method (most reliable fallback)
            try:
                result = self._simple_word_to_pdf_fixed(file_path, session_id)
                if result:
                    print("✓ Simple conversion successful")
                    return result
            except Exception as e:
                print(f"✗ Simple method failed: {e}")
            
            raise Exception("ಎಲ್ಲಾ ಪರಿವರ್ತನೆ ವಿಧಾನಗಳು ವಿಫಲವಾಗಿವೆ")
            
>>>>>>> 7755f4f7d2fb75faa5f9017e5bb4f5c1c9a17f1c
        except Exception as e:
            raise Exception(f"Word PDF ಪರಿವರ್ತನೆ ವಿಫಲ: {str(e)}")

<<<<<<< HEAD
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
            
            # Create output filename
            original_name = os.path.splitext(os.path.basename(file_path))[0]
            output_filename = f"{original_name}_protected.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            # Handle file name conflicts by adding a number if file already exists
            counter = 1
            while os.path.exists(output_path):
                output_filename = f"{original_name}_protected_{counter}.pdf"
                output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
                counter += 1
            
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

    def unlock_pdf(self, file_path, password, session_id):
        """Remove password protection from PDF file"""
        try:
            if not os.path.exists(file_path):
                raise Exception('PDF ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ')
            
            if not password or password.strip() == '':
                raise Exception('ಪಾಸ್‌ವರ್ಡ್ ಅಗತ್ಯ')
            
            # Check if file is actually encrypted
            try:
                from PyPDF2 import PdfReader, PdfWriter
                reader = PdfReader(file_path)
                if not reader.is_encrypted:
                    raise Exception('ಈ PDF ಫೈಲ್ ರಕ್ಷಿತವಾಗಿಲ್ಲ')
            except Exception as e:
                if "not encrypted" in str(e):
                    raise e
                # If we can't read it, assume it's encrypted and continue
                pass
            
            # Try to decrypt the PDF
            reader = PdfReader(file_path)
            
            if not reader.decrypt(password):
                raise Exception('ತಪ್ಪು ಪಾಸ್‌ವರ್ಡ್ - ದಯವಿಟ್ಟು ಸರಿಯಾದ ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ')
            
            # Create output filename
            original_name = os.path.splitext(os.path.basename(file_path))[0]
            output_filename = f"{original_name}_unlocked.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            # Handle file name conflicts by adding a number if file already exists
            counter = 1
            while os.path.exists(output_path):
                output_filename = f"{original_name}_unlocked_{counter}.pdf"
                output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
                counter += 1
            
            # Create new unlocked PDF
            writer = PdfWriter()
            
            # Add all pages to the writer
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                writer.add_page(page)
            
            # Write the unlocked PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Verify the output file was created properly
            if not os.path.exists(output_path):
                raise Exception('ಔಟ್‌ಪುಟ್ ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ')
            
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise Exception('ಖಾಲಿ ಫೈಲ್ ರಚಿಸಲಾಗಿದೆ')
            
            print(f"Unlocked PDF created successfully: {file_size} bytes")
            
            return {
                'success': True,
                'output_path': output_path,
                'filename': output_filename,
                'message': f'PDF ಯಶಸ್ವಿಯಾಗಿ ಅನ್‌ಲಾಕ್ ಮಾಡಲಾಗಿದೆ'
            }
            
        except Exception as e:
            print(f"Unlock error: {str(e)}")
            return {'success': False, 'error': f'PDF ಅನ್‌ಲಾಕ್ ವಿಫಲ: {str(e)}'}
=======
    def _convert_with_docx2pdf_threaded(self, input_path, session_id):
        """docx2pdf conversion with COM initialization in the worker thread"""
        try:
            # Check if docx2pdf is available
            try:
                import docx2pdf
            except ImportError:
                print("docx2pdf not installed")
                return None
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_from_word.pdf")
            
            # Remove existing output file if it exists
            if os.path.exists(output_path):
                os.remove(output_path)
            
            print(f"Converting {input_path} to {output_path}")
            
            # CRITICAL FIX: COM must be initialized in the same thread that uses it
            conversion_result = {'success': False, 'error': None, 'path': None}
            
            def convert_worker():
                """Worker function that initializes COM in its own thread"""
                try:
                    # Initialize COM in this thread
                    if platform.system() == "Windows":
                        import pythoncom
                        pythoncom.CoInitialize()
                        print("✓ COM initialized in worker thread")
                    
                    # Perform conversion
                    docx2pdf.convert(input_path, output_path)
                    
                    # Check if successful
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        conversion_result['success'] = True
                        conversion_result['path'] = output_path
                    else:
                        conversion_result['error'] = "No output file created"
                    
                except Exception as e:
                    conversion_result['error'] = str(e)
                    print(f"Worker thread error: {e}")
                finally:
                    # Clean up COM in this thread
                    if platform.system() == "Windows":
                        try:
                            import pythoncom
                            pythoncom.CoUninitialize()
                            print("✓ COM uninitialized in worker thread")
                        except:
                            pass
            
            # Run conversion in thread with timeout
            thread = threading.Thread(target=convert_worker)
            thread.daemon = True
            thread.start()
            thread.join(timeout=120)  # 2 minute timeout
            
            if thread.is_alive():
                print("✗ Conversion timed out")
                return None
            
            if conversion_result['success']:
                print(f"✓ docx2pdf conversion successful: {os.path.getsize(conversion_result['path'])} bytes")
                return conversion_result['path']
            else:
                print(f"✗ Conversion failed: {conversion_result['error']}")
                return None
            
        except Exception as e:
            print(f"✗ docx2pdf threaded conversion failed: {e}")
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

    def _simple_word_to_pdf_fixed(self, file_path, session_id):
        """Simple and reliable Word to PDF conversion - COMPLETE FIX"""
        try:
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
            from reportlab.lib.units import inch
            from reportlab.lib.pagesizes import A4
            from docx import Document
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont

            # Register Kannada font (optional - will fall back to default if fails)
            font_registered = False
            try:
                font_path = 'static/fonts/NotoSansKannada-Regular.ttf'
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('NotoSansKannada', font_path))
                    font_registered = True
                    print("✓ Kannada font registered")
                else:
                    print(f"⚠️ Kannada font not found at: {font_path}")
            except Exception as e:
                print(f"⚠️ Kannada font registration failed: {e}")

            print("Starting simple Word to PDF conversion...")
            
            # Read Word document
            doc = Document(file_path)
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_from_word.pdf")
            pdf_doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                leftMargin=0.75 * inch,
                rightMargin=0.75 * inch,
                topMargin=1 * inch,
                bottomMargin=1 * inch
            )
            
            # CRITICAL FIX: Initialize styles BEFORE using them
            styles = getSampleStyleSheet()
            
            # Create custom styles with proper font fallback
            font_name = 'NotoSansKannada' if font_registered else 'Helvetica'
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=12,
                alignment=TA_JUSTIFY,
                leading=16,
                spaceAfter=8
            )

            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontName=font_name,
                fontSize=16,
                alignment=TA_CENTER,
                spaceAfter=20
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading1'],
                fontName=font_name,
                fontSize=14,
                alignment=TA_LEFT,
                spaceBefore=12,
                spaceAfter=12
            )
            
            story = []
            
            # Process paragraphs
            for i, para in enumerate(doc.paragraphs):
                text = para.text.strip()
                if not text:
                    story.append(Spacer(1, 6))
                    continue
                
                # Clean text - handle special characters
                clean_text = self._clean_text_simple(text)
                
                # Determine style based on paragraph style
                style_name = para.style.name.lower() if para.style and para.style.name else ''
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
        
        # FIXED: Keep all Kannada characters and don't replace with '?'
        cleaned = ''
        for char in text:
            if ord(char) < 127:  # Basic ASCII
                cleaned += char
            elif ord(char) in range(2304, 2432):  # Devanagari range
                cleaned += char
            elif ord(char) in range(3200, 3327):  # Kannada Unicode range
                cleaned += char
            elif char in ['\n', '\r', '\t', ' ']:  # Whitespace characters
                cleaned += char
            else:
                # CRITICAL FIX: Don't replace with '?' - keep the original character
                cleaned += char  # CHANGED: This preserves Kannada characters that might be outside the range
        
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

    def _convert_with_docx2pdf_threaded(self, input_path, session_id):
        """docx2pdf conversion with COM initialization in worker thread - FIXED"""
        try:
            # Check if docx2pdf is available
            try:
                import docx2pdf
            except ImportError:
                print("docx2pdf not installed")
                return None
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_from_word.pdf")
            
            # Remove existing output file if it exists
            if os.path.exists(output_path):
                os.remove(output_path)
            
            print(f"Converting {input_path} to {output_path}")
            
            # Shared result container
            conversion_result = {'success': False, 'error': None, 'path': None}
            
            def convert_worker():
                """Worker function that initializes COM in its own thread"""
                try:
                    # CRITICAL FIX: Initialize COM in THIS thread
                    if platform.system() == "Windows":
                        import pythoncom
                        pythoncom.CoInitialize()
                        print("✓ COM initialized in worker thread")
                    
                    # Perform conversion
                    docx2pdf.convert(input_path, output_path)
                    
                    # Check if successful
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        conversion_result['success'] = True
                        conversion_result['path'] = output_path
                        print(f"✓ Conversion completed: {os.path.getsize(output_path)} bytes")
                    else:
                        conversion_result['error'] = "No output file created"
                    
                except Exception as e:
                    conversion_result['error'] = str(e)
                    print(f"✗ Worker thread error: {e}")
                finally:
                    # CRITICAL: Clean up COM in the same thread
                    if platform.system() == "Windows":
                        try:
                            import pythoncom
                            pythoncom.CoUninitialize()
                            print("✓ COM uninitialized in worker thread")
                        except Exception as cleanup_error:
                            print(f"⚠️ COM cleanup error: {cleanup_error}")
            
            # Run conversion in thread with timeout
            thread = threading.Thread(target=convert_worker)
            thread.daemon = True
            thread.start()
            thread.join(timeout=120)  # 2 minute timeout
            
            if thread.is_alive():
                print("✗ Conversion timed out")
                return None
            
            if conversion_result['success']:
                return conversion_result['path']
            else:
                print(f"✗ Conversion failed: {conversion_result.get('error', 'Unknown error')}")
                return None
            
        except Exception as e:
            print(f"✗ docx2pdf threaded conversion failed: {e}")
            return None

    # Alternative simpler approach - avoid threading altogether
    def _convert_with_docx2pdf_direct(self, input_path, session_id):
        """Direct docx2pdf conversion without threading"""
        try:
            # Check if docx2pdf is available
            try:
                import docx2pdf
            except ImportError:
                print("docx2pdf not installed")
                return None
            
            # Initialize COM before any operations
            if platform.system() == "Windows":
                import pythoncom
                pythoncom.CoInitialize()
                print("✓ COM initialized")
            
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_from_word.pdf")
            
            # Remove existing output file if it exists
            if os.path.exists(output_path):
                os.remove(output_path)
            
            print(f"Converting {input_path} to {output_path}")
            
            # Direct conversion
            docx2pdf.convert(input_path, output_path)
            
            # Check if successful
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"✓ Direct conversion successful: {os.path.getsize(output_path)} bytes")
                return output_path
            
            return None
            
        except Exception as e:
            print(f"✗ Direct docx2pdf conversion failed: {e}")
            return None
        finally:
            # Clean up COM
            if platform.system() == "Windows":
                try:
                    import pythoncom
                    pythoncom.CoUninitialize()
                    print("✓ COM uninitialized")
                except:
                    pass

        # Alternative method using pdf2image for full PDF processing
    def generate_page_previews_pdf2image(self, pdf_path, session_id, preview_folder, max_pages=None, batch_size=20):
        """
        Alternative method using pdf2image library for full PDF processing
        Requires: pip install pdf2image
        Also requires poppler-utils (system dependency)
        
        Args:
            pdf_path (str): Path to the PDF file
            session_id (str): Session identifier for organizing previews
            preview_folder (str): Base folder for storing preview images
            max_pages (int, optional): Maximum number of pages to generate previews for.
                                    If None, processes all pages
            batch_size (int): Number of pages to process in each batch
        """
        try:
            from pdf2image import convert_from_path
        
            # Create session-specific preview directory
            session_preview_dir = os.path.join(preview_folder, session_id)
            os.makedirs(session_preview_dir, exist_ok=True)
        
            # Get total page count
            total_pages = self.get_pdf_page_count(pdf_path)
            pages_to_process = total_pages if max_pages is None else min(total_pages, max_pages)
            
            print(f"Processing {pages_to_process} pages out of {total_pages} total pages...")
        
            previews = []
            
            # Process pages in batches to avoid memory issues
            for batch_start in range(0, pages_to_process, batch_size):
                batch_end = min(batch_start + batch_size, pages_to_process)
                first_page = batch_start + 1  # pdf2image uses 1-based indexing
                last_page = batch_end
                
                print(f"Processing batch: pages {first_page} to {last_page}")
                
                # Convert batch of PDF pages to images
                images = convert_from_path(
                    pdf_path,
                    dpi=150,  # Lower DPI for thumbnails
                    first_page=first_page,
                    last_page=last_page,
                    thread_count=2
                )
            
                for i, image in enumerate(images):
                    try:
                        # Resize to thumbnail
                        thumbnail_size = (200, 280)
                        image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                    
                        # Save thumbnail
                        page_num = batch_start + i + 1
                        filename = f"page_{page_num}.png"
                        file_path = os.path.join(session_preview_dir, filename)
                        image.save(file_path, "PNG", optimize=True)
                    
                        previews.append({
                            'page_num': page_num,
                            'image_path': file_path,
                            'width': image.width,
                            'height': image.height
                        })
                    
                    except Exception as e:
                        print(f"Error processing preview for page {batch_start + i + 1}: {str(e)}")
                        continue
                
                # Clean up memory
                images = None
                import gc
                gc.collect()
        
            return {
                'total_pages': total_pages,
                'previews': previews,
                'session_id': session_id,
                'processed_pages': len(previews)
            }
        
        except ImportError:
            print("pdf2image not installed. Please install: pip install pdf2image")
            return None
        except Exception as e:
            print(f"Error generating PDF previews with pdf2image: {str(e)}")
            return None

    # Helper method to get PDF page count (if not already implemented)
    def get_pdf_page_count(self, pdf_path):
        """Get the total number of pages in a PDF"""
        try:
            import fitz  # PyMuPDF
            pdf_document = fitz.open(pdf_path)
            page_count = len(pdf_document)
            pdf_document.close()
            return page_count
        except Exception as e:
            print(f"Error getting page count: {str(e)}")
            return 0

>>>>>>> 7755f4f7d2fb75faa5f9017e5bb4f5c1c9a17f1c
