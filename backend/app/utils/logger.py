"""
Logging configuration for LandLedger
Supports local logging and AWS CloudWatch integration
"""

import logging
import sys
from typing import Optional

from app.config import settings


def setup_logging(
    level: Optional[str] = None,
    enable_cloudwatch: bool = False
) -> logging.Logger:
    """
    Setup application logging
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        enable_cloudwatch: Whether to enable CloudWatch logging
        
    Returns:
        Configured root logger
    """
    
    log_level = level or ("DEBUG" if settings.DEBUG else "INFO")
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # CloudWatch handler (if enabled and watchtower is available)
    if enable_cloudwatch:
        try:
            import watchtower  # type: ignore
            import boto3  # type: ignore
            
            cloudwatch_handler = watchtower.CloudWatchLogHandler(
                log_group=f"/landledger/{settings.ENVIRONMENT}",
                stream_name=f"backend-{settings.APP_VERSION}",
                boto3_client=boto3.client(
                    'logs',
                    region_name=settings.AWS_REGION,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
            )
            cloudwatch_handler.setLevel(getattr(logging, log_level))
            cloudwatch_handler.setFormatter(formatter)
            root_logger.addHandler(cloudwatch_handler)
            
            root_logger.info("CloudWatch logging enabled")
            
        except ImportError:
            root_logger.warning("watchtower not installed, CloudWatch logging disabled")
        except Exception as e:
            root_logger.warning(f"CloudWatch logging could not be enabled: {e}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Named logger instance
    """
    return logging.getLogger(name)


# Application-specific loggers
class StructuredLogger:
    """Structured logger for consistent log formatting"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _format_extra(self, **kwargs) -> str:
        """Format extra data for log message"""
        if not kwargs:
            return ""
        return " | " + " | ".join(f"{k}={v}" for k, v in kwargs.items())
    
    def info(self, message: str, **kwargs):
        """Log info message with extra data"""
        self.logger.info(f"{message}{self._format_extra(**kwargs)}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message with extra data"""
        self.logger.debug(f"{message}{self._format_extra(**kwargs)}")
    
    def warning(self, message: str, **kwargs):
        """Log warning message with extra data"""
        self.logger.warning(f"{message}{self._format_extra(**kwargs)}")
    
    def error(self, message: str, **kwargs):
        """Log error message with extra data"""
        self.logger.error(f"{message}{self._format_extra(**kwargs)}")
    
    def critical(self, message: str, **kwargs):
        """Log critical message with extra data"""
        self.logger.critical(f"{message}{self._format_extra(**kwargs)}")


def get_structured_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)
