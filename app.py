from flask import Flask, request, render_template, jsonify, send_file, session, url_for
import os
import uuid
import sys
from werkzeug.utils import secure_filename
from utils.file_handler import FileHandler
from utils.pdf_operations import PDFOperations
import config
import fitz  # PyMuPDF
from PIL import Image
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import traceback
import time
import sys
import html
from flask import redirect, url_for
from utils.pdf_compare import PDFCompare
import unicodedata
from flask import Response
import requests
from weasyprint import HTML, CSS
from flask import make_response
import json

# Initialize Flask app
app = Flask(__name__)

# Base directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')

# Initialize PDF compare instance
pdf_compare = PDFCompare()

# Configure Flask app
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

# UTF-8 encoding configuration
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set UTF-8 encoding for the entire application
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

@app.after_request  
def after_request(response):
    """Ensure UTF-8 encoding for all responses"""
    if response.content_type:
        if 'charset' not in response.content_type:
            if 'text/html' in response.content_type:
                response.content_type = 'text/html; charset=utf-8'
            elif 'application/json' in response.content_type:
                response.content_type = 'application/json; charset=utf-8'
    return response

# App configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['PREVIEW_FOLDER'] = 'static/previews'
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # 1000MB from file 2

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['PREVIEW_FOLDER'], exist_ok=True)

# Create temporary directory for comparison images
app.config['TEMP_FOLDER'] = 'static/temp'
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

# Initialize handlers
file_handler = FileHandler()
pdf_ops = PDFOperations()

@app.route('/')
def index():
    # Clear session on main page load to ensure fresh start (from file 2)
    session.clear()
    return render_template('index.html')

