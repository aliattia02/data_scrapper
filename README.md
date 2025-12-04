# 🇪🇬 Egyptian Supermarket Data Scraper

Complete Python backend and React admin dashboard for scraping Egyptian supermarket data (Kazyon, Carrefour, Metro) with OCR support, REST API, and automated exports for the **OfferCatalog** mobile app.

## 🛠️ Tech Stack

### Backend
- **Scrapers**: Selenium (Carrefour) + BeautifulSoup (Metro)
- **OCR**: Pytesseract + OpenCV + pdf2image (Kazyon flyers)
- **Database**: SQLite + SQLAlchemy
- **API**: FastAPI + Uvicorn
- **Export**: JSON/CSV for mobile app
- **Automation**: GitHub Actions (daily scraping at 6 AM Egypt time)

### Frontend (Coming Soon)
- **Framework**: Vite + React 18 + TypeScript
- **Styling**: Tailwind CSS
- **State**: React Query + Axios
- **Routing**: React Router

## 🚀 Quick Start

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-ara chromium-chromedriver

# macOS
brew install tesseract tesseract-lang chromedriver
```

### Installation

```bash
# Clone repository
git clone https://github.com/aliattia02/data_scrapper.git
cd data_scrapper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database with seed data
python -m src.main db init
```

### Usage

```bash
# Run scrapers
python -m src.main scrape --store all           # All stores
python -m src.main scrape --store carrefour     # Carrefour only
python -m src.main scrape --store metro         # Metro only

# Process Kazyon flyers with OCR
python -m src.main ocr --input ./data/flyers/kazyon.jpg
python -m src.main ocr --input ./data/flyers --batch

# Export data for mobile app
python -m src.main export --format json         # JSON export
python -m src.main export --format csv          # CSV export
python -m src.main export --format json --store kazyon  # Filter by store

# Start API server
python -m src.main serve --host 0.0.0.0 --port 8000
# Access API docs at: http://localhost:8000/docs
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# API will be available at http://localhost:8000
```

## 📱 API Endpoints

### Mobile App Endpoints (Existing)
- `GET /products` - List products with filters
- `GET /products/{id}` - Get single product
- `GET /products/search?q={query}` - Search products
- `GET /stores` - List available stores
- `GET /categories` - List categories (AR/EN)
- `GET /deals` - Get best deals
- `GET /stats` - Overall statistics

### Admin Dashboard Endpoints (New)
- `GET/POST /api/v1/stores` - Store management
- `GET /api/v1/stores/{store_id}/branches` - Store branches
- `GET/POST /api/v1/categories` - Category management
- `GET/POST /api/v1/products` - Product management
- `GET/POST /api/v1/offers` - Offer management
- `GET/POST /api/v1/catalogues` - Catalogue management
- `POST /api/v1/catalogues/{id}/upload` - Upload PDF/images
- `POST /api/v1/catalogues/{id}/process` - Run OCR on catalogue
- `GET /api/v1/export/app` - Export for mobile app
- `POST /api/v1/scraper/run` - Trigger scrapers

## 🗃️ Database Schema

### Core Models
- **Store**: Supermarket chains (Kazyon, Carrefour, Metro)
- **Branch**: Store locations (Zagazig branches)
- **Category**: Product categories (12 categories - Dairy, Meat, Oils, etc.)
- **Product**: Product information with pricing
- **Offer**: Special deals and promotions
- **Catalogue**: Store flyers/catalogues (PDF/images)
- **CataloguePage**: Individual catalogue pages with OCR text
- **ScrapingLog**: Scraping operation tracking

### Seed Data (Zagazig Focus)

#### Stores
- كازيون (Kazyon)
- كارفور (Carrefour)
- مترو (Metro)

#### Zagazig Branches
- **كازيون**: شارع الجلاء، شارع أحمد عرابي، شارع الجمهورية
- **كارفور**: مول الزقازيق

#### Categories (Arabic + English)
Dairy, Meat, Oils, Grains, Beverages, Snacks, Household, Personal Care, Baby, Frozen, Bakery, Vegetables

## 📂 Project Structure

```
data_scrapper/
├── src/
│   ├── main.py              # CLI entry point
│   ├── config.py            # Configuration management
│   ├── models/              # (Reserved)
│   ├── scrapers/            # Store scrapers
│   │   ├── base.py          # Base scraper class
│   │   ├── carrefour.py     # Carrefour scraper (Selenium)
│   │   └── metro.py         # Metro scraper (BeautifulSoup)
│   ├── ocr/                 # OCR processing
│   │   ├── processor.py     # Main OCR processor
│   │   └── kazyon_parser.py # Kazyon-specific parser
│   ├── database/            # SQLAlchemy models
│   │   ├── models.py        # ORM models
│   │   └── manager.py       # Database manager + seed data
│   ├── api/                 # FastAPI app
│   │   ├── app.py           # FastAPI application
│   │   └── routes.py        # API routes
│   ├── exporters/           # Data exporters
│   │   ├── json_exporter.py # JSON export for mobile app
│   │   └── csv_exporter.py  # CSV export
│   └── utils/               # Utilities
│       ├── categories.py    # Category definitions
│       └── helpers.py       # Helper functions
├── data/
│   ├── flyers/              # Input images/PDFs
│   ├── exports/             # JSON/CSV outputs
│   └── database/            # SQLite database
├── frontend/                # React admin dashboard (coming soon)
├── tests/                   # Tests
├── .github/workflows/       # GitHub Actions
├── docker-compose.yml       # Docker Compose config
├── Dockerfile               # Docker config
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## 🔄 Automated Scraping

GitHub Actions workflow runs daily at 6 AM Egypt time:
1. Scrapes all stores (Carrefour, Metro)
2. Processes Kazyon flyers with OCR
3. Exports fresh JSON/CSV
4. Uploads artifacts
5. Commits and pushes updated data

## 📱 Mobile App Export Format

```json
{
  "metadata": {
    "exported_at": "2024-12-04T12:00:00Z",
    "total_products": 150,
    "store_filter": null,
    "version": "1.0.0"
  },
  "products": [
    {
      "id": 1,
      "storeProductId": "carrefour_123",
      "store": "carrefour",
      "nameAr": "حليب المراعي",
      "nameEn": "Almarai Milk",
      "categoryAr": "ألبان",
      "categoryEn": "Dairy",
      "price": 25.99,
      "originalPrice": 29.99,
      "discountPercentage": 13.34,
      "currency": "EGP",
      "size": "1L",
      "inStock": true,
      "imageUrl": "https://...",
      "source": "scraper",
      "scrapedAt": "2024-12-04T10:30:00Z"
    }
  ]
}
```

## 🔗 Connected Repository

This scraper feeds data to: **[aliattia02/OfferCatalog](https://github.com/aliattia02/OfferCatalog)** (React Native mobile app)

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src
```

## 📝 Development Roadmap

- [x] Python backend with scrapers
- [x] SQLAlchemy models and database
- [x] OCR processing with Tesseract
- [x] FastAPI REST API
- [x] JSON/CSV exporters
- [x] GitHub Actions automation
- [x] Docker support
- [ ] React admin dashboard
- [ ] PDF to images conversion
- [ ] Enhanced error handling
- [ ] Comprehensive test coverage
- [ ] API authentication
- [ ] Rate limiting
- [ ] Caching layer

## 📄 License

MIT

## 👤 Author

**Ali Attia**
- GitHub: [@aliattia02](https://github.com/aliattia02)
