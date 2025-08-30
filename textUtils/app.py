#!/usr/bin/env python3
"""
Flask Web Application for PDF Text Extraction and OCR
Provides a web interface for uploading PDFs/images and extracting text with editing capabilities.
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import tempfile
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import re

# Import our extraction modules
try:
    from pdf_text_extractor import extract_text_from_pdf, check_dependencies as check_pdf_deps
    PDF_AVAILABLE = True
    print("✅ PDF processing available")
except ImportError as e:
    PDF_AVAILABLE = False
    print(f"❌ PDF processing not available: {e}")

try:
    import pytesseract
    from PIL import Image, ImageEnhance
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
    OPENCV_AVAILABLE = True
    print("✅ OCR processing available")
    print("✅ OpenCV available")
except ImportError as e:
    OCR_AVAILABLE = False
    OPENCV_AVAILABLE = False
    print(f"❌ OCR/OpenCV processing not available: {e}")

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Transliteration features removed from server-side. If needed, re-add an
# explicit transliteration service or integrate a third-party API.


def preprocess_image_opencv(image_path, output_dir=None):
    """
    Advanced image preprocessing using OpenCV for better OCR results.

    Args:
        image_path (str): Path to input image
        output_dir (str): Directory to save processed images (optional)

    Returns:
        list: List of processed ROI image paths
    """
    if not OPENCV_AVAILABLE:
        return []

    try:
        print(f"🔧 Starting OpenCV preprocessing for: {image_path}")

        # Read image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Could not read image: {image_path}")
            return []

        print(f"📊 Original image shape: {image.shape}")

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print("✅ Converted to grayscale")

        # Apply Gaussian blur
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        print("✅ Applied Gaussian blur")

        # Apply threshold with OTSU
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        print("✅ Applied OTSU thresholding")

        # Create morphological kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 13))

        # Apply dilation
        dilate = cv2.dilate(thresh, kernel, iterations=1)
        print("✅ Applied morphological operations")

        # Find contours
        cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        # Sort contours by x-coordinate (left to right)
        cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[0])
        print(f"🔍 Found {len(cnts)} contours")

        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = os.path.join(os.path.dirname(image_path), 'temp')
            os.makedirs(output_dir, exist_ok=True)

        roi_paths = []
        valid_contours = 0

        # Process each contour
        for i, c in enumerate(cnts):
            x, y, w, h = cv2.boundingRect(c)

            # Filter contours based on size (height > 200 and width > 20)
            if h > 200 and w > 20:
                valid_contours += 1

                # Extract ROI (Region of Interest)
                roi = image[y:y+h, x:x+w]  # Fixed: was x:x+h, should be x:x+w

                # Save ROI
                roi_filename = f"roi_{i}_{valid_contours}.png"
                roi_path = os.path.join(output_dir, roi_filename)
                cv2.imwrite(roi_path, roi)
                roi_paths.append(roi_path)

                # Draw bounding rectangle on original image
                cv2.rectangle(image, (x, y), (x+w, y+h), (36, 255, 12), 2)

                print(f"✅ Extracted ROI {valid_contours}: {w}x{h} at ({x},{y})")

        # Save image with bounding boxes
        bbox_filename = f"bbox_{os.path.basename(image_path)}"
        bbox_path = os.path.join(output_dir, bbox_filename)
        cv2.imwrite(bbox_path, image)

        print(f"🎯 Found {valid_contours} valid text regions")
        print(f"💾 Saved bounding box image: {bbox_path}")
        print(f"💾 Saved {len(roi_paths)} ROI images")

        return roi_paths

    except Exception as e:
        print(f"❌ Error in OpenCV preprocessing: {str(e)}")
        return []


def extract_text_from_image(image_path, preprocess=True, use_opencv=True):
    """Extract text from image using OCR with optional OpenCV preprocessing."""
    if not OCR_AVAILABLE:
        return "OCR libraries not available. Please install pytesseract and pillow."

    try:
        print(f"📂 Opening image: {image_path}")

        # Check if Kannada language is available, fallback to English
        try:
            available_langs = pytesseract.get_languages()
            lang = 'kan' if 'kan' in available_langs else 'eng'
            print(f"🌐 Using OCR language: {lang}")
        except:
            lang = 'eng'
            print("🌐 Using default language: eng")

        extracted_text = ""

        # Use OpenCV preprocessing if available and requested
        if use_opencv and OPENCV_AVAILABLE and preprocess:
            print("🔧 Using OpenCV preprocessing...")

            # Get ROI images using OpenCV preprocessing
            roi_paths = preprocess_image_opencv(image_path)

            if roi_paths:
                print(f"📝 Processing {len(roi_paths)} ROI regions...")

                # Extract text from each ROI
                for i, roi_path in enumerate(roi_paths):
                    print(f"🔍 Processing ROI {i+1}/{len(roi_paths)}: {roi_path}")

                    try:
                        # Load ROI image with PIL for OCR
                        roi_image = Image.open(roi_path)

                        # OCR configuration for better results
                        custom_config = r'--oem 3 --psm 6'
                        roi_text = pytesseract.image_to_string(
                            roi_image,
                            lang=lang,
                            config=custom_config
                        )

                        if roi_text.strip():
                            extracted_text += f"\n--- Region {i+1} ---\n"
                            extracted_text += roi_text.strip() + "\n"
                            print(f"✅ Extracted {len(roi_text)} characters from ROI {i+1}")
                        else:
                            print(f"⚠️ No text found in ROI {i+1}")

                    except Exception as e:
                        print(f"❌ Error processing ROI {i+1}: {str(e)}")
                        continue

                # Clean up ROI files
                for roi_path in roi_paths:
                    try:
                        os.remove(roi_path)
                    except:
                        pass

            else:
                print("⚠️ No valid ROI regions found, falling back to standard OCR")
                use_opencv = False

        # Fallback to standard PIL preprocessing if OpenCV not used or failed
        if not use_opencv or not OPENCV_AVAILABLE or not extracted_text.strip():
            print("🔧 Using standard PIL preprocessing...")

            image = Image.open(image_path)
            print(f"📊 Image size: {image.size}, mode: {image.mode}")

            if preprocess:
                # Convert to grayscale and enhance contrast
                image = image.convert('L')
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(2.0)
                print("✅ Applied PIL preprocessing")

            # Extract text using OCR
            custom_config = r'--oem 3 --psm 6'
            standard_text = pytesseract.image_to_string(
                image,
                lang=lang,
                config=custom_config
            )

            # Use standard text if OpenCV didn't produce results
            if not extracted_text.strip():
                extracted_text = standard_text
            else:
                # Append standard OCR results
                if standard_text.strip():
                    extracted_text += f"\n--- Full Image OCR ---\n"
                    extracted_text += standard_text.strip()

        print(f"🎯 OCR completed, total text length: {len(extracted_text)}")
        return extracted_text

    except Exception as e:
        error_msg = f"Error processing image: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg


def save_extracted_text(text, original_filename, output_dir=OUTPUT_FOLDER):
    """Save extracted text to a file."""
    base_name = os.path.splitext(original_filename)[0]
    output_filename = f"{base_name}_extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Extracted Text from: {original_filename}\n")
            f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Character Count: {len(text)}\n")
            f.write(f"Word Count: {len(text.split())}\n")
            f.write("=" * 50 + "\n\n")
            f.write(text)
        
        return output_path
    except Exception as e:
        return None


@app.route('/')
def index():
    """Main page with upload form."""
    print("Index route called")  # Debug log
    return render_template('index.html',
                         pdf_available=PDF_AVAILABLE,
                         ocr_available=OCR_AVAILABLE)


@app.route('/test')
def test():
    """Simple test route."""
    return f"""
    <h1>Flask App Test</h1>
    <p>PDF Available: {PDF_AVAILABLE}</p>
    <p>OCR Available: {OCR_AVAILABLE}</p>
    <p>Upload folder exists: {os.path.exists(UPLOAD_FOLDER)}</p>
    <p>Output folder exists: {os.path.exists(OUTPUT_FOLDER)}</p>
    <a href="/">Back to main page</a>
    """


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handle file upload and text extraction."""
    print(f"Upload route called with method: {request.method}")  # Debug log

    if request.method == 'GET':
        print("GET request to upload, redirecting to index")  # Debug log
        return redirect(url_for('index'))

    print(f"POST request received. Files in request: {list(request.files.keys())}")  # Debug log
    print(f"Form data: {dict(request.form)}")  # Debug log

    if 'file' not in request.files:
        print("No 'file' key in request.files")  # Debug log
        flash('No file selected')
        return redirect(url_for('index'))

    file = request.files['file']
    print(f"File object: {file}, filename: {file.filename}")  # Debug log

    if file.filename == '':
        print("Empty filename")  # Debug log
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        print(f"File is valid and allowed: {file.filename}")  # Debug log

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        print(f"Saving file to: {filepath}")  # Debug log

        try:
            file.save(filepath)
            print(f"File saved successfully: {filepath}")  # Debug log
        except Exception as e:
            print(f"Error saving file: {e}")  # Debug log
            flash(f'Error saving file: {str(e)}')
            return redirect(url_for('index'))
        
        # Extract text based on file type
        file_ext = filename.rsplit('.', 1)[1].lower()

        try:
            print(f"Processing file: {filename}, extension: {file_ext}")  # Debug log

            if file_ext == 'pdf':
                if not PDF_AVAILABLE:
                    flash('PDF processing not available. Please install required dependencies.')
                    return redirect(url_for('index'))

                method = request.form.get('method', 'auto')
                print(f"Using PDF method: {method}")  # Debug log
                extracted_text = extract_text_from_pdf(filepath, method=method)
            else:
                if not OCR_AVAILABLE:
                    flash('OCR processing not available. Please install required dependencies.')
                    return redirect(url_for('index'))

                preprocess = request.form.get('preprocess', 'true') == 'true'
                use_opencv = request.form.get('use_opencv', 'true') == 'true'
                print(f"Using OCR with preprocessing: {preprocess}, OpenCV: {use_opencv}")  # Debug log
                extracted_text = extract_text_from_image(filepath, preprocess=preprocess, use_opencv=use_opencv)

            print(f"Extracted text length: {len(extracted_text) if extracted_text else 0}")  # Debug log

            # Check if extraction was successful
            if not extracted_text or extracted_text.startswith("❌") or extracted_text.startswith("Error"):
                flash(f'Text extraction failed: {extracted_text}')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(url_for('index'))

            # Save extracted text
            output_path = save_extracted_text(extracted_text, file.filename)

            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)

            print(f"Rendering result page with {len(extracted_text)} characters")  # Debug log

            return render_template('result.html',
                                 text=extracted_text,
                                 filename=file.filename,
                                 output_file=os.path.basename(output_path) if output_path else None,
                                 char_count=len(extracted_text),
                                 word_count=len(extracted_text.split()),
                                 line_count=len(extracted_text.splitlines()))
        
        except Exception as e:
            print(f"Exception during processing: {e}")  # Debug log
            flash(f'Error processing file: {str(e)}')
            if os.path.exists(filepath):
                os.remove(filepath)
            return redirect(url_for('index'))

    else:
        print(f"File not allowed or invalid: {file.filename if file else 'No file'}")  # Debug log
        flash('Invalid file type. Please upload PDF, PNG, JPG, JPEG, GIF, BMP, or TIFF files.')
        return redirect(url_for('index'))


