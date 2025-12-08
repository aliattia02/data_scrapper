"""
src/utils/helpers.py - Helper utility functions
"""
import re
from typing import Optional


def extract_price(text: str) -> Optional[float]:
    """
    Extract price from Arabic/English text
    Examples:
        "99.99 جنيه" -> 99.99
        "EGP 150" -> 150.0
        "٥٩٫٩٩" -> 59.99
    """
    if not text:
        return None

    # Remove common words
    text = text.lower()
    text = re.sub(r'(egp|جنيه|ج\.م|le|pound|جم)', '', text, flags=re.IGNORECASE)

    # Convert Arabic numerals to English
    arabic_to_english = {
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
        '٫': '.'
    }

    for arabic, english in arabic_to_english.items():
        text = text.replace(arabic, english)

    # Find price patterns
    # Matches: 99.99, 99,99, 99
    pattern = r'(\d+(?:[.,]\d{1,2})?)'
    matches = re.findall(pattern, text)

    if matches:
        # Take the first number found
        price_str = matches[0].replace(',', '.')
        try:
            price = float(price_str)
            # Sanity check: prices should be between 0.01 and 100,000
            if 0.01 <= price <= 100000:
                return price
        except ValueError:
            pass

    return None


def clean_product_name(text: str) -> str:
    """
    Clean product name from OCR artifacts
    """
    if not text:
        return ""

    # Remove excessive whitespace
    text = ' '.join(text.split())

    # Remove price-related suffixes
    text = re.sub(r'(egp|جنيه|ج\.م|le|\d+\.\d+|\d+)', '', text, flags=re.IGNORECASE)

    # Remove special characters but keep Arabic and English letters
    text = re.sub(r'[^\w\s\u0600-\u06FF-]', ' ', text)

    # Clean up whitespace again
    text = ' '.join(text.split())

    return text.strip()


def parse_arabic_number(text: str) -> Optional[float]:
    """Convert Arabic numerals to float"""
    arabic_to_english = {
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
        '٫': '.'
    }

    for arabic, english in arabic_to_english.items():
        text = text.replace(arabic, english)

    try:
        return float(text)
    except ValueError:
        return None


def extract_discount_percentage(original_price: float, sale_price: float) -> Optional[float]:
    """Calculate discount percentage"""
    if not original_price or not sale_price or original_price <= sale_price:
        return None

    discount = ((original_price - sale_price) / original_price) * 100
    return round(discount, 2)