import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """Configures and returns a standard logger instance."""
    logger = logging.getLogger(name)
    
    # This will prevent adding duplicate handlers if the logger is called multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Stream handler to output logs to the terminal/console
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)-8s - %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger