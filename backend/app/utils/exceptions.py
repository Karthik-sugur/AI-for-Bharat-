"""
Custom exceptions for LandLedger application
"""

from typing import Optional, Dict, Any


class LandLedgerException(Exception):
    """Base exception for LandLedger application"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or "LANDLEDGER_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response"""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class PropertyNotFoundException(LandLedgerException):
    """Exception raised when property is not found"""
    
    def __init__(
        self,
        survey_number: str,
        district: str,
        taluk: str,
        message: Optional[str] = None
    ):
        self.survey_number = survey_number
        self.district = district
        self.taluk = taluk
        
        default_message = (
            f"Property not found: Survey {survey_number}, "
            f"District {district}, Taluk {taluk}"
        )
        
        super().__init__(
            message=message or default_message,
            error_code="PROPERTY_NOT_FOUND",
            details={
                "survey_number": survey_number,
                "district": district,
                "taluk": taluk
            }
        )


class AnalysisException(LandLedgerException):
    """Exception raised during property analysis"""
    
    def __init__(
        self,
        message: str,
        property_id: Optional[str] = None,
        stage: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code="ANALYSIS_ERROR",
            details={
                "property_id": property_id,
                "stage": stage
            }
        )


class DocumentExtractionException(LandLedgerException):
    """Exception raised during document OCR/extraction"""
    
    def __init__(
        self,
        message: str,
        document_type: Optional[str] = None,
        filename: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code="DOCUMENT_EXTRACTION_ERROR",
            details={
                "document_type": document_type,
                "filename": filename
            }
        )


class CacheException(LandLedgerException):
    """Exception raised during cache operations"""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        cache_key: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details={
                "operation": operation,
                "cache_key": cache_key
            }
        )


class AWSServiceException(LandLedgerException):
    """Exception raised for AWS service errors"""
    
    def __init__(
        self,
        message: str,
        service: str,
        operation: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code=f"AWS_{service.upper()}_ERROR",
            details={
                "service": service,
                "operation": operation
            }
        )


class ValidationException(LandLedgerException):
    """Exception raised for input validation errors"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={
                "field": field,
                "value": str(value) if value is not None else None
            }
        )


class RateLimitException(LandLedgerException):
    """Exception raised when rate limit is exceeded"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details={
                "retry_after_seconds": retry_after
            }
        )
