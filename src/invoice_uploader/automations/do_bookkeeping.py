import time
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto import Desktop
from ...utils.logging_setup import LoggingSetup
from ...utils.config import Config
from ...utils.wait_utils import wait_for_element, safe_click

class DoBookkeepingAutomation:
    """Handles SnelStart bookkeeping automation."""
    
    def __init__(self):
        """Initialize the bookkeeping automation."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.ui_elements = Config.get_ui_elements()
    
    def start_bookkeeping_process(self, window: UIAWrapper):
        """
        Starts the bookkeeping process by clicking the 'Afschriften Inlezen' button inside the Boekhouden toolbar.

        Args:
            window (UIAWrapper): The bookkeeping window.

        Raises:
            RuntimeError: If the button could not be found or clicked.
        """
        try:
            def find_invoice_button(parent):
                for ctrl in parent.descendants():
                    try:
                        if (ctrl.friendly_class_name() == "Button" and 
                            ctrl.window_text() == self.ui_elements['invoice_button_text']):
                            return ctrl
                    except:
                        continue
                return None
            
            self.logger.info(f"Looking for '{self.ui_elements['invoice_button_text']}' button...")
            
            # Wait for the button to be available
            invoice_button = wait_for_element(window, find_invoice_button,
                                            f"'{self.ui_elements['invoice_button_text']}' button")
            
            # Use safe_click which includes clickability verification
            safe_click(invoice_button, f"'{self.ui_elements['invoice_button_text']}' button")
            
            self.logger.info(f"Successfully clicked '{self.ui_elements['invoice_button_text']}' button")

        except Exception as e:
            self.logger.error(f"Failed to click '{self.ui_elements['invoice_button_text']}': {e}")
            raise RuntimeError(f"Could not interact with '{self.ui_elements['invoice_button_text']}': {e}")


# Backwards compatibility function for existing code
def start_bookkeeping_process(window: UIAWrapper):
    """Backwards compatibility function."""
    bookkeeping_automation = DoBookkeepingAutomation()
    return bookkeeping_automation.start_bookkeeping_process(window)