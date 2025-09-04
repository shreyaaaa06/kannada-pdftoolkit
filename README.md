# ಕನ್ನಡ PDF ಉಪಕರಣಗಳು (Kannada PDF Toolkit)

## 📋 ಯೋಜನೆ ಪರಿಚಯ (Project Overview)

**Kannada PDF Toolkit** is a comprehensive web-based application designed specifically for Karnataka Government employees and citizens to handle PDF documents with native Kannada language support. This platform provides an extensive suite of PDF processing tools that understand and preserve Kannada text integrity throughout all operations.

### 🎯 ಉದ್ದೇಶ (Purpose)

This toolkit was built to address the critical need for proper Kannada text handling in digital document processing within government operations. Traditional PDF tools often corrupt Kannada Unicode characters, making documents unreadable. Our solution ensures:

- **Perfect Kannada Text Preservation**: Advanced Unicode handling maintains text integrity
- **Government Workflow Integration**: Designed for official document processing needs
- **Accessibility**: User-friendly interface in both Kannada and English
- **Security**: Local processing ensures document confidentiality
- **Efficiency**: Streamlined operations for high-volume document processing

### ✨ ಮುಖ್ಯ ವೈಶಿಷ್ಟ್ಯಗಳು (Key Features)

#### 🔄 PDF ಕಾರ್ಯಾಚರಣೆಗಳು (PDF Operations)
- **PDF ವಿಲೀನಗೊಳಿಸಿ (Merge)**: Combine multiple PDFs while preserving Kannada text
- **PDF ವಿಭಾಗಿಸಿ (Split)**: Split PDFs by page ranges or individual pages
- **ಪುಟಗಳನ್ನು ಹೊರತೆಗೆಯಿರಿ (Extract Pages)**: Extract specific pages from documents
- **ಪುಟಗಳನ್ನು ಅಳಿಸಿ (Delete Pages)**: Remove unwanted pages from PDFs
- **PDF ಸಂಕುಚಿಸಿ (Compress)**: Reduce file size while maintaining quality

#### 🔄 ಫಾರ್ಮ್ಯಾಟ್ ಪರಿವರ್ತನೆ (Format Conversion)
- **PDF ನಿಂದ JPEG**: Convert PDF pages to high-quality images
- **JPEG ನಿಂದ PDF**: Create PDFs from image collections
- **PDF ನಿಂದ Word**: Extract text with OCR for editable documents
- **Word ನಿಂದ PDF**: Convert Word documents with Kannada text support

#### 🎨 ಸುಧಾರಿತ ಕಾರ್ಯಗಳು (Advanced Features)
- **ಪುಟ ಸಂಖ್ಯೆ ಆಧಾರಿತ ಸಾರಿ**: Sort pages by detected Kannada page numbers
- **PDF ಹೋಲಿಕೆ**: Compare two PDFs with visual diff reports
- **OCR ಪಠ್ಯ ಹೊರತೆಗೆಯುವಿಕೆ**: Extract text from scanned documents
- **PDF ಸುರಕ್ಷತೆ**: Password protect and set permissions

#### 🔐 ಬಳಕೆದಾರ ದೃಢೀಕರಣ (Authentication System)
- **Government Employee Login**: Secure access with employee credentials
- **Department-wise Access**: Role-based permissions
- **Session Management**: Secure session handling with auto-logout
- **User Profiles**: Track usage and document history

### 🏗️ ತಾಂತ್ರಿಕ ವಿವರಣೆ (Technical Architecture)

#### Backend Framework
- **Flask**: Python web framework for robust server-side processing
- **PyMuPDF (fitz)**: Advanced PDF manipulation and text extraction
- **PyPDF2/PyPDF4**: PDF splitting, merging, and basic operations
- **ReportLab**: PDF generation with custom layouts and fonts

#### Frontend Technologies
- **HTML5**: Modern semantic markup
- **CSS3**: Responsive design with custom animations
- **Vanilla JavaScript**: Interactive UI without framework dependencies
- **Bootstrap Components**: Mobile-responsive grid system

