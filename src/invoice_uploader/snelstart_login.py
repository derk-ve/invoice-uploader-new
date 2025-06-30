import os
import time
import logging
from dotenv import load_dotenv
from pywinauto.controls.uiawrapper import UIAWrapper

# Logging setup
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def get_login_dialog(window: UIAWrapper):
    """Search for and return the login dialog inside the main window."""
    logger.info("Searching for login dialog inside main window...")
    for child in window.descendants():
        try:
            if child.friendly_class_name() == "Dialog" and "Inloggen" in child.window_text():
                logger.info(f"Found login dialog: '{child.window_text()}'")
                return child
        except Exception as e:
            logger.debug(f"Skipping element due to error: {e}")
    raise RuntimeError("Login dialog not found inside main window")

def perform_login(login_dialog: UIAWrapper, username: str, password: str):
    """Perform the login sequence in the Snelstart application."""
    logger.info("Attempting to perform login...")
    
    # Focus the login dialog
    login_dialog.set_focus()
    time.sleep(2)
    
    # Enter username
    logger.info("Entering username...")
    login_dialog.type_keys(username, with_spaces=True)
    time.sleep(2)
    
    # Navigate to password field
    logger.info("Navigating to password field...")
    login_dialog.type_keys("{TAB}")
    time.sleep(2)
    login_dialog.type_keys("{ENTER}")
    time.sleep(2)
    
    # Click "Doorgaan met wachtwoord"
    logger.info("Selecting password login option...")
    login_dialog.type_keys("{TAB}{TAB}{ENTER}")
    time.sleep(2)
    
    # Enter password
    logger.info("Entering password...")
    login_dialog.type_keys(password, with_spaces=True)
    time.sleep(2)
    
    # Submit login
    logger.info("Submitting login...")
    login_dialog.type_keys("{ENTER}")
    
    logger.info("Login attempt complete")

def login_to_snelstart(window: UIAWrapper):
    """Main login function that handles the complete login process."""
    try:
        username = os.getenv("SNELSTART_EMAIL")
        password = os.getenv("SNELSTART_PASSWORD")

        if not username or not password:
            raise ValueError("Snelstart credentials not found in environment variables")

        try:
            login_dialog = get_login_dialog(window)
        except RuntimeError:
            logger.info("Login dialog not found — assuming already logged in.")
            return True

        # Wait briefly to see if the dialog disappears automatically
        logger.info("Login dialog found — waiting briefly to check for auto-login...")
        try:
        # Try accessing something on the dialog after waiting
            time.sleep(2)
            if not login_dialog.is_visible():
                logger.info("Login dialog is no longer visible — assuming auto-login succeeded.")
                return True
        except Exception:
            logger.info("Login dialog no longer exists — assuming auto-login succeeded.")
            return True

        # Still exists? Then perform manual login
        perform_login(login_dialog, username, password)
        return True

    except Exception as e:
        logger.error(f"Login failed: {e}")
        return False
