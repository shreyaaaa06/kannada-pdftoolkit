"""
Font Manager for Kannada Support
Handles downloading and managing Kannada fonts for watermarks
"""

import os
import requests
import tempfile
from pathlib import Path

class KannadaFontManager:
    """Manages Kannada fonts for PDF watermarks"""
    
    def __init__(self):
        self.fonts_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')
        os.makedirs(self.fonts_dir, exist_ok=True)
        
    def get_kannada_font_path(self):
        """Get path to a Kannada font, downloading if necessary"""
        
        # Check system fonts first
        system_fonts = [
            r"C:\Windows\Fonts\NotoSansKannada-Regular.ttf",
            r"C:\Windows\Fonts\Tunga.ttf",
            r"C:\Windows\Fonts\Kedage.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf",  # Linux
            "/System/Library/Fonts/Helvetica.ttc"  # Mac fallback
        ]
        
        for font_path in system_fonts:
            if os.path.exists(font_path):
                return font_path
        
        local_font = os.path.join(self.fonts_dir, "NotoSansKannada-Regular.ttf")
        if os.path.exists(local_font):
            return local_font
            
        try:
            font_url = "https://fonts.gstatic.com/s/notosanskannada/v26/Yq6R-LCAWCX3-6lKHYhMW5rptlRlIVPO.ttf"
            
            response = requests.get(font_url, timeout=30)
            response.raise_for_status()
            
            with open(local_font, 'wb') as f:
                f.write(response.content)
                
            return local_font
            
        except Exception as e:
            return None
    
    def is_kannada_text(self, text):
        """Check if text contains Kannada characters"""
        return any('\u0c80' <= char <= '\u0cff' for char in text)
    
    def get_font_for_text(self, text):
        """Get appropriate font based on text content"""
        if self.is_kannada_text(text):
            return self.get_kannada_font_path()
        return None  # Use default font for non-Kannada text
