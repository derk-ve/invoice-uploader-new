import os
import time
from pywinauto.application import Application
from pywinauto import Desktop
from ...utils.logging_setup import LoggingSetup
from ...utils.config import Config
from ...utils.wait_utils import wait_with_timeout


class LaunchAutomation:
    """Handles SnelStart application launch and window detection."""
    
    def __init__(self):
        """Initialize the launch automation."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.app_path = self.get_snelstart_path()
        
        # Get timing configuration from centralized config
        timing = Config.get_timing_config('launch')
        self.DEFAULT_TIMEOUT = timing.get('default_timeout', 30)
        self.DEFAULT_INTERVAL = timing.get('default_interval', 5)
    
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

    def get_main_window(self):
        """
        Pure action function: searches for SnelStart window once without waiting.
        
        Returns:
            Main window if found, None otherwise
        """
        for window in Desktop(backend="uia").windows():
            try:
                window_text = window.window_text()
                # Substring match for any SnelStart window
                if "SnelStart" in window_text:
                    self.logger.debug(f"Found SnelStart window: '{window_text}'")
                    return window
            except Exception as e:
                self.logger.debug(f"Skipping window due to error: {e}")
                continue
        return None
    
    def wait_for_main_window(self, timeout=None, interval=None):
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT
        if interval is None:
            interval = self.DEFAULT_INTERVAL

        def main_window_exists():
            window = self.get_main_window()
            return window

        return wait_with_timeout(
            main_window_exists,
            timeout=timeout,
            interval=interval,
            description="main window to appear",
            provide_feedback=True  # or False if you want no logging
        )
    



# Backwards compatibility functions for existing code
def get_snelstart_path():
    """Backwards compatibility function."""
    launch_automation = LaunchAutomation()
    return launch_automation.get_snelstart_path()

def start_snelstart_application(app_path: str):
    """Backwards compatibility function."""
    launch_automation = LaunchAutomation()
    return launch_automation.start_snelstart_application(app_path)

def get_main_window():
    """Backwards compatibility function."""
    launch_automation = LaunchAutomation()
    return launch_automation.get_main_window()

