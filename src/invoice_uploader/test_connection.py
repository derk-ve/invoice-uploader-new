import logging
from snelstart_automation import SnelstartAutomation

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        else:
            logger.error("Failed to log in to Snelstart")

        input("\nPress Enter to close Snelstart...")
        snelstart.close()

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()