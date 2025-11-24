# In-built packages (Standard Library modules)
import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# External packages
from colorlog import ColoredFormatter
from pythonjsonlogger.json import JsonFormatter

# Our Own Imports


# Directory where all log files will be stored.
# Path("logs") means ./logs directory relative to project root.
LOG_DIR = Path("logs")

# Create the directory if it doesn't exist
LOG_DIR.mkdir(exist_ok = True)


# ------------------------------------------------------------
# Helper function: extract only the filename from __file__
# ------------------------------------------------------------
def _extract_module_name(file_path : str) -> str:
    """
    Extracts the module name from a file path.
    
    Example:
        file_path → "/project/app/users.py"
        return    → "users"
    
    Why this is useful:
    - Allows each Python file (users.py, payments.py, auth.py)
      to automatically create its own logger and its own log file.
    """
    return os.path.splitext(os.path.basename(file_path))[0]


# ------------------------------------------------------------
# Helper function: create a rotating JSONL log handler
# ------------------------------------------------------------
def _get_rotating_jsonl_handler(log_path : Path):
    """
    Creates a rotating log file handler that writes logs in JSON Lines format.
    
    What is JSONL?
    - Each log entry is one valid JSON object per line.
    - Great for machine parsing, log analysis, ELK, Datadog, etc.
    
    RotatingFileHandler:
    - Automatically rotates logs when file grows too large.
    - Prevents disk from filling up.
    
    backupCount = 5:
    - Keeps last 5 rotated log files.
    """
    
    # Creates a file handler that rotates after 5 MB
    handler = RotatingFileHandler(log_path, 
        maxBytes = 5 * 1024 * 1024,  # 5 MB
        backupCount = 5,             # keep 5 backups
        encoding = "utf-8"
    )
    
    # JSON formatter for structured logs
    formatter = JsonFormatter(
        fmt = (
            "%(asctime)s %(levelname)s %(module)s "
            "%(filename)s %(funcName)s %(lineno)d %(message)s"
        ), 
        datefmt = "%Y-%m-%d %H:%M:%S"  # Example: 2025-11-24 21:11:28
    )
    
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)  # Log everything (DEBUG → CRITICAL)
    
    return handler


# ------------------------------------------------------------
# Helper function: create colored console logs for readability
# ------------------------------------------------------------
def _get_colored_console_handler():
    """
    Creates a StreamHandler that outputs beautiful colored logs to the terminal.
    
    Why color?
    - Makes debugging easier.
    - Common industry practice (Django, Flask, FastAPI dev servers do similar).
    
    Example console output:
        [24-Nov-2025 21:11:28] [INFO    ] users.py:45 - Server started
    """
    
    console_formatter = ColoredFormatter(
        fmt = (
            "%(log_color)s[%(asctime)s] "
            "[%(levelname)-8s]%(reset)s "
            "%(cyan)s%(filename)s:%(lineno)d%(reset)s - "
            "%(bold_white)s%(message)s"
        ), 
        datefmt = "%d-%b-%Y %H:%M:%S",  # Example: 24-Nov-2025 21:11:28
        log_colors = {
            "DEBUG" : "blue", 
            "INFO" : "green", 
            "WARNING" : "yellow", 
            "ERROR" : "red", 
            "CRITICAL" : "bold_red"
        }, 
        style = "%"  # Python default printf-like formatting
    )
    
    handler = logging.StreamHandler()  # Sends logs to terminal (stdout)
    handler.setFormatter(console_formatter)
    handler.setLevel(logging.INFO)     # Only show >= INFO to keep console clean
    
    return handler


# ------------------------------------------------------------
# Public API: the function developers will use
# ------------------------------------------------------------
def get_logger(file_path : str):
    """
    Creates a customized logger for a specific module (file).
    
    How to use:
        logger = get_logger(__file__)
        
    What this provides:
        ✔ Colored logs in terminal
        ✔ One central app.jsonl file
        ✔ One per-module JSONL file (users.jsonl, auth.jsonl, etc.)
        ✔ Rotating logs so disk never fills
        ✔ JSON structured logs for readability + analytics
        
    Logging Levels:
        DEBUG    (most verbose)
        INFO
        WARNING
        ERROR
        CRITICAL (most severe)
    """
    
    # Extract the short module name from the file path (e.g., "users")
    module_name = _extract_module_name(file_path)
    
    # Create a logger object with that module name
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)   # Capture all logs
    logger.propagate = False         # Prevent duplicate logs
    
    # If logger already has handlers (e.g., FastAPI auto-imports modules),
    # return immediately to avoid adding duplicate handlers.
    if logger.handlers:
        return logger
    
    # -------------------------------------
    # 1. Add central application log (app.jsonl)
    # -------------------------------------
    logger.addHandler(_get_rotating_jsonl_handler(LOG_DIR / "app.jsonl"))
    
    # -------------------------------------
    # 2. Add module-specific log (users.jsonl, auth.jsonl, etc.)
    # -------------------------------------
    logger.addHandler(_get_rotating_jsonl_handler(LOG_DIR / f"{module_name}.jsonl"))
    
    # -------------------------------------
    # 3. Add colored terminal output
    # -------------------------------------
    logger.addHandler(_get_colored_console_handler())
    
    return logger