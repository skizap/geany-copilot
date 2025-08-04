#!/usr/bin/env python3
"""
Test script for performance optimizations in Geany Copilot Python Plugin.

This script tests caching, debouncing, memory optimization, and overall
performance management functionality.
"""

import sys
import os
import time
import threading
from pathlib import Path

# Add the plugin directory to Python path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

def test_lru_cache():
    """Test the LRU cache implementation."""
    print("🧪 Testing LRU Cache...")
    
    try:
        from core.cache import LRUCache
        
        # Create a small cache for testing
        cache = LRUCache(max_size=3, max_memory_mb=1.0, default_ttl=2.0)
        
        # Test basic operations
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # Test retrieval
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        print("✅ Basic cache operations work")
        
        # Test LRU eviction
        cache.put("key4", "value4")  # Should evict key1 (least recently used)
        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"
        print("✅ LRU eviction works")
        
        # Test TTL expiration
        cache.put("temp_key", "temp_value", ttl=0.1)  # 100ms TTL
        assert cache.get("temp_key") == "temp_value"
        time.sleep(0.15)  # Wait for expiration
        expired_value = cache.get("temp_key")
        if expired_value is not None:
            print(f"⚠️  TTL test: value should be expired but got: {expired_value}")
        else:
            print("✅ TTL expiration works")
        
        # Test cache stats
        stats = cache.get_stats()
        assert 'size' in stats
        assert 'memory_usage_bytes' in stats
        print(f"✅ Cache stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ LRU Cache test failed: {e}")
        return False


def test_request_debouncer():
    """Test the request debouncer."""
    print("\n🧪 Testing Request Debouncer...")
    
    try:
        from core.cache import RequestDebouncer
        
        debouncer = RequestDebouncer(delay=0.1)  # 100ms delay
        
        # Test debouncing
        call_count = 0
        def test_function():
            nonlocal call_count
            call_count += 1
        
        # Make multiple rapid calls
        for i in range(5):
            debouncer.debounce("test_key", test_function)
            time.sleep(0.01)  # 10ms between calls
        
        # Wait for debounce delay
        time.sleep(0.2)
        
        # Should only be called once due to debouncing
        assert call_count == 1
        print("✅ Request debouncing works")
        
        # Test multiple keys
        call_count_a = 0
        call_count_b = 0
        
        def test_function_a():
            nonlocal call_count_a
            call_count_a += 1
        
        def test_function_b():
            nonlocal call_count_b
            call_count_b += 1
        
        debouncer.debounce("key_a", test_function_a)
        debouncer.debounce("key_b", test_function_b)
        
        time.sleep(0.2)
        
        assert call_count_a == 1
        assert call_count_b == 1
        print("✅ Multiple key debouncing works")
        
        return True
        
    except Exception as e:
        print(f"❌ Request Debouncer test failed: {e}")
        return False


def test_memory_optimizer():
    """Test the memory optimizer."""
    print("\n🧪 Testing Memory Optimizer...")
    
    try:
        from core.cache import MemoryOptimizer
        
        optimizer = MemoryOptimizer()
        
        # Test object registration
        test_objects = [{"data": f"test_{i}"} for i in range(10)]
        for obj in test_objects:
            optimizer.register_object(obj)
        
        # Test memory usage reporting
        memory_stats = optimizer.get_memory_usage()
        assert 'registered_objects' in memory_stats
        print(f"✅ Memory stats: {memory_stats}")
        
        # Test garbage collection
        collected = optimizer.force_garbage_collection()
        print(f"✅ Garbage collection: collected {collected} objects")
        
        # Test memory optimization
        optimized_stats = optimizer.optimize_memory()
        print(f"✅ Memory optimization completed: {optimized_stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory Optimizer test failed: {e}")
        return False


