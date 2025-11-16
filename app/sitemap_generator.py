import sys
sys.path.insert(0, '/app')

import requests
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Optional

try:
    from config import settings
except ImportError:
    from app.config import settings

# ... rest of your existing sitemap_generator code ...
# ... rest of your sitemap_generator code ...
class SitemapGenerator:
    def __init__(self):
        self.base_url = settings.SITE_BASE_URL
        self.api_url = settings.API_BASE_URL
        
    def prettify_xml(self, elem):
        """Return a pretty-printed XML string for the Element."""
        rough_string = ET.tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8')
    
    def get_articles(self, from_date: str, to_date: str, page: int = 1, page_size: int = 5000) -> List[Dict]:
        """Fetch articles from the API with date filtering."""
        params = {
            'from_date': from_date,
            'to_date': to_date,
            'page': page,
            'page_size': page_size
        }
        
        try:
            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Adjust this based on your API response structure
            if isinstance(data, dict) and 'results' in data:
                return data['results']
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            elif isinstance(data, list):
                return data
            else:
                print(f"Unexpected API response structure: {data}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching articles from API: {e}")
            return []
    
    def build_url_path(self, article: Dict) -> str:
        """Build URL path from article data following the exact pattern from the sitemap."""
        # Extract category and subcategory from article data
        category_slug = article.get('category_slug') or article.get('category', {}).get('slug', 'news')
        
        # Handle subcategories - use specific subcategory slugs as in your sitemap
        subcategory_slug = article.get('subcategory_slug') or 'general'
        
        # If we have subcategories array, use the first one
        subcategories = article.get('subcategories', [])
        if subcategories and len(subcategories) > 0:
            if isinstance(subcategories[0], dict):
                subcategory_slug = subcategories[0].get('slug', subcategory_slug)
            else:
                subcategory_slug = str(subcategories[0])
        
        # Use the specific news identifier (like t6w6g3wlpl, a6zhbtczd6, etc.)
        news_slug = article.get('url_slug') or article.get('slug') or article.get('id')
        
        return f"{category_slug}/{subcategory_slug}/{news_slug}"
    
    def format_datetime(self, dt_string: str) -> str:
        """Format datetime to the exact format in your sitemap with microseconds and timezone."""
        # Handle None or empty datetime
        if not dt_string:
            # Fallback to current time in Bangladesh timezone
            bd_tz = pytz.timezone('Asia/Dhaka')
            now = datetime.now(bd_tz)
            formatted = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + now.strftime('%z')
            if len(formatted) > 25 and formatted[-5] != ':':
                formatted = formatted[:-2] + ':' + formatted[-2:]
            return formatted
        
        try:
            # Parse the datetime string
            if 'T' in dt_string:
                if dt_string.endswith('Z'):
                    dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
                else:
                    # Handle various datetime formats
                    try:
                        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
                    except ValueError:
                        # Try parsing with different format
                        dt = datetime.strptime(dt_string, '%Y-%m-%dT%H:%M:%S.%f%z')
            else:
                # Handle date-only strings
                dt = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
            
            # Convert to Bangladesh timezone with exact format including microseconds
            bd_tz = pytz.timezone('Asia/Dhaka')
            if dt.tzinfo is None:
                dt = pytz.utc.localize(dt)
            dt_bd = dt.astimezone(bd_tz)
            
            # Format to match exactly: 2025-06-30T23:51:20.912146+06:00
            formatted = dt_bd.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + dt_bd.strftime('%z')
            # Ensure timezone format has colon: +0600 -> +06:00
            if len(formatted) > 25 and formatted[-5] != ':':
                formatted = formatted[:-2] + ':' + formatted[-2:]
            
            return formatted
            
        except (ValueError, AttributeError) as e:
            print(f"Error formatting datetime {dt_string}: {e}")
            # Fallback to current time in Bangladesh timezone with proper format
            bd_tz = pytz.timezone('Asia/Dhaka')
            now = datetime.now(bd_tz)
            formatted = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + now.strftime('%z')
            if len(formatted) > 25 and formatted[-5] != ':':
                formatted = formatted[:-2] + ':' + formatted[-2:]
            return formatted
    
    def get_publication_name(self, article: Dict) -> str:
        """Get exact Bengali publication name based on category as in your sitemap."""
        category_slug = article.get('category_slug') or article.get('category', {}).get('slug', 'news')
        
        # Exact mapping from your sitemap examples
        publication_map = {
            'domestic-politics': 'রাজনীতি',
            'field-politics': 'মাঠের রাজনীতি', 
            'world-politics': 'বিশ্ব রাজনীতি',
            'economy': 'অর্থের রাজনীতি',
            'news': 'খবরাখবর'
        }
        
        return publication_map.get(category_slug, 'খবরাখবর')
    
    def get_image_url(self, article: Dict) -> str:
        """Get image URL in the exact format from your sitemap."""
        image_url = article.get('image_url') or article.get('featured_image') or article.get('thumbnail')
        
        # Ensure it follows the cdn.rajneete.com/original_images/ pattern if it's a relative path
        if image_url and not image_url.startswith('http'):
            image_url = f"https://cdn.rajneete.com/original_images/{image_url}"
        
        return image_url
    
    def get_image_caption(self, article: Dict) -> str:
        """Get image caption, using title as fallback as in your sitemap."""
        return article.get('image_caption') or article.get('title', '')
    
    def generate_sitemap(self, from_date: str, to_date: str) -> bytes:
        """Generate sitemap XML for the given date range following exact structure."""
        # Create root element with namespaces
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        urlset.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
        urlset.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')
        
        # Add XML declaration
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        
        # Fetch articles
        articles = self.get_articles(from_date, to_date, page_size=50)
        print(f"Fetched {len(articles)} articles for sitemap")
        
        for article in articles:
            url_element = ET.SubElement(urlset, 'url')
            
            # Build URL - following exact pattern from your sitemap
            url_path = self.build_url_path(article)
            loc = f"{self.base_url}/{url_path}"
            ET.SubElement(url_element, 'loc').text = loc
            
            # Last modification - handle None values
            lastmod_dt = article.get('last_published_at') or article.get('updated_at') or article.get('created_at')
            lastmod = self.format_datetime(lastmod_dt)
            ET.SubElement(url_element, 'lastmod').text = lastmod
            
            # News markup - exact structure as in your sitemap
            news_news = ET.SubElement(url_element, 'news:news')
            
            publication = ET.SubElement(news_news, 'news:publication')
            publication_name = self.get_publication_name(article)
            ET.SubElement(publication, 'news:name').text = publication_name
            ET.SubElement(publication, 'news:language').text = 'bn'
            
            # Publication date - handle None values
            pub_date = article.get('published_at') or article.get('created_at')
            publication_date = self.format_datetime(pub_date)
            ET.SubElement(news_news, 'news:publication_date').text = publication_date
            
            news_title = article.get('title', '')
            ET.SubElement(news_news, 'news:title').text = news_title
            ET.SubElement(news_news, 'news:keywords')  # Empty keywords as in your sitemap
            
            # Image markup - exact structure
            image_url = self.get_image_url(article)
            if image_url:
                image_image = ET.SubElement(url_element, 'image:image')
                ET.SubElement(image_image, 'image:loc').text = image_url
                image_caption = self.get_image_caption(article)
                ET.SubElement(image_image, 'image:caption').text = image_caption
            
            # SEO elements - exactly as in your sitemap
            ET.SubElement(url_element, 'changefreq').text = settings.CHANGE_FREQ
            ET.SubElement(url_element, 'priority').text = settings.PRIORITY
        
        # Generate the XML with proper formatting
        xml_content = self.prettify_xml(urlset)
        # Combine declaration with content
        return xml_declaration.encode('utf-8') + xml_content
    
    def generate_monthly_sitemap(self, year: int, month: int) -> bytes:
        """Generate sitemap for a specific month."""
        from_date = f"{year}-{month:02d}-01"
        
        # Calculate last day of month
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        last_day = next_month - timedelta(days=1)
        to_date = last_day.strftime('%Y-%m-%d')
        
        print(f"Generating sitemap for {from_date} to {to_date}")
        return self.generate_sitemap(from_date, to_date)
