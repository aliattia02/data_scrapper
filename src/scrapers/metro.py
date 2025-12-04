"""
src/scrapers/metro.py - Metro Markets Egypt Scraper
"""
import requests
from bs4 import BeautifulSoup
import time
from typing import List
from datetime import datetime

from src.scrapers.base import BaseScraper
from src.database.models import Product
from src.utils.categories import match_category
from src.utils.helpers import extract_price, clean_product_name

class MetroScraper(BaseScraper):
    """Scraper for Metro Markets Egypt"""
    
    STORE_NAME = 'metro'
    BASE_URL = 'https://www.metro-markets.com'
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    async def scrape(self) -> List[Product]:
        """Main scraping method"""
        self.start_log()
        products = []
        
        try:
            # Get offers page
            response = self.session.get(f'{self.BASE_URL}/en/offers', timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find product elements
            product_elements = soup.select('.product-item, .product-card, .offer-item')
            
            for idx, elem in enumerate(product_elements[:50]):  # Limit for testing
                try:
                    product = self._parse_product_element(elem, idx)
                    if product:
                        products.append(product)
                except Exception as e:
                    self.log_error(f'Failed to parse product {idx}: {e}')
                
                time.sleep(0.5)  # Rate limiting
            
            # Save products
            self._save_products(products)
            self.complete_log(len(products), 'completed')
            
        except Exception as e:
            self.log_error(f'Scraping failed: {e}')
            self.complete_log(len(products), 'failed')
        
        return products
    
    def _parse_product_element(self, elem, idx) -> Product:
        """Parse product from BeautifulSoup element"""
        try:
            # Extract name
            name_elem = elem.select_one('.product-name, .product-title, h3, h4')
            if not name_elem:
                return None
            name = clean_product_name(name_elem.text)
            
            # Extract price
            price_elem = elem.select_one('.price, .product-price')
            if not price_elem:
                return None
            price = extract_price(price_elem.text)
            
            if not price:
                return None
            
            # Extract image
            img_elem = elem.select_one('img')
            image_url = img_elem.get('src') if img_elem else None
            
            # Extract product URL
            link_elem = elem.select_one('a')
            product_url = link_elem.get('href') if link_elem else None
            if product_url and not product_url.startswith('http'):
                product_url = self.BASE_URL + product_url
            
            # Match category
            category_ar, category_en = match_category(name)
            
            # Create product
            product = Product(
                store=self.STORE_NAME,
                store_product_id=f'metro_{idx}_{int(time.time())}',
                name_ar=name,
                name_en=name,
                category_ar=category_ar,
                category_en=category_en,
                price=price,
                currency='EGP',
                in_stock=True,
                image_url=image_url,
                url=product_url,
                source='scraper',
                scraped_at=datetime.utcnow()
            )
            
            return product
            
        except Exception as e:
            raise Exception(f'Parse error: {e}')
