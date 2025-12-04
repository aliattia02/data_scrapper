"""
src/api/app.py - FastAPI REST API for OfferCatalog Mobile App
"""
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.database.models import Product
from src.database.manager import DatabaseManager


def create_app(db_manager: DatabaseManager) -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="🇪🇬 Egyptian Grocery API",
        description="REST API for OfferCatalog - Egyptian grocery store data",
        version="1.0.0"
    )

    # CORS for React Native mobile app
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def get_db():
        """Database session dependency"""
        session = db_manager.get_session()
        try:
            yield session
        finally:
            session.close()

    @app.get("/")
    def root():
        """API root endpoint"""
        return {
            "message": "🇪🇬 Egyptian Grocery API",
            "version": "1.0.0",
            "docs": "/docs"
        }

    @app.get("/health")
    def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }

    @app.get("/products", response_model=List[dict])
    def get_products(
            store: Optional[str] = Query(None, description="Filter by store (carrefour, metro, kazyon)"),
            category_ar: Optional[str] = Query(None, description="Filter by Arabic category"),
            category_en: Optional[str] = Query(None, description="Filter by English category"),
            min_price: Optional[float] = Query(None, description="Minimum price"),
            max_price: Optional[float] = Query(None, description="Maximum price"),
            on_sale: Optional[bool] = Query(None, description="Only discounted products"),
            limit: int = Query(100, le=500, description="Max products to return"),
            offset: int = Query(0, description="Pagination offset"),
            db: Session = Depends(get_db)
    ):
        """
        Get products with filters
        Returns list of products for mobile app
        """
        query = db.query(Product)

        # Apply filters
        if store:
            query = query.filter(Product.store == store.lower())

        if category_ar:
            query = query.filter(Product.category_ar == category_ar)

        if category_en:
            query = query.filter(Product.category_en == category_en)

        if min_price is not None:
            query = query.filter(Product.price >= min_price)

        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        if on_sale:
            query = query.filter(Product.discount_percentage != None)

        # Order by most recent
        query = query.order_by(Product.scraped_at.desc())

        # Pagination
        products = query.offset(offset).limit(limit).all()

        return [product.to_dict() for product in products]

    @app.get("/products/{product_id}", response_model=dict)
    def get_product(product_id: int, db: Session = Depends(get_db)):
        """Get single product by ID"""
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return product.to_dict()

    @app.get("/products/search", response_model=List[dict])
    def search_products(
            q: str = Query(..., min_length=2, description="Search query"),
            store: Optional[str] = Query(None),
            limit: int = Query(50, le=200),
            db: Session = Depends(get_db)
    ):
        """Search products by name"""
        query = db.query(Product).filter(
            (Product.name_ar.contains(q)) |
            (Product.name_en.contains(q))
        )

        if store:
            query = query.filter(Product.store == store.lower())

        products = query.limit(limit).all()

        return [product.to_dict() for product in products]

    @app.get("/stores", response_model=List[dict])
    def get_stores(db: Session = Depends(get_db)):
        """Get list of available stores with product counts"""
        from sqlalchemy import func

        stores = db.query(
            Product.store,
            func.count(Product.id).label('product_count'),
            func.min(Product.price).label('min_price'),
            func.max(Product.price).label('max_price')
        ).group_by(Product.store).all()

        return [
            {
                "name": store[0],
                "product_count": store[1],
                "price_range": {
                    "min": store[2],
                    "max": store[3]
                }
            }
            for store in stores
        ]

    @app.get("/categories", response_model=List[dict])
    def get_categories(
            store: Optional[str] = Query(None),
            db: Session = Depends(get_db)
    ):
        """Get list of categories"""
        from sqlalchemy import func, distinct

        query = db.query(
            Product.category_ar,
            Product.category_en,
            func.count(Product.id).label('product_count')
        )

        if store:
            query = query.filter(Product.store == store.lower())

        categories = query.group_by(
            Product.category_ar,
            Product.category_en
        ).all()

        return [
            {
                "name_ar": cat[0],
                "name_en": cat[1],
                "product_count": cat[2]
            }
            for cat in categories
        ]

    @app.get("/deals", response_model=List[dict])
    def get_deals(
            store: Optional[str] = Query(None),
            min_discount: float = Query(10.0, description="Minimum discount percentage"),
            limit: int = Query(50, le=200),
            db: Session = Depends(get_db)
    ):
        """Get products with best deals"""
        query = db.query(Product).filter(
            Product.discount_percentage >= min_discount
        )

        if store:
            query = query.filter(Product.store == store.lower())

        # Order by highest discount
        products = query.order_by(
            Product.discount_percentage.desc()
        ).limit(limit).all()

        return [product.to_dict() for product in products]

    @app.get("/stats", response_model=dict)
    def get_stats(db: Session = Depends(get_db)):
        """Get overall statistics"""
        from sqlalchemy import func

        total_products = db.query(func.count(Product.id)).scalar()
        total_stores = db.query(func.count(func.distinct(Product.store))).scalar()
        total_categories = db.query(func.count(func.distinct(Product.category_ar))).scalar()

        avg_price = db.query(func.avg(Product.price)).scalar()
        products_on_sale = db.query(func.count(Product.id)).filter(
            Product.discount_percentage != None
        ).scalar()

        return {
            "total_products": total_products,
            "total_stores": total_stores,
            "total_categories": total_categories,
            "average_price": round(avg_price, 2) if avg_price else 0,
            "products_on_sale": products_on_sale,
            "last_updated": datetime.utcnow().isoformat()
        }

    return app