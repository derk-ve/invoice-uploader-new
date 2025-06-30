import os
import time
from pywinauto.application import Application
from pywinauto import Desktop
from ...utils.logging_setup import get_logger
from ...utils.config import get_snelstart_path as get_snelstart_path_config, get_timing_config, get_timeouts
from ...utils.wait_utils import wait_for_window_by_title, wait_for_window_ready

class LaunchAutomation:
    """Handles SnelStart application launch and window detection."""
    
    def __init__(self):
        """Initialize the launch automation."""
        self.logger = get_logger(self.__class__.__name__)
        self.app_path = self.get_snelstart_path()
        self.timing = get_timing_config()
        self.timeouts = get_timeouts()
    
    def get_snelstart_path(self):
        """Get the path to the SnelStart application from environment variables."""
        return get_snelstart_path_config()

    def start_snelstart_application(self, app_path: str = None):
        """
        Start the SnelStart application if it's not running.
        
        Args:
            app_path: Path to the SnelStart application (optional, uses instance path if not provided)
            
        Returns:
            Application instance if started successfully, None otherwise
        """
        if app_path is None:
            app_path = self.app_path
            
        try:
            # Start the application
            self.logger.info("Activating SnelStart Application...")
            app = Application(backend='uia').start(app_path)
            
            # Wait for the application window to appear instead of fixed sleep
            self.logger.info("Waiting for SnelStart window to appear...")
            main_window = wait_for_window_by_title("SnelStart", 
                                                   self.timeouts['window_timeout'])
            
            self.logger.info(f"SnelStart application started successfully with window: '{main_window.window_text()}'")
            return app
            
        except Exception as e:
            self.logger.error(f"Error starting SnelStart: {str(e)}")
            return None

    def get_main_window(self, timeout: int = None, interval: int = None):
        """
        Wait for and return the main SnelStart window.
        
        Args:
            timeout: Maximum time to wait in seconds (optional, uses config default)
            interval: Check interval in seconds (optional, uses config default)
            
        Returns:
            Main window if found, raises RuntimeError otherwise
        """
        if timeout is None:
            timeout = self.timeouts['window_timeout']
        if interval is None:
            interval = self.timeouts['retry_interval']
        
        try:
            self.logger.info(f"Waiting for SnelStart window (timeout: {timeout}s)...")
            main_window = wait_for_window_by_title("SnelStart", timeout)
            
            # Ensure the window is fully ready for interaction
            ready_window = wait_for_window_ready(main_window, timeout=10, 
                                                window_name="SnelStart main window")
            
            self.logger.info(f"SnelStart window is ready: '{ready_window.window_text()}'")
            return ready_window
            
        except Exception as e:
            self.logger.error(f"Failed to get SnelStart main window: {e}")
            raise RuntimeError(f"SnelStart window not found or not ready: {e}")


# Backwards compatibility functions for existing code
def get_snelstart_path():
    """Backwards compatibility function."""
    launch_automation = LaunchAutomation()
    return launch_automation.get_snelstart_path()

def start_snelstart_application(app_path: str):
    """Backwards compatibility function."""
    launch_automation = LaunchAutomation()
    return launch_automation.start_snelstart_application(app_path)

def get_main_window(timeout: int = 30, interval: int = 5):
    """Backwards compatibility function."""
    launch_automation = LaunchAutomation()
    return launch_automation.get_main_window(timeout, interval)