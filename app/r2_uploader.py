import sys
sys.path.insert(0, '/app')

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

try:
    from config import settings
except ImportError:
    from app.config import settings

# ... rest of your existing r2_uploader code ...
# ... rest of your r2_uploader code ...
class R2Uploader:
    def __init__(self):
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.R2_ENDPOINT_URL,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY
            )
            self.bucket_name = settings.R2_BUCKET_NAME
            print(f"R2 client initialized with endpoint: {settings.R2_ENDPOINT_URL}")
        except Exception as e:
            print(f"Error initializing R2 client: {e}")
            raise
    
    def upload_sitemap(self, sitemap_content: bytes, filename: str) -> bool:
        """Upload sitemap to R2 bucket in specified folder."""
        try:
            # Construct the full path with folder
            if settings.SITEMAP_FOLDER:
                # Ensure folder ends with slash
                folder = settings.SITEMAP_FOLDER.rstrip('/') + '/'
                key = f"{folder}{filename}"
            else:
                key = filename
            
            print(f"Attempting to upload to R2: {self.bucket_name}/{key}")
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=sitemap_content,
                ContentType='application/xml'
            )
            print(f"Successfully uploaded {key} to R2 bucket {self.bucket_name}")
            return True
        except ClientError as e:
            print(f"ClientError uploading to R2: {e}")
            return False
        except EndpointConnectionError as e:
            print(f"EndpointConnectionError: Cannot connect to R2 endpoint. Check your R2_ENDPOINT_URL: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error uploading to R2: {e}")
            return False
    
    def create_folder(self, folder_name: str) -> bool:
        """Create a folder in R2 bucket (folders are just prefixes in S3/R2)."""
        try:
            # Ensure folder name ends with slash
            if not folder_name.endswith('/'):
                folder_name += '/'
            
            # In S3/R2, folders are created by putting an empty object with the folder name
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=folder_name,
                Body=b''
            )
            print(f"Successfully created folder: {folder_name}")
            return True
        except ClientError as e:
            print(f"Error creating folder in R2: {e}")
            return False
