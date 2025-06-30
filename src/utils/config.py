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


def get_timing_config():
    """Get timing configuration values."""
    return {
        'window_timeout': WINDOW_TIMEOUT,
        'window_check_interval': WINDOW_CHECK_INTERVAL,
        'button_wait_time': BUTTON_WAIT_TIME,
        'login_wait_time': LOGIN_WAIT_TIME,
        'admin_open_wait_time': ADMIN_OPEN_WAIT_TIME
    }


def get_smart_wait_config():
    """Get smart wait timing configuration."""
    # Check for performance profile in environment
    profile = os.getenv('SNELSTART_TIMING_PROFILE', 'normal').lower()
    
    if profile in TIMING_PROFILES:
        return TIMING_PROFILES[profile]
    
    # Return default values if profile not found
    return {
        'element_timeout': DEFAULT_ELEMENT_TIMEOUT,
        'clickable_timeout': DEFAULT_CLICKABLE_TIMEOUT,
        'window_ready_timeout': DEFAULT_WINDOW_READY_TIMEOUT,
        'dialog_timeout': DEFAULT_DIALOG_TIMEOUT,
        'wait_interval': DEFAULT_WAIT_INTERVAL
    }


def get_wait_timeouts():
    """Get individual wait timeout values with environment variable overrides."""
    config = get_smart_wait_config()
    
    return {
        'element_timeout': float(os.getenv('SNELSTART_ELEMENT_TIMEOUT', config['element_timeout'])),
        'clickable_timeout': float(os.getenv('SNELSTART_CLICKABLE_TIMEOUT', config['clickable_timeout'])),
        'window_ready_timeout': float(os.getenv('SNELSTART_WINDOW_READY_TIMEOUT', config['window_ready_timeout'])),
        'dialog_timeout': float(os.getenv('SNELSTART_DIALOG_TIMEOUT', config['dialog_timeout'])),
        'text_input_timeout': float(os.getenv('SNELSTART_TEXT_INPUT_TIMEOUT', DEFAULT_TEXT_INPUT_TIMEOUT)),
        'wait_interval': float(os.getenv('SNELSTART_WAIT_INTERVAL', config['wait_interval']))
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