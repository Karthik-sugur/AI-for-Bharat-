"""
Pydantic schemas for request/response models
Defines the data structures for LandLedger API
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PropertyType(str, Enum):
    RESIDENTIAL = "Residential"
    AGRICULTURAL = "Agricultural"
    COMMERCIAL = "Commercial"
    INDUSTRIAL = "Industrial"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SEVERE = "severe"


class TransferMethod(str, Enum):
    SALE_DEED = "Sale Deed"
    INHERITANCE = "Inheritance"
    GIFT_DEED = "Gift Deed"
    PARTITION = "Partition"
    COURT_ORDER = "Court Order"
    GOVT_ALLOTMENT = "Government Allotment"


# ============================================================================
# Request Models
# ============================================================================

class PropertySearchRequest(BaseModel):
    """Request model for property search/analysis"""
    survey_number: str = Field(..., min_length=1, description="Survey number of the property")
    district: str = Field(..., min_length=1, description="District name")
    taluk: str = Field(..., min_length=1, description="Taluk name")
    village: Optional[str] = Field(None, description="Village name")
    state: Optional[str] = Field("Karnataka", description="State name")
    owner_name: Optional[str] = Field(None, description="Current owner name")
    property_type: Optional[PropertyType] = Field(None, description="Type of property")
    area: Optional[str] = Field(None, description="Property area/extent")
    
    class Config:
        json_schema_extra = {
            "example": {
                "survey_number": "84/3B",
                "district": "Bengaluru Urban",
                "taluk": "Mahadevapura",
                "village": "Whitefield",
                "state": "Karnataka",
                "property_type": "Residential",
                "area": "2400 sq ft"
            }
        }


class DocumentUploadRequest(BaseModel):
    """Request model for document OCR"""
    document_type: str = Field(..., description="Type of document (sale_deed, mutation, etc.)")
    property_id: Optional[str] = Field(None, description="Associated property ID")


# ============================================================================
# Data Models
# ============================================================================

class OwnerData(BaseModel):
    """Owner information in ownership chain"""
    owner_id: str
    name: str
    acquisition_date: str
    disposal_date: Optional[str] = None
    acquisition_method: TransferMethod
    document_number: Optional[str] = None
    share_percentage: float = 100.0
    is_current: bool = False
    heirs: Optional[List[dict]] = None


class EncumbranceData(BaseModel):
    """Encumbrance/lien information"""
    encumbrance_id: str
    type: str  # loan, mortgage, lien, etc.
    holder: str  # Bank name, person, etc.
    amount: Optional[float] = None
    currency: str = "INR"
    registration_date: str
    status: str  # active, discharged, disputed
    document_number: Optional[str] = None
    description: Optional[str] = None


class RiskFlag(BaseModel):
    """Individual risk flag"""
    flag_id: str
    category: str
    severity: RiskLevel
    title: str
    description: str
    impact: str
    recommended_action: str
    legal_reference: Optional[str] = None


class PropertyData(BaseModel):
    """Complete property information"""
    property_id: str
    survey_number: str
    district: str
    taluk: str
    village: Optional[str] = None
    state: str
    property_type: Optional[PropertyType] = None
    area: Optional[str] = None
    boundaries: Optional[dict] = None
    registration_info: Optional[dict] = None


class OwnershipChain(BaseModel):
    """Complete ownership lineage"""
    property_id: str
    chain_length: int
    original_owner: OwnerData
    current_owner: OwnerData
    ownership_history: List[OwnerData]
    family_tree: Optional[dict] = None
    gaps_detected: List[str] = []


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    analysis_id: str
    property: PropertyData
    title_confidence_score: int = Field(..., ge=0, le=1000)
    risk_level: RiskLevel
    ownership_chain: OwnershipChain
    encumbrances: List[EncumbranceData]
    risk_flags: List[RiskFlag]
    ai_summary: str
    recommendations: List[str]
    analyzed_at: datetime
    data_sources: List[str]
    disclaimer: str


class DocumentExtractionResult(BaseModel):
    """Result from document OCR"""
    extraction_id: str
    document_type: str
    extracted_text: str
    structured_data: dict
    confidence_score: float
    detected_fields: List[dict]
    storage_url: Optional[str] = None
    processed_at: datetime


class AudioGenerationResult(BaseModel):
    """Result from voice synthesis"""
    audio_id: str
    english_audio_url: str
    hindi_audio_url: Optional[str] = None
    duration_seconds: float
    generated_at: datetime
