"""
src/scrapers/pdf_scraper.py - PDF Catalogue Scraper (No OCR)
Scrapes catalogue images and merges into PDF for external app usage
"""
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
import img2pdf
from PIL import Image
import io
import time
import re


class PdfScraper:
    """Scrape catalogue images and merge into PDF (no OCR)"""
    
    BASE_URL = 'https://www.filloffer.com'
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Referer': 'https://www.filloffer.com/'
        })
        
        # Create directories
        self.pdf_dir = Path("data/catalogues")
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        
        self.temp_dir = Path("data/temp_images")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.thumbnail_dir = Path("data/thumbnails")
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
    
    def scrape_single_catalogue(self, url: str, metadata: dict) -> dict:
        """
        Download all images from a catalogue page and merge into PDF
        
        Args:
            url: Catalogue URL (e.g., https://www.filloffer.com/markets/Kazyon-Market/.../pdf)
            metadata: {
                "market_category": "supermarket",
                "market_name": "Metro",
                "start_date": "2024-12-01",
                "end_date": "2024-12-08",
                "latitude": 30.0444,
                "longitude": 31.2357
            }
        
        Returns:
            {
                "pdf_path": "...",
                "filename": "...",
                "pages": 7,
                "thumbnail_path": "...",
                "file_size": 1024000
            }
        """
        print(f"📥 Scraping catalogue: {url}")
        
        try:
            # Download catalogue images
            images = self._download_catalogue_images(url)
            
            if not images:
                raise ValueError("No images found in catalogue")
            
            print(f"📄 Downloaded {len(images)} images")
            
            # Generate filename
            filename = self._generate_filename(metadata)
            
            # Merge to PDF
            pdf_path = self._merge_to_pdf(images, filename)
            
            # Generate thumbnail from first image
            thumbnail_path = self._generate_thumbnail(images[0], filename)
            
            # Get file size
            file_size = pdf_path.stat().st_size
            
            # Cleanup temp images
            for img in images:
                try:
                    img.unlink()
                except Exception as e:
                    print(f"Warning: Failed to delete temp file {img}: {e}")
            
            print(f"✅ PDF created: {pdf_path.name} ({file_size / 1024:.1f} KB)")
            
            return {
                "pdf_path": str(pdf_path),
                "filename": filename,
                "pages": len(images),
                "thumbnail_path": str(thumbnail_path),
                "file_size": file_size
            }
            
        except Exception as e:
            print(f"❌ Error scraping catalogue: {e}")
            raise
    
    def scrape_store_catalogues(self, store_url: str, metadata: dict) -> List[dict]:
        """
        Find all catalogue links on a store page and scrape each one
        
        Args:
            store_url: Store page URL (e.g., https://www.filloffer.com/markets/Metro-Markets)
            metadata: Base metadata to use for all catalogues
        
        Returns:
            List of scraped catalogue results
        """
        print(f"🏪 Scraping store: {store_url}")
        
        try:
            # Find all catalogue links
            catalogue_links = self._find_catalogue_links(store_url)
            
            if not catalogue_links:
                raise ValueError("No catalogues found on store page")
            
            print(f"📚 Found {len(catalogue_links)} catalogues")
            
            results = []
            for i, cat_link in enumerate(catalogue_links, 1):
                try:
                    print(f"\n[{i}/{len(catalogue_links)}] Processing: {cat_link['title']}")
                    
                    # Merge metadata
                    cat_metadata = {**metadata}
                    
                    # Extract dates from catalogue if available
                    if cat_link.get('dates'):
                        cat_metadata.update(cat_link['dates'])
                    
                    # Scrape this catalogue
                    result = self.scrape_single_catalogue(cat_link['url'], cat_metadata)
                    result['title'] = cat_link['title']
                    results.append(result)
                    
                    # Be nice to the server
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"❌ Failed to scrape {cat_link['title']}: {e}")
                    continue
            
            print(f"\n✅ Scraped {len(results)}/{len(catalogue_links)} catalogues")
            
            return results
            
        except Exception as e:
            print(f"❌ Error scraping store: {e}")
            raise
    
    def _find_catalogue_links(self, store_url: str) -> List[dict]:
        """
        Parse store page to find all catalogue links
        
        Returns:
            [{"url": "...", "title": "...", "dates": {...}}, ...]
        """
        try:
            response = self.session.get(store_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            catalogues = []
            
            # Find catalogue links - adjust selectors based on actual HTML structure
            # Look for links containing 'pdf' or leading to catalogue pages
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                
                # Check if this is a catalogue link
                if 'offer' in href.lower() or 'catalogue' in href.lower() or 'pdf' in href.lower():
                    full_url = urljoin(self.BASE_URL, href)
                    
                    # Get title
                    title = link.get_text(strip=True) or link.get('title', '')
                    
                    # Try to extract dates from title or nearby elements
                    dates = self._extract_dates_from_text(title)
                    
                    if full_url not in [c['url'] for c in catalogues]:
                        catalogues.append({
                            'url': full_url,
                            'title': title or 'Catalogue',
                            'dates': dates
                        })
            
            return catalogues
            
        except Exception as e:
            print(f"Error finding catalogue links: {e}")
            return []
    
    def _download_catalogue_images(self, url: str) -> List[Path]:
        """
        Download all images from catalogue page
        
        Returns:
            List of paths to downloaded images
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            images = []
            image_urls = []
            
            # Find all image elements
            img_tags = soup.find_all('img')
            
            for img in img_tags:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                
                if not src:
                    continue
                
                # Filter out small images (like icons, logos)
                # Keep only catalogue page images
                if any(skip in src.lower() for skip in ['logo', 'icon', 'banner', 'social']):
                    continue
                
                full_url = urljoin(url, src)
                
                # Avoid duplicates
                if full_url not in image_urls:
                    image_urls.append(full_url)
            
            # Download images
            for i, img_url in enumerate(image_urls, 1):
                try:
                    print(f"  Downloading image {i}/{len(image_urls)}...")
                    
                    img_response = self.session.get(img_url, timeout=30)
                    img_response.raise_for_status()
                    
                    # Save to temp directory
                    img_path = self.temp_dir / f"temp_{int(time.time())}_{i}.jpg"
                    
                    # Convert to JPEG if needed
                    img_data = Image.open(io.BytesIO(img_response.content))
                    
                    # Convert RGBA to RGB if needed
                    if img_data.mode == 'RGBA':
                        img_data = img_data.convert('RGB')
                    
                    # Save as JPEG
                    img_data.save(img_path, 'JPEG', quality=90)
                    
                    images.append(img_path)
                    
                except Exception as e:
                    print(f"  Failed to download image {img_url}: {e}")
                    continue
            
            return images
            
        except Exception as e:
            print(f"Error downloading catalogue images: {e}")
            return []
    
    def _merge_to_pdf(self, images: List[Path], filename: str) -> Path:
        """
        Merge images into single PDF with specified filename
        
        Args:
            images: List of image paths
            filename: Output PDF filename
        
        Returns:
            Path to created PDF
        """
        try:
            pdf_path = self.pdf_dir / filename
            
            # Convert images to PDF using img2pdf
            with open(pdf_path, "wb") as f:
                f.write(img2pdf.convert([str(img) for img in images]))
            
            return pdf_path
            
        except Exception as e:
            print(f"Error merging to PDF: {e}")
            raise
    
    def _generate_thumbnail(self, first_image: Path, filename: str) -> Optional[Path]:
        """
        Generate thumbnail from first page
        
        Args:
            first_image: Path to first image
            filename: Base filename (will create thumbnail with same base)
        
        Returns:
            Path to thumbnail or None if generation fails
        """
        try:
            # Remove .pdf extension and add _thumb.jpg
            thumb_name = filename.replace('.pdf', '_thumb.jpg')
            thumb_path = self.thumbnail_dir / thumb_name
            
            # Open and resize image
            img = Image.open(first_image)
            
            # Calculate thumbnail size (maintain aspect ratio)
            max_size = (300, 400)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Save thumbnail
            img.save(thumb_path, 'JPEG', quality=85)
            
            return thumb_path
            
        except Exception as e:
            import logging
            logging.error(f"Error generating thumbnail: {e}")
            return None
    
    def _generate_filename(self, metadata: dict) -> str:
        """
        Generate filename: {category}_{name}_{start}_{end}.pdf
        
        Args:
            metadata: Catalogue metadata
        
        Returns:
            Filename string
        """
        category = metadata.get('market_category', 'catalogue').lower().replace(' ', '_')
        name = metadata.get('market_name', 'store').lower().replace(' ', '_')
        start = metadata.get('start_date', '').replace('-', '')
        end = metadata.get('end_date', '').replace('-', '')
        
        if start and end:
            filename = f"{category}_{name}_{start}_{end}.pdf"
        else:
            # Fallback to timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{category}_{name}_{timestamp}.pdf"
        
        return filename
    
    def _extract_dates_from_text(self, text: str) -> dict:
        """
        Extract start and end dates from text
        
        Args:
            text: Text potentially containing dates
        
        Returns:
            {"start_date": "2024-12-01", "end_date": "2024-12-08"} or {}
        """
        dates = {}
        
        # Try to find date patterns
        # Example: "1 Dec - 8 Dec" or "01/12 - 08/12"
        
        # Pattern: DD/MM - DD/MM
        pattern1 = r'(\d{1,2})/(\d{1,2})\s*-\s*(\d{1,2})/(\d{1,2})'
        match1 = re.search(pattern1, text)
        
        if match1:
            # Assume current year
            year = datetime.now().year
            start_day, start_month, end_day, end_month = match1.groups()
            
            dates['start_date'] = f"{year}-{int(start_month):02d}-{int(start_day):02d}"
            dates['end_date'] = f"{year}-{int(end_month):02d}-{int(end_day):02d}"
        
        return dates
