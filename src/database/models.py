"""
src/database/models.py - SQLAlchemy ORM Models
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Store(Base):
    """Store model - Supermarket chains"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String(50), unique=True, nullable=False, index=True)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    logo_url = Column(String(500))
    website = Column(String(500))

    # NEW Location fields
    latitude = Column(Float)
    longitude = Column(Float)
    address_ar = Column(String(500))
    address_en = Column(String(500))
    city = Column(String(100))
    governorate = Column(String(100))
    phone = Column(String(50))

    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    branches = relationship("Branch", back_populates="store", cascade="all, delete-orphan")
    catalogues = relationship("Catalogue", back_populates="store", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.store_id,
            "nameAr": self.name_ar,
            "nameEn": self.name_en,
            "logoUrl": self.logo_url,
            "website": self.website,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "addressAr": self.address_ar,
            "addressEn": self.address_en,
            "city": self.city,
            "governorate": self.governorate,
            "phone": self.phone,
            "active": self.active,
            "branchCount": len(self.branches) if self.branches else 0
        }


class Branch(Base):
    """Branch model - Store locations"""
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200))
    address_ar = Column(String(500))
    address_en = Column(String(500))
    city = Column(String(100))
    governorate = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    phone = Column(String(50))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    store = relationship("Store", back_populates="branches")

    def to_dict(self):
        return {
            "id": self.id,
            "storeId": self.store.store_id if self.store else None,
            "nameAr": self.name_ar,
            "nameEn": self.name_en,
            "addressAr": self.address_ar,
            "addressEn": self.address_en,
            "city": self.city,
            "governorate": self.governorate,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "phone": self.phone,
            "active": self.active
        }


class Category(Base):
    """Category model - Product categories"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(String(50), unique=True, nullable=False, index=True)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    icon = Column(String(100))
    sort_order = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = relationship("Product", back_populates="category")

    def to_dict(self):
        return {
            "id": self.category_id,
            "nameAr": self.name_ar,
            "nameEn": self.name_en,
            "icon": self.icon,
            "sortOrder": self.sort_order,
            "active": self.active
        }


class Product(Base):
    """Product model"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_product_id = Column(String(200), unique=True, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    store = Column(String(50), nullable=False, index=True)
    name_ar = Column(String(500), nullable=False)
    name_en = Column(String(500))
    brand = Column(String(200))
    category_ar = Column(String(200))
    category_en = Column(String(200))
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    discount_percentage = Column(Float)
    currency = Column(String(10), default="EGP")
    size = Column(String(50))
    unit = Column(String(20))
    description = Column(Text)
    in_stock = Column(Boolean, default=True)
    image_url = Column(String(1000))
    url = Column(String(1000))
    source = Column(String(50), default="scraper")
    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="products")

    def to_dict(self):
        return {
            "id": self.id,
            "storeProductId": self.store_product_id,
            "store": self.store,
            "nameAr": self.name_ar,
            "nameEn": self.name_en,
            "brand": self.brand,
            "categoryAr": self.category_ar or (self.category.name_ar if self.category else None),
            "categoryEn": self.category_en or (self.category.name_en if self.category else None),
            "price": self.price,
            "originalPrice": self.original_price,
            "discountPercentage": self.discount_percentage,
            "currency": self.currency,
            "size": self.size,
            "unit": self.unit,
            "description": self.description,
            "inStock": self.in_stock,
            "imageUrl": self.image_url,
            "url": self.url,
            "source": self.source,
            "scrapedAt": self.scraped_at.isoformat() if self.scraped_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }


