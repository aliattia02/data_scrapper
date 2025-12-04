"""
src/database/manager.py - Database Manager
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path

from src.database.models import Base, Store, Branch, Category
from src.utils.categories import get_all_categories


class DatabaseManager:
    """Manage database connections and operations"""

    def __init__(self, db_url: str = None):
        if db_url is None:
            db_path = Path("data/database")
            db_path.mkdir(parents=True, exist_ok=True)
            db_url = f"sqlite:///{db_path}/products.db"

        self.engine = create_engine(
            db_url,
            echo=False,
            connect_args={"check_same_thread": False}
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
        
        # Seed initial data
        self.seed_data()

    def seed_data(self):
        """Seed initial data for stores, branches, and categories"""
        session = self.get_session()
        
        try:
            # Check if data already exists
            if session.query(Store).count() > 0:
                print("⏭️  Seed data already exists, skipping...")
                return
            
            # Create stores
            kazyon = Store(
                store_id="kazyon",
                name_ar="كازيون",
                name_en="Kazyon",
                website="https://kazyon.com",
                active=True
            )
            
            carrefour = Store(
                store_id="carrefour",
                name_ar="كارفور",
                name_en="Carrefour",
                website="https://www.carrefouregypt.com",
                active=True
            )
            
            metro = Store(
                store_id="metro",
                name_ar="مترو",
                name_en="Metro",
                website="https://www.metro-markets.com",
                active=True
            )
            
            session.add_all([kazyon, carrefour, metro])
            session.flush()
            
            # Create Zagazig branches
            branches = [
                # Kazyon branches
                Branch(
                    store_id=kazyon.id,
                    name_ar="كازيون - شارع الجلاء",
                    name_en="Kazyon - Al Galaa Street",
                    address_ar="شارع الجلاء، الزقازيق",
                    city="Zagazig",
                    governorate="Sharqia",
                    active=True
                ),
                Branch(
                    store_id=kazyon.id,
                    name_ar="كازيون - شارع أحمد عرابي",
                    name_en="Kazyon - Ahmed Orabi Street",
                    address_ar="شارع أحمد عرابي، الزقازيق",
                    city="Zagazig",
                    governorate="Sharqia",
                    active=True
                ),
                Branch(
                    store_id=kazyon.id,
                    name_ar="كازيون - شارع الجمهورية",
                    name_en="Kazyon - Al Gomhoureya Street",
                    address_ar="شارع الجمهورية، الزقازيق",
                    city="Zagazig",
                    governorate="Sharqia",
                    active=True
                ),
                # Carrefour branch
                Branch(
                    store_id=carrefour.id,
                    name_ar="كارفور - مول الزقازيق",
                    name_en="Carrefour - Zagazig Mall",
                    address_ar="مول الزقازيق، الزقازيق",
                    city="Zagazig",
                    governorate="Sharqia",
                    active=True
                ),
            ]
            
            session.add_all(branches)
            
            # Create categories
            categories = []
            for idx, cat_data in enumerate(get_all_categories()):
                cat = Category(
                    category_id=cat_data['id'],
                    name_ar=cat_data['name_ar'],
                    name_en=cat_data['name_en'],
                    icon=cat_data['icon'],
                    sort_order=idx,
                    active=True
                )
                categories.append(cat)
            
            session.add_all(categories)
            session.commit()
            
            print(f"✅ Seeded {len([kazyon, carrefour, metro])} stores")
            print(f"✅ Seeded {len(branches)} branches")
            print(f"✅ Seeded {len(categories)} categories")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Seed data failed: {e}")
            raise
        finally:
            session.close()

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    def migrate(self):
        """Run database migrations"""
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
