"""
Amazon S3 Service - Document Storage
Handles secure storage of documents, analysis results, and audio files
"""

import boto3  # type: ignore
import json
import logging
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime
import uuid
import mimetypes

from app.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    """Service for document storage using Amazon S3"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self.presigned_url_expiry = settings.S3_PRESIGNED_URL_EXPIRY
    
    def upload_document(
        self,
        file_content: bytes,
        filename: str,
        document_type: str,
        property_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload document to S3
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            document_type: Type of document (sale_deed, mutation, etc.)
            property_id: Associated property ID
            metadata: Additional metadata
            
        Returns:
            Upload result with S3 key and presigned URL
        """
        
        # Generate unique key
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        extension = filename.split('.')[-1] if '.' in filename else 'pdf'
        
        if property_id:
            s3_key = f"documents/{property_id}/{document_type}/{timestamp}_{unique_id}.{extension}"
        else:
            s3_key = f"documents/{document_type}/{timestamp}_{unique_id}.{extension}"
        
        # Detect content type
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        # Build metadata
        s3_metadata = {
            'original-filename': filename,
            'document-type': document_type,
            'uploaded-at': datetime.utcnow().isoformat()
        }
        if property_id:
            s3_metadata['property-id'] = property_id
        if metadata:
            s3_metadata.update(metadata)
        
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                Metadata=s3_metadata
            )
            
            # Generate presigned URL
            presigned_url = self.generate_presigned_url(s3_key)
            
            return {
                'success': True,
                's3_key': s3_key,
                'bucket': self.bucket_name,
                'presigned_url': presigned_url,
                'content_type': content_type,
                'size_bytes': len(file_content),
                'uploaded_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise
    
    def upload_analysis_result(
        self,
        property_id: str,
        analysis_result: Dict[str, Any]
    ) -> str:
        """
        Store analysis result as JSON in S3
        
        Args:
            property_id: Property ID
            analysis_result: Analysis result dict
            
        Returns:
            S3 key for the stored result
        """
        
        timestamp = datetime.utcnow().isoformat()
        s3_key = f"analysis/{property_id}/{timestamp}.json"
        
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(analysis_result, indent=2, default=str),
                ContentType='application/json',
                Metadata={
                    'property-id': property_id,
                    'analyzed-at': timestamp
                }
            )
            
            logger.info(f"Analysis result stored: {s3_key}")
            return s3_key
            
        except Exception as e:
            logger.error(f"Failed to store analysis: {str(e)}")
            raise
    
    def upload_audio(
        self,
        audio_content: bytes,
        property_id: str,
        language: str = 'english'
    ) -> Dict[str, Any]:
        """
        Upload generated audio to S3
        
        Args:
            audio_content: Audio bytes
            property_id: Property ID
            language: Audio language
            
        Returns:
            Upload result with presigned URL
        """
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        s3_key = f"audio/{property_id}/{language}_{timestamp}.mp3"
        
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=audio_content,
                ContentType='audio/mpeg',
                Metadata={
                    'property-id': property_id,
                    'language': language,
                    'generated-at': timestamp
                }
            )
            
            presigned_url = self.generate_presigned_url(s3_key)
            
            return {
                'success': True,
                's3_key': s3_key,
                'presigned_url': presigned_url,
                'language': language
            }
            
        except Exception as e:
            logger.error(f"Audio upload failed: {str(e)}")
            raise
    
    def download_document(self, s3_key: str) -> bytes:
        """
        Download document from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Document content as bytes
        """
        
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return response['Body'].read()
            
        except Exception as e:
            logger.error(f"S3 download failed: {str(e)}")
            raise
    
    def get_analysis_result(self, s3_key: str) -> Dict[str, Any]:
        """
        Retrieve analysis result from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Analysis result dict
        """
        
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            data = json.loads(response['Body'].read())
            return data
            
        except Exception as e:
            logger.error(f"Failed to retrieve analysis: {str(e)}")
            raise
    
    def generate_presigned_url(
        self,
        s3_key: str,
        expiry: Optional[int] = None
    ) -> str:
        """
        Generate presigned URL for S3 object
        
        Args:
            s3_key: S3 object key
            expiry: URL expiry in seconds
            
        Returns:
            Presigned URL
        """
        
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiry or self.presigned_url_expiry
            )
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise
    
    def list_property_documents(self, property_id: str) -> list:
        """
        List all documents for a property
        
        Args:
            property_id: Property ID
            
        Returns:
            List of document metadata
        """
        
        prefix = f"documents/{property_id}/"
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            documents = []
            for obj in response.get('Contents', []):
                documents.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': self.generate_presigned_url(obj['Key'])
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            return []
    
    def delete_document(self, s3_key: str) -> bool:
        """
        Delete document from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Success status
        """
        
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Deleted: {s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Delete failed: {str(e)}")
            return False
    
    def ensure_bucket_exists(self) -> bool:
        """
        Ensure the S3 bucket exists, create if not
        
        Returns:
            True if bucket exists or was created
        """
        
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except self.client.exceptions.ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    if settings.AWS_REGION == 'us-east-1':
                        self.client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={
                                'LocationConstraint': settings.AWS_REGION
                            }
                        )
                    logger.info(f"Created S3 bucket: {self.bucket_name}")
                    return True
                except Exception as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    return False
            else:
                logger.error(f"Error checking bucket: {e}")
                return False


# Singleton instance
s3_service = S3Service()
