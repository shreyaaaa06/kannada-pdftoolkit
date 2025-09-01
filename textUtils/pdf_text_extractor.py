#!/usr/bin/env python3
"""
PDF Text Extractor Script
This script extracts text from PDF files and saves them to txt files.
Supports both text-based PDFs and image-based PDFs (using OCR).
"""

import os
import sys
import argparse
from datetime import datetime

# PDF text extraction libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

# OCR libraries for image-based PDFs
try:
    import pytesseract
    from PIL import Image
    import pdf2image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Word document library
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    missing_deps = []
    
    if not PYPDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE:
        missing_deps.append("PyPDF2 or pdfplumber")
    
    if PYPDF2_AVAILABLE:
        print("✅ PyPDF2 is available")
    elif PDFPLUMBER_AVAILABLE:
        print("✅ pdfplumber is available")
    
    if OCR_AVAILABLE:
        print("✅ OCR libraries (pytesseract, PIL, pdf2image) are available")
    else:
        print("⚠️  OCR libraries not available (for image-based PDFs)")
        missing_deps.append("pytesseract, pillow, pdf2image (for OCR)")
    
    if DOCX_AVAILABLE:
        print("✅ python-docx is available")
    else:
        print("⚠️  python-docx not available (for DOCX output)")
        missing_deps.append("python-docx (for DOCX output)")
    
    if missing_deps:
        print("\n❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstall with:")
        print("pip install PyPDF2 pdfplumber pytesseract pillow pdf2image python-docx")
        return False
    
    return True


def extract_text_pypdf2(pdf_path):
    """
    Extract text from PDF using PyPDF2.
    
    Args:
        pdf_path (str): Path to PDF file
    
    Returns:
        str: Extracted text
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            print(f"📄 PDF has {len(pdf_reader.pages)} pages")
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                print(f"📖 Processing page {page_num}...")
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += f"\n--- Page {page_num} ---\n"
                    text += page_text + "\n"
            
            return text
    except Exception as e:
        return f"❌ Error extracting text with PyPDF2: {str(e)}"


def extract_text_pdfplumber(pdf_path):
    """
    Extract text from PDF using pdfplumber (better for complex layouts).
    
    Args:
        pdf_path (str): Path to PDF file
    
    Returns:
        str: Extracted text
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            
            print(f"📄 PDF has {len(pdf.pages)} pages")
            
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"📖 Processing page {page_num}...")
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += f"\n--- Page {page_num} ---\n"
                    text += page_text + "\n"
            
            return text
    except Exception as e:
        return f"❌ Error extracting text with pdfplumber: {str(e)}"


def extract_text_ocr(pdf_path, language='kan'):
    """
    Extract text from PDF using OCR (for image-based PDFs).
    
    Args:
        pdf_path (str): Path to PDF file
        language (str): OCR language code
    
    Returns:
        str: Extracted text
    """
    if not OCR_AVAILABLE:
        return "❌ OCR libraries not available. Install pytesseract, pillow, and pdf2image."
    
    try:
        # Convert PDF pages to images
        print("🔄 Converting PDF pages to images...")
        images = pdf2image.convert_from_path(pdf_path)
        
        text = ""
        print(f"📄 PDF converted to {len(images)} image(s)")
        
        for page_num, image in enumerate(images, 1):
            print(f"🔍 OCR processing page {page_num}...")
            
            # Extract text using OCR
            page_text = pytesseract.image_to_string(image, lang=language)
            
            if page_text.strip():
                text += f"\n--- Page {page_num} (OCR) ---\n"
                text += page_text + "\n"
        
        return text
    except Exception as e:
        return f"❌ Error extracting text with OCR: {str(e)}"


