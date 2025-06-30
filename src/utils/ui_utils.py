import logging
from pywinauto.controls.uiawrapper import UIAWrapper

# Configure logging
logger = logging.getLogger(__name__)

def print_control_tree(control: UIAWrapper, level: int = 0):
    """
    Print the control tree of a window for debugging purposes.
    
    Args:
        control: The UI control to print
        level: The current indentation level
    """
    indent = "  " * level
    try:
        print(f"{indent}- {control.friendly_class_name()}: '{control.window_text()}' (ID: {control.control_id()})")
        for child in control.children():
            print_control_tree(child, level + 1)
    except Exception as e:
        logger.error(f"Error printing control tree: {e}")

def find_control_by_text(control: UIAWrapper, text: str, case_sensitive: bool = False):
    """
    Find a control by its text.
    
    Args:
        control: The parent control to search in
        text: The text to search for
        case_sensitive: Whether to perform case-sensitive matching
        
    Returns:
        The first matching control or None if not found
    """
    try:
        for child in control.descendants():
            try:
                child_text = child.window_text()
                if not case_sensitive:
                    child_text = child_text.lower()
                    search_text = text.lower()
                else:
                    search_text = text
                    
                if search_text in child_text:
                    return child
            except:
                pass
    except Exception as e:
        logger.error(f"Error finding control by text: {e}")
    
    return None

def find_control_by_class(control: UIAWrapper, class_name: str):
    """
    Find a control by its class name.
    
    Args:
        control: The parent control to search in
        class_name: The class name to search for
        
    Returns:
        The first matching control or None if not found
    """
    try:
        for child in control.descendants():
            try:
                if child.friendly_class_name() == class_name:
                    return child
            except:
                pass
    except Exception as e:
        logger.error(f"Error finding control by class: {e}")
    
    return None 