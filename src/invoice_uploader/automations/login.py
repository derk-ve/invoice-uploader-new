import os
import time
from dotenv import load_dotenv
from pywinauto.controls.uiawrapper import UIAWrapper
from ...utils.logging_setup import LoggingSetup
from ...utils.config import Config
from ...utils.wait_utils import simple_retry, safe_type
from .launch_snelstart import LaunchAutomation
from ...utils.ui_utils import generate_window_report

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

    def perform_login(self, login_dialog: UIAWrapper, username: str, password: str):
        """Perform the login sequence in the SnelStart login dialog."""
        self.logger.info("Attempting to perform login...")
        
        try:
            # Focus the login dialog
            login_dialog.set_focus()
            time.sleep(2)
            
            # Enter username
            self.logger.info("Entering username...")
            login_dialog.type_keys(username, with_spaces=True)
            time.sleep(2)
            
            # Navigate to password field
            self.logger.info("Navigating to password field...")
            login_dialog.type_keys("{TAB}")
            time.sleep(2)
            login_dialog.type_keys("{ENTER}")
            time.sleep(2)
            
            # Click "Doorgaan met wachtwoord"
            self.logger.info("Selecting password login option...")
            login_dialog.type_keys("{TAB}{TAB}{ENTER}")
            time.sleep(2)
            
            # Enter password
            self.logger.info("Entering password...")
            login_dialog.type_keys(password, with_spaces=True)
            time.sleep(2)
            
            # Submit login
            self.logger.info("Submitting login...")
            login_dialog.type_keys("{ENTER}")
            
            self.logger.info("Login attempt complete")
            
        except Exception as e:
            self.logger.error(f"Error during login sequence: {e}")
            raise

    def is_logged_in(self, main_window: UIAWrapper = None):
        """Check if user is already logged in by verifying absence of login dialog in main window."""
        self.logger.info("Checking if user is already logged in...")
        
        try:
            # Get main window if not provided
            if main_window is None:
                main_window = self.launch_automation.get_main_window()
            
            # Check if login dialog exists in main window
            try:
                login_dialog = self.get_login_dialog(main_window)
                # Login dialog exists, user is not logged in
                self.logger.info("Login dialog found in main window - user is not logged in")
                return False
            except RuntimeError:
                # Login dialog not found, user is logged in
                self.logger.info("Login dialog not found in main window - user is logged in")
                return True
                
        except Exception as e:
            self.logger.warning(f"Error checking login status: {e}")
            # If we can't determine, assume not logged in to be safe
            return False

    def login_to_snelstart(self, main_window: UIAWrapper = None):
        """Main login function that handles the complete login process."""
        try:
            # Get main window if not provided
            if main_window is None:
                main_window = self.launch_automation.get_main_window()
            
            # Try to find login dialog inside main window
            try:
                login_dialog = self.get_login_dialog(main_window)
            except RuntimeError:
                self.logger.info("Login dialog not found — assuming already logged in.")
                return True

            # Wait briefly to see if the dialog disappears automatically (auto-login)
            self.logger.info("Login dialog found — waiting briefly to check for auto-login...")
            time.sleep(5)
            
            try:
                # Check if dialog still exists and is visible
                if not login_dialog.is_visible():
                    self.logger.info("Login dialog is no longer visible — assuming auto-login succeeded.")
                    return True
            except Exception:
                self.logger.info("Login dialog no longer exists — assuming auto-login succeeded.")
                return True

            # Still exists? Then perform manual login
            self.perform_login(login_dialog, self.username, self.password)
            
            # Wait a moment for login to complete
            time.sleep(3)
            self.logger.info("Manual login completed successfully")
            return True

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
    """Backwards compatibility function. Window parameter is used as main window."""
    login_automation = LoginAutomation()
    return login_automation.login_to_snelstart(window)

def is_logged_in(main_window: UIAWrapper = None):
    """New function for checking login status."""
    login_automation = LoginAutomation()
    return login_automation.is_logged_in(main_window)