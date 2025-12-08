"""
src/ocr/processor.py - OCR Processing with Pytesseract + OpenCV
"""
import cv2
import numpy as np
import pytesseract
from typing import List, Dict
from datetime import datetime
import re

from src.database.models import Product
from src.database.manager import DatabaseManager
from src.utils.categories import match_category
from src.ocr.image_preprocessor import ImagePreprocessor


class OCRProcessor:
    """Process Kazyon flyers with OCR"""

    def __init__(self):
        self.db_manager = DatabaseManager()
        # Configure Tesseract for Arabic + English with LSTM engine
        # OEM 1 = LSTM Neural Net mode (better accuracy for modern documents)
        # PSM 11 = Sparse text mode (best for unstructured flyer layouts)
        self.config = '--oem 1 --psm 11 -l ara+eng'
        self.preprocessor = ImagePreprocessor()

    def process_flyer(self, image_path: str) -> List[Product]:
        """
        Process a single Kazyon flyer image
        Returns list of extracted products
        """
        print(f"🔍 Processing flyer: {image_path}")

        # Use enhanced preprocessing
        processed_image = self.preprocessor.preprocess(image_path)

        # Extract text with multiple passes for better accuracy
        text = self._extract_text_multi_pass(processed_image)

        # Parse products from text
        products = self._parse_flyer_text(text)

        # Save to database
        if products:
            self._save_products(products)
            print(f"✅ Extracted {len(products)} products")

        return products

    def _extract_text_multi_pass(self, image: np.ndarray) -> str:
        """
        Extract text using multiple OCR passes with different configurations
        Returns the longest/best result
        """
        configs = [
            '--oem 1 --psm 11',  # LSTM + sparse text (best for flyers)
            '--oem 1 --psm 6',   # LSTM + uniform block
            '--oem 1 --psm 4',   # LSTM + single column
        ]
        
        texts = []
        for config in configs:
            try:
                text = pytesseract.image_to_string(image, lang='ara+eng', config=config)
                texts.append(text)
            except Exception:
                continue
        
        # Return longest result
        return max(texts, key=len) if texts else ""

    def _parse_flyer_text(self, text: str) -> List[Product]:
        """
        Parse OCR text to extract product information
        Kazyon flyers typically have format:
        - Product name (Arabic/English)
        - Price with EGP
        - Sometimes discount info
        """
        products = []
        lines = text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Check if line contains price (indicator of product)
            price_match = re.search(r'(\d+\.?\d*)\s*(?:EGP|ج\.م|جنيه)', line, re.IGNORECASE)

            if price_match:
                price = float(price_match.group(1))

                # Product name is likely in current or previous line
                product_name = self._extract_product_name(lines, i)

                # Check for discount
                discount_match = re.search(r'(\d+)%', line)
                discount_pct = float(discount_match.group(1)) if discount_match else None

                # Calculate original price if discount exists
                original_price = None
                if discount_pct:
                    original_price = round(price / (1 - discount_pct / 100), 2)

                # Try to determine category from product name
                category_ar, category_en = match_category(product_name)

                # Extract size/weight if present
                size_match = re.search(r'(\d+\.?\d*)\s*(kg|g|l|ml|كجم|جرام|لتر)',
                                       product_name, re.IGNORECASE)
                size = size_match.group(0) if size_match else None

                product = Product(
                    store='kazyon',
                    store_product_id=f"kazyon_{hash(product_name + str(price))}",
                    name_ar=product_name,
                    name_en=product_name,  # Will improve with translation
                    category_ar=category_ar,
                    category_en=category_en,
                    price=price,
                    original_price=original_price,
                    discount_percentage=discount_pct,
                    currency='EGP',
                    size=size,
                    in_stock=True,
                    source='ocr',
                    scraped_at=datetime.utcnow()
                )

                products.append(product)

            i += 1

        return products

    def _extract_product_name(self, lines: List[str], current_idx: int) -> str:
        """
        Extract product name from nearby lines
        Usually 1-2 lines before price
        """
        # Look back up to 3 lines
        candidates = []

        for offset in range(1, 4):
            idx = current_idx - offset
            if idx >= 0:
                line = lines[idx].strip()
                # Skip if line contains only numbers or is too short
                if line and len(line) > 3 and not line.replace('.', '').isdigit():
                    candidates.append(line)

        # Return the closest non-empty candidate
        if candidates:
            return candidates[0]

        # Fallback to current line
        return lines[current_idx].strip()

    def _save_products(self, products: List[Product]):
        """Save extracted products to database"""
        session = self.db_manager.get_session()

        try:
            for product in products:
                # Check if product already exists
                existing = session.query(Product).filter_by(
                    store_product_id=product.store_product_id
                ).first()

                if existing:
                    # Update existing
                    existing.price = product.price
                    existing.original_price = product.original_price
                    existing.discount_percentage = product.discount_percentage
                    existing.updated_at = datetime.utcnow()
                else:
                    # Add new
                    session.add(product)

            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def batch_process(self, flyer_directory: str) -> Dict[str, List[Product]]:
        """
        Process multiple flyers in a directory
        Returns: {filename: [products]}
        """
        import os
        from pathlib import Path

        results = {}
        flyer_dir = Path(flyer_directory)

        for image_file in flyer_dir.glob('*.jpg') + flyer_dir.glob('*.png'):
            try:
                products = self.process_flyer(str(image_file))
                results[image_file.name] = products
            except Exception as e:
                print(f"❌ Failed to process {image_file.name}: {e}")
                results[image_file.name] = []

        return results