# URL-Based Scraper - Implementation Summary

## Overview
This implementation adds a URL-based scraper that allows users to scrape specific catalogue URLs from filloffer.com with enhanced OCR processing and better price extraction.

## Key Features

### 1. URL-Based Scraping
- Accept specific catalogue URLs as input via frontend or API
- Download all catalogue page images with retry logic
- Combine images into PDF files for storage
- Track scraping jobs with status updates

### 2. Enhanced OCR Processing
- **Image Preprocessing**:
  - Automatic upscaling for small images
  - Deskewing using Hough transform
  - Noise removal with Non-local Means Denoising
  - Otsu's binarization for better text contrast
  
- **OCR Configuration**:
  - LSTM Neural Net engine (--oem 1) for better accuracy
  - Sparse text mode (--psm 11) for flyer layouts
  - Multi-pass OCR with different configurations
  - Support for both Arabic and English text

### 3. Improved Product Extraction
- Better price pattern matching for Egyptian prices (ج.م, جنيه, EGP, LE)
- Price validation (1-10000 EGP range for groceries)
- Noise filtering (store names, dates, website URLs)
- Better Arabic product name cleaning

### 4. Job Tracking
- Database model for tracking scrape jobs
- Status: pending → downloading → processing_ocr → completed/failed
- Progress metrics: pages downloaded, processed, products found
- Error tracking

## Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

Required new packages:
- `img2pdf==0.5.0` - For converting images to PDF
- `aiohttp==3.9.4` - For async HTTP requests (patched for security vulnerabilities)

### 2. Install System Dependencies

**Tesseract OCR** (required for text extraction):
- Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-ara`
- macOS: `brew install tesseract tesseract-lang`
- Windows: Download from https://github.com/tesseract-ocr/tesseract

**Poppler** (required for PDF processing):
- Linux: `sudo apt-get install poppler-utils`
- macOS: `brew install poppler`
- Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/

### 3. Run Database Migration
```bash
python db_migration_scrape_jobs.py
```

This creates the `scrape_jobs` table to track scraping jobs.

## API Endpoints

### Scrape Specific URL
```
POST /api/v1/scraper/scrape-url
Content-Type: application/json

{
  "url": "https://www.filloffer.com/markets/Kazyon-Market/.../pdf",
  "store": "kazyon"  // optional, auto-detected from URL
}

Response:
{
  "status": "completed",
  "job_id": 123,
  "products_found": 45,
  "pages_processed": 12,
  "pdf_path": "/path/to/pdf"
}
```

### Get Job Status
```
GET /api/v1/scraper/jobs/{job_id}

Response:
{
  "id": 123,
  "sourceUrl": "https://...",
  "store": "kazyon",
  "status": "completed",
  "totalPages": 12,
  "pagesDownloaded": 12,
  "pagesProcessed": 12,
  "productsFound": 45,
  "pdfPath": "/path/to/pdf",
  "createdAt": "2024-12-08T...",
  "completedAt": "2024-12-08T...",
  "durationSeconds": 45.2
}
```

### List Jobs
```
GET /api/v1/scraper/jobs?skip=0&limit=50

Response: [
  { /* job object */ },
  ...
]
```

## Frontend Usage

1. Navigate to the "Scrapers" page
2. Enter a filloffer.com catalogue URL in the "Scrape Specific Catalogue URL" section
3. Select the store (or leave for auto-detection)
4. Click "Scrape URL"
5. Monitor progress in the logs panel

### Example URLs
- https://www.filloffer.com/markets/Kazyon-Market/new-offers-from-Kazyon-market-starting-from-4-december-8-december/pdf
- https://www.filloffer.com/markets/Kazyon-Market/new-offers-from-Kazyon-market-Weekend-starting-from-2-december-to-8-december/pdf

## Testing

### Run Tests
```bash
# Test URL scraper with specific Kazyon URLs
python test_filloffer.py --mode url

# Test general scraper
python test_filloffer.py --mode general

# Test both
python test_filloffer.py --mode both
```

### Expected Output
- Downloaded images in `data/catalogue_images/`
- Generated PDFs in `data/pdfs/`
- OCR text files alongside images (*.txt)
- Products saved to database

## Architecture

### File Structure
```
src/
├── scrapers/
│   ├── url_scraper.py          # NEW: URL-based scraper
│   ├── filloffer.py            # Existing: General scraper
│   └── base.py
├── ocr/
│   ├── processor.py            # UPDATED: Enhanced OCR
│   ├── kazyon_parser.py        # UPDATED: Better parsing
│   └── image_preprocessor.py   # NEW: Advanced preprocessing
├── api/
│   └── routes.py               # UPDATED: New endpoints
└── database/
    └── models.py               # UPDATED: ScrapeJob model

frontend/
└── src/
    ├── pages/
    │   └── Scrapers.tsx        # UPDATED: URL input UI
    └── services/
        └── api.ts              # UPDATED: New API functions
```

### Data Flow
1. User inputs URL → Frontend sends to `/scrape-url` endpoint
2. URLScraper creates ScrapeJob (status: pending)
3. Download images (status: downloading)
4. Convert to PDF
5. Process with enhanced OCR (status: processing_ocr)
6. Extract products with validation
7. Save to database (status: completed)

## Security

### Security Scan Results
✅ **No security vulnerabilities found** in CodeQL analysis for both Python and JavaScript code.
✅ **All dependency vulnerabilities patched** - aiohttp updated to 3.9.4 to fix:
  - CVE-2024-23334: Denial of Service vulnerability when parsing malformed POST requests
  - Directory traversal vulnerability (< 3.9.2)

### Security Considerations
- URL validation to prevent SSRF attacks
- Timeout handling to prevent hanging requests
- Price validation to filter out unrealistic values
- Input sanitization for product names
- Database transaction handling with rollback on errors

## Known Limitations

1. **OCR Accuracy**: While improved, OCR on scanned flyers may still have errors
2. **Network Dependency**: Requires stable internet connection for downloading images
3. **Processing Time**: Large catalogues may take several minutes to process
4. **Language Support**: Currently optimized for Arabic + English only

## Future Improvements

1. Add pagination support for very large catalogues
2. Implement async/parallel image downloads with aiohttp
3. Add product image extraction and storage
4. Improve OCR with machine learning-based post-processing
5. Add webhook notifications for job completion
6. Implement retry logic for failed jobs

## Troubleshooting

### No products found
- Check if PDFs/images are downloading to `data/pdfs/` and `data/catalogue_images/`
- Verify Tesseract is installed: `tesseract --version`
- Check Arabic language pack: `tesseract --list-langs` (should show 'ara')
- Review OCR text files (*.txt) to see what was extracted

### OCR not working
- Install Tesseract OCR with Arabic support
- Verify language pack: `tesseract --list-langs`
- Check image quality in `data/catalogue_images/`

### PDF conversion fails
- Install Poppler utilities
- Verify: `pdftoppm -v` (Linux/macOS) or check PATH on Windows

### Import errors
- Install all dependencies: `pip install -r requirements.txt`
- Install system packages (Tesseract, Poppler)

## Support

For issues or questions:
1. Check the logs in the frontend logs panel
2. Review the `scrape_jobs` table for error details
3. Check OCR text output files (*.txt) in image directories
4. Verify dependencies are installed correctly
