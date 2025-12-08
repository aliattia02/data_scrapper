"""
Database migration to add ScrapeJob table
"""
from sqlalchemy import create_engine, inspect
from src.config import DATABASE_URL
from src.database.models import Base, ScrapeJob


def migrate_scrape_jobs_table():
    """Add ScrapeJob table if it doesn't exist"""
    print("🔧 Running migration for ScrapeJob table...")
    
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    # Check if table exists
    if 'scrape_jobs' not in inspector.get_table_names():
        print("  Creating scrape_jobs table...")
        ScrapeJob.__table__.create(engine)
        print("  ✅ scrape_jobs table created")
    else:
        print("  ℹ️  scrape_jobs table already exists")
    
    engine.dispose()


if __name__ == '__main__':
    migrate_scrape_jobs_table()
