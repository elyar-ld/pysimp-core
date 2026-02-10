
import sys
from loguru import logger

def setup_logger():
    """
    Configures and returns a Loguru logger instance.
    """
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    return logger
