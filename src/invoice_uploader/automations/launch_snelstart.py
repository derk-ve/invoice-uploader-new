import os
import time
from pywinauto.application import Application
from pywinauto import Desktop
from ...utils.logging_setup import get_logger
from ...utils.config import get_snelstart_path as get_snelstart_path_config, get_timing_config

class LaunchAutomation:
    """Handles SnelStart application launch and window detection."""
    
    def __init__(self):
        """Initialize the launch automation."""
        self.logger = get_logger(self.__class__.__name__)
        self.app_path = self.get_snelstart_path()
        self.timing = get_timing_config()
    
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
            time.sleep(5)  # Give it initial time to spawn UI
            
            self.logger.info("SnelStart application started successfully")
            return app
            
        except Exception as e:
            self.logger.error(f"Error starting SnelStart: {str(e)}")
            return None

    def get_main_window(self, timeout: int = 30, interval: int = 5):
        """
        Wait for and return the main SnelStart window.
        
        Args:
            timeout: Maximum time to wait in seconds
            interval: Check interval in seconds
            
        Returns:
            Main window if found, raises RuntimeError otherwise
        """
        elapsed = 0
        while elapsed < timeout:
            self.logger.info(f"Waiting for SnelStart window... ({elapsed}/{timeout}s)")

            for window in Desktop(backend="uia").windows():
                if "SnelStart" in window.window_text():
                    self.logger.info(f"Found SnelStart window: '{window.window_text()}'")
                    return window
                
            time.sleep(interval)
            elapsed += interval

        raise RuntimeError("SnelStart window not found after timeout")


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