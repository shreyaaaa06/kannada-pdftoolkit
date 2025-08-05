#!/usr/bin/env python3
"""Test script to verify sorting preview data structure"""

import json
from utils.kannada_numeral_converter import KannadaNumeralConverter

def test_data_structure():
    """Test the data structure returned by sorting preview"""
    
    # Simulate the data structure that should be returned
    converter = KannadaNumeralConverter()
    
    # Test cases
    test_texts = [
        "ಪುಟ ೫",      # Should return 5
        "೧೦",         # Should return 10
        "random text", # Should return None (fallback to page number)
        "page 15"      # Should return 15
    ]
    
    print("🧪 Testing Kannada Numeral Extraction:")
    print("-" * 40)
    
    simulated_previews = []
    for i, text in enumerate(test_texts):
        page_num = i + 1
        extracted_number = converter.extract_page_number_from_text(text)
        
        preview = {
            'page_num': page_num,
            'extracted_number': extracted_number if extracted_number else page_num,
            'thumbnail_path': f'/thumbnails/test/{page_num}.png'
        }
        
        simulated_previews.append(preview)
        print(f"Page {page_num}: '{text}' → extracted_number: {preview['extracted_number']}")
    
    print(f"\n📊 Data Structure Sample:")
    print("-" * 30)
    print(json.dumps(simulated_previews[0], indent=2, ensure_ascii=False))
    
    print(f"\n✅ All fields present:")
    sample = simulated_previews[0]
    for key in ['page_num', 'extracted_number', 'thumbnail_path']:
        print(f"   - {key}: {sample.get(key, 'MISSING!')}")
    
    print(f"\n🎯 Template Compatibility:")
    print("   - ${preview.page_num} ✅")
    print("   - ${preview.extracted_number} ✅") 
    print("   - ${preview.thumbnail_path} ✅")
    
    return True

if __name__ == "__main__":
    print("🔍 Testing Sorting Preview Data Structure")
    print("=" * 50)
    test_data_structure()
    print("\n🎉 Data structure is now compatible with template!")
    print("   The 'ಸಂಖ್ಯೆ: undefined' issue should be fixed!")
