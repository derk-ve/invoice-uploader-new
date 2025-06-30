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
        self.window_titles = Config.get_window_titles()
    
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
        Wait for and return the main SnelStart window (not the login window).
        
        Args:
            timeout: Maximum time to wait in seconds (optional, uses config default)
            interval: Check interval in seconds (optional, uses config default)
            
        Returns:
            Main window if found, raises RuntimeError otherwise
        """
        try:
            self.logger.info("Waiting for SnelStart main window...")
            main_window_title = self.window_titles['main_window']
            
            # Use retry logic to find the main window specifically
            def find_main_window():
                for window in Desktop(backend="uia").windows():
                    try:
                        window_text = window.window_text()
                        # Exact match for main window (not substring match)
                        if window_text == main_window_title:
                            self.logger.info(f"Found main window: '{window_text}'")
                            return window
                    except Exception as e:
                        self.logger.debug(f"Skipping window due to error: {e}")
                        continue
                raise RuntimeError(f"Main window '{main_window_title}' not found")
            
            main_window = simple_retry(find_main_window, "find SnelStart main window")
            self.logger.info(f"SnelStart main window found: '{main_window.window_text()}'")
            return main_window
            
        except Exception as e:
            self.logger.error(f"Failed to get SnelStart main window: {e}")
            raise RuntimeError(f"SnelStart main window not found: {e}")

    def get_login_window(self):
        """
        Find and return the login window if it exists.
        
        Returns:
            Login window if found, None if not found
        """
        try:
            self.logger.info("Searching for SnelStart login window...")
            login_window_title = self.window_titles['login_window']
            
            for window in Desktop(backend="uia").windows():
                try:
                    window_text = window.window_text()
                    # Exact match for login window
                    if window_text == login_window_title:
                        self.logger.info(f"Found login window: '{window_text}'")
                        return window
                except Exception as e:
                    self.logger.debug(f"Skipping window due to error: {e}")
                    continue
            
            self.logger.info("Login window not found")
            return None
            
        except Exception as e:
            self.logger.warning(f"Error searching for login window: {e}")
            return None

    def get_all_snelstart_windows(self):
        """
        Get all SnelStart-related windows for debugging purposes.
        
        Returns:
            Dictionary with 'main' and 'login' windows (values can be None)
        """
        try:
            self.logger.debug("Searching for all SnelStart windows...")
            main_window_title = self.window_titles['main_window']
            login_window_title = self.window_titles['login_window']
            
            windows = {'main': None, 'login': None}
            
            for window in Desktop(backend="uia").windows():
                try:
                    window_text = window.window_text()
                    if window_text == main_window_title:
                        windows['main'] = window
                        self.logger.debug(f"Found main window: '{window_text}'")
                    elif window_text == login_window_title:
                        windows['login'] = window  
                        self.logger.debug(f"Found login window: '{window_text}'")
                except Exception as e:
                    self.logger.debug(f"Skipping window due to error: {e}")
                    continue
            
            self.logger.debug(f"Windows found: main={windows['main'] is not None}, login={windows['login'] is not None}")
            return windows
            
        except Exception as e:
            self.logger.warning(f"Error searching for SnelStart windows: {e}")
            return {'main': None, 'login': None}


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

def get_login_window():
    """Backwards compatibility function."""
    launch_automation = LaunchAutomation()
    return launch_automation.get_login_window()

def get_all_snelstart_windows():
    """Backwards compatibility function."""
    launch_automation = LaunchAutomation()
    return launch_automation.get_all_snelstart_windows()