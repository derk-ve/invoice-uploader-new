import os
import time
import logging
from pywinauto.application import Application
from dotenv import load_dotenv
from pywinauto import Desktop
from pywinauto.controls.uiawrapper import UIAWrapper
from utils.ui_utils import print_control_tree, find_control_by_text, find_control_by_class
from snelstart_login import get_login_dialog, perform_login, login_to_snelstart
from snelstart_administratie import get_administratie_window
from snelstart_afschriften_inlezen import click_afschriften_inlezen


# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SnelstartAutomation:
    def __init__(self):
        """
        Initialize the Snelstart automation.
        
        Args:
            app_path: Path to the Snelstart application
        """
        self.app_path = os.getenv('SNELSTART_PATH', r'C:\Program Files\Snelstart\Snelstart.exe')
        self.app = None
        self.main_window = None
        self.admin_window = None
        
        logger.info(f"Snelstart automation initialized. Application path: {self.app_path}")
    
    def start(self):
        """
        Start the Snelstart application if it's not running.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Start the application
            logger.info("Activating SnelStart Application...")
            self.app = Application(backend='uia').start(self.app_path)
            time.sleep(5)  # Give it initial time to spawn UI
            
            # Wait for the main window to appear
            self.main_window = self._get_main_window()
            
            logger.info(f"Activated Snelstart application")
            logger.info(f"Window title: {self.main_window.window_text()}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error activating Snelstart: {str(e)}")
            return False
    
    def _get_main_window(self, timeout: int = 30, interval: int = 5):
        """Wait for and return the main Snelstart window."""
        elapsed = 0
        while elapsed < timeout:

            logger.info(f"Waiting for SnelStart window... ({elapsed}/{timeout}s)")

            for window in Desktop(backend="uia").windows():

                if "SnelStart" in window.window_text():
                    logger.info(f"Found SnelStart window: '{window.window_text()}'")
                    return window
                
            time.sleep(interval)
            elapsed += interval

        raise RuntimeError("SnelStart window not found after timeout")
    
    def login(self):
        """
        Main login function that handles the complete login process.
        
        Returns:
            True if login was successful, False otherwise
        """
        try:
            if not self.main_window:
                logger.error("No main window available for login")
                return False
                
            return login_to_snelstart(self.main_window)
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
        
    def open_administratie(self):
        try:

            admin_window = get_administratie_window(self.main_window)
            self.admin_window = admin_window
            logger.info("Successfully opened Administratie section")

            return True
        
        except Exception as e:
            logger.error(f"Could not open administratie: {e}")
            return False
        

    def load_in_afschriften(self):
        """
        Load in afschriften (bank statements) in the Snelstart application.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.admin_window:
                logger.error("No admin window available for loading afschriften")
                return False
            
            # Click on the "Afschriften Inlezen" button
            click_afschriften_inlezen(self.admin_window)
            
            logger.info("Successfully loaded afschriften")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load afschriften: {e}")
            return False

    def print_control_tree(self, control: UIAWrapper = None, level: int = 0):
        """Print the control tree of a window for debugging purposes."""

        if control is None:
            control = self.main_window

        print_control_tree(control, level)
    
    def upload_file(self, file_path: str):
        """
        Upload a file to Snelstart.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            True if uploaded successfully, False otherwise
        """
        try:
            # Make sure we're connected to the application
            if not self.app or not self.main_window:
                if not self.start():
                    logger.error("Failed to start Snelstart application")
                    return False
            
            # This is where you would implement the specific steps to upload a file
            # The exact steps will depend on the Snelstart application interface
            
            # Example steps (you'll need to adjust these based on the actual Snelstart interface):
            # 1. Click on the "Documents" or "Files" menu
            # 2. Click on "Upload" or "Import"
            # 3. Enter the file path in the file dialog
            # 4. Click "OK" or "Upload"
            
            # For now, we'll just log the file path
            logger.info(f"Would upload file: {file_path}")
            
            # Simulate some work
            time.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {str(e)}")
            return False
    
    def close(self):
        """
        Close the Snelstart application.
        
        Returns:
            True if closed successfully, False otherwise
        """
        try:
            if self.main_window:
                self.main_window.close()
            elif self.app:
                self.app.kill()
            logger.info("Closed Snelstart application")
            return True
        except Exception as e:
            logger.error(f"Error closing Snelstart: {str(e)}")
            return False 