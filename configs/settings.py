"""
Simple configuration settings for SnelStart automation.
"""

# Application defaults
DEFAULT_SNELSTART_PATH = r'C:\Program Files\Snelstart\Snelstart.exe'

# Simple retry configuration
MAX_RETRIES = 10          # How many times to retry operations
RETRY_DELAY = 1.0         # Seconds to wait between retries

# Legacy timing settings (for backward compatibility) 
WINDOW_TIMEOUT = 30
WINDOW_CHECK_INTERVAL = 5
BUTTON_WAIT_TIME = 2  # Legacy - use smart waits instead
LOGIN_WAIT_TIME = 2   # Legacy - use smart waits instead  
ADMIN_OPEN_WAIT_TIME = 5  # Legacy - use smart waits instead

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