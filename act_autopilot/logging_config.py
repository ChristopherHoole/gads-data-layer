"""
Centralized logging configuration for Ads Control Tower.

Usage:
    from act_autopilot.logging_config import setup_logging
    
    logger = setup_logging(__name__)
    logger.info("Normal operation")
    logger.warning("Potential issue")
    logger.error("Failure")
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(
    module_name: str,
    log_level: str = "INFO",
    log_dir: str = "logs",
    console_output: bool = True
) -> logging.Logger:
    """
    Set up logging for a module with both file and console output.
    
    Args:
        module_name: Name of the module (use __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files (default: logs/)
        console_output: Whether to output to console (default: True)
    
    Returns:
        Configured logger instance
    
    Log Levels:
        DEBUG: Detailed execution flow (disabled by default)
        INFO: Normal operations (rule firing, API calls, changes)
        WARNING: Potential issues (low data, cooldown blocks, guardrail violations)
        ERROR: Failures (API errors, invalid configs, crashes)
    
    Log Files:
        Format: logs/{module}_{date}.log
        Example: logs/autopilot_2026-02-14.log
        Rotation: Daily (new file each day)
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(module_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate handlers if setup_logging called multiple times
    if logger.handlers:
        return logger
    
    # Format for log messages
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler - daily rotation
    today = datetime.now().strftime("%Y-%m-%d")
    simple_module = module_name.split('.')[-1]  # Get last part of module name
    log_file = log_path / f"{simple_module}_{today}.log"
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler (optional)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(module_name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.
    
    Args:
        module_name: Name of the module (use __name__)
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(module_name)
    
    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        return setup_logging(module_name)
    
    return logger


# Convenience function for quick setup
def init_logging(log_level: str = "INFO") -> None:
    """
    Initialize root logger for the entire application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    setup_logging("act_autopilot", log_level=log_level)