@app.route('/save_edited', methods=['POST'])
def save_edited():
    """Save edited text from Quill editor."""
    try:
        data = request.get_json()
        edited_text = data.get('text', '')
        original_filename = data.get('filename', 'edited_text')
        
        # Save the edited text
        output_path = save_extracted_text(edited_text, f"edited_{original_filename}")
        
        if output_path:
            return jsonify({
                'success': True, 
                'message': 'Text saved successfully!',
                'filename': os.path.basename(output_path)
            })
        else:
            return jsonify({'success': False, 'message': 'Error saving file'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@app.route('/download/<filename>')
def download_file(filename):
    """Download saved text file."""
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('File not found')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error downloading file: {str(e)}')
        return redirect(url_for('index'))


@app.route('/api/check_dependencies')
def check_dependencies():
    """API endpoint to check available dependencies."""
    deps = {
        'pdf_available': PDF_AVAILABLE,
        'ocr_available': OCR_AVAILABLE,
        'opencv_available': OPENCV_AVAILABLE
    }
    
    if PDF_AVAILABLE:
        try:
            pdf_deps = check_pdf_deps()
            deps['pdf_details'] = 'All PDF dependencies available'
        except:
            deps['pdf_details'] = 'Some PDF dependencies missing'
    
    if OCR_AVAILABLE:
        try:
            languages = pytesseract.get_languages()
            deps['ocr_languages'] = languages
            deps['kannada_available'] = 'kan' in languages
        except:
            deps['ocr_languages'] = []
            deps['kannada_available'] = False
    
    return jsonify(deps)


# Transliteration features removed from server-side. If needed, re-add an
# explicit transliteration service or integrate a third-party API.


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File is too large. Maximum size is 16MB.')
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("🚀 Starting PDF/OCR Text Extraction Web App")
    print("=" * 50)
    print(f"PDF Support: {'✅' if PDF_AVAILABLE else '❌'}")
    print(f"OCR Support: {'✅' if OCR_AVAILABLE else '❌'}")
    print(f"OpenCV Support: {'✅' if OPENCV_AVAILABLE else '❌'}")
    print("=" * 50)
    print("📝 Install missing dependencies:")
    if not PDF_AVAILABLE:
        print("   pip install PyPDF2 pdfplumber pdf2image")
    if not OCR_AVAILABLE:
        print("   pip install pytesseract pillow")
    print("=" * 40)
    
    app.run(debug=True, host='0.0.0.0', port=8000)
