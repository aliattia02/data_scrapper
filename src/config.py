"""
src/config.py - Configuration Management
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/database/products.db')

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    FLYERS_DIR = DATA_DIR / 'flyers'
    EXPORTS_DIR = DATA_DIR / 'exports'
    DB_DIR = DATA_DIR / 'database'

    # Selenium
    CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', '/usr/local/bin/chromedriver')
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'

    # Tesseract
    TESSERACT_CMD = os.getenv('TESSERACT_CMD', '/usr/bin/tesseract')

    # API
    API_HOST = os.getenv('API_HOST', '127.0.0.1')
    API_PORT = int(os.getenv('API_PORT', '8000'))
    API_WORKERS = int(os.getenv('API_WORKERS', '4'))

    # Scraping
    USER_AGENT = os.getenv(
        'USER_AGENT',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    RATE_LIMIT_DELAY = int(os.getenv('RATE_LIMIT_DELAY', '2'))

    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.FLYERS_DIR.mkdir(exist_ok=True)
        cls.EXPORTS_DIR.mkdir(exist_ok=True)
        cls.DB_DIR.mkdir(exist_ok=True)


# Initialize directories on import
Config.create_directories()