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
import psutil
import gc
from datetime import datetime
import json
import tempfile

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
        """
        Compress PDF file with proper compression techniques
    Returns compressed file path or raises exception
    """
        try:
            print(f"=== PDF COMPRESSION ===")
            print(f"Input: {file_path}")
            print(f"Level: {compression_level}")
        
        # Validate input
            if not os.path.exists(file_path):
                raise Exception("PDF ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ")
        
            original_size = os.path.getsize(file_path)
            print(f"Original size: {original_size:,} bytes ({original_size/1024/1024:.2f} MB)")
        
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
        
        # Try compression methods in order of preference
            methods = [
            ("PyMuPDF", self._compress_pymupdf),
            ("PyPDF2", self._compress_pypdf2),
            ("Basic", self._compress_basic)
            ]
        
            for method_name, method_func in methods:
                try:
                    print(f"Trying {method_name} compression...")
                    result = method_func(file_path, output_path, compression_level)
                
                    if result and os.path.exists(output_path):
                        compressed_size = os.path.getsize(output_path)
                    
                        if compressed_size > 0:
                            reduction = (1 - compressed_size/original_size) * 100
                            print(f"✓ {method_name} successful!")
                            print(f"Compressed size: {compressed_size:,} bytes ({compressed_size/1024/1024:.2f} MB)")
                            print(f"Size reduction: {reduction:.1f}%")
                        
                        # Validate the compressed PDF
                            if self._validate_compressed_pdf(output_path):
                                return output_path
                            else:
                                print(f"✗ {method_name} produced invalid PDF")
                                if os.path.exists(output_path):
                                    os.remove(output_path)
                        else:
                            print(f"✗ {method_name} produced empty file")
                    else:
                        print(f"✗ {method_name} failed to create output")
                    
                except Exception as e:
                    print(f"✗ {method_name} failed: {e}")
                    continue
        
        # If all methods failed
            raise Exception("ಎಲ್ಲಾ ಸಂಕುಚನ ವಿಧಾನಗಳು ವಿಫಲವಾಗಿವೆ")
        
        except Exception as e:
            print(f"Compression error: {str(e)}")
            raise Exception(f"PDF ಸಂಕುಚನ ವಿಫಲ: {str(e)}")

    def _compress_pymupdf(self, input_path, output_path, level):
        """Compress using PyMuPDF - Best method"""
        try:
            doc = fitz.open(input_path)
        
        # Compression settings based on level
            if level == 'high':
            # Aggressive compression
                options = {
                    'garbage': 4,        # Remove all unused objects
                'clean': True,       # Clean content streams
                'deflate': True,     # Compress all streams
                'deflate_images': True,   # Compress images
                'deflate_fonts': True,    # Compress fonts
                'linear': True,      # Linearize (optimize for web)
                'pretty': False,     # Don't pretty-print
                'ascii': False,      # Don't force ASCII
                'expand': 0          # Don't expand abbreviations
                }
            
            elif level == 'medium':
            # Balanced compression
                options = {
                'garbage': 3,
                'clean': True,
                'deflate': True,
                'deflate_images': True,
                'deflate_fonts': False,  # Keep fonts uncompressed
                'linear': True,
                'pretty': False
            }
            
            else:  # 'low'
            # Light compression
                options = {
                'garbage': 2,        # Remove some unused objects
                'clean': True,       # Clean content streams
                'deflate': True,     # Basic stream compression
                'deflate_images': False,  # Don't compress images
                'deflate_fonts': False,   # Don't compress fonts
                'linear': False,     # Don't linearize
                'pretty': False
                }
        
            print(f"PyMuPDF options: {options}")
        
        # Save with compression
            doc.save(output_path, **options)
            doc.close()
        
            return True
        
        except Exception as e:
            print(f"PyMuPDF compression error: {e}")
            return False

    def _compress_pypdf2(self, input_path, output_path, level):
        """Compress using PyPDF2 - Fallback method"""
        try:
            from PyPDF2 import PdfReader, PdfWriter
            
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            # Process each page
            for page_num, page in enumerate(reader.pages):
                # Compress content streams
                page.compress_content_streams()
                
                # For high compression, try to compress images
                if level == 'high':
                    try:
                        # Scale down images (crude but effective)
                        if '/XObject' in page.get('/Resources', {}):
                            pass  # More complex image processing would go here
                    except:
                        pass
                
                writer.add_page(page)
            
            # Remove duplicate objects for better compression
            writer.remove_duplication()
            
            # Write compressed PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            print(f"PyPDF2 compression error: {e}")
            return False

    def _compress_basic(self, input_path, output_path, level):
        """Basic compression - just copy with minimal processing"""
        try:
            import shutil
            
            # For basic compression, just copy the file
            # This ensures we always have a result, even if no compression
            shutil.copy2(input_path, output_path)
            
            print("Basic compression: File copied without modification")
            return True
            
        except Exception as e:
            print(f"Basic compression error: {e}")
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

    def _compress_with_image_optimization(self, file_path, session_id):
        """Advanced compression with image optimization for high compression"""
        try:
            print("Starting advanced image optimization...")
            
            doc = fitz.open(file_path)
            output_path = os.path.join(self.config.OUTPUT_FOLDER, f"{session_id}_compressed_advanced.pdf")
            
            # Create new document with optimized images
            new_doc = fitz.open()
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert page to image with reduced quality
                mat = fitz.Matrix(1.5, 1.5)  # Slightly higher resolution
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to PIL for better compression control
                img_data = pix.tobytes("png")
                
                from PIL import Image
                import io
                
                pil_img = Image.open(io.BytesIO(img_data))
                
                # Compress as JPEG with quality setting
                compressed_io = io.BytesIO()
                
                # Convert to RGB if necessary
                if pil_img.mode in ('RGBA', 'LA'):
                    # Create white background
                    background = Image.new('RGB', pil_img.size, (255, 255, 255))
                    if pil_img.mode == 'RGBA':
                        background.paste(pil_img, mask=pil_img.split()[-1])
                    else:
                        background.paste(pil_img)
                    pil_img = background
                
                # Save with compression
                pil_img.save(compressed_io, format='JPEG', quality=75, optimize=True)
                compressed_io.seek(0)
                
                # Create new page from compressed image
                img_pdf = fitz.open("pdf", compressed_io.getvalue())
                new_doc.insert_pdf(img_pdf)
                img_pdf.close()
            
            doc.close()
            
            # Save with maximum compression
            new_doc.save(output_path, garbage=4, clean=True, deflate=True)
            new_doc.close()
            
            print("Advanced compression completed")
            return output_path
            
        except Exception as e:
            print(f"Advanced compression error: {e}")
            raise Exception(f"Advanced compression failed: {str(e)}")    
    
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
        
    def generate_page_previews(self, pdf_path, session_id, preview_folder, max_pages=None, batch_size=20):
        """
        Generate thumbnail previews for PDF pages
        
        Args:
            pdf_path (str): Path to the PDF file
            session_id (str): Session identifier for organizing previews
            preview_folder (str): Base folder for storing preview images
            max_pages (int, optional): Maximum number of pages to generate previews for. 
                                    If None, processes all pages
            batch_size (int): Number of pages to process in each batch for memory management
        
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
        
            # Process all pages if max_pages is None, otherwise limit
            pages_to_process = total_pages if max_pages is None else min(total_pages, max_pages)
            
            print(f"Processing {pages_to_process} pages out of {total_pages} total pages...")
        
            previews = []
            
            # Process pages in batches to manage memory
            for batch_start in range(0, pages_to_process, batch_size):
                batch_end = min(batch_start + batch_size, pages_to_process)
                print(f"Processing batch: pages {batch_start + 1} to {batch_end}")
                
                for page_num in range(batch_start, batch_end):
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
                        
                        # Clean up memory
                        pix = None
                        img = None
                    
                    except Exception as e:
                        print(f"Error generating preview for page {page_num + 1}: {str(e)}")
                        continue
                
                # Optional: Force garbage collection after each batch
                import gc
                gc.collect()
        
            pdf_document.close()
        
            return {
                'total_pages': total_pages,
                'previews': previews,
                'session_id': session_id,
                'processed_pages': len(previews)
            }
        
        except Exception as e:
            print(f"Error generating PDF previews: {str(e)}")
            return None

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

# Usage examples:
# For processing all pages:
# result = self.generate_page_previews(pdf_path, session_id, preview_folder)

# For processing specific number of pages:
# result = self.generate_page_previews(pdf_path, session_id, preview_folder, max_pages=100)

# For large PDFs with custom batch size:
# result = self.generate_page_previews(pdf_path, session_id, preview_folder, batch_size=10)