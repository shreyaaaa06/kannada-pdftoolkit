import os
import fitz
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import config

class PDFOperations:
    def __init__(self):
        self.config = config.Config()
    
    def sort_pdf_by_page_numbers(self, file_path, session_id, pages=""):
        """Sort PDF pages by detected Kannada page numbers"""
        try:
            from .kannada_numeral_converter import KannadaNumeralConverter
            
            converter = KannadaNumeralConverter()
            doc = fitz.open(file_path)
            
            page_data = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                extracted_number = converter.extract_page_number_from_text(text)
                
                page_data.append({
                    'page': page,
                    'original_num': page_num + 1,
                    'extracted_num': extracted_number if extracted_number else page_num + 1
                })
            
            page_data.sort(key=lambda x: x['extracted_num'])
            
            output_filename = f"{session_id}_sortedbynum.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            new_doc = fitz.open()
            for data in page_data:
                new_doc.insert_pdf(doc, from_page=data['original_num']-1, to_page=data['original_num']-1)
            
            new_doc.save(output_path)
            new_doc.close()
            doc.close()
            
            return output_path
            
        except Exception as e:
            raise Exception(f"ಪುಟ ಸಾರಿಸುವಿಕೆ ವಿಫಲ: {str(e)}")

    def get_page_sorting_preview(self, file_path, session_id):
        """Generate preview for page sorting"""
        try:
            from .kannada_numeral_converter import KannadaNumeralConverter
            
            converter = KannadaNumeralConverter()
            doc = fitz.open(file_path)
            
            previews = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                extracted_number = converter.extract_page_number_from_text(text)
                
                thumbnail_path = self._generate_page_thumbnail(page, page_num + 1, session_id)
                
                previews.append({
                    'page_num': page_num + 1,
                    'extracted_number': extracted_number if extracted_number else page_num + 1,
                    'thumbnail_path': thumbnail_path
                })
            
            # Sort previews by extracted number to show the expected order
            sorted_previews = sorted(previews, key=lambda x: x['extracted_number'])
            
            # For the sorted_order, we need to return the sorted preview objects with proper field names
            sorted_order = []
            for preview in sorted_previews:
                sorted_order.append({
                    'page_num': preview['page_num'],
                    'extracted_number': preview['extracted_number'],
                    'thumbnail_path': preview['thumbnail_path']
                })
            
            doc.close()
            
            return {
                'total_pages': len(previews),
                'previews': previews,
                'sorted_order': sorted_order
            }
            
        except Exception as e:
            return {'error': f'ಪೂರ್ವವೀಕ್ಷಣೆ ರಚನೆ ವಿಫಲ: {str(e)}'}

    def _generate_page_thumbnail(self, page, page_num, session_id):
        """Generate a thumbnail image for a PDF page with automatic orientation detection"""
        try:
            import os
            from PIL import Image
            import io
            
            thumbnails_dir = os.path.join(self.config.OUTPUT_FOLDER, 'thumbnails', session_id)
            os.makedirs(thumbnails_dir, exist_ok=True)
            
            import time
            timestamp = int(time.time() * 1000)
            thumbnail_filename = f"page_{page_num}_{timestamp}.png"
            thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
            
            zoom = 1.5
            mat = fitz.Matrix(zoom, zoom)
            
            # Get page dimensions for orientation detection
            rect = page.rect
            page_width = rect.width
            page_height = rect.height
            
            # Automatically detect if page needs rotation
            if page_width > page_height:
                # Landscape page - might need rotation for better thumbnail
                mat = mat * fitz.Matrix(1, 1)  # Keep original orientation for now
            
            # Generate pixmap with the transformation matrix
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Load with PIL for additional processing
            img = Image.open(io.BytesIO(img_data))
            
            # Resize to thumbnail size while maintaining aspect ratio
            thumbnail_size = (200, 280)  # Width x Height for portrait orientation
            img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            
            # Save the thumbnail
            img.save(thumbnail_path, "PNG", optimize=True)
            
            return f"/thumbnails/{session_id}/{thumbnail_filename}"
            
        except Exception as e:
            print(f"Thumbnail generation error: {str(e)}")
            return None

    def protect_pdf(self, file_path, session_id, protection_options):
        """Protect PDF with password and permissions using PyPDF2 for better compatibility"""
        try:
            # Validate protection options
            password = protection_options.get('protection_password', '')
            if len(password) < 6:
                raise Exception('ಪಾಸ್‌ವರ್ಡ್ ಕನಿಷ್ಠ 6 ಅಕ್ಷರಗಳು ಇರಬೇಕು')
            
            confirm_password = protection_options.get('confirm_password', '')
            if password != confirm_password:
                raise Exception('ಪಾಸ್‌ವರ್ಡ್‌ಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ')
            
            output_filename = f"{session_id}_protected.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            # Try PyPDF2 method first (more reliable for password protection)
            try:
                from PyPDF2 import PdfReader, PdfWriter
                
                # Read the source PDF
                reader = PdfReader(file_path)
                writer = PdfWriter()
                
                # Copy all pages
                for page in reader.pages:
                    writer.add_page(page)
                
                # Set password protection
                user_password = password
                owner_password = password
                
                # Apply encryption with password
                writer.encrypt(
                    user_password=user_password,
                    owner_password=owner_password,
                    use_128bit=True
                )
                
                # Save the protected PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                print(f"PyPDF2 method successful: {output_path}")
                
            except Exception as pypdf2_error:
                print(f"PyPDF2 method failed: {pypdf2_error}")
                
                # Fallback to PyMuPDF with minimal encryption
                doc = fitz.open(file_path)
                
                # Use only basic password protection without complex permissions
                doc.save(
                    output_path,
                    encryption=1,  # Use basic RC4 encryption for compatibility
                    owner_pw=password,
                    user_pw=password
                    # No permissions parameter to avoid corruption
                )
                doc.close()
                print(f"PyMuPDF fallback method used: {output_path}")
            
            # Verify the output file was created properly
            if not os.path.exists(output_path):
                raise Exception('ಔಟ್‌ಪುಟ್ ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ')
            
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise Exception('ಖಾಲಿ ಫೈಲ್ ರಚಿಸಲಾಗಿದೆ')
            
            print(f"Protected PDF created successfully: {file_size} bytes")
            
            return {
                'success': True,
                'output_path': output_path,
                'filename': output_filename,
                'message': f'PDF ಯಶಸ್ವಿಯಾಗಿ ರಕ್ಷಿಸಲಾಗಿದೆ - ಪಾಸ್‌ವರ್ಡ್ ಅಗತ್ಯ'
            }
            
        except Exception as e:
            print(f"Protection error: {str(e)}")
            return {'success': False, 'error': f'PDF ರಕ್ಷಣೆ ವಿಫಲ: {str(e)}'}

    def unlock_pdf(self, file_path, session_id, password):
        """Unlock a password-protected PDF"""
        try:
            if not password:
                raise Exception('PDF ಅನ್‌ಲಾಕ್ ಮಾಡಲು ಪಾಸ್‌ವರ್ಡ್ ಅಗತ್ಯ')
            
            output_filename = f"{session_id}_unlocked.pdf"
            output_path = os.path.join(self.config.OUTPUT_FOLDER, output_filename)
            
            # Try PyPDF2 method first
            try:
                from PyPDF2 import PdfReader, PdfWriter
                
                # Read the protected PDF
                reader = PdfReader(file_path)
                
                # Check if PDF is encrypted
                if not reader.is_encrypted:
                    raise Exception('PDF ಈಗಾಗಲೇ ಅನ್‌ಲಾಕ್ ಆಗಿದೆ')
                
                # Try to decrypt with password
                if not reader.decrypt(password):
                    raise Exception('ತಪ್ಪಾದ ಪಾಸ್‌ವರ್ಡ್')
                
                # Create new PDF without password protection
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                
                # Save unlocked PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                print(f"PyPDF2 unlock successful: {output_path}")
                
            except Exception as pypdf2_error:
                print(f"PyPDF2 unlock failed: {pypdf2_error}")
                
                # Fallback to PyMuPDF
                doc = fitz.open(file_path)
                
                # Check if document needs authentication
                if doc.needs_pass:
                    # Try to authenticate with password
                    if not doc.authenticate(password):
                        doc.close()
                        raise Exception('ತಪ್ಪಾದ ಪಾಸ್‌ವರ್ಡ್')
                
                # Save unlocked version
                doc.save(output_path)
                doc.close()
                print(f"PyMuPDF unlock successful: {output_path}")
            
            # Verify the output file was created properly
            if not os.path.exists(output_path):
                raise Exception('ಔಟ್‌ಪುಟ್ ಫೈಲ್ ರಚಿಸಲಾಗಿಲ್ಲ')
            
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                raise Exception('ಖಾಲಿ ಫೈಲ್ ರಚಿಸಲಾಗಿದೆ')
            
            return {
                'success': True,
                'output_path': output_path,
                'filename': output_filename,
                'message': 'PDF ಯಶಸ್ವಿಯಾಗಿ ಅನ್‌ಲಾಕ್ ಆಗಿದೆ'
            }
            
        except Exception as e:
            print(f"Unlock error: {str(e)}")
            return {'success': False, 'error': f'PDF ಅನ್‌ಲಾಕ್ ವಿಫಲ: {str(e)}'}

    def is_pdf_encrypted(self, file_path):
        """Check if PDF is password protected"""
        try:
            # Try PyPDF2 first
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(file_path)
                return reader.is_encrypted
            except:
                pass
            
            # Fallback to PyMuPDF
            doc = fitz.open(file_path)
            needs_password = doc.needs_pass
            doc.close()
            return needs_password
            
        except Exception as e:
            print(f"Error checking encryption: {str(e)}")
            return False
