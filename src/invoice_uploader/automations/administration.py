from pywinauto import Desktop

import time
from pywinauto.controls.uiawrapper import UIAWrapper
from ...utils.logging_setup import get_logger
from ...utils.config import get_timing_config, get_ui_elements

class AdministrationAutomation:
    """Handles SnelStart administration window automation."""
    
    def __init__(self):
        """Initialize the administration automation."""
        self.logger = get_logger(self.__class__.__name__)
        self.timing = get_timing_config()
        self.ui_elements = get_ui_elements()
    
    def get_administratie_window(self, window: UIAWrapper):
        """
        Double-clicks 'Row 1' to open the administratie window.

        Args:
            window (UIAWrapper): The main administratie view window.

        Returns:
            None

        Raises:
            RuntimeError: If the row could not be found or clicked.
        """
        try:
            for ctrl in window.descendants():
                if ctrl.friendly_class_name() == "Custom" and ctrl.window_text() == self.ui_elements['admin_row_text']:
                    ctrl.set_focus()
                    ctrl.double_click_input()
                    self.logger.info("Double-clicked row 1 to open administratie.")
                    time.sleep(self.timing['admin_open_wait_time'])
                    return
            raise RuntimeError("Row 1 not found in administratie view")
        except Exception as e:
            self.logger.error(f"Failed to open administratie: {e}")
            raise RuntimeError("Could not open administratie window")


# Backwards compatibility function for existing code
def get_administratie_window(window: UIAWrapper):
    """Backwards compatibility function."""
    admin_automation = AdministrationAutomation()
    return admin_automation.get_administratie_window(window)