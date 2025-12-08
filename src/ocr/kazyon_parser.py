"""
src/ocr/kazyon_parser.py - Kazyon-specific OCR parsing logic
"""
import re
from typing import List, Tuple, Optional


def parse_kazyon_text(text: str) -> List[dict]:
    """
    Parse OCR text specifically for Kazyon flyers
    Returns list of product dictionaries
    """
    products = []
    lines = text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # Look for price patterns
        price_match = re.search(r'(\d+\.?\d*)\s*(?:EGP|ج\.م|جنيه)', line, re.IGNORECASE)
        
        if price_match:
            price = float(price_match.group(1))
            
            # Get product name from previous lines
            product_name = extract_product_name(lines, i)
            
            # Check for discount
            discount_match = re.search(r'(\d+)%', line)
            discount = float(discount_match.group(1)) if discount_match else None
            
            # Extract size/weight
            size_match = re.search(r'(\d+\.?\d*)\s*(kg|g|l|ml|كجم|جرام|لتر)', 
                                    product_name, re.IGNORECASE)
            size = size_match.group(0) if size_match else None
            
            product = {
                'name': product_name,
                'price': price,
                'discount': discount,
                'size': size
            }
            
            products.append(product)
        
        i += 1
    
    return products


def extract_product_name(lines: List[str], price_line_idx: int) -> str:
    """Extract product name from lines before price"""
    candidates = []
    
    for offset in range(1, 4):
        idx = price_line_idx - offset
        if idx >= 0:
            line = lines[idx].strip()
            if line and len(line) > 3 and not line.replace('.', '').isdigit():
                candidates.append(line)
    
    if candidates:
        return candidates[0]
    
    return lines[price_line_idx].strip()


def extract_price_from_kazyon_text(text: str) -> Optional[float]:
    """
    Extract price from Kazyon-specific text format
    Enhanced to handle Egyptian prices (ج.م, جنيه, EGP, LE)
    Validates prices are in reasonable range (1-10000 EGP for groceries)
    """
    # Try different patterns specific to Egyptian currency
    patterns = [
        r'(\d+[\.,]?\d*)\s*(?:جنيه|ج\.م|جم)',  # Arabic
        r'(\d+[\.,]?\d*)\s*(?:EGP|LE|egp|le)',  # English abbreviations
        r'(\d+[\.,]?\d*)\s*(?:pound)',          # English word
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace(',', '.')
            try:
                price = float(price_str)
                # Validate price is in reasonable range for groceries
                if 1.0 <= price <= 10000.0:
                    return price
            except ValueError:
                continue
    
    return None
