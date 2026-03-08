"""
API Response models for standardized responses
"""

from pydantic import BaseModel
from typing import Any, Optional, Dict
from datetime import datetime


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    data: Any
    message: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __init__(self, **data):
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    
    def __init__(self, **data):
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class AnalysisResponse(BaseModel):
    """Response model for property analysis"""
    success: bool = True
    data: dict
    cached: bool = False
    cache_key: Optional[str] = None
    processing_time_ms: Optional[float] = None
    timestamp: Optional[datetime] = None
    
    def __init__(self, **data):
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    environment: str
    services: Dict[str, str]
    uptime_seconds: float
    timestamp: Optional[datetime] = None
    
    def __init__(self, **data):
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class DocumentExtractionResponse(BaseModel):
    """Response for document extraction"""
    success: bool = True
    extracted_text: str
    structured_data: dict
    confidence_score: float
    storage_url: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __init__(self, **data):
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class AudioResponse(BaseModel):
    """Response for audio generation"""
    success: bool = True
    analysis_data: dict
    audio: dict
    timestamp: Optional[datetime] = None
    
    def __init__(self, **data):
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)
