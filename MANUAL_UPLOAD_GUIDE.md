# Manual Catalogue Upload - User Guide

## Overview

The manual upload feature allows users to upload their own catalogue images or PDFs for automatic OCR processing. This addresses issues with poor OCR results from rotated/tilted images and provides flexibility when catalogues aren't available through automated scraping.

## Features

### 🎯 Core Capabilities
- **Multiple image uploads**: Upload multiple .jpg or .png images that will be merged into a single PDF
- **Direct PDF upload**: Upload PDF catalogues directly for processing
- **Mixed uploads**: Combine images and PDFs in a single upload
- **Store association**: Link uploads to specific stores (Kazyon, Carrefour, Metro, Lulu, or Other)
- **Date tracking**: Optionally specify offer validity period
- **Automatic OCR**: Uploaded files are automatically processed with enhanced OCR

### 🔧 OCR Improvements
- **Rotation detection**: Automatically detects and corrects image rotation using Tesseract OSD
- **Improved deskewing**: Uses text-line detection for more accurate straightening
- **Color preservation**: Optional color preservation for flyers with important color information
- **Better accuracy**: Addresses issues with incomplete product names and garbled text

## How to Use

### Step-by-Step Instructions

1. **Navigate to Scrapers Page**
   - Open the Egyptian Grocery Admin dashboard
   - Click on "Scrapers" in the navigation menu

2. **Locate Manual Upload Section**
   - Scroll down to the "Manual Catalogue Upload" section (purple icon)

3. **Select Files**
   - Click "Choose File" button
   - Select one or more files:
     - Images: .jpg, .jpeg, .png
     - PDFs: .pdf
   - You can select multiple images or a single PDF
   - File selection feedback will show the count

4. **Choose Store**
   - Select the store from the dropdown:
     - Kazyon
     - Carrefour
     - Metro
     - Lulu
     - Other

5. **Set Date Range (Optional)**
   - **Valid From**: Select the offer start date
   - **Valid Until**: Select the offer end date
   - Leave blank if dates are unknown

6. **Upload & Process**
   - Click "Upload & Process" button
   - Wait for processing to complete
   - Progress indicator will show activity

7. **View Results**
   - Check the "Scraping Logs" panel at the bottom
   - Results will show:
     - Products extracted count
     - Pages processed count
     - Catalogue ID for reference

## Technical Details

### Upload Workflow

```
User selects files
    ↓
Frontend validates file types
    ↓
FormData sent to API endpoint
    ↓
Backend receives multipart data
    ↓
Images merged to PDF (if needed)
    ↓
OCR preprocessing applied:
  - Rotation detection
  - Deskewing
  - Denoising
  - Optional binarization
    ↓
Products extracted from text
    ↓
Saved to database with catalogue record
    ↓
Results returned to frontend
```

### Image Processing Pipeline

1. **Upscale**: Ensures minimum 1000x1000 resolution for better OCR
2. **Rotation Detection**: Uses Tesseract OSD to detect orientation
3. **Deskew**: Text-line based method for accurate straightening
4. **Denoise**: Non-local means denoising for cleaner text
5. **Binarize**: Optional black/white conversion (can skip for colored flyers)

### API Endpoint

- **URL**: `POST /api/v1/scraper/upload-catalogue`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `files`: Array of files (required)
  - `store`: Store identifier (required)
  - `valid_from`: ISO date string (optional)
  - `valid_until`: ISO date string (optional)
- **Response**:
  ```json
  {
    "status": "completed",
    "catalogue_id": 123,
    "pdf_path": "/path/to/merged.pdf",
    "products_extracted": 45,
    "pages_processed": 12
  }
  ```

## Troubleshooting

### Upload Fails
- **Check file format**: Only .jpg, .jpeg, .png, and .pdf are accepted
- **Check file size**: Very large files may timeout
- **Check connection**: Ensure API server is running on port 8000

### No Products Extracted
- **Check image quality**: Low-resolution images may not OCR well
- **Check text visibility**: Ensure text is clearly visible and not too small
- **Check language**: OCR is configured for Arabic + English text

### Rotated Images Still Incorrect
- **OSD requires sufficient text**: Very small or sparse text may not detect rotation
- **Manual rotation**: Pre-rotate images before upload if OSD fails

### Products Incomplete or Garbled
- **Check image quality**: Blurry or low-contrast images reduce accuracy
- **Check preprocessing**: Try different preprocessing options
- **Check OCR configuration**: Tesseract should have Arabic + English language packs

## File Organization

### Uploaded Files Location
- **Directory**: `data/flyers/`
- **Naming**: 
  - Single image: `upload_YYYYMMDD_HHMMSS.pdf`
  - Merged images: `merged_YYYYMMDD_HHMMSS.pdf`
  - Temporary files are cleaned up automatically

### Database Records
- **Table**: `catalogues`
- **Fields stored**:
  - `store_id`: Foreign key to stores table
  - `title_ar`, `title_en`: Auto-generated titles
  - `valid_from`, `valid_until`: Offer dates
  - `file_path`: Path to PDF file
  - `file_type`: Always 'pdf' for uploads
  - `page_count`: Number of pages processed
  - `source_url`: Set to 'manual_upload'
  - `status`: 'completed' or 'failed'
  - `ocr_processed`: Boolean flag

## Security

### File Validation
- Only accepted file types: .jpg, .jpeg, .png, .pdf
- Files are validated server-side
- Invalid files are rejected with error message

### Processing Safety
- All processing happens server-side
- Temporary files are cleaned up after processing
- Failed uploads don't leave orphaned files
- Database records track all uploads

### Data Privacy
- Uploaded files stored in local directory
- No external services used for OCR
- All processing is on-premises

## Support

### Common Questions

**Q: Can I upload multiple PDFs at once?**
A: Yes, multiple PDFs will be merged into a single catalogue.

**Q: What happens if OCR fails?**
A: The catalogue status is set to 'failed' and an error message is shown in the logs.

**Q: Can I re-process a failed upload?**
A: Currently, you need to upload again. The catalogue record will remain in the database.

**Q: How do I know if products were extracted correctly?**
A: Check the Products page in the admin dashboard to see extracted products.

**Q: Can I edit products after upload?**
A: Currently, there's no built-in product editing UI. Products are stored in the database.

### Getting Help

- Check the "Troubleshooting" section in the Scrapers page
- Review logs in the "Scraping Logs" panel
- Verify Tesseract OCR is installed: `tesseract --list-langs`
- Verify Poppler is installed: `pdftoppm -v`

## Version History

- **v1.0.0** (2024-12-09): Initial release
  - Manual upload support for images and PDFs
  - Enhanced OCR preprocessing with rotation detection
  - Frontend UI with date range selection
  - API endpoint for multipart uploads
