import pdfkit

try:
    # Test with simple HTML
    simple_html = "<html><body><h1>Test</h1></body></html>"
    pdfkit.from_string(simple_html, "test.pdf")
    print("✓ wkhtmltopdf is working!")
except Exception as e:
    print(f"Error: {e}")