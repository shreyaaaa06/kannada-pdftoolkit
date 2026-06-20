# ಕನ್ನಡ PDF ಟೂಲ್‌ಕಿಟ್ — Kannada PDF Toolkit 📄

> **ಕರ್ನಾಟಕ ಸರ್ಕಾರಿ ನೌಕರರಿಗಾಗಿ ವಿಶೇಷವಾಗಿ ವಿನ್ಯಾಸಗೊಳಿಸಲಾದ ಸಂಪೂರ್ಣ PDF ನಿರ್ವಹಣಾ ವ್ಯವಸ್ಥೆ**
>
> A comprehensive, all-in-one web application for manipulating, converting, and editing PDF files — built exclusively with a **Kannada language interface** for Karnataka Government Employees.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Technology Stack](#️-technology-stack)
4. [Project Structure](#-project-structure)
5. [System Requirements](#-system-requirements)
6. [Installation & Setup](#-installation--setup)
7. [Running the Application](#-running-the-application)
8. [User Authentication](#-user-authentication)
9. [All PDF Operations — Step-by-Step Guide](#-all-pdf-operations--step-by-step-guide)
10. [Interactive Preview System](#️-interactive-preview-system)
11. [PDF Comparison Feature](#-pdf-comparison-feature)
12. [Security & Access Control](#-security--access-control)
13. [Deployment Guide](#-deployment-guide)
14. [Configuration Reference](#️-configuration-reference)
15. [File Management & Cleanup](#-file-management--cleanup)
16. [Troubleshooting](#-troubleshooting)
17. [API Endpoints Reference](#-api-endpoints-reference)
18. [Contributing](#-contributing)

---

## 🏛 Project Overview

The **Kannada PDF Toolkit** is a Python Flask–based web application designed specifically to serve Karnataka Government employees who work with PDF documents on a daily basis. Every part of the user interface — buttons, labels, error messages, confirmations — is written in the Kannada language (ಕನ್ನಡ), making it fully accessible to native Kannada speakers without requiring knowledge of English.

The application supports a very wide range of PDF operations: from basic actions like merging and splitting to advanced tasks like OCR-powered conversion to Word, password protection, page-level comparison, and more — all through a clean, browser-based interface without requiring any desktop software.

**Designed for:**
- Karnataka State Government Departments
- District and Taluk-level offices
- Revenue, Education, Health, and other Government departments
- Any government employee who handles Kannada-language PDF documents

---

## 🌟 Key Features

The toolkit provides 15 distinct PDF operations, a visual preview system, secure login, PDF comparison, and Kannada font support — all in one place.

### PDF Operations

| # | Operation | Kannada Name | Description |
|---|-----------|--------------|-------------|
| 1 | **Merge** | ವಿಲೀನ | Combine 2 or more PDF files into one |
| 2 | **Split** | ವಿಭಾಗ | Divide a PDF into multiple smaller files |
| 3 | **Extract** | ಹೊರತೆಗೆಯುವಿಕೆ | Pull specific pages out of a PDF |
| 4 | **Delete Pages** | ಅಳಿಸುವಿಕೆ | Remove unwanted pages from a PDF |
| 5 | **Rotate** | ತಿರುಗಿಸುವಿಕೆ | Rotate individual or all pages |
| 6 | **Crop** | ಕತ್ತರಿಸುವಿಕೆ | Trim/crop margins and page content areas |
| 7 | **Compress** | ಸಂಕುಚನ | Reduce file size with quality control |
| 8 | **PDF to Image** | PDF ರಿಂದ JPEG | Convert PDF pages to high-quality images |
| 9 | **Image to PDF** | JPEG ರಿಂದ PDF | Convert images/photos to a PDF document |
| 10 | **Word to PDF** | Word ರಿಂದ PDF | Convert `.docx` / `.doc` files to PDF |
| 11 | **PDF to Word** | PDF ರಿಂದ Word | Extract text (with OCR) from PDF to `.docx` |
| 12 | **Compare PDFs** | ಹೋಲಿಕೆ | Side-by-side visual comparison of two PDFs |
| 13 | **Sort Pages** | ಸಾರಿಸು | Re-order PDF pages by page number |
| 14 | **Protect PDF** | ರಕ್ಷಿಸು | Add password protection with permissions |
| 15 | **Unlock PDF** | ಅನ್‌ಲಾಕ್ | Remove password from a protected PDF |

### Additional Highlights

- **Kannada Language Interface** — entire UI is in Kannada; error messages, labels, and buttons all use Kannada text
- **Visual Preview System** — see thumbnails of pages before executing any operation
- **Secure Session-Based Login** — each user gets an 8-hour authenticated session
- **Government Employee Profiles** — stores Employee ID, Department, and Designation
- **Large File Support** — accepts files up to 1000 MB (1 GB)
- **Operation Chaining** — the output of one operation can immediately be used as input for the next
- **Auto Cleanup** — uploaded and temporary files are automatically deleted after 1 hour
- **Kannada Font Support** — bundles Noto Sans Kannada, Tunga, Baloo Tamma, and other Kannada fonts for PDF rendering
- **Unicode-Safe** — fully handles Kannada filenames and text without encoding errors
- **Cloud-Ready** — can be deployed on Render, Heroku, or any cloud platform

---

## 🛠️ Technology Stack

### Backend
| Component | Technology | Version |
|-----------|------------|---------|
| Web Framework | Flask | 2.3.3 |
| WSGI Server | Werkzeug | 2.3.7 |
| Production Server | Gunicorn | 21.2.0 |
| Configuration | python-dotenv | ≥ 1.0.0 |

### PDF Processing
| Component | Technology | Version |
|-----------|------------|---------|
| Primary PDF Engine | PyMuPDF (`fitz`) | ≥ 1.23.0 |
| PDF Read/Write | PyPDF2 | 3.0.1 |
| PDF Data Extraction | pdfplumber | ≥ 0.11.0 |
| PDF-to-Image | pdf2image | ≥ 1.17.0 |

### Image & Document Processing
| Component | Technology | Version |
|-----------|------------|---------|
| Image Processing | Pillow (PIL) | 10.1.0 |
| Computer Vision | OpenCV (`opencv-python-headless`) | ≥ 4.12.0 |
| Word Documents | python-docx | 1.1.0 |
| PDF Generation | ReportLab | 4.0.7 |
| HTML-to-PDF | WeasyPrint | ≥ 60.0 |
| Numerical Computing | NumPy | ≥ 1.26.0 |
| System Monitoring | psutil | ≥ 5.9.0 |
| HTTP Requests | requests | ≥ 2.31.0 |

### OCR (Text Recognition)
| Component | Technology | Version |
|-----------|------------|---------|
| OCR Engine (Python) | pytesseract | ≥ 0.3.10 |
| OCR Engine (System) | Tesseract OCR | Must be installed separately |

### Frontend
| Component | Details |
|-----------|---------|
| HTML Templates | Jinja2 (Flask's built-in) |
| Styling | Custom CSS (`static/css/styles.css`) |
| JavaScript | Vanilla JS (`static/js/main.js`) |
| Kannada Fonts | Noto Sans Kannada, Tunga, Baloo Tamma (bundled in `static/fonts/`) |

---

## 📁 Project Structure

```
kannada-pdftoolkit/
│
├── app.py                         # Main Flask application — all routes & session logic
├── config.py                      # App configuration (file limits, allowed extensions, etc.)
├── requirements.txt               # All Python package dependencies
├── users.json                     # Stores registered user accounts (auto-created)
├── sessions.json                  # Active login sessions (auto-created)
│
├── utils/                         # All specialized backend logic
│   ├── __init__.py
│   ├── auth.py                    # Authentication: login, signup, sessions, password hashing
│   ├── file_handler.py            # File upload handling and validation
│   ├── pdf_operations.py          # Core PDF operations (merge, split, rotate, compress, etc.)
│   ├── pdf_compare.py             # PDF comparison logic and report generation
│   ├── pdf_ocr_processor.py       # OCR processing for scanned PDFs
│   ├── kannada_font_manager.py    # Kannada font loading and management for PDF output
│   ├── kannada_numeral_converter.py # Converts numerals to Kannada script
│   ├── validators.py              # Input validation utilities
│   └── fonts/                     # Internal fonts used for PDF generation
│
├── textUtils/                     # Text extraction utilities
│   └── pdf_text_extractor.py      # PDF-to-Word conversion (OCR + text + images)
│
├── templates/                     # HTML templates (Jinja2)
│   ├── base.html                  # Base layout (header, navigation, footer)
│   ├── index.html                 # Home page — tool selection dashboard
│   ├── upload.html                # Main upload & operation page
│   ├── login.html                 # Login page (Kannada UI)
│   ├── signup.html                # Registration page with employee fields
│   ├── profile.html               # User profile and settings
│   └── compare_result.html        # Side-by-side PDF comparison result viewer
│
├── static/                        # Frontend assets
│   ├── css/
│   │   └── styles.css             # All application styles
│   ├── js/
│   │   └── main.js                # Frontend JavaScript logic
│   ├── fonts/                     # Bundled Kannada font files (.ttf)
│   │   ├── NotoSansKannada-Regular.ttf
│   │   ├── NotoSansKannada_Condensed-Bold.ttf
│   │   ├── Noto_Sans_Kannada-Regular.ttf
│   │   ├── tunga-regular-unicode-kannada-font.ttf
│   │   ├── tunga-bold-unicode-kannada-font.ttf
│   │   ├── baloo-tamma-regular-unicode-kannada-font.ttf
│   │   ├── lohit-kannada-ansi-font.ttf
│   │   ├── nudi-kannada-ansi-font.ttf
│   │   └── baraha-kannada-ansi-font.TTF
│   ├── images/                    # Application images and icons
│   │   └── government/            # Karnataka government logos
│   ├── comparisons/               # Temporarily stored comparison images
│   ├── uploads/                   # Temporary upload storage (auto-created)
│   ├── previews/                  # Thumbnail preview storage (auto-created)
│   └── temp/                      # Comparison temp images (auto-created)
│
└── output/                        # Processed output files for download (auto-created)
```

---

## 💻 System Requirements

### Minimum Requirements
| Component | Requirement |
|-----------|-------------|
| Operating System | Windows 10/11, Ubuntu 20.04+, macOS 11+ |
| Python | Python 3.9 or higher |
| RAM | 4 GB minimum (8 GB recommended) |
| Disk Space | 2 GB free (for app + dependencies + temporary files) |
| Browser | Chrome 90+, Firefox 88+, Edge 90+, Safari 14+ |

### System-Level Dependencies (Must be installed separately)

**Tesseract OCR** — required for the "PDF to Word" operation (OCR on scanned documents):

- **Windows:** Download installer from https://github.com/UB-Mannheim/tesseract/wiki
  After installing, add Tesseract to your system PATH.
- **Ubuntu/Debian Linux:**
  ```bash
  sudo apt update
  sudo apt install tesseract-ocr tesseract-ocr-kan
  ```
  The `tesseract-ocr-kan` package adds Kannada language support.
- **macOS:**
  ```bash
  brew install tesseract tesseract-lang
  ```

**Poppler** — required for the `pdf2image` library (PDF to Image conversion):

- **Windows:** Download from https://github.com/oschwartz10612/poppler-windows/releases and add `bin/` folder to PATH.
- **Ubuntu/Debian Linux:**
  ```bash
  sudo apt install poppler-utils
  ```
- **macOS:**
  ```bash
  brew install poppler
  ```

---

## 🚀 Installation & Setup

Follow these steps exactly, in order, to install and set up the Kannada PDF Toolkit on your machine.

### Step 1 — Clone the Repository

Open a terminal (Command Prompt / PowerShell on Windows, Terminal on Linux/macOS) and run:

```bash
git clone https://github.com/shreyaaaa06/kannada-pdftoolkit.git
cd kannada-pdftoolkit
```

### Step 2 — Install Python (if not already installed)

Check your Python version:
```bash
python --version
```
or
```bash
python3 --version
```

You need Python 3.9 or above. If not installed, download from https://www.python.org/downloads/. During installation on Windows, check the box **"Add Python to PATH"**.

### Step 3 — Create a Virtual Environment

A virtual environment keeps this project's dependencies separate from other Python projects on your system.

```bash
# Create the virtual environment
python -m venv venv
```

Now activate it:

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```
> If you get a PowerShell policy error, first run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**On Linux / macOS:**
```bash
source venv/bin/activate
```

You will see `(venv)` appear at the beginning of your terminal prompt, confirming the environment is active.

### Step 4 — Install Python Dependencies

With the virtual environment active, install all required packages:

```bash
pip install -r requirements.txt
```

This installs Flask, PyMuPDF, PyPDF2, Pillow, OpenCV, pytesseract, python-docx, ReportLab, WeasyPrint, gunicorn, and all other dependencies listed in `requirements.txt`.

> **Note:** This step may take 3–5 minutes depending on your internet speed and machine. If you see any warnings about dependency conflicts, they are usually safe to ignore unless installation fails.

### Step 5 — Install Tesseract OCR (for PDF to Word)

If you plan to use the **PDF to Word** feature with scanned documents, install Tesseract with Kannada language support as described in the [System Requirements](#-system-requirements) section above.

After installing, verify it works:
```bash
tesseract --version
```

### Step 6 — Install Poppler (for PDF to Image)

Install Poppler as described in the [System Requirements](#-system-requirements) section. After installing, verify:
```bash
pdftoppm -v
```

### Step 7 — Verify the Installation

Run a quick check to make sure all key packages are importable:

```bash
python -c "import flask, fitz, PyPDF2, PIL, docx, reportlab; print('All packages OK')"
```

If you see `All packages OK`, you are ready to run the application.

---

## ▶️ Running the Application

### Development Mode (Local Machine)

To avoid Unicode/Kannada text encoding issues — especially on Windows — always set the encoding flag when starting:

**On Windows PowerShell:**
```powershell
$env:PYTHONIOENCODING="utf-8"; python app.py
```

**On Windows Command Prompt:**
```cmd
set PYTHONIOENCODING=utf-8 && python app.py
```

**On Linux / macOS:**
```bash
PYTHONIOENCODING=utf-8 python app.py
```

Once started, you will see output similar to:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: off
```

Open your browser and go to: **http://127.0.0.1:5000**

The application will automatically:
- Create the `uploads/`, `output/`, `static/uploads/`, `static/previews/`, and `static/temp/` directories if they do not exist.
- Create `users.json` with default government employee accounts on first run.
- Create `sessions.json` for session tracking.
- Clean up temporary files older than 1 hour from previous sessions.

### Stopping the Application

Press `Ctrl + C` in the terminal to stop the server.

---

## 🔐 User Authentication

The application requires login before accessing any PDF operation (preview generation for basic operations is publicly accessible, but all actual processing requires a logged-in session).

### Default Accounts (Pre-loaded on First Run)

| Username | Password | Role | Department |
|----------|----------|------|------------|
| `admin` | `admin123` | Administrator | ಮಾಹಿತಿ ತಂತ್ರಜ್ಞಾನ ವಿಭಾಗ |
| `employee1` | `emp123` | Employee | ರಾಜಸ್ವ ವಿಭಾಗ |
| `employee2` | `emp123` | Employee | ಶಿಕ್ಷಣ ವಿಭಾಗ |

> **Security Note:** Change default passwords immediately after first login in any production/official deployment.

### Registering a New Government Employee Account

1. Go to **http://127.0.0.1:5000/signup**
2. Fill in the following fields:
   - **ಹೆಸರು (Name):** Full name of the employee
   - **ಇಮೇಲ್ (Email):** Official government email address
   - **ಉದ್ಯೋಗಿ ID (Employee ID):** Government employee ID number (optional)
   - **ವಿಭಾಗ (Department):** Department name (e.g., ರಾಜಸ್ವ ವಿಭಾಗ)
   - **ಹುದ್ದೆ (Designation):** Job title / designation
   - **ಪಾಸ್‌ವರ್ಡ್ (Password):** Minimum 6 characters
   - **ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ (Confirm Password):** Repeat the password
3. Click the signup button.
4. The system will create a unique username derived from the email address.
5. Log in with the generated username or the registered email address.

### Session Management

- Sessions last **8 hours** from login time.
- Sessions are stored securely in `sessions.json`.
- Expired sessions are automatically removed.
- To log out, click the logout button (ಹೊರಹೋಗಿ) in the navigation bar.

### Changing Your Password

1. Log in and go to your Profile page (`/profile`).
2. Enter your current password and the new password.
3. Confirm the new password and save.
4. Passwords are hashed using PBKDF2-SHA256 with a random salt — they are never stored in plain text.

---

## 📖 All PDF Operations — Step-by-Step Guide

After logging in, go to the Upload / Operation page. For each operation:

1. Select the operation from the dashboard.
2. Upload the required file(s).
3. Set the parameters.
4. (Optional) Generate a preview first.
5. Click "ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ" (Start Process) to execute.
6. Download the result.

---

### 1. Merge PDFs (ವಿಲೀನ)

**Purpose:** Combine 2 or more PDF files into a single PDF document.

**Steps:**
1. Select **"ವಿಲೀನ"** from the tool list.
2. Upload the first PDF file.
3. Add more PDF files using the "Add File" button (minimum 2 files required).
4. Optionally generate a merge preview to see page counts from each file.
5. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
6. The merged file will be named `<original_name>_merged.pdf` and will be available for download.

**Note:** Each uploaded file is assigned a unique identifier to prevent file name conflicts. Invalid or empty PDFs are automatically skipped during merge.

---

### 2. Split PDF (ವಿಭಾಗ)

**Purpose:** Divide a single PDF into multiple smaller PDF files.

**Steps:**
1. Select **"ವಿಭಾಗ"** from the tool list.
2. Upload the PDF file (must have at least 2 pages).
3. Choose the split method:
   - **By Pages:** Specify a page range (e.g., `1-3,4-6`)
   - **By File Size:** Split automatically based on target file size in MB
   - **By Pages per Chunk:** Set how many pages per output file
4. Set the maximum allowed output file size if needed.
5. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
6. If the result is multiple files, they are packaged into a `.zip` archive for download (`<original_name>_split.zip`).

---

### 3. Extract Pages (ಹೊರತೆಗೆಯುವಿಕೆ)

**Purpose:** Pull specific pages from a PDF into a new PDF file.

**Steps:**
1. Select **"ಹೊರತೆಗೆಯುವಿಕೆ"** from the tool list.
2. Upload the PDF file.
3. Enter the page numbers or ranges to extract. Supported formats:
   - Single page: `3`
   - Range: `1-5`
   - Multiple pages/ranges: `1,3,5-8,12`
4. Optionally generate a preview to verify which pages will be extracted.
5. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
6. Download the extracted file (`<original_name>_extracted.pdf`).

---

### 4. Delete Pages (ಅಳಿಸುವಿಕೆ)

**Purpose:** Remove specific pages from a PDF, keeping the rest.

**Steps:**
1. Select **"ಅಳಿಸುವಿಕೆ"** from the tool list.
2. Upload the PDF file.
3. Enter the page numbers or ranges to delete (same format as Extract).
4. Generate a before/after preview to confirm which pages will be removed.
5. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
6. Download the resulting file (`<original_name>_pages_deleted.pdf`).

---

### 5. Rotate Pages (ತಿರುಗಿಸುವಿಕೆ)

**Purpose:** Rotate one or all pages of a PDF by a specified angle.

**Steps:**
1. Select **"ತಿರುಗಿಸುವಿಕೆ"** from the tool list.
2. Upload the PDF file.
3. Choose the rotation angle: **90°, 180°, or 270°** (clockwise).
4. Specify which pages to rotate:
   - Leave blank to rotate all pages.
   - Enter page numbers/ranges (e.g., `1,3,5`) to rotate specific pages.
5. Toggle **"ಎಲ್ಲಾ ಪುಟಗಳಿಗೆ ಅನ್ವಯಿಸಿ"** (Apply to All) to rotate all pages.
6. Generate a preview to see the result before processing.
7. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
8. Download the rotated file (`<original_name>_rotated.pdf`).

---

### 6. Crop Pages (ಕತ್ತರಿಸುವಿಕೆ)

**Purpose:** Trim the margins of PDF pages to crop content.

**Steps:**
1. Select **"ಕತ್ತರಿಸುವಿಕೆ"** from the tool list.
2. Upload the PDF file.
3. Enter the crop margins (in points or millimetres):
   - **Top Margin (ಮೇಲ್ಭಾಗ)**
   - **Bottom Margin (ಕೆಳಭಾಗ)**
   - **Left Margin (ಎಡ)**
   - **Right Margin (ಬಲ)**
4. Generate a preview to verify the crop area.
5. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
6. Download the cropped PDF.

---

### 7. Compress PDF (ಸಂಕುಚನ)

**Purpose:** Reduce the file size of a PDF while maintaining acceptable quality.

**Steps:**
1. Select **"ಸಂಕುಚನ"** from the tool list.
2. Upload the PDF file.
3. Choose a compression level:
   - **Low (ಕಡಿಮೆ):** `0.9` quality ratio — minimal size reduction, best quality
   - **Medium (ಮಧ್ಯಮ):** `0.7` quality ratio — balanced (default)
   - **High (ಅಧಿಕ):** `0.5` quality ratio — maximum compression, smaller file
4. Optionally set a **Target Size in MB** to aim for a specific output file size.
5. Generate a preview to see estimated output size before processing.
6. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
7. Download the compressed file (`<original_name>_compressed.pdf`).

**Note:** If the primary compression method fails, the system automatically falls back to an alternative compression algorithm.

---

### 8. PDF to Image (PDF ರಿಂದ JPEG/PNG)

**Purpose:** Convert each page (or specific pages) of a PDF into image files.

**Steps:**
1. Select **"PDF ರಿಂದ JPEG"** from the tool list.
2. Upload the PDF file.
3. Set the following parameters:
   - **Image Format:** JPEG or PNG
   - **DPI (Resolution):** Default is 300 DPI (high quality). Lower DPI = smaller files.
   - **Page Range:** Leave blank for all pages, or enter a range (e.g., `1-5`).
4. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
5. If multiple pages are converted, all images are packaged into a `.zip` file for download (`<original_name>_images.zip`).

---

### 9. Image to PDF (JPEG ರಿಂದ PDF)

**Purpose:** Convert one or more image files (JPEG, PNG, etc.) into a single PDF document.

**Steps:**
1. Select **"JPEG ರಿಂದ PDF"** from the tool list.
2. Upload one or more image files. Supported formats: JPG, JPEG, PNG, GIF, BMP, TIFF.
3. The images are combined in the order they are uploaded.
4. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
5. Download the resulting PDF (`images_to_pdf.pdf`).

---

### 10. Word to PDF (Word ರಿಂದ PDF)

**Purpose:** Convert a Microsoft Word document (`.docx` or `.doc`) to PDF format.

**Steps:**
1. Select **"Word ರಿಂದ PDF"** from the tool list.
2. Upload the Word file (`.docx` or `.doc` only).
3. The system validates that the file is non-empty and has a correct extension.
4. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
5. Download the converted PDF (`<original_name>.pdf`).

**Note:** Uses WeasyPrint for conversion. Kannada text in Word documents is handled using the bundled Noto Sans Kannada font.

---

### 11. PDF to Word (PDF ರಿಂದ Word)

**Purpose:** Extract text from a PDF — including scanned/image-based PDFs — into a `.docx` Word file, using OCR if needed.

**Steps:**
1. Select **"PDF ರಿಂದ Word"** from the tool list.
2. Upload the PDF file.
3. Optionally specify a **Page Range** (e.g., `1-10`) to convert only certain pages.
4. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
5. The system extracts text using direct text extraction first; for image-based pages, it uses Tesseract OCR with Kannada language support.
6. Embedded images from the PDF are also extracted and embedded in the Word document.
7. Download the `.docx` file (`<original_name>.docx`).

**Requirements:** Tesseract OCR must be installed on the system for scanned document support.

---

### 12. Compare PDFs (ಹೋಲಿಕೆ)

See the dedicated [PDF Comparison Feature](#-pdf-comparison-feature) section below.

---

### 13. Sort Pages (ಸಾರಿಸು)

**Purpose:** Reorder the pages of a PDF by their printed page numbers (useful for scanned documents where pages are out of order).

**Steps:**
1. Select **"ಸಾರಿಸು"** from the tool list.
2. Upload the PDF file.
3. The system detects the page numbers printed on each page.
4. Generate a sorting preview to see the proposed new order.
5. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
6. Download the sorted file (`<original_name>_sorted.pdf`).

---

### 14. Protect PDF (ರಕ್ಷಿಸು)

**Purpose:** Add password protection to a PDF, with granular control over what readers can do.

**Steps:**
1. Select **"ರಕ್ಷಿಸು"** from the tool list.
2. Upload the PDF file.
3. Enter a password (minimum 6 characters).
4. Confirm the password.
5. Choose the encryption level: **128-bit** (standard) is recommended.
6. Set the permission options (what is allowed for someone with the password):
   - **ಮುದ್ರಣ (Allow Printing):** Allow the reader to print the document
   - **ನಕಲು (Allow Copying):** Allow copying text from the document
   - **ಮಾರ್ಪಾಡು (Allow Modification):** Allow editing the document
   - **ಟಿಪ್ಪಣಿ (Allow Annotation):** Allow adding comments/annotations
   - **ಫಾರ್ಮ್ ಭರ್ತಿ (Allow Form Filling):** Allow filling in PDF forms
7. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
8. Download the protected file (`<original_name>_protected.pdf`).

---

### 15. Unlock PDF (ಅನ್‌ಲಾಕ್)

**Purpose:** Remove the password from a password-protected PDF.

**Steps:**
1. Select **"ಅನ್‌ಲಾಕ್"** from the tool list.
2. Upload the password-protected PDF file.
3. Enter the correct password to unlock the file.
4. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
5. Download the unlocked file (`<original_name>_unlocked.pdf`).

**Note:** You must know the current password to unlock the file. This tool does not crack or bypass passwords.

---

## 👁️ Interactive Preview System

Nearly every operation supports a visual preview before you commit to processing. This prevents mistakes with irreversible operations like deletion or page removal.

### How the Preview Works

Thumbnails are generated at **0.3× scale** for fast loading without sacrificing visual accuracy. Each user's previews are fully isolated using their unique Session ID, so previews from different users never interfere with each other.

### Using the Preview (for Any Operation)

1. Select an operation and upload your PDF file.
2. Set the operation parameters (page range, rotation angle, etc.).
3. Click **"ಪೂರ್ವವೀಕ್ಷಣೆ ರಚಿಸಿ" (Generate Preview)**.
4. Wait a moment while page thumbnails are generated.
5. Review the preview to confirm the expected result.
6. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ" (Start Process)** to execute the actual operation.

### What Each Preview Shows

| Operation | Preview Shows |
|-----------|---------------|
| Rotate | Before and after thumbnails for each affected page |
| Delete | Which pages will be removed (highlighted/crossed out) |
| Extract | Which pages will be pulled out |
| Merge | All input files and their page counts |
| Split | How pages will be divided across output files |
| Compress | Estimated output file size and quality sample |
| PDF to Image | Sample output images for first/selected pages |
| Sort | Current order vs. proposed sorted order |

---

## 📊 PDF Comparison Feature

The PDF Comparison tool allows you to compare two PDF files side-by-side and get a detailed difference report. This is particularly useful for government employees who need to verify that a document has or has not been altered.

### Step-by-Step Comparison

1. Select **"ಹೋಲಿಕೆ"** (Compare) from the tool list.
2. Upload the **first PDF** (left side of comparison).
3. Upload the **second PDF** (right side of comparison).
4. Click **"ಪ್ರಕ್ರಿಯೆ ಪ್ರಾರಂಭಿಸಿ"**.
5. The system performs both **text-level** and **visual-level** comparison.
6. You are automatically redirected to the **Comparison Results** page (`/compare_result/<session_id>`).

### Reading the Comparison Report

The comparison result page shows:
- **Side-by-side view** of both PDFs with highlighted differences
- **Text differences** — added, removed, or changed text highlighted per page
- **Page-level summary** — which pages differ between the two documents
- The comparison result can be downloaded as a PDF report named `Comparison_<File1>_vs_<File2>.pdf`

### Comparison Data Persistence

Comparison results are stored both in the user session and in a JSON file (`output/<session_id>_comparison.json`), so the results remain accessible even after a page refresh.

---

## 🔒 Security & Access Control

### Login Protection

All PDF processing routes are protected by the `@login_required` decorator. Unauthenticated requests to protected routes return a `401 Unauthorized` response (or redirect to the login page for browser requests).

### File Security

- Uploaded filenames are sanitized using `werkzeug.utils.secure_filename` to prevent path traversal attacks.
- The application verifies that file serving is restricted to within the designated output directory (prevents directory traversal).
- Comparison temp files are served through a security-checked endpoint (`/static/temp/<session_id>/<filename>`).

### Password Security

- All passwords are hashed with **PBKDF2-SHA256** using a unique 16-byte random salt per user.
- Plaintext passwords are never stored anywhere.
- Password minimum length is enforced at 6 characters.

### Session Security

- Sessions use a cryptographically random token generated with `secrets.token_urlsafe(32)`.
- Sessions expire automatically after **8 hours**.
- Each session is tracked individually in `sessions.json`.
- On logout, the session token is immediately invalidated.

### File Size Limits

- Maximum upload file size: **1000 MB (1 GB)** per request.
- This limit is enforced at the Flask level and returns a `413 Request Entity Too Large` response with a Kannada error message if exceeded.

---

## 🌐 Deployment Guide

### Deploying on Render (Recommended for Karnataka Government Use)

1. Push your code to a GitHub repository.
2. Go to https://render.com and create a free account.
3. Click **"New Web Service"** and connect it to your GitHub repository.
4. Set the following options:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3
5. Add an environment variable:
   - Key: `SECRET_KEY`
   - Value: A long random string (e.g., `openssl rand -hex 32`)
6. Click **Deploy**. Render will build and start the application.
7. Your application will be live at `https://<your-app-name>.onrender.com`.

**Important Note:** Tesseract OCR and Poppler may not be available on Render's free tier. For full OCR support in a cloud environment, use a Docker-based deployment or a cloud VM (such as AWS EC2, Azure VM, or DigitalOcean Droplet) where you can install system-level packages.

### Deploying with Gunicorn (Linux Server)

For production use on a Linux server (Ubuntu/Debian):

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn (4 worker processes recommended)
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or with a specific port
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Deploying with Nginx (Reverse Proxy)

For serving behind Nginx on a Linux server, create a systemd service file and an Nginx configuration pointing to your Gunicorn instance on localhost port 5000. This setup is recommended for official government department deployments.

---

## ⚙️ Configuration Reference

The application's configuration is centralized in `config.py`. Key settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `SECRET_KEY` | `kannada-pdf-toolkit-secret-key-2024` | Flask secret key for sessions. **Change this in production.** |
| `MAX_CONTENT_LENGTH` | 1 GB | Maximum upload file size |
| `UPLOAD_FOLDER` | `./uploads` | Directory for temporary uploaded files |
| `OUTPUT_FOLDER` | `./output` | Directory for processed output files |
| `PDF_DPI` | 200 | DPI for PDF rendering |
| `PDF_QUALITY` | 85 | Image quality for PDF thumbnails |
| `CLEANUP_INTERVAL` | 3600 seconds | How often old files are cleaned up |
| `MAX_FILE_AGE` | 3600 seconds | Maximum age before a file is deleted |
| `COMPRESSION_LEVELS.low` | 0.9 | Low compression quality ratio |
| `COMPRESSION_LEVELS.medium` | 0.7 | Medium compression quality ratio |
| `COMPRESSION_LEVELS.high` | 0.5 | High compression quality ratio |

### Allowed File Extensions

| Type | Extensions |
|------|------------|
| PDF | `.pdf` |
| Image | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff` |
| Word | `.doc`, `.docx` |

---

## 🧹 File Management & Cleanup

The application automatically manages temporary files to prevent disk space buildup.

### Automatic Cleanup on Startup

When `app.py` starts, `cleanup_old_files()` runs and deletes all files in `uploads/`, `output/`, and `static/previews/` that are older than 1 hour.

### Per-Session Cleanup

- When a user resets their session (using the reset button), all files associated with that session are immediately deleted.
- The `/reset` endpoint clears all session data and triggers `cleanup_session_files()` for the previous session ID.
- The `/cleanup-session` endpoint can be called explicitly to clean up session files.

### Manual Cleanup

If you need to manually clear all temporary files:

```bash
# From within the project directory
rm -rf static/uploads/*
rm -rf static/previews/*
rm -rf static/temp/*
rm -rf output/*
```

---

## 🛠 Troubleshooting

### Problem: Kannada text appears as boxes/squares

**Cause:** The browser or PDF viewer does not have a Kannada font installed, or the system font is not rendering correctly.

**Solution:**
- The application bundles Noto Sans Kannada and Tunga fonts in `static/fonts/`. Ensure these files exist.
- On Windows, install the "Noto Sans Kannada" font from Google Fonts.
- For PDF output with Kannada text, ensure the font is being registered through `utils/kannada_font_manager.py`.

---

### Problem: `UnicodeEncodeError` or garbled Kannada text in terminal

**Cause:** Windows terminal does not default to UTF-8 encoding.

**Solution:** Always start the application with the encoding flag:
```powershell
$env:PYTHONIOENCODING="utf-8"; python app.py
```

---

### Problem: PDF to Word conversion fails or produces empty output

**Cause:** Tesseract OCR is not installed or not in the system PATH.

**Solution:**
1. Install Tesseract OCR (see [System Requirements](#-system-requirements)).
2. Verify it is accessible: `tesseract --version`
3. For Kannada OCR, also install the Kannada language pack: `sudo apt install tesseract-ocr-kan`

---

### Problem: PDF to Image conversion fails

**Cause:** Poppler utilities are not installed or not in the system PATH.

**Solution:**
1. Install Poppler (see [System Requirements](#-system-requirements)).
2. Verify: `pdftoppm -v`
3. On Windows, ensure the Poppler `bin/` folder is added to your system PATH.

---

### Problem: Word to PDF conversion produces an empty or broken PDF

**Cause:** WeasyPrint requires proper system libraries on Linux (Cairo, Pango, etc.).

**Solution on Ubuntu/Debian:**
```bash
sudo apt install libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

---

### Problem: `ModuleNotFoundError` for any package

**Cause:** The virtual environment is not activated, or `pip install` was not completed.

**Solution:**
1. Activate the virtual environment: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows).
2. Re-run: `pip install -r requirements.txt`

---

### Problem: File upload fails with "413 Request Entity Too Large"

**Cause:** The file exceeds the 1000 MB limit set in `app.config['MAX_CONTENT_LENGTH']`.

**Solution:** The current limit is 1 GB. For larger files, increase the limit in `app.py` (line 191):
```python
app.config['MAX_CONTENT_LENGTH'] = 2000 * 1024 * 1024  # 2 GB
```

---

### Problem: Session expires unexpectedly

**Cause:** Sessions are set to expire after 8 hours by default.

**Solution:** To extend session duration, modify the `timedelta` in `utils/auth.py`:
```python
'expires_at': (datetime.now() + timedelta(hours=12)).isoformat(),  # Change to 12 hours
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/` | No | Home page (shows user info if logged in) |
| GET/POST | `/login` | No | Login page and authentication |
| GET/POST | `/signup` | No | User registration page |
| GET | `/logout` | Yes | Logout and invalidate session |
| GET | `/profile` | Yes | User profile page |
| POST | `/upload` | Yes (for process) | Main file upload and operation endpoint |
| POST | `/process` | Yes | Alias for `/upload` |
| GET | `/download/<session_id>/<filename>` | No | Download a processed file |
| POST | `/generate-preview` | No | Generate page thumbnails for a PDF |
| POST | `/generate-sort-preview` | No | Generate page sorting preview |
| POST | `/generate-operation-preview` | Yes | Generate operation-specific preview |
| POST | `/compare` | No | Compare two PDF files (alternate endpoint) |
| GET | `/compare_result/<session_id>` | No | View comparison results |
| GET | `/compare-result` | No | View comparison results (session-based) |
| GET | `/thumbnails/<session_id>/<filename>` | No | Serve thumbnail images |
| GET | `/output/<path:filename>` | Yes | Serve output files |
| GET | `/static/temp/<session_id>/<filename>` | No | Serve comparison temp images |
| GET | `/pdf-page/<session_id>/<file_num>/<page_num>` | No | Serve rendered PDF page image |
| POST | `/reset` | No | Reset session and clean up files |
| POST | `/cleanup-session` | No | Clean up session files |

---

## 🤝 Contributing

Contributions to improve the Kannada PDF Toolkit are welcome. To contribute:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes.
4. Test thoroughly, especially for Kannada text handling and encoding.
5. Commit with a clear message:
   ```bash
   git commit -m "Add: description of what you added"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Open a Pull Request on the main repository.

### Development Guidelines

- All user-facing text (labels, buttons, error messages) should be in Kannada (ಕನ್ನಡ).
- Always test file operations with both English and Kannada filenames.
- Always set `PYTHONIOENCODING=utf-8` when testing on Windows.
- Keep the Tesseract and Poppler dependencies documented if adding new features that use them.

---

## 📜 License

This project is developed for use by Karnataka Government Departments. Please refer to the project repository for licensing details.

---

## 📞 Support

For technical issues or feature requests:
- Open an issue on the GitHub repository: https://github.com/shreyaaaa06/kannada-pdftoolkit/issues
- Contact the development team through the repository's contact information.

---

*ಕರ್ನಾಟಕ ಸರ್ಕಾರಿ ನೌಕರರ ಸೇವೆಯಲ್ಲಿ — In service of Karnataka Government Employees* 🇮🇳
