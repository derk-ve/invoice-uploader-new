import logging
import json
import os
from datetime import datetime
from pywinauto.controls.uiawrapper import UIAWrapper


class UIUtils:
    """Utility class for UI debugging and element manipulation."""
    
    def __init__(self):
        """Initialize UIUtils with logger."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def print_control_tree(self, control: UIAWrapper, level: int = 0):
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
                self.print_control_tree(child, level + 1)
        except Exception as e:
            self.logger.error(f"Error printing control tree: {e}")

    def get_control_by_text(self, control: UIAWrapper, text: str, case_sensitive: bool = False):
        """
        Get a control by its text.
        
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
            self.logger.error(f"Error finding control by text: {e}")
        
        return None

    def get_control_by_class(self, control: UIAWrapper, class_name: str):
        """
        Get a control by its class name.
        
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
            self.logger.error(f"Error finding control by class: {e}")
        
        return None

    def get_descendant_by_criteria(self, parent: UIAWrapper, class_name: str = None, 
                                   text: str = None, text_contains: bool = False):
        """
        Get a descendant element matching specified criteria.
        
        This is a unified utility function that replaces the scattered
        'for ctrl in parent.descendants()' patterns throughout the codebase.
        
        Args:
            parent: Parent control to search in
            class_name: friendly_class_name to match (optional)
            text: window_text to match (optional) 
            text_contains: If True, check if text is contained in window_text; 
                          if False, require exact match (default: False)
            
        Returns:
            UIAWrapper: First matching control or None if not found
            
        Examples:
            # Get button with specific text
            button = ui_utils.get_descendant_by_criteria(window, "Button", "Afschriften Inlezen")
            
            # Get dialog containing text
            dialog = ui_utils.get_descendant_by_criteria(window, "Dialog", "Inloggen", text_contains=True)
            
            # Get any element of specific class
            custom = ui_utils.get_descendant_by_criteria(window, class_name="Custom")
            
            # Get element by text only
            element = ui_utils.get_descendant_by_criteria(window, text="Row 1")
        """
        try:
            if not parent:
                self.logger.debug("Parent control is None")
                return None
                
            for ctrl in parent.descendants():
                try:
                    # Check class name match if specified
                    if class_name and ctrl.friendly_class_name() != class_name:
                        continue
                    
                    # Check text match if specified
                    if text is not None:
                        ctrl_text = ctrl.window_text()
                        if text_contains:
                            if text not in ctrl_text:
                                continue
                        else:
                            if ctrl_text != text:
                                continue
                    
                    # If we get here, all criteria match
                    self.logger.debug(f"Found matching element: class='{ctrl.friendly_class_name()}', text='{ctrl.window_text()}'")
                    return ctrl
                    
                except Exception as e:
                    # Skip problematic controls (common in UI automation)
                    self.logger.debug(f"Skipping control due to error: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error searching for descendant: {e}")
        
        self.logger.debug(f"No descendant found matching criteria: class_name='{class_name}', text='{text}', text_contains={text_contains}")
        return None

    def safe_click(self, element, element_name: str = "element"):
        """
        Safely click an element after ensuring it's clickable.
        
        Args:
            element: The element to click
            element_name: Description for error messages
            
        Raises:
            Exception: If element not clickable or click fails
        """
        try:
            
            if not (element.exists() and element.is_visible() and element.is_enabled()):
                self.logger.error(f"Element not clickable: {element_name}")
            
            element.set_focus()
            element.click_input()
            self.logger.debug(f"Successfully clicked {element_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to click {element_name}: {e}")
            raise

    def generate_window_report(self, control: UIAWrapper, window_name: str = None, reports_dir: str = "reports"):
        """
        Generate a structured report of all UI elements in a window.
        
        Args:
            control: The window control to analyze
            window_name: Optional custom name for the window
            reports_dir: Directory to save reports (default: "reports")
            
        Returns:
            dict: Structured element data
        """
        try:
            # Create reports directory if it doesn't exist
            os.makedirs(reports_dir, exist_ok=True)
            
            # Get window information
            if not window_name:
                window_name = control.window_text() or "Unknown_Window"
            
            # Clean window name for filename
            clean_name = "".join(c for c in window_name if c.isalnum() or c in ('-', '_', ' ')).strip()
            clean_name = clean_name.replace(' ', '_')
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Collect all elements
            elements = []
            
            def collect_element_info(elem, level=0):
                """Recursively collect element information"""
                try:
                    element_info = {
                        "level": level,
                        "class_name": elem.friendly_class_name(),
                        "text": elem.window_text(),
                        "control_id": getattr(elem, 'control_id', lambda: None)(),
                        "enabled": getattr(elem, 'is_enabled', lambda: None)(),
                        "visible": getattr(elem, 'is_visible', lambda: None)(),
                        "rect": str(getattr(elem, 'rectangle', lambda: None)())
                    }
                    elements.append(element_info)
                    
                    # Process children
                    for child in elem.children():
                        collect_element_info(child, level + 1)
                        
                except Exception as e:
                    self.logger.debug(f"Error collecting element info: {e}")
            
            # Start collecting from the main control
            collect_element_info(control)
            
            # Create report structure
            report_data = {
                "window_name": window_name,
                "timestamp": timestamp,
                "total_elements": len(elements),
                "elements": elements
            }
            
            # Save JSON report
            json_filename = f"{clean_name}.json"
            json_path = os.path.join(reports_dir, json_filename)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            # Save human-readable text report
            txt_filename = f"{clean_name}.txt"
            txt_path = os.path.join(reports_dir, txt_filename)
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"Window Report: {window_name}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Elements: {len(elements)}\n")
                f.write("=" * 60 + "\n\n")
                
                for elem in elements:
                    indent = "  " * elem["level"]
                    f.write(f"{indent}├── {elem['class_name']}")
                    if elem['text']:
                        f.write(f": '{elem['text']}'")
                    if elem['control_id']:
                        f.write(f" (ID: {elem['control_id']})")
                    f.write(f" [Enabled: {elem['enabled']}, Visible: {elem['visible']}]")
                    f.write("\n")
            
            self.logger.info(f"Window report generated: {json_path}")
            self.logger.info(f"Human-readable report: {txt_path}")
            
            return report_data
            
        except Exception as e:
            self.logger.error(f"Error generating window report: {e}")
            return None


# Create singleton instance for easy access
ui_utils = UIUtils()

# Backwards compatibility functions for existing code
def print_control_tree(control: UIAWrapper, level: int = 0):
    return ui_utils.print_control_tree(control, level)

def find_control_by_text(control: UIAWrapper, text: str, case_sensitive: bool = False):
    return ui_utils.get_control_by_text(control, text, case_sensitive)

def find_control_by_class(control: UIAWrapper, class_name: str):
    return ui_utils.get_control_by_class(control, class_name)

def generate_window_report(control: UIAWrapper, window_name: str = None, reports_dir: str = "reports"):
    return ui_utils.generate_window_report(control, window_name, reports_dir)