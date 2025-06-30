import os
import time
from dotenv import load_dotenv
from pywinauto.controls.uiawrapper import UIAWrapper
from ...utils.logging_setup import get_logger
from ...utils.config import get_credentials, get_timing_config, get_ui_elements

load_dotenv()

class LoginAutomation:
    """Handles SnelStart login automation."""
    
    def __init__(self):
        """Initialize the login automation."""
        self.logger = get_logger(self.__class__.__name__)
        self.username, self.password = get_credentials()
        self.timing = get_timing_config()
        self.ui_elements = get_ui_elements()
    
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
        
        wait_time = self.timing['login_wait_time']
        
        # Focus the login dialog
        login_dialog.set_focus()
        time.sleep(wait_time)
        
        # Enter username
        self.logger.info("Entering username...")
        login_dialog.type_keys(username, with_spaces=True)
        time.sleep(wait_time)
        
        # Navigate to password field
        self.logger.info("Navigating to password field...")
        login_dialog.type_keys("{TAB}")
        time.sleep(wait_time)
        login_dialog.type_keys("{ENTER}")
        time.sleep(wait_time)
        
        # Click "Doorgaan met wachtwoord"
        self.logger.info("Selecting password login option...")
        login_dialog.type_keys("{TAB}{TAB}{ENTER}")
        time.sleep(wait_time)
        
        # Enter password
        self.logger.info("Entering password...")
        login_dialog.type_keys(password, with_spaces=True)
        time.sleep(wait_time)
        
        # Submit login
        self.logger.info("Submitting login...")
        login_dialog.type_keys("{ENTER}")
        
        self.logger.info("Login attempt complete")

    def login_to_snelstart(self, window: UIAWrapper):
        """Main login function that handles the complete login process."""
        try:
            try:
                login_dialog = self.get_login_dialog(window)
            except RuntimeError:
                self.logger.info("Login dialog not found — assuming already logged in.")
                return True

            # Wait briefly to see if the dialog disappears automatically
            self.logger.info("Login dialog found — waiting briefly to check for auto-login...")
            try:
                # Try accessing something on the dialog after waiting
                time.sleep(2)
                if not login_dialog.is_visible():
                    self.logger.info("Login dialog is no longer visible — assuming auto-login succeeded.")
                    return True
            except Exception:
                self.logger.info("Login dialog no longer exists — assuming auto-login succeeded.")
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