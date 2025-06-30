import time
import logging
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto import Desktop

logger = logging.getLogger(__name__)

def click_afschriften_inlezen(window: UIAWrapper):
    """
    Clicks the 'Afschriften Inlezen' button inside the Boekhouden toolbar.

    Args:
        window (UIAWrapper): The administratie window.

    Raises:
        RuntimeError: If the button could not be found or clicked.
    """
    try:
        logger.info("Looking for 'Afschriften Inlezen' button...")

        for ctrl in window.descendants():
            if ctrl.friendly_class_name() == "Button" and ctrl.window_text() == "Afschriften Inlezen":
                logger.info("Found 'Afschriften Inlezen' button. Clicking...")
                ctrl.set_focus()
                ctrl.click_input()
                time.sleep(2)
                return

        raise RuntimeError("'Afschriften Inlezen' button not found")

    except Exception as e:
        logger.error(f"Failed to click 'Afschriften Inlezen': {e}")
        raise RuntimeError("Could not interact with 'Afschriften Inlezen'")