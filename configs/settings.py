"""
Simple configuration settings for SnelStart automation.
"""

# Application defaults
DEFAULT_SNELSTART_PATH = r'C:\Program Files\Snelstart\Snelstart.exe'

# Simple retry configuration
MAX_WAITING_TIME = 30     # Maximum seconds to wait per retry attempt
MAX_RETRIES = 3           # Maximum number of retries


# UI element identifiers
LOGIN_DIALOG_TEXT = "Inloggen"
ADMIN_ROW_TEXT = "Row 1"
INVOICE_BUTTON_TEXT = "Afschriften Inlezen"

# Global logging format - easy to adjust
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s - [%(name)s.%(funcName)s]'

# Global logging configuration
DEFAULT_LOG_LEVEL = 'INFO'  # Default level for loggers not explicitly defined
GLOBAL_ROOT_LEVEL = 'DEBUG'  # Root logger level - set to DEBUG to allow all configured levels through

# Per-class log levels (can be overridden by environment variables)
LOG_LEVELS = {
    # Class-based loggers (for automation classes using self.__class__.__name__)
    'LoginAutomation': 'INFO',
    'LaunchAutomation': 'INFO', 
    'AdministrationAutomation': 'INFO',
    'InvoiceReaderAutomation': 'INFO',
    'SnelstartAutomation': 'INFO',
    'UIUtils': 'INFO',
    'WaitUtils': 'DEBUG',
    'Config': 'INFO',
    'LoggingSetup': 'INFO',

    # Module-level loggers (for files using __name__)
    '__main__': 'INFO',  # main.py
    'src.invoice_uploader.tests.test_connection': 'INFO',  # test_connection.py
}