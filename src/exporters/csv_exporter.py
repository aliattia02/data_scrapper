"""
src/exporters/csv_exporter.py - Export data to CSV
"""
import csv
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.database.models import Product


class CSVExporter:
    """Export products to CSV format"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.output_dir = Path("data/exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, store_filter: Optional[str] = None) -> str:
        """
        Export products to CSV file
        Returns: path to exported file
        """
        session = self.db_manager.get_session()

        try:
            query = session.query(Product)

            if store_filter:
                query = query.filter(Product.store == store_filter.lower())

            products = query.all()

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            store_suffix = f"_{store_filter}" if store_filter else "_all"
            filename = f"products{store_suffix}_{timestamp}.csv"

            output_path = self.output_dir / filename

            # Write CSV file
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                # Write header
                writer.writerow([
                    'ID', 'Store', 'Product ID',
                    'Name (AR)', 'Name (EN)', 'Brand',
                    'Category (AR)', 'Category (EN)',
                    'Price', 'Original Price', 'Discount %', 'Currency',
                    'Size', 'Unit', 'In Stock',
                    'Image URL', 'Product URL',
                    'Source', 'Scraped At', 'Updated At'
                ])

                # Write products
                for product in products:
                    writer.writerow([
                        product.id,
                        product.store,
                        product.store_product_id,
                        product.name_ar,
                        product.name_en,
                        product.brand,
                        product.category_ar,
                        product.category_en,
                        product.price,
                        product.original_price,
                        product.discount_percentage,
                        product.currency,
                        product.size,
                        product.unit,
                        product.in_stock,
                        product.image_url,
                        product.url,
                        product.source,
                        product.scraped_at.isoformat() if product.scraped_at else '',
                        product.updated_at.isoformat() if product.updated_at else ''
                    ])

            return str(output_path)

        finally:
            session.close()