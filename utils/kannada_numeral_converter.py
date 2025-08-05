import re

class KannadaNumeralConverter:
    def __init__(self):
        # Kannada to Arabic number mapping
        self.kannada_digits = {
            '೦': '0', '೧': '1', '೨': '2', '೩': '3', '೪': '4',
            '೫': '5', '೬': '6', '೭': '7', '೮': '8', '೯': '9'
        }
        
        # Kannada number words to Arabic numbers
        self.kannada_words = {
            'ಒಂದು': 1, 'ಎರಡು': 2, 'ಮೂರು': 3, 'ನಾಲ್ಕು': 4, 'ಐದು': 5,
            'ಆರು': 6, 'ಏಳು': 7, 'ಎಂಟು': 8, 'ಒಂಬತ್ತು': 9, 'ಹತ್ತು': 10,
            'ಹನ್ನೊಂದು': 11, 'ಹನ್ನೆರಡು': 12, 'ಹದಿಮೂರು': 13, 'ಹದಿನಾಲ್ಕು': 14,
            'ಹದಿನೈದು': 15, 'ಹದಿನಾರು': 16, 'ಹದಿನೇಳು': 17, 'ಹದಿನೆಂಟು': 18,
            'ಹದಿನೊಂಬತ್ತು': 19, 'ಇಪ್ಪತ್ತು': 20
        }
    
    def kannada_digits_to_arabic(self, text):
        """Convert Kannada digits to Arabic digits"""
        for kannada_digit, arabic_digit in self.kannada_digits.items():
            text = text.replace(kannada_digit, arabic_digit)
        return text
    
    def find_page_number_in_text(self, text):
        """Extract page number from text content"""
        if not text:
            return None
        
        # Convert Kannada digits to Arabic first
        converted_text = self.kannada_digits_to_arabic(text)
        
        # Look for patterns like "Page 123", "ಪುಟ 123", etc.
        page_patterns = [
            r'(?:page|ಪುಟ|ಪೃಷ್ಠ)\s*[:\-]?\s*(\d+)',
            r'(\d+)\s*(?:ನೇ|ನೇ\s*ಪುಟ)',
            r'^\s*(\d+)\s*$',  # Just a number on its own line
            r'(\d+)'  # Any number (fallback)
        ]
        
        for pattern in page_patterns:
            matches = re.findall(pattern, converted_text, re.IGNORECASE | re.MULTILINE)
            if matches:
                try:
                    return int(matches[0])
                except (ValueError, IndexError):
                    continue
        
        # Try Kannada word numbers
        for word, number in self.kannada_words.items():
            if word in text:
                return number
        
        return None

    def extract_page_number_from_text(self, text):
        """Extract page number from text content - alias for find_page_number_in_text"""
        return self.find_page_number_in_text(text)
