import time
from pywinauto.controls.uiawrapper import UIAWrapper
from ...utils.logging_setup import LoggingSetup
from ...utils.config import Config
from ...utils.wait_utils import wait_with_timeout, WaitTimeoutError

class NavigateToBookkeepingAutomation:
    """Handles navigation to SnelStart bookkeeping interface."""
    
    def __init__(self):
        """Initialize the navigate to bookkeeping automation."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.ui_elements = Config.get_ui_elements()
        
        # Get timing configuration from centralized config
        timing = Config.get_timing_config('administration')
        self.WORKSPACE_READY_TIMEOUT = timing.get('workspace_ready_timeout', 30)
        self.BOEKHOUDEN_TAB_TIMEOUT = timing.get('boekhouden_tab_timeout', 10)
        self.BOEKHOUDEN_READY_TIMEOUT = timing.get('boekhouden_ready_timeout', 15)
    
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
            wait_with_timeout(check_ready, timeout=timeout, interval=3, 
                            description="administration workspace ready", 
                            provide_feedback=True)
            time.sleep(5)
            return True
        except WaitTimeoutError:
            self.logger.warning("Timeout waiting for administration workspace to be ready")
            raise
    
    def navigate_to_administration(self, window: UIAWrapper):
        """
        Orchestration function: navigates to administration by clicking Row 1 and waiting for workspace.

        Args:
            window (UIAWrapper): The main window.

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

    def _click_boekhouden_tab(self, window: UIAWrapper):
        """
        Pure action function: finds and clicks the 'BOEKHOUDEN' tab in the ribbon.

        Args:
            window (UIAWrapper): The main window containing the ribbon.

        Returns:
            None

        Raises:
            RuntimeError: If the BOEKHOUDEN tab could not be found or clicked.
        """
        try:
            # Search for BOEKHOUDEN tab in the ribbon tabs
            for ctrl in window.descendants():
                try:
                    if (ctrl.friendly_class_name() == "TabItem" and 
                        ctrl.window_text() == self.ui_elements['boekhouden_tab_text']):
                        ctrl.set_focus()
                        ctrl.click_input()
                        self.logger.info(f"Successfully clicked '{self.ui_elements['boekhouden_tab_text']}' tab")
                        return
                        
                except Exception as e:
                    self.logger.debug(f"Skipping control due to error: {e}")
                    continue
            
            # If we get here, tab was not found
            raise RuntimeError(f"Tab '{self.ui_elements['boekhouden_tab_text']}' not found in ribbon")
            
        except Exception as e:
            self.logger.error(f"Failed to click BOEKHOUDEN tab: {e}")
            raise RuntimeError(f"Could not click BOEKHOUDEN tab: {e}")

    def _wait_for_boekhouden_ready(self, window: UIAWrapper, timeout=None):
        """
        Pure wait function: waits for bookkeeping interface to be ready.

        Args:
            window (UIAWrapper): The main window to check.
            timeout (int): Maximum time to wait in seconds (uses config default if None).

        Returns:
            True if bookkeeping interface is ready

        Raises:
            WaitTimeoutError: If interface not ready within timeout.
        """
        if timeout is None:
            timeout = self.BOEKHOUDEN_READY_TIMEOUT
            
        def check_ready():
            # Check if bookkeeping interface has loaded by looking for specific elements
            try:
                for control in window.descendants():
                    # Look for bookkeeping-specific elements
                    if (control.window_text() == "Afschriften Inlezen" or 
                        control.window_text() == "Bankieren" or
                        control.window_text() == "Boekhouden"):
                        return True
                return False
            except:
                return False
        
        try:
            wait_with_timeout(check_ready, timeout=timeout, interval=2, 
                            description="bookkeeping interface ready", 
                            provide_feedback=True)
            time.sleep(5)
            return True
        except WaitTimeoutError:
            self.logger.warning("Timeout waiting for bookkeeping interface to be ready")
            raise

    def navigate_to_bookkeeping_tab(self, window: UIAWrapper):
        """
        Orchestration function: navigates to bookkeeping section by clicking BOEKHOUDEN tab.

        Args:
            window (UIAWrapper): The main window.

        Returns:
            None

        Raises:
            RuntimeError: If the navigation fails.
        """
        try:
            # Step 1: Click BOEKHOUDEN tab (pure action)
            self._click_boekhouden_tab(window)
            
            # Step 2: Wait for bookkeeping interface to load (pure wait)
            self._wait_for_boekhouden_ready(window)
            
            self.logger.info("Successfully navigated to bookkeeping section")
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to bookkeeping: {e}")
            raise RuntimeError(f"Could not navigate to bookkeeping section: {e}")


# Backwards compatibility functions for existing code
def navigate_to_administration(window: UIAWrapper):
    """Backwards compatibility function."""
    admin_automation = NavigateToBookkeepingAutomation()
    return admin_automation.navigate_to_administration(window)

def navigate_to_bookkeeping_tab(window: UIAWrapper):
    """Backwards compatibility function for bookkeeping navigation."""
    admin_automation = NavigateToBookkeepingAutomation()
    return admin_automation.navigate_to_bookkeeping_tab(window)