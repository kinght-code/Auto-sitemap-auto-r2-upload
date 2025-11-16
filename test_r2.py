import os
import boto3
from botocore.exceptions import ClientError

print("Testing R2 connection...")
print(f"R2_ENDPOINT_URL: {os.getenv('R2_ENDPOINT_URL')}")
print(f"R2_BUCKET_NAME: {os.getenv('R2_BUCKET_NAME')}")
print(f"R2_ACCESS_KEY_ID: {'*' * len(os.getenv('R2_ACCESS_KEY_ID', ''))}")
print(f"R2_SECRET_ACCESS_KEY: {'*' * len(os.getenv('R2_SECRET_ACCESS_KEY', ''))}")

try:
    s3_client = boto3.client(
        's3',
        endpoint_url=os.getenv('R2_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY')
    )
    
    # Test listing buckets (this validates credentials)
    response = s3_client.list_buckets()
    print("✓ R2 connection successful!")
    print(f"Available buckets: {[b['Name'] for b in response['Buckets']]}")
    
    # Test if our target bucket exists
    bucket_name = os.getenv('R2_BUCKET_NAME')
    if bucket_name:
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✓ Bucket '{bucket_name}' exists and is accessible")
        except ClientError as e:
            print(f"✗ Bucket '{bucket_name}' error: {e}")
    
except Exception as e:
    print(f"✗ R2 connection failed: {e}")
    print(f"Error type: {type(e).__name__}")
