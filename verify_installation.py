#!/usr/bin/env python3
"""
Kannada PDF Toolkit - Installation Verification Script
=====================================================

This script verifies that all required dependencies are properly installed
and configured for the Kannada PDF Toolkit.

Run this script after installing requirements.txt to ensure everything works.

Usage: python verify_installation.py
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_section(title):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print_section("Python Version Check")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_package(package_name, import_name=None, version_attr=None):
    """Check if a Python package is installed and importable"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = importlib.import_module(import_name)
        version = "Unknown"
        
        if version_attr and hasattr(module, version_attr):
            version = getattr(module, version_attr)
        elif hasattr(module, '__version__'):
            version = module.__version__
        
        print_success(f"{package_name} - Version: {version}")
        return True
    except ImportError as e:
        print_error(f"{package_name} - Not installed or import failed: {e}")
        return False

def check_system_dependency(command, name, install_hint=""):
    """Check if a system-level dependency is available"""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print_success(f"{name} - {version}")
            return True
        else:
            print_error(f"{name} - Command failed")
            if install_hint:
                print_warning(f"Install hint: {install_hint}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        print_error(f"{name} - Not found in PATH")
        if install_hint:
            print_warning(f"Install hint: {install_hint}")
        return False

def check_playwright_browsers():
    """Check if Playwright browsers are installed"""
    try:
        result = subprocess.run(['playwright', 'install', '--dry-run'], 
                              capture_output=True, text=True, timeout=30)
        if "chromium" in result.stdout.lower():
            print_success("Playwright - Chromium browser available")
            return True
        else:
            print_warning("Playwright - Chromium browser may not be installed")
            print_warning("Run: playwright install chromium")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        print_error("Playwright - Cannot check browser installation")
        print_warning("Run: playwright install chromium")
        return False

def check_file_permissions():
    """Check file system permissions for required directories"""
    print_section("File System Permissions")
    
    directories = ['uploads', 'output', 'static/previews', 'static/temp', 'logs']
    all_good = True
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            test_file = Path(directory) / 'test_write.tmp'
            test_file.write_text('test')
            test_file.unlink()
            print_success(f"Directory '{directory}' - Read/Write OK")
        except Exception as e:
            print_error(f"Directory '{directory}' - Permission error: {e}")
            all_good = False
    
    return all_good

def check_kannada_font():
    """Check if Kannada fonts are available"""
    print_section("Kannada Font Check")
    
    font_paths = [
        "static/fonts/NotoSansKannada-Regular.ttf",
        "C:/Windows/Fonts/NotoSansKannada-Regular.ttf",
        "/System/Library/Fonts/Supplemental/NotoSansKannada.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf"
    ]
    
    found_font = False
    for font_path in font_paths:
        if os.path.exists(font_path):
            print_success(f"Kannada font found: {font_path}")
            found_font = True
            break
    
    if not found_font:
        print_warning("No Kannada font found in standard locations")
        print_warning("Download Noto Sans Kannada from Google Fonts")
    
    return found_font

def main():
    """Main verification function"""
    print(f"{Colors.BOLD}Kannada PDF Toolkit - Installation Verification{Colors.END}")
    print("=" * 60)
    
    all_checks = []
    
    # Python version
    all_checks.append(check_python_version())
    
    # Core Flask dependencies
    print_section("Core Web Framework")
    core_packages = [
        ('Flask', 'flask'),
        ('Werkzeug', 'werkzeug'),
        ('Jinja2', 'jinja2'),
        ('itsdangerous', 'itsdangerous'),
    ]
    
    for package_name, import_name in core_packages:
        all_checks.append(check_package(package_name, import_name))
    
    # PDF processing libraries
    print_section("PDF Processing Libraries")
    pdf_packages = [
        ('PyMuPDF', 'fitz'),
        ('PyPDF2', 'PyPDF2'),
        ('pypdf', 'pypdf'),
        ('reportlab', 'reportlab'),
        ('pdfplumber', 'pdfplumber'),
    ]
    
    for package_name, import_name in pdf_packages:
        all_checks.append(check_package(package_name, import_name))
    
    # Image processing
    print_section("Image Processing Libraries")
    image_packages = [
        ('Pillow', 'PIL'),
        ('OpenCV', 'cv2'),
        ('pdf2image', 'pdf2image'),
        ('numpy', 'numpy'),
    ]
    
    for package_name, import_name in image_packages:
        all_checks.append(check_package(package_name, import_name))
    
    # OCR libraries
    print_section("OCR Libraries")
    ocr_packages = [
        ('pytesseract', 'pytesseract'),
        ('easyocr', 'easyocr'),
    ]
    
    for package_name, import_name in ocr_packages:
        all_checks.append(check_package(package_name, import_name))
    
    # Browser automation
    print_section("Browser Automation")
    all_checks.append(check_package('Playwright', 'playwright'))
    all_checks.append(check_package('WeasyPrint', 'weasyprint'))
    
    # Language processing
    print_section("Language Processing")
    lang_packages = [
        ('indic-transliteration', 'indic_transliteration'),
        ('langdetect', 'langdetect'),
    ]
    
    for package_name, import_name in lang_packages:
        all_checks.append(check_package(package_name, import_name))
    
    # System dependencies
    print_section("System Dependencies")
    
    # Check Tesseract
    tesseract_hints = {
        'Windows': 'Download from https://github.com/UB-Mannheim/tesseract/wiki',
        'Linux': 'sudo apt install tesseract-ocr tesseract-ocr-kan',
        'Darwin': 'brew install tesseract tesseract-lang'
    }
    platform = sys.platform
    if platform.startswith('win'):
        hint = tesseract_hints['Windows']
    elif platform.startswith('linux'):
        hint = tesseract_hints['Linux']
    elif platform.startswith('darwin'):
        hint = tesseract_hints['Darwin']
    else:
        hint = "Install Tesseract OCR for your platform"
    
    all_checks.append(check_system_dependency('tesseract', 'Tesseract OCR', hint))
    
    # Check Playwright browsers
    all_checks.append(check_playwright_browsers())
    
    # File system checks
    all_checks.append(check_file_permissions())
    
    # Font checks
    all_checks.append(check_kannada_font())
    
    # Summary
    print_section("Installation Summary")
    
    passed = sum(all_checks)
    total = len(all_checks)
    percentage = (passed / total) * 100 if total > 0 else 0
    
    if percentage >= 90:
        print_success(f"Installation Status: {passed}/{total} checks passed ({percentage:.1f}%)")
        print_success("✓ Your Kannada PDF Toolkit installation is ready!")
        print("\nTo start the application, run:")
        print("  python app.py")
    elif percentage >= 70:
        print_warning(f"Installation Status: {passed}/{total} checks passed ({percentage:.1f}%)")
        print_warning("⚠ Some optional components are missing but core functionality should work")
    else:
        print_error(f"Installation Status: {passed}/{total} checks passed ({percentage:.1f}%)")
        print_error("✗ Critical dependencies are missing. Please install missing components.")
    
    print(f"\n{Colors.BOLD}For detailed installation instructions, see README.md{Colors.END}")
    
    return percentage >= 70

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Verification interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Verification failed with error: {e}{Colors.END}")
        sys.exit(1)
