"""
Simple configuration access for SnelStart automation.
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


def get_snelstart_path():
    """Get SnelStart application path from environment or default."""
    return os.getenv('SNELSTART_PATH', DEFAULT_SNELSTART_PATH)


def get_credentials():
    """Get SnelStart credentials from environment variables."""
    username = os.getenv("SNELSTART_EMAIL")
    password = os.getenv("SNELSTART_PASSWORD")
    
    if not username or not password:
        raise ValueError("SnelStart credentials not found in environment variables")
    
    return username, password




def get_retry_config():
    """Get simple retry configuration with optional environment overrides."""
    return {
        'max_waiting_time': int(os.getenv('SNELSTART_MAX_WAITING_TIME', MAX_WAITING_TIME)),
        'max_retries': int(os.getenv('SNELSTART_MAX_RETRIES', MAX_RETRIES))
    }


def get_ui_elements():
    """Get UI element identifiers."""
    return {
        'login_dialog_text': LOGIN_DIALOG_TEXT,
        'admin_row_text': ADMIN_ROW_TEXT,
        'invoice_button_text': INVOICE_BUTTON_TEXT
    }


def get_log_level(class_name):
    """Get log level for a specific class.
    
    Checks environment variable first, then config file.
    Environment variable format: LOG_LEVEL_CLASSNAME (e.g., LOG_LEVEL_LOGINAUTOMATION)
    """
    env_var = f'LOG_LEVEL_{class_name.upper()}'
    return os.getenv(env_var, LOG_LEVELS.get(class_name, 'INFO'))


def get_log_format():
    """Get global logging format."""
    return LOG_FORMAT