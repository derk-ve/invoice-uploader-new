import time
from typing import Callable, Optional, Any
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto import Desktop
from .logging_setup import get_logger
from .config import get_timeouts

logger = get_logger(__name__)

# Get timeout configuration
_timeouts = get_timeouts()

class WaitTimeoutError(Exception):
    """Exception raised when wait operations timeout."""
    pass

def wait_for_element(parent: UIAWrapper, selector_func: Callable[[UIAWrapper], UIAWrapper], 
                    timeout: float = None, interval: float = None, element_name: str = "element") -> UIAWrapper:
    """
    Wait for an element to exist and be accessible within a parent.
    
    Args:
        parent: The parent element to search within
        selector_func: Function that takes parent and returns the desired element
        timeout: Maximum time to wait in seconds (uses config default if None)
        interval: Time between attempts in seconds (uses config default if None)
        element_name: Description of element for error messages
        
    Returns:
        The found element
        
    Raises:
        WaitTimeoutError: If element not found within timeout
    """
    if timeout is None:
        timeout = _timeouts['element_timeout']
    if interval is None:
        interval = _timeouts['retry_interval']
    
    start_time = time.time()
    attempt = 0
    
    while time.time() - start_time < timeout:
        attempt += 1
        try:
            element = selector_func(parent)
            if element and element.exists():
                logger.debug(f"Found {element_name} after {attempt} attempts ({time.time() - start_time:.1f}s)")
                return element
        except Exception as e:
            logger.debug(f"Attempt {attempt} failed for {element_name}: {e}")
        
        # Exponential backoff with max interval
        actual_interval = min(interval * (1.2 ** attempt), 2.0)
        time.sleep(actual_interval)
    
    raise WaitTimeoutError(f"Timeout waiting for {element_name} after {timeout}s (parent: {parent.window_text() if parent else 'None'})")

def wait_for_clickable(element: UIAWrapper, timeout: float = None, element_name: str = "element") -> UIAWrapper:
    """
    Wait for an element to be clickable (visible, enabled, and interactive).
    
    Args:
        element: The element to check
        timeout: Maximum time to wait in seconds (uses config default if None)
        element_name: Description of element for error messages
        
    Returns:
        The element if clickable
        
    Raises:
        WaitTimeoutError: If element not clickable within timeout
    """
    if timeout is None:
        timeout = _timeouts['clickable_timeout']
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            if (element.exists() and 
                element.is_visible() and 
                element.is_enabled() and
                hasattr(element, 'click_input')):
                logger.debug(f"{element_name} is clickable after {time.time() - start_time:.1f}s")
                return element
        except Exception as e:
            logger.debug(f"Clickable check failed for {element_name}: {e}")
        
        time.sleep(0.2)
    
    raise WaitTimeoutError(f"Timeout waiting for {element_name} to be clickable after {timeout}s")

def wait_for_window_ready(window: UIAWrapper, timeout: float = None, window_name: str = "window") -> UIAWrapper:
    """
    Wait for a window to be fully loaded and responsive.
    
    Args:
        window: The window to check
        timeout: Maximum time to wait in seconds (uses config default if None)
        window_name: Description of window for error messages
        
    Returns:
        The window if ready
        
    Raises:
        WaitTimeoutError: If window not ready within timeout
    """
    if timeout is None:
        timeout = _timeouts['window_timeout']
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            if (window.exists() and 
                window.is_visible() and 
                window.has_keyboard_focus() or window.can_be_focused()):
                
                # Additional check: try to enumerate children to ensure window is responsive
                try:
                    list(window.children())
                    logger.debug(f"{window_name} is ready after {time.time() - start_time:.1f}s")
                    return window
                except:
                    # Window exists but not fully loaded yet
                    pass
                    
        except Exception as e:
            logger.debug(f"Window ready check failed for {window_name}: {e}")
        
        time.sleep(0.5)
    
    raise WaitTimeoutError(f"Timeout waiting for {window_name} to be ready after {timeout}s")

