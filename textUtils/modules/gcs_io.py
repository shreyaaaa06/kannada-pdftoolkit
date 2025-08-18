import os
try:
    from google.cloud import storage
    from google.auth import default
except ImportError:
    storage = None
    default = None
from datetime import datetime, timedelta
import logging
from .path_utils import resolve_service_account_from_env

logger = logging.getLogger(__name__)

def upload_to_gcs(local_path: str, bucket_name: str, gcs_key: str) -> str:
    """Upload local file to GCS and return gs:// URI"""
    if storage is None:
        raise ImportError("google-cloud-storage package not installed. Run: pip install google-cloud-storage")
    
    try:
        creds_path = resolve_service_account_from_env()
        client = storage.Client.from_service_account_json(creds_path) if creds_path else storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcs_key)
        
        blob.upload_from_filename(local_path)
        logger.info(f"Uploaded {local_path} to gs://{bucket_name}/{gcs_key}")
        
        return f"gs://{bucket_name}/{gcs_key}"
    except Exception as e:
        logger.error(f"GCS upload failed: {e}")
        raise

def download_from_gcs(gs_uri: str, local_path: str) -> str:
    """Download from GCS URI to local path"""
    if storage is None:
        raise ImportError("google-cloud-storage package not installed. Run: pip install google-cloud-storage")
    
    try:
        # Parse gs://bucket/key
        parts = gs_uri.replace("gs://", "").split("/", 1)
        bucket_name = parts[0]
        gcs_key = parts[1]
        
        creds_path = resolve_service_account_from_env()
        client = storage.Client.from_service_account_json(creds_path) if creds_path else storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcs_key)
        
        blob.download_to_filename(local_path)
        logger.info(f"Downloaded {gs_uri} to {local_path}")
        
        return local_path
    except Exception as e:
        logger.error(f"GCS download failed: {e}")
        raise

def signed_url(gs_uri: str, minutes: int = 60) -> str:
    """Generate v4 signed URL for GCS object"""
    if storage is None:
        raise ImportError("google-cloud-storage package not installed. Run: pip install google-cloud-storage")
    
    try:
        # Parse gs://bucket/key
        parts = gs_uri.replace("gs://", "").split("/", 1)
        bucket_name = parts[0]
        gcs_key = parts[1]
        
        creds_path = resolve_service_account_from_env()
        client = storage.Client.from_service_account_json(creds_path) if creds_path else storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcs_key)
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.utcnow() + timedelta(minutes=minutes),
            method="GET"
        )
        
        logger.info(f"Generated signed URL for {gs_uri}")
        return url
    except Exception as e:
        logger.error(f"Signed URL generation failed: {e}")
        raise

