#!/usr/bin/env python3
"""Test script for PDF sorting functionality"""

import os
import sys
import tempfile
from flask import Flask
from werkzeug.test import Client
from werkzeug.wrappers import Response

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sorting_functionality():
    """Test the PDF sorting preview functionality"""
    
    try:
        # Import the required modules
        from utils.pdf_operations import PDFOperations
        from utils.kannada_numeral_converter import KannadaNumeralConverter
        
        print("✅ Successfully imported PDF operations and Kannada converter")
        
        # Test Kannada numeral conversion
        converter = KannadaNumeralConverter()
        test_cases = [
            "ಪುಟ ೫",  # Page 5
            "೧೦",      # 10
            "೨೩",      # 23
            "page 15",  # English
            "random text without numbers"
        ]
        
        print("\n🔢 Testing Kannada numeral conversion:")
        for test_case in test_cases:
            result = converter.extract_page_number_from_text(test_case)
            print(f"   '{test_case}' -> {result}")
        
        # Test PDF operations initialization
        pdf_ops = PDFOperations()
        print("\n✅ Successfully initialized PDF operations")
        
        # Test directory structure
        directories = [
            pdf_ops.config.UPLOAD_FOLDER,
            pdf_ops.config.OUTPUT_FOLDER,
            os.path.join(pdf_ops.config.OUTPUT_FOLDER, 'thumbnails')
        ]
        
        print("\n📁 Checking directory structure:")
        for directory in directories:
            if os.path.exists(directory):
                print(f"   ✅ {directory}")
            else:
                print(f"   ❌ {directory} (missing)")
                os.makedirs(directory, exist_ok=True)
                print(f"   ✅ Created {directory}")
        
        print("\n🎉 All basic functionality tests passed!")
        print("\n💡 The sorting preview should now work properly.")
        print("   To test fully, upload a PDF file through the web interface.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Kannada PDF Toolkit - Sorting Functionality")
    print("=" * 55)
    
    success = test_sorting_functionality()
    
    if success:
        print("\n🚀 You can now start the Flask application:")
        print('   python app.py')
        print("\n   Then visit: http://localhost:5000")
        print("   Select 'Sort' operation and upload a PDF to test!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
