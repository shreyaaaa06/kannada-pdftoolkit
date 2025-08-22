import os
import threading
import platform
import time

def test_docx2pdf_direct():
    """Test docx2pdf directly without threading"""
    try:
        import docx2pdf
        print("✓ docx2pdf imported")
        
        # Initialize COM
        if platform.system() == "Windows":
            import pythoncom
            pythoncom.CoInitialize()
            print("✓ COM initialized in main thread")
        
        # Find a test Word file (use any .docx file in uploads folder)
        uploads_dir = "uploads"
        test_file = None
        
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                if filename.endswith('.docx'):
                    test_file = os.path.join(uploads_dir, filename)
                    break
        
        if not test_file:
            print("❌ No .docx file found in uploads folder for testing")
            print("Please upload a Word file first to test conversion")
            return False
        
        print(f"Testing with file: {test_file}")
        
        # Create output path
        output_file = "test_output.pdf"
        if os.path.exists(output_file):
            os.remove(output_file)
        
        print("Starting docx2pdf conversion...")
        
        # Direct conversion (no threading)
        docx2pdf.convert(test_file, output_file)
        
        # Check result
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            size = os.path.getsize(output_file)
            print(f"✓ Direct conversion successful: {size} bytes")
            os.remove(output_file)  # Clean up
            return True
        else:
            print("✗ Direct conversion failed - no output file")
            return False
            
    except Exception as e:
        print(f"✗ Direct conversion error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if platform.system() == "Windows":
            try:
                import pythoncom
                pythoncom.CoUninitialize()
                print("✓ COM uninitialized in main thread")
            except:
                pass

def test_docx2pdf_threaded():
    """Test docx2pdf with threading (like your actual code)"""
    try:
        import docx2pdf
        
        # Find test file
        uploads_dir = "uploads"
        test_file = None
        
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                if filename.endswith('.docx'):
                    test_file = os.path.join(uploads_dir, filename)
                    break
        
        if not test_file:
            print("❌ No .docx file found for threaded testing")
            return False
        
        print(f"Testing threaded conversion with: {test_file}")
        
        output_file = "test_output_threaded.pdf"
        if os.path.exists(output_file):
            os.remove(output_file)
        
        conversion_result = {'success': False, 'error': None}
        
        def convert_worker():
            """Worker thread function (exactly like your code)"""
            try:
                # Initialize COM in this thread
                if platform.system() == "Windows":
                    import pythoncom
                    pythoncom.CoInitialize()
                    print("✓ COM initialized in worker thread")
                
                # Perform conversion
                docx2pdf.convert(test_file, output_file)
                
                # Check result
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    conversion_result['success'] = True
                    print(f"✓ Threaded conversion successful: {os.path.getsize(output_file)} bytes")
                else:
                    conversion_result['error'] = "No output file created"
                    print("✗ Threaded conversion failed - no output")
                
            except Exception as e:
                conversion_result['error'] = str(e)
                print(f"✗ Worker thread error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # Clean up COM
                if platform.system() == "Windows":
                    try:
                        import pythoncom
                        pythoncom.CoUninitialize()
                        print("✓ COM uninitialized in worker thread")
                    except:
                        pass
        
        # Run in thread
        thread = threading.Thread(target=convert_worker)
        thread.daemon = True
        thread.start()
        thread.join(timeout=60)  # 1 minute timeout
        
        if thread.is_alive():
            print("✗ Threaded conversion timed out")
            return False
        
        # Clean up test file
        if os.path.exists(output_file):
            os.remove(output_file)
        
        return conversion_result['success']
        
    except Exception as e:
        print(f"✗ Threaded test setup error: {e}")
        return False

def find_word_installation():
    possible_paths = [
        r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\Office16\WINWORD.EXE",
        r"C:\Program Files\Microsoft Office\Office15\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\Office15\WINWORD.EXE",
        r"C:\Program Files\Microsoft Office\Office14\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\Office14\WINWORD.EXE",
    ]
    
    print("Searching for Microsoft Word...")
    found_paths = []
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✓ Found Word at: {path}")
            found_paths.append(path)
    
    # Try to find via registry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Winword.exe")
        word_path, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        print(f"✓ Found Word via registry: {word_path}")
        if word_path not in found_paths:
            found_paths.append(word_path)
    except Exception as e:
        print(f"✗ Registry lookup failed: {e}")
    
    return found_paths[0] if found_paths else None

if __name__ == "__main__":
    print("=== Microsoft Word Installation Check ===")
    find_word_installation()
    
    print("\n=== Testing docx2pdf Direct Conversion ===")
    direct_success = test_docx2pdf_direct()
    
    print("\n=== Testing docx2pdf Threaded Conversion ===")
    threaded_success = test_docx2pdf_threaded()
    
    print("\n=== SUMMARY ===")
    print(f"Direct conversion: {'✓ SUCCESS' if direct_success else '✗ FAILED'}")
    print(f"Threaded conversion: {'✓ SUCCESS' if threaded_success else '✗ FAILED'}")
    
    if direct_success and not threaded_success:
        print("\n💡 SOLUTION: Use direct conversion instead of threading")
    elif not direct_success and not threaded_success:
        print("\n💡 SOLUTION: Use fallback method (ReportLab) - Word COM may have permissions issues")