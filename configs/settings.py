"""
Simple configuration settings for SnelStart automation.
"""

# Application defaults
DEFAULT_SNELSTART_PATH = r'C:\Program Files\Snelstart\Snelstart.exe'

# Simple retry configuration
MAX_WAITING_TIME = 30     # Maximum seconds to wait per retry attempt
MAX_RETRIES = 3           # Maximum number of retries

# Timing configuration for automation actions
TIMING_CONFIG = {
    'login': {
        'dialog_focus_delay': 2,        # Time to wait after focusing login dialog
        'input_delay': 3,               # Time to wait between input steps
        'auto_login_wait': 5,           # Time to wait for auto-login to complete
        'login_completion_wait': 3,     # Time to wait after manual login submission
        'login_dialog_wait_timeout': 10, # Time to wait for login dialog to appear
        'login_dialog_wait_interval': 2, # Interval between login dialog detection attempts
        'login_completion_timeout': 10   # Time to wait for login completion verification
    },
    'launch': {
        'default_timeout': 30,       # Default timeout for window detection
        'default_interval': 5        # Default interval for window polling
    },
    'administration': {
        'workspace_ready_timeout': 30, # Time to wait for workspace to load after clicking Row 1
        'boekhouden_tab_timeout': 15,  # Time to wait for BOEKHOUDEN tab to become available
        'boekhouden_ready_timeout': 15 # Time to wait for bookkeeping interface to load
    },
    'invoice_matching': {
        'amount_tolerance': 0.01,           # Default amount tolerance for matching
        'case_sensitive_description': False, # Case sensitivity for description matching
        'require_exact_invoice_number': True, # Require exact invoice number match
        'minimum_confidence_score': 0.7,    # Minimum confidence score for matches
        'max_matches_per_transaction': 1     # Maximum matches per transaction
    }
}


# UI element identifiers
LOGIN_DIALOG_TEXT = "Inloggen"
ADMIN_ROW_TEXT = "Row 1"
INVOICE_BUTTON_TEXT = "Afschriften Inlezen"
BOEKHOUDEN_TAB_TEXT = "BOEKHOUDEN"

# Window title patterns
MAIN_WINDOW_TITLE = "SnelStart 12"
LOGIN_WINDOW_TITLE = "Inloggen SnelStart 12"

# Login verification elements (only visible when logged in)
LOGIN_VERIFICATION_TAB = "ADMINISTRATIE"
LOGIN_VERIFICATION_BUTTON = "Administraties"

# Global logging format - easy to adjust
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s - [%(name)s.%(funcName)s]'

# Global logging configuration
DEFAULT_LOG_LEVEL = 'INFO'  # Default level for loggers not explicitly defined
GLOBAL_ROOT_LEVEL = 'DEBUG'  # Root logger level - set to DEBUG to allow all configured levels through

# Per-class log levels (can be overridden by environment variables)
LOG_LEVELS = {
    # Class-based loggers (for automation classes using self.__class__.__name__)
    'LoginAutomation': 'INFO',
    'LaunchAutomation': 'DEBUG', 
    'NavigateToBookkeepingAutomation': 'INFO',
    'DoBookkeepingAutomation': 'INFO',
    'SnelstartAutomation': 'INFO',
    'InvoiceMatcher': 'INFO',
    'PDFScanner': 'DEBUG',
    'MT940Parser': 'INFO',
    'UIUtils': 'INFO',
    'WaitUtils': 'DEBUG',
    'Config': 'INFO',
    'LoggingSetup': 'INFO',

    # Module-level loggers (for files using __name__)
    '__main__': 'INFO',  # main.py
    'src.invoice_uploader.tests.test_connection': 'INFO',  # test_connection.py
}