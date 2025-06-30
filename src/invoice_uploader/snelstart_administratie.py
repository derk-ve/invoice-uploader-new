from pywinauto import Desktop

import time
import logging
from pywinauto.controls.uiawrapper import UIAWrapper

# Logging setup
logger = logging.getLogger(__name__)
    
def get_administratie_window(window: UIAWrapper):
    """
    Double-clicks 'Row 1' to open the administratie window.

    Args:
        window (UIAWrapper): The main administratie view window.

    Returns:
        None

    Raises:
        RuntimeError: If the row could not be found or clicked.
    """
    try:
        for ctrl in window.descendants():
            if ctrl.friendly_class_name() == "Custom" and ctrl.window_text() == "Row 1":
                ctrl.set_focus()
                ctrl.double_click_input()
                logger.info("Double-clicked row 1 to open administratie.")
                time.sleep(5)
                return
        raise RuntimeError("Row 1 not found in administratie view")
    except Exception as e:
        logger.error(f"Failed to open administratie: {e}")
        raise RuntimeError("Could not open administratie window")




    


