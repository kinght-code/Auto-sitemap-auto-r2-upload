# Auto-sitemap-auto-r2-upload

# For specific month
docker run -v $(pwd)/sitemaps:/app/sitemaps --env-file .env sitemap-generator python -m app.main 2025 6

# For current month  
docker run -v $(pwd)/sitemaps:/app/sitemaps --env-file .env sitemap-generator python -m app.main --current-month

# For help
docker run --env-file .env sitemap-generator python -m app.main --help
