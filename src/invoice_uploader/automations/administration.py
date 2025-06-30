from pywinauto import Desktop

import time
from pywinauto.controls.uiawrapper import UIAWrapper
from ...utils.logging_setup import LoggingSetup
from ...utils.config import Config
from ...utils.wait_utils import wait_for_element, safe_click

class AdministrationAutomation:
    """Handles SnelStart administration window automation."""
    
    def __init__(self):
        """Initialize the administration automation."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.ui_elements = Config.get_ui_elements()
    
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
            def find_admin_row(parent):
                for ctrl in parent.descendants():
                    try:
                        if (ctrl.friendly_class_name() == "Custom" and 
                            ctrl.window_text() == self.ui_elements['admin_row_text']):
                            return ctrl
                    except:
                        continue
                return None
            
            # Wait for the admin row to be available
            admin_row = wait_for_element(window, find_admin_row, 
                                       f"admin row '{self.ui_elements['admin_row_text']}'")
            
            # Perform the double-click
            admin_row.set_focus()
            admin_row.double_click_input()
            self.logger.info(f"Successfully double-clicked '{self.ui_elements['admin_row_text']}' to open administratie")
            
        except Exception as e:
            self.logger.error(f"Failed to open administratie: {e}")
            raise RuntimeError(f"Could not open administratie window: {e}")


# Backwards compatibility function for existing code
def get_administratie_window(window: UIAWrapper):
    """Backwards compatibility function."""
    admin_automation = AdministrationAutomation()
    return admin_automation.get_administratie_window(window)