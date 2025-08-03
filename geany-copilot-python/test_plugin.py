#!/usr/bin/env python3
"""
Test script for Geany Copilot Python Plugin.

This script tests the plugin components outside of Geany to verify
that the basic structure and imports work correctly.
"""

import sys
import os
from pathlib import Path

# Add the plugin directory to Python path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        # Test core modules
        from core.config import ConfigManager
        print("✅ ConfigManager imported successfully")
        
        from core.api_client import APIClient
        print("✅ APIClient imported successfully")
        
        from core.context import ContextAnalyzer
        print("✅ ContextAnalyzer imported successfully")
        
        from core.agent import AIAgent
        print("✅ AIAgent imported successfully")
        
        # Test agent modules
        from agents.code_assistant import CodeAssistant
        print("✅ CodeAssistant imported successfully")
        
        from agents.copywriter import CopywriterAssistant
        print("✅ CopywriterAssistant imported successfully")
        
        # Test utility modules
        from utils.logging_setup import setup_plugin_logging
        print("✅ Logging setup imported successfully")
        
        from utils.helpers import get_plugin_data_dir
        print("✅ Helper functions imported successfully")
        
        # Test UI modules (may fail if GTK not available)
        try:
            from ui.dialogs import SettingsDialog, CodeAssistantDialog, CopywriterDialog
            print("✅ UI dialogs imported successfully")
        except ImportError as e:
            print(f"⚠️  UI dialogs not available: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_configuration():
    """Test configuration management."""
    print("\n🧪 Testing configuration management...")
    
    try:
        from core.config import ConfigManager
        
        # Create a temporary config manager
        config = ConfigManager()
        
        # Test basic configuration operations
        config.set("test.key", "test_value")
        value = config.get("test.key")
        
        if value == "test_value":
            print("✅ Configuration set/get works")
        else:
            print(f"❌ Configuration test failed: expected 'test_value', got '{value}'")
            return False
        
        # Test API configuration
        api_config = config.get_api_config("deepseek")
        if api_config:
            print("✅ API configuration retrieval works")
        else:
            print("❌ API configuration retrieval failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_api_client():
    """Test API client initialization."""
    print("\n🧪 Testing API client...")
    
    try:
        from core.api_client import APIClient
        from core.config import ConfigManager
        
        config = ConfigManager()
        client = APIClient(config)
        
        if client:
            print("✅ API client created successfully")
        else:
            print("❌ API client creation failed")
            return False
        
        # Test basic functionality
        from core.api_client import ChatMessage
        messages = [ChatMessage("user", "Test message")]
        if messages and len(messages) > 0:
            print("✅ Message creation works")
        else:
            print("❌ Message creation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ API client test failed: {e}")
        return False


def test_agents():
    """Test agent initialization."""
    print("\n🧪 Testing agents...")
    
    try:
        from core.config import ConfigManager
        from core.agent import AIAgent
        from agents.code_assistant import CodeAssistant
        from agents.copywriter import CopywriterAssistant
        
        config = ConfigManager()
        ai_agent = AIAgent(config)
        
        # Test code assistant
        code_assistant = CodeAssistant(ai_agent, config)
        if code_assistant:
            print("✅ CodeAssistant created successfully")
        else:
            print("❌ CodeAssistant creation failed")
            return False
        
        # Test copywriter
        copywriter = CopywriterAssistant(ai_agent, config)
        if copywriter:
            print("✅ CopywriterAssistant created successfully")
        else:
            print("❌ CopywriterAssistant creation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False


def test_logging():
    """Test logging setup."""
    print("\n🧪 Testing logging...")
    
    try:
        from utils.logging_setup import setup_plugin_logging
        
        logger = setup_plugin_logging(debug=True)
        if logger:
            print("✅ Logger setup successful")
            logger.info("Test log message")
            print("✅ Test log message written")
        else:
            print("❌ Logger setup failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False


def test_plugin_structure():
    """Test overall plugin structure."""
    print("\n🧪 Testing plugin structure...")
    
    # Check for required files
    required_files = [
        "__init__.py",
        "requirements.txt",
        "README.md",
        "core/__init__.py",
        "core/config.py",
        "core/api_client.py",
        "core/context.py",
        "core/agent.py",
        "agents/__init__.py",
        "agents/code_assistant.py",
        "agents/copywriter.py",
        "ui/__init__.py",
        "ui/dialogs.py",
        "utils/__init__.py",
        "utils/logging_setup.py",
        "utils/helpers.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = plugin_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
    
    return True


def main():
    """Run all tests."""
    print("🚀 Geany Copilot Python Plugin Test Suite")
    print("=" * 50)
    
    tests = [
        ("Plugin Structure", test_plugin_structure),
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("API Client", test_api_client),
        ("Agents", test_agents),
        ("Logging", test_logging),
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
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Plugin structure is valid.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
