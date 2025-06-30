import os
import time
from pywinauto.application import Application
from pywinauto import Desktop
from ...utils.logging_setup import LoggingSetup
from ...utils.config import Config
from ...utils.wait_utils import simple_retry

class LaunchAutomation:
    """Handles SnelStart application launch and window detection."""
    
    def __init__(self):
        """Initialize the launch automation."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.app_path = self.get_snelstart_path()
    
    def get_snelstart_path(self):
        """Get the path to the SnelStart application from environment variables."""
        return Config.get_snelstart_path()

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
            
            self.logger.info(f"SnelStart application started successfully")
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
        try:
            self.logger.info("Waiting for SnelStart window...")
            windows = []
            # Use original proven window detection logic with retry
            def find_snelstart_window():
                for window in Desktop(backend="uia").windows():
                    try:
                        if "SnelStart 12" in window.window_text():
                            windows.append(window)
                            self.logger.info(f"Found SnelStart window: '{window.window_text()}'")
                    except Exception as e:
                        self.logger.debug(f"Skipping window due to error: {e}")
                        continue
                raise RuntimeError("SnelStart window not found")
            
            self.logger.debug(f"Windows found: {windows}")
            main_window = simple_retry(find_snelstart_window, "find SnelStart window")
            self.logger.info(f"SnelStart window found: '{main_window.window_text()}'")
            return main_window
            
        except Exception as e:
            self.logger.error(f"Failed to get SnelStart main window: {e}")
            raise RuntimeError(f"SnelStart window not found: {e}")


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