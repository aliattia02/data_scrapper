"""
src/main.py - CLI Entry Point for Egyptian Grocery Scraper
"""
import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

from src.scrapers.carrefour import CarrefourScraper
from src.scrapers.metro import MetroScraper
from src.ocr.processor import OCRProcessor
from src.database.manager import DatabaseManager
from src.exporters.json_exporter import JSONExporter
from src.exporters.csv_exporter import CSVExporter
from src.api.app import create_app
import uvicorn


class CLI:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.scrapers = {
            'carrefour': CarrefourScraper(self.db_manager),
            'metro': MetroScraper(self.db_manager)
        }

    async def scrape(self, store: Optional[str] = None):
        """Run scrapers for specified store or all stores"""
        if store == 'all' or store is None:
            print("🛒 Scraping all stores...")
            for name, scraper in self.scrapers.items():
                print(f"\n📍 Starting {name.upper()} scraper...")
                try:
                    products = await scraper.scrape()
                    print(f"✅ Exported to: {output_path}")
        except Exception as e:
        print(f"❌ Export failed: {e}")


def serve(self, host: str = "127.0.0.1", port: int = 8000):
    """Start FastAPI server"""
    print(f"🚀 Starting API server on {host}:{port}")
    print(f"📖 Docs available at: http://{host}:{port}/docs")

    app = create_app(self.db_manager)
    uvicorn.run(app, host=host, port=port)


def db_command(self, action: str):
    """Database management commands"""
    if action == 'init':
        print("🗄️  Initializing database...")
        self.db_manager.init_db()
        print("✅ Database initialized")
    elif action == 'migrate':
        print("🔄 Running migrations...")
        self.db_manager.migrate()
        print("✅ Migration complete")
    elif action == 'clean':
        response = input("⚠️  Delete all data? (yes/no): ")
        if response.lower() == 'yes':
            self.db_manager.clean()
            print("✅ Database cleaned")
        else:
            print("❌ Cancelled")
    else:
        print(f"❌ Unknown action: {action}")


def main():
    parser = argparse.ArgumentParser(
        description='🇪🇬 Egyptian Grocery Scraper - OfferCatalog Backend'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape stores')
    scrape_parser.add_argument(
        '--store',
        choices=['all', 'carrefour', 'metro'],
        default='all',
        help='Store to scrape'
    )

    # OCR command
    ocr_parser = subparsers.add_parser('ocr', help='Process flyers with OCR')
    ocr_parser.add_argument('--input', required=True, help='Input image path')
    ocr_parser.add_argument('--batch', action='store_true', help='Batch process directory')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export data')
    export_parser.add_argument(
        '--format',
        choices=['json', 'csv'],
        default='json',
        help='Export format'
    )
    export_parser.add_argument('--store', help='Filter by store')

    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start API server')
    serve_parser.add_argument('--host', default='127.0.0.1', help='Host address')
    serve_parser.add_argument('--port', type=int, default=8000, help='Port number')

    # Database command
    db_parser = subparsers.add_parser('db', help='Database management')
    db_parser.add_argument(
        'action',
        choices=['init', 'migrate', 'clean'],
        help='Database action'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = CLI()

    try:
        if args.command == 'scrape':
            asyncio.run(cli.scrape(args.store))
        elif args.command == 'ocr':
            cli.ocr(args.input, args.batch)
        elif args.command == 'export':
            cli.export(args.format, args.store)
        elif args.command == 'serve':
            cli.serve(args.host, args.port)
        elif args.command == 'db':
            cli.db_command(args.action)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
    {name}: {len(products)}
    products
    scraped
    ")
    except Exception as e:
    print(f"❌ {name} failed: {e}")
else:
    if store not in self.scrapers:
        print(f"❌ Unknown store: {store}")
        print(f"Available: {', '.join(self.scrapers.keys())}")
        return

print(f"🛒 Scraping {store.upper()}...")
scraper = self.scrapers[store]
try:
    products = await scraper.scrape()
    print(f"✅ Scraped {len(products)} products from {store}")
except Exception as e:
    print(f"❌ Scraping failed: {e}")


def ocr(self, input_path: str, batch: bool = False):
    """Process Kazyon flyers with OCR"""
    processor = OCRProcessor()

    if batch:
        print(f"📸 Batch processing flyers in: {input_path}")
        flyer_dir = Path(input_path)
        if not flyer_dir.exists():
            print(f"❌ Directory not found: {input_path}")
            return

        image_files = list(flyer_dir.glob("*.jpg")) + list(flyer_dir.glob("*.png"))
        print(f"Found {len(image_files)} images")

        for img_path in image_files:
            print(f"\n🔍 Processing: {img_path.name}")
            try:
                products = processor.process_flyer(str(img_path))
                print(f"✅ Extracted {len(products)} products")
            except Exception as e:
                print(f"❌ Failed: {e}")
    else:
        print(f"📸 Processing single flyer: {input_path}")
        try:
            products = processor.process_flyer(input_path)
            print(f"✅ Extracted {len(products)} products")
            print(f"💾 Saved to database")
        except Exception as e:
            print(f"❌ OCR processing failed: {e}")


def export(self, format: str = 'json', store: Optional[str] = None):
    """Export data to JSON or CSV"""
    print(f"📦 Exporting data to {format.upper()}...")

    if format == 'json':
        exporter = JSONExporter(self.db_manager)
    elif format == 'csv':
        exporter = CSVExporter(self.db_manager)
    else:
        print(f"❌ Unknown format: {format}")
        return

    try:
        output_path = exporter.export(store_filter=store)
        print(f"✅