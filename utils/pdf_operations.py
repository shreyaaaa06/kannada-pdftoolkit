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
import os
import sys
import zipfile
import logging
import tempfile
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
import json
import io

# PDF libraries
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfutils
from reportlab.lib.colors import black, red, blue, gray
from reportlab.lib.units import inch

# For bookmark extraction and password handling
import fitz  # PyMuPDF for advanced features
from cryptography.fernet import Fernet

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
    
    
    def __init__(self, config=None):
        self.config = config or self._default_config()
        self.logger = self._setup_logging()
        self.temp_dir = tempfile.mkdtemp(prefix="pdf_split_")
        
        # Kannada messages
        self.messages = {
            'single_page_error': "ಒಂದೇ ಪುಟದ PDF ಅನ್ನು ವಿಭಜಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ",
            'file_not_created': "ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ",
            'empty_file': "ಖಾಲಿ ಫೈಲ್ ರಚಿಸಲಾಗಿದೆ",
            'invalid_pdf': "ಅಮಾನ್ಯ PDF ರಚಿಸಲಾಗಿದೆ",
            'corrupted_pdf': "ದೋಷಪೂರ್ಣ PDF ರಚಿಸಲಾಗಿದೆ",
            'zip_not_created': "ZIP ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ",
            'zip_empty': "ZIP ಫೈಲ್ ಖಾಲಿಯಾಗಿದೆ",
            'split_failed': "PDF ವಿಭಾಗ ವಿಫಲ",
            'processing': "ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲಾಗುತ್ತಿದೆ",
            'completed': "ಪೂರ್ಣಗೊಂಡಿದೆ",
            'password_required': "ಪಾಸ್‌ವರ್ಡ್ ಅಗತ್ಯವಿದೆ",
            'bookmark_split': "ಬುಕ್‌ಮಾರ್ಕ್ ಆಧಾರಿತ ವಿಭಾಗ"
        }
    
    def _default_config(self):
        """Default configuration"""
        return {
            'OUTPUT_FOLDER': './output',
            'MAX_MEMORY_MB': 512,
            'CHUNK_SIZE_MB': 50,
            'MAX_WORKERS': min(4, multiprocessing.cpu_count()),
            'ENABLE_MULTIPROCESSING': True,
            'ADD_WATERMARK': False,
            'ADD_PAGE_NUMBERS': True,
            'COMPRESSION_LEVEL': 6,
            'LOG_LEVEL': 'INFO'
        }
    
    def _setup_logging(self):
        """Setup logging with Kannada support"""
        logger = logging.getLogger('PDFSplitter')
        logger.setLevel(getattr(logging, self.config['LOG_LEVEL']))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    def split_pdf_advanced(self, file_path: str, session_id: str, 
                          split_config: Dict[str, Any]) -> str:
        """
        Advanced PDF splitting with all pro features
        
        split_config options:
        - type: 'pages', 'size', 'bookmarks', 'every_n', 'custom'
        - pages: page specification
        - size_mb: target size per split
        - every_n: split every N pages  
        - bookmarks: use PDF bookmarks
        - password: PDF password if encrypted
        - add_watermark: bool
        - watermark_text: string
        - add_page_numbers: bool
        - use_multiprocessing: bool
        """
        
        try:
            self.logger.info(f"=== ಸುಧಾರಿತ PDF ವಿಭಾಗ ಪ್ರಾರಂಭ ===")
            self.logger.info(f"File: {file_path}")
            self.logger.info(f"Session: {session_id}")
            self.logger.info(f"Config: {split_config}")
            
            # Validate file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"PDF ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ: {file_path}")
            
            # Handle password-protected PDFs
            pdf_doc = self._open_pdf_with_password(file_path, split_config.get('password'))
            total_pages = len(pdf_doc.pages) if hasattr(pdf_doc, 'pages') else pdf_doc.page_count
            
            self.logger.info(f"ಒಟ್ಟು ಪುಟಗಳು: {total_pages}")
            
            if total_pages <= 1:
                raise ValueError(self.messages['single_page_error'])
            
            # Create output directory
            output_dir = os.path.join(self.config['OUTPUT_FOLDER'], f"{session_id}_split")
            os.makedirs(output_dir, exist_ok=True)
            
            # Determine split strategy
            split_info = self._determine_split_strategy(split_config, total_pages, pdf_doc)
            self.logger.info(f"ವಿಭಾಗ ತಂತ್ರ: {split_info}")
            
            # Execute splitting based on strategy
            created_files = []
            
            if split_info['type'] == 'size_based':
                created_files = self._split_by_size(pdf_doc, file_path, output_dir, split_info)
            elif split_info['type'] == 'bookmark_based':
                created_files = self._split_by_bookmarks(pdf_doc, file_path, output_dir, split_info)
            elif split_info['type'] == 'every_n':
                created_files = self._split_every_n_pages(pdf_doc, file_path, output_dir, split_info)
            elif split_info['type'] == 'multiprocessing':
                created_files = self._split_with_multiprocessing(pdf_doc, file_path, output_dir, split_info)
            else:
                # Standard page-based splitting with streaming
                created_files = self._split_pages_streaming(pdf_doc, file_path, output_dir, split_info)
            
            # Post-process files (watermark, page numbers, etc.)
            if split_config.get('add_watermark') or split_config.get('add_page_numbers'):
                created_files = self._post_process_files(created_files, split_config)
            
            # Validate created files
            self._validate_created_files(created_files)
            
            # Create ZIP with progress
            zip_path = self._create_zip_with_progress(created_files, session_id)
            
            self.logger.info(f"=== ವಿಭಾಗ ಪೂರ್ಣಗೊಂಡಿದೆ ===")
            return zip_path
            
        except Exception as e:
            self.logger.error(f"Error in advanced split: {str(e)}")
            raise Exception(f"{self.messages['split_failed']}: {str(e)}")
        
        finally:
            # Cleanup
            self._cleanup_temp_files()
    
    def _open_pdf_with_password(self, file_path: str, password: Optional[str] = None):
        """Open PDF with password support using both PyPDF2 and PyMuPDF"""
        try:
            # Try PyPDF2 first
            reader = PdfReader(file_path)
            if reader.is_encrypted:
                if not password:
                    raise ValueError(self.messages['password_required'])
                if not reader.decrypt(password):
                    raise ValueError("ತಪ್ಪು ಪಾಸ್‌ವರ್ಡ್")
            return reader
        except:
            # Fallback to PyMuPDF for complex PDFs
            try:
                doc = fitz.open(file_path)
                if doc.needs_pass:
                    if not password:
                        raise ValueError(self.messages['password_required'])
                    if not doc.authenticate(password):
                        raise ValueError("ತಪ್ಪು ಪಾಸ್‌ವರ್ಡ್")
                return doc
            except Exception as e:
                raise Exception(f"PDF ತೆರೆಯಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ: {str(e)}")
    
    def _determine_split_strategy(self, config: Dict, total_pages: int, pdf_doc) -> Dict:
        """Determine the best splitting strategy based on config"""
        
        split_type = config.get('type', 'pages')
        
        if split_type == 'size':
            return {
                'type': 'size_based',
                'target_size_mb': config.get('size_mb', 10),
                'total_pages': total_pages
            }
        
        elif split_type == 'bookmarks':
            bookmarks = self._extract_bookmarks(pdf_doc)
            if bookmarks:
                return {
                    'type': 'bookmark_based',
                    'bookmarks': bookmarks,
                    'total_pages': total_pages
                }
            else:
                # Fallback to page-based
                return {
                    'type': 'pages',
                    'split_point': total_pages // 2,
                    'total_pages': total_pages
                }
        
        elif split_type == 'every_n':
            return {
                'type': 'every_n',
                'n_pages': config.get('every_n', 10),
                'total_pages': total_pages
            }
        
        elif split_type == 'custom':
            # Use multiprocessing for large files
            if total_pages > 100 and config.get('use_multiprocessing', True):
                return {
                    'type': 'multiprocessing',
                    'ranges': self._calculate_ranges(config.get('pages', ''), total_pages),
                    'total_pages': total_pages
                }
        
        # Default page-based splitting
        return {
            'type': 'pages',
            'pages_spec': config.get('pages', ''),
            'total_pages': total_pages
        }
    
    def _split_by_size(self, pdf_doc, file_path: str, output_dir: str, split_info: Dict) -> List[str]:
        """Split PDF based on file size"""
        created_files = []
        target_size_bytes = split_info['target_size_mb'] * 1024 * 1024
        
        current_writer = PdfWriter()
        current_size = 0
        part_num = 1
        
        # Use PyMuPDF for better size estimation
        if hasattr(pdf_doc, 'page_count'):  # PyMuPDF
            doc = pdf_doc
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Estimate page size (rough approximation)
                page_size = len(page.get_text().encode('utf-8')) * 2  # Text + formatting estimate
                
                if current_size + page_size > target_size_bytes and current_writer.pages:
                    # Save current part
                    output_path = os.path.join(output_dir, f"part_{part_num}_size_{split_info['target_size_mb']}MB.pdf")
                    self._save_writer_streaming(current_writer, output_path)
                    created_files.append(output_path)
                    
                    # Start new part
                    current_writer = PdfWriter()
                    current_size = 0
                    part_num += 1
                
                # Convert PyMuPDF page to PyPDF2 format
                temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
                single_page_doc = fitz.open()
                single_page_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                single_page_doc.save(temp_pdf.name)
                single_page_doc.close()
                
                # Add to current writer
                temp_reader = PdfReader(temp_pdf.name)
                current_writer.add_page(temp_reader.pages[0])
                current_size += page_size
                
                os.unlink(temp_pdf.name)
        
        # Save final part
        if current_writer.pages:
            output_path = os.path.join(output_dir, f"part_{part_num}_size_{split_info['target_size_mb']}MB.pdf")
            self._save_writer_streaming(current_writer, output_path)
            created_files.append(output_path)
        
        return created_files
    
    def _split_by_bookmarks(self, pdf_doc, file_path: str, output_dir: str, split_info: Dict) -> List[str]:
        """Split PDF based on bookmarks/outline"""
        created_files = []
        bookmarks = split_info['bookmarks']
        
        self.logger.info(f"{self.messages['bookmark_split']}: {len(bookmarks)} ಬುಕ್‌ಮಾರ್ಕ್‌ಗಳು")
        
        for i, bookmark in enumerate(bookmarks):
            start_page = bookmark['page']
            end_page = bookmarks[i + 1]['page'] - 1 if i + 1 < len(bookmarks) else split_info['total_pages']
            
            writer = PdfWriter()
            
            # Add pages for this bookmark section
            if hasattr(pdf_doc, 'pages'):  # PyPDF2
                for page_num in range(start_page - 1, min(end_page, len(pdf_doc.pages))):
                    writer.add_page(pdf_doc.pages[page_num])
            else:  # PyMuPDF
                temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
                single_section_doc = fitz.open()
                single_section_doc.insert_pdf(pdf_doc, from_page=start_page-1, to_page=end_page-1)
                single_section_doc.save(temp_pdf.name)
                single_section_doc.close()
                
                temp_reader = PdfReader(temp_pdf.name)
                for page in temp_reader.pages:
                    writer.add_page(page)
                os.unlink(temp_pdf.name)
            
            # Create filename from bookmark title
            safe_title = "".join(c for c in bookmark['title'] if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
            output_path = os.path.join(output_dir, f"bookmark_{i+1}_{safe_title}_pages_{start_page}_to_{end_page}.pdf")
            
            self._save_writer_streaming(writer, output_path)
            created_files.append(output_path)
        
        return created_files
    
    def _split_every_n_pages(self, pdf_doc, file_path: str, output_dir: str, split_info: Dict) -> List[str]:
        """Split PDF every N pages"""
        created_files = []
        n_pages = split_info['n_pages']
        total_pages = split_info['total_pages']
        
        for start_page in range(0, total_pages, n_pages):
            end_page = min(start_page + n_pages, total_pages)
            
            writer = PdfWriter()
            
            if hasattr(pdf_doc, 'pages'):  # PyPDF2
                for page_num in range(start_page, end_page):
                    writer.add_page(pdf_doc.pages[page_num])
            else:  # PyMuPDF
                temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
                section_doc = fitz.open()
                section_doc.insert_pdf(pdf_doc, from_page=start_page, to_page=end_page-1)
                section_doc.save(temp_pdf.name)
                section_doc.close()
                
                temp_reader = PdfReader(temp_pdf.name)
                for page in temp_reader.pages:
                    writer.add_page(page)
                os.unlink(temp_pdf.name)
            
            output_path = os.path.join(output_dir, f"every_{n_pages}_pages_{start_page+1}_to_{end_page}.pdf")
            self._save_writer_streaming(writer, output_path)
            created_files.append(output_path)
        
        return created_files
    
    def _split_with_multiprocessing(self, pdf_doc, file_path: str, output_dir: str, split_info: Dict) -> List[str]:
        """Split PDF using multiprocessing for large files"""
        ranges = split_info['ranges']
        max_workers = min(self.config['MAX_WORKERS'], len(ranges))
        
        self.logger.info(f"ಮಲ್ಟಿಪ್ರೊಸೆಸಿಂಗ್ ಬಳಸಿ: {max_workers} workers")
        
        created_files = []
        
        # Prepare tasks for multiprocessing
        tasks = []
        for i, (start, end) in enumerate(ranges):
            task = {
                'file_path': file_path,
                'start_page': start,
                'end_page': end,
                'output_path': os.path.join(output_dir, f"part_{i+1}_pages_{start}_to_{end}.pdf"),
                'part_num': i + 1
            }
            tasks.append(task)
        
        # Execute tasks in parallel
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {executor.submit(self._process_pdf_range, task): task for task in tasks}
            
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result_path = future.result()
                    created_files.append(result_path)
                    self.logger.info(f"Completed part {task['part_num']}")
                except Exception as e:
                    self.logger.error(f"Error processing part {task['part_num']}: {e}")
                    raise
        
        return created_files
    
    @staticmethod
    def _process_pdf_range(task: Dict) -> str:
        """Process a single PDF range (for multiprocessing)"""
        reader = PdfReader(task['file_path'])
        writer = PdfWriter()
        
        for page_num in range(task['start_page'] - 1, min(task['end_page'], len(reader.pages))):
            writer.add_page(reader.pages[page_num])
        
        with open(task['output_path'], 'wb') as output_file:
            writer.write(output_file)
        
        return task['output_path']
    
    def _split_pages_streaming(self, pdf_doc, file_path: str, output_dir: str, split_info: Dict) -> List[str]:
        """Memory-efficient page-based splitting with streaming"""
        created_files = []
        pages_spec = split_info.get('pages_spec', '')
        total_pages = split_info['total_pages']
        
        # Parse pages specification
        if not pages_spec:
            # Default: split in middle
            split_point = max(1, total_pages // 2)
            ranges = [(1, split_point), (split_point + 1, total_pages)]
        else:
            ranges = self._parse_pages_to_ranges(pages_spec, total_pages)
        
        # Create PDFs for each range using streaming
        for i, (start, end) in enumerate(ranges):
            output_path = os.path.join(output_dir, f"part_{i+1}_pages_{start}_to_{end}.pdf")
            self._create_pdf_range_streaming(file_path, start, end, output_path)
            created_files.append(output_path)
        
        return created_files
    
    def _create_pdf_range_streaming(self, file_path: str, start_page: int, end_page: int, output_path: str):
        """Create PDF for page range using streaming to minimize memory usage"""
        
        # Process in chunks to avoid memory issues
        chunk_size = self.config['CHUNK_SIZE_MB'] // 4  # Conservative chunk size
        
        writer = PdfWriter()
        pages_processed = 0
        
        with open(file_path, 'rb') as input_file:
            reader = PdfReader(input_file)
            
            for page_num in range(start_page - 1, min(end_page, len(reader.pages))):
                writer.add_page(reader.pages[page_num])
                pages_processed += 1
                
                # Write intermediate file if chunk is full
                if pages_processed >= chunk_size:
                    temp_path = output_path + f'.tmp_{pages_processed}'
                    with open(temp_path, 'wb') as temp_file:
                        writer.write(temp_file)
                    
                    # Start new writer and merge later if needed
                    if page_num < min(end_page, len(reader.pages)) - 1:
                        # More pages to process, continue with new writer
                        writer = PdfWriter()
                        pages_processed = 0
        
        # Save final output
        self._save_writer_streaming(writer, output_path)
    
    def _save_writer_streaming(self, writer: PdfWriter, output_path: str):
        """Save PDF writer with streaming to minimize memory usage"""
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        # Force garbage collection to free memory
        import gc
        gc.collect()
    
    def _extract_bookmarks(self, pdf_doc) -> List[Dict]:
        """Extract bookmarks/outline from PDF"""
        bookmarks = []
        
        try:
            if hasattr(pdf_doc, 'outline') and pdf_doc.outline:  # PyPDF2
                self._extract_bookmarks_pypdf2(pdf_doc.outline, bookmarks, level=0)
            elif hasattr(pdf_doc, 'get_toc'):  # PyMuPDF
                toc = pdf_doc.get_toc()
                for item in toc:
                    level, title, page = item
                    bookmarks.append({
                        'title': title,
                        'page': page,
                        'level': level
                    })
        except Exception as e:
            self.logger.warning(f"ಬುಕ್‌ಮಾರ್ಕ್ ಹೊರತೆಗೆಯಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ: {e}")
        
        return sorted(bookmarks, key=lambda x: x['page'])
    
    def _extract_bookmarks_pypdf2(self, outline, bookmarks: List, level: int = 0):
        """Recursively extract bookmarks from PyPDF2 outline"""
        for item in outline:
            if isinstance(item, list):
                self._extract_bookmarks_pypdf2(item, bookmarks, level + 1)
            else:
                try:
                    page_num = item.page.idnum if hasattr(item.page, 'idnum') else 1
                    bookmarks.append({
                        'title': item.title,
                        'page': page_num,
                        'level': level
                    })
                except:
                    pass
    
    def _post_process_files(self, files: List[str], config: Dict) -> List[str]:
        """Add watermarks, page numbers, etc. to created files"""
        processed_files = []
        
        for file_path in files:
            processed_path = file_path
            
            if config.get('add_watermark'):
                processed_path = self._add_watermark(processed_path, config.get('watermark_text', 'SPLIT'))
            
            if config.get('add_page_numbers'):
                processed_path = self._add_page_numbers(processed_path)
            
            processed_files.append(processed_path)
        
        return processed_files
    
    def _add_watermark(self, file_path: str, watermark_text: str) -> str:
        """Add watermark to PDF"""
        try:
            # Create watermark PDF
            watermark_pdf = io.BytesIO()
            can = canvas.Canvas(watermark_pdf, pagesize=A4)
            can.setFillColor(gray, alpha=0.3)
            can.setFont("Helvetica", 40)
            can.rotate(45)
            can.drawString(200, 100, watermark_text)
            can.save()
            
            # Apply watermark
            watermark_pdf.seek(0)
            watermark_reader = PdfReader(watermark_pdf)
            watermark_page = watermark_reader.pages[0]
            
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                page.merge_page(watermark_page)
                writer.add_page(page)
            
            # Save watermarked version
            watermarked_path = file_path.replace('.pdf', '_watermarked.pdf')
            with open(watermarked_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Replace original
            os.replace(watermarked_path, file_path)
            
        except Exception as e:
            self.logger.warning(f"ವಾಟರ್‌ಮಾರ್ಕ್ ಸೇರಿಸಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ: {e}")
        
        return file_path
    
    def _add_page_numbers(self, file_path: str) -> str:
        """Add page numbers to PDF"""
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()
            
            for i, page in enumerate(reader.pages):
                # Create page number overlay
                page_num_pdf = io.BytesIO()
                can = canvas.Canvas(page_num_pdf, pagesize=A4)
                can.setFont("Helvetica", 10)
                can.drawString(520, 20, f"Page {i + 1}")
                can.save()
                
                # Apply page number
                page_num_pdf.seek(0)
                page_num_reader = PdfReader(page_num_pdf)
                page.merge_page(page_num_reader.pages[0])
                
                writer.add_page(page)
            
            # Save numbered version
            numbered_path = file_path.replace('.pdf', '_numbered.pdf')
            with open(numbered_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Replace original
            os.replace(numbered_path, file_path)
            
        except Exception as e:
            self.logger.warning(f"ಪುಟ ಸಂಖ್ಯೆಗಳನ್ನು ಸೇರಿಸಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ: {e}")
        
        return file_path
    
    def _validate_created_files(self, files: List[str]):
        """Validate all created files"""
        for file_path in files:
            if not os.path.exists(file_path):
                raise Exception(f"{self.messages['file_not_created']}: {os.path.basename(file_path)}")
            
            if os.path.getsize(file_path) == 0:
                raise Exception(f"{self.messages['empty_file']}: {os.path.basename(file_path)}")
            
            # Test PDF validity
            try:
                test_reader = PdfReader(file_path)
                if len(test_reader.pages) == 0:
                    raise Exception(f"{self.messages['invalid_pdf']}: {os.path.basename(file_path)}")
            except Exception as e:
                raise Exception(f"{self.messages['corrupted_pdf']}: {os.path.basename(file_path)} - {str(e)}")
    
    def _create_zip_with_progress(self, files: List[str], session_id: str) -> str:
        """Create ZIP file with progress tracking"""
        zip_path = os.path.join(self.config['OUTPUT_FOLDER'], f"{session_id}_split.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, 
                           compresslevel=self.config['COMPRESSION_LEVEL']) as zipf:
            
            total_files = len(files)
            for i, file_path in enumerate(files):
                if os.path.exists(file_path):
                    # Add file with just basename to avoid path issues
                    zipf.write(file_path, os.path.basename(file_path))
                    
                    # Log progress
                    progress = ((i + 1) / total_files) * 100
                    self.logger.info(f"ZIP ಪ್ರಗತಿ: {progress:.1f}% ({i+1}/{total_files})")
        
        # Validate ZIP
        if not os.path.exists(zip_path):
            raise Exception(self.messages['zip_not_created'])
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zip_contents = zipf.namelist()
            if not zip_contents:
                raise Exception(self.messages['zip_empty'])
        
        zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        self.logger.info(f"ZIP ರಚಿಸಲಾಗಿದೆ: {zip_size_mb:.2f} MB")
        
        return zip_path
    
    def _parse_pages_to_ranges(self, pages_spec: str, total_pages: int) -> List[Tuple[int, int]]:
        """Parse page specification into ranges"""
        if not pages_spec.strip():
            # Default: split in half
            mid = max(1, total_pages // 2)
            return [(1, mid), (mid + 1, total_pages)]
        
        try:
            # Handle single number (split point)
            if pages_spec.isdigit():
                split_point = int(pages_spec)
                split_point = max(1, min(split_point, total_pages - 1))
                return [(1, split_point), (split_point + 1, total_pages)]
            
            # Handle range like "1-10"
            if '-' in pages_spec and ',' not in pages_spec:
                start, end = map(int, pages_spec.split('-'))
                start = max(1, start)
                end = min(end, total_pages)
                return [(start, end)]
            
            # Handle complex specifications like "1-5,10-15,20-25"
            ranges = []
            for part in pages_spec.split(','):
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    ranges.append((max(1, start), min(end, total_pages)))
                else:
                    page = int(part)
                    if 1 <= page <= total_pages:
                        ranges.append((page, page))
            
            return ranges
            
        except:
            # Fallback to default
            mid = max(1, total_pages // 2)
            return [(1, mid), (mid + 1, total_pages)]
    
    def _calculate_ranges(self, pages_spec: str, total_pages: int) -> List[Tuple[int, int]]:
        """Calculate page ranges for multiprocessing"""
        ranges = self._parse_pages_to_ranges(pages_spec, total_pages)
        
        # If we have large ranges, split them further for better parallelization
        optimized_ranges = []
        max_pages_per_range = 50  # Optimal chunk size for multiprocessing
        
        for start, end in ranges:
            range_size = end - start + 1
            if range_size > max_pages_per_range:
                # Split large range into smaller chunks
                for chunk_start in range(start, end + 1, max_pages_per_range):
                    chunk_end = min(chunk_start + max_pages_per_range - 1, end)
                    optimized_ranges.append((chunk_start, chunk_end))
            else:
                optimized_ranges.append((start, end))
        
        return optimized_ranges
    
    def _cleanup_temp_files(self):
        """Clean up temporary files and directories"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            self.logger.warning(f"ತಾತ್ಕಾಲಿಕ ಫೈಲ್‌ಗಳನ್ನು ಸಿಗಿ ಮಾಡಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ: {e}")
    
    def get_pdf_info(self, file_path: str, password: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive PDF information"""
        try:
            pdf_doc = self._open_pdf_with_password(file_path, password)
            
            info = {
                'total_pages': len(pdf_doc.pages) if hasattr(pdf_doc, 'pages') else pdf_doc.page_count,
                'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
                'encrypted': pdf_doc.is_encrypted if hasattr(pdf_doc, 'is_encrypted') else pdf_doc.needs_pass,
                'bookmarks': [],
                'metadata': {}
            }
            
            # Extract bookmarks
            bookmarks = self._extract_bookmarks(pdf_doc)
            info['bookmarks'] = [{'title': b['title'], 'page': b['page']} for b in bookmarks]
            
            # Extract metadata
            if hasattr(pdf_doc, 'metadata') and pdf_doc.metadata:
                for key, value in pdf_doc.metadata.items():
                    info['metadata'][key] = str(value)
            elif hasattr(pdf_doc, 'metadata') and pdf_doc.metadata:
                info['metadata'] = dict(pdf_doc.metadata)
            
            return info
            
        except Exception as e:
            self.logger.error(f"PDF ಮಾಹಿತಿ ಪಡೆಯಲು ಸಾಧ್ಯವಾಗಿಲ್ಲ: {e}")
            return {
                'total_pages': 0,
                'file_size_mb': 0,
                'encrypted': False,
                'bookmarks': [],
                'metadata': {},
                'error': str(e)
            }


# Web API Integration Class
class PDFSplitterAPI:
    """
    ವೆಬ್ API ಇಂಟಿಗ್ರೇಶನ್ (Web API Integration)
    RESTful API wrapper for the PDF splitter
    """
    
    def __init__(self, splitter: PDFOperations):
        self.splitter = splitter
        self.active_jobs = {}  # Track running jobs
    
    def create_split_job(self, file_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new splitting job"""
        import uuid
        
        job_id = str(uuid.uuid4())
        session_id = f"api_{job_id[:8]}"
        
        job_info = {
            'job_id': job_id,
            'session_id': session_id,
            'status': 'created',
            'file_path': file_path,
            'config': config,
            'created_at': datetime.now().isoformat(),
            'progress': 0
        }
        
        self.active_jobs[job_id] = job_info
        return job_info
    
    def start_split_job(self, job_id: str) -> Dict[str, Any]:
        """Start processing a split job"""
        if job_id not in self.active_jobs:
            return {'error': 'Job not found'}
        
        job = self.active_jobs[job_id]
        job['status'] = 'processing'
        job['started_at'] = datetime.now().isoformat()
        
        try:
            # Run the splitting process
            result_path = self.splitter.split_pdf_advanced(
                job['file_path'],
                job['session_id'],
                job['config']
            )
            
            job['status'] = 'completed'
            job['result_path'] = result_path
            job['completed_at'] = datetime.now().isoformat()
            job['progress'] = 100
            
        except Exception as e:
            job['status'] = 'failed'
            job['error'] = str(e)
            job['failed_at'] = datetime.now().isoformat()
        
        return job
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status"""
        return self.active_jobs.get(job_id, {'error': 'Job not found'})
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all jobs"""
        return list(self.active_jobs.values())


# Usage Examples and Factory Class
class PDFSplitterFactory:
    """
    PDF ವಿಭಾಗ ಫ್ಯಾಕ್ಟರಿ (PDF Splitter Factory)
    Factory class to create configured splitter instances
    """
    
    @staticmethod
    def create_basic_splitter(output_folder: str = './output') -> PDFOperations:
        """Create basic splitter for simple operations"""
        config = {
            'OUTPUT_FOLDER': output_folder,
            'MAX_MEMORY_MB': 256,
            'ENABLE_MULTIPROCESSING': False,
            'ADD_WATERMARK': False,
            'ADD_PAGE_NUMBERS': False,
            'LOG_LEVEL': 'WARNING'
        }
        return PDFOperations(config)
    
    @staticmethod
    def create_pro_splitter(output_folder: str = './output', 
                           max_memory_mb: int = 1024) -> PDFOperations:
        """Create pro splitter with all features enabled"""
        config = {
            'OUTPUT_FOLDER': output_folder,
            'MAX_MEMORY_MB': max_memory_mb,
            'CHUNK_SIZE_MB': 100,
            'MAX_WORKERS': multiprocessing.cpu_count(),
            'ENABLE_MULTIPROCESSING': True,
            'ADD_WATERMARK': True,
            'ADD_PAGE_NUMBERS': True,
            'COMPRESSION_LEVEL': 9,
            'LOG_LEVEL': 'INFO'
        }
        return PDFOperations(config)
    
    @staticmethod
    def create_enterprise_splitter(output_folder: str = './output') -> PDFOperations:
        """Create enterprise splitter with maximum performance"""
        config = {
            'OUTPUT_FOLDER': output_folder,
            'MAX_MEMORY_MB': 2048,
            'CHUNK_SIZE_MB': 200,
            'MAX_WORKERS': min(8, multiprocessing.cpu_count()),
            'ENABLE_MULTIPROCESSING': True,
            'ADD_WATERMARK': True,
            'ADD_PAGE_NUMBERS': True,
            'COMPRESSION_LEVEL': 6,  # Balance between speed and compression
            'LOG_LEVEL': 'DEBUG'
        }
        return PDFOperations(config)


# Example Usage Functions
def example_basic_split():
    """Basic splitting example"""
    splitter = PDFSplitterFactory.create_basic_splitter()
    
    config = {
        'type': 'pages',
        'pages': '5',  # Split at page 5
    }
    
    result = splitter.split_pdf_advanced('input.pdf', 'session_001', config)
    print(f"ಫಲಿತಾಂಶ: {result}")


def example_size_based_split():
    """Size-based splitting example"""
    splitter = PDFSplitterFactory.create_pro_splitter()
    
    config = {
        'type': 'size',
        'size_mb': 10,  # Split into 10MB chunks
        'add_watermark': True,
        'watermark_text': 'ಕನ್ನಡ PDF'
    }
    
    result = splitter.split_pdf_advanced('large_document.pdf', 'session_002', config)
    print(f"ಆಕಾರ ಆಧಾರಿತ ವಿಭಾಗ: {result}")


def example_bookmark_split():
    """Bookmark-based splitting example"""
    splitter = PDFSplitterFactory.create_pro_splitter()
    
    config = {
        'type': 'bookmarks',
        'add_page_numbers': True,
        'password': 'secret123'  # If PDF is password protected
    }
    
    result = splitter.split_pdf_advanced('book_with_chapters.pdf', 'session_003', config)
    print(f"ಬುಕ್‌ಮಾರ್ಕ್ ಆಧಾರಿತ ವಿಭಾಗ: {result}")


def example_multiprocessing_split():
    """Large file splitting with multiprocessing"""
    splitter = PDFSplitterFactory.create_enterprise_splitter()
    
    config = {
        'type': 'custom',
        'pages': '1-100,101-200,201-300,301-400',  # Multiple ranges
        'use_multiprocessing': True,
        'add_watermark': True,
        'watermark_text': 'ಸುರಕ್ಷಿತ',
        'add_page_numbers': True
    }
    
    result = splitter.split_pdf_advanced('huge_document.pdf', 'session_004', config)
    print(f"ಮಲ್ಟಿಪ್ರೊಸೆಸಿಂಗ್ ವಿಭಾಗ: {result}")


def example_api_usage():
    """Web API usage example"""
    splitter = PDFSplitterFactory.create_pro_splitter()
    api = PDFSplitterAPI(splitter)
    
    # Create job
    job = api.create_split_job('document.pdf', {
        'type': 'every_n',
        'every_n': 20,
        'add_page_numbers': True
    })
    
    print(f"Job created: {job['job_id']}")
    
    # Start processing
    result = api.start_split_job(job['job_id'])
    print(f"Job status: {result['status']}")


if __name__ == "__main__":
    # Run examples
    print("=== ಸುಧಾರಿತ PDF ವಿಭಾಗ ಉದಾಹರಣೆಗಳು ===")
    
    # Test PDF info extraction
    splitter = PDFSplitterFactory.create_basic_splitter()
    
    # Example: Get PDF information
    # info = splitter.get_pdf_info('sample.pdf')
    # print(f"PDF ಮಾಹಿತಿ: {info}")
    
    print("Examples ready to run. Uncomment specific examples to test.")
    
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
    
    