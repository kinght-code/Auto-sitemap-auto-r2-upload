import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', "https://api.rajneete.com/api/v2/home")
SITE_BASE_URL = os.getenv('SITE_BASE_URL', "https://rajneete.com")

# R2 Configuration
R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME')
R2_ENDPOINT_URL = os.getenv('R2_ENDPOINT_URL', 'https://r2.cloudflarestorage.com')

# Sitemap Configuration
SITEMAP_FILENAME = os.getenv('SITEMAP_FILENAME', "sitemap-monthly-{year}-{month:02d}.xml")
SITEMAP_FOLDER = os.getenv('SITEMAP_FOLDER', "sitemaps/")  # New: Folder path in R2
CHANGE_FREQ = os.getenv('CHANGE_FREQ', "daily")
PRIORITY = os.getenv('PRIORITY', "0.8")

# API Pagination
PAGE_SIZE = int(os.getenv('PAGE_SIZE', '50'))