def wait_for_dialog_ready(parent: UIAWrapper, dialog_text: str, timeout: float = None) -> UIAWrapper:
    """
    Wait for a dialog to appear and be ready for interaction.
    
    Args:
        parent: The parent window to search within
        dialog_text: Text that should appear in the dialog
        timeout: Maximum time to wait in seconds (uses config default if None)
        
    Returns:
        The dialog element
        
    Raises:
        WaitTimeoutError: If dialog not found within timeout
    """
    if timeout is None:
        timeout = _timeouts['element_timeout']
    
    def find_dialog(parent_elem):
        for child in parent_elem.descendants():
            try:
                if (child.friendly_class_name() == "Dialog" and 
                    dialog_text in child.window_text()):
                    return child
            except:
                continue
        return None
    
    dialog = wait_for_element(parent, find_dialog, timeout, _timeouts['retry_interval'], f"dialog containing '{dialog_text}'")
    return wait_for_window_ready(dialog, timeout=_timeouts['window_timeout'], window_name=f"dialog '{dialog_text}'")

def wait_for_window_by_title(title_substring: str, timeout: float = None, exact_match: bool = False) -> UIAWrapper:
    """
    Wait for a window with specific title to appear on desktop.
    
    Args:
        title_substring: Text that should appear in window title
        timeout: Maximum time to wait in seconds (uses config default if None)
        exact_match: If True, title must match exactly
        
    Returns:
        The window if found
        
    Raises:
        WaitTimeoutError: If window not found within timeout
    """
    if timeout is None:
        timeout = _timeouts['window_timeout']
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            for window in Desktop(backend="uia").windows():
                window_text = window.window_text()
                if exact_match:
                    if window_text == title_substring:
                        return wait_for_window_ready(window, _timeouts['window_timeout'], f"window '{title_substring}'")
                else:
                    if title_substring in window_text:
                        return wait_for_window_ready(window, _timeouts['window_timeout'], f"window containing '{title_substring}'")
        except Exception as e:
            logger.debug(f"Window search failed: {e}")
        
        time.sleep(1.0)
    
    raise WaitTimeoutError(f"Timeout waiting for window with title '{title_substring}' after {timeout}s")

def wait_for_text_input_ready(element: UIAWrapper, timeout: float = None) -> UIAWrapper:
    """
    Wait for a text input field to be ready for typing.
    
    Args:
        element: The input element
        timeout: Maximum time to wait in seconds (uses config default if None)
        
    Returns:
        The element if ready for input
        
    Raises:
        WaitTimeoutError: If element not ready within timeout
    """
    if timeout is None:
        timeout = _timeouts['clickable_timeout']
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            if (element.exists() and 
                element.is_visible() and 
                element.is_enabled() and
                element.has_keyboard_focus()):
                return element
                
            # Try to set focus if not focused
            if element.exists() and element.is_visible() and element.is_enabled():
                element.set_focus()
                time.sleep(0.1)
                if element.has_keyboard_focus():
                    return element
                    
        except Exception as e:
            logger.debug(f"Text input ready check failed: {e}")
        
        time.sleep(0.2)
    
    raise WaitTimeoutError(f"Timeout waiting for text input to be ready after {timeout}s")

def safe_click(element: UIAWrapper, timeout: float = None, element_name: str = "element") -> None:
    """
    Safely click an element after ensuring it's clickable.
    
    Args:
        element: The element to click
        timeout: Maximum time to wait for element to be clickable (uses config default if None)
        element_name: Description for error messages
        
    Raises:
        WaitTimeoutError: If element not clickable within timeout
    """
    if timeout is None:
        timeout = _timeouts['clickable_timeout']
    
    clickable_element = wait_for_clickable(element, timeout, element_name)
    try:
        clickable_element.click_input()
        logger.debug(f"Successfully clicked {element_name}")
    except Exception as e:
        logger.error(f"Failed to click {element_name}: {e}")
        raise

def safe_type(element: UIAWrapper, text: str, timeout: float = None, element_name: str = "input field") -> None:
    """
    Safely type text into an element after ensuring it's ready.
    
    Args:
        element: The element to type into
        text: Text to type
        timeout: Maximum time to wait for element to be ready (uses config default if None)
        element_name: Description for error messages
        
    Raises:
        WaitTimeoutError: If element not ready within timeout
    """
    if timeout is None:
        timeout = _timeouts['clickable_timeout']
    
    ready_element = wait_for_text_input_ready(element, timeout)
    try:
        ready_element.type_keys(text, with_spaces=True)
        logger.debug(f"Successfully typed into {element_name}")
    except Exception as e:
        logger.error(f"Failed to type into {element_name}: {e}")
        raise