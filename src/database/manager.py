"""
src/database/manager.py - Database Manager
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path

from src.database.models import Base


class DatabaseManager:
    """Manage database connections and operations"""

    def __init__(self, db_url: str = None):
        if db_url is None:
            # Default SQLite database
            db_path = Path("data/database")
            db_path.mkdir(parents=True, exist_ok=True)
            db_url = f"sqlite:///{db_path}/products.db"

        self.engine = create_engine(
            db_url,
            echo=False,  # Set to True for SQL debugging
            connect_args={"check_same_thread": False}  # For SQLite
        )

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database initialized")

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    def migrate(self):
        """Run database migrations"""
        # Simple migration - recreate tables
        Base.metadata.create_all(bind=self.engine)
        print("✅ Migration complete")

    def clean(self):
        """Clean all data from database"""
        from src.database.models import Product, ScrapingLog

        session = self.get_session()

        try:
            session.query(Product).delete()
            session.query(ScrapingLog).delete()
            session.commit()
            print("✅ Database cleaned")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_stats(self) -> dict:
        """Get database statistics"""
        from src.database.models import Product
        from sqlalchemy import func

        session = self.get_session()

        try:
            total_products = session.query(func.count(Product.id)).scalar()

            by_store = session.query(
                Product.store,
                func.count(Product.id)
            ).group_by(Product.store).all()

            by_category = session.query(
                Product.category_en,
                func.count(Product.id)
            ).group_by(Product.category_en).all()

            return {
                "total_products": total_products,
                "by_store": {store: count for store, count in by_store},
                "by_category": {cat: count for cat, count in by_category}
            }
        finally:
            session.close()
