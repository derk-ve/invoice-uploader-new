import time
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto import Desktop
from ...utils.logging_setup import get_logger
from ...utils.config import get_timing_config, get_ui_elements

class InvoiceReaderAutomation:
    """Handles SnelStart invoice reading automation."""
    
    def __init__(self):
        """Initialize the invoice reader automation."""
        self.logger = get_logger(self.__class__.__name__)
        self.timing = get_timing_config()
        self.ui_elements = get_ui_elements()
    
    def click_afschriften_inlezen(self, window: UIAWrapper):
        """
        Clicks the 'Afschriften Inlezen' button inside the Boekhouden toolbar.

        Args:
            window (UIAWrapper): The administratie window.

        Raises:
            RuntimeError: If the button could not be found or clicked.
        """
        try:
            self.logger.info("Looking for 'Afschriften Inlezen' button...")

            for ctrl in window.descendants():
                if ctrl.friendly_class_name() == "Button" and ctrl.window_text() == self.ui_elements['invoice_button_text']:
                    self.logger.info("Found 'Afschriften Inlezen' button. Clicking...")
                    ctrl.set_focus()
                    ctrl.click_input()
                    time.sleep(self.timing['button_wait_time'])
                    return

            raise RuntimeError("'Afschriften Inlezen' button not found")

        except Exception as e:
            self.logger.error(f"Failed to click 'Afschriften Inlezen': {e}")
            raise RuntimeError("Could not interact with 'Afschriften Inlezen'")


# Backwards compatibility function for existing code
def click_afschriften_inlezen(window: UIAWrapper):
    """Backwards compatibility function."""
    invoice_reader_automation = InvoiceReaderAutomation()
    return invoice_reader_automation.click_afschriften_inlezen(window)