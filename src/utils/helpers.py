"""
src/utils/helpers.py - Utility Functions
"""
import re
from typing import Optional

def extract_price(text: str) -> Optional[float]:
    """Extract price from Arabic/English text"""
    # Remove currency symbols and Arabic digits
    text = text.replace('EGP', '').replace('ج.م', '').replace('جنيه', '')
    
    # Find numbers
    match = re.search(r'(\d+\.?\d*)', text)
    if match:
        return float(match.group(1))
    return None

def normalize_arabic_text(text: str) -> str:
    """Normalize Arabic text for better matching"""
    # Remove diacritics
    text = re.sub(r'[ؗ-ًؚ-ْ]', '', text)
    # Normalize alef
    text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
    # Normalize teh marbuta
    text = text.replace('ة', 'ه')
    return text.strip()

def calculate_discount(original_price: float, sale_price: float) -> float:
    """Calculate discount percentage"""
    if original_price <= 0 or sale_price < 0:
        return 0.0
    if sale_price >= original_price:
        return 0.0
    return round(((original_price - sale_price) / original_price) * 100, 2)

def clean_product_name(name: str) -> str:
    """Clean product name"""
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name)
    return name.strip()
