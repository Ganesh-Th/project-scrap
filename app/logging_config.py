"""Logging configuration with file rotation."""
import logging
import os
from logging.handlers import RotatingFileHandler
from app.config import get_settings


def setup_logging() -> logging.Logger:
    """Configure application logging with file rotation and console output."""
    settings = get_settings()
    
    # Create logs directory
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Get root logger
    logger = logging.getLogger("scraper_api")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    logger.handlers = []
    
    # File handler with rotation
    try:
        file_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")
    
    return logger


def get_logger(name: str = "scraper_api") -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
