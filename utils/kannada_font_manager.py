"""
Enhanced Kannada Font Manager for PDF Toolkit
Automatically downloads and manages high-quality Kannada fonts for optimal PDF rendering
"""

import os
import urllib.request
import tempfile
import shutil
from pathlib import Path

class KannadaFontManager:
    """Manages Kannada fonts for optimal PDF rendering with WeasyPrint"""
    
    def __init__(self):
        self.fonts_dir = os.path.join(os.getcwd(), 'static', 'fonts')
        self.temp_dir = tempfile.gettempdir()
        
        # High-quality Kannada fonts with download URLs
        self.font_sources = {
            'noto_sans_kannada': {
                'name': 'Noto Sans Kannada',
                'filename': 'NotoSansKannada-Regular.ttf',
                'url': 'https://github.com/notofonts/kannada/raw/main/fonts/NotoSansKannada/hinted/ttf/NotoSansKannada-Regular.ttf',
                'fallback_url': 'https://fonts.gstatic.com/s/notosanskannada/v26/Yq6R-LCAWCX3-6Ky7FAFnOZwkwgtTZ-bdQ.ttf',
                'priority': 1
            },
            'baloo_tamma_2': {
                'name': 'Baloo Tamma 2',
                'filename': 'BalooTamma2-Regular.ttf',
                'url': 'https://fonts.gstatic.com/s/balootamma2/v7/vEFA2_hBT3UWKGVtTG1OIel-U2j_TjZDnA.ttf',
                'priority': 2
            },
            'hind_mysuru': {
                'name': 'Hind Mysuru',
                'filename': 'HindMysuru-Regular.ttf',
                'url': 'https://fonts.gstatic.com/s/hindmysuru/v12/MCoUzAL91sNO3d-B7BB5YPCJ3Z9aw_w.ttf',
                'priority': 3
            },
            'mukti_narrow': {
                'name': 'Mukti Narrow',
                'filename': 'MuktiNarrow.ttf',
                'url': 'https://github.com/MihailJP/muktinarrow/raw/master/MuktiNarrow.ttf',
                'priority': 4
            }
        }
        
        # System font locations (Windows/Linux/Mac)
        self.system_font_paths = [
            # Windows
            r"C:\Windows\Fonts\NotoSansKannada-Regular.ttf",
            r"C:\Windows\Fonts\tunga.ttf",
            r"C:\Windows\Fonts\Kalinga.ttf",
            r"C:\Windows\Fonts\BalooTamma2-Regular.ttf",
            # Linux
            "/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf",
            "/usr/share/fonts/truetype/kannada/lohit_kn.ttf",
            "/usr/share/fonts/truetype/kannada/KannadaWin95.ttf",
            # User fonts directory
            os.path.expanduser("~/.fonts/NotoSansKannada-Regular.ttf"),
            # Project fonts directory
            os.path.join(self.fonts_dir, 'NotoSansKannada-Regular.ttf'),
            os.path.join(self.fonts_dir, 'BalooTamma2-Regular.ttf'),
            os.path.join(self.fonts_dir, 'tunga.ttf')
        ]
    
    def ensure_fonts_directory(self):
        """Create fonts directory if it doesn't exist"""
        try:
            os.makedirs(self.fonts_dir, exist_ok=True)
            return True
        except Exception as e:
            print(f"⚠️ Could not create fonts directory: {e}")
            return False
    
    def find_system_fonts(self):
        """Find existing Kannada fonts on the system"""
        found_fonts = []
        
        for font_path in self.system_font_paths:
            if os.path.exists(font_path):
                try:
                    # Verify it's a valid font file
                    file_size = os.path.getsize(font_path)
                    if file_size > 1024:  # At least 1KB
                        found_fonts.append({
                            'path': font_path,
                            'name': os.path.basename(font_path),
                            'size': file_size
                        })
                        print(f"✓ Found system font: {font_path}")
                except Exception as e:
                    print(f"⚠️ Error checking font {font_path}: {e}")
        
        return found_fonts
    
    def download_font(self, font_key, force_download=False):
        """Download a specific Kannada font"""
        if font_key not in self.font_sources:
            print(f"❌ Unknown font key: {font_key}")
            return None
        
        font_info = self.font_sources[font_key]
        
        # Check multiple possible locations
        possible_paths = [
            os.path.join(self.fonts_dir, font_info['filename']),
            os.path.join(self.temp_dir, font_info['filename'])
        ]
        
        # Check if font already exists
        if not force_download:
            for path in possible_paths:
                if os.path.exists(path) and os.path.getsize(path) > 1024:
                    print(f"✓ Font already available: {font_info['name']} at {path}")
                    return path
        
        # Try to download to fonts directory first, then temp
        self.ensure_fonts_directory()
        
        for target_path in possible_paths:
            try:
                print(f"📥 Downloading {font_info['name']}...")
                
                # Try primary URL first
                try:
                    urllib.request.urlretrieve(font_info['url'], target_path)
                except Exception as primary_error:
                    print(f"⚠️ Primary URL failed: {primary_error}")
                    # Try fallback URL if available
                    if 'fallback_url' in font_info:
                        print(f"🔄 Trying fallback URL...")
                        urllib.request.urlretrieve(font_info['fallback_url'], target_path)
                    else:
                        raise primary_error
                
                # Verify download
                if os.path.exists(target_path) and os.path.getsize(target_path) > 1024:
                    print(f"✅ Successfully downloaded {font_info['name']} to {target_path}")
                    return target_path
                else:
                    print(f"❌ Downloaded file is invalid: {target_path}")
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    
            except Exception as e:
                print(f"⚠️ Failed to download to {target_path}: {e}")
                continue
        
        print(f"❌ Failed to download {font_info['name']}")
        return None
    
    def download_all_fonts(self, force_download=False):
        """Download all available Kannada fonts"""
        print("🚀 Setting up Kannada fonts for optimal PDF rendering...")
        
        downloaded_fonts = []
        
        # Sort fonts by priority
        sorted_fonts = sorted(self.font_sources.items(), key=lambda x: x[1]['priority'])
        
        for font_key, font_info in sorted_fonts:
            try:
                font_path = self.download_font(font_key, force_download)
                if font_path:
                    downloaded_fonts.append({
                        'key': font_key,
                        'name': font_info['name'],
                        'path': font_path,
                        'priority': font_info['priority']
                    })
            except Exception as e:
                print(f"⚠️ Error with font {font_info['name']}: {e}")
                continue
        
        return downloaded_fonts
    
    def get_best_available_font(self):
        """Get the best available Kannada font for PDF generation"""
        print("🔍 Finding best available Kannada font...")
        
        # First check system fonts
        system_fonts = self.find_system_fonts()
        
        # Check for high-priority fonts first
        priority_fonts = [
            'NotoSansKannada-Regular.ttf',
            'BalooTamma2-Regular.ttf',
            'tunga.ttf',
            'Kalinga.ttf'
        ]
        
        for priority_font in priority_fonts:
            for system_font in system_fonts:
                if priority_font.lower() in system_font['name'].lower():
                    print(f"🎯 Best system font found: {system_font['name']}")
                    return system_font['path']
        
        # If no good system font, try downloading
        downloaded_fonts = self.download_all_fonts()
        
        if downloaded_fonts:
            best_font = min(downloaded_fonts, key=lambda x: x['priority'])
            print(f"🎯 Best downloaded font: {best_font['name']}")
            return best_font['path']
        
        # Fallback to any system font
        if system_fonts:
            fallback_font = system_fonts[0]
            print(f"⚠️ Using fallback font: {fallback_font['name']}")
            return fallback_font['path']
        
        print("❌ No suitable Kannada fonts found!")
        return None
    
    def generate_font_css(self, font_path, font_family_name="KannadaPrimary"):
        """Generate CSS for the given font"""
        if not font_path or not os.path.exists(font_path):
            return ""
        
        # Convert path for CSS (handle Windows paths)
        css_path = font_path.replace('\\', '/')
        
        css = f"""
        @font-face {{
            font-family: '{font_family_name}';
            src: url('file:///{css_path}') format('truetype');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
        }}
        """
        
        return css
    
    def get_font_fallback_list(self):
        """Get a comprehensive font fallback list for Kannada"""
        return [
            'KannadaPrimary',
            'Noto Sans Kannada',
            'Baloo Tamma 2', 
            'Hind Mysuru',
            'Tunga',
            'Kalinga',
            'Lohit Kannada',
            'Kedage',
            'Sampige',
            'sans-serif'
        ]

def setup_kannada_fonts():
    """Convenience function to setup Kannada fonts"""
    font_manager = KannadaFontManager()
    best_font = font_manager.get_best_available_font()
    
    return {
        'font_path': best_font,
        'font_css': font_manager.generate_font_css(best_font),
        'fallback_list': font_manager.get_font_fallback_list(),
        'manager': font_manager
    }

if __name__ == "__main__":
    # Test the font manager
    print("🧪 Testing Kannada Font Manager...")
    setup_result = setup_kannada_fonts()
    
    if setup_result['font_path']:
        print(f"✅ Setup successful! Best font: {setup_result['font_path']}")
        print(f"📝 CSS generated: {len(setup_result['font_css'])} characters")
        print(f"🔗 Fallback fonts: {', '.join(setup_result['fallback_list'][:5])}...")
    else:
        print("❌ Setup failed - no fonts available")
