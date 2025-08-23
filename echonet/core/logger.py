import sys

import loguru

from echonet.core.paths import LOG_FILE

# Assign the loguru logger to a variable
logger = loguru.logger

# Remove any default handlers
logger.remove()

# Console sink (minimal format: time only)
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    colorize=True,
    level="DEBUG",
    enqueue=True,
)

# File sink (full details for history)
logger.add(
    LOG_FILE,
    format="{time:YYYY-MM-DD} | {time:HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}",
    rotation="10 MB",
    retention="14 days",
    compression="zip",
    level="DEBUG",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,  # Better tracebacks in files
    diagnose=True,  # Adds variables to stack traces
)

# Optionally integrate Rich's pretty tracebacks for CLI tools
try:
    from rich.traceback import install

    install(show_locals=True)
except ImportError:
    pass


# Shortcut function to get logger in other modules
def get_logger() -> "loguru.Logger":
    """
    Returns the core logger
    """
    return logger
