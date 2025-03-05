import sys
import os
import logging
from loguru import logger

from app.core.config import settings

# Configure loguru logger
class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages toward Loguru.
    
    This handler intercepts all standard logging messages and redirects them to Loguru.
    """
    
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        """
        Emit a log record.

        This method retrieves the appropriate Loguru logging level for the given
        standard logging record. It then finds the originating caller of the log 
        message and redirects the log record to Loguru with the correct level and 
        exception information.

        Args:
            record (logging.LogRecord): The log record to be processed.
        """

        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

# Flag to track if logging has been set up
_logging_initialized = False

def setup_logging():
    """
    Set up logging configuration.
    
    This function configures Loguru and intercepts standard logging messages.
    It sets up a centralized log file for all logs.
    
    The function ensures logging is only set up once to prevent duplicate logs.
    """
    global _logging_initialized
    
    # Only set up logging once
    if _logging_initialized:
        logger.debug("Logging already initialized, skipping setup")
        return
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Remove default loguru handler
    logger.remove()
    
    # Add new handler with custom format for console output
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    
    # Add file handler for all logs (centralized log file)
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        compression="zip",
        retention="30 days",
    )
    
    # Add file handler for errors and above
    logger.add(
        "logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="ERROR",
        rotation="10 MB",
        compression="zip",
        retention="30 days",
    )
    
    # Intercept standard logging messages
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # Intercept uvicorn logging
    for _log in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "streamlit"]:
        _logger = logging.getLogger(_log)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False  # Prevent propagation to avoid duplicate logs
    
    logger.info("[LOGGING] Logging configured successfully")
    
    # Mark logging as initialized
    _logging_initialized = True

# Note: We no longer automatically set up logging when the module is imported
# This will be explicitly called in the FastAPI application