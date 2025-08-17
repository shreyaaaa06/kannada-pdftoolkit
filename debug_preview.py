#!/usr/bin/env python3
"""
Debug Preview Issues - Comprehensive Test
"""

import os
import sys
import tempfile
import requests
from io import BytesIO

def create_test_pdf():
    """Create a simple test PDF with Kannada content"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create a simple PDF in memory
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Add some content with Kannada page numbers
        p.drawString(100, 750, "Test PDF Page 1")
        p.drawString(100, 700, "ಪುಟ ೧")  # Kannada for "Page 1"
        p.showPage()
        
        p.drawString(100, 750, "Test PDF Page 2") 
        p.drawString(100, 700, "ಪುಟ ೨")  # Kannada for "Page 2"
        p.showPage()
        
        p.save()
        buffer.seek(0)
        return buffer
        
    except ImportError:
        print("⚠️ ReportLab not available, cannot create test PDF")
        return None
    except Exception as e:
        print(f"❌ Error creating test PDF: {e}")
        return None

def test_sort_preview_api():
    """Test the sort preview API directly"""
    print("🧪 Testing Sort Preview API...")
    
    try:
        # Create test PDF
        pdf_buffer = create_test_pdf()
        if not pdf_buffer:
            print("   ❌ Could not create test PDF")
            return False
        
        # Test the API endpoint
        files = {'file': ('test.pdf', pdf_buffer, 'application/pdf')}
        
        response = requests.post(
            'http://localhost:5000/generate-sort-preview',
            files=files,
            timeout=30
        )
        
        print(f"   📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Response Data: {data}")
            
            if data.get('success'):
                print("   ✅ API returns success")
                print(f"   📄 Total Pages: {data.get('total_pages', 'Unknown')}")
                print(f"   🔍 Previews Count: {len(data.get('previews', []))}")
                print(f"   📋 Sorted Order Count: {len(data.get('sorted_order', []))}")
                
                # Check preview data structure
                previews = data.get('previews', [])
                if previews:
                    first_preview = previews[0]
                    print(f"   🔍 First Preview Sample: {first_preview}")
                
                return True
            else:
                print(f"   ❌ API returns error: {data.get('error')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to Flask app (is it running?)")
        return False
    except Exception as e:
        print(f"   ❌ API Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_operations():
    """Test PDF operations directly"""
    print("\n🔧 Testing PDF Operations...")
    
    try:
        from utils.pdf_operations import PDFOperations
        from utils.kannada_numeral_converter import KannadaNumeralConverter
        
        # Test converter
        converter = KannadaNumeralConverter()
        test_cases = [
            ("ಪುಟ ೧", 1),
            ("ಪುಟ ೨", 2), 
            ("page 5", 5),
            ("random text", None)
        ]
        
        print("   🔤 Testing Kannada Converter:")
        for text, expected in test_cases:
            result = converter.extract_page_number_from_text(text)
            status = "✅" if result == expected else "❌"
            print(f"      {status} '{text}' → {result} (expected {expected})")
        
        # Test PDF operations
        pdf_ops = PDFOperations()
        print("   ✅ PDF Operations initialized")
        
        return True
        
    except Exception as e:
        print(f"   ❌ PDF Operations Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_directory_structure():
    """Test directory structure"""
    print("\n📁 Testing Directory Structure...")
    
    try:
        import config
        conf = config.Config()
        
        directories = [
            ('Upload', conf.UPLOAD_FOLDER),
            ('Output', conf.OUTPUT_FOLDER),
            ('Thumbnails', os.path.join(conf.OUTPUT_FOLDER, 'thumbnails'))
        ]
        
        for name, path in directories:
            if os.path.exists(path):
                print(f"   ✅ {name}: {path}")
            else:
                print(f"   ❌ {name}: {path} (missing)")
                try:
                    os.makedirs(path, exist_ok=True)
                    print(f"   ✅ Created: {path}")
                except Exception as e:
                    print(f"   ❌ Failed to create {path}: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Directory Test Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Comprehensive Preview Debug Test")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    if test_directory_structure():
        success_count += 1
    
    if test_pdf_operations():
        success_count += 1
        
    if test_sort_preview_api():
        success_count += 1
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Preview should work.")
        print("\n💡 If preview still doesn't work in browser:")
        print("   1. Check browser console for JavaScript errors")
        print("   2. Ensure you're clicking 'Sort Pages' operation first")
        print("   3. Upload a PDF file")
        print("   4. Click the 'Preview' button")
    else:
        print("❌ Some tests failed. Check the errors above.")
