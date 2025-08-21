#!/usr/bin/env python3
"""
Test script for PDF Sorting and Lock Toolkit
Tests basic functionality of all components
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.kannada_numeral_converter import KannadaNumeralConverter
from utils.pdf_operations import PDFOperations
import config

class TestKannadaNumeralConverter(unittest.TestCase):
    def setUp(self):
        self.converter = KannadaNumeralConverter()
    
    def test_kannada_digits_conversion(self):
        """Test conversion of Kannada digits to Arabic"""
        test_text = "೧೨೩"
        result = self.converter.kannada_digits_to_arabic(test_text)
        self.assertEqual(result, "123")
    
    def test_page_number_extraction(self):
        """Test page number extraction from text"""
        test_cases = [
            ("ಪುಟ ೧೨", 12),
            ("Page 25", 25),
            ("೧೫ನೇ ಪುಟ", 15),
            ("ಒಂದು", 1),
            ("ಎರಡು", 2),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.converter.extract_page_number_from_text(text)
                self.assertEqual(result, expected)

class TestConfig(unittest.TestCase):
    def test_config_initialization(self):
        """Test configuration initialization"""
        cfg = config.Config()
        self.assertTrue(hasattr(cfg, 'BASE_DIR'))
        self.assertTrue(hasattr(cfg, 'UPLOAD_FOLDER'))
        self.assertTrue(hasattr(cfg, 'OUTPUT_FOLDER'))
        self.assertTrue(hasattr(cfg, 'MAX_FILE_SIZE'))
        self.assertTrue(hasattr(cfg, 'ALLOWED_EXTENSIONS'))

class TestPDFOperations(unittest.TestCase):
    def setUp(self):
        self.pdf_ops = PDFOperations()
    
    def test_pdf_operations_initialization(self):
        """Test PDF operations initialization"""
        self.assertIsNotNone(self.pdf_ops.config)
    
    @patch('os.path.exists')
    def test_is_pdf_encrypted_file_not_exists(self, mock_exists):
        """Test encryption check with non-existent file"""
        mock_exists.return_value = False
        result = self.pdf_ops.is_pdf_encrypted("nonexistent.pdf")
        self.assertFalse(result)

def run_basic_tests():
    """Run basic functionality tests"""
    print("="*50)
    print("PDF Sorting and Lock Toolkit - Basic Tests")
    print("="*50)
    
    # Test 1: Import all modules
    try:
        from utils.kannada_numeral_converter import KannadaNumeralConverter
        from utils.pdf_operations import PDFOperations
        from utils.file_handler import FileHandler
        import config
        print("✓ All modules imported successfully")
    except ImportError as e:
        print(f"✗ Module import failed: {e}")
        return False
    
    # Test 2: Initialize components
    try:
        converter = KannadaNumeralConverter()
        pdf_ops = PDFOperations()
        cfg = config.Config()
        print("✓ All components initialized successfully")
    except Exception as e:
        print(f"✗ Component initialization failed: {e}")
        return False
    
    # Test 3: Test Kannada numeral conversion
    try:
        test_text = "೧೨೩"
        result = converter.kannada_digits_to_arabic(test_text)
        assert result == "123", f"Expected '123', got '{result}'"
        print("✓ Kannada numeral conversion works")
    except Exception as e:
        print(f"✗ Kannada numeral conversion failed: {e}")
        return False
    
    # Test 4: Test page number extraction
    try:
        result = converter.extract_page_number_from_text("ಪುಟ ೧೨")
        assert result == 12, f"Expected 12, got {result}"
        print("✓ Page number extraction works")
    except Exception as e:
        print(f"✗ Page number extraction failed: {e}")
        return False
    
    # Test 5: Check required directories
    try:
        required_dirs = ['uploads', 'output', 'static', 'templates', 'utils']
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
        print("✓ All required directories exist or created")
    except Exception as e:
        print(f"✗ Directory check failed: {e}")
        return False
    
    # Test 6: Flask app import
    try:
        import app
        print("✓ Flask application can be imported")
    except ImportError as e:
        print(f"✗ Flask application import failed: {e}")
        return False
    
    print("="*50)
    print("All basic tests passed! ✓")
    print("The toolkit should work correctly.")
    print("="*50)
    return True

def run_unit_tests():
    """Run unittest suite"""
    print("Running unit tests...")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestKannadaNumeralConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestPDFOperations))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("PDF Sorting and Lock Toolkit - Test Suite")
    print("========================================")
    
    # Run basic tests first
    basic_success = run_basic_tests()
    
    if basic_success:
        print("\nRunning detailed unit tests...")
        unit_success = run_unit_tests()
        
        if unit_success:
            print("\n🎉 All tests passed! The toolkit is ready to use.")
            print("Run 'python app.py' to start the application.")
        else:
            print("\n⚠️  Some unit tests failed, but basic functionality works.")
    else:
        print("\n❌ Basic tests failed. Please check the installation.")
        sys.exit(1)
