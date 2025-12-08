"""
test_filloffer_improved.py - Test the improved scraper
"""
from src.database.manager import DatabaseManager
from src.scrapers.filloffer import FillofferScraperImproved
from src.scrapers.url_scraper import URLScraper
import sys


# Test URLs for Kazyon Market
TEST_URLS = [
    "https://www.filloffer.com/markets/Kazyon-Market/new-offers-from-Kazyon-market-starting-from-4-december-8-december/pdf",
    "https://www.filloffer.com/markets/Kazyon-Market/new-offers-from-Kazyon-market-Weekend-starting-from-2-december-to-8-december/pdf"
]


def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...\n")

    issues = []

    # Check Tesseract
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR: v{version}")

        try:
            langs = pytesseract.get_languages()
            if 'ara' in langs:
                print(f"✅ Arabic language pack: installed")
            else:
                print(f"⚠️  Arabic language pack: NOT installed")
                issues.append("Install Arabic: tesseract-ocr-ara")
        except:
            print(f"⚠️  Could not check language packs")
    except ImportError:
        print("❌ pytesseract: NOT installed")
        issues.append("Install: pip install pytesseract")
    except Exception as e:
        print(f"❌ Tesseract: NOT found ({e})")
        issues.append("Install Tesseract OCR")

    # Check PIL/Pillow
    try:
        from PIL import Image
        import PIL
        print(f"✅ Pillow: v{PIL.__version__}")
    except ImportError:
        print("❌ Pillow: NOT installed")
        issues.append("Install: pip install pillow")

    # Check pdf2image
    try:
        import pdf2image
        print(f"✅ pdf2image: installed")

        # Try to check poppler
        try:
            from pdf2image.exceptions import PDFInfoNotInstalledError
            print("   ℹ️  Make sure poppler is installed for PDF conversion")
        except:
            pass
    except ImportError:
        print("⚠️  pdf2image: NOT installed")
        issues.append("Install: pip install pdf2image")
        print("   Also install poppler-utils (Linux) or download poppler for Windows")

    # Check other dependencies
    try:
        import requests
        print(f"✅ requests: installed")
    except ImportError:
        print("❌ requests: NOT installed")
        issues.append("Install: pip install requests")

    try:
        from bs4 import BeautifulSoup
        print(f"✅ BeautifulSoup: installed")
    except ImportError:
        print("❌ BeautifulSoup: NOT installed")
        issues.append("Install: pip install beautifulsoup4 lxml")

    if issues:
        print(f"\n⚠️  Issues found:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print(f"\n✅ All dependencies OK!\n")
        return True


def test_scraper():
    """Test the improved scraper"""
    print("🚀 Testing Improved Filloffer Scraper\n")

    try:
        db_manager = DatabaseManager()
        scraper = FillofferScraperImproved(db_manager, target_store='kazyon')

        print("Starting scrape with PDF download approach...")
        print("=" * 70)

        products = scraper.scrape()

        print("\n" + "=" * 70)
        print(f"\n✅ Scraping completed!")
        print(f"📦 Total products found: {len(products)}")

        if products:
            print("\n📋 Sample products:")
            for i, p in enumerate(products[:10], 1):
                print(f"{i:2d}. {p.name_ar[:60]}")
                print(f"     Price: {p.price} {p.currency}")
                print(f"     Category: {p.category_ar}")
                print()
        else:
            print("\n⚠️  No products found.")
            print("\nDebugging tips:")
            print("  1. Check data/pdfs/ for downloaded PDFs")
            print("  2. Check data/flyers/ for converted images")
            print("  3. Check .txt files for OCR output")
            print("  4. Verify Arabic language pack: tesseract --list-langs")

        return len(products)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0


def test_url_scraper():
    """Test the URL-based scraper with specific Kazyon URLs"""
    print("🚀 Testing URL Scraper with Kazyon Market URLs\n")

    try:
        db_manager = DatabaseManager()
        scraper = URLScraper(db_manager)

        total_products = 0

        for i, url in enumerate(TEST_URLS, 1):
            print(f"\n{'='*70}")
            print(f"Testing URL {i}/{len(TEST_URLS)}")
            print(f"{'='*70}")
            print(f"URL: {url}\n")

            try:
                result = scraper.scrape_url(url, store='kazyon')
                
                print(f"\n✅ URL scraping completed!")
                print(f"  Status: {result['status']}")
                print(f"  Job ID: {result['job_id']}")
                print(f"  Products found: {result['products_found']}")
                print(f"  Pages processed: {result['pages_processed']}")
                print(f"  PDF saved: {result['pdf_path']}")
                
                total_products += result['products_found']

            except Exception as e:
                print(f"\n❌ Error processing URL {i}: {e}")
                import traceback
                traceback.print_exc()

        print(f"\n{'='*70}")
        print(f"Total products from all URLs: {total_products}")
        print(f"{'='*70}")

        return total_products

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """Main test function"""
    print("=" * 70)
    print("IMPROVED FILLOFFER SCRAPER TEST")
    print("=" * 70)
    print()

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test Filloffer scrapers')
    parser.add_argument('--mode', choices=['url', 'general', 'both'], default='both',
                       help='Test mode: url (specific URLs), general (scrape from main page), or both')
    args = parser.parse_args()

    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Please install missing dependencies before running the scraper.")
        print("\nRequired installations:")
        print("  pip install pytesseract pillow pdf2image beautifulsoup4 lxml requests img2pdf")
        print("\nAlso install:")
        print("  - Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
        print("  - Poppler: https://github.com/oschwartz10612/poppler-windows/releases/")
        sys.exit(1)

    # Run migration check
    print("🔧 Checking database schema...")
    try:
        from db_migration_catalogues import migrate_catalogues_table
        migrate_catalogues_table()
    except ImportError:
        print("⚠️  Migration script not found")

    print()

    # Run tests based on mode
    product_count = 0
    
    if args.mode in ['url', 'both']:
        print("\n" + "=" * 70)
        print("TEST MODE: URL Scraper")
        print("=" * 70)
        product_count += test_url_scraper()
    
    if args.mode in ['general', 'both']:
        print("\n" + "=" * 70)
        print("TEST MODE: General Scraper")
        print("=" * 70)
        product_count += test_scraper()

    # Final summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total products scraped: {product_count}")

    if product_count > 0:
        print("Status: ✅ SUCCESS")
        print("\n📁 Check these folders:")
        print("  • data/pdfs/ - Downloaded PDF files")
        print("  • data/catalogue_images/ - Downloaded images from URL scraper")
        print("  • data/flyers/ - Converted images from general scraper")
        print("  • data/*/*.txt - OCR text output")
    else:
        print("Status: ⚠️  NO PRODUCTS FOUND")

    print("=" * 70)


if __name__ == '__main__':
    main()