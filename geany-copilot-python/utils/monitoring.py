"""
Advanced monitoring and metrics collection for Geany Copilot Python plugin.

This module provides comprehensive monitoring capabilities including performance
metrics, user behavior analytics, system health monitoring, and secure logging.
"""

import time
import logging
import threading
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricEntry:
    """A single metric entry."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'value': self.value,
            'type': self.metric_type.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags
        }


class PerformanceMonitor:
    """
    Advanced performance monitoring with metrics collection and analysis.
    """
    
    def __init__(self, max_entries: int = 10000, retention_hours: int = 24):
        """
        Initialize the performance monitor.
        
        Args:
            max_entries: Maximum number of metric entries to keep
            retention_hours: How long to retain metrics (in hours)
        """
        self.max_entries = max_entries
        self.retention_hours = retention_hours
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self._metrics: deque = deque(maxlen=max_entries)
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, List[float]] = defaultdict(list)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance tracking
        self._operation_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._success_counts: Dict[str, int] = defaultdict(int)
        
        self.logger.debug("Performance monitor initialized")
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, 
                     tags: Optional[Dict[str, str]] = None):
        """
        Record a metric entry.
        
        Args:
            name: Metric name
            value: Metric value
            metric_type: Type of metric
            tags: Optional tags for the metric
        """
        with self._lock:
            entry = MetricEntry(
                name=name,
                value=value,
                metric_type=metric_type,
                timestamp=datetime.now(),
                tags=tags or {}
            )
            
            self._metrics.append(entry)
            
            # Update type-specific storage
            if metric_type == MetricType.COUNTER:
                self._counters[name] += value
            elif metric_type == MetricType.GAUGE:
                self._gauges[name] = value
            elif metric_type == MetricType.HISTOGRAM:
                self._histograms[name].append(value)
                # Keep only recent values
                if len(self._histograms[name]) > 1000:
                    self._histograms[name] = self._histograms[name][-1000:]
            elif metric_type == MetricType.TIMER:
                self._timers[name].append(value)
                if len(self._timers[name]) > 1000:
                    self._timers[name] = self._timers[name][-1000:]
    
    def increment_counter(self, name: str, value: float = 1.0, 
                         tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        self.record_metric(name, value, MetricType.COUNTER, tags)
    
    def set_gauge(self, name: str, value: float, 
                  tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        self.record_metric(name, value, MetricType.GAUGE, tags)
    
    def record_histogram(self, name: str, value: float, 
                        tags: Optional[Dict[str, str]] = None):
        """Record a histogram value."""
        self.record_metric(name, value, MetricType.HISTOGRAM, tags)
    
    def time_operation(self, operation_name: str):
        """
        Context manager for timing operations.
        
        Usage:
            with monitor.time_operation("api_call"):
                # operation code here
                pass
        """
        return OperationTimer(self, operation_name)
    
    def record_operation_result(self, operation: str, success: bool, 
                              duration: Optional[float] = None):
        """
        Record the result of an operation.
        
        Args:
            operation: Operation name
            success: Whether the operation succeeded
            duration: Operation duration in seconds
        """
        with self._lock:
            if success:
                self._success_counts[operation] += 1
                self.increment_counter(f"{operation}.success")
            else:
                self._error_counts[operation] += 1
                self.increment_counter(f"{operation}.error")
            
            if duration is not None:
                self._operation_times[operation].append(duration)
                self.record_metric(f"{operation}.duration", duration, MetricType.TIMER)
    
    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation."""
        with self._lock:
            times = list(self._operation_times.get(operation, []))
            success_count = self._success_counts.get(operation, 0)
            error_count = self._error_counts.get(operation, 0)
            total_count = success_count + error_count
            
            stats = {
                'operation': operation,
                'total_calls': total_count,
                'success_count': success_count,
                'error_count': error_count,
                'success_rate': success_count / total_count if total_count > 0 else 0,
                'error_rate': error_count / total_count if total_count > 0 else 0
            }
            
            if times:
                stats.update({
                    'avg_duration': sum(times) / len(times),
                    'min_duration': min(times),
                    'max_duration': max(times),
                    'recent_avg_duration': sum(times[-10:]) / min(len(times), 10)
                })
            
            return stats
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        with self._lock:
            return {
                'counters': dict(self._counters),
                'gauges': dict(self._gauges),
                'histograms': {k: list(v) for k, v in self._histograms.items()},
                'timers': {k: list(v) for k, v in self._timers.items()},
                'total_entries': len(self._metrics)
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics."""
        with self._lock:
            operations = set(self._success_counts.keys()) | set(self._error_counts.keys())
            operation_stats = {op: self.get_operation_stats(op) for op in operations}
            
            # Calculate overall statistics
            total_operations = sum(self._success_counts.values()) + sum(self._error_counts.values())
            total_errors = sum(self._error_counts.values())
            overall_error_rate = total_errors / total_operations if total_operations > 0 else 0
            
            return {
                'overall': {
                    'total_operations': total_operations,
                    'total_errors': total_errors,
                    'overall_error_rate': overall_error_rate,
                    'monitored_operations': len(operations)
                },
                'operations': operation_stats,
                'metrics_summary': {
                    'counters': len(self._counters),
                    'gauges': len(self._gauges),
                    'histograms': len(self._histograms),
                    'timers': len(self._timers)
                }
            }
    
    def cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        
        with self._lock:
            # Filter out old metrics
            old_count = len(self._metrics)
            self._metrics = deque(
                (entry for entry in self._metrics if entry.timestamp > cutoff_time),
                maxlen=self.max_entries
            )
            new_count = len(self._metrics)
            
            if old_count != new_count:
                self.logger.debug(f"Cleaned up {old_count - new_count} old metrics")
    
    def export_metrics(self, format: str = "json") -> str:
        """
        Export metrics in the specified format.
        
        Args:
            format: Export format ("json" or "prometheus")
            
        Returns:
            Formatted metrics string
        """
        if format == "json":
            return json.dumps(self.get_all_metrics(), indent=2)
        elif format == "prometheus":
            return self._export_prometheus_format()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        with self._lock:
            # Export counters
            for name, value in self._counters.items():
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name} {value}")
            
            # Export gauges
            for name, value in self._gauges.items():
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name} {value}")
        
        return "\n".join(lines)


class OperationTimer:
    """Context manager for timing operations."""
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None
        self.success = True
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        success = exc_type is None
        self.monitor.record_operation_result(self.operation_name, success, duration)
        return False  # Don't suppress exceptions


class SecureLogger:
    """
    Secure logging utility that prevents sensitive data exposure.
    """
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
        self.sensitive_patterns = [
            r'api[_-]?key',
            r'password',
            r'token',
            r'secret',
            r'auth',
            r'bearer',
        ]
    
    def sanitize_message(self, message: str) -> str:
        """Sanitize log message to remove sensitive information."""
        import re
        
        sanitized = message
        
        # Mask potential API keys and tokens
        for pattern in self.sensitive_patterns:
            # Replace sensitive values with masked versions
            sanitized = re.sub(
                rf'({pattern}["\']?\s*[:=]\s*["\']?)([^"\'\s]+)',
                r'\1***MASKED***',
                sanitized,
                flags=re.IGNORECASE
            )
        
        return sanitized
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message with sanitization."""
        self.logger.debug(self.sanitize_message(message), *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message with sanitization."""
        self.logger.info(self.sanitize_message(message), *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message with sanitization."""
        self.logger.warning(self.sanitize_message(message), *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message with sanitization."""
        self.logger.error(self.sanitize_message(message), *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message with sanitization."""
        self.logger.critical(self.sanitize_message(message), *args, **kwargs)
