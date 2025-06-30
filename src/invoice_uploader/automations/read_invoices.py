import time
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto import Desktop
from ...utils.logging_setup import get_logger
from ...utils.config import get_timing_config, get_ui_elements, get_wait_timeouts
from ...utils.wait_utils import wait_for_element, wait_for_clickable, safe_click

class InvoiceReaderAutomation:
    """Handles SnelStart invoice reading automation."""
    
    def __init__(self):
        """Initialize the invoice reader automation."""
        self.logger = get_logger(self.__class__.__name__)
        self.timing = get_timing_config()
        self.ui_elements = get_ui_elements()
        self.wait_timeouts = get_wait_timeouts()
    
    def click_afschriften_inlezen(self, window: UIAWrapper):
        """
        Clicks the 'Afschriften Inlezen' button inside the Boekhouden toolbar.

        Args:
            window (UIAWrapper): The administratie window.

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
                                            self.wait_timeouts['element_timeout'],
                                            self.wait_timeouts['wait_interval'],
                                            f"'{self.ui_elements['invoice_button_text']}' button")
            
            # Use safe_click which includes clickability verification
            safe_click(invoice_button, 
                      self.wait_timeouts['clickable_timeout'],
                      f"'{self.ui_elements['invoice_button_text']}' button")
            
            self.logger.info(f"Successfully clicked '{self.ui_elements['invoice_button_text']}' button")

        except Exception as e:
            self.logger.error(f"Failed to click '{self.ui_elements['invoice_button_text']}': {e}")
            raise RuntimeError(f"Could not interact with '{self.ui_elements['invoice_button_text']}': {e}")


# Backwards compatibility function for existing code
def click_afschriften_inlezen(window: UIAWrapper):
    """Backwards compatibility function."""
    invoice_reader_automation = InvoiceReaderAutomation()
    return invoice_reader_automation.click_afschriften_inlezen(window)