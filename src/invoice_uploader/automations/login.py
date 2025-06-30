import os
import time
from dotenv import load_dotenv
from pywinauto.controls.uiawrapper import UIAWrapper
from ...utils.logging_setup import LoggingSetup
from ...utils.config import Config
from ...utils.wait_utils import simple_retry, safe_type
from .launch_snelstart import LaunchAutomation

load_dotenv()

class LoginAutomation:
    """Handles SnelStart login automation."""
    
    def __init__(self):
        """Initialize the login automation."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.username, self.password = Config.get_credentials()
        self.ui_elements = Config.get_ui_elements()
        self.launch_automation = LaunchAutomation()
    
    def get_login_dialog(self, window: UIAWrapper):
        """Search for and return the login dialog inside the main window."""
        self.logger.info("Searching for login dialog inside main window...")
        for child in window.descendants():
            try:
                if child.friendly_class_name() == "Dialog" and self.ui_elements['login_dialog_text'] in child.window_text():
                    self.logger.info(f"Found login dialog: '{child.window_text()}'")
                    return child
            except Exception as e:
                self.logger.debug(f"Skipping element due to error: {e}")
        raise RuntimeError("Login dialog not found inside main window")

    def perform_login(self, login_window: UIAWrapper, username: str, password: str):
        """Perform the login sequence in the SnelStart login window."""
        self.logger.info("Attempting to perform login...")
        
        try:
            # Enter username
            self.logger.info("Entering username...")
            safe_type(login_window, username, "username field")
            
            # Navigate to password field
            self.logger.info("Navigating to password field...")
            login_window.type_keys("{TAB}")
            login_window.type_keys("{ENTER}")
            
            # Click "Doorgaan met wachtwoord"
            self.logger.info("Selecting password login option...")
            login_window.type_keys("{TAB}{TAB}{ENTER}")
            
            # Wait briefly for password field to be ready
            time.sleep(0.5)
            
            # Enter password
            self.logger.info("Entering password...")
            safe_type(login_window, password, "password field")
            
            # Submit login
            self.logger.info("Submitting login...")
            login_window.type_keys("{ENTER}")
            
            self.logger.info("Login attempt complete")
            
        except Exception as e:
            self.logger.error(f"Error during login sequence: {e}")
            raise

    def is_logged_in(self):
        """Check if user is already logged in by verifying absence of separate login window."""
        self.logger.info("Checking if user is already logged in...")
        
        # Check if login window exists
        login_window = self.launch_automation.get_login_window()
        
        if login_window is not None:
            # Login window exists, user is not logged in
            self.logger.info("Login window found - user is not logged in")
            return False
        else:
            # Login window does not exist, user is logged in
            self.logger.info("Login window not found - user is logged in")
            return True

    def login_to_snelstart(self):
        """Main login function that handles the complete login process."""
        try:
            # First, check if we're already logged in
            if self.is_logged_in():
                self.logger.info("User is already logged in.")
                return True
            
            # Not logged in, so look for login window
            login_window = self.launch_automation.get_login_window()
            if login_window is None:
                self.logger.warning("Login window not found and user not logged in — this is unexpected.")
                return False

            self.logger.info("Login window found — checking for auto-login...")
            
            # Wait briefly to see if the window disappears automatically (auto-login)
            time.sleep(10)
            if self.is_logged_in():
                self.logger.info("Auto-login succeeded - login window disappeared.")
                return True

            # Still not logged in? Get the login window again and perform manual login
            login_window = self.launch_automation.get_login_window()
            if login_window is None:
                # Window disappeared, check if we're logged in
                if self.is_logged_in():
                    self.logger.info("Login window disappeared during wait - auto-login succeeded.")
                    return True
                else:
                    self.logger.error("Login window disappeared but user not logged in.")
                    return False

            # Perform manual login
            self.perform_login(login_window, self.username, self.password)
            
            # Wait a moment for login to complete, then verify
            time.sleep(3)
            login_success = self.is_logged_in()
            
            if login_success:
                self.logger.info("Manual login completed successfully")
            else:
                self.logger.error("Manual login failed - user not logged in after login attempt")
            
            return login_success

        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False


# Backwards compatibility functions for existing code
def get_login_dialog(window: UIAWrapper):
    """Backwards compatibility function - DEPRECATED: Login is now a separate window."""
    login_automation = LoginAutomation()
    return login_automation.get_login_dialog(window)

def perform_login(login_window: UIAWrapper, username: str, password: str):
    """Backwards compatibility function."""
    login_automation = LoginAutomation()
    login_automation.perform_login(login_window, username, password)

def login_to_snelstart(window: UIAWrapper = None):
    """Backwards compatibility function. Window parameter is ignored in new implementation."""
    login_automation = LoginAutomation()
    return login_automation.login_to_snelstart()

def is_logged_in():
    """New function for checking login status."""
    login_automation = LoginAutomation()
    return login_automation.is_logged_in()