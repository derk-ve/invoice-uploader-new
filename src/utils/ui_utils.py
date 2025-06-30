import logging
import json
import os
from datetime import datetime
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


def generate_window_report(control: UIAWrapper, window_name: str = None, reports_dir: str = "reports"):
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
                logger.debug(f"Error collecting element info: {e}")
        
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
        
        logger.info(f"Window report generated: {json_path}")
        logger.info(f"Human-readable report: {txt_path}")
        
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating window report: {e}")
        return None 