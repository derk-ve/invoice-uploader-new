import os
import time
from dotenv import load_dotenv
from pywinauto.controls.uiawrapper import UIAWrapper
from ...utils.logging_setup import LoggingSetup
from ...utils.config import Config
from ...utils.wait_utils import simple_retry, safe_type

load_dotenv()

class LoginAutomation:
    """Handles SnelStart login automation."""
    
    def __init__(self):
        """Initialize the login automation."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.username, self.password = Config.get_credentials()
        self.ui_elements = Config.get_ui_elements()
    
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

    def perform_login(self, login_dialog: UIAWrapper, username: str, password: str):
        """Perform the login sequence in the SnelStart application."""
        self.logger.info("Attempting to perform login...")
        
        try:
            # Enter username
            self.logger.info("Entering username...")
            safe_type(login_dialog, username, "username field")
            
            # Navigate to password field
            self.logger.info("Navigating to password field...")
            login_dialog.type_keys("{TAB}")
            login_dialog.type_keys("{ENTER}")
            
            # Click "Doorgaan met wachtwoord"
            self.logger.info("Selecting password login option...")
            login_dialog.type_keys("{TAB}{TAB}{ENTER}")
            
            # Wait briefly for password field to be ready
            time.sleep(0.5)
            
            # Enter password
            self.logger.info("Entering password...")
            safe_type(login_dialog, password, "password field")
            
            # Submit login
            self.logger.info("Submitting login...")
            login_dialog.type_keys("{ENTER}")
            
            self.logger.info("Login attempt complete")
            
        except Exception as e:
            self.logger.error(f"Error during login sequence: {e}")
            raise

    def is_logged_in(self, window: UIAWrapper):
        """Check if user is already logged in by verifying absence of login dialog."""
        self.logger.info("Checking if user is already logged in...")
        
        try:
            # Try to find the login dialog
            self.get_login_dialog(window)
            # If we found the login dialog, user is not logged in
            self.logger.info("Login dialog found - user is not logged in")
            return False
            
        except Exception:
            # If login dialog is not found, user is logged in
            self.logger.info("Login dialog not found - user is logged in")
            return True

    def login_to_snelstart(self, window: UIAWrapper):
        """Main login function that handles the complete login process."""
        try:
            # First, check if we're already logged in
            if self.is_logged_in(window):
                self.logger.info("User is already logged in.")
                return True
            
            # Not logged in, so look for login dialog
            try:
                # Use wait_utils retry logic with the proven get_login_dialog method
                def find_login_dialog():
                    return self.get_login_dialog(window)
                
                login_dialog = simple_retry(find_login_dialog, "find login dialog")
                self.logger.info(f"Found and verified login dialog is ready")
            except Exception:
                self.logger.warning("Login dialog not found and user not logged in — this is unexpected.")
                return False

            # Wait briefly to see if the dialog disappears automatically (auto-login)
            self.logger.info("Login dialog found — checking for auto-login...")
            try:
                time.sleep(2)
                if not login_dialog.exists() or not login_dialog.is_visible():
                    self.logger.info("Login dialog disappeared — checking if auto-login succeeded.")
                    # Verify that we're actually logged in now
                    return self.is_logged_in(window)
            except Exception:
                self.logger.info("Login dialog no longer accessible — checking if auto-login succeeded.")
                # Verify that we're actually logged in now
                return self.is_logged_in(window)

            # Still exists and not logged in? Then perform manual login
            self.perform_login(login_dialog, self.username, self.password)
            
            # Wait a moment for login to complete, then verify
            time.sleep(3)
            login_success = self.is_logged_in(window)
            
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
    """Backwards compatibility function."""
    login_automation = LoginAutomation()
    return login_automation.get_login_dialog(window)

def perform_login(login_dialog: UIAWrapper, username: str, password: str):
    """Backwards compatibility function."""
    login_automation = LoginAutomation()
    login_automation.perform_login(login_dialog, username, password)

def login_to_snelstart(window: UIAWrapper):
    """Backwards compatibility function."""
    login_automation = LoginAutomation()
    return login_automation.login_to_snelstart(window)