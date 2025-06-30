import time
from typing import Callable
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto import Desktop
from .logging_setup import get_logger
from .config import get_retry_config

logger = get_logger(__name__)

# Get retry configuration
_config = get_retry_config()

class WaitTimeoutError(Exception):
    """Exception raised when wait operations timeout."""
    pass

def simple_retry(operation, operation_name="operation"):
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
    max_retries = _config['max_retries']
    max_waiting_time = _config['max_waiting_time']
    
    last_exception = None
    
    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1}/{max_retries} for {operation_name}")
        
        start_time = time.time()
        while time.time() - start_time < max_waiting_time:
            try:
                result = operation()
                if attempt > 0:
                    logger.debug(f"{operation_name} succeeded after {attempt + 1} attempts")
                return result
            except Exception as e:
                last_exception = e
                # Wait a bit before next check within this attempt
                time.sleep(0.5)
        
        logger.debug(f"Attempt {attempt + 1} timed out after {max_waiting_time}s for {operation_name}")
    
    raise Exception(f"{operation_name} failed after {max_retries} attempts. Last error: {last_exception}")

def find_window_by_title(title_substring, exact_match=False):
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
                        logger.debug(f"Found exact match window: '{window_text}'")
                        return window
                else:
                    if title_substring.lower() in window_text.lower():
                        logger.debug(f"Found window containing '{title_substring}': '{window_text}'")
                        return window
            except Exception as e:
                logger.debug(f"Error checking window: {e}")
                continue
    except Exception as e:
        logger.error(f"Error enumerating windows: {e}")
    
    # Log all found windows for debugging
    logger.error(f"Window with title '{title_substring}' not found. Available windows: {all_windows}")
    raise Exception(f"Window not found: '{title_substring}'. Available: {all_windows}")

def wait_for_window_by_title(title_substring, exact_match=False):
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
        return find_window_by_title(title_substring, exact_match)
    
    return simple_retry(find_operation, f"find window '{title_substring}'")

def wait_for_element(parent, selector_func, element_name="element"):
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
    
    return simple_retry(find_operation, element_name)

def safe_click(element, element_name="element"):
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
    
    simple_retry(click_operation, f"click {element_name}")
    logger.debug(f"Successfully clicked {element_name}")

def safe_type(element, text, element_name="input field"):
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
    
    simple_retry(type_operation, f"type into {element_name}")
    logger.debug(f"Successfully typed into {element_name}")

def wait_for_dialog_ready(parent, dialog_text):
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
    
    return wait_for_element(parent, find_dialog, f"dialog containing '{dialog_text}'")