"""
Error handling and recovery utilities for Geany Copilot Python plugin.

This module provides comprehensive error handling, recovery mechanisms,
and graceful degradation capabilities.
"""

import logging
import traceback
import functools
import time
from typing import Any, Callable, Dict, List, Optional, Type, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better handling."""
    NETWORK = "network"
    API = "api"
    UI = "ui"
    MEMORY = "memory"
    CONFIG = "config"
    SECURITY = "security"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """Information about an error occurrence."""
    timestamp: datetime
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    exception_type: str
    traceback_str: str
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_attempted: bool = False
    recovery_successful: bool = False


class ErrorRecoveryManager:
    """
    Manages error recovery strategies and graceful degradation.
    
    Provides automatic retry mechanisms, circuit breaker patterns,
    and fallback strategies for different types of errors.
    """
    
    def __init__(self, max_errors_per_hour: int = 50):
        """
        Initialize the error recovery manager.
        
        Args:
            max_errors_per_hour: Maximum errors allowed per hour before degradation
        """
        self.logger = logging.getLogger(__name__)
        self.max_errors_per_hour = max_errors_per_hour
        self.error_history: List[ErrorInfo] = []
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.degraded_features: set = set()
        
    def record_error(self, error: Exception, category: ErrorCategory = ErrorCategory.UNKNOWN,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                    context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """
        Record an error occurrence.
        
        Args:
            error: The exception that occurred
            category: Category of the error
            severity: Severity level
            context: Additional context information
            
        Returns:
            ErrorInfo object with details about the error
        """
        error_info = ErrorInfo(
            timestamp=datetime.now(),
            category=category,
            severity=severity,
            message=str(error),
            exception_type=type(error).__name__,
            traceback_str=traceback.format_exc(),
            context=context or {}
        )
        
        self.error_history.append(error_info)
        self._cleanup_old_errors()
        
        # Log the error
        log_level = self._get_log_level(severity)
        self.logger.log(log_level, f"Error recorded: {error_info.message}", 
                       extra={'category': category.value, 'severity': severity.value})
        
        # Check if we need to trigger degradation
        self._check_error_threshold()
        
        return error_info
    
    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """Get appropriate log level for error severity."""
        mapping = {
            ErrorSeverity.LOW: logging.DEBUG,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        return mapping.get(severity, logging.ERROR)
    
    def _cleanup_old_errors(self):
        """Remove errors older than 1 hour."""
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.error_history = [e for e in self.error_history if e.timestamp > cutoff_time]
    
    def _check_error_threshold(self):
        """Check if error threshold is exceeded and trigger degradation if needed."""
        recent_errors = len(self.error_history)
        
        if recent_errors > self.max_errors_per_hour:
            self.logger.warning(f"Error threshold exceeded: {recent_errors} errors in the last hour")
            self._trigger_graceful_degradation()
    
    def _trigger_graceful_degradation(self):
        """Trigger graceful degradation of features."""
        # Disable non-essential features
        self.degraded_features.add('streaming')
        self.degraded_features.add('auto_context_analysis')
        self.degraded_features.add('advanced_caching')
        
        self.logger.warning("Graceful degradation activated due to high error rate")
    
    def is_feature_degraded(self, feature: str) -> bool:
        """Check if a feature is currently degraded."""
        return feature in self.degraded_features
    
    def restore_feature(self, feature: str):
        """Restore a degraded feature."""
        self.degraded_features.discard(feature)
        self.logger.info(f"Feature restored: {feature}")
    
    def get_circuit_breaker_state(self, operation: str) -> str:
        """Get the state of a circuit breaker for an operation."""
        breaker = self.circuit_breakers.get(operation, {})
        return breaker.get('state', 'closed')
    
    def trip_circuit_breaker(self, operation: str, timeout_seconds: int = 300):
        """Trip a circuit breaker for an operation."""
        self.circuit_breakers[operation] = {
            'state': 'open',
            'tripped_at': datetime.now(),
            'timeout_seconds': timeout_seconds
        }
        self.logger.warning(f"Circuit breaker tripped for operation: {operation}")
    
    def check_circuit_breaker(self, operation: str) -> bool:
        """Check if a circuit breaker allows the operation."""
        breaker = self.circuit_breakers.get(operation)
        if not breaker or breaker['state'] == 'closed':
            return True
        
        # Check if timeout has passed
        if datetime.now() - breaker['tripped_at'] > timedelta(seconds=breaker['timeout_seconds']):
            # Reset circuit breaker
            breaker['state'] = 'half-open'
            self.logger.info(f"Circuit breaker reset to half-open: {operation}")
            return True
        
        return False
    
    def reset_circuit_breaker(self, operation: str):
        """Reset a circuit breaker after successful operation."""
        if operation in self.circuit_breakers:
            self.circuit_breakers[operation]['state'] = 'closed'
            self.logger.info(f"Circuit breaker reset: {operation}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        total_errors = len(self.error_history)
        
        # Count by category
        category_counts = {}
        severity_counts = {}
        
        for error in self.error_history:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        return {
            'total_errors': total_errors,
            'errors_per_hour': total_errors,  # Already filtered to last hour
            'category_breakdown': category_counts,
            'severity_breakdown': severity_counts,
            'degraded_features': list(self.degraded_features),
            'circuit_breakers': {op: state['state'] for op, state in self.circuit_breakers.items()}
        }


def with_error_handling(category: ErrorCategory = ErrorCategory.UNKNOWN,
                       severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                       retry_count: int = 0,
                       retry_delay: float = 1.0,
                       fallback_value: Any = None,
                       circuit_breaker: Optional[str] = None):
    """
    Decorator for comprehensive error handling with retry and circuit breaker support.
    
    Args:
        category: Error category
        severity: Error severity
        retry_count: Number of retries to attempt
        retry_delay: Delay between retries in seconds
        fallback_value: Value to return if all retries fail
        circuit_breaker: Name of circuit breaker to check/trip
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get error manager from first argument if it's available
            error_manager = None
            if args and hasattr(args[0], 'error_manager'):
                error_manager = args[0].error_manager
            elif args and hasattr(args[0], '_error_manager'):
                error_manager = args[0]._error_manager
            
            # Check circuit breaker if specified
            if circuit_breaker and error_manager:
                if not error_manager.check_circuit_breaker(circuit_breaker):
                    logger = logging.getLogger(func.__module__)
                    logger.warning(f"Circuit breaker open for {circuit_breaker}, returning fallback")
                    return fallback_value
            
            last_exception = None
            
            for attempt in range(retry_count + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Reset circuit breaker on success
                    if circuit_breaker and error_manager and attempt > 0:
                        error_manager.reset_circuit_breaker(circuit_breaker)
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Record error if error manager is available
                    if error_manager:
                        context = {
                            'function': func.__name__,
                            'attempt': attempt + 1,
                            'max_attempts': retry_count + 1
                        }
                        error_manager.record_error(e, category, severity, context)
                    
                    # If this is the last attempt, break
                    if attempt == retry_count:
                        break
                    
                    # Wait before retry
                    if retry_delay > 0:
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            
            # All retries failed
            if circuit_breaker and error_manager:
                error_manager.trip_circuit_breaker(circuit_breaker)
            
            # Log final failure
            logger = logging.getLogger(func.__module__)
            logger.error(f"Function {func.__name__} failed after {retry_count + 1} attempts: {last_exception}")
            
            # Return fallback value or re-raise exception
            if fallback_value is not None:
                return fallback_value
            else:
                raise last_exception
        
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, fallback_value: Any = None, 
                log_errors: bool = True, **kwargs) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        fallback_value: Value to return on error
        log_errors: Whether to log errors
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or fallback value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger = logging.getLogger(func.__module__ if hasattr(func, '__module__') else __name__)
            logger.error(f"Error in safe_execute for {func.__name__ if hasattr(func, '__name__') else str(func)}: {e}")
        return fallback_value
