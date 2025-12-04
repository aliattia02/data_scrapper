"""
src/scrapers/carrefour.py - Carrefour Egypt Scraper
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import List
from datetime import datetime

from src.scrapers.base import BaseScraper
from src.database.models import Product
from src.utils.categories import match_category
from src.utils.helpers import extract_price, clean_product_name

class CarrefourScraper(BaseScraper):
    """Scraper for Carrefour Egypt website"""
    
    STORE_NAME = 'carrefour'
    BASE_URL = 'https://www.carrefouregypt.com'
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.driver = None
    
    def _init_driver(self):
        """Initialize Selenium WebDriver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
    
    def scrape(self) -> List[Product]:
        """Main scraping method"""
        self.start_log()
        products = []
        
        try:
            self._init_driver()
            
            # Navigate to offers page
            self.driver.get(f'{self.BASE_URL}/mafegy/en/offers')
            time.sleep(3)
            
            # Find product elements
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, '.product-item, .product-card')
            
            for idx, elem in enumerate(product_elements[:50]):  # Limit to 50 for testing
                try:
                    product = self._parse_product_element(elem, idx)
                    if product:
                        products.append(product)
                except Exception as e:
                    self.log_error(f'Failed to parse product {idx}: {e}')
            
            # Save products
            self._save_products(products)
            self.complete_log(len(products), 'completed')
            
        except Exception as e:
            self.log_error(f'Scraping failed: {e}')
            self.complete_log(len(products), 'failed')
        finally:
            if self.driver:
                self.driver.quit()
        
        return products
    
    def _parse_product_element(self, elem, idx) -> Product:
        """Parse product from HTML element"""
        try:
            # Extract name
            name_elem = elem.find_element(By.CSS_SELECTOR, '.product-name, .product-title, h3, h4')
            name = clean_product_name(name_elem.text)
            
            # Extract price
            price_elem = elem.find_element(By.CSS_SELECTOR, '.price, .product-price')
            price_text = price_elem.text
            price = extract_price(price_text)
            
            if not price:
                return None
            
            # Extract image
            try:
                img_elem = elem.find_element(By.CSS_SELECTOR, 'img')
                image_url = img_elem.get_attribute('src')
            except:
                image_url = None
            
            # Extract product URL
            try:
                link_elem = elem.find_element(By.CSS_SELECTOR, 'a')
                product_url = link_elem.get_attribute('href')
            except:
                product_url = None
            
            # Match category
            category_ar, category_en = match_category(name)
            
            # Create product
            product = Product(
                store=self.STORE_NAME,
                store_product_id=f'carrefour_{idx}_{int(time.time())}',
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
