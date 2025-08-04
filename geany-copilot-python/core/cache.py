"""
Caching and performance optimization module for Geany Copilot Python Plugin.

This module provides intelligent caching, request debouncing, and memory optimization
to improve plugin performance and reduce API calls.
"""

import time
import hashlib
import threading
import logging
from typing import Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from collections import OrderedDict
import weakref
import gc


logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """A cache entry with metadata."""
    value: Any
    timestamp: float
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    size_bytes: int = 0
    
    def __post_init__(self):
        """Calculate approximate size of the cached value."""
        self.size_bytes = self._calculate_size(self.value)
    
    def _calculate_size(self, obj: Any) -> int:
        """Estimate the size of an object in bytes."""
        try:
            if isinstance(obj, str):
                return len(obj.encode('utf-8'))
            elif isinstance(obj, (int, float)):
                return 8
            elif isinstance(obj, (list, tuple)):
                return sum(self._calculate_size(item) for item in obj)
            elif isinstance(obj, dict):
                return sum(self._calculate_size(k) + self._calculate_size(v) 
                          for k, v in obj.items())
            else:
                # Rough estimate for other objects
                return len(str(obj)) * 2
        except Exception:
            return 100  # Default estimate
    
    def is_expired(self, ttl: float) -> bool:
        """Check if the cache entry has expired."""
        return time.time() - self.timestamp > ttl
    
    def touch(self):
        """Update access information."""
        self.access_count += 1
        self.last_access = time.time()


