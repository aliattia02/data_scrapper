"""
src/scrapers/filloffer_improved.py - Enhanced Filloffer Scraper with PDF download
"""
import requests
from bs4 import BeautifulSoup
import re
import os
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path
import time
import hashlib

from src.scrapers.base import BaseScraper
from src.database.models import Product, Catalogue
from src.utils.categories import match_category
from src.utils.helpers import extract_price, clean_product_name


class FillofferScraperImproved(BaseScraper):
    """Enhanced Filloffer Scraper - Downloads PDFs first, then processes"""

    STORE_NAME = 'filloffer'
    BASE_URL = 'https://www.filloffer.com'

    STORE_MAPPING = {
        'kazyon-market': 'kazyon',
        'carrefour': 'carrefour',
        'metro-market': 'metro',
        'lulu-hypermarket': 'lulu',
        'kheir-zaman': 'kheirzaman',
        'spinneys': 'spinneys'
    }

    def __init__(self, db_manager, target_store=None):
        super().__init__(db_manager)
        self.target_store = target_store
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Referer': 'https://www.filloffer.com/'
        })

        # Create directories
        self.download_dir = Path("data/flyers")
        self.pdf_dir = Path("data/pdfs")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

    def scrape(self) -> List[Product]:
        """Main scraping method with PDF download approach"""
        self.start_log()
        all_products = []

        try:
            catalogues = self._get_latest_catalogues()
            print(f"Found {len(catalogues)} catalogues\n")

            for cat_info in catalogues[:3]:  # Process first 3 catalogues
                try:
                    print(f"\n{'='*70}")
                    print(f"📥 Processing: {cat_info['title'][:60]}...")
                    print(f"{'='*70}")

                    # Try to download PDF first
                    pdf_path = self._download_pdf(cat_info)

                    if pdf_path and pdf_path.exists():
                        print(f"✅ PDF downloaded: {pdf_path.name}")

                        # Convert PDF to images
                        images = self._pdf_to_images(pdf_path, cat_info)
                        print(f"📄 Extracted {len(images)} pages from PDF")

                    else:
                        print("⚠️  No PDF found, trying direct image extraction...")
                        # Fallback: Extract images from page
                        images = self._extract_images_from_page(cat_info)

                    if images:
                        # Process images with OCR
                        products = self._process_images(images, cat_info)
                        all_products.extend(products)
                        print(f"✅ Extracted {len(products)} products")
                    else:
                        print("❌ No images found")

                except Exception as e:
                    self.log_error(f"Failed to process {cat_info['title']}: {e}")
                    print(f"❌ Error: {e}")
                    import traceback
                    traceback.print_exc()

            # Save products
            self._save_products(all_products)
            self.complete_log(len(all_products), 'completed')

        except Exception as e:
            self.log_error(f'Scraping failed: {e}')
            self.complete_log(len(all_products), 'failed')
            import traceback
            traceback.print_exc()

        return all_products

    def _get_latest_catalogues(self) -> List[Dict]:
        """Get list of latest catalogues"""
        catalogues = []

        try:
            if self.target_store:
                store_slug = [k for k, v in self.STORE_MAPPING.items() if v == self.target_store]
                url = f'{self.BASE_URL}/markets/{store_slug[0]}' if store_slug else f'{self.BASE_URL}/egypt'
            else:
                url = f'{self.BASE_URL}/egypt'

            print(f"🔍 Fetching catalogues from: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')
            links = soup.find_all('a', href=True)

            for link in links:
                href = link.get('href', '')

                # Look for PDF or offer links
                if '/pdf' in href.lower() or ('/markets/' in href and any(x in href.lower() for x in ['offer', 'catalogue', 'flyer'])):
                    full_url = urljoin(self.BASE_URL, href)

                    # Skip duplicates
                    if any(c['url'] == full_url for c in catalogues):
                        continue

                    # Extract store info
                    store_match = re.search(r'/markets/([^/]+)/', href)
                    store_slug = store_match.group(1) if store_match else 'unknown'
                    store_name = self.STORE_MAPPING.get(store_slug.lower(), store_slug)

                    # Get title
                    title = link.get_text(strip=True) or link.get('title', '')
                    if not title or len(title) < 5:
                        continue

                    # Extract dates
                    dates = self._extract_dates(href + ' ' + title)

                    catalogues.append({
                        'url': full_url,
                        'title': title,
                        'store': store_name,
                        'store_slug': store_slug,
                        'valid_from': dates.get('from'),
                        'valid_until': dates.get('until')
                    })

            print(f"✅ Found {len(catalogues)} catalogues")
            return catalogues

        except Exception as e:
            print(f"❌ Error getting catalogues: {e}")
            return []

    def _download_pdf(self, cat_info: Dict) -> Optional[Path]:
        """Download PDF file if available"""
        try:
            print(f"\n🔍 Looking for PDF at: {cat_info['url']}")

            response = self.session.get(cat_info['url'], timeout=30, allow_redirects=True)
            response.raise_for_status()

            # Check if response is a PDF
            content_type = response.headers.get('Content-Type', '')

            if 'application/pdf' in content_type:
                # Direct PDF download
                filename = self._generate_pdf_filename(cat_info)
                pdf_path = self.pdf_dir / filename

                print(f"📥 Downloading PDF ({len(response.content)/1024:.1f} KB)...")
                pdf_path.write_bytes(response.content)
                print(f"✅ PDF saved: {pdf_path}")
                return pdf_path

            else:
                # Parse HTML page to find PDF link
                soup = BeautifulSoup(response.text, 'lxml')

                # Look for PDF links in common patterns
                pdf_patterns = [
                    r'\.pdf',
                    r'/pdf/',
                    r'download',
                    r'catalogue',
                    r'flyer'
                ]

                # Check all links
                for link in soup.find_all(['a', 'iframe'], href=True):
                    href = link.get('href') or link.get('src', '')

                    if any(pattern in href.lower() for pattern in pdf_patterns):
                        pdf_url = urljoin(self.BASE_URL, href)

                        # Try to download
                        try:
                            print(f"🔗 Found potential PDF: {pdf_url}")
                            pdf_response = self.session.get(pdf_url, timeout=30)

                            if 'application/pdf' in pdf_response.headers.get('Content-Type', ''):
                                filename = self._generate_pdf_filename(cat_info)
                                pdf_path = self.pdf_dir / filename

                                print(f"📥 Downloading PDF ({len(pdf_response.content)/1024:.1f} KB)...")
                                pdf_path.write_bytes(pdf_response.content)
                                print(f"✅ PDF saved: {pdf_path}")
                                return pdf_path
                        except:
                            continue

            print("⚠️  No PDF found")
            return None

        except Exception as e:
            print(f"⚠️  PDF download failed: {e}")
            return None

    def _generate_pdf_filename(self, cat_info: Dict) -> str:
        """Generate unique PDF filename"""
        # Create hash from URL for uniqueness
        url_hash = hashlib.md5(cat_info['url'].encode()).hexdigest()[:8]
        store = cat_info['store']
        timestamp = int(time.time())

        # Clean title for filename
        clean_title = re.sub(r'[^\w\s-]', '', cat_info['title'])[:30]
        clean_title = re.sub(r'[-\s]+', '_', clean_title)

        return f"{store}_{clean_title}_{url_hash}_{timestamp}.pdf"

    def _pdf_to_images(self, pdf_path: Path, cat_info: Dict) -> List[Path]:
        """Convert PDF to images using pdf2image"""
        images = []

        try:
            from pdf2image import convert_from_path

            print(f"📄 Converting PDF to images...")

            # Convert PDF to images (300 DPI for good OCR quality)
            pages = convert_from_path(
                str(pdf_path),
                dpi=300,
                fmt='jpeg',
                thread_count=4
            )

            print(f"✅ Converted {len(pages)} pages")

            # Save each page as image
            for i, page in enumerate(pages, 1):
                timestamp = int(time.time())
                image_filename = f"{cat_info['store']}_page_{i}_{timestamp}.jpg"
                image_path = self.download_dir / image_filename

                page.save(image_path, 'JPEG', quality=95, optimize=True)
                images.append(image_path)
                print(f"  ✓ Saved page {i}: {image_path.name}")

            return images

        except ImportError:
            print("❌ pdf2image not installed. Install: pip install pdf2image")
            print("   Also requires poppler: https://github.com/oschwartz10612/poppler-windows/releases/")
            return []
        except Exception as e:
            print(f"❌ PDF conversion failed: {e}")
            return []

    def _extract_images_from_page(self, cat_info: Dict) -> List[Path]:
        """Fallback: Extract images directly from HTML page"""
        images = []

        try:
            print(f"🔍 Extracting images from: {cat_info['url']}")
            response = self.session.get(cat_info['url'], timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            # Look for high-resolution images
            for img in soup.find_all('img'):
                src = img.get('data-src') or img.get('src') or img.get('data-original')

                if not src:
                    continue

                # Skip small thumbnails
                if any(x in src.lower() for x in ['thumb', 'small', '_s.', 'icon']):
                    continue

                # Get full URL
                img_url = urljoin(self.BASE_URL, src)

                # Download image
                try:
                    img_response = self.session.get(img_url, timeout=30)
                    img_response.raise_for_status()

                    # Check size (skip if too small)
                    if len(img_response.content) < 50000:  # Less than 50KB
                        continue

                    # Save image
                    timestamp = int(time.time())
                    filename = f"{cat_info['store']}_img_{len(images)}_{timestamp}.jpg"
                    image_path = self.download_dir / filename

                    image_path.write_bytes(img_response.content)
                    images.append(image_path)
                    print(f"  ✓ Downloaded image {len(images)}: {filename}")

                except Exception as e:
                    continue

            return images

        except Exception as e:
            print(f"❌ Image extraction failed: {e}")
            return []

    def _process_images(self, image_paths: List[Path], cat_info: Dict) -> List[Product]:
        """Process downloaded images with OCR"""
        products = []

        try:
            import pytesseract
            from PIL import Image

            for idx, img_path in enumerate(image_paths, 1):
                try:
                    print(f"\n  🔍 Processing page {idx}/{len(image_paths)}: {img_path.name}")

                    # Open and validate image
                    image = Image.open(img_path)
                    print(f"     Size: {image.size[0]}x{image.size[1]}, Mode: {image.mode}")

                    # Convert RGBA to RGB
                    if image.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        if image.mode == 'P':
                            image = image.convert('RGBA')
                        if image.mode in ('RGBA', 'LA'):
                            background.paste(image, mask=image.split()[-1])
                        image = background

                    # Enhance for OCR
                    image_enhanced = self._enhance_image_for_ocr(image)

                    # Extract text
                    text = self._extract_text_multi_pass(image_enhanced)

                    # Save extracted text
                    text_path = img_path.with_suffix('.txt')
                    text_path.write_text(text, encoding='utf-8')

                    word_count = len(text.split())
                    print(f"     Extracted: {len(text)} chars, {word_count} words")

                    if word_count < 10:
                        print(f"     ⚠️  Very little text extracted")
                        continue

                    # Extract products
                    page_products = self._extract_products_from_text(text, cat_info, idx)
                    products.extend(page_products)

                    print(f"     ✅ Found {len(page_products)} products")

                except Exception as e:
                    print(f"     ❌ Error: {e}")
                    continue

        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            print("   Install: pip install pytesseract pillow")

        return products

    def _enhance_image_for_ocr(self, image):
        """Enhance image for better OCR"""
        try:
            from PIL import ImageEnhance, ImageFilter

            # Convert to grayscale
            image = image.convert('L')

            # Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.5)

            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)

            # Apply unsharp mask
            image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

            return image
        except:
            return image

    def _extract_text_multi_pass(self, image):
        """Extract text using multiple OCR strategies"""
        import pytesseract

        texts = []

        # Pass 1: Standard OCR
        text1 = pytesseract.image_to_string(image, lang='ara+eng', config='--psm 6')
        texts.append(text1)

        # Pass 2: Different page segmentation
        text2 = pytesseract.image_to_string(image, lang='ara+eng', config='--psm 3')
        texts.append(text2)

        # Pass 3: Single column
        text3 = pytesseract.image_to_string(image, lang='ara+eng', config='--psm 4')
        texts.append(text3)

        # Return longest result
        return max(texts, key=len)

    def _extract_products_from_text(self, text: str, cat_info: Dict, page_num: int) -> List[Product]:
        """Extract products from OCR text"""
        products = []
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        i = 0
        while i < len(lines):
            line = lines[i]

            if len(line) < 3:
                i += 1
                continue

            # Look for price
            price = extract_price(line)

            if price and price > 0.5:  # Minimum price threshold
                # Build product name from surrounding lines
                name_parts = []

                # Previous lines (up to 3)
                for j in range(max(0, i-3), i):
                    prev_line = lines[j]
                    if prev_line and len(prev_line) > 2 and not extract_price(prev_line):
                        name_parts.append(prev_line)

                # Current line (remove price)
                current_clean = re.sub(
                    r'\d+[\.,]?\d*\s*(جنيه|ج\.م|egp|le|pound)?',
                    '',
                    line,
                    flags=re.IGNORECASE
                ).strip()

                if current_clean and len(current_clean) > 2:
                    name_parts.append(current_clean)

                # Next line if name too short
                if i + 1 < len(lines) and len(' '.join(name_parts)) < 10:
                    next_line = lines[i + 1]
                    if next_line and not extract_price(next_line):
                        name_parts.append(next_line)

                name = ' '.join(name_parts)
                name = clean_product_name(name)

                # Validate product name
                if name and 3 < len(name) < 200:
                    # Filter common noise
                    noise_words = ['page', 'offer', 'valid', 'كازيون', 'kazyon', 'market', 'www.', 'http']
                    if not any(noise in name.lower() for noise in noise_words):

                        category_ar, category_en = match_category(name)

                        product = Product(
                            store=cat_info['store'],
                            store_product_id=f"{cat_info['store']}_p{page_num}_{len(products)}_{int(time.time())}",
                            name_ar=name,
                            name_en=name,
                            category_ar=category_ar,
                            category_en=category_en,
                            price=price,
                            currency='EGP',
                            in_stock=True,
                            url=cat_info['url'],
                            source='filloffer_ocr',
                            scraped_at=datetime.utcnow()
                        )
                        products.append(product)
                        print(f"        ✓ {name[:50]}... - {price} EGP")

            i += 1

        return products

    def _extract_dates(self, text: str) -> Dict:
        """Extract dates from text"""
        dates = {}

        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'يناير': 1, 'فبراير': 2, 'مارس': 3, 'أبريل': 4,
            'مايو': 5, 'يونيو': 6, 'يوليو': 7, 'أغسطس': 8,
            'سبتمبر': 9, 'أكتوبر': 10, 'نوفمبر': 11, 'ديسمبر': 12
        }

        # Find all dates
        pattern = r'(\d{1,2})\s*[-/]?\s*(' + '|'.join(months.keys()) + r')'
        matches = re.findall(pattern, text.lower())

        if len(matches) >= 2:
            try:
                current_year = datetime.now().year
                day1, month1 = matches[0]
                month_num1 = months.get(month1.lower(), 1)
                dates['from'] = datetime(current_year, month_num1, int(day1))

                day2, month2 = matches[1]
                month_num2 = months.get(month2.lower(), 1)
                dates['until'] = datetime(current_year, month_num2, int(day2))
            except:
                pass

        return dates