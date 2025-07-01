import os
import time
from dotenv import load_dotenv
from pywinauto.controls.uiawrapper import UIAWrapper
from ...utils.logging_setup import LoggingSetup
from ...utils.config import Config
from .launch_snelstart import LaunchAutomation
from ...utils.wait_utils import wait_with_timeout, WaitTimeoutError

load_dotenv()

class LoginAutomation:
    """Handles SnelStart login automation."""
    
    def __init__(self):
        """Initialize the login automation."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self.username, self.password = Config.get_credentials()
        self.ui_elements = Config.get_ui_elements()
        self.launch_automation = LaunchAutomation()
        
        # Get timing configuration from centralized config
        timing = Config.get_timing_config('login')
        self.DIALOG_FOCUS_DELAY = timing.get('dialog_focus_delay', 2)
        self.INPUT_DELAY = timing.get('input_delay', 2)
        self.AUTO_LOGIN_WAIT = timing.get('auto_login_wait', 5)
        self.LOGIN_COMPLETION_WAIT = timing.get('login_completion_wait', 3)
        self.LOGIN_DIALOG_WAIT_TIMEOUT = timing.get('login_dialog_wait_timeout', 10)
        self.LOGIN_DIALOG_WAIT_INTERVAL = timing.get('login_dialog_wait_interval', 2)
        self.LOGIN_COMPLETION_TIMEOUT = timing.get('login_completion_timeout', 10)
    
    def _get_main_window(self, main_window: UIAWrapper = None):
        """Get main window, retrieving it if not provided."""
        if main_window is None:
            return self.launch_automation.get_main_window()
        return main_window

    def get_login_dialog(self, window: UIAWrapper):
        """Search for and return the login dialog inside the main window (single attempt)."""
        self.logger.debug("Searching for login dialog inside main window...")
        for child in window.descendants():
            try:
                if child.friendly_class_name() == "Dialog" and self.ui_elements['login_dialog_text'] in child.window_text():
                    self.logger.debug(f"Found login dialog: '{child.window_text()}'")
                    return child
            except Exception as e:
                self.logger.debug(f"Skipping element due to error: {e}")
        raise RuntimeError("Login dialog not found inside main window")
    
    def _wait_for_login_dialog(self, window: UIAWrapper):
        """
        Wait for login dialog to appear with retry logic.
        
        Args:
            window: The main window to search in
            
        Returns:
            Login dialog if found, None if not found after timeout (indicating already logged in)
        """
        def find_dialog():
            try:
                return self.get_login_dialog(window)
            except RuntimeError:
                return None
        
        try:
            self.logger.info("Waiting for login dialog to appear...")
            result = wait_with_timeout(
                lambda: find_dialog() is not None,
                timeout=self.LOGIN_DIALOG_WAIT_TIMEOUT,
                interval=self.LOGIN_DIALOG_WAIT_INTERVAL,
                description="login dialog detection",
                provide_feedback=True
            )
            if result:
                return self.get_login_dialog(window)
        except WaitTimeoutError:
            self.logger.info("Login dialog not found after timeout - assuming already logged in")
            return None

    def _try_auto_login(self, login_dialog: UIAWrapper):
        """
        Try auto-login by waiting for login dialog to disappear automatically.
        
        Args:
            login_dialog: The login dialog to monitor
            
        Returns:
            True if auto-login succeeded, False if manual login is needed
        """
        def check_auto_login():
            try:
                # Check if dialog still exists and is visible
                if not login_dialog.is_visible():
                    self.logger.info("Login dialog is no longer visible — auto-login succeeded.")
                    return True
            except Exception:
                self.logger.info("Login dialog no longer exists — auto-login succeeded.")
                return True
            return False  # Dialog still exists, continue waiting
        
        try:
            self.logger.info("Checking for auto-login...")
            wait_with_timeout(check_auto_login, timeout=self.AUTO_LOGIN_WAIT, interval=1, 
                            description="auto-login completion", provide_feedback=False)
            return True  # Auto-login succeeded
        except WaitTimeoutError:
            self.logger.info("Auto-login timeout — manual login required")
            return False

    def _enter_username(self, login_dialog: UIAWrapper, username: str):
        """Pure action: Enter username in the login dialog without waiting."""
        self.logger.info("Entering username...")
        login_dialog.type_keys(username, with_spaces=True)

    def _submit_username(self, login_dialog: UIAWrapper):
        """Pure action: Navigate to password field and select password login option."""
        self.logger.info("Navigating to password field...")
        login_dialog.type_keys("{TAB}")
        login_dialog.type_keys("{ENTER}")

    def _navigate_to_password(self, login_dialog: UIAWrapper):
        """Pure action: Navigate to password field and select password login option."""
        self.logger.info("Selecting password login option...")
        login_dialog.type_keys("{TAB}{TAB}{ENTER}")

    def _enter_password(self, login_dialog: UIAWrapper, password: str):
        """Pure action: Enter password in the login dialog without waiting."""
        self.logger.info("Entering password...")
        login_dialog.type_keys(password, with_spaces=True)

    def _submit_password(self, login_dialog: UIAWrapper):
        """Submit the login form."""
        self.logger.info("Submitting login...")
        login_dialog.type_keys("{ENTER}")

    def _wait_between_steps(self, step_name: str, delay: float = None):
        """Pure wait function: adds timing delays between login steps."""
        if delay is None:
            delay = self.INPUT_DELAY
        self.logger.debug(f"Waiting {delay}s after {step_name}...")
        time.sleep(delay)



    def is_admin_row_ready(
        self,
        main_window: UIAWrapper
    ) -> bool:
        """
        Returns True if the 'Row 1' element is visible and enabled in the main window.
        """

        admin_row_text = Config.get_ui_elements()['admin_row_text']
        try:
            for ctrl in main_window.descendants():
                if (
                    ctrl.friendly_class_name() == "Custom"
                    and ctrl.window_text() == admin_row_text
                    and ctrl.is_visible()
                    and ctrl.is_enabled()
                ):
                    return True
        except Exception:
            pass
        return False
    
    
    def wait_for_login_completion(self, main_window: UIAWrapper):
        """
        Smart wait function: waits for login process to complete by checking login status.
        
        Args:
            main_window: The main window to check login status against
            
        Returns:
            True if login completed successfully
            
        Raises:
            WaitTimeoutError: If login not completed within timeout
        """
        def check_login_complete():
            return self.is_logged_in(main_window) and self.is_admin_row_ready(main_window)
        
        try:
            self.logger.info("Waiting for login to complete...")
            wait_with_timeout(
                check_login_complete,
                timeout=self.LOGIN_COMPLETION_TIMEOUT,
                interval=1,
                description="login completion verification",
                provide_feedback=True
            )
            time.sleep(5)
            return True
        except WaitTimeoutError:
            self.logger.error("Login completion timeout - login may have failed")
            raise
    
    def perform_login(self, login_dialog: UIAWrapper, username: str, password: str):
        """Orchestration function: perform login sequence with proper timing."""
        self.logger.info("Attempting to perform login...")
        
        try:
            # Focus the login dialog
            login_dialog.set_focus()
            self._wait_between_steps("dialog focus", self.DIALOG_FOCUS_DELAY)
            
            # Perform login steps with timing
            self._enter_username(login_dialog, username)
            self._wait_between_steps("username entry")

            self._submit_username(login_dialog)
            self._wait_between_steps("username submition")
            
            self._navigate_to_password(login_dialog)
            self._wait_between_steps("password navigation")
            
            self._enter_password(login_dialog, password)
            self._wait_between_steps("password entry")
            
            self._submit_password(login_dialog)
            
            self.logger.info("Login attempt complete")
            
        except Exception as e:
            self.logger.error(f"Error during login sequence: {e}")
            raise

    def is_logged_in(self, main_window: UIAWrapper = None):
        """Check if user is already logged in by verifying absence of login dialog in main window."""
        self.logger.info("Checking if user is already logged in...")
        
        try:
            main_window = self._get_main_window(main_window)
            
            # Check if login dialog exists in main window
            try:
                self.get_login_dialog(main_window)
                # Login dialog exists, user is not logged in
                self.logger.info("Login dialog found in main window - user is not logged in")
                return False
            except RuntimeError:
                 # Login dialog not found, now check if main window is enabled
                if main_window.is_enabled():
                    self.logger.info("Login dialog not found and main window is enabled - user is logged in")
                    return True
                else:# Login dialog not found, user is logged in
                    self.logger.info("Login dialog not found but main window is not enabled - still loading")
                return True
                
        except Exception as e:
            self.logger.warning(f"Error checking login status: {e}")
            # If we can't determine, assume not logged in to be safe
            return False

    def login_to_snelstart(self, main_window: UIAWrapper = None):
        """
        Main login function that handles the complete login process.
        
        This orchestration function follows a clear 4-step process:
        1. Wait for login dialog (with retry)
        2. Try auto-login  
        3. Manual login (if needed)
        4. Wait for login completion (smart waiting)
        """
        try:
            main_window = self._get_main_window(main_window)
            
            # Step 1: Wait for login dialog (with retry)
            login_dialog = self._wait_for_login_dialog(main_window)
            if not login_dialog:
                self.logger.info("No login dialog found - already logged in")
                return True
            
            # Step 2: Try auto-login
            if self._try_auto_login(login_dialog):
                self.logger.info("Auto-login succeeded")
                return True
            
            # Step 3: Manual login (separate from waiting)
            self.logger.info("Proceeding with manual login...")
            self.perform_login(login_dialog, self.username, self.password)
            
            # Step 4: Wait for login completion (smart waiting)
            self.wait_for_login_completion(main_window)
            self.logger.info("Manual login completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False


# Backwards compatibility functions for existing code
def get_login_dialog(window: UIAWrapper):
    """Backwards compatibility function for getting login dialog inside main window."""
    login_automation = LoginAutomation()
    return login_automation.get_login_dialog(window)

def perform_login(login_window: UIAWrapper, username: str, password: str):
    """Backwards compatibility function."""
    login_automation = LoginAutomation()
    login_automation.perform_login(login_window, username, password)

def login_to_snelstart(window: UIAWrapper = None):
    """Backwards compatibility function. Window parameter is used as main window."""
    login_automation = LoginAutomation()
    return login_automation.login_to_snelstart(window)

def is_logged_in(main_window: UIAWrapper = None):
    """New function for checking login status."""
    login_automation = LoginAutomation()
    return login_automation.is_logged_in(main_window)

def wait_for_login_completion(main_window: UIAWrapper = None):
    """New function for waiting for login completion."""
    login_automation = LoginAutomation()
    return login_automation.wait_for_login_completion(main_window)