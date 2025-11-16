import os
import sys
from datetime import datetime, timedelta


from .sitemap_generator import SitemapGenerator
from .r2_uploader import R2Uploader
from config import settings  # config is at the same level as app

def main():
    # Check if environment variables are set
    required_env_vars = ['R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_BUCKET_NAME']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Determine date range
    now = datetime.now()
    
    # If running manually, use command line arguments or default to current month
    if len(sys.argv) > 1:
        if sys.argv[1] == '--current-month':
            year = now.year
            month = now.month
        elif len(sys.argv) >= 3:
            try:
                year = int(sys.argv[1])
                month = int(sys.argv[2])
            except ValueError:
                print("Usage: python main.py [year month] | [--current-month]")
                sys.exit(1)
        else:
            # Default to previous month for scheduled runs
            first_day = now.replace(day=1)
            last_month = first_day - timedelta(days=1)
            year = last_month.year
            month = last_month.month
    else:
        # Default to current month for manual runs
        year = now.year
        month = now.month
    
    # Generate sitemap
    generator = SitemapGenerator()
    sitemap_content = generator.generate_monthly_sitemap(year, month)
    
    # Save locally
    filename = settings.SITEMAP_FILENAME.format(year=year, month=month)
    local_path = f"/app/sitemaps/{filename}"
    
    with open(local_path, 'wb') as f:
        f.write(sitemap_content)
    print(f"Sitemap saved locally: {local_path}")
    
    # Upload to R2
    uploader = R2Uploader()
    
    # Create folder if it doesn't exist (optional - R2 creates folders automatically on upload)
    if settings.SITEMAP_FOLDER:
        uploader.create_folder(settings.SITEMAP_FOLDER)
    
    if uploader.upload_sitemap(sitemap_content, filename):
        print("Sitemap generation and upload completed successfully!")
    else:
        print("Sitemap generation completed but upload failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
