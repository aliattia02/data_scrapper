"""
src/api/routes.py - FastAPI Routes for Admin Dashboard
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil

from src.database.models import Store, Branch, Category, Product, Offer, Catalogue, CataloguePage
from src.database.manager import DatabaseManager

# Create routers
stores_router = APIRouter(prefix="/api/v1/stores", tags=["stores"])
categories_router = APIRouter(prefix="/api/v1/categories", tags=["categories"])
products_router = APIRouter(prefix="/api/v1/products", tags=["products"])
offers_router = APIRouter(prefix="/api/v1/offers", tags=["offers"])
catalogues_router = APIRouter(prefix="/api/v1/catalogues", tags=["catalogues"])
export_router = APIRouter(prefix="/api/v1/export", tags=["export"])
scraper_router = APIRouter(prefix="/api/v1/scraper", tags=["scraper"])


def get_db():
    """Database session dependency"""
    db_manager = DatabaseManager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()


# Stores endpoints
@stores_router.get("")
async def list_stores(db: Session = Depends(get_db)):
    """List all stores"""
    stores = db.query(Store).all()
    return [store.to_dict() for store in stores]


@stores_router.post("")
async def create_store(store_data: dict, db: Session = Depends(get_db)):
    """Create a new store"""
    store = Store(**store_data)
    db.add(store)
    db.commit()
    db.refresh(store)
    return store.to_dict()


@stores_router.get("/{store_id}/branches")
async def list_store_branches(store_id: str, db: Session = Depends(get_db)):
    """List branches for a store"""
    store = db.query(Store).filter(Store.store_id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return [branch.to_dict() for branch in store.branches]


# Categories endpoints
@categories_router.get("")
async def list_categories(db: Session = Depends(get_db)):
    """List all categories"""
    categories = db.query(Category).order_by(Category.sort_order).all()
    return [cat.to_dict() for cat in categories]


@categories_router.post("")
async def create_category(category_data: dict, db: Session = Depends(get_db)):
    """Create a new category"""
    category = Category(**category_data)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category.to_dict()


# Products endpoints
@products_router.get("")
async def list_products(
    skip: int = 0,
    limit: int = 100,
    store: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List products with pagination"""
    query = db.query(Product)
    if store:
        query = query.filter(Product.store == store)
    
    products = query.offset(skip).limit(limit).all()
    return [product.to_dict() for product in products]


@products_router.post("")
async def create_product(product_data: dict, db: Session = Depends(get_db)):
    """Create a new product"""
    product = Product(**product_data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product.to_dict()


# Offers endpoints
@offers_router.get("")
async def list_offers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List offers"""
    offers = db.query(Offer).offset(skip).limit(limit).all()
    return [offer.to_dict() for offer in offers]


@offers_router.post("")
async def create_offer(offer_data: dict, db: Session = Depends(get_db)):
    """Create a new offer"""
    offer = Offer(**offer_data)
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer.to_dict()


# Catalogues endpoints
@catalogues_router.get("")
async def list_catalogues(db: Session = Depends(get_db)):
    """List all catalogues"""
    catalogues = db.query(Catalogue).order_by(Catalogue.created_at.desc()).all()
    return [cat.to_dict() for cat in catalogues]


@catalogues_router.post("")
async def create_catalogue(catalogue_data: dict, db: Session = Depends(get_db)):
    """Create a new catalogue"""
    # Get store
    store = db.query(Store).filter(Store.store_id == catalogue_data.get('store_id')).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    catalogue = Catalogue(
        store_id=store.id,
        title_ar=catalogue_data.get('title_ar'),
        title_en=catalogue_data.get('title_en'),
        valid_from=catalogue_data.get('valid_from'),
        valid_until=catalogue_data.get('valid_until'),
        status='pending'
    )
    db.add(catalogue)
    db.commit()
    db.refresh(catalogue)
    return catalogue.to_dict()


@catalogues_router.post("/{catalogue_id}/upload")
async def upload_catalogue_file(
    catalogue_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload PDF or image file for catalogue"""
    catalogue = db.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
    if not catalogue:
        raise HTTPException(status_code=404, detail="Catalogue not found")
    
    # Save file
    upload_dir = os.path.join("data", "flyers")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(upload_dir, f"catalogue_{catalogue_id}{file_extension}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update catalogue
    catalogue.file_path = file_path
    catalogue.file_type = 'pdf' if file_extension == '.pdf' else 'image'
    catalogue.status = 'uploaded'
    db.commit()
    
    return {"message": "File uploaded successfully", "file_path": file_path}


@catalogues_router.post("/{catalogue_id}/process")
async def process_catalogue(catalogue_id: int, db: Session = Depends(get_db)):
    """Process catalogue with OCR"""
    catalogue = db.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
    if not catalogue:
        raise HTTPException(status_code=404, detail="Catalogue not found")
    
    if not catalogue.file_path:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    try:
        from src.ocr.processor import OCRProcessor
        
        processor = OCRProcessor()
        
        # Process the file
        if catalogue.file_type == 'pdf':
            # TODO: Implement PDF to images conversion
            raise HTTPException(status_code=501, detail="PDF processing not yet implemented")
        else:
            products = processor.process_flyer(catalogue.file_path)
            
            catalogue.status = 'completed'
            catalogue.ocr_processed = True
            catalogue.processed_at = datetime.utcnow()
            db.commit()
            
            return {
                "message": "Catalogue processed successfully",
                "products_extracted": len(products)
            }
    
    except Exception as e:
        catalogue.status = 'failed'
        db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


# PDF Scraper endpoints
@catalogues_router.post("/scrape-pdf")
async def scrape_pdf(request: dict, db: Session = Depends(get_db)):
    """
    Scrape catalogue images and merge into PDF
    
    Request body:
    {
        "url": "https://...",
        "market_category": "supermarket",
        "market_name": "Metro",
        "start_date": "2024-12-01",
        "end_date": "2024-12-08",
        "latitude": 30.0444,
        "longitude": 31.2357
    }
    
    Returns: { "pdf_path": "...", "filename": "...", "pages": 7 }
    """
    try:
        from src.scrapers.pdf_scraper import PdfScraper
        
        url = request.get('url')
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        metadata = {
            'market_category': request.get('market_category', 'catalogue'),
            'market_name': request.get('market_name', 'store'),
            'start_date': request.get('start_date', ''),
            'end_date': request.get('end_date', ''),
        }
        
        scraper = PdfScraper()
        result = scraper.scrape_single_catalogue(url, metadata)
        
        # Parse dates with validation
        valid_from = None
        valid_until = None
        
        if request.get('start_date'):
            try:
                valid_from = datetime.fromisoformat(request['start_date'])
            except (ValueError, TypeError) as e:
                raise HTTPException(status_code=400, detail=f"Invalid start_date format: {str(e)}")
        
        if request.get('end_date'):
            try:
                valid_until = datetime.fromisoformat(request['end_date'])
            except (ValueError, TypeError) as e:
                raise HTTPException(status_code=400, detail=f"Invalid end_date format: {str(e)}")
        
        # Save to database
        catalogue = Catalogue(
            store_id=None,  # Can be linked later
            market_category=metadata['market_category'],
            market_name=metadata['market_name'],
            valid_from=valid_from,
            valid_until=valid_until,
            latitude=request.get('latitude'),
            longitude=request.get('longitude'),
            file_path=result['pdf_path'],
            original_filename=result['filename'],
            file_type='pdf',
            page_count=result['pages'],
            file_size=result['file_size'],
            source_url=url,
            thumbnail_path=result.get('thumbnail_path'),
            status='completed'
        )
        
        db.add(catalogue)
        db.commit()
        db.refresh(catalogue)
        
        return {
            "success": True,
            "catalogue_id": catalogue.id,
            "pdf_path": result['pdf_path'],
            "filename": result['filename'],
            "pages": result['pages'],
            "file_size": result['file_size']
        }
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"PDF scraping failed: {str(e)}\n{error_detail}")


@catalogues_router.post("/scrape-store-catalogues")
async def scrape_store_catalogues(request: dict, db: Session = Depends(get_db)):
    """
    Scrape all catalogue links from a store page
    
    Request body:
    {
        "store_url": "https://www.filloffer.com/markets/Metro-Markets",
        "market_category": "supermarket",
        "market_name": "Metro",
        "latitude": 30.0444,
        "longitude": 31.2357
    }
    
    Returns: { "catalogues": [...], "total": 5 }
    """
    try:
        from src.scrapers.pdf_scraper import PdfScraper
        
        store_url = request.get('store_url')
        if not store_url:
            raise HTTPException(status_code=400, detail="Store URL is required")
        
        metadata = {
            'market_category': request.get('market_category', 'catalogue'),
            'market_name': request.get('market_name', 'store'),
        }
        
        scraper = PdfScraper()
        results = scraper.scrape_store_catalogues(store_url, metadata)
        
        # Save all to database
        catalogues = []
        for result in results:
            # Parse dates if available
            valid_from = None
            valid_until = None
            
            if result.get('start_date'):
                try:
                    valid_from = datetime.fromisoformat(result['start_date'])
                except (ValueError, TypeError) as e:
                    print(f"Invalid start_date format: {result.get('start_date')}")
            
            if result.get('end_date'):
                try:
                    valid_until = datetime.fromisoformat(result['end_date'])
                except (ValueError, TypeError) as e:
                    print(f"Invalid end_date format: {result.get('end_date')}")
            
            catalogue = Catalogue(
                store_id=None,
                market_category=metadata['market_category'],
                market_name=metadata['market_name'],
                title_en=result.get('title', ''),
                valid_from=valid_from,
                valid_until=valid_until,
                latitude=request.get('latitude'),
                longitude=request.get('longitude'),
                file_path=result['pdf_path'],
                original_filename=result['filename'],
                file_type='pdf',
                page_count=result['pages'],
                file_size=result['file_size'],
                source_url=result.get('url', store_url),
                thumbnail_path=result.get('thumbnail_path'),
                status='completed'
            )
            
            db.add(catalogue)
            catalogues.append(catalogue)
        
        db.commit()
        
        return {
            "success": True,
            "catalogues": [cat.to_dict() for cat in catalogues],
            "total": len(catalogues)
        }
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Store scraping failed: {str(e)}\n{error_detail}")


@catalogues_router.get("/list")
async def list_catalogues_filtered(
    store: Optional[str] = None,
    category: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all catalogues with optional filters"""
    query = db.query(Catalogue)
    
    if store:
        query = query.filter(Catalogue.market_name == store)
    
    if category:
        query = query.filter(Catalogue.market_category == category)
    
    if from_date:
        query = query.filter(Catalogue.valid_from >= datetime.fromisoformat(from_date))
    
    if to_date:
        query = query.filter(Catalogue.valid_until <= datetime.fromisoformat(to_date))
    
    catalogues = query.order_by(Catalogue.created_at.desc()).all()
    return [cat.to_dict() for cat in catalogues]


@catalogues_router.put("/{catalogue_id}/rename")
async def rename_catalogue(catalogue_id: int, request: dict, db: Session = Depends(get_db)):
    """Rename catalogue PDF file"""
    catalogue = db.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
    if not catalogue:
        raise HTTPException(status_code=404, detail="Catalogue not found")
    
    new_name = request.get('new_name')
    if not new_name:
        raise HTTPException(status_code=400, detail="new_name is required")
    
    # Ensure .pdf extension
    if not new_name.endswith('.pdf'):
        new_name = f"{new_name}.pdf"
    
    # Rename file on disk
    try:
        from pathlib import Path
        
        old_path = Path(catalogue.file_path)
        new_path = old_path.parent / new_name
        
        if old_path.exists():
            old_path.rename(new_path)
            catalogue.file_path = str(new_path)
            catalogue.original_filename = new_name
            
            # Also rename thumbnail if exists
            if catalogue.thumbnail_path:
                old_thumb = Path(catalogue.thumbnail_path)
                new_thumb_name = new_name.replace('.pdf', '_thumb.jpg')
                new_thumb = old_thumb.parent / new_thumb_name
                
                if old_thumb.exists():
                    old_thumb.rename(new_thumb)
                    catalogue.thumbnail_path = str(new_thumb)
        
        db.commit()
        
        return {"success": True, "new_name": new_name}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rename failed: {str(e)}")


@catalogues_router.get("/{catalogue_id}/pdf")
async def get_catalogue_pdf(catalogue_id: int, db: Session = Depends(get_db)):
    """Return PDF file for download/viewing"""
    catalogue = db.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
    if not catalogue:
        raise HTTPException(status_code=404, detail="Catalogue not found")
    
    if not catalogue.file_path or not os.path.exists(catalogue.file_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(
        catalogue.file_path,
        media_type='application/pdf',
        filename=catalogue.original_filename or 'catalogue.pdf'
    )


@catalogues_router.get("/{catalogue_id}/thumbnail")
async def get_catalogue_thumbnail(catalogue_id: int, db: Session = Depends(get_db)):
    """Return first page as thumbnail image"""
    catalogue = db.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
    if not catalogue:
        raise HTTPException(status_code=404, detail="Catalogue not found")
    
    if not catalogue.thumbnail_path or not os.path.exists(catalogue.thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    return FileResponse(
        catalogue.thumbnail_path,
        media_type='image/jpeg'
    )


@catalogues_router.delete("/{catalogue_id}")
async def delete_catalogue(catalogue_id: int, db: Session = Depends(get_db)):
    """Delete catalogue and PDF file"""
    catalogue = db.query(Catalogue).filter(Catalogue.id == catalogue_id).first()
    if not catalogue:
        raise HTTPException(status_code=404, detail="Catalogue not found")
    
    # Delete files from disk
    try:
        from pathlib import Path
        
        if catalogue.file_path and os.path.exists(catalogue.file_path):
            Path(catalogue.file_path).unlink()
        
        if catalogue.thumbnail_path and os.path.exists(catalogue.thumbnail_path):
            Path(catalogue.thumbnail_path).unlink()
    except Exception as e:
        print(f"Warning: Failed to delete files: {e}")
    
    # Delete from database
    db.delete(catalogue)
    db.commit()
    
    return {"success": True, "message": "Catalogue deleted"}


# Export endpoint
@export_router.get("/app")
async def export_for_mobile_app(db: Session = Depends(get_db)):
    """Export data in mobile app format"""
    from src.exporters.json_exporter import JSONExporter
    from src.database.manager import DatabaseManager
    
    db_manager = DatabaseManager()
    exporter = JSONExporter(db_manager)
    
    try:
        output_path = exporter.export()
        
        # Read the exported file
        with open(output_path, 'r', encoding='utf-8') as f:
            import json
            data = json.load(f)
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# Scraper endpoint
@scraper_router.post("/run")
async def run_scraper(request_data: dict, db: Session = Depends(get_db)):
    """Trigger scrapers"""
    store = request_data.get('store', 'all')

    try:
        from src.scrapers.filloffer import FillofferScraperImproved
        from src.database.manager import DatabaseManager

        db_manager = DatabaseManager()
        results = []

        if store == 'all':
            scraper = FillofferScraperImproved(db_manager)
        else:
            scraper = FillofferScraperImproved(db_manager, target_store=store)

        products = scraper.scrape()
        results.append({"store": store, "products": len(products)})

        return {"message": "Scraping completed", "results": results}

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}\n{error_detail}")


@scraper_router.post("/scrape-url")
async def scrape_from_url(request_data: dict, db: Session = Depends(get_db)):
    """
    Scrape a specific catalogue URL
    
    Request body:
    {
        "url": "https://www.filloffer.com/markets/Kazyon-Market/...",
        "store": "kazyon"  # optional, auto-detect from URL
    }
    
    Returns:
    {
        "status": "completed",
        "job_id": 123,
        "products_found": 45,
        "pages_processed": 12,
        "pdf_path": "/path/to/pdf"
    }
    """
    url = request_data.get('url')
    store = request_data.get('store')
    
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    try:
        from src.scrapers.url_scraper import URLScraper
        from src.database.manager import DatabaseManager
        
        db_manager = DatabaseManager()
        scraper = URLScraper(db_manager)
        
        # Run the scraper
        result = scraper.scrape_url(url, store)
        
        return result
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"URL scraping failed: {str(e)}\n{error_detail}")


@scraper_router.get("/jobs/{job_id}")
async def get_scrape_job(job_id: int, db: Session = Depends(get_db)):
    """Get status of a scrape job"""
    from src.database.models import ScrapeJob
    
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job.to_dict()


@scraper_router.get("/jobs")
async def list_scrape_jobs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List scrape jobs"""
    from src.database.models import ScrapeJob
    
    jobs = db.query(ScrapeJob).order_by(ScrapeJob.created_at.desc()).offset(skip).limit(limit).all()
    return [job.to_dict() for job in jobs]


@scraper_router.post("/upload-catalogue")
async def upload_catalogue(
    files: List[UploadFile] = File(...),
    store: str = Form(...),
    valid_from: Optional[str] = Form(None),
    valid_until: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload catalogue files (images or PDF) for manual processing
    
    Form data:
    - files: Multiple image files (.jpg, .png) or single PDF file
    - store: Store identifier (kazyon, carrefour, metro, etc.)
    - valid_from: Optional offer start date (ISO format)
    - valid_until: Optional offer end date (ISO format)
    
    Returns:
    {
        "status": "completed",
        "catalogue_id": 123,
        "pdf_path": "/path/to/pdf",
        "products_extracted": 45,
        "pages_processed": 12
    }
    """
    try:
        from src.scrapers.upload_handler import UploadHandler
        from src.database.manager import DatabaseManager
        
        db_manager = DatabaseManager()
        upload_handler = UploadHandler(db_manager)
        
        # Process the upload
        result = upload_handler.process_upload(
            files=files,
            store=store,
            valid_from=valid_from,
            valid_until=valid_until
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Upload processing failed: {str(e)}\n{error_detail}"
        )