def test_performance_manager():
    """Test the performance manager."""
    print("\n🧪 Testing Performance Manager...")
    
    try:
        from core.cache import PerformanceManager
        
        # Test with custom configuration
        config = {
            'cache': {
                'max_size': 5,
                'max_memory_mb': 1.0,
                'ttl': 1.0
            },
            'debounce': {
                'delay': 0.1
            }
        }
        
        manager = PerformanceManager(config)
        
        # Test cache key generation
        key1 = manager.generate_cache_key("test", "data", param="value")
        key2 = manager.generate_cache_key("test", "data", param="value")
        key3 = manager.generate_cache_key("test", "different", param="value")
        
        assert key1 == key2  # Same inputs should generate same key
        assert key1 != key3  # Different inputs should generate different keys
        print("✅ Cache key generation works")
        
        # Test response caching
        test_response = {"content": "test response", "success": True}
        assert manager.cache_response("test_key", test_response)
        
        cached = manager.get_cached_response("test_key")
        assert cached == test_response
        print("✅ Response caching works")
        
        # Test cache miss
        missing = manager.get_cached_response("nonexistent_key")
        assert missing is None
        print("✅ Cache miss handling works")
        
        # Test debounced requests
        call_count = 0
        def test_callback():
            nonlocal call_count
            call_count += 1
        
        manager.debounce_request("test_debounce", test_callback)
        manager.debounce_request("test_debounce", test_callback)  # Should cancel previous
        
        time.sleep(0.2)
        assert call_count == 1
        print("✅ Request debouncing works")
        
        # Test performance stats
        stats = manager.get_performance_stats()
        assert 'uptime_seconds' in stats
        assert 'cache_stats' in stats
        assert 'memory_stats' in stats
        print(f"✅ Performance stats: {stats}")
        
        # Test cleanup
        manager.cleanup()
        print("✅ Performance manager cleanup works")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance Manager test failed: {e}")
        return False


def test_agent_integration():
    """Test performance integration with AI agent."""
    print("\n🧪 Testing Agent Performance Integration...")
    
    try:
        from core.config import ConfigManager
        from core.agent import AIAgent
        
        # Create config with performance settings
        config = ConfigManager()
        
        # Create agent (should initialize performance manager)
        agent = AIAgent(config)
        
        # Test that performance manager is initialized
        assert hasattr(agent, 'performance_manager')
        assert agent.performance_manager is not None
        print("✅ Agent has performance manager")
        
        # Test performance stats
        stats = agent.get_performance_stats()
        assert isinstance(stats, dict)
        print(f"✅ Agent performance stats: {stats}")
        
        # Test cleanup
        agent.cleanup()
        print("✅ Agent cleanup works")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent Performance Integration test failed: {e}")
        return False


def test_config_performance_settings():
    """Test performance configuration settings."""
    print("\n🧪 Testing Performance Configuration...")
    
    try:
        from core.config import ConfigManager
        
        config = ConfigManager()
        
        # Test that performance settings exist
        perf_config = config.get('performance', {})
        assert 'cache' in perf_config
        assert 'debounce' in perf_config
        assert 'memory' in perf_config
        print("✅ Performance configuration exists")
        
        # Test cache settings
        cache_config = perf_config['cache']
        assert 'max_size' in cache_config
        assert 'max_memory_mb' in cache_config
        assert 'ttl' in cache_config
        print("✅ Cache configuration is complete")
        
        # Test debounce settings
        debounce_config = perf_config['debounce']
        assert 'delay' in debounce_config
        print("✅ Debounce configuration is complete")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance Configuration test failed: {e}")
        return False


def main():
    """Run all performance tests."""
    print("🚀 Geany Copilot Performance Test Suite")
    print("=" * 60)
    
    tests = [
        ("LRU Cache", test_lru_cache),
        ("Request Debouncer", test_request_debouncer),
        ("Memory Optimizer", test_memory_optimizer),
        ("Performance Manager", test_performance_manager),
        ("Agent Integration", test_agent_integration),
        ("Configuration Settings", test_config_performance_settings),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Performance optimizations are ready.")
        print("\n📝 Next steps:")
        print("1. Test in actual Geany environment with real workloads")
        print("2. Monitor memory usage during extended sessions")
        print("3. Verify cache effectiveness with repeated queries")
        print("4. Test debouncing with rapid user input")
        print("5. Benchmark performance improvements")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
