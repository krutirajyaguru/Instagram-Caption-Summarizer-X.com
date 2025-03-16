import logging
import os
from datetime import datetime

def setup_logging(log_dir="/app/logs"):
    """Sets up logging to output logs to a file in the specified directory."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"log_{datetime.today().strftime('%Y-%m-%d')}.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logging.info("Logging is set up.")
