# Deployment Guide - PDF Sorting and Lock Toolkit

## Quick Start

### Option 1: Using the Startup Script (Recommended)
1. Double-click `start_app.bat`
2. The script will automatically:
   - Check Python installation
   - Create virtual environment
   - Install dependencies
   - Start the application
3. Open your browser to `http://localhost:5000`

### Option 2: Manual Setup
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

## Features Overview

### 🔢 Page Sorting (ಪುಟ ಸಾರಿಸುವಿಕೆ)
- **Purpose**: Sort PDF pages based on Kannada numerals found in the text
- **Input**: PDF file with Kannada page numbers
- **Output**: PDF with pages sorted in correct numerical order
- **Supports**: 
  - Kannada digits (೦೧೨೩೪೫೬೭೮೯)
  - Kannada number words (ಒಂದು, ಎರಡು, ಮೂರು, etc.)
  - Mixed formats (ಪುಟ ೧೨, Page 25, ೧೫ನೇ ಪುಟ)

### 🔒 PDF Protection (PDF ರಕ್ಷಣೆ)
- **Purpose**: Add password protection to PDF files
- **Input**: Any PDF file + password
- **Output**: Password-protected PDF
- **Features**:
  - Minimum 6-character password requirement
  - Password confirmation for security
  - 128-bit encryption
  - Compatible with most PDF readers

### 🔓 PDF Unlock (PDF ಅನ್‌ಲಾಕ್)
- **Purpose**: Remove password protection from PDF files
- **Input**: Password-protected PDF + correct password
- **Output**: Unlocked PDF file
- **Features**:
  - Automatic encryption detection
  - Support for various encryption methods
  - Secure password handling

## File Structure

```
sorting_lock_toolkit/
├── app.py                    # Main Flask application
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── start_app.bat           # Windows startup script
├── cleanup.bat             # File cleanup script
├── test_toolkit.py         # Test suite
├── README.md               # Documentation
│
├── utils/                  # Core utilities
│   ├── __init__.py
│   ├── file_handler.py     # File management
│   ├── pdf_operations.py   # PDF processing
│   └── kannada_numeral_converter.py # Kannada number detection
│
├── templates/              # Web interface
│   └── index.html          # Main page
│
├── static/                 # Static assets
│   ├── css/
│   │   └── styles.css      # Custom styling
│   └── uploads/            # Temporary uploads
│
├── uploads/                # File upload directory
└── output/                 # Processed files output
```

## Usage Instructions

### 1. Page Sorting
1. **Upload File**: Click "ಪುಟ ಸಾರಿಸುವಿಕೆ" tab and upload your PDF
2. **Preview**: Review the detected page numbers and sorting order
3. **Process**: Click "ಪುಟಗಳನ್ನು ಸಾರಿಸಿ" to sort pages
4. **Download**: Download the sorted PDF file

### 2. PDF Protection
1. **Upload File**: Click "PDF ರಕ್ಷಣೆ" tab and upload your PDF
2. **Set Password**: Enter a password (minimum 6 characters)
3. **Confirm**: Re-enter password for confirmation
4. **Process**: Click "PDF ರಕ್ಷಿಸಿ" to protect the file
5. **Download**: Download the protected PDF

### 3. PDF Unlock
1. **Upload File**: Click "PDF ಅನ್‌ಲಾಕ್" tab and upload protected PDF
2. **Check Status**: System automatically detects if PDF is encrypted
3. **Enter Password**: Input the PDF password
4. **Process**: Click "PDF ಅನ್‌ಲಾಕ್ ಮಾಡಿ" to unlock
5. **Download**: Download the unlocked PDF

## Technical Specifications

### System Requirements
- **Python**: 3.7 or higher
- **RAM**: Minimum 512MB (2GB recommended for large files)
- **Storage**: 100MB free space + space for temporary files
- **Browser**: Modern browser with JavaScript enabled

### File Limitations
- **Maximum file size**: 100MB per file
- **Supported formats**: PDF only
- **Page limit**: No specific limit (performance may vary with very large documents)

### Security Features
- Session-based file management
- Automatic file cleanup after 1 hour
- Secure password handling (passwords not stored)
- Input validation and sanitization
- CSRF protection

### Kannada Number Recognition
The toolkit recognizes various Kannada numeral formats:

**Kannada Digits**: ೦೧೨೩೪೫೬೭೮೯
**Number Words**: 
- ಒಂದು (1), ಎರಡು (2), ಮೂರು (3), ನಾಲ್ಕು (4), ಐದು (5)
- ಆರು (6), ಏಳು (7), ಎಂಟು (8), ಒಂಬತ್ತು (9), ಹತ್ತು (10)
- ಹನ್ನೊಂದು (11), ಹನ್ನೆರಡು (12), ಹದಿಮೂರು (13), etc.

**Pattern Recognition**:
- "ಪುಟ ೧೨" (Page 12)
- "೧೫ನೇ ಪುಟ" (15th page)
- "Page 25" (English mixed)
- Standalone numbers

## Troubleshooting

### Common Issues

**1. "Python not found" error**
- Install Python 3.7+ from python.org
- Add Python to system PATH

**2. "Module not found" error**
- Run: `pip install -r requirements.txt`
- Ensure virtual environment is activated

**3. "File upload failed"**
- Check file size (max 100MB)
- Ensure file is a valid PDF
- Check available disk space

**4. "PDF processing failed"**
- Ensure PDF is not corrupted
- Try with a different PDF file
- Check if PDF has text content for sorting

**5. "Page sorting not working correctly"**
- PDF may not contain detectable Kannada numerals
- Check if page numbers are in image format (OCR required)
- Manually verify page number patterns

### Performance Tips
- Use smaller PDF files for faster processing
- Close unnecessary browser tabs
- Clear browser cache if experiencing issues
- Restart application for memory cleanup

### Security Considerations
- Don't upload sensitive documents on shared computers
- Clear browser downloads folder regularly
- Use strong passwords for PDF protection
- Application automatically cleans temporary files

## Development

### Running Tests
```bash
python test_toolkit.py
```

### Adding Features
1. Core functionality: Edit `utils/pdf_operations.py`
2. Web interface: Edit `templates/index.html`
3. Styling: Edit `static/css/styles.css`
4. Configuration: Edit `config.py`

### Debugging
1. Enable debug mode in `app.py`: `app.run(debug=True)`
2. Check browser console for JavaScript errors
3. Monitor Flask console for Python errors
4. Use test files for validation

## Maintenance

### Regular Cleanup
- Run `cleanup.bat` to remove temporary files
- Monitor disk space usage
- Clear old log files if any

### Updates
- Update Python packages: `pip install -r requirements.txt --upgrade`
- Test functionality after updates
- Backup configuration before major changes

## Support

For technical issues or feature requests:
1. Check this documentation first
2. Run the test suite: `python test_toolkit.py`
3. Contact the development team with specific error messages
4. Provide sample files that cause issues (if not sensitive)

## License and Credits

**Developed for**: Government of Karnataka - Digital Karnataka Initiative
**Purpose**: Official document processing for government departments
**Language Support**: Kannada (primary), English (technical terms)

This toolkit is specifically designed for Karnataka Government use and includes specialized Kannada language processing capabilities.