@app.route('/generate-preview', methods=['POST'])
def generate_preview():
    """Generate page previews for PDF files"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'ಯಾವುದೇ ಫೈಲ್ ಕಳುಹಿಸಲಾಗಿಲ್ಲ'})
        
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'success': False, 'error': 'ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಿ'})
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'PDF ಫೈಲ್ ಮಾತ್ರ ಬೆಂಬಲಿತ'})
        
        # Generate session ID if not exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        session_id = session['session_id']
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(temp_path)
        
        # Generate page previews
        preview_data = pdf_ops.generate_page_previews(temp_path, session_id, app.config['PREVIEW_FOLDER'])
        
        if preview_data:
            # Convert file paths to URLs
            for preview in preview_data['previews']:
                preview_dir = f"previews/{session_id}"
                filename = f"page_{preview['page_num']}.png"
                preview['image_path'] = url_for('static', filename=f"{preview_dir}/{filename}")
            
            return jsonify({
                'success': True,
                'total_pages': preview_data['total_pages'],
                'previews': preview_data['previews']
            })
        else:
            return jsonify({'success': False, 'error': 'ಪೂರ್ವವೀಕ್ಷಣೆ ರಚನೆ ವಿಫಲವಾಗಿದೆ'})
            
    except Exception as e:
        print(f"Preview generation error: {str(e)}")
        return jsonify({'success': False, 'error': f'ಪೂರ್ವವೀಕ್ಷಣೆ ದೋಷ: {str(e)}'})

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Always generate new session for each upload operation (from file 2)
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        session['processed_files'] = []  # Clear any previous files
        session.modified = True
        
        operation = request.form.get('operation')
        # Store original filenames for later use
        original_filenames = []
        for file in request.files.getlist('files'):
            if file and file.filename:
                original_filenames.append(file.filename)

        use_previous = request.form.get('use_previous') == 'true'
        
        print(f"=== DEBUG UPLOAD (NEW SESSION) ===")
        print(f"Operation: {operation}")
        print(f"New Session ID: {session_id}")
        print(f"Use previous: {use_previous}")
        print(f"Form data: {dict(request.form)}")
        
        # Get files from upload (enhanced file handling from file 2)
        files = request.files.getlist('files')
        if not files or all(not f.filename for f in files):
            return jsonify({'success': False, 'error': 'ಕನಿಷ್ಠ ಒಂದು ಫೈಲ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ'})
        
        file_paths = []
        
        for i, file in enumerate(files):  # Add enumerate to ensure unique processing
            if file and file.filename:
                # Enhanced filename processing with guaranteed uniqueness
                print(f"=== PROCESSING FILE {i+1} ===")
                print(f"Original filename: '{file.filename}'")
                print(f"Original filename bytes: {file.filename.encode('utf-8')}")
                
                original_filename = file.filename
                secure_name = secure_filename(original_filename)
                print(f"After secure_filename: '{secure_name}'")
                
                # CRITICAL FIX: Handle Kannada/Unicode filenames better
                if not secure_name or len(secure_name) < 3:
                    # If secure_filename stripped everything, preserve extension
                    if '.' in original_filename:
                        file_ext = original_filename.rsplit('.', 1)[1].lower()
                    else:
                        file_ext = 'pdf'  # Default extension
                    secure_name = f"file.{file_ext}"
                    print(f"Generated fallback filename: '{secure_name}'")
                elif '.' not in secure_name:
                    # Add extension if missing after secure_filename
                    if '.' in original_filename:
                        file_ext = original_filename.rsplit('.', 1)[1].lower()
                        secure_name = f"{secure_name}.{file_ext}"
                        print(f"Added missing extension: '{secure_name}'")
                
                # GUARANTEED UNIQUENESS: Always add file index + timestamp + UUID
                timestamp = str(int(time.time() * 1000))  # Millisecond precision
                unique_id = str(uuid.uuid4().hex[:8])
                file_index = f"f{i+1}"  # f1, f2, f3, etc.
                
                # Final unique filename with multiple uniqueness guarantees
                unique_filename = f"{session_id}_{file_index}_{timestamp}_{unique_id}_{secure_name}"
                print(f"Final unique filename: '{unique_filename}'")
                
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                print(f"Full file path: '{file_path}'")
                
                try:
                    # Save the file
                    file.save(file_path)
                    print(f"File saved successfully")
                    
                    # CRITICAL: Verify file was saved with correct content
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        print(f"Saved file size: {file_size} bytes")
                        
                        if file_size > 0:
                            file_paths.append(file_path)
                            print(f"✓ File {i+1} processed successfully: {file_path}")
                        else:
                            print(f"✗ File {i+1} is empty after save")
                    else:
                        print(f"✗ File {i+1} was not saved properly")
                        
                except Exception as save_error:
                    print(f"✗ Error saving file {i+1} ({file.filename}): {save_error}")
                    continue
                finally:
                    # Ensure file stream is properly closed
                    try:
                        if hasattr(file, 'close'):
                            file.close()
                        elif hasattr(file, 'stream') and hasattr(file.stream, 'close'):
                            file.stream.close()
                    except:
                        pass
                
                print(f"=== FILE {i+1} PROCESSING COMPLETE ===")
        
        print(f"=== FINAL SUMMARY ===")
        print(f"Total files processed: {len(file_paths)}")
        for idx, path in enumerate(file_paths):
            print(f"File {idx+1}: {path} (exists: {os.path.exists(path)}, size: {os.path.getsize(path) if os.path.exists(path) else 'N/A'})")
        print("=== END SUMMARY ===")
        
        if not file_paths:
            return jsonify({'success': False, 'error': 'ಯಾವುದೇ ಸರಿಯಾದ ಫೈಲ್‌ಗಳು ಅಪ್‌ಲೋಡ್ ಆಗಿಲ್ಲ'})
        
        # For merge operation, ensure we have at least 2 different files
        if operation == 'merge' and len(file_paths) < 2:
            return jsonify({'success': False, 'error': 'ವಿಲೀನಕ್ಕೆ ಕನಿಷ್ಠ 2 ವಿಭಿನ್ನ PDF ಫೈಲ್‌ಗಳು ಅಗತ್ಯ'})
        
        # Get operation parameters
        pages = request.form.get('pages', '') or request.form.get('selected_pages', '')
        compression = request.form.get('compression', 'medium')
        
        # Get split-specific parameters (from file 2)
        split_method = request.form.get('split_method', 'pages')
        target_size_mb = request.form.get('target_size_mb', '10')
        pages_per_chunk = request.form.get('pages_per_chunk', '20')
        max_file_size = request.form.get('max_file_size', '1000')
        
        print(f"Processing {len(file_paths)} files for operation: {operation}")
        
        result_path = None
        
        # Process operations
        try:
            if operation == 'merge':
                print("Processing merge operation")
                result_path = pdf_ops.merge_pdfs(file_paths, session_id)
                
            elif operation == 'split':
                print("Processing split operation")
                if not file_paths:
                    return jsonify({'success': False, 'error': 'ವಿಭಜನೆಗಾಗಿ PDF ಫೈಲ್ ಅಗತ್ಯ'})
                
                # Validate PDF file exists and is readable
                pdf_path = file_paths[0]
                if not os.path.exists(pdf_path):
                    return jsonify({'success': False, 'error': 'PDF ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ'})
                
                # Check if PDF has multiple pages
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(pdf_path)
                    total_pages = len(reader.pages)
                    print(f"PDF has {total_pages} pages")
                    
                    if total_pages < 2:
                        return jsonify({'success': False, 'error': 'ವಿಭಜನೆಗೆ ಕನಿಷ್ಠ 2 ಪುಟಗಳು ಬೇಕಾಗುತ್ತವೆ'})
                        
                except Exception as pdf_error:
                    print(f"PDF validation error: {pdf_error}")
                    return jsonify({'success': False, 'error': f'PDF ಫೈಲ್ ದೋಷಪೂರ್ಣ: {str(pdf_error)}'})
                
                # Enhanced split operation from file 2
                try:
                    target_size_mb_int = int(target_size_mb) if target_size_mb.isdigit() else 10
                    pages_per_chunk_int = int(pages_per_chunk) if pages_per_chunk.isdigit() else 20
                    max_file_size_int = int(max_file_size) if max_file_size.isdigit() else 1000
                except ValueError:
                    target_size_mb_int = 10
                    pages_per_chunk_int = 20
                    max_file_size_int = 1000
                
                result_path = pdf_ops.split_pdf(
                    pdf_path, 
                    session_id, 
                    pages=pages,
                    split_method=split_method,
                    target_size_mb=target_size_mb_int,
                    pages_per_chunk=pages_per_chunk_int,
                    max_file_size_mb=max_file_size_int
                )
                
            elif operation == 'extract':
                print("Processing extract operation")
                if not pages:
                    return jsonify({'success': False, 'error': 'ಹೊರತೆಗೆಯಲು ಪುಟ ಸಂಖ್ಯೆಗಳನ್ನು ನಮೂದಿಸಿ'})
                result_path = pdf_ops.extract_pages(file_paths[0], pages, session_id)

            elif operation == 'rotate':
                # Rotation operation from file 2
                print("=== ROTATION OPERATION DEBUG ===")
                print(f"Raw form data: {dict(request.form)}")
                
                # Get and validate rotation parameters
                rotation_angle_raw = request.form.get('rotation_angle', '90')
                pages_param = request.form.get('pages', '')
                apply_to_all_raw = request.form.get('apply_to_all', 'false')
                
                print(f"rotation_angle (raw): '{rotation_angle_raw}' (type: {type(rotation_angle_raw)})")
                print(f"pages_param: '{pages_param}'")
                print(f"apply_to_all (raw): '{apply_to_all_raw}' (type: {type(apply_to_all_raw)})")
                
                # Convert and validate rotation angle
                try:
                    rotation_angle = int(rotation_angle_raw)
                    print(f"rotation_angle (converted): {rotation_angle} (type: {type(rotation_angle)})")
                except (ValueError, TypeError) as e:
                    print(f"Error converting rotation_angle: {e}")
                    rotation_angle = 90
                
                # Convert apply_to_all
                if isinstance(apply_to_all_raw, str):
                    apply_to_all = apply_to_all_raw.lower() in ['true', '1', 'yes', 'on']
                else:
                    apply_to_all = bool(apply_to_all_raw)
                
                print(f"apply_to_all (converted): {apply_to_all} (type: {type(apply_to_all)})")
                print(f"file_paths[0]: {file_paths[0] if file_paths else 'No files'}")
                print("=== CALLING ROTATE_PDF ===")
                
                result_path = pdf_ops.rotate_pdf(
                    file_paths[0], 
                    session_id, 
                    rotation_angle, 
                    pages_param, 
                    apply_to_all
                )
                
                print(f"Result path: {result_path}")
                print("=== ROTATION OPERATION COMPLETE ===")

            elif operation == 'delete':
                print("Processing delete operation")
                if not pages:
                    return jsonify({'success': False, 'error': 'ಅಳಿಸಲು ಪುಟ ಸಂಖ್ಯೆಗಳನ್ನು ನಮೂದಿಸಿ'})
                result_path = pdf_ops.delete_pages(file_paths[0], pages, session_id)
                
            elif operation == 'compress':
                print("Processing compress operation")
                
                # Get compression parameters
                compression_level = request.form.get('compression', 'medium')
                target_size_mb = request.form.get('target_size_mb')
                
                # Convert target size to float if provided
                target_size = None
                if target_size_mb and target_size_mb.strip():
                    try:
                        target_size = float(target_size_mb)
                        print(f"Target size specified: {target_size}MB")
                    except (ValueError, TypeError):
                        target_size = None
                        print("Invalid target size, ignoring")
                
                # Get advanced options if provided
                image_quality = request.form.get('imageQuality')
                image_dpi = request.form.get('imageDPI')
                remove_metadata = request.form.get('removeMetadata') == 'on'
                optimize_fonts = request.form.get('optimizeFonts') == 'on'
                
                # Convert string parameters to integers if provided and valid
                quality = None
                dpi = None
                
                if image_quality and image_quality.strip():
                    try:
                        quality = int(image_quality)
                        quality = max(10, min(100, quality))  # Clamp between 10-100
                        print(f"Image quality: {quality}")
                    except (ValueError, TypeError):
                        print("Invalid image quality, using default")
                
                if image_dpi and image_dpi.strip():
                    try:
                        dpi = int(image_dpi)
                        dpi = max(50, min(600, dpi))  # Clamp between 50-600
                        print(f"Image DPI: {dpi}")
                    except (ValueError, TypeError):
                        print("Invalid image DPI, using default")
                
                print(f"Compression settings: level={compression_level}, target={target_size}MB")
                print(f"Advanced options: quality={quality}, dpi={dpi}, remove_metadata={remove_metadata}, optimize_fonts={optimize_fonts}")
                
                # Use the enhanced compression method
                result_path = pdf_ops.compress_pdf_enhanced(
                    file_paths[0], 
                    compression_level, 
                    session_id,
                    target_size_mb=target_size,
                    image_quality=quality,
                    image_dpi=dpi,
                    remove_metadata=remove_metadata,
                    optimize_fonts=optimize_fonts
                )
                
            elif operation == 'pdf_to_jpeg':
                print("Processing PDF to JPEG operation")
                result_path = pdf_ops.pdf_to_images(file_paths[0], session_id)
                
            elif operation == 'jpeg_to_pdf':
                print("Processing JPEG to PDF operation")
                result_path = pdf_ops.images_to_pdf(file_paths, session_id)
                
            elif operation == 'pdf_to_word':
                print("Processing PDF to Word operation")
                result_path = pdf_ops.pdf_to_word(file_paths[0], session_id)

            elif operation == 'word_to_pdf':
                # Enhanced Word to PDF operation from file 2
                print("=== PROCESSING WORD TO PDF OPERATION (FIXED) ===")
                print(f"File paths: {file_paths}")
                
                if not file_paths:
                    return jsonify({'success': False, 'error': 'Word ಫೈಲ್ ಅಗತ್ಯ'})
                
                word_file_path = file_paths[0]
                print(f"Processing Word file: {word_file_path}")
                
                # Validate file exists and has content
                if not os.path.exists(word_file_path):
                    return jsonify({'success': False, 'error': 'Word ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ'})
                
                file_size = os.path.getsize(word_file_path)
                if file_size == 0:
                    return jsonify({'success': False, 'error': 'ಖಾಲಿ Word ಫೈಲ್'})
                
                # Check file extension
                file_ext = os.path.splitext(word_file_path)[1].lower()
                if file_ext not in ['.doc', '.docx']:
                    return jsonify({'success': False, 'error': 'ಮಾನ್ಯವಾದ Word ಫೈಲ್ ಅಲ್ಲ (.doc ಅಥವಾ .docx ಬೇಕು)'})
                
                print(f"File validation passed - Extension: {file_ext}, Size: {file_size} bytes")
                
                # Call the conversion function with proper error handling
                try:
                    result_path = pdf_ops.word_to_pdf(word_file_path, session_id)
                    print(f"word_to_pdf returned: {result_path}")
                    
                    if result_path and os.path.exists(result_path):
                        result_size = os.path.getsize(result_path)
                        print(f"✓ Word to PDF conversion successful: {result_size} bytes")
                        
                        if result_size == 0:
                            print("✗ Result file is empty")
                            return jsonify({'success': False, 'error': 'ಪರಿವರ್ತನೆ ವಿಫಲ - ಖಾಲಿ PDF ರಚಿಸಲಾಗಿದೆ'})
                    else:
                        print("✗ Word to PDF conversion failed - no result file")
                        return jsonify({'success': False, 'error': 'Word to PDF ಪರಿವರ್ತನೆ ವಿಫಲವಾಗಿದೆ'})
                        
                except Exception as word_error:
                    print(f"✗ Word to PDF conversion error: {word_error}")
                    traceback.print_exc()
                    return jsonify({'success': False, 'error': f'Word to PDF ಪರಿವರ್ತನೆ ವಿಫಲ: {str(word_error)}'})
                
                print("=== WORD TO PDF OPERATION COMPLETE ===")
            
            elif operation == 'compare':
                print("Processing compare operation")
                if len(file_paths) != 2:
                    return jsonify({'success': False, 'error': 'ಹೋಲಿಕೆಗಾಗಿ ನಿಖರವಾಗಿ 2 PDF ಫೈಲ್‌ಗಳು ಬೇಕು'})
                
                session.pop('comparison_data', None)
                session.pop('comparison_report_url', None)
                compare_type = 'both'
                
                # Maintain upload order
                pdf1_path = file_paths[0]  # First uploaded file - LEFT side
                pdf2_path = file_paths[1]  # Second uploaded file - RIGHT side
                
                print(f"Comparing: {pdf1_path} (LEFT) vs {pdf2_path} (RIGHT)")
                
                # Use the dedicated comparison class with maintained order
                comparison_results = pdf_compare.compare_pdfs_web(pdf1_path, pdf2_path, session_id, compare_type)
                
                if not comparison_results:
                    return jsonify({'success': False, 'error': 'ಹೋಲಿಕೆ ವಿಫಲವಾಗಿದೆ'})
                
                # Store comparison data in session for the results page
                session['comparison_summary'] = {
                    'file1_name': comparison_results['file1_name'],
                    'file2_name': comparison_results['file2_name'],
                    'file1_pages': comparison_results['file1_pages'],
                    'file2_pages': comparison_results['file2_pages'],
                    'total_text_changes': comparison_results['summary']['total_text_changes'],
                    'visual_diff_pages': comparison_results['summary']['visual_diff_pages'],
                    'session_id': session_id
                }

                # Save full data to file instead of session
                comparison_file = os.path.join(app.config['OUTPUT_FOLDER'], f'{session_id}_comparison.json')
                with open(comparison_file, 'w', encoding='utf-8') as f:
                    json.dump(comparison_results, f, ensure_ascii=False, indent=2)

                session['comparison_report_url'] = comparison_results.get('report_path', '')
                session.modified = True

                # Return success with redirect to results page
                return jsonify({
                    'success': True,
                    'message': 'ಹೋಲಿಕೆ ಪೂರ್ಣಗೊಂಡಿದೆ!',
                    'redirect_url': '/compare-result',
                    'comparison_data': comparison_results
                })
            else:
                return jsonify({'success': False, 'error': f'ಅಮಾನ್ಯ ಕಾರ್ಯಾಚರಣೆ: {operation}'})
                
        except Exception as op_error:
            print(f"Operation error: {str(op_error)}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'ಕಾರ್ಯಾಚರಣೆ ವಿಫಲ: {str(op_error)}'})
        
        # Clean up input files after successful processing (from file 2)
        try:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    try:
                        # Add small delay to ensure file handles are released
                        time.sleep(0.1)
                        os.remove(file_path)
                        print(f"Cleaned up input file: {file_path}")
                    except Exception as cleanup_error:
                        print(f"Warning: Could not clean up {file_path}: {cleanup_error}")
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")
        
        # Generate user-friendly filename if possible
        if result_path and original_filenames:
            original_name = original_filenames[0]  # first uploaded file name
            base_name = os.path.splitext(original_name)[0]

            if operation == 'merge':
                user_filename = f"{base_name}_merged.pdf"
            elif operation == 'split':
                if result_path.endswith('.zip'):
                    user_filename = f"{base_name}_split.zip"
                else:
                    user_filename = f"{base_name}_split.pdf"
            elif operation == 'compress':
                user_filename = f"{base_name}_compressed.pdf"
            elif operation == 'extract':
                user_filename = f"{base_name}_extracted.pdf"
            elif operation == 'rotate':
                user_filename = f"{base_name}_rotated.pdf"
            elif operation == 'delete':
                user_filename = f"{base_name}_pages_deleted.pdf"
            elif operation == 'pdf_to_jpeg':
                user_filename = f"{base_name}_images.zip"
            elif operation == 'jpeg_to_pdf':
                user_filename = "images_to_pdf.pdf"
            elif operation == 'pdf_to_word':
                user_filename = f"{base_name}.docx"
            elif operation == 'word_to_pdf':
                user_filename = f"{base_name}.pdf"
            else:
                user_filename = original_name

            # Store the mapping in session
            session['download_mapping'] = {
                'system_filename': os.path.basename(result_path),
                'user_filename': user_filename
            }

        # Validate result
        if not result_path:
            return jsonify({'success': False, 'error': 'ಫೈಲ್ ಪ್ರಕ್ರಿಯೆ ವಿಫಲವಾಗಿದೆ - ಯಾವುದೇ ಫಲಿತಾಂಶ ಇಲ್ಲ'})
        
        if not os.path.exists(result_path):
            return jsonify({'success': False, 'error': f'ಫಲಿತಾಂಶ ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ: {result_path}'})
        
        result_size = os.path.getsize(result_path)
        if result_size == 0:
            return jsonify({'success': False, 'error': 'ಖಾಲಿ ಫೈಲ್ ರಚಿಸಲಾಗಿದೆ'})
        
        filename = os.path.basename(result_path)
        print(f"Success! Result file: {filename}, Size: {result_size} bytes")
        
        # Store result in session for potential chaining
        session['processed_files'] = [{
            'path': result_path,
            'filename': filename,
            'operation': operation
        }]
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'ಕಾರ್ಯಾಚರಣೆ ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಂಡಿದೆ!',
            'download_url': f'/download/{session_id}/{filename}',
            'filename': filename,
            'can_chain': True  # Enable chaining capability
        })

    except Exception as e:
        print(f"Upload error: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'ದೋಷ: {str(e)}'})

@app.route('/process', methods=['POST'])
def process_files():
    """Alternative endpoint for processing files (matches main.js expectations)"""
    return upload_file()

@app.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        print(f"Download request - Session: {session_id}, File: {filename}")
        print(f"Looking for file at: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")

        if os.path.exists(file_path):
            # Get the user-friendly filename from session
            download_mapping = session.get('download_mapping', {})
            user_filename = download_mapping.get('user_filename', filename)
            
            print(f"System filename: {filename}")
            print(f"User filename: {user_filename}")
            
            # Serve HTML in-browser
            if filename.endswith('.html'):
                return send_file(file_path)
            else:
                # Use the user-friendly filename for download
                return send_file(file_path, as_attachment=True, download_name=user_filename)

        print("File not found")
        return "ಫೈಲ್ ಕಂಡುಬಂದಿಲ್ಲ", 404

    except Exception as e:
        print(f"Download error: {str(e)}")
        return f"ದೋಷ: {str(e)}", 500
    
@app.route('/reset', methods=['POST'])
def reset_session():
    """Reset session and clear processed files - Enhanced version from file 2"""
    # Completely clear session and cleanup files
    old_session_id = session.get('session_id')
    
    # Clear all session data
    session.clear()
    
    # Generate new session ID
    session['session_id'] = str(uuid.uuid4())
    session['processed_files'] = []
    session.modified = True
    
    # Clean up old session files if they exist
    if old_session_id:
        cleanup_session_files(old_session_id)
    
    return jsonify({'success': True, 'message': 'ಅಧಿವೇಶನ ಮರುಹೊಂದಿಸಲಾಗಿದೆ'})

def cleanup_session_files(session_id):
    """Clean up all files associated with a session - From file 2"""
    try:
        # Clean up preview files
        preview_dir = os.path.join(app.config['PREVIEW_FOLDER'], session_id)
        if os.path.exists(preview_dir):
            import shutil
            shutil.rmtree(preview_dir)
            print(f"Cleaned up preview directory: {preview_dir}")
        
        # Clean up uploaded files
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith(session_id):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    os.remove(file_path)
                    print(f"Cleaned up upload file: {file_path}")
                except Exception as e:
                    print(f"Could not remove upload file {file_path}: {e}")
        
        # Clean up output files for this session
        for filename in os.listdir(app.config['OUTPUT_FOLDER']):
            if filename.startswith(session_id):
                file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                try:
                    os.remove(file_path)
                    print(f"Cleaned up output file: {file_path}")
                except Exception as e:
                    print(f"Could not remove output file {file_path}: {e}")
        
    except Exception as e:
        print(f"Session cleanup error: {e}")

@app.route('/cleanup-session', methods=['POST'])
def cleanup_session():
    """Clean up session files and previews"""
    if 'session_id' not in session:
        return jsonify({'success': True})
    
    session_id = session['session_id']
    cleanup_session_files(session_id)
    
    return jsonify({'success': True})

@app.route('/compare', methods=['POST'])
def compare_pdfs():
    try:
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({'error': 'ಎರಡು ಫೈಲ್‌ಗಳು ಅಗತ್ಯ'}), 400
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1.filename == '' or file2.filename == '':
            return jsonify({'error': 'ಫೈಲ್‌ಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಿ'}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Save uploaded files with identifiable names
        file1_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_file1_{file1.filename}")
        file2_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_file2_{file2.filename}")
        
        file1.save(file1_path)
        file2.save(file2_path)
        
        # Generate preview images for both PDFs
        preview_folder = app.config['PREVIEW_FOLDER']
        pdf_ops.generate_page_previews(file1_path, session_id, preview_folder)
        pdf_ops.generate_page_previews(file2_path, session_id, preview_folder)
        
        # Compare PDFs
        comparison_data = pdf_compare.compare_pdfs_web(
            file1_path, file2_path, session_id, 'both'
        )
        
        if not comparison_data:
            return jsonify({'error': 'ಹೋಲಿಕೆ ವಿಫಲವಾಗಿದೆ'}), 500
        
        # Store session data
        session['comparison_data'] = comparison_data
        session['session_id'] = session_id
        
        # Redirect to the result page instead of rendering directly
        return redirect(url_for('compare_result'))
        
    except Exception as e:
        print(f"Compare error: {e}")
        return jsonify({'error': f'ದೋಷ: {str(e)}'}), 500

@app.route('/compare-result')
def compare_result():
    try:
        if 'session_id' not in session:
            return redirect(url_for('index'))
        
        session_id = session['session_id']
        
        # Load comparison data from file instead of session
        comparison_file = os.path.join(app.config['OUTPUT_FOLDER'], f'{session_id}_comparison.json')
        
        if not os.path.exists(comparison_file):
            return redirect(url_for('index'))
        
        with open(comparison_file, 'r', encoding='utf-8') as f:
            comparison_data = json.load(f)
        
        # Ensure UTF-8 encoding
        def ensure_utf8(obj):
            if isinstance(obj, dict):
                return {k: ensure_utf8(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [ensure_utf8(item) for item in obj]
            elif isinstance(obj, str):
                return unicodedata.normalize('NFC', obj)
            else:
                return obj
        
        comparison_data = ensure_utf8(comparison_data)
        
        response = make_response(render_template('compare_result.html', 
                                               comparison_data=comparison_data))
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
        
    except Exception as e:
        print(f"Compare result error: {e}")
        return redirect(url_for('index'))

def generate_page_image(pdf_path, session_id, file_num, page_num):
    """Generate page image from PDF"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]  # PDF pages are 0-indexed
        
        # Generate high-quality image
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
        
        # Save image
        output_dir = f"static/temp/{session_id}"
        os.makedirs(output_dir, exist_ok=True)
        image_path = os.path.join(output_dir, f"page_{page_num}_{file_num}.png")
        
        pix.save(image_path)
        doc.close()
        
        return image_path
    except Exception as e:
        print(f"Image generation error: {e}")
        return None 

