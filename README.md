# PDF Sorting and Lock Toolkit

This is a specialized toolkit focused on two core PDF operations:
1. **Page Sorting by Kannada Numerals** - Automatically detect and sort PDF pages based on Kannada page numbers
2. **PDF Password Protection/Unlock** - Add password protection to PDFs or unlock password-protected PDFs

## Features

### 🔢 Page Sorting
- Detects Kannada numerals and page numbers in PDF text
- Automatically sorts pages in the correct numerical order
- Provides visual preview of original vs sorted page order
- Supports both Kannada digits (೦೧೨೩...) and Kannada number words (ಒಂದು, ಎರಡು, ಮೂರು...)

### 🔒 PDF Protection
- Add password protection to PDF files
- Multiple encryption levels supported
- Secure password validation with confirmation
- Uses PyPDF2 and PyMuPDF for maximum compatibility

### 🔓 PDF Unlock
- Remove password protection from PDFs
- Automatic encryption detection
- Support for various PDF encryption methods
- Secure password handling

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Usage

### Page Sorting
1. Select the "ಪುಟ ಸಾರಿಸುವಿಕೆ" tab
2. Upload your PDF file
3. Review the preview showing original vs sorted order
4. Click "ಪುಟಗಳನ್ನು ಸಾರಿಸಿ" to process
5. Download the sorted PDF

### PDF Protection
1. Select the "PDF ರಕ್ಷಣೆ" tab
2. Upload your PDF file
3. Enter a password (minimum 6 characters)
4. Confirm the password
5. Click "PDF ರಕ್ಷಿಸಿ" to process
6. Download the protected PDF

### PDF Unlock
1. Select the "PDF ಅನ್‌ಲಾಕ್" tab
2. Upload your password-protected PDF file
3. The system will detect if the PDF is encrypted
4. Enter the PDF password
5. Click "PDF ಅನ್‌ಲಾಕ್ ಮಾಡಿ" to process
6. Download the unlocked PDF

## Technical Details

### Dependencies
- Flask 2.3.3 - Web framework
- PyPDF2 3.0.1 - PDF manipulation
- PyMuPDF 1.23.5 - PDF processing and rendering
- Pillow 10.0.1 - Image processing for thumbnails
- python-docx 0.8.11 - Document processing
- reportlab 4.0.4 - PDF generation

### File Structure
```
sorting_lock_toolkit/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── utils/
│   ├── __init__.py
│   ├── file_handler.py   # File upload/management utilities
│   ├── pdf_operations.py # PDF processing operations
│   └── kannada_numeral_converter.py # Kannada number detection
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── css/
│   │   └── styles.css    # Custom styling
│   └── uploads/          # Temporary file storage
├── uploads/              # File upload directory
└── output/               # Processed file output
```

### Kannada Numeral Detection
The toolkit recognizes:
- Kannada digits: ೦೧೨೩೪೫೬೭೮೯
- Kannada number words: ಒಂದು, ಎರಡು, ಮೂರು, ನಾಲ್ಕು, ಐದು, etc.
- Page patterns: "ಪುಟ 123", "123ನೇ ಪುಟ", standalone numbers

### Security Features
- Secure file handling with proper validation
- Password strength requirements (minimum 6 characters)
- Session-based file management
- Automatic cleanup of temporary files
- Input sanitization and validation

## Browser Support
- Modern browsers with JavaScript enabled
- Responsive design for mobile devices
- Accessibility features for screen readers

## Language Support
- Primary interface in Kannada
- English technical terms where appropriate
- Unicode support for Kannada text processing

## File Limits
- Maximum file size: 100MB
- Supported formats: PDF only
- Session-based processing with automatic cleanup

## Development

### Local Development
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python app.py`
4. Access at: `http://localhost:5000`

### Deployment
- Configure production WSGI server (gunicorn, uwsgi)
- Set appropriate file upload limits
- Configure secure secret key
- Set up proper logging and monitoring

## Contributing
This toolkit is designed for Karnataka Government use. For contributions or issues, please follow the established development guidelines.

## License
Government of Karnataka - Digital Karnataka Initiative

## Support
For technical support or feature requests, contact the Digital Karnataka team.
