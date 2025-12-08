"""
src/api/routes.py - FastAPI Routes for Admin Dashboard
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
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