"""
db_migration_catalogues.py - Add missing source_url column to catalogues table
"""
import sqlite3
from pathlib import Path


def migrate_catalogues_table():
    """Add source_url column to catalogues table"""

    db_path = Path("data/database/products.db")

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False

    print(f"🔧 Migrating catalogues table in: {db_path}")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(catalogues)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'source_url' in columns:
            print("✅ source_url column already exists!")
            return True

        print("📝 Adding source_url column...")

        # Add source_url column
        cursor.execute("""
            ALTER TABLE catalogues 
            ADD COLUMN source_url VARCHAR(500)
        """)

        conn.commit()
        print("✅ Migration completed successfully!")

        # Verify
        cursor.execute("PRAGMA table_info(catalogues)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        print("\n📋 Current catalogues table schema:")
        for col_name, col_type in columns.items():
            print(f"  • {col_name}: {col_type}")

        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == '__main__':
    print("🚀 Starting Catalogues Table Migration\n")
    migrate_catalogues_table()