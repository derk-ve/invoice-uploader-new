from ..snelstart_automation import SnelstartAutomation
from ...utils.logging_setup import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

def main():
    try:
        # Create Snelstart automation instance
        snelstart = SnelstartAutomation()
        
        # Start Snelstart and get the main window
        logger.info("Starting Snelstart...")
        if not snelstart.start():
            logger.error("Failed to start Snelstart")
            return
        
        # Print control tree for debugging
        logger.info("Printing control tree...")
        snelstart.print_control_tree()
        
        # Attempt login
        logger.info("Attempting login...")
        if snelstart.login():
            logger.info("Successfully connected and logged in to Snelstart")
            
            # Test opening administration window
            logger.info("Opening administration window...")
            if snelstart.open_administratie():
                logger.info("Successfully opened administration window")
            else:
                logger.error("Failed to open administration window")

        else:
            logger.error("Failed to log in to Snelstart")

        input("\nPress Enter to close Snelstart...")
        snelstart.close()

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()