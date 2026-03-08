"""
Amazon DynamoDB Service - Caching Layer
Caches analysis results and property data for fast retrieval
"""

import boto3  # type: ignore
import json
import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING, cast
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib

from app.config import settings

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def convert_to_dynamodb(data: Any) -> Any:
    """Convert Python types to DynamoDB-compatible types"""
    if isinstance(data, float):
        return Decimal(str(data))
    elif isinstance(data, dict):
        return {k: convert_to_dynamodb(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_dynamodb(v) for v in data]
    return data


def convert_from_dynamodb(data: Any) -> Any:
    """Convert DynamoDB types back to Python types"""
    if isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, dict):
        return {k: convert_from_dynamodb(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_from_dynamodb(v) for v in data]
    return data


class DynamoService:
    """Service for caching using Amazon DynamoDB"""
    
    dynamodb: Any
    client: Any
    
    def __init__(self):
        """Initialize DynamoDB resource"""
        self.dynamodb: Any = cast(Any, boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        ))
        self.client: Any = cast(Any, boto3.client(
            'dynamodb',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        ))
        self.table_name = settings.DYNAMODB_TABLE_NAME
        self.ttl_hours = settings.DYNAMODB_TTL_HOURS
        self._table = None
    
    @property
    def table(self):
        """Get or create DynamoDB table"""
        if self._table is None:
            try:
                self._table = self.dynamodb.Table(self.table_name)
                self._table.load()  # Check if table exists
            except self.client.exceptions.ResourceNotFoundException:
                self._create_table()
                self._table = self.dynamodb.Table(self.table_name)
        return self._table
    
    def _create_table(self):
        """Create DynamoDB table if it doesn't exist"""
        try:
            self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'cache_key', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'cache_key', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Wait for table to be created
            waiter = self.client.get_waiter('table_exists')
            waiter.wait(TableName=self.table_name)
            
            # Enable TTL
            self.client.update_time_to_live(
                TableName=self.table_name,
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'ttl'
                }
            )
            
            logger.info(f"Created DynamoDB table: {self.table_name}")
            
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            raise
    
    def generate_cache_key(
        self,
        survey_number: str,
        district: str,
        taluk: str,
        village: Optional[str] = None
    ) -> str:
        """
        Generate unique cache key for property
        
        Args:
            survey_number: Property survey number
            district: District name
            taluk: Taluk name
            village: Village name (optional)
            
        Returns:
            Cache key string
        """
        key_parts = [
            survey_number.lower().strip(),
            district.lower().strip(),
            taluk.lower().strip()
        ]
        if village:
            key_parts.append(village.lower().strip())
        
        key_string = '|'.join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]
    
    def cache_analysis_result(
        self,
        cache_key: str,
        analysis_result: Dict[str, Any],
        ttl_hours: Optional[int] = None
    ) -> bool:
        """
        Cache analysis result in DynamoDB
        
        Args:
            cache_key: Unique cache key
            analysis_result: Analysis result to cache
            ttl_hours: Time to live in hours
            
        Returns:
            Success status
        """
        
        expiration_time = int(
            (datetime.utcnow() + timedelta(hours=ttl_hours or self.ttl_hours)).timestamp()
        )
        
        try:
            item = {
                'cache_key': cache_key,
                'result': convert_to_dynamodb(analysis_result),
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': expiration_time
            }
            
            self.table.put_item(Item=item)
            logger.info(f"Cached analysis result: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Cache write failed: {e}")
            return False
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached analysis result
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached result or None if not found/expired
        """
        
        try:
            response = self.table.get_item(Key={'cache_key': cache_key})
            
            if 'Item' not in response:
                return None
            
            item = response['Item']
            
            # Check if expired (in case TTL hasn't cleaned it yet)
            if item.get('ttl', 0) < datetime.utcnow().timestamp():
                return None
            
            result = convert_from_dynamodb(item.get('result', {}))
            return result
            
        except Exception as e:
            logger.error(f"Cache read failed: {e}")
            return None
    
    def invalidate_cache(self, cache_key: str) -> bool:
        """
        Invalidate cached result
        
        Args:
            cache_key: Cache key
            
        Returns:
            Success status
        """
        
        try:
            self.table.delete_item(Key={'cache_key': cache_key})
            logger.info(f"Invalidated cache: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Cache invalidation failed: {e}")
            return False
    
    def store_property_data(
        self,
        property_id: str,
        property_data: Dict[str, Any]
    ) -> bool:
        """
        Store property data for quick retrieval
        
        Args:
            property_id: Unique property ID
            property_data: Property data
            
        Returns:
            Success status
        """
        
        try:
            item = {
                'cache_key': f"property:{property_id}",
                'result': convert_to_dynamodb(property_data),
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': int((datetime.utcnow() + timedelta(days=30)).timestamp())
            }
            
            self.table.put_item(Item=item)
            return True
            
        except Exception as e:
            logger.error(f"Property data storage failed: {e}")
            return False
    
    def get_property_data(self, property_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve stored property data
        
        Args:
            property_id: Property ID
            
        Returns:
            Property data or None
        """
        
        return self.get_cached_result(f"property:{property_id}")
    
    def store_search_history(
        self,
        user_id: str,
        search_params: Dict[str, Any]
    ) -> bool:
        """
        Store user search history
        
        Args:
            user_id: User identifier
            search_params: Search parameters
            
        Returns:
            Success status
        """
        
        try:
            timestamp = datetime.utcnow().isoformat()
            
            item = {
                'cache_key': f"search:{user_id}:{timestamp}",
                'result': convert_to_dynamodb({
                    'user_id': user_id,
                    'search_params': search_params,
                    'searched_at': timestamp
                }),
                'cached_at': timestamp,
                'ttl': int((datetime.utcnow() + timedelta(days=90)).timestamp())
            }
            
            self.table.put_item(Item=item)
            return True
            
        except Exception as e:
            logger.error(f"Search history storage failed: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Cache statistics
        """
        
        try:
            response = self.client.describe_table(TableName=self.table_name)
            table_info = response['Table']
            
            return {
                'table_name': self.table_name,
                'item_count': table_info.get('ItemCount', 0),
                'size_bytes': table_info.get('TableSizeBytes', 0),
                'status': table_info.get('TableStatus', 'UNKNOWN'),
                'ttl_enabled': True
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {
                'error': str(e),
                'status': 'ERROR'
            }


# Singleton instance
dynamo_service = DynamoService()
