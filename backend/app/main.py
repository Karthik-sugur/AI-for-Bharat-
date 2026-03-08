"""
LandLedger Backend - Main Application
AI-Powered Land Title Intelligence using AWS Services
"""

import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"AWS Region: {settings.AWS_REGION}")
    
    # Initialize services
    try:
        from app.services.s3_service import s3_service
        from app.services.dynamo_service import dynamo_service
        
        # Ensure S3 bucket exists
        s3_service.ensure_bucket_exists()
        logger.info("S3 service initialized")
        
        # Check DynamoDB table
        dynamo_service.get_cache_stats()
        logger.info("DynamoDB service initialized")
        
    except Exception as e:
        logger.warning(f"Some services may not be available: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## LandLedger - AI-Powered Land Title Intelligence
    
    Comprehensive land ownership verification and risk assessment platform for India.
    
    ### Features
    - **Property Analysis**: Comprehensive ownership chain reconstruction
    - **Risk Assessment**: AI-powered title confidence scoring
    - **Document OCR**: Extract data from scanned land documents
    - **Voice Output**: Audio summaries in English and Hindi
    
    ### AWS Services
    - Amazon Bedrock (AI Analysis)
    - Amazon Textract (Document OCR)
    - Amazon Polly (Text-to-Speech)
    - Amazon S3 (Document Storage)
    - Amazon DynamoDB (Caching)
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Include API routes
app.include_router(router, prefix=settings.API_PREFIX)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-Powered Land Title Intelligence API",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "health": f"{settings.API_PREFIX}/health",
            "analyze": f"{settings.API_PREFIX}/analyze",
            "extract_document": f"{settings.API_PREFIX}/extract-document",
            "analyze_with_audio": f"{settings.API_PREFIX}/analyze-with-audio"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
