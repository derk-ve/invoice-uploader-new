import os
import time
from dotenv import load_dotenv
from pywinauto.controls.uiawrapper import UIAWrapper
from ...utils.logging_setup import get_logger
from ...utils.config import get_credentials, get_timing_config, get_ui_elements, get_wait_timeouts
from ...utils.wait_utils import wait_for_dialog_ready, wait_for_text_input_ready, safe_type, safe_click

load_dotenv()

class LoginAutomation:
    """Handles SnelStart login automation."""
    
    def __init__(self):
        """Initialize the login automation."""
        self.logger = get_logger(self.__class__.__name__)
        self.username, self.password = get_credentials()
        self.timing = get_timing_config()
        self.ui_elements = get_ui_elements()
        self.wait_timeouts = get_wait_timeouts()
    
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
            # Ensure dialog is ready for interaction
            ready_dialog = wait_for_text_input_ready(login_dialog, self.wait_timeouts['text_input_timeout'])
            
            # Enter username
            self.logger.info("Entering username...")
            safe_type(ready_dialog, username, self.wait_timeouts['text_input_timeout'], "username field")
            
            # Navigate to password field
            self.logger.info("Navigating to password field...")
            ready_dialog.type_keys("{TAB}")
            ready_dialog.type_keys("{ENTER}")
            
            # Click "Doorgaan met wachtwoord"
            self.logger.info("Selecting password login option...")
            ready_dialog.type_keys("{TAB}{TAB}{ENTER}")
            
            # Wait briefly for password field to be ready
            time.sleep(0.5)
            
            # Enter password
            self.logger.info("Entering password...")
            safe_type(ready_dialog, password, self.wait_timeouts['text_input_timeout'], "password field")
            
            # Submit login
            self.logger.info("Submitting login...")
            ready_dialog.type_keys("{ENTER}")
            
            self.logger.info("Login attempt complete")
            
        except Exception as e:
            self.logger.error(f"Error during login sequence: {e}")
            raise

    def login_to_snelstart(self, window: UIAWrapper):
        """Main login function that handles the complete login process."""
        try:
            try:
                login_dialog = wait_for_dialog_ready(window, self.ui_elements['login_dialog_text'], 
                                                    self.wait_timeouts['dialog_timeout'])
                self.logger.info(f"Found and verified login dialog is ready")
            except Exception:
                self.logger.info("Login dialog not found — assuming already logged in.")
                return True

            # Wait briefly to see if the dialog disappears automatically (auto-login)
            self.logger.info("Login dialog found — checking for auto-login...")
            try:
                time.sleep(2)
                if not login_dialog.exists() or not login_dialog.is_visible():
                    self.logger.info("Login dialog disappeared — auto-login succeeded.")
                    return True
            except Exception:
                self.logger.info("Login dialog no longer accessible — auto-login succeeded.")
                return True

            # Still exists? Then perform manual login
            self.perform_login(login_dialog, self.username, self.password)
            return True

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