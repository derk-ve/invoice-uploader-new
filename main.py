import time
from src.invoice_uploader.snelstart_automation import SnelstartAutomation
from src.utils.logging_setup import setup_logging, get_logger
from dotenv import load_dotenv

load_dotenv()

# Setup logging
setup_logging()
logger = get_logger(__name__)

def main():
    try:
        print('\n')
        snelstart = initialize_snelstart()
        if not snelstart:
            return
        time.sleep(2)
        print('\n')

        if not perform_login(snelstart):
            return
        time.sleep(5)
        print('\n')

        if not open_administratie(snelstart):
            return
        time.sleep(2)
        print('\n')

        if not upload_afschriften(snelstart):
            return
        time.sleep(2)
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


def open_administratie(snelstart: SnelstartAutomation):
    logger.info("Opening Administratie window...")
    if snelstart.open_administratie():
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