class LRUCache:
    """
    Least Recently Used cache with size and TTL limits.
    
    Features:
    - Size-based eviction
    - Time-based expiration
    - Access frequency tracking
    - Memory usage monitoring
    """
    
    def __init__(self, 
                 max_size: int = 100,
                 max_memory_mb: float = 50.0,
                 default_ttl: float = 3600.0):  # 1 hour
        self.max_size = max_size
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self.default_ttl = default_ttl
        
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._total_size = 0
        
        logger.debug(f"Initialized LRU cache: max_size={max_size}, "
                    f"max_memory={max_memory_mb}MB, ttl={default_ttl}s")
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired(self.default_ttl):
                self._remove_entry(key)
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.touch()
            
            logger.debug(f"Cache hit: {key} (access_count={entry.access_count})")
            return entry.value
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Put a value in the cache."""
        if ttl is None:
            ttl = self.default_ttl
        
        with self._lock:
            # Create new entry
            entry = CacheEntry(
                value=value,
                timestamp=time.time()
            )
            
            # Check if adding this entry would exceed memory limit
            if entry.size_bytes > self.max_memory_bytes:
                logger.warning(f"Entry too large for cache: {entry.size_bytes} bytes")
                return False
            
            # Remove existing entry if present
            if key in self._cache:
                self._remove_entry(key)
            
            # Ensure we have space
            while (len(self._cache) >= self.max_size or 
                   self._total_size + entry.size_bytes > self.max_memory_bytes):
                if not self._evict_lru():
                    logger.warning("Could not make space in cache")
                    return False
            
            # Add new entry
            self._cache[key] = entry
            self._total_size += entry.size_bytes
            
            logger.debug(f"Cache put: {key} ({entry.size_bytes} bytes, "
                        f"total: {self._total_size} bytes)")
            return True
    
    def _remove_entry(self, key: str):
        """Remove an entry from the cache."""
        if key in self._cache:
            entry = self._cache.pop(key)
            self._total_size -= entry.size_bytes
            logger.debug(f"Cache remove: {key}")
    
    def _evict_lru(self) -> bool:
        """Evict the least recently used entry."""
        if not self._cache:
            return False
        
        # Get the least recently used key (first in OrderedDict)
        lru_key = next(iter(self._cache))
        self._remove_entry(lru_key)
        logger.debug(f"Cache evict LRU: {lru_key}")
        return True
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._total_size = 0
            logger.debug("Cache cleared")
    
    def cleanup_expired(self):
        """Remove expired entries."""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired(self.default_ttl):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_entry(key)
            
            if expired_keys:
                logger.debug(f"Cache cleanup: removed {len(expired_keys)} expired entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'memory_usage_bytes': self._total_size,
                'memory_usage_mb': self._total_size / (1024 * 1024),
                'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
                'memory_utilization': self._total_size / self.max_memory_bytes if self.max_memory_bytes > 0 else 0
            }


class RequestDebouncer:
    """
    Request debouncer to prevent excessive API calls.
    
    Delays execution of functions until after a specified delay has passed
    since the last time it was invoked.
    """
    
    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self._timers: Dict[str, threading.Timer] = {}
        self._lock = threading.Lock()
    
    def debounce(self, key: str, func: Callable, *args, **kwargs):
        """Debounce a function call."""
        with self._lock:
            # Cancel existing timer for this key
            if key in self._timers:
                self._timers[key].cancel()
            
            # Create new timer
            timer = threading.Timer(self.delay, func, args, kwargs)
            self._timers[key] = timer
            timer.start()
            
            logger.debug(f"Debounced call: {key} (delay={self.delay}s)")
    
    def cancel(self, key: str):
        """Cancel a debounced call."""
        with self._lock:
            if key in self._timers:
                self._timers[key].cancel()
                del self._timers[key]
                logger.debug(f"Cancelled debounced call: {key}")
    
    def cancel_all(self):
        """Cancel all debounced calls."""
        with self._lock:
            for timer in self._timers.values():
                timer.cancel()
            self._timers.clear()
            logger.debug("Cancelled all debounced calls")


class MemoryOptimizer:
    """
    Memory optimization utilities.
    
    Provides methods to monitor and optimize memory usage.
    """
    
    def __init__(self):
        self._weak_refs: weakref.WeakSet = weakref.WeakSet()
    
    def register_object(self, obj: Any):
        """Register an object for memory monitoring."""
        try:
            self._weak_refs.add(obj)
        except TypeError:
            # Object is not weakly referenceable
            pass
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        import psutil
        import os
        
        try:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / (1024 * 1024),  # Resident Set Size
                'vms_mb': memory_info.vms / (1024 * 1024),  # Virtual Memory Size
                'percent': process.memory_percent(),
                'registered_objects': len(self._weak_refs)
            }
        except ImportError:
            # psutil not available
            return {
                'registered_objects': len(self._weak_refs)
            }
    
    def force_garbage_collection(self):
        """Force garbage collection."""
        collected = gc.collect()
        logger.debug(f"Garbage collection: collected {collected} objects")
        return collected
    
    def optimize_memory(self):
        """Perform memory optimization."""
        # Force garbage collection
        collected = self.force_garbage_collection()
        
        # Get memory stats
        memory_stats = self.get_memory_usage()
        
        logger.info(f"Memory optimization: collected {collected} objects, "
                   f"RSS: {memory_stats.get('rss_mb', 0):.1f}MB")
        
        return memory_stats


class PerformanceManager:
    """
    Main performance management class that coordinates caching, debouncing,
    and memory optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the performance manager."""
        config = config or {}
        
        # Cache configuration
        cache_config = config.get('cache', {})
        self.response_cache = LRUCache(
            max_size=cache_config.get('max_size', 100),
            max_memory_mb=cache_config.get('max_memory_mb', 50.0),
            default_ttl=cache_config.get('ttl', 3600.0)
        )
        
        # Debouncer configuration
        debounce_config = config.get('debounce', {})
        self.debouncer = RequestDebouncer(
            delay=debounce_config.get('delay', 0.5)
        )
        
        # Memory optimizer
        self.memory_optimizer = MemoryOptimizer()
        
        # Performance monitoring
        self._start_time = time.time()
        self._request_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        
        logger.info("Performance manager initialized")
    
    def cache_response(self, key: str, response: Any, ttl: Optional[float] = None) -> bool:
        """Cache an API response."""
        success = self.response_cache.put(key, response, ttl)
        if success:
            logger.debug(f"Cached response: {key}")
        return success
    
    def get_cached_response(self, key: str) -> Optional[Any]:
        """Get a cached API response."""
        response = self.response_cache.get(key)
        if response is not None:
            self._cache_hits += 1
            logger.debug(f"Cache hit: {key}")
        else:
            self._cache_misses += 1
            logger.debug(f"Cache miss: {key}")
        return response
    
    def generate_cache_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        # Create a string representation of all arguments
        key_data = str(args) + str(sorted(kwargs.items()))
        
        # Hash the key data to create a consistent key
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def debounce_request(self, key: str, func: Callable, *args, **kwargs):
        """Debounce a request."""
        self.debouncer.debounce(key, func, *args, **kwargs)
    
    def cleanup(self):
        """Cleanup resources."""
        self.response_cache.cleanup_expired()
        self.debouncer.cancel_all()
        self.memory_optimizer.optimize_memory()
        logger.info("Performance manager cleanup completed")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        uptime = time.time() - self._start_time
        cache_stats = self.response_cache.get_stats()
        memory_stats = self.memory_optimizer.get_memory_usage()
        
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests) if total_requests > 0 else 0
        
        return {
            'uptime_seconds': uptime,
            'total_requests': total_requests,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'cache_hit_rate': hit_rate,
            'cache_stats': cache_stats,
            'memory_stats': memory_stats
        }
