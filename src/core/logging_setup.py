import structlog
import logging
import sys
from datetime import datetime
from src.core.config import settings

def setup_logging():
    """Configure structured logging"""
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper())
    )
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if settings.DEBUG else structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False
    )

logger = structlog.get_logger()

def log_prediction(transaction_id: str, prediction: bool, probability: float, risk_level: str):
    """Log prediction with structured data"""
    logger.info(
        "prediction_made",
        transaction_id=transaction_id,
        prediction=prediction,
        fraud_probability=probability,
        risk_level=risk_level,
        timestamp=datetime.utcnow().isoformat()
    )

def log_api_request(method: str, endpoint: str, status_code: int, duration_ms: float):
    """Log API request"""
    logger.info(
        "api_request",
        method=method,
        endpoint=endpoint,
        status_code=status_code,
        duration_ms=duration_ms
    )

def log_error(error_type: str, message: str, **kwargs):
    """Log error with context"""
    logger.error(
        "error_occurred",
        error_type=error_type,
        message=message,
        **kwargs
    )

def log_cache_operation(operation: str, key: str, hit: bool = None):
    """Log cache operations"""
    logger.debug(
        "cache_operation",
        operation=operation,
        key=key,
        hit=hit
    )
