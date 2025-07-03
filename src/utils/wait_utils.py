import time
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


def wait_for_element(parent, selector_func, element_name="element"):
    return wait_utils.wait_for_element(parent, selector_func, element_name)

def safe_type(element, text, element_name="input field"):
    return wait_utils.safe_type(element, text, element_name)

def wait_with_timeout(condition_func, timeout=30, interval=2, description="condition", 
                     provide_feedback=True):
    return wait_utils.wait_with_timeout(condition_func, timeout, interval, description, provide_feedback)