def extract_text_from_pdf(pdf_path, method='auto', ocr_language='kan'):
    """
    Extract text from PDF using specified method.
    
    Args:
        pdf_path (str): Path to PDF file
        method (str): Extraction method ('auto', 'pypdf2', 'pdfplumber', 'ocr')
        ocr_language (str): Language for OCR
    
    Returns:
        str: Extracted text
    """
    if not os.path.exists(pdf_path):
        return f"❌ PDF file '{pdf_path}' not found."
    
    print(f"📂 Processing PDF: {pdf_path}")
    
    if method == 'pypdf2' and PYPDF2_AVAILABLE:
        return extract_text_pypdf2(pdf_path)
    elif method == 'pdfplumber' and PDFPLUMBER_AVAILABLE:
        return extract_text_pdfplumber(pdf_path)
    elif method == 'ocr':
        return extract_text_ocr(pdf_path, ocr_language)
    elif method == 'auto':
        # Try pdfplumber first, then PyPDF2, then OCR
        if PDFPLUMBER_AVAILABLE:
            print("🔄 Trying pdfplumber extraction...")
            text = extract_text_pdfplumber(pdf_path)
            if text and not text.startswith("❌") and text.strip():
                return text
        
        if PYPDF2_AVAILABLE:
            print("🔄 Trying PyPDF2 extraction...")
            text = extract_text_pypdf2(pdf_path)
            if text and not text.startswith("❌") and text.strip():
                return text
        
        if OCR_AVAILABLE:
            print("🔄 Trying OCR extraction...")
            return extract_text_ocr(pdf_path, ocr_language)
        
        return "❌ No suitable extraction method available."
    else:
        return f"❌ Method '{method}' not available or not supported."


def save_text_to_file(text, pdf_path, output_dir=None):
    """
    Save extracted text to a .txt file.
    
    Args:
        text (str): Extracted text to save
        pdf_path (str): Path to the original PDF
        output_dir (str): Directory to save the text file (optional)
    
    Returns:
        str: Path to the saved text file
    """
    # Generate output filename based on PDF name
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = f"{pdf_name}_extracted_text.txt"
    
    # Determine output directory
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
    else:
        # Save in the same directory as the PDF
        pdf_dir = os.path.dirname(pdf_path) or '.'
        output_path = os.path.join(pdf_dir, output_filename)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header with metadata
            f.write(f"Extracted Text from: {os.path.basename(pdf_path)}\n")
            f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Character Count: {len(text)}\n")
            f.write(f"Word Count: {len(text.split())}\n")
            f.write(f"Line Count: {len(text.splitlines())}\n")
            f.write("=" * 50 + "\n\n")
            
            # Write the extracted text
            f.write(text)
        
        return output_path
    except Exception as e:
        print(f"❌ Error saving text file: {str(e)}")
        return None


def save_text_to_docx(text, output_path):
    """Save extracted text to a DOCX file."""
    if not DOCX_AVAILABLE:
        raise RuntimeError("python-docx is not available. Install with 'pip install python-docx'")
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    doc = Document()
    # Split by lines to preserve basic structure
    for line in text.splitlines():
        doc.add_paragraph(line)
    doc.save(output_path)
    return output_path


def convert_pdf_to_docx(pdf_path, session_id, output_dir=None, method='ocr', ocr_language='kan'):
    """
    Convert a PDF to a DOCX by extracting text (auto/ocr) and writing to a Word document.
    Returns the path to the generated .docx file.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Extract text using the chosen method
    extracted_text = extract_text_from_pdf(pdf_path, method=method, ocr_language=ocr_language)
    if not extracted_text or extracted_text.startswith("❌"):
        raise RuntimeError(f"Text extraction failed: {extracted_text}")

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_dir_final = output_dir or (os.path.dirname(pdf_path) or '.')
    output_filename = f"{session_id}_{base_name}.docx"
    output_path = os.path.join(output_dir_final, output_filename)

    # Save to DOCX
    save_text_to_docx(extracted_text, output_path)

    if not os.path.exists(output_path):
        raise RuntimeError("DOCX file was not created")

    return output_path


def display_results(text, pdf_path, save_output=False, output_dir=None):
    """
    Display the extraction results and optionally save to file.
    
    Args:
        text (str): Extracted text
        pdf_path (str): Path to the processed PDF
        save_output (bool): Whether to save text to file
        output_dir (str): Directory to save the text file
    """
    print("\n" + "="*60)
    print(f"📋 EXTRACTION RESULTS FOR: {os.path.basename(pdf_path)}")
    print("="*60)
    
    if text.strip() and not text.startswith("❌"):
        print("📝 Extracted Text Preview (first 500 characters):")
        print("-" * 40)
        preview = text[:500] + "..." if len(text) > 500 else text
        print(preview)
        print("-" * 40)
        print(f"📊 Character count: {len(text)}")
        print(f"📊 Word count: {len(text.split())}")
        print(f"📊 Line count: {len(text.splitlines())}")
        
        # Save to file if requested
        if save_output:
            output_path = save_text_to_file(text, pdf_path, output_dir)
            if output_path:
                print(f"💾 Text saved to: {output_path}")
    else:
        print("⚠️  No text was extracted from the PDF or an error occurred.")
        print("💡 Tips:")
        print("   - Try using --method ocr for image-based PDFs")
        print("   - Ensure the PDF is not password protected")
        print("   - Check if the PDF contains actual text or just images")


def process_multiple_pdfs(folder_path, method='auto', ocr_language='kan', save_output=False, output_dir=None):
    """
    Process all PDF files in a folder.
    
    Args:
        folder_path (str): Path to folder containing PDFs
        method (str): Extraction method
        ocr_language (str): Language for OCR
        save_output (bool): Whether to save text to files
        output_dir (str): Directory to save the text files
    """
    if not os.path.exists(folder_path):
        print(f"❌ Folder '{folder_path}' not found.")
        return
    
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ No PDF files found in '{folder_path}'")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF file(s) in '{folder_path}")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n🔄 Processing PDF {i}/{len(pdf_files)}: {pdf_file}")
        pdf_path = os.path.join(folder_path, pdf_file)
        
        extracted_text = extract_text_from_pdf(pdf_path, method, ocr_language)
        display_results(extracted_text, pdf_path, save_output, output_dir)


def main():
    """Main function to handle command line arguments and execute PDF text extraction."""
    parser = argparse.ArgumentParser(
        description="Extract text from PDF files and save to txt files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_text_extractor.py document.pdf                    # Extract text from PDF
  python pdf_text_extractor.py document.pdf --save             # Extract and save to txt
  python pdf_text_extractor.py --folder ./pdfs --save          # Process folder and save
  python pdf_text_extractor.py document.pdf --method ocr       # Use OCR for image-based PDF
  python pdf_text_extractor.py document.pdf --save --output ./texts  # Save to specific directory
        """
    )
    
    parser.add_argument('path', nargs='?', help='Path to PDF file or folder')
    parser.add_argument('--folder', action='store_true',
                       help='Process all PDF files in the specified folder')
    parser.add_argument('--method', choices=['auto', 'pypdf2', 'pdfplumber', 'ocr'], 
                       default='auto', help='Text extraction method (default: auto)')
    parser.add_argument('--ocr-language', default='kan',
                       help='Language for OCR (default: kan for Kannada)')
    parser.add_argument('--save', action='store_true',
                       help='Save extracted text to .txt files')
    parser.add_argument('--output', type=str, metavar='DIR',
                       help='Directory to save text files (default: same as PDF location)')
    parser.add_argument('--check', action='store_true',
                       help='Check available dependencies')
    
    args = parser.parse_args()
    
    print("🚀 PDF Text Extractor")
    print("=" * 30)
    
    # Check dependencies if requested
    if args.check:
        check_dependencies()
        return
    
    # Check if path is provided
    if not args.path:
        print("❌ Please provide a PDF path or folder path.")
        print("Use --help for usage information.")
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Validate output directory if specified
    if args.output and not args.save:
        print("⚠️  --output can only be used with --save option")
        return
    
    print()  # Add spacing
    
    # Process folder or single PDF
    if args.folder:
        process_multiple_pdfs(args.path, args.method, args.ocr_language, args.save, args.output)
    else:
        # Process single PDF
        extracted_text = extract_text_from_pdf(args.path, args.method, args.ocr_language)
        display_results(extracted_text, args.path, args.save, args.output)
    
    print("\n✅ Processing completed!")


if __name__ == "__main__":
    main()
