import time
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto import Desktop
from ...utils.logging_setup import LoggingSetup
from ...utils.config import Config
from ...utils.wait_utils import wait_for_element
from ...utils.ui_utils import UIUtils

class DoBookkeepingAutomation:
    """Handles SnelStart bookkeeping automation."""
    
    def __init__(self):
        """Initialize the bookkeeping automation."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.ui_elements = Config.get_ui_elements()
        self.ui_utils = UIUtils()
    
    def find_invoice_button(self, window: UIAWrapper):
        """
        Find the 'Afschriften Inlezen' button in the given window.

        Args:
            window (UIAWrapper): The window to search in.

        Returns:
            UIAWrapper: The button element if found, None otherwise.
        """
        try:
            self.logger.debug(f"Searching for '{self.ui_elements['invoice_button_text']}' button...")
            
            # Use the unified utility function
            button = self.ui_utils.get_descendant_by_criteria(
                window, 
                class_name="Button", 
                text=self.ui_elements['invoice_button_text']
            )
            
            if button:
                self.logger.debug(f"Found '{self.ui_elements['invoice_button_text']}' button")
            else:
                self.logger.debug(f"'{self.ui_elements['invoice_button_text']}' button not found")
                
            return button

        except Exception as e:
            self.logger.debug(f"Error searching for button: {e}")
            return None
    
    def click_invoice_button(self, window: UIAWrapper):
        """
        Find and click the 'Afschriften Inlezen' button.

        Args:
            window (UIAWrapper): The window containing the button.

        Raises:
            RuntimeError: If the button could not be found or clicked.
        """
        try:
            self.logger.info(f"Looking for '{self.ui_elements['invoice_button_text']}' button...")
            
            # Wait for the button to be available using find_invoice_button
            invoice_button = wait_for_element(window, self.find_invoice_button,
                                            f"'{self.ui_elements['invoice_button_text']}' button")
            
            # Use safe_click which includes clickability verification
            self.ui_utils.safe_click(invoice_button, f"'{self.ui_elements['invoice_button_text']}' button")
            
            self.logger.info(f"Successfully clicked '{self.ui_elements['invoice_button_text']}' button")

        except Exception as e:
            self.logger.error(f"Failed to click '{self.ui_elements['invoice_button_text']}': {e}")
            raise RuntimeError(f"Could not interact with '{self.ui_elements['invoice_button_text']}': {e}")

