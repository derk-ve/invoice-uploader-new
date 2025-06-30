import time
from typing import Callable
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto import Desktop
from .logging_setup import LoggingSetup
from .config import Config


class WaitTimeoutError(Exception):
    """Exception raised when wait operations timeout."""
    pass


class WaitUtils:
    """Utility class for wait operations and UI element interactions."""
    
    def __init__(self):
        """Initialize WaitUtils with logger and config."""
        self.logger = LoggingSetup.get_logger(self.__class__.__name__)
        self._config = Config.get_retry_config()

    def simple_retry(self, operation, operation_name="operation"):
        """
        Simple retry pattern: try MAX_RETRIES times, wait up to MAX_WAITING_TIME per attempt.
        
        Args:
            operation: Function to call (should return result or raise exception)
            operation_name: Description for error messages
        
        Returns:
            Result from operation
            
        Raises:
            Exception: Last exception after all retries failed
        """
        max_retries = self._config['max_retries']
        max_waiting_time = self._config['max_waiting_time']
        
        last_exception = None
        
        for attempt in range(max_retries):
            self.logger.debug(f"Attempt {attempt + 1}/{max_retries} for {operation_name}")
            
            start_time = time.time()
            while time.time() - start_time < max_waiting_time:
                try:
                    result = operation()
                    if attempt > 0:
                        self.logger.debug(f"{operation_name} succeeded after {attempt + 1} attempts")
                    return result
                except Exception as e:
                    last_exception = e
                    # Wait a bit before next check within this attempt
                    time.sleep(0.5)
            
            self.logger.debug(f"Attempt {attempt + 1} timed out after {max_waiting_time}s for {operation_name}")
        
        raise Exception(f"{operation_name} failed after {max_retries} attempts. Last error: {last_exception}")

    def find_window_by_title(self, title_substring, exact_match=False):
        """
        Find a window by title with debug logging.
        
        Args:
            title_substring: Text that should appear in window title
            exact_match: If True, title must match exactly
            
        Returns:
            Window if found
            
        Raises:
            Exception: If window not found
        """
        all_windows = []
        
        try:
            for window in Desktop(backend="uia").windows():
                try:
                    window_text = window.window_text()
                    all_windows.append(window_text)
                    
                    if exact_match:
                        if window_text == title_substring:
                            self.logger.debug(f"Found exact match window: '{window_text}'")
                            return window
                    else:
                        if title_substring.lower() in window_text.lower():
                            self.logger.debug(f"Found window containing '{title_substring}': '{window_text}'")
                            return window
                except Exception as e:
                    self.logger.debug(f"Error checking window: {e}")
                    continue
        except Exception as e:
            self.logger.error(f"Error enumerating windows: {e}")
        
        # Log all found windows for debugging
        self.logger.error(f"Window with title '{title_substring}' not found. Available windows: {all_windows}")
        raise Exception(f"Window not found: '{title_substring}'. Available: {all_windows}")

    def wait_for_window_by_title(self, title_substring, exact_match=False):
        """
        Wait for a window with specific title to appear.
        
        Args:
            title_substring: Text that should appear in window title
            exact_match: If True, title must match exactly
            
        Returns:
            The window if found
            
        Raises:
            Exception: If window not found after retries
        """
        def find_operation():
            return self.find_window_by_title(title_substring, exact_match)
        
        return self.simple_retry(find_operation, f"find window '{title_substring}'")

    def wait_for_element(self, parent, selector_func, element_name="element"):
        """
        Wait for an element to exist within a parent.
        
        Args:
            parent: The parent element to search within
            selector_func: Function that takes parent and returns the desired element
            element_name: Description of element for error messages
            
        Returns:
            The found element
            
        Raises:
            Exception: If element not found after retries
        """
        def find_operation():
            element = selector_func(parent)
            if element and element.exists():
                return element
            raise Exception(f"Element not found: {element_name}")
        
        return self.simple_retry(find_operation, element_name)

    def safe_click(self, element, element_name="element"):
        """
        Safely click an element after ensuring it's clickable.
        
        Args:
            element: The element to click
            element_name: Description for error messages
            
        Raises:
            Exception: If element not clickable or click fails
        """
        def click_operation():
            if not (element.exists() and element.is_visible() and element.is_enabled()):
                raise Exception(f"Element not clickable: {element_name}")
            
            element.click_input()
            return True
        
        self.simple_retry(click_operation, f"click {element_name}")
        self.logger.debug(f"Successfully clicked {element_name}")

    def safe_type(self, element, text, element_name="input field"):
        """
        Safely type text into an element.
        
        Args:
            element: The element to type into
            text: Text to type
            element_name: Description for error messages
            
        Raises:
            Exception: If element not ready or typing fails
        """
        def type_operation():
            if not (element.exists() and element.is_visible() and element.is_enabled()):
                raise Exception(f"Element not ready for typing: {element_name}")
            
            # Try to set focus if needed
            if not element.has_keyboard_focus():
                element.set_focus()
                time.sleep(0.1)  # Brief pause for focus to take effect
            
            element.type_keys(text, with_spaces=True)
            return True
        
        self.simple_retry(type_operation, f"type into {element_name}")
        self.logger.debug(f"Successfully typed into {element_name}")

    def wait_for_dialog_ready(self, parent, dialog_text):
        """
        Wait for a dialog to appear and be ready for interaction.
        
        Args:
            parent: The parent window to search within
            dialog_text: Text that should appear in the dialog
            
        Returns:
            The dialog element
            
        Raises:
            Exception: If dialog not found after retries
        """
        def find_dialog(parent_elem):
            for child in parent_elem.descendants():
                try:
                    if (child.friendly_class_name() == "Dialog" and 
                        dialog_text in child.window_text()):
                        return child
                except:
                    continue
            return None
        
        return self.wait_for_element(parent, find_dialog, f"dialog containing '{dialog_text}'")

    def wait_with_timeout(self, condition_func, timeout=30, interval=2, description="condition", 
                         provide_feedback=True):
        """
        Wait for a condition with timeout/interval pattern (like get_main_window).
        
        Args:
            condition_func: Function that returns True/truthy when condition is met, 
                           False/falsy to continue waiting, or raises exception on error
            timeout: Maximum time to wait in seconds (default: 30)
            interval: Check interval in seconds (default: 2)  
            description: What we're waiting for (for logging)
            provide_feedback: Whether to log progress (default: True)
        
        Returns:
            True when condition met, or the truthy value returned by condition_func
            
        Raises:
            WaitTimeoutError: If timeout reached without condition being met
            Exception: Any exception raised by condition_func
        """
        elapsed = 0
        
        while elapsed < timeout:
            if provide_feedback:
                self.logger.info(f"Waiting for {description}... ({elapsed}/{timeout}s)")
            
            try:
                result = condition_func()
                if result:  # Condition met
                    if provide_feedback and elapsed > 0:
                        self.logger.info(f"{description} completed after {elapsed}s")
                    return result
            except Exception as e:
                # Let condition_func decide if exceptions should stop waiting or continue
                self.logger.debug(f"Exception in condition check for {description}: {e}")
                raise e
                
            time.sleep(interval)
            elapsed += interval

        raise WaitTimeoutError(f"Timeout waiting for {description} after {timeout}s")


# Create singleton instance for easy access
wait_utils = WaitUtils()

# Backwards compatibility functions for existing code
logger = wait_utils.logger

def simple_retry(operation, operation_name="operation"):
    return wait_utils.simple_retry(operation, operation_name)

def find_window_by_title(title_substring, exact_match=False):
    return wait_utils.find_window_by_title(title_substring, exact_match)

def wait_for_window_by_title(title_substring, exact_match=False):
    return wait_utils.wait_for_window_by_title(title_substring, exact_match)

def wait_for_element(parent, selector_func, element_name="element"):
    return wait_utils.wait_for_element(parent, selector_func, element_name)

def safe_click(element, element_name="element"):
    return wait_utils.safe_click(element, element_name)

def safe_type(element, text, element_name="input field"):
    return wait_utils.safe_type(element, text, element_name)

def wait_for_dialog_ready(parent, dialog_text):
    return wait_utils.wait_for_dialog_ready(parent, dialog_text)

def wait_with_timeout(condition_func, timeout=30, interval=2, description="condition", 
                     provide_feedback=True):
    return wait_utils.wait_with_timeout(condition_func, timeout, interval, description, provide_feedback)