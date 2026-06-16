# Kannada PDF Toolkit 📄

A powerful, all-in-one web application for manipulating, converting, and editing PDF files, designed with a complete **Kannada** language interface. Built with Python and Flask, this toolkit focuses on providing an accessible, robust, and highly visual experience for users processing document files.

## 🌟 Key Features

The toolkit supports a massive array of PDF operations:
1. **Merge** - Combine multiple PDFs into a single document.
2. **Split** - Divide a large PDF into smaller, manageable chunks.
3. **Extract** - Pull specific pages out of a PDF document.
4. **Delete** - Remove unwanted pages from a document.
5. **Rotate** - Rotate specific pages or entire documents.
6. **Crop** - Trim page margins and crop content areas.
7. **Compress** - Reduce PDF file size with multiple quality options.
8. **PDF to Image** - Convert PDF pages into high-quality images.
9. **Word to PDF** - Convert `.docx` files to PDF format.
10. **PDF to Word** - Extract text (and run OCR on images) to create `.docx` files.

---

## 👁️ Interactive Preview System

A comprehensive preview system has been implemented for nearly all PDF operations. This allows users to visually inspect what will happen to their PDF files **before** actually processing them, preventing mistakes and saving time.

### Preview Capabilities:
- **Visual Thumbnails**: See before/after thumbnails for Rotations, Deletions, and Extractions.
- **Merge/Split Estimates**: View all input files and see exactly how pages will be divided or combined.
- **Compression Previews**: Get estimated output sizes and quality samples before compressing.
- **Fast Rendering**: Thumbnails are generated at a 0.3x scale to ensure the preview screen loads almost instantly.
- **Secure Sessions**: All preview generation is completely isolated using unique Session IDs.

**How to Use the Preview:**
1. Select an operation and upload your PDF.
2. Set your specific parameters (e.g., pages to extract, rotation angle).
3. Click **"ಪೂರ್ವವೀಕ್ಷಣೆ ರಚಿಸಿ" (Generate Preview)** to see the simulated result.
4. Once satisfied, click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ" (Start Process)** to execute the actual operation!

---

## 🛠️ Technology Stack

- **Backend:** Python 3, Flask, Werkzeug
- **PDF Manipulation:** PyMuPDF (`fitz`), PyPDF2, pdfplumber
- **Image Processing:** Pillow (`PIL`), OpenCV (`cv2`)
- **Document Conversion:** `python-docx`, ReportLab, WeasyPrint
- **OCR (Optical Character Recognition):** Tesseract OCR (`pytesseract`)
- **Deployment Ready:** `gunicorn`, `python-dotenv`

---

## 🚀 How to Run Locally

Follow these steps to run the Kannada PDF Toolkit on your own machine:

### 1. Clone the repository
```bash
git clone https://github.com/shreyaaaa06/kannada-pdftoolkit.git
cd kannada-pdftoolkit
```

### 2. Set up a Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Note: If you plan on using the OCR features, you must have [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed on your system).*

### 4. Start the Application
To avoid Unicode encoding issues on Windows, it is recommended to set the encoding flag:
```bash
# On Windows PowerShell:
$env:PYTHONIOENCODING="utf-8"; python app.py

# On macOS/Linux:
PYTHONIOENCODING=utf-8 python app.py
```
The server will start running on `http://127.0.0.1:5000`.

---

## 🌐 Deployment

This application is ready to be deployed to modern cloud platforms like Render, Heroku, or AWS Elastic Beanstalk. 

**For Render Deployment:**
1. Create a New Web Service connected to this GitHub repository.
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `gunicorn app:app`
4. Deploy! All temporary folders and cache systems are automatically managed.

---

## 📁 File Structure Overview

- `app.py`: The main Flask application containing routing and session logic.
- `utils/`: Contains all specialized operational logic (`pdf_operations.py`, `pdf_compare.py`, etc.)
- `templates/`: HTML templates for the frontend interface.
- `static/`: Contains the CSS, JS, Fonts, and temporary workspace directories.
- `output/`: Directory where processed files are temporarily staged before download.
