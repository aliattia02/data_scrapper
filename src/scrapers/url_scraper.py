"""
src/scrapers/url_scraper.py - URL-based scraper for specific catalogue pages
Downloads images from catalogue pages and converts them to PDF
"""
import requests
import time
import hashlib
import cv2
import pytesseract
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re

from src.database.models import ScrapeJob, Product
from src.database.manager import DatabaseManager
from src.utils.categories import match_category
from src.utils.helpers import extract_price
from src.ocr.processor import OCRProcessor
from src.ocr.image_preprocessor import ImagePreprocessor


class URLScraper:
    """Scraper for specific catalogue URLs from filloffer.com"""
    
    BASE_URL = 'https://www.filloffer.com'
    
    # Store name mapping
    STORE_MAPPING = {
        'kazyon-market': 'kazyon',
        'carrefour': 'carrefour',
        'metro-market': 'metro',
        'lulu-hypermarket': 'lulu',
        'kheir-zaman': 'kheirzaman',
        'spinneys': 'spinneys'
    }
    
    # Arabic month names pattern for filtering dates
    MONTH_PATTERN = r'ديسمبر|يناير|فبراير|مارس|ابريل|مايو|يونيو|يوليو|اغسطس|سبتمبر|اكتوبر|نوفمبر|Nov|Dec'
    
    # Price validation range for Egyptian groceries (in EGP)
    # Min: 5 EGP (small items like single piece snacks)
    # Max: 5000 EGP (large bulk purchases or appliances in grocery stores)
    MIN_PRICE = 5.0
    MAX_PRICE = 5000.0
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Referer': 'https://www.filloffer.com/'
        })
        
        # Create directories
        self.images_dir = Path("data/catalogue_images")
        self.pdf_dir = Path("data/pdfs")
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_job = None
    
    def scrape_url(self, url: str, store: Optional[str] = None) -> Dict:
        """
        Scrape a specific catalogue URL
        
        Args:
            url: Full URL to catalogue page (e.g., https://www.filloffer.com/markets/Kazyon-Market/.../pdf)
            store: Optional store name override (auto-detected if not provided)
        
        Returns:
            Dictionary with scraping results
        """
        # Auto-detect store from URL if not provided
        if not store:
            store = self._detect_store_from_url(url)
        
        # Create scrape job
        self.current_job = self._create_job(url, store)
        
        try:
            # Update job status
            self._update_job_status('downloading')
            
            # Download images from the catalogue page
            images = self._download_catalogue_images(url)
            
            if not images:
                raise Exception("No images found on catalogue page")
            
            self._update_job_progress(
                total_pages=len(images),
                pages_downloaded=len(images)
            )
            
            # Convert images to PDF
            pdf_path = self._images_to_pdf(images, url)
            self._update_job(pdf_path=str(pdf_path))
            
            # Process with OCR
            self._update_job_status('processing_ocr')
            products = self._process_with_ocr(images, url, store)
            
            self._update_job_progress(
                pages_processed=len(images),
                products_found=len(products)
            )
            
            # Save products to database
            self._save_products(products)
            
            # Mark as completed
            self._update_job_status('completed')
            
            return {
                'status': 'completed',
                'job_id': self.current_job.id,
                'products_found': len(products),
                'pages_processed': len(images),
                'pdf_path': str(pdf_path)
            }
            
        except Exception as e:
            # Mark as failed
            self._update_job_status('failed', str(e))
            raise
    
    def _detect_store_from_url(self, url: str) -> str:
        """Auto-detect store name from URL"""
        url_lower = url.lower()
        
        for slug, store_name in self.STORE_MAPPING.items():
            if slug in url_lower:
                return store_name
        
        # Default to unknown
        return 'unknown'
    
    def _create_job(self, url: str, store: str) -> ScrapeJob:
        """Create a new scrape job in database"""
        session = self.db_manager.get_session()
        try:
            job = ScrapeJob(
                source_url=url,
                store=store,
                status='pending',
                started_at=datetime.utcnow()
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            return job
        finally:
            session.close()
    
    def _update_job_status(self, status: str, error: Optional[str] = None):
        """Update job status"""
        if not self.current_job:
            return
        
        session = self.db_manager.get_session()
        try:
            job = session.query(ScrapeJob).filter_by(id=self.current_job.id).first()
            if job:
                job.status = status
                if error:
                    job.errors = error
                if status == 'completed':
                    job.completed_at = datetime.utcnow()
                    if job.started_at:
                        job.duration_seconds = (job.completed_at - job.started_at).total_seconds()
                session.commit()
                session.refresh(job)
                self.current_job = job
        finally:
            session.close()
    
    def _update_job_progress(self, **kwargs):
        """Update job progress fields"""
        if not self.current_job:
            return
        
        session = self.db_manager.get_session()
        try:
            job = session.query(ScrapeJob).filter_by(id=self.current_job.id).first()
            if job:
                for key, value in kwargs.items():
                    if hasattr(job, key):
                        setattr(job, key, value)
                session.commit()
                session.refresh(job)
                self.current_job = job
        finally:
            session.close()
    
    def _update_job(self, **kwargs):
        """Update job fields"""
        if not self.current_job:
            return
        
        session = self.db_manager.get_session()
        try:
            job = session.query(ScrapeJob).filter_by(id=self.current_job.id).first()
            if job:
                for key, value in kwargs.items():
                    if hasattr(job, key):
                        setattr(job, key, value)
                session.commit()
                session.refresh(job)
                self.current_job = job
        finally:
            session.close()
    
    def _download_catalogue_images(self, url: str, max_retries: int = 3, timeout: int = 30) -> List[Path]:
        """
        Download all catalogue page images from the /pdf page
        Uses proper timeout handling and retry logic
        """
        images = []
        
        print(f"🔍 Fetching catalogue page: {url}")
        
        # Retry logic for the main page
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                break
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⚠️  Timeout on attempt {attempt + 1}, retrying...")
                    time.sleep(2)
                else:
                    raise Exception(f"Failed to fetch page after {max_retries} attempts")
            except Exception as e:
                raise Exception(f"Failed to fetch catalogue page: {e}")
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find all image tags (look for catalogue page images)
        img_tags = soup.find_all('img')
        
        # Create a unique directory for this catalogue
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        catalogue_dir = self.images_dir / f"catalogue_{url_hash}"
        catalogue_dir.mkdir(exist_ok=True)
        
        page_num = 1
        for img in img_tags:
            # Get image source (try multiple attributes)
            src = img.get('data-src') or img.get('src') or img.get('data-original')
            
            if not src:
                continue
            
            # Skip thumbnails and small images
            if any(x in src.lower() for x in ['thumb', 'small', '_s.', 'icon', 'logo']):
                continue
            
            # Get full URL
            img_url = urljoin(self.BASE_URL, src)
            
            # Download with retry logic
            downloaded = False
            for attempt in range(max_retries):
                try:
                    print(f"  📥 Downloading page {page_num}...")
                    img_response = self.session.get(img_url, timeout=timeout, stream=True)
                    img_response.raise_for_status()
                    
                    # Check size (skip if too small - likely not a catalogue page)
                    content_length = img_response.headers.get('content-length')
                    if content_length and int(content_length) < 50000:  # Less than 50KB
                        print(f"    ⚠️  Skipping small image ({int(content_length)/1024:.1f}KB)")
                        break
                    
                    # Save image
                    image_path = catalogue_dir / f"page_{page_num:03d}.jpg"
                    with open(image_path, 'wb') as f:
                        for chunk in img_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    images.append(image_path)
                    print(f"    ✅ Downloaded: {image_path.name} ({image_path.stat().st_size/1024:.1f}KB)")
                    page_num += 1
                    downloaded = True
                    break
                    
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        print(f"    ⚠️  Timeout on attempt {attempt + 1}, retrying...")
                        time.sleep(2)
                    else:
                        print(f"    ❌ Failed to download after {max_retries} attempts")
                except Exception as e:
                    print(f"    ⚠️  Error downloading: {e}")
                    break
            
            # Small delay to avoid overwhelming server
            if downloaded:
                time.sleep(0.5)
        
        # Store images directory in job
        if images:
            self._update_job(images_dir=str(catalogue_dir))
        
        print(f"✅ Downloaded {len(images)} catalogue pages")
        return images
    
    def _images_to_pdf(self, image_paths: List[Path], source_url: str) -> Path:
        """
        Combine downloaded images into a single PDF file
        Uses img2pdf for efficient conversion
        """
        try:
            import img2pdf
            
            # Generate PDF filename
            url_hash = hashlib.md5(source_url.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            pdf_filename = f"catalogue_{url_hash}_{timestamp}.pdf"
            pdf_path = self.pdf_dir / pdf_filename
            
            print(f"\n📄 Creating PDF from {len(image_paths)} images...")
            
            # Convert images to PDF
            with open(pdf_path, "wb") as f:
                # img2pdf expects file paths as strings or bytes
                image_files = [str(img) for img in image_paths]
                f.write(img2pdf.convert(image_files))
            
            print(f"✅ PDF created: {pdf_path.name} ({pdf_path.stat().st_size/1024:.1f}KB)")
            return pdf_path
            
        except ImportError:
            print("⚠️  img2pdf not installed, skipping PDF creation")
            print("   Install with: pip install img2pdf")
            return None
        except Exception as e:
            print(f"⚠️  PDF creation failed: {e}")
            return None
    
    def _process_with_ocr(self, image_paths: List[Path], source_url: str, store: str) -> List[Product]:
        """Process images with OCR to extract products"""
        products = []
        preprocessor = ImagePreprocessor()
        
        for idx, img_path in enumerate(image_paths, 1):
            try:
                print(f"\n🔍 Processing page {idx}/{len(image_paths)}: {img_path.name}")
                
                # Preprocess image
                processed_image = preprocessor.preprocess(str(img_path))
                
                # Save preprocessed image for debugging
                processed_path = img_path.parent / f"{img_path.stem}_processed.jpg"
                cv2.imwrite(str(processed_path), processed_image)
                
                # Extract text with improved OCR
                text = self._extract_text_enhanced(processed_image)
                
                # Save extracted text
                text_path = img_path.with_suffix('.txt')
                text_path.write_text(text, encoding='utf-8')
                
                word_count = len(text.split())
                print(f"  📝 Extracted: {len(text)} chars, {word_count} words")
                
                if word_count < 10:
                    print(f"  ⚠️  Very little text extracted")
                    continue
                
                # Extract products from text
                page_products = self._extract_products_enhanced(text, source_url, store, idx)
                products.extend(page_products)
                
                print(f"  ✅ Found {len(page_products)} products")
                
            except Exception as e:
                print(f"  ❌ Error processing page {idx}: {e}")
                continue
        
        return products
    
    def _extract_text_enhanced(self, image) -> str:
        """
        Extract text using enhanced OCR settings for Arabic grocery flyers
        """
        # Try configurations optimized for Arabic flyers
        configs = [
            '--oem 1 --psm 6',   # LSTM + uniform block (best for structured flyers)
            '--oem 1 --psm 11',  # LSTM + sparse text
            '--oem 1 --psm 3',   # LSTM + auto
        ]
        
        texts = []
        for config in configs:
            try:
                text = pytesseract.image_to_string(image, lang='ara+eng', config=config)
                texts.append(text)
            except:
                continue
        
        # Return longest result (usually has more useful content)
        return max(texts, key=len) if texts else ""
    
    def _extract_products_enhanced(self, text: str, source_url: str, store: str, page_num: int) -> List[Product]:
        """
        Enhanced product extraction using sliding window for price-name association
        """
        products = []
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 1]
        
        # Noise patterns to filter
        noise_patterns = [
            r'www\.',  r'\.com', r'\.eg',
            self.MONTH_PATTERN,  # Months
            r'خميس|جمعة|سبت|احد|اثنين|ثلاثاء|اربعاء',  # Days
            r'حتى|من|الى',  # Date words
            r'kazyon|كازيون|ماركت|market|bim',  # Store names
        ]
        
        # Arabic product keywords (indicates this is likely a product name)
        product_keywords = [
            'دجاج', 'لحم', 'برجر', 'جبنة', 'زبدة', 'لبن', 'حليب', 'زيت',
            'أرز', 'مكرونة', 'سكر', 'شاي', 'قهوة', 'عصير', 'مياه',
            'صابون', 'شامبو', 'منظف', 'معجون', 'بسكويت', 'شيكولاتة',
            'تونة', 'سمك', 'بيض', 'خضار', 'فاكهة', 'طماطم', 'بطاطس',
            'فول', 'عدس', 'فاصوليا', 'بازلاء', 'ذرة', 'خبز', 'توست',
            'مجمد', 'طازج', 'معلب', 'بانيه', 'صدور', 'اوراك', 'مشكل',
            'كجم', 'جرام', 'لتر', 'مل', 'قطعة', 'علبة', 'كيس', 'عبوة'
        ]
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip noise lines
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in noise_patterns):
                i += 1
                continue
            
            # Try to extract price from current line
            price = self._extract_price_enhanced(line)
            
            if price:
                # Look for product name in surrounding lines
                name_candidates = []
                
                # Check previous 3 lines
                for j in range(max(0, i-3), i):
                    prev_line = lines[j]
                    if self._is_likely_product_name(prev_line, product_keywords, noise_patterns):
                        name_candidates.append((prev_line, i - j))  # (name, distance)
                
                # Check next 2 lines
                for j in range(i+1, min(len(lines), i+3)):
                    next_line = lines[j]
                    if self._is_likely_product_name(next_line, product_keywords, noise_patterns):
                        name_candidates.append((next_line, j - i))
                
                # Sort by distance (prefer closer names)
                name_candidates.sort(key=lambda x: x[1])
                
                if name_candidates:
                    name = name_candidates[0][0]
                    name = self._clean_product_name(name)
                    
                    if name and 3 < len(name) < 100:
                        category_ar, category_en = match_category(name)
                        
                        product = Product(
                            store=store,
                            store_product_id=f"{store}_url_p{page_num}_{len(products)}_{int(time.time())}",
                            name_ar=name,
                            name_en=name,
                            category_ar=category_ar,
                            category_en=category_en,
                            price=price,
                            currency='EGP',
                            in_stock=True,
                            url=source_url,
                            source='url_scraper_ocr',
                            scraped_at=datetime.utcnow()
                        )
                        products.append(product)
                        print(f"    ✓ {name[:40]}... - {price} EGP")
            
            i += 1
        
        return products
    
    def _is_likely_product_name(self, text: str, product_keywords: List[str], noise_patterns: List[str]) -> bool:
        """Check if text is likely a product name"""
        # Must have some Arabic characters
        if not re.search(r'[\u0600-\u06FF]', text):
            return False
        
        # Skip if matches noise patterns
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in noise_patterns):
            return False
        
        # Skip if it's just a number
        if re.match(r'^[\d\s\.,]+$', text):
            return False
        
        # Must be reasonable length
        if len(text) < 3 or len(text) > 100:
            return False
        
        return True

    def _clean_product_name(self, name: str) -> str:
        """
        Clean product name from OCR artifacts specific to Kazyon flyers
        This is more targeted than the generic clean_product_name helper
        and preserves important product information like sizes/quantities
        """
        # Remove English letters mixed in (OCR artifacts)
        name = re.sub(r'[a-zA-Z]{1,3}(?=\s|$)', '', name)
        # Remove excessive punctuation
        name = re.sub(r'[;:,\.\*\+\-\|\[\]\(\)]+', ' ', name)
        # Remove numbers at start/end (but preserve in middle for sizes like "2 كجم")
        name = re.sub(r'^\d+\s*', '', name)
        name = re.sub(r'\s*\d+$', '', name)
        # Clean whitespace
        name = ' '.join(name.split())
        return name.strip()

    def _extract_price_enhanced(self, text: str) -> Optional[float]:
        """
        Enhanced price extraction for Kazyon flyers
        Handles standalone numbers and OCR artifacts
        """
        if not text:
            return None
        
        # Convert Arabic numerals to English
        arabic_to_english = {
            '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
            '٫': '.', '،': ','
        }
        for ar, en in arabic_to_english.items():
            text = text.replace(ar, en)
        
        # Clean OCR artifacts
        text = text.replace(';', '.')  # OCR often reads decimals as semicolons
        text = re.sub(r'[a-zA-Z]+$', '', text)  # Remove trailing letters (e.g., "995 Salg")
        text = re.sub(r'^[a-zA-Z]+', '', text)  # Remove leading letters
        
        # Price patterns - from most specific to least
        patterns = [
            # With currency suffix
            r'(\d+[\.,]?\d*)\s*(?:جنيه|ج\.م|جم|EGP|LE)',
            # Currency before number
            r'(?:جنيه|ج\.م|جم|EGP|LE)\s*(\d+[\.,]?\d*)',
            # Decimal prices (XX.XX or XXX.XX format - common for Egyptian prices)
            r'\b(\d{2,3}\.\d{1,2})\b',
            # Whole number prices (2-4 digits, typical grocery range)
            # Exclude month names to avoid matching dates
            rf'\b(\d{{2,4}})\b(?!\s*(?:{self.MONTH_PATTERN}))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '.')
                try:
                    price = float(price_str)
                    # Validate range for Egyptian groceries
                    if self.MIN_PRICE <= price <= self.MAX_PRICE:
                        return price
                except ValueError:
                    continue
        
        return None
    
    def _save_products(self, products: List[Product]):
        """Save products to database"""
        if not products:
            return
        
        session = self.db_manager.get_session()
        try:
            for product in products:
                # Check if product exists
                existing = session.query(Product).filter_by(
                    store_product_id=product.store_product_id
                ).first()
                
                if existing:
                    # Update existing
                    existing.name_ar = product.name_ar
                    existing.name_en = product.name_en
                    existing.price = product.price
                    existing.category_ar = product.category_ar
                    existing.category_en = product.category_en
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
