"""
Simple configuration settings for SnelStart automation.
"""

# Application defaults
DEFAULT_SNELSTART_PATH = r'C:\Program Files\Snelstart\Snelstart.exe'

# Timing configuration - Smart wait system
WINDOW_TIMEOUT = 30
WINDOW_CHECK_INTERVAL = 5
BUTTON_WAIT_TIME = 2  # Legacy - use smart waits instead
LOGIN_WAIT_TIME = 2   # Legacy - use smart waits instead
ADMIN_OPEN_WAIT_TIME = 5  # Legacy - use smart waits instead

# Smart wait timeouts and intervals
DEFAULT_ELEMENT_TIMEOUT = 30
DEFAULT_CLICKABLE_TIMEOUT = 10
DEFAULT_WINDOW_READY_TIMEOUT = 20
DEFAULT_DIALOG_TIMEOUT = 15
DEFAULT_TEXT_INPUT_TIMEOUT = 5

# Wait retry intervals
DEFAULT_WAIT_INTERVAL = 0.5
DEFAULT_CLICKABLE_INTERVAL = 0.2
DEFAULT_WINDOW_READY_INTERVAL = 0.5

# System performance profiles
TIMING_PROFILES = {
    'fast': {
        'element_timeout': 15,
        'clickable_timeout': 5,
        'window_ready_timeout': 10,
        'dialog_timeout': 8,
        'wait_interval': 0.3
    },
    'normal': {
        'element_timeout': 30,
        'clickable_timeout': 10,
        'window_ready_timeout': 20,
        'dialog_timeout': 15,
        'wait_interval': 0.5
    },
    'slow': {
        'element_timeout': 60,
        'clickable_timeout': 20,
        'window_ready_timeout': 40,
        'dialog_timeout': 30,
        'wait_interval': 1.0
    }
}

# UI element identifiers
LOGIN_DIALOG_TEXT = "Inloggen"
ADMIN_ROW_TEXT = "Row 1"
INVOICE_BUTTON_TEXT = "Afschriften Inlezen"

# Global logging format - easy to adjust
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s - [%(name)s.%(funcName)s]'

# Per-class log levels (can be overridden by environment variables)
LOG_LEVELS = {
    'LoginAutomation': 'INFO',
    'LaunchAutomation': 'INFO', 
    'AdministrationAutomation': 'INFO',
    'InvoiceReaderAutomation': 'INFO',
    'SnelstartAutomation': 'INFO'
}