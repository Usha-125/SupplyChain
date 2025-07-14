import logging
import os

# Get the root directory of the project (SupplyChain-main)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Define correct path for the actual log file at root level
LOG_FILE_PATH = os.path.join(BASE_DIR, "app.log")

# Set up the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
