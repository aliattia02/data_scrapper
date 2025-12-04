"""
src/exporters/json_exporter.py - Export data to JSON for mobile app
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.database.models import Product


class JSONExporter:
    """Export products to JSON format for React Native app"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.output_dir = Path("data/exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, store_filter: Optional[str] = None) -> str:
        """
        Export products to JSON file
        Returns: path to exported file
        """
        session = self.db_manager.get_session()

        try:
            query = session.query(Product)

            if store_filter:
                query = query.filter(Product.store == store_filter.lower())

            products = query.all()

            # Convert to dictionaries
            data = {
                "metadata": {
                    "exported_at": datetime.utcnow().isoformat(),
                    "total_products": len(products),
                    "store_filter": store_filter,
                    "version": "1.0.0"
                },
                "products": [product.to_dict() for product in products]
            }

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            store_suffix = f"_{store_filter}" if store_filter else "_all"
            filename = f"products{store_suffix}_{timestamp}.json"

            output_path = self.output_dir / filename

            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return str(output_path)

        finally:
            session.close()

    def export_by_store(self) -> dict:
        """
        Export separate JSON files for each store
        Returns: {store_name: file_path}
        """
        session = self.db_manager.get_session()

        try:
            from sqlalchemy import distinct

            stores = session.query(distinct(Product.store)).all()
            results = {}

            for (store_name,) in stores:
                output_path = self.export(store_filter=store_name)
                results[store_name] = output_path

            return results

        finally:
            session.close()