class Offer(Base):
    """Offer model"""
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    catalogue_id = Column(Integer, ForeignKey("catalogues.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    title_ar = Column(String(500))
    title_en = Column(String(500))
    description_ar = Column(Text)
    description_en = Column(Text)
    offer_price = Column(Float, nullable=False)
    regular_price = Column(Float)
    discount_percentage = Column(Float)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    image_url = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    catalogue = relationship("Catalogue", back_populates="offers")
    product = relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "catalogueId": self.catalogue_id,
            "productId": self.product_id,
            "titleAr": self.title_ar,
            "titleEn": self.title_en,
            "descriptionAr": self.description_ar,
            "descriptionEn": self.description_en,
            "offerPrice": self.offer_price,
            "regularPrice": self.regular_price,
            "discountPercentage": self.discount_percentage,
            "validFrom": self.valid_from.isoformat() if self.valid_from else None,
            "validUntil": self.valid_until.isoformat() if self.valid_until else None,
            "imageUrl": self.image_url
        }


class Catalogue(Base):
    """Catalogue model"""
    __tablename__ = "catalogues"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    
    # Naming fields
    market_category = Column(String(100))  # supermarket, hypermarket, grocery, etc.
    market_name = Column(String(200))
    
    title_ar = Column(String(500))
    title_en = Column(String(500))
    
    # Date range
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    
    # Location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # File info
    file_path = Column(String(1000))
    original_filename = Column(String(500))
    file_type = Column(String(20))  # pdf, images
    page_count = Column(Integer, default=0)
    file_size = Column(Integer)  # bytes
    
    # Source
    source_url = Column(String(1000))
    
    # Status
    status = Column(String(50), default="pending")
    ocr_processed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Thumbnail
    thumbnail_path = Column(String(1000), nullable=True)

    store = relationship("Store", back_populates="catalogues")
    pages = relationship("CataloguePage", back_populates="catalogue", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="catalogue", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "storeId": self.store.store_id if self.store else None,
            "marketCategory": self.market_category,
            "marketName": self.market_name,
            "titleAr": self.title_ar,
            "titleEn": self.title_en,
            "validFrom": self.valid_from.isoformat() if self.valid_from else None,
            "validUntil": self.valid_until.isoformat() if self.valid_until else None,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status,
            "ocrProcessed": self.ocr_processed,
            "filePath": self.file_path,
            "originalFilename": self.original_filename,
            "fileType": self.file_type,
            "pageCount": self.page_count,
            "fileSize": self.file_size,
            "sourceUrl": self.source_url,
            "thumbnailPath": self.thumbnail_path,
            "offerCount": len(self.offers) if self.offers else 0,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "processedAt": self.processed_at.isoformat() if self.processed_at else None
        }


class CataloguePage(Base):
    """CataloguePage model"""
    __tablename__ = "catalogue_pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    catalogue_id = Column(Integer, ForeignKey("catalogues.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    image_path = Column(String(1000))
    ocr_text = Column(Text)
    ocr_confidence = Column(Float)
    ocr_language = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    catalogue = relationship("Catalogue", back_populates="pages")

    def to_dict(self):
        return {
            "id": self.id,
            "catalogueId": self.catalogue_id,
            "pageNumber": self.page_number,
            "imagePath": self.image_path,
            "ocrText": self.ocr_text,
            "ocrConfidence": self.ocr_confidence,
            "ocrLanguage": self.ocr_language
        }


class ScrapingLog(Base):
    """ScrapingLog model"""
    __tablename__ = "scraping_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    products_scraped = Column(Integer, default=0)
    errors = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)

    def to_dict(self):
        return {
            "id": self.id,
            "store": self.store,
            "status": self.status,
            "productsScraped": self.products_scraped,
            "errors": self.errors,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "durationSeconds": self.duration_seconds
        }


class ScrapeJob(Base):
    """ScrapeJob model - Track URL-based scraping jobs"""
    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_url = Column(String(1000), nullable=False)
    store = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False, default='pending', index=True)
    # Status values: pending, downloading, processing_ocr, completed, failed
    
    # Progress tracking
    total_pages = Column(Integer, default=0)
    pages_downloaded = Column(Integer, default=0)
    pages_processed = Column(Integer, default=0)
    products_found = Column(Integer, default=0)
    
    # File paths
    pdf_path = Column(String(1000))
    images_dir = Column(String(1000))
    
    # Error tracking
    errors = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)

    def to_dict(self):
        return {
            "id": self.id,
            "sourceUrl": self.source_url,
            "store": self.store,
            "status": self.status,
            "totalPages": self.total_pages,
            "pagesDownloaded": self.pages_downloaded,
            "pagesProcessed": self.pages_processed,
            "productsFound": self.products_found,
            "pdfPath": self.pdf_path,
            "errors": self.errors,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "durationSeconds": self.duration_seconds
        }
