"""
Configuration file for LandLedger API
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Gemini AI settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')
    
    # Data paths
    DATA_PATH = os.environ.get('DATA_PATH', str(BASE_DIR / 'data' / 'synthetic_data.json'))
    SAMPLE_QUERIES_PATH = os.environ.get('SAMPLE_QUERIES_PATH', str(BASE_DIR / 'data' / 'sample_queries.json'))
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Risk assessment thresholds
    RISK_SCORE_HIGH = int(os.environ.get('RISK_SCORE_HIGH', 700))
    RISK_SCORE_MEDIUM = int(os.environ.get('RISK_SCORE_MEDIUM', 850))
    RISK_SCORE_LOW = int(os.environ.get('RISK_SCORE_LOW', 900))
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def init_app(app):
        """Initialize application configuration"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
