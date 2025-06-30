"""
Simple configuration settings for SnelStart automation.
"""

# Application defaults
DEFAULT_SNELSTART_PATH = r'C:\Program Files\Snelstart\Snelstart.exe'

# Timing configuration
WINDOW_TIMEOUT = 30
WINDOW_CHECK_INTERVAL = 5
BUTTON_WAIT_TIME = 2
LOGIN_WAIT_TIME = 2
ADMIN_OPEN_WAIT_TIME = 5

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