"""
Logging configuration for SnelStart automation.
"""

import logging
from .config import Config


class LoggingSetup:
    """Handles logging configuration and logger creation."""
    
    @staticmethod
    def setup_logging():
        """Setup global logging configuration."""
        log_format = Config.get_log_format()
        root_level = Config.get_global_root_level()
        
        # Configure root logger with configurable level
        logging.basicConfig(
            level=getattr(logging, root_level.upper(), logging.INFO),
            format=log_format,
            force=True  # Override any existing configuration
        )

    @staticmethod  
    def get_logger(class_name):
        """Get a configured logger for a specific class.
        
        Args:
            class_name: Name of the class (usually self.__class__.__name__)
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(class_name)
        
        # Set class-specific log level
        log_level = Config.get_log_level(class_name)
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        return logger


# Create singleton instance for easy access
logging_setup = LoggingSetup()

# Backwards compatibility functions for existing code
def setup_logging():
    return logging_setup.setup_logging()

def get_logger(class_name):
    return logging_setup.get_logger(class_name)