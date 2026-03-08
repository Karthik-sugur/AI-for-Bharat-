"""
API Routes for LandLedger Backend
All REST API endpoints for property analysis
"""

import logging
import time
from typing import Optional
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, BackgroundTasks
from pydantic import BaseModel, Field

from app.config import settings
from app.services.bedrock_service import bedrock_service
from app.services.textract_service import textract_service
from app.services.polly_service import polly_service
from app.services.s3_service import s3_service
from app.services.dynamo_service import dynamo_service
from app.services.land_records_service import land_records_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class PropertySearchRequest(BaseModel):
    """Property search request"""
    survey_number: str = Field(..., min_length=1, description="Survey number")
    district: str = Field(..., min_length=1, description="District name")
    taluk: str = Field(..., min_length=1, description="Taluk name")
    village: Optional[str] = Field(None, description="Village name")
    state: Optional[str] = Field("Karnataka", description="State name")
    owner_name: Optional[str] = Field(None, description="Owner name")
    property_type: Optional[str] = Field(None, description="Property type")
    area: Optional[str] = Field(None, description="Property area")


class AnalysisResponse(BaseModel):
    """Analysis response"""
    success: bool = True
    data: dict
    cached: bool = False
    processing_time_ms: float
    timestamp: datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str
    services: dict
    timestamp: datetime


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns service status and version information
    """
    
    # Check service connectivity
    services_status = {
        "bedrock": "unknown",
        "textract": "unknown",
        "polly": "unknown",
        "s3": "unknown",
        "dynamodb": "unknown"
    }
    
    # Quick connectivity checks (can be expanded)
    try:
        services_status["s3"] = "connected" if s3_service.ensure_bucket_exists() else "error"
    except Exception:
        services_status["s3"] = "error"
    
    try:
        cache_stats = dynamo_service.get_cache_stats()
        services_status["dynamodb"] = "connected" if cache_stats.get('status') != 'ERROR' else "error"
    except Exception:
        services_status["dynamodb"] = "error"
    
    # Mark others as available (actual check would require API calls)
    services_status["bedrock"] = "available"
    services_status["textract"] = "available"
    services_status["polly"] = "available"
    
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "services": services_status,
        "timestamp": datetime.utcnow()
    }


@router.get("/", tags=["Health"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-Powered Land Title Intelligence API",
        "docs": "/docs",
        "health": "/api/health"
    }


# ============================================================================
# Property Analysis Endpoints
# ============================================================================

@router.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_property(request: PropertySearchRequest, background_tasks: BackgroundTasks):
    """
    Analyze property ownership and risks
    
    This is the main analysis endpoint that:
    1. Searches property records
    2. Reconstructs ownership chain
    3. Identifies encumbrances
    4. Performs AI-powered risk analysis
    5. Returns comprehensive analysis with score
    """
    
    start_time = time.time()
    
    try:
        # Generate cache key
        cache_key = dynamo_service.generate_cache_key(
            request.survey_number,
            request.district,
            request.taluk,
            request.village
        )
        
        # Check cache first
        cached_result = dynamo_service.get_cached_result(cache_key)
        if cached_result:
            logger.info(f"Cache hit for {cache_key}")
            return AnalysisResponse(
                success=True,
                data=cached_result,
                cached=True,
                processing_time_ms=round((time.time() - start_time) * 1000, 2),
                timestamp=datetime.utcnow()
            )
        
        # Search property in land records
        property_data = land_records_service.search_property(
            survey_number=request.survey_number,
            district=request.district,
            taluk=request.taluk,
            village=request.village,
            state=request.state
        )
        
        # Get ownership chain
        owners = property_data.get('owners', [])
        encumbrances = property_data.get('encumbrances', [])
        
        # Perform AI analysis using Bedrock
        try:
            ai_analysis = bedrock_service.analyze_property(
                property_data={
                    'property_id': property_data.get('property_id'),
                    'survey_number': request.survey_number,
                    'district': request.district,
                    'taluk': request.taluk,
                    'village': request.village,
                    'state': request.state,
                    'property_type': request.property_type or property_data.get('property_type'),
                    'area': request.area or property_data.get('area')
                },
                owners_data=owners,
                encumbrances_data=encumbrances
            )
        except Exception as e:
            logger.warning(f"AI analysis failed, using fallback: {e}")
            # Use pre-calculated risk from land_records_service
            ai_analysis = {
                'title_confidence_score': property_data.get('risk_score', 700),
                'risk_level': property_data.get('risk_level', 'medium'),
                'risk_flags': property_data.get('risk_flags', []),
                'recommendations': [
                    'Verify ownership chain with local sub-registrar',
                    'Obtain latest encumbrance certificate',
                    'Cross-verify revenue records',
                    'Commission boundary survey if necessary'
                ],
                'ai_summary': 'Analysis completed using rule-based assessment. For AI-powered insights, ensure AWS Bedrock is configured.'
            }
        
        # Build comprehensive response
        # Prefer pre-calculated scores from synthetic data over AI fallback
        final_score = property_data.get('risk_score') or ai_analysis.get('title_confidence_score', 700)
        final_risk_level = property_data.get('risk_level', ai_analysis.get('risk_level', 'medium')).lower()
        final_risk_flags = property_data.get('risk_flags', []) or ai_analysis.get('risk_flags', [])
        
        analysis_result = {
            'analysis_id': str(uuid.uuid4()),
            'property': {
                'property_id': property_data.get('property_id'),
                'survey_number': request.survey_number,
                'district': request.district,
                'taluk': request.taluk,
                'village': request.village,
                'state': request.state or 'Karnataka',
                'property_type': request.property_type or property_data.get('property_type'),
                'area': request.area or property_data.get('area'),
                'boundaries': property_data.get('boundaries'),
                'registration_info': property_data.get('registration_info')
            },
            'title_confidence_score': final_score,
            'risk_level': final_risk_level,
            'ownership_chain': {
                'chain_length': len(owners),
                'original_owner': owners[0] if owners else None,
                'current_owner': owners[-1] if owners else None,
                'ownership_history': owners,
                'gaps_detected': ai_analysis.get('ownership_analysis', {}).get('gaps_detected', [])
            },
            'encumbrances': encumbrances,
            'risk_flags': final_risk_flags,
            'ai_summary': ai_analysis.get('ai_summary', ''),
            'recommendations': ai_analysis.get('recommendations', []),
            'family_tree': land_records_service.get_family_tree(str(property_data.get('property_id', ''))),
            'score_breakdown': property_data.get('score_breakdown', {}),
            'lineage_analysis': property_data.get('lineage_analysis', {}),
            'analyzed_at': datetime.utcnow().isoformat(),
            'data_sources': ['synthetic_database', 'rule_based_analysis'] if property_data.get('data_source') == 'synthetic_database' else ['ai_analysis'],
            'disclaimer': 'This analysis is for informational purposes only. Please consult a legal professional before making any property transaction decisions.'
        }
        
        # Cache the result in background
        background_tasks.add_task(
            dynamo_service.cache_analysis_result,
            cache_key,
            analysis_result
        )
        
        # Store in S3 in background
        background_tasks.add_task(
            s3_service.upload_analysis_result,
            str(property_data.get('property_id', '')),
            analysis_result
        )
        
        return AnalysisResponse(
            success=True,
            data=analysis_result,
            cached=False,
            processing_time_ms=round((time.time() - start_time) * 1000, 2),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-with-audio", tags=["Analysis"])
async def analyze_with_audio(
    request: PropertySearchRequest,
    include_hindi: bool = Query(True, description="Include Hindi audio")
):
    """
    Analyze property and generate audio summary
    
    Same as /analyze but also generates audio summaries using Amazon Polly
    """
    
    start_time = time.time()
    
    try:
        # First, run standard analysis
        property_data = land_records_service.search_property(
            survey_number=request.survey_number,
            district=request.district,
            taluk=request.taluk,
            village=request.village,
            state=request.state
        )
        
        owners = property_data.get('owners', [])
        encumbrances = property_data.get('encumbrances', [])
        
        # Build analysis result
        analysis_result = {
            'title_confidence_score': property_data.get('risk_score', 700),
            'risk_level': property_data.get('risk_level', 'medium'),
            'risk_flags': property_data.get('risk_flags', []),
            'recommendations': [
                'Verify ownership chain with local sub-registrar',
                'Obtain latest encumbrance certificate',
                'Cross-verify revenue records',
                'Commission boundary survey if necessary'
            ],
            'ai_summary': f"Property analysis for {request.survey_number} in {request.district}. Score: {property_data.get('risk_score', 700)}/1000. {len(property_data.get('risk_flags', []))} risk flags identified."
        }
        
        # Generate audio
        try:
            audio_result = polly_service.generate_analysis_audio(
                analysis_result,
                include_hindi=include_hindi
            )
            
            # Upload audio to S3
            if audio_result.get('english', {}).get('audio_base64'):
                import base64
                english_audio_bytes = base64.b64decode(audio_result['english']['audio_base64'])
                english_upload = s3_service.upload_audio(
                    english_audio_bytes,
                    str(property_data.get('property_id', '')),
                    'english'
                )
                audio_result['english']['url'] = english_upload.get('presigned_url')
            
            if include_hindi and audio_result.get('hindi', {}).get('audio_base64'):
                import base64
                hindi_audio_bytes = base64.b64decode(audio_result['hindi']['audio_base64'])
                hindi_upload = s3_service.upload_audio(
                    hindi_audio_bytes,
                    str(property_data.get('property_id', '')),
                    'hindi'
                )
                audio_result['hindi']['url'] = hindi_upload.get('presigned_url')
                
        except Exception as e:
            logger.warning(f"Audio generation failed: {e}")
            audio_result = {
                'error': 'Audio generation unavailable',
                'message': str(e)
            }
        
        return {
            "success": True,
            "data": {
                'property': {
                    'property_id': property_data.get('property_id'),
                    'survey_number': request.survey_number,
                    'district': request.district,
                    'taluk': request.taluk
                },
                'analysis': analysis_result,
                'audio': audio_result
            },
            "processing_time_ms": round((time.time() - start_time) * 1000, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analysis with audio failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Document Processing Endpoints
# ============================================================================

@router.post("/extract-document", tags=["Documents"])
async def extract_document(
    file: UploadFile = File(..., description="Document file (PDF, PNG, JPG)"),
    document_type: str = Form("sale_deed", description="Document type"),
    property_id: Optional[str] = Form(None, description="Associated property ID")
):
    """
    Extract text and data from scanned document using Amazon Textract
    
    Supports:
    - Sale deeds
    - Mutation records
    - Encumbrance certificates
    - Partition deeds
    - Will documents
    """
    
    start_time = time.time()
    
    # Validate file type
    allowed_types = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {allowed_types}"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload to S3 first
        upload_result = s3_service.upload_document(
            file_content=file_content,
            filename=str(file.filename or 'document'),
            document_type=document_type,
            property_id=property_id
        )
        
        # Extract text using Textract
        extraction_result = textract_service.extract_land_document_data(
            document_bytes=file_content,
            document_type=document_type
        )
        
        return {
            "success": True,
            "data": {
                "extraction_id": extraction_result.get('extraction_id'),
                "document_type": document_type,
                "extracted_text": extraction_result.get('extracted_text'),
                "structured_data": extraction_result.get('structured_data'),
                "form_data": extraction_result.get('form_data'),
                "tables": extraction_result.get('tables'),
                "confidence_score": extraction_result.get('confidence_score'),
                "storage": {
                    "s3_key": upload_result.get('s3_key'),
                    "presigned_url": upload_result.get('presigned_url')
                }
            },
            "processing_time_ms": round((time.time() - start_time) * 1000, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Document extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{property_id}", tags=["Documents"])
async def list_property_documents(property_id: str):
    """List all documents for a property"""
    
    try:
        documents = s3_service.list_property_documents(property_id)
        
        return {
            "success": True,
            "data": {
                "property_id": property_id,
                "document_count": len(documents),
                "documents": documents
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Risk & Recommendations Endpoints
# ============================================================================

@router.post("/explain-risk", tags=["Analysis"])
async def explain_risk(risk_flag: dict):
    """
    Generate detailed explanation for a risk flag using AI
    """
    
    try:
        explanation = bedrock_service.generate_legal_explanation(risk_flag)
        
        return {
            "success": True,
            "data": {
                "risk_flag": risk_flag,
                "explanation": explanation
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Risk explanation failed: {str(e)}")
        # Return basic explanation
        return {
            "success": True,
            "data": {
                "risk_flag": risk_flag,
                "explanation": f"This risk ({risk_flag.get('title', 'Unknown')}) requires attention. Please consult a property lawyer for detailed guidance."
            },
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/family-tree/{property_id}", tags=["Analysis"])
async def get_family_tree(property_id: str):
    """
    Get family tree visualization data for property ownership
    """
    
    try:
        tree_data = land_records_service.get_family_tree(property_id)
        
        return {
            "success": True,
            "data": tree_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Family tree fetch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Cache Management Endpoints
# ============================================================================

@router.delete("/cache/{cache_key}", tags=["Cache"])
async def invalidate_cache(cache_key: str):
    """
    Invalidate cached analysis result
    """
    
    try:
        success = dynamo_service.invalidate_cache(cache_key)
        
        return {
            "success": success,
            "message": "Cache invalidated" if success else "Cache invalidation failed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache invalidation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats", tags=["Cache"])
async def get_cache_stats():
    """
    Get cache statistics
    """
    
    try:
        stats = dynamo_service.get_cache_stats()
        
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