@app.route('/pdf-page/<session_id>/<file_num>/<int:page_num>')
def serve_pdf_page(session_id, file_num, page_num):
    try:
        import glob
        
        # Find the uploaded PDF file
        if file_num == 'file1':
            file_pattern = f"{session_id}_file1_*"
        else:  # file2
            file_pattern = f"{session_id}_file2_*"
        
        matching_files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], file_pattern))
        
        if not matching_files:
            return "PDF file not found", 404
            
        pdf_path = matching_files[0]
        
        # Generate or get existing page image
        image_path = generate_page_image(pdf_path, session_id, file_num, page_num)
        
        if image_path and os.path.exists(image_path):
            return send_file(image_path)
        else:
            return "Page image not found", 404
            
    except Exception as e:
        print(f"Error serving page: {e}")
        return "Error", 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'success': False, 'error': 'ಫೈಲ್ ತುಂಬಾ ದೊಡ್ಡದಾಗಿದೆ. ಗರಿಷ್ಠ 1000MB ಅನುಮತಿ'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'ವಿನಂತಿಸಿದ ಸಂಪನ್ಮೂಲ ಸಿಗಲಿಲ್ಲ'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'ಸರ್ವರ್ ದೋಷ ಸಂಭವಿಸಿದೆ'}), 500

# Enhanced cleanup function from file 2
def cleanup_old_files():
    """Clean up old files on server startup"""
    import time
    current_time = time.time()
    
    # Clean up files older than 1 hour (from file 2)
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['PREVIEW_FOLDER']]:
        if not os.path.exists(folder):
            continue
            
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.getctime(file_path) < current_time - 3600:  # 1 hour
                        os.remove(file_path)
                        print(f"Cleaned up old file: {file_path}")
                except Exception as e:
                    print(f"Could not clean up {file_path}: {e}")
                    continue
            
            # Remove empty directories
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        print(f"Removed empty directory: {dir_path}")
                except Exception as e:
                    print(f"Could not remove directory {dir_path}: {e}")
                    continue

if __name__ == '__main__':
    cleanup_old_files()
    app.run(debug=True)