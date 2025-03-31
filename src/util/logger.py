import logging
import os

# Configure the logger
logging.basicConfig(
    level=logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%m-%Y %I:%M:%S %p"  # Custom date format: dd-mm-yyyy hh:mm:ss AM/PM
)

# Create a logger
def getLogger(className):
    return logging.getLogger(className)

