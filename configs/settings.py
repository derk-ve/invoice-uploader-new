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

# UI element identifiers
LOGIN_DIALOG_TEXT = "Inloggen"
ADMIN_ROW_TEXT = "Row 1"
INVOICE_BUTTON_TEXT = "Afschriften Inlezen"

# Global logging format - easy to adjust
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s - [%(name)s.%(funcName)s]'

# Per-class log levels (can be overridden by environment variables)
LOG_LEVELS = {
    # Class-based loggers (for use with get_logger(class_name))
    'LoginAutomation': 'INFO',
    'LaunchAutomation': 'INFO',
    'AdministrationAutomation': 'INFO',
    'InvoiceReaderAutomation': 'INFO',
    'SnelstartAutomation': 'INFO',

    # Module-level loggers (for use with logging.getLogger(__name__) or get_logger(__name__))
    'main': 'INFO',
    'utils.ui_utils': 'INFO',
    'utils.wait_utils': 'DEBUG',
    'invoice_uploader.automations.administration': 'INFO',
    'invoice_uploader.automations.launch_snelstart': 'INFO',
    'invoice_uploader.automations.login': 'INFO',
    'invoice_uploader.automations.read_invoices': 'INFO',
    'invoice_uploader.snelstart_automation': 'INFO',
    'invoice_uploader.tests.test_connection': 'INFO'
}