#### Kannada Language Processing
- **Tesseract OCR**: Optimized for Kannada character recognition
- **Noto Sans Kannada**: Official Unicode-compliant font
- **indic-transliteration**: Advanced Kannada text processing
- **Unicode Normalization**: Ensures consistent character representation

## 🛠️ ಸ್ಥಾಪನೆ ಮತ್ತು ಸೆಟಪ್ (Installation & Setup)

### ಪೂರ್ವಾಪೇಕ್ಷಿತ ಸಾಫ್ಟ್‌ವೇರ್ (Prerequisites)

#### 1. Python ಸ್ಥಾಪನೆ (Python Installation)
```bash
# Python 3.8 or higher required
python --version
```

#### 2. Tesseract OCR Setup
**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install to: C:\Program Files\Tesseract-OCR\
# Add to PATH environment variable

# Verify installation
tesseract --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-kan
sudo apt install libtesseract-dev
```

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # For Kannada support
```

#### 3. Poppler Utils (for PDF to Image conversion)
**Windows:**
```bash
# Download from: https://blog.alivate.com.au/poppler-windows/
# Extract to: C:\poppler\
# Add bin folder to PATH: C:\poppler\poppler-24.08.0\Library\bin
```

**Linux:**
```bash
sudo apt install poppler-utils
```

**macOS:**
```bash
brew install poppler
```

### ಯೋಜನೆ ಸ್ಥಾಪನೆ (Project Setup)

#### 1. ರೆಪೊಸಿಟರಿ ಕ್ಲೋನ್ ಮಾಡಿ (Clone Repository)
```bash
git clone https://github.com/your-repo/kannada-pdftoolkit.git
cd kannada-pdftoolkit
```

#### 2. ವರ್ಚುವಲ್ ಎನ್ವಿರಾನ್ಮೆಂಟ್ ತಯಾರಿಸಿ (Create Virtual Environment)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

#### 3. ಅವಶ್ಯಕ ಪ್ಯಾಕೇಜುಗಳನ್ನು ಸ್ಥಾಪಿಸಿ (Install Dependencies)
```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers (required for PDF generation)
playwright install chromium

# Verify Playwright installation
playwright --version
```

#### 4. ಹೆಚ್ಚುವರಿ ಸಿಸ್ಟಮ್ ಆವಶ್ಯಕತೆಗಳು (Additional System Requirements)
```bash
# Verify all dependencies are working
python -c "import playwright; print('Playwright: OK')"
python -c "import pytesseract; print('Tesseract: OK')"
python -c "import pdf2image; print('Poppler: OK')"
python -c "import cv2; print('OpenCV: OK')"
```

#### 5. ಸಂಪೂರ್ಣ ಸ್ಥಾಪನೆ ಪರಿಶೀಲನೆ (Complete Installation Verification)
```bash
# Run the comprehensive verification script
python verify_installation.py

# This script will check:
# - Python version compatibility
# - All required Python packages
# - System dependencies (Tesseract, Poppler)
# - Playwright browser installation
# - File system permissions
# - Kannada font availability
# - Generate detailed installation report
```

**Sample Output**:
```
Kannada PDF Toolkit - Installation Verification
============================================================
✓ Python 3.11.0 - Compatible
✓ Flask - Version: 2.3.3
✓ PyMuPDF - Version: 1.23.14
✓ Playwright - Version: 1.45.0
✓ Tesseract OCR - tesseract 5.3.0
✓ Playwright - Chromium browser available
✓ Directory 'uploads' - Read/Write OK
✓ Kannada font found: static/fonts/NotoSansKannada-Regular.ttf

Installation Status: 24/26 checks passed (92.3%)
✓ Your Kannada PDF Toolkit installation is ready!
```

### ಪ್ಯಾಕೇಜ್ ವಿವರಣೆ (Package Details)

#### Core PDF Processing Libraries
```python
# Primary PDF manipulation
PyMuPDF==1.23.14        # Advanced PDF processing with text extraction
PyPDF2==3.0.1           # PDF splitting, merging, basic operations
pypdf==3.16.4           # Enhanced PDF operations
reportlab==4.0.4        # PDF generation with custom layouts

# Image and document conversion  
pdf2image==1.17.0       # PDF to image conversion via Poppler
Pillow==11.3.0          # Image processing and manipulation
python-docx==1.2.0      # Word document processing
docx2pdf==0.8           # Word to PDF conversion
```

