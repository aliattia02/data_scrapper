"""
src/scrapers/base.py - Base Scraper Class
"""
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime

from src.database.models import Product, ScrapingLog


class BaseScraper(ABC):
    """Base class for all store scrapers"""

    STORE_NAME = None
    BASE_URL = None

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_log = None
        self.errors = []

    @abstractmethod
    async def scrape(self) -> List[Product]:
        """
        Main scraping method - must be implemented by subclasses
        Returns list of Product objects
        """
        pass

    def start_log(self):
        """Create a new scraping log entry"""
        session = self.db_manager.get_session()

        try:
            self.current_log = ScrapingLog(
                store=self.STORE_NAME,
                status='running',
                started_at=datetime.utcnow()
            )
            session.add(self.current_log)
            session.commit()
            session.refresh(self.current_log)
        finally:
            session.close()

    def complete_log(self, products_count: int, status: str):
        """Complete the scraping log"""
        if not self.current_log:
            return

        session = self.db_manager.get_session()

        try:
            log = session.query(ScrapingLog).filter_by(
                id=self.current_log.id
            ).first()

            if log:
                log.status = status
                log.products_scraped = products_count
                log.completed_at = datetime.utcnow()

                if log.started_at:
                    duration = (log.completed_at - log.started_at).total_seconds()
                    log.duration_seconds = duration

                if self.errors:
                    log.errors = '\n'.join(self.errors)

                session.commit()
        finally:
            session.close()

    def log_error(self, error: str):
        """Add error to the log"""
        self.errors.append(error)

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
                    # Update existing product
                    existing.name_ar = product.name_ar
                    existing.name_en = product.name_en
                    existing.price = product.price
                    existing.original_price = product.original_price
                    existing.discount_percentage = product.discount_percentage
                    existing.in_stock = product.in_stock
                    existing.image_url = product.image_url
                    existing.url = product.url
                    existing.updated_at = datetime.utcnow()
                else:
                    # Add new product
                    session.add(product)

            session.commit()

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()