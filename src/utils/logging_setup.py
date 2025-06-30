"""
Simple logging configuration for SnelStart automation.
"""

import logging
from .config import get_log_level, get_log_format


def setup_logging():
    """Setup global logging configuration."""
    log_format = get_log_format()
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        force=True  # Override any existing configuration
    )


def get_logger(class_name):
    """Get a configured logger for a specific class.
    
    Args:
        class_name: Name of the class (usually self.__class__.__name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(class_name)
    
    # Set class-specific log level
    log_level = get_log_level(class_name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    return logger