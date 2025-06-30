import time
from pywinauto.controls.uiawrapper import UIAWrapper
from ..utils.ui_utils import print_control_tree, find_control_by_text, find_control_by_class
from ..utils.logging_setup import get_logger
from .automations.launch_snelstart import LaunchAutomation
from .automations.login import LoginAutomation
from .automations.administration import AdministrationAutomation
from .automations.read_invoices import InvoiceReaderAutomation

class SnelstartAutomation:
    def __init__(self):
        """
        Initialize the Snelstart automation.
        """
        # Initialize logging
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize automation components
        self.launch_automation = LaunchAutomation()
        self.login_automation = LoginAutomation()
        self.admin_automation = AdministrationAutomation()
        self.invoice_reader_automation = InvoiceReaderAutomation()
        
        # Application state
        self.app_path = self.launch_automation.app_path
        self.app = None
        self.main_window = None
        self.admin_window = None
        
        self.logger.info(f"Snelstart automation initialized. Application path: {self.app_path}")
    
    def start(self):
        """
        Start the Snelstart application if it's not running.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Start the application
            self.app = self.launch_automation.start_snelstart_application()
            if not self.app:
                return False
            
            # Wait for the main window to appear
            self.main_window = self.launch_automation.get_main_window()
            
            self.logger.info(f"Activated Snelstart application")
            self.logger.info(f"Window title: {self.main_window.window_text()}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error activating Snelstart: {str(e)}")
            return False
    
    
    def login(self):
        """
        Main login function that handles the complete login process.
        
        Returns:
            True if login was successful, False otherwise
        """
        try:
            if not self.main_window:
                self.logger.error("No main window available for login")
                return False
                
            return self.login_automation.login_to_snelstart(self.main_window)
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
        
    def open_administratie(self):
        try:

            self.admin_automation.get_administratie_window(self.main_window)
            admin_window = self.main_window  # The function doesn't return the window, it opens it
            self.admin_window = admin_window
            self.logger.info("Successfully opened Administratie section")

            return True
        
        except Exception as e:
            self.logger.error(f"Could not open administratie: {e}")
            return False
        

    def load_in_afschriften(self):
        """
        Load in afschriften (bank statements) in the Snelstart application.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.admin_window:
                self.logger.error("No admin window available for loading afschriften")
                return False
            
            # Click on the "Afschriften Inlezen" button
            self.invoice_reader_automation.click_afschriften_inlezen(self.admin_window)
            
            self.logger.info("Successfully loaded afschriften")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to load afschriften: {e}")
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
                    self.logger.error("Failed to start Snelstart application")
                    return False
            
            # This is where you would implement the specific steps to upload a file
            # The exact steps will depend on the Snelstart application interface
            
            # Example steps (you'll need to adjust these based on the actual Snelstart interface):
            # 1. Click on the "Documents" or "Files" menu
            # 2. Click on "Upload" or "Import"
            # 3. Enter the file path in the file dialog
            # 4. Click "OK" or "Upload"
            
            # For now, we'll just log the file path
            self.logger.info(f"Would upload file: {file_path}")
            
            # Simulate some work
            time.sleep(2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error uploading file {file_path}: {str(e)}")
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
            self.logger.info("Closed Snelstart application")
            return True
        except Exception as e:
            self.logger.error(f"Error closing Snelstart: {str(e)}")
            return False 