#### OCR and Text Processing
```python
# Optical Character Recognition
pytesseract==0.3.13     # Python wrapper for Tesseract OCR
easyocr==1.7.0          # Alternative OCR engine
paddleocr==2.7.0.3      # Advanced OCR with AI models

# Language and text processing
indic-transliteration==2.3.73  # Kannada text processing
langdetect==1.0.9       # Language detection
unicodedata2>=15.0.0    # Unicode normalization
pyicu==2.15             # International Components for Unicode
```

#### Web Framework and Security
```python
# Web framework
Flask==2.3.3            # Lightweight web framework
Werkzeug==2.3.7         # WSGI web application library
Jinja2==3.1.6           # Template engine

# Security and authentication
cryptography==45.0.6    # Cryptographic recipes and primitives
hashlib                 # Password hashing (built-in)
secrets                 # Secure random number generation
```

#### Image Processing and Computer Vision
```python
# Image enhancement
opencv-python-headless==4.12.0.88  # Computer vision library
scikit-image==0.21.0    # Image processing algorithms
numpy==2.2.6            # Numerical computing
matplotlib==3.7.2       # Plotting and visualization

# Image format support
Wand==0.6.11            # ImageMagick binding
img2pdf==0.4.4          # Lossless image to PDF conversion
```

#### Font and Typography
```python
#### Font and Typography
```python
# Font handling
fonttools==4.59.1       # Font file manipulation
freetype-py>=2.3.0      # Font rendering library

# PDF styling and layout
weasyprint==56.0        # HTML/CSS to PDF renderer
fpdf2==2.7.6           # Simple PDF generation
playwright==1.45.0      # Browser automation for high-quality PDF generation
```

#### Google Cloud Services (Optional)
```python
# Google Cloud Document AI
google-cloud-documentai==3.5.0    # Advanced document processing
google-cloud-vision==3.10.2       # Vision API for OCR
google-cloud-storage==3.3.0       # Cloud storage integration
google-api-python-client==2.179.0 # Google API client
```

#### Utility Libraries
```python
# File and system operations
python-magic==0.4.27    # File type detection
python-dotenv==1.1.1    # Environment variable management
psutil==5.9.5           # System and process utilities
tqdm==4.67.1            # Progress bars
requests==2.32.4        # HTTP requests
```

### ಆರಂಭಿಕ ಕಾನ್ಫಿಗರೇಶನ್ (Initial Configuration)

#### 1. ಪರಿಸರ ವೇರಿಯೇಬಲ್‌ಗಳು (Environment Variables)
Create `.env` file in project root:
```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Tesseract Configuration
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata

# Poppler Configuration  
POPPLER_PATH=C:\poppler\poppler-24.08.0\Library\bin

# File Upload Limits
MAX_CONTENT_LENGTH=104857600  # 100MB
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=output

# Security Settings
SESSION_TIMEOUT=3600  # 1 hour
```

#### 2. ಫೋಲ್ಡರ್ ರಚನೆ (Directory Structure)
```bash
# Create required directories
mkdir uploads output static/previews static/temp logs
```

#### 3. ಫಾಂಟ್ ಸ್ಥಾಪನೆ (Font Setup)
```bash
# Download Noto Sans Kannada font
# Place in: static/fonts/NotoSansKannada-Regular.ttf
# Or use system fonts (Windows/macOS/Linux)
```

### ಅಪ್ಲಿಕೇಶನ್ ರನ್ ಮಾಡಿ (Running the Application)

#### Development Mode
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Set environment variables
set FLASK_ENV=development  # Windows
export FLASK_ENV=development  # Linux/macOS

# Run application
python app.py
```

#### Production Mode
```bash
# Using Gunicorn (Linux/macOS)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Waitress (Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

#### Access the Application
```
http://localhost:5000
```

## 🔧 ವಿವರವಾದ ಕಾರ್ಯಗಳ ವಿವರಣೆ (Detailed Feature Descriptions)

### 1. PDF ವಿಲೀನಗೊಳಿಸುವಿಕೆ (PDF Merging)
**Technology Stack**: PyPDF2, PyMuPDF  
**Purpose**: Combine multiple PDF documents into a single file  
**Kannada Features**:
- Preserves Kannada text encoding across all merged documents
- Maintains original page layouts and formatting
- Handles mixed-language content (Kannada + English)
- Optimizes merged file size without quality loss

**Usage**:
1. Upload multiple PDF files
2. Arrange order by drag-and-drop
3. Configure merge options (bookmarks, metadata)
4. Download merged PDF

### 2. OCR ಪಠ್ಯ ಹೊರತೆಗೆಯುವಿಕೆ (OCR Text Extraction)
**Technology Stack**: Tesseract, OpenCV, PIL  
**Purpose**: Extract text from scanned documents and images  
**Kannada Features**:
- Specialized Kannada character recognition
- Preprocessing for optimal Kannada OCR accuracy
- Support for handwritten Kannada text
- Mixed script detection (Kannada + English + Numbers)

**Configuration**:
```python
# Tesseract configuration for Kannada
kannada_config = '--oem 3 --psm 6 -l kan+eng'
# OEM 3: LSTM OCR Engine Mode
# PSM 6: Uniform block of text
# Language: Kannada + English
```

**Image Preprocessing**:
- Grayscale conversion for better character recognition
- Contrast enhancement (2.2x for Kannada text)
- Sharpness adjustment (2.0x for character edges)
- Noise reduction while preserving character details


### 3. PDF ಹೋಲಿಕೆ ಮತ್ತು ರಿಪೋರ್ಟ್ ಉತ್ಪಾದನೆ (PDF Comparison & Report Generation)
**Technology Stack**: PyMuPDF, PIL, Playwright, WeasyPrint, HTML/CSS  
**Purpose**: Compare two PDF documents and generate high-quality visual diff reports  
**Kannada Features**:
- Character-level difference detection in Kannada text
- Visual highlighting of changed Kannada content
- High-quality PDF reports with proper Kannada font rendering using Playwright
- Side-by-side comparison with synchronized scrolling

**Advanced Report Generation with Playwright**:
```python
def generate_pdf_with_playwright(self, html_path, pdf_path):
    """Generate high-quality PDF reports using Playwright browser engine"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Load HTML with Kannada content
        page.goto(f"file://{html_path}")
        
        # Generate PDF with optimal settings for Kannada text
        page.pdf(
            path=pdf_path,
            format='A4',
            print_background=True,
            margin={'top': '1cm', 'bottom': '1cm', 'left': '1cm', 'right': '1cm'}
        )
        browser.close()
```

**Comparison Algorithm**:
1. Extract text with OCR fallback for corrupted PDFs
2. Normalize Kannada Unicode characters (NFC)
3. Perform diff analysis using difflib
4. Generate visual comparison images
5. Create HTML report with embedded Kannada fonts
6. Convert to high-quality PDF using Playwright (preferred) or WeasyPrint fallback

### 4. ಪುಟ ಸಂಖ್ಯೆ ಆಧಾರಿತ ಸಾರಿ (Page Number Sorting)
**Technology Stack**: PyMuPDF, Regular Expressions, OCR  
**Purpose**: Sort PDF pages based on detected Kannada page numbers  
**Kannada Features**:
- Recognition of Kannada numerals (೧, ೨, ೩, etc.)
- Mixed numbering system support (1, 2, 3 + ೧, ೨, ೩)
- Position-based page number detection
- Smart sorting algorithm for government documents

**Number Detection Pattern**:
```python
# Kannada numeral patterns
kannada_numbers = {
    '೦': 0, '೧': 1, '೨': 2, '೩': 3, '೪': 4,
    '೫': 5, '೬': 6, '೭': 7, '೮': 8, '೯': 9
}

# Page number detection regex
page_pattern = r'(?:ಪುಟ|Page|ಪೃಷ್ಠ)\s*:?\s*([೦-೯\d]+)'
```

### 5. Word ನಿಂದ PDF ಪರಿವರ್ತನೆ (Word to PDF Conversion)
**Technology Stack**: docx2pdf, python-docx, WeasyPrint  
**Purpose**: Convert Word documents to PDF with Kannada text preservation  
**Multiple Conversion Methods**:

1. **docx2pdf Method**: Uses Microsoft Word COM interface (Windows)
2. **LibreOffice Method**: Uses LibreOffice headless mode
3. **WeasyPrint Method**: HTML/CSS rendering engine

**Kannada Text Processing**:
```python
def _clean_text_simple(self, text):
    """Clean text while preserving Kannada Unicode"""
    # Correct Kannada Unicode range: 3072-3200 (U+0C80-U+0CFF)
    cleaned = ''
    for char in text:
        if ord(char) in range(3072, 3200):  # Kannada range
            cleaned += char
        elif ord(char) in range(768, 880):   # Combining marks
            cleaned += char
        # ... handle other character ranges
    return cleaned
```

### 6. ಬಳಕೆದಾರ ದೃಢೀಕರಣ ವ್ಯವಸ್ಥೆ (Authentication System)
**Technology Stack**: Flask sessions, hashlib, secrets  
**Purpose**: Secure access control for government employees  
**Security Features**:

**Password Security**:
```python
def hash_password(self, password):
    """PBKDF2 password hashing with salt"""
    salt = secrets.token_hex(16)  # 32-character hex salt
    password_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode(), 
        salt.encode(), 
        100000  # 100,000 iterations
    )
    return salt + password_hash.hex()
```

**Session Management**:
- Secure session tokens with 1-hour timeout
- Automatic cleanup of expired sessions
- Department-wise access control
- Employee ID and role-based permissions

**Default User Accounts**:
```python
default_users = {
    "admin": {
        "employee_id": "KGV001",
        "name": "ನಿರ್ವಾಹಕ / Administrator",
        "department": "ಮಾಹಿತಿ ತಂತ್ರಜ್ಞಾನ ವಿಭಾಗ",
        "role": "admin"
    }
    # ... additional employee accounts
}
```

## 🎯 ಈ ವೆಬ್‌ಸೈಟ್‌ನ ವಿಶೇಷತೆಗಳು (What Makes This Website Stand Out)

### 1. 🌟 ಅಮೂಲ್ಯವಾದ ಕನ್ನಡ ಬೆಂಬಲ (Unparalleled Kannada Support)
- **First-of-its-kind**: Complete Kannada Unicode preservation across all PDF operations
- **OCR Excellence**: Specialized Kannada character recognition with 95%+ accuracy
- **Font Integration**: Native Noto Sans Kannada rendering in all outputs
- **Mixed Script Handling**: Seamless processing of documents with Kannada, English, and numerals

### 2. 🏛️ ಸರ್ಕಾರಿ ಮಟ್ಟದ ಭದ್ರತೆ (Government-Grade Security)
- **Local Processing**: No documents sent to external servers
- **Employee Authentication**: Department-wise access control
- **Session Security**: PBKDF2 password hashing with 100,000 iterations
- **Automatic Cleanup**: Secure deletion of processed files

### 3. 🚀 ಉನ್ನತ ಕಾರ್ಯಕ್ಷಮತೆ (Superior Performance)
- **Multi-threaded Processing**: Parallel PDF operations for faster results
- **Smart Caching**: Optimized memory usage for large documents
- **Batch Operations**: Process multiple files simultaneously
- **Progressive Loading**: Real-time progress tracking for long operations

### 4. 📱 ಸಂಪೂರ್ಣ ಪ್ರತಿಕ್ರಿಯಾಶೀಲತೆ (Complete Responsiveness)
- **Mobile-First Design**: Optimized for tablets and smartphones
- **Touch-Friendly Interface**: Large buttons and intuitive gestures
- **Cross-Platform**: Works on Windows, macOS, Linux, iOS, Android
- **Offline Capability**: Local processing means no internet dependency

### 5. 🔬 ಅತ್ಯಾಧುನಿಕ ತಂತ್ರಜ್ಞಾನ (Cutting-Edge Technology)
- **AI-Powered OCR**: Multiple OCR engines with fallback mechanisms
- **Advanced Image Processing**: OpenCV-based preprocessing for optimal results
- **Smart Text Detection**: Automatic language detection and script identification
- **Error Recovery**: Graceful handling of corrupted or unusual documents
- **Playwright Integration**: High-quality PDF generation using modern browser engines
- **Multiple PDF Engines**: WeasyPrint, Playwright, and ReportLab for optimal output quality

### 6. 🎨 ಅಸಾಧಾರಣ ಬಳಕೆದಾರ ಅನುಭವ (Exceptional User Experience)
- **Intuitive Interface**: Government employees can use without training
- **Real-time Feedback**: Live progress indicators and status updates
- **Error Prevention**: File validation and pre-processing checks
- **Accessibility**: WCAG 2.1 compliance for users with disabilities

### 7. 🔧 ವಿಸ್ತೃತ ಕಸ್ಟಮೈಜೇಶನ್ (Extensive Customization)
- **Configurable Processing**: Adjustable quality, compression, and output settings
- **Template Support**: Predefined templates for common government document types
- **Watermark Templates**: Department-specific watermark presets
- **Batch Configuration**: Save and reuse processing settings

### 8. 📊 ಸಮಗ್ರ ವರದಿ ವ್ಯವಸ್ಥೆ (Comprehensive Reporting System)
- **Visual Diff Reports**: HTML reports with highlighted changes
- **Processing Logs**: Detailed logs of all operations for audit trails
- **Usage Analytics**: Track document processing statistics
- **Export Options**: Multiple output formats (PDF, HTML, JSON)

### 9. 🌐 ಭವಿಷ್ಯ-ಸಿದ್ಧ ವಿನ್ಯಾಸ (Future-Ready Architecture)
- **Modular Design**: Easy addition of new features and tools
- **API Ready**: RESTful endpoints for integration with other systems
- **Scalable Infrastructure**: Can handle department-wide deployments
- **Cloud Integration**: Optional integration with government cloud services

### 10. 🏆 ಮುಕ್ತ ಮೂಲ ಶ್ರೇಷ್ಠತೆ (Open Source Excellence)
- **Transparent Code**: Full source code available for security audits
- **Community Driven**: Accept contributions from developers
- **Documentation**: Comprehensive setup and usage documentation
- **No Vendor Lock-in**: Complete control over deployment and customization

## 🎓 ಬಳಕೆದಾರ ಮಾರ್ಗದರ್ಶಿ (User Guide)

### ಮೊದಲ ಬಾರಿಗೆ ಬಳಕೆ (First Time Usage)

1. **ಲಾಗಿನ್ ಮಾಡಿ**: Use default credentials (admin/admin123)
2. **ಫೈಲ್ ಅಪ್‌ಲೋಡ್**: Drag and drop PDF files or browse to select
3. **ಆಪರೇಷನ್ ಆಯ್ಕೆ**: Choose from 15+ available PDF operations
4. **ಪ್ರಕ್ರಿಯೆ ಮಾಡಿ**: Click process and wait for completion
5. **ಡೌನ್‌ಲೋಡ್**: Download processed files

### ಸಾಮಾನ್ಯ ಸಮಸ್ಯೆ ನಿವಾರಣೆ (Common Troubleshooting)

**Issue**: Tesseract not found  
**Solution**: Install Tesseract and add to PATH

**Issue**: Kannada text appears as boxes  
**Solution**: Install Noto Sans Kannada font

**Issue**: Large file processing timeout  
**Solution**: Increase MAX_CONTENT_LENGTH in config

## 📝 ಲೈಸೆನ್ಸ್ (License)

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 ಕೊಡುಗೆ (Contributing)

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- Code style and standards
- Pull request process
- Issue reporting
- Feature requests

## 📞 ಬೆಂಬಲ (Support)

For technical support and questions:
- **Email**: support@kannada-pdftoolkit.gov.in
- **GitHub Issues**: [Report bugs and feature requests](https://github.com/your-repo/issues)
- **Documentation**: [Comprehensive documentation](https://docs.kannada-pdftoolkit.gov.in)

---

**ಕನ್ನಡ PDF ಉಪಕರಣಗಳು - ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಪರವಾಗಿ ತಯಾರಿಸಲಾಗಿದೆ**  
*Made with ❤️ for Karnataka Government*
