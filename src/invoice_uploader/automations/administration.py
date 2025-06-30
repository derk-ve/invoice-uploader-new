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
        
        # Get timing configuration from centralized config
        timing = Config.get_timing_config('administration')
        self.WORKSPACE_READY_TIMEOUT = timing.get('workspace_ready_timeout', 3)
    
    def _click_row_one(self, window: UIAWrapper):
        """
        Pure action function: finds and double-clicks 'Row 1' without any waiting.

        Args:
            window (UIAWrapper): The main administratie view window.

        Returns:
            None

        Raises:
            RuntimeError: If the row could not be found or clicked.
        """
        try:
            # Direct search through descendants
            for ctrl in window.descendants():
                try:
                    if (ctrl.friendly_class_name() == "Custom" and 
                        ctrl.window_text() == self.ui_elements['admin_row_text']):
                        ctrl.set_focus()
                        ctrl.double_click_input()
                        self.logger.info(f"Successfully double-clicked '{self.ui_elements['admin_row_text']}'")
                        return
                        
                except Exception as e:
                    self.logger.debug(f"Skipping control due to error: {e}")
                    continue
            
            # If we get here, row was not found
            raise RuntimeError(f"Row '{self.ui_elements['admin_row_text']}' not found in administratie view")
            
        except Exception as e:
            self.logger.error(f"Failed to click row: {e}")
            raise RuntimeError(f"Could not click row: {e}")
    
    def _wait_for_workspace_ready(self, window: UIAWrapper, timeout=None):
        """
        Pure wait function: waits for administration workspace to be ready.

        Args:
            window (UIAWrapper): The main window to check.
            timeout (int): Maximum time to wait in seconds (uses config default if None).

        Returns:
            True if workspace is ready

        Raises:
            WaitTimeoutError: If workspace not ready within timeout.
        """
        if timeout is None:
            timeout = self.WORKSPACE_READY_TIMEOUT
        def check_ready():
            # Check if administration workspace has loaded by looking for workspace elements
            try:
                for control in window.descendants():
                    if (control.window_text() == "Dashboard" or 
                        control.window_text() == "Afschriften Inlezen"):
                        return True
                return False
            except:
                return False
        
        try:
            wait_with_timeout(check_ready, timeout=timeout, interval=1, 
                            description="administration workspace ready", 
                            provide_feedback=False)
            return True
        except WaitTimeoutError:
            self.logger.warning("Timeout waiting for administration workspace to be ready")
            raise
    
    def get_administratie_window(self, window: UIAWrapper):
        """
        Orchestration function: opens administratie by clicking Row 1 and waiting for workspace.

        Args:
            window (UIAWrapper): The main administratie view window.

        Returns:
            None

        Raises:
            RuntimeError: If the operation fails.
        """
        try:
            # Step 1: Click Row 1 (pure action)
            self._click_row_one(window)
            
            # Step 2: Wait for workspace to load (pure wait)
            self._wait_for_workspace_ready(window)
            
            self.logger.info("Successfully opened administratie workspace")
            
        except Exception as e:
            self.logger.error(f"Failed to open administratie: {e}")
            raise RuntimeError(f"Could not open administratie window: {e}")


# Backwards compatibility function for existing code
def get_administratie_window(window: UIAWrapper):
    """Backwards compatibility function."""
    admin_automation = AdministrationAutomation()
    return admin_automation.get_administratie_window(window)