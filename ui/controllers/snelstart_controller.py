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
    READY_FOR_UPLOAD = "ready_for_upload"
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
        self.on_upload_ready: Optional[Callable[[str], None]] = None
        self.on_state_changed: Optional[Callable[[SnelStartConnectionState, str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        # Polling for upload readiness
        self.polling_active = False
        
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
    
    def open_snelstart(self) -> bool:
        """
        Open or connect to SnelStart application (user will handle login/navigation).
        
        Returns:
            True if SnelStart opened/connected successfully, False otherwise
        """
        try:
            self._set_state(SnelStartConnectionState.CONNECTING, "Opening SnelStart...")
            
            if self.on_connection_start:
                self.on_connection_start("Opening SnelStart application...")
            
            # Initialize SnelStart automation
            self.snelstart_automation = SnelstartAutomation()
            
            # Attempt to start/connect
            if self.snelstart_automation.start():
                self._set_state(SnelStartConnectionState.CONNECTED, "SnelStart opened - please log in and navigate to bookkeeping")
                
                if self.on_connection_established:
                    self.on_connection_established("SnelStart is open. Please log in and navigate to the bookkeeping section.")
                
                # Start polling for upload readiness
                self.start_polling_for_upload_readiness()
                
                self.logger.info("Successfully opened/connected to SnelStart")
                return True
            else:
                self._set_state(SnelStartConnectionState.ERROR, "Failed to open SnelStart")
                if self.on_error:
                    self.on_error("Failed to start or connect to SnelStart application")
                return False
                
        except Exception as e:
            error_msg = f"Error opening SnelStart: {e}"
            self.logger.error(error_msg)
            self._set_state(SnelStartConnectionState.ERROR, error_msg)
            if self.on_error:
                self.on_error(error_msg)
            return False
    
    def start_polling_for_upload_readiness(self):
        """Start background polling to detect when upload button becomes available."""
        import threading
        import time
        
        if self.polling_active:
            return  # Already polling
            
        self.polling_active = True
        self.logger.info("Started polling for upload readiness")
        
        def poll_for_button():
            """Background thread to poll for the upload button."""
            while self.polling_active and self.connection_state == SnelStartConnectionState.CONNECTED:
                try:
                    if self._check_upload_button_available():
                        # Found the button! Update state
                        self._set_state(SnelStartConnectionState.READY_FOR_UPLOAD, "Ready for upload - 'Afschriften Inlezen' button found!")
                        
                        if self.on_upload_ready:
                            self.on_upload_ready("Upload button detected! You can now upload matched invoices.")
                        
                        self.polling_active = False
                        break
                    
                    # Wait before next check
                    time.sleep(3)  # Check every 3 seconds
                    
                except Exception as e:
                    self.logger.debug(f"Polling check failed (normal if user hasn't navigated yet): {e}")
                    time.sleep(3)
            
            self.logger.debug("Polling stopped")
        
        # Start background thread
        polling_thread = threading.Thread(target=poll_for_button, daemon=True)
        polling_thread.start()
    
    def stop_polling(self):
        """Stop the background polling."""
        self.polling_active = False
    
    def _check_upload_button_available(self) -> bool:
        """
        Check if the 'Afschriften Inlezen' button is available.
        
        Returns:
            True if button is found and clickable, False otherwise
        """
        try:
            if not self.snelstart_automation or not self.snelstart_automation.main_window:
                return False
            
            # Use the refactored button detection logic from DoBookkeepingAutomation
            from src.snelstart_automation.automations.do_bookkeeping import DoBookkeepingAutomation
            bookkeeping_automation = DoBookkeepingAutomation()
            
            # Use the dedicated find_invoice_button method
            button = bookkeeping_automation.find_invoice_button(self.snelstart_automation.main_window)
            return button is not None
            
        except Exception as e:
            self.logger.debug(f"Button check failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from SnelStart and clean up resources.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            # Stop polling
            self.stop_polling()
            
            # Close SnelStart automation
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
    
    
    # Callback setters
    def set_connection_start_callback(self, callback: Callable[[str], None]):
        """Set callback for connection start notifications."""
        self.on_connection_start = callback
    
    def set_connection_established_callback(self, callback: Callable[[str], None]):
        """Set callback for connection established notifications."""
        self.on_connection_established = callback
    
    def set_upload_ready_callback(self, callback: Callable[[str], None]):
        """Set callback for upload ready notifications."""
        self.on_upload_ready = callback
    
    def set_state_changed_callback(self, callback: Callable[[SnelStartConnectionState, str], None]):
        """Set callback for state change notifications."""
        self.on_state_changed = callback
    
    def set_error_callback(self, callback: Callable[[str], None]):
        """Set callback for error notifications."""
        self.on_error = callback