"""
Controller for SnelStart automation business logic.
"""

from enum import Enum
from typing import Optional, Callable, List
from pathlib import Path

from src.snelstart_automation.snelstart_auto import SnelstartAutomation
from src.utils.logging_setup import LoggingSetup


class SnelStartConnectionState(Enum):
    """Enumeration of SnelStart connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    LOGGING_IN = "logging_in"
    LOGGED_IN = "logged_in"
    NAVIGATING = "navigating"
    READY_FOR_UPLOAD = "ready_for_upload"
    UPLOADING = "uploading"
    ERROR = "error"


class SnelStartController:
    """Controller for handling SnelStart automation business logic from UI."""
    
    def __init__(self):
        """Initialize the SnelStart controller."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        
        # SnelStart automation instance
        self.snelstart_automation: Optional[SnelstartAutomation] = None
        self.connection_state = SnelStartConnectionState.DISCONNECTED
        
        # Callbacks for progress updates
        self.on_connection_start: Optional[Callable[[str], None]] = None
        self.on_connection_established: Optional[Callable[[str], None]] = None
        self.on_login_start: Optional[Callable[[str], None]] = None
        self.on_login_completed: Optional[Callable[[str], None]] = None
        self.on_navigation_start: Optional[Callable[[str], None]] = None
        self.on_navigation_completed: Optional[Callable[[str], None]] = None
        self.on_upload_ready: Optional[Callable[[str], None]] = None
        self.on_state_changed: Optional[Callable[[SnelStartConnectionState, str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        self.logger.debug("SnelStart controller initialized")
    
    def get_connection_state(self) -> SnelStartConnectionState:
        """
        Get the current SnelStart connection state.
        
        Returns:
            Current connection state
        """
        return self.connection_state
    
    def is_ready_for_upload(self) -> bool:
        """
        Check if SnelStart is ready to accept file uploads.
        
        Returns:
            True if ready for upload, False otherwise
        """
        return self.connection_state == SnelStartConnectionState.READY_FOR_UPLOAD
    
    def connect_to_snelstart(self) -> bool:
        """
        Start or connect to SnelStart application.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._set_state(SnelStartConnectionState.CONNECTING, "Connecting to SnelStart...")
            
            if self.on_connection_start:
                self.on_connection_start("Starting SnelStart application...")
            
            # Initialize SnelStart automation
            self.snelstart_automation = SnelstartAutomation()
            
            # Attempt to start/connect
            if self.snelstart_automation.start():
                self._set_state(SnelStartConnectionState.CONNECTED, "Connected to SnelStart")
                
                if self.on_connection_established:
                    self.on_connection_established("Successfully connected to SnelStart")
                
                self.logger.info("Successfully connected to SnelStart")
                return True
            else:
                self._set_state(SnelStartConnectionState.ERROR, "Failed to connect to SnelStart")
                if self.on_error:
                    self.on_error("Failed to start or connect to SnelStart application")
                return False
                
        except Exception as e:
            error_msg = f"Error connecting to SnelStart: {e}"
            self.logger.error(error_msg)
            self._set_state(SnelStartConnectionState.ERROR, error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False
    
    def perform_login(self) -> bool:
        """
        Perform SnelStart login process.
        
        Returns:
            True if login successful, False otherwise
        """
        try:
            if not self._ensure_connected():
                return False
            
            self._set_state(SnelStartConnectionState.LOGGING_IN, "Logging into SnelStart...")
            
            if self.on_login_start:
                self.on_login_start("Starting login process...")
            
            # Perform login
            if self.snelstart_automation.login():
                self._set_state(SnelStartConnectionState.LOGGED_IN, "Successfully logged in")
                
                if self.on_login_completed:
                    self.on_login_completed("Login completed successfully")
                
                self.logger.info("SnelStart login completed")
                return True
            else:
                self._set_state(SnelStartConnectionState.ERROR, "Login failed")
                if self.on_error:
                    self.on_error("SnelStart login failed")
                return False
                
        except Exception as e:
            error_msg = f"Error during login: {e}"
            self.logger.error(error_msg)
            self._set_state(SnelStartConnectionState.ERROR, error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False
    
    def navigate_to_bookkeeping(self) -> bool:
        """
        Navigate to SnelStart bookkeeping section.
        
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            if not self._ensure_logged_in():
                return False
            
            self._set_state(SnelStartConnectionState.NAVIGATING, "Navigating to bookkeeping...")
            
            if self.on_navigation_start:
                self.on_navigation_start("Opening administration and bookkeeping...")
            
            # Navigate to bookkeeping
            if self.snelstart_automation.open_bookkeeping():
                self._set_state(SnelStartConnectionState.READY_FOR_UPLOAD, "Ready for file upload")
                
                if self.on_navigation_completed:
                    self.on_navigation_completed("Navigation completed - bookkeeping section opened")
                
                self.logger.info("Successfully navigated to bookkeeping section")
                return True
            else:
                self._set_state(SnelStartConnectionState.ERROR, "Navigation failed")
                if self.on_error:
                    self.on_error("Failed to navigate to bookkeeping section")
                return False
                
        except Exception as e:
            error_msg = f"Error during navigation: {e}"
            self.logger.error(error_msg)
            self._set_state(SnelStartConnectionState.ERROR, error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False
    
    def prepare_for_upload(self) -> bool:
        """
        Prepare SnelStart for file upload by clicking 'Afschriften Inlezen'.
        
        Returns:
            True if preparation successful, False otherwise
        """
        try:
            if not self._ensure_ready_for_upload():
                return False
            
            self._set_state(SnelStartConnectionState.UPLOADING, "Preparing for file upload...")
            
            if self.on_upload_ready:
                self.on_upload_ready("Clicking 'Afschriften Inlezen' to prepare upload...")
            
            # Click the upload button (this will be extended later for actual file handling)
            if self.snelstart_automation.load_in_afschriften():
                if self.on_upload_ready:
                    self.on_upload_ready("SnelStart is ready to accept file uploads")
                
                self.logger.info("SnelStart prepared for file upload")
                return True
            else:
                self._set_state(SnelStartConnectionState.ERROR, "Failed to prepare upload")
                if self.on_error:
                    self.on_error("Failed to prepare SnelStart for file upload")
                return False
                
        except Exception as e:
            error_msg = f"Error preparing upload: {e}"
            self.logger.error(error_msg)
            self._set_state(SnelStartConnectionState.ERROR, error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False
    
    def run_complete_workflow(self) -> bool:
        """
        Run the complete SnelStart workflow: connect → login → navigate → prepare.
        
        Returns:
            True if entire workflow successful, False otherwise
        """
        try:
            self.logger.info("Starting complete SnelStart workflow")
            
            # Step 1: Connect
            if not self.connect_to_snelstart():
                return False
            
            # Step 2: Login
            if not self.perform_login():
                return False
            
            # Step 3: Navigate
            if not self.navigate_to_bookkeeping():
                return False
            
            # Step 4: Prepare for upload
            if not self.prepare_for_upload():
                return False
            
            self.logger.info("Complete SnelStart workflow completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Error in complete workflow: {e}"
            self.logger.error(error_msg)
            self._set_state(SnelStartConnectionState.ERROR, error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from SnelStart and clean up resources.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            if self.snelstart_automation:
                self.snelstart_automation.close()
                self.snelstart_automation = None
            
            self._set_state(SnelStartConnectionState.DISCONNECTED, "Disconnected from SnelStart")
            self.logger.info("Disconnected from SnelStart")
            return True
            
        except Exception as e:
            error_msg = f"Error disconnecting: {e}"
            self.logger.error(error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False
    
    def _set_state(self, state: SnelStartConnectionState, message: str):
        """
        Set the connection state and notify callbacks.
        
        Args:
            state: New connection state
            message: Status message
        """
        self.connection_state = state
        self.logger.debug(f"State changed to {state.value}: {message}")
        
        if self.on_state_changed:
            self.on_state_changed(state, message)
    
    def _ensure_connected(self) -> bool:
        """Ensure SnelStart is connected."""
        if self.connection_state == SnelStartConnectionState.DISCONNECTED:
            if self.on_error:
                self.on_error("Not connected to SnelStart. Please connect first.")
            return False
        if not self.snelstart_automation:
            if self.on_error:
                self.on_error("SnelStart automation not initialized.")
            return False
        return True
    
    def _ensure_logged_in(self) -> bool:
        """Ensure SnelStart is logged in."""
        if not self._ensure_connected():
            return False
        if self.connection_state not in [SnelStartConnectionState.LOGGED_IN, 
                                       SnelStartConnectionState.NAVIGATING,
                                       SnelStartConnectionState.READY_FOR_UPLOAD]:
            if self.on_error:
                self.on_error("Not logged in to SnelStart. Please login first.")
            return False
        return True
    
    def _ensure_ready_for_upload(self) -> bool:
        """Ensure SnelStart is ready for upload."""
        if not self._ensure_logged_in():
            return False
        if self.connection_state != SnelStartConnectionState.READY_FOR_UPLOAD:
            if self.on_error:
                self.on_error("SnelStart not ready for upload. Please navigate to bookkeeping first.")
            return False
        return True
    
    # Callback setters
    def set_connection_start_callback(self, callback: Callable[[str], None]):
        """Set callback for connection start notifications."""
        self.on_connection_start = callback
    
    def set_connection_established_callback(self, callback: Callable[[str], None]):
        """Set callback for connection established notifications."""
        self.on_connection_established = callback
    
    def set_login_start_callback(self, callback: Callable[[str], None]):
        """Set callback for login start notifications."""
        self.on_login_start = callback
    
    def set_login_completed_callback(self, callback: Callable[[str], None]):
        """Set callback for login completed notifications."""
        self.on_login_completed = callback
    
    def set_navigation_start_callback(self, callback: Callable[[str], None]):
        """Set callback for navigation start notifications."""
        self.on_navigation_start = callback
    
    def set_navigation_completed_callback(self, callback: Callable[[str], None]):
        """Set callback for navigation completed notifications."""
        self.on_navigation_completed = callback
    
    def set_upload_ready_callback(self, callback: Callable[[str], None]):
        """Set callback for upload ready notifications."""
        self.on_upload_ready = callback
    
    def set_state_changed_callback(self, callback: Callable[[SnelStartConnectionState, str], None]):
        """Set callback for state change notifications."""
        self.on_state_changed = callback
    
    def set_error_callback(self, callback: Callable[[str], None]):
        """Set callback for error notifications."""
        self.on_error = callback