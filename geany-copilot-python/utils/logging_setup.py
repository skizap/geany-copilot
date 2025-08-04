"""
Advanced logging setup for Geany Copilot Python plugin.

This module provides centralized logging configuration with monitoring,
performance tracking, and secure logging capabilities.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

from .monitoring import PerformanceMonitor, SecureLogger


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


def setup_monitored_logging(debug: bool = False,
                           enable_monitoring: bool = True) -> tuple[logging.Logger, Optional[PerformanceMonitor]]:
    """
    Setup logging with integrated performance monitoring.

    Args:
        debug: Whether to enable debug logging
        enable_monitoring: Whether to enable performance monitoring

    Returns:
        Tuple of (logger, performance_monitor)
    """
    # Setup basic logging
    logger = setup_plugin_logging(debug)

    # Setup performance monitoring
    monitor = None
    if enable_monitoring:
        monitor = PerformanceMonitor()

        # Add monitoring handler to logger
        monitoring_handler = MonitoringLogHandler(monitor)
        monitoring_handler.setLevel(logging.WARNING)  # Monitor warnings and errors
        logger.addHandler(monitoring_handler)

        logger.info("Performance monitoring enabled")

    return logger, monitor


def get_secure_logger(name: str) -> SecureLogger:
    """
    Get a secure logger that automatically sanitizes sensitive data.

    Args:
        name: Logger name

    Returns:
        SecureLogger instance
    """
    return SecureLogger(name)


class MonitoringLogHandler(logging.Handler):
    """
    Custom log handler that feeds log events to the performance monitor.
    """

    def __init__(self, monitor: PerformanceMonitor):
        super().__init__()
        self.monitor = monitor

    def emit(self, record: logging.LogRecord):
        """Process a log record and update monitoring metrics."""
        try:
            # Count log events by level
            level_name = record.levelname.lower()
            self.monitor.increment_counter(f"log.{level_name}")

            # Track errors and warnings
            if record.levelno >= logging.ERROR:
                self.monitor.increment_counter("log.errors")

                # Extract operation name from logger name if possible
                logger_parts = record.name.split('.')
                if len(logger_parts) > 1:
                    operation = logger_parts[-1]
                    self.monitor.record_operation_result(operation, False)

            elif record.levelno >= logging.WARNING:
                self.monitor.increment_counter("log.warnings")

        except Exception:
            # Don't let monitoring errors break logging
            pass


class PerformanceLogFilter(logging.Filter):
    """
    Log filter that adds performance context to log records.
    """

    def __init__(self, monitor: PerformanceMonitor):
        super().__init__()
        self.monitor = monitor

    def filter(self, record: logging.LogRecord) -> bool:
        """Add performance context to log records."""
        try:
            # Add performance metrics to log record
            stats = self.monitor.get_performance_summary()
            record.performance_context = {
                'total_operations': stats['overall']['total_operations'],
                'error_rate': stats['overall']['overall_error_rate']
            }
        except Exception:
            # Don't break logging if monitoring fails
            record.performance_context = {}

        return True


def setup_advanced_logging(debug: bool = False,
                          log_file: Optional[str] = None,
                          enable_monitoring: bool = True,
                          enable_rotation: bool = True) -> tuple[logging.Logger, Optional[PerformanceMonitor]]:
    """
    Setup advanced logging with all features enabled.

    Args:
        debug: Whether to enable debug logging
        log_file: Optional custom log file path
        enable_monitoring: Whether to enable performance monitoring
        enable_rotation: Whether to enable log rotation

    Returns:
        Tuple of (logger, performance_monitor)
    """
    log_level = "DEBUG" if debug else "INFO"
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    if log_file is None:
        log_file = get_default_log_file()

    # Create logger
    logger = logging.getLogger("geany_copilot_python")
    logger.setLevel(numeric_level)
    logger.handlers.clear()

    # Setup performance monitoring
    monitor = None
    if enable_monitoring:
        monitor = PerformanceMonitor()

    # Enhanced formatter with performance context
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            if enable_rotation:
                # Use rotating file handler
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5
                )
            else:
                file_handler = logging.FileHandler(log_file)

            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)

            # Add performance filter if monitoring is enabled
            if monitor:
                perf_filter = PerformanceLogFilter(monitor)
                file_handler.addFilter(perf_filter)

            logger.addHandler(file_handler)
            logger.info(f"Advanced logging to file: {log_file}")

        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")

    # Add monitoring handler
    if monitor:
        monitoring_handler = MonitoringLogHandler(monitor)
        monitoring_handler.setLevel(logging.WARNING)
        logger.addHandler(monitoring_handler)
        logger.info("Performance monitoring enabled")

    logger.info(f"Advanced logging initialized at level: {log_level}")
    return logger, monitor
