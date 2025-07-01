import time
from src.invoice_uploader.snelstart_automation import SnelstartAutomation
from src.utils.logging_setup import LoggingSetup
from src.utils.wait_utils import wait_with_timeout, WaitTimeoutError
from dotenv import load_dotenv

load_dotenv()

# Setup logging
LoggingSetup.setup_logging()
logger = LoggingSetup.get_logger(__name__)

def wait_for_step_ready(step_name, timeout=5):
    """Wait for application to stabilize after a step."""
    def check_ready():
        # Simple readiness check - in a real scenario, this could check for UI elements, etc.
        # For now, we'll just do a shorter wait with feedback
        return True
    
    try:
        wait_with_timeout(check_ready, timeout=timeout, interval=1, 
                         description=f"{step_name} stabilization", provide_feedback=False)
    except WaitTimeoutError:
        logger.warning(f"Timeout waiting for {step_name} to stabilize")

def main():
    try:
        print('\n')
        snelstart = initialize_snelstart()
        if not snelstart:
            return
        wait_for_step_ready("application startup", timeout=3)
        print('\n')

        if not perform_login(snelstart):
            return
        wait_for_step_ready("login completion", timeout=3)
        print('\n')

        if not open_bookkeeping(snelstart):
            return
        wait_for_step_ready("administration opening", timeout=2)
        print('\n')

        if not upload_afschriften(snelstart):
            return
        wait_for_step_ready("afschriften upload", timeout=2)
        print('\n')

        logger.info("Waiting for user to exit...")
        wait_for_user_exit(snelstart)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

def initialize_snelstart():
    logger.info("Starting Snelstart...")
    snelstart = SnelstartAutomation()
    if not snelstart.start():
        logger.error("Failed to start Snelstart")
        return None
    return snelstart


def perform_login(snelstart: SnelstartAutomation):
    logger.info("Attempting login...")
    if snelstart.login():
        logger.info("Successfully logged in to Snelstart")
        return True
    logger.error("Failed to log in to Snelstart")
    return False


def open_bookkeeping(snelstart: SnelstartAutomation):
    logger.info("Opening Administratie window...")
    if snelstart.open_bookkeeping():
        logger.info("Administratie window opened")
        return True
    logger.error("Failed to open Administratie window")
    return False

def upload_afschriften(snelstart: SnelstartAutomation):
    logger.info("Uploading Afschriften...")
    if snelstart.load_in_afschriften():
        logger.info("Successfully uploaded afschriften")
        snelstart.print_control_tree(snelstart.admin_window)
        return True
    logger.error("Failed to upload afschriften")
    return False


def wait_for_user_exit(snelstart: SnelstartAutomation):
    input("\nPress Enter to close Snelstart...")
    snelstart.close()



if __name__ == "__main__":
    main()