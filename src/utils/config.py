"""
Configuration access for SnelStart automation.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration settings
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from configs.settings import *


class Config:
    """Configuration manager for SnelStart automation."""
    
    @staticmethod
    def get_snelstart_path():
        """Get SnelStart application path from environment or default."""
        return os.getenv('SNELSTART_PATH', DEFAULT_SNELSTART_PATH)

    @staticmethod
    def get_credentials():
        """Get SnelStart credentials from environment variables."""
        username = os.getenv("SNELSTART_EMAIL")
        password = os.getenv("SNELSTART_PASSWORD")
        
        if not username or not password:
            raise ValueError("SnelStart credentials not found in environment variables")
        
        return username, password

    @staticmethod
    def get_retry_config():
        """Get simple retry configuration with optional environment overrides."""
        return {
            'max_waiting_time': int(os.getenv('SNELSTART_MAX_WAITING_TIME', MAX_WAITING_TIME)),
            'max_retries': int(os.getenv('SNELSTART_MAX_RETRIES', MAX_RETRIES))
        }

    @staticmethod
    def get_ui_elements():
        """Get UI element identifiers."""
        return {
            'login_dialog_text': LOGIN_DIALOG_TEXT,
            'admin_row_text': ADMIN_ROW_TEXT,
            'invoice_button_text': INVOICE_BUTTON_TEXT,
            'login_verification_tab': LOGIN_VERIFICATION_TAB,
            'login_verification_button': LOGIN_VERIFICATION_BUTTON
        }

    @staticmethod
    def get_window_titles():
        """Get window title patterns."""
        return {
            'main_window': MAIN_WINDOW_TITLE,
            'login_window': LOGIN_WINDOW_TITLE
        }

    @staticmethod
    def get_log_level(class_name):
        """Get log level for a specific class.
        
        Checks environment variable first, then config file.
        Environment variable format: LOG_LEVEL_CLASSNAME (e.g., LOG_LEVEL_LOGINAUTOMATION)
        """
        env_var = f'LOG_LEVEL_{class_name.upper()}'
        return os.getenv(env_var, LOG_LEVELS.get(class_name, Config.get_default_log_level()))

    @staticmethod
    def get_log_format():
        """Get global logging format."""
        return LOG_FORMAT

    @staticmethod
    def get_global_root_level():
        """Get global root logger level.
        
        Checks environment variable first, then config file.
        Environment variable: ROOT_LOG_LEVEL (e.g., ROOT_LOG_LEVEL=DEBUG)
        """
        return os.getenv('ROOT_LOG_LEVEL', GLOBAL_ROOT_LEVEL)

    @staticmethod
    def get_default_log_level():
        """Get default log level for undefined loggers.
        
        Checks environment variable first, then config file.
        Environment variable: DEFAULT_LOG_LEVEL (e.g., DEFAULT_LOG_LEVEL=DEBUG)
        """
        from configs.settings import DEFAULT_LOG_LEVEL as default_level
        return os.getenv('DEFAULT_LOG_LEVEL', default_level)

    @staticmethod
    def get_timing_config(module_name=None):
        """Get timing configuration for automation modules.
        
        Args:
            module_name: Optional module name (e.g., 'login', 'launch', 'administration')
                        If None, returns entire timing config
        
        Returns:
            Timing configuration dict
        """
        from configs.settings import TIMING_CONFIG
        if module_name:
            return TIMING_CONFIG.get(module_name, {})
        return TIMING_CONFIG


# Create singleton instance for easy access
config = Config()

# Backwards compatibility functions for existing code
def get_snelstart_path():
    return config.get_snelstart_path()

def get_credentials():
    return config.get_credentials()

def get_retry_config():
    return config.get_retry_config()

def get_ui_elements():
    return config.get_ui_elements()

def get_window_titles():
    return config.get_window_titles()

def get_log_level(class_name):
    return config.get_log_level(class_name)

def get_log_format():
    return config.get_log_format()

def get_global_root_level():
    return config.get_global_root_level()

def get_default_log_level():
    return config.get_default_log_level()