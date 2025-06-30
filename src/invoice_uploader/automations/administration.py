import time
from pywinauto.controls.uiawrapper import UIAWrapper
from ...utils.logging_setup import LoggingSetup
from ...utils.config import Config
from ...utils.wait_utils import wait_with_timeout, WaitTimeoutError

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
            # Direct search through descendants (like working code)
            for ctrl in window.descendants():
                try:
                    if (ctrl.friendly_class_name() == "Custom" and 
                        ctrl.window_text() == self.ui_elements['admin_row_text']):
                        ctrl.set_focus()
                        ctrl.double_click_input()
                        self.logger.info(f"Successfully double-clicked '{self.ui_elements['admin_row_text']}' to open administratie")
                        
                        # Post-click stabilization wait
                        def check_ready():
                            return True  # Simple readiness check
                        
                        try:
                            wait_with_timeout(check_ready, timeout=3, interval=1, 
                                            description="administration window stabilization", 
                                            provide_feedback=False)
                            
                        except WaitTimeoutError:
                            self.logger.warning("Timeout waiting for administration to stabilize")
                        
                        return
                        
                except Exception as e:
                    self.logger.debug(f"Skipping control due to error: {e}")
                    continue
            
            # If we get here, row was not found
            raise RuntimeError(f"Row '{self.ui_elements['admin_row_text']}' not found in administratie view")
            
        except Exception as e:
            self.logger.error(f"Failed to open administratie: {e}")
            raise RuntimeError(f"Could not open administratie window: {e}")


# Backwards compatibility function for existing code
def get_administratie_window(window: UIAWrapper):
    """Backwards compatibility function."""
    admin_automation = AdministrationAutomation()
    return admin_automation.get_administratie_window(window)