"""
Controller for SnelStart automation business logic.
"""

from enum import Enum
from typing import Optional, Callable, List
from pathlib import Path

from src.snelstart_automation.automations.launch_snelstart import LaunchAutomation
from src.snelstart_automation.snelstart_auto import SnelstartAutomation
from src.utils.logging_setup import LoggingSetup


class SnelStartConnectionState(Enum):
    """Enumeration of SnelStart connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting" 
    CONNECTED = "connected"
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
        
        # Health monitoring
        self.health_monitoring_active = False
        
        self.logger.debug("SnelStart controller initialized")
    
    def get_connection_state(self) -> SnelStartConnectionState:
        """
        Get the current SnelStart connection state.
        
        Returns:
            Current connection state
        """
        return self.connection_state
    
    def is_connected(self) -> bool:
        """
        Check if SnelStart is connected and available.
        
        Returns:
            True if connected, False otherwise
        """
        return self.connection_state == SnelStartConnectionState.CONNECTED
    
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
            
            # Clean up any existing connection first
            if self.snelstart_automation:
                self.disconnect()
            
            # Initialize SnelStart automation
            self.snelstart_automation = SnelstartAutomation()
            
            # Attempt to start/connect
            if self.snelstart_automation.start():
                self._set_state(SnelStartConnectionState.CONNECTED, "Successfully connected to SnelStart")
                
                if self.on_connection_established:
                    self.on_connection_established("SnelStart connection established successfully!")
                
                # Start health monitoring instead of upload polling
                self.start_health_monitoring()
                
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
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to SnelStart.
        
        Returns:
            True if reconnection successful, False otherwise
        """
        self.logger.info("Attempting to reconnect to SnelStart")
        
        # Reset state and try to connect again
        if self.connection_state == SnelStartConnectionState.ERROR:
            return self.open_snelstart()
        else:
            self.logger.warning("Reconnect called but not in error state")
            return False
    
    def start_health_monitoring(self):
        """Start background health monitoring to detect connection loss."""
        import threading
        import time
        
        if self.health_monitoring_active:
            return  # Already monitoring
            
        self.health_monitoring_active = True
        self.logger.info("Started connection health monitoring")
        
        def monitor_connection():
            """Background thread to monitor connection health."""
            while self.health_monitoring_active and self.connection_state == SnelStartConnectionState.CONNECTED:
                try:
                    self.logger.debug("Checking health...")
                    if not self._check_connection_health():
                        # Connection lost! Update state
                        self._set_state(SnelStartConnectionState.ERROR, "Connection to SnelStart lost")
                        
                        if self.on_error:
                            self.on_error("SnelStart connection lost. Please reconnect.")
                        
                        self.health_monitoring_active = False
                        break
                    
                    # Wait before next check (every 15 seconds)
                    time.sleep(15)
                    
                except Exception as e:
                    self.logger.debug(f"Health check failed: {e}")
                    time.sleep(15)
            
            self.logger.debug("Health monitoring stopped")
        
        # Start background thread
        health_thread = threading.Thread(target=monitor_connection, daemon=True)
        health_thread.start()
    
    def stop_health_monitoring(self):
        """Stop the health monitoring."""
        self.health_monitoring_active = False
    
    def _check_connection_health(self) -> bool:
        """
        Check if the SnelStart connection is still healthy.
        
        Returns:
            True if connection is healthy, False if connection lost
        """
        try:
            if not self.snelstart_automation or not self.snelstart_automation.main_window:
                return False
            
            # Check if the main window still exists and is accessible
            # This is a lightweight check to see if SnelStart is still running
            window = LaunchAutomation.get_main_window()
            
            if window is not None:
                self.logger.debug("Health check: Snelstart window found")
                return True
            else:
                self.logger.debug("Health check: SnelStart window NOT found")
                self.snelstart_automation.main_window = None
                return False
            
        except Exception as e:
            self.logger.debug(f"Health check failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from SnelStart and clean up resources.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            # Stop health monitoring
            self.stop_health_monitoring()
            
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