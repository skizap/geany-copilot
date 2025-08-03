"""
Logging setup for Geany Copilot Python plugin.

This module provides centralized logging configuration for the plugin.
"""

import logging
import os
from pathlib import Path
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup logging for the plugin.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("geany_copilot_python")
    logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        try:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            logger.info(f"Logging to file: {log_file}")
            
        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")
    
    logger.info(f"Logging initialized at level: {log_level}")
    return logger


def get_default_log_file() -> str:
    """
    Get the default log file path.
    
    Returns:
        Default log file path
    """
    try:
        # Try to get Geany's config directory
        import geany
        if hasattr(geany, 'app') and hasattr(geany.app, 'configdir'):
            base_dir = Path(geany.app.configdir)
        else:
            base_dir = Path.home() / ".config" / "geany"
    except ImportError:
        # Fallback when not running in Geany
        base_dir = Path.home() / ".config" / "geany"
    
    log_dir = base_dir / "plugins" / "geanylua" / "geany-copilot-python" / "logs"
    return str(log_dir / "geany-copilot-python.log")


def setup_plugin_logging(debug: bool = False) -> logging.Logger:
    """
    Setup logging specifically for the plugin with default settings.
    
    Args:
        debug: Whether to enable debug logging
        
    Returns:
        Configured logger instance
    """
    log_level = "DEBUG" if debug else "INFO"
    log_file = get_default_log_file()
    
    return setup_logging(log_level, log_file)
