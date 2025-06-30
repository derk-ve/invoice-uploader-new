"""
Simple configuration settings for SnelStart automation.
"""

# Application defaults
DEFAULT_SNELSTART_PATH = r'C:\Program Files\Snelstart\Snelstart.exe'

# Simple timing configuration
WINDOW_TIMEOUT = 30       # How long to wait for windows to appear/be ready
ELEMENT_TIMEOUT = 15      # How long to wait for UI elements to exist  
CLICKABLE_TIMEOUT = 10    # How long to wait for elements to be clickable
RETRY_INTERVAL = 0.5      # How often to retry (seconds between attempts)

# Legacy timing settings (for backward compatibility)
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