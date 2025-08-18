from flask import Flask, render_template, request, send_from_directory, flash, url_for, jsonify
from datetime import datetime
import os
import logging
from modules.unified_pdf_converter import UnifiedPDFConverter
from modules.legacy_kannada import is_kannada_text
from dotenv import load_dotenv

# Load environment variables explicitly from textUtils/.env (CWD-agnostic)
from pathlib import Path
_BASE = Path(__file__).resolve().parent
load_dotenv((_BASE / ".env").as_posix())

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = os.path.join("static", "converted")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE_MB', '40')) * 1024 * 1024
app.secret_key = os.getenv('SECRET_KEY', 'secret-key-change-in-production')

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Check if request is JSON API call
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return handle_api_request()
        
        # Handle form submission
        pdf_file = request.files.get("pdf")
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        use_google = request.form.get("use_google") == "on"
        force_ocr = request.form.get("force_ocr") == "on"
        debug_mode = request.form.get("debug_mode") == "on"
        mode = request.form.get("mode", "auto")
        store_gcs = request.form.get("store_gcs") == "on"

        # Validate file
        if not pdf_file or pdf_file.filename == '' or not pdf_file.filename.lower().endswith('.pdf'):
            flash("Please upload a valid PDF file.", "error")
            return render_template("index.html")

        try:
            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            safe_filename = "".join(c for c in pdf_file.filename if c.isalnum() or c in '._-')
            input_path = os.path.join(UPLOAD_FOLDER, f"{timestamp}_{safe_filename}")
            
            output_filename = f"{timestamp}.docx"
            output_path = os.path.join(CONVERTED_FOLDER, output_filename)
            txt_filename = f"{timestamp}.txt"
            txt_path = os.path.join(CONVERTED_FOLDER, txt_filename)

            # Save uploaded file
            pdf_file.save(input_path)
            logger.info(f"File uploaded: {input_path}")

            # Convert using unified converter
            converter = UnifiedPDFConverter(
                use_google_vision=use_google,
                debug_mode=debug_mode
            )

            docx_path, txt_path_result, gcs_urls = converter.convert_pdf_to_word(
                input_path,
                output_path,
                txt_path,
                title=title or None,
                author=author or None,
                force_ocr=force_ocr,
                mode=mode,
                store_gcs=store_gcs
            )

            # Validate results
            try:
                with open(txt_path_result, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()

                if not extracted_text.strip():
                    flash("Warning: No text was extracted from the PDF.", "warning")
                elif not is_kannada_text(extracted_text):
                    flash("Warning: No Kannada text detected.", "warning")
                else:
                    flash("PDF successfully converted!", "success")

            except Exception as e:
                logger.warning(f"Could not validate results: {e}")

            # Prepare download links
            local_docx = url_for('download', filename=output_filename)
            local_txt = url_for('download', filename=txt_filename)
            
            template_vars = {
                "download_docx": local_docx,
                "download_txt": local_txt
            }
            
            # Add GCS signed URLs if available
            if gcs_urls:
                template_vars["gcs_docx_url"] = gcs_urls.get('docx')
                template_vars["gcs_txt_url"] = gcs_urls.get('txt')

            return render_template("index.html", **template_vars)

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            flash(f"Conversion failed: {str(e)}", "error")
            return render_template("index.html")

    return render_template("index.html")

def handle_api_request():
    """Handle JSON API requests"""
    try:
        data = request.get_json()
        # TODO: Implement API endpoint for programmatic access
        return jsonify({"error": "API endpoint not yet implemented"}), 501
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download/<path:filename>")
def download(filename):
    return send_from_directory(CONVERTED_FOLDER, filename, as_attachment=True)

@app.errorhandler(413)
def too_large(e):
    max_size = app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
    flash(f"File too large. Maximum size is {max_size}MB.", "error")
    return render_template("index.html"), 413

if __name__ == '__main__':
    logger.info("Starting TextUtils Flask application")
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5001))  # Changed default port to 5001
    app.run(debug=debug_mode, port=port, host='0.0.0.0')