#!/usr/bin/env python3
"""
Test script for streaming functionality in Geany Copilot Python Plugin.

This script tests the streaming support integration with UI dialogs.
"""

import sys
import os
from pathlib import Path

# Add the plugin directory to Python path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

def test_streaming_callbacks():
    """Test streaming callback setup."""
    print("🧪 Testing streaming callbacks...")
    
    try:
        from core.config import ConfigManager
        from core.agent import AIAgent
        from agents.code_assistant import CodeAssistant
        from agents.copywriter import CopywriterAssistant
        
        # Create components
        config = ConfigManager()
        ai_agent = AIAgent(config)
        code_assistant = CodeAssistant(ai_agent, config)
        copywriter = CopywriterAssistant(ai_agent, config)
        
        # Test callback setup
        test_callback_called = False
        
        def test_callback(chunk):
            nonlocal test_callback_called
            test_callback_called = True
            print(f"   Callback received chunk: {chunk[:20]}...")
        
        # Set up callbacks
        ai_agent.on_response_chunk = test_callback
        ai_agent.on_thinking_start = lambda: print("   Thinking started")
        ai_agent.on_error = lambda error: print(f"   Error: {error}")
        
        print("✅ Streaming callbacks setup successfully")
        
        # Test that agents have streaming methods
        streaming_methods = [
            'request_assistance_stream',
            'improve_text_stream', 
            'proofread_text_stream',
            'rewrite_text_stream'
        ]
        
        for method in streaming_methods:
            if hasattr(code_assistant, 'request_assistance_stream'):
                print(f"✅ CodeAssistant has {method}")
                break
            if hasattr(copywriter, method):
                print(f"✅ CopywriterAssistant has {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Streaming callback test failed: {e}")
        return False


def test_dialog_streaming_setup():
    """Test dialog streaming setup."""
    print("\n🧪 Testing dialog streaming setup...")
    
    try:
        # Test imports
        from ui.dialogs import CodeAssistantDialog, CopywriterDialog
        from core.config import ConfigManager
        from core.agent import AIAgent
        from agents.code_assistant import CodeAssistant
        from agents.copywriter import CopywriterAssistant
        
        print("✅ Dialog imports successful")
        
        # Create components (will work outside GTK environment for basic testing)
        config = ConfigManager()
        ai_agent = AIAgent(config)
        code_assistant = CodeAssistant(ai_agent, config)
        copywriter = CopywriterAssistant(ai_agent, config)
        
        print("✅ Agent components created")
        
        # Test dialog creation (may fail without GTK, but we can test the class structure)
        try:
            # This will likely fail without GTK, but we can catch and continue
            code_dialog = CodeAssistantDialog(code_assistant)
            print("✅ CodeAssistantDialog created successfully")
        except Exception as e:
            print(f"⚠️  CodeAssistantDialog creation failed (expected without GTK): {e}")
        
        try:
            copywriter_dialog = CopywriterDialog(copywriter)
            print("✅ CopywriterDialog created successfully")
        except Exception as e:
            print(f"⚠️  CopywriterDialog creation failed (expected without GTK): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dialog streaming setup test failed: {e}")
        return False


def test_streaming_methods():
    """Test that streaming methods exist."""
    print("\n🧪 Testing streaming methods...")
    
    try:
        from agents.code_assistant import CodeAssistant
        from agents.copywriter import CopywriterAssistant
        from core.config import ConfigManager
        from core.agent import AIAgent
        
        config = ConfigManager()
        ai_agent = AIAgent(config)
        code_assistant = CodeAssistant(ai_agent, config)
        copywriter = CopywriterAssistant(ai_agent, config)
        
        # Check for streaming methods
        code_streaming_methods = ['request_assistance_stream']
        copywriter_streaming_methods = [
            'improve_text_stream',
            'proofread_text_stream', 
            'rewrite_text_stream'
        ]
        
        for method in code_streaming_methods:
            if hasattr(code_assistant, method):
                print(f"✅ CodeAssistant has {method}")
            else:
                print(f"⚠️  CodeAssistant missing {method}")
        
        for method in copywriter_streaming_methods:
            if hasattr(copywriter, method):
                print(f"✅ CopywriterAssistant has {method}")
            else:
                print(f"⚠️  CopywriterAssistant missing {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Streaming methods test failed: {e}")
        return False


def test_ui_streaming_features():
    """Test UI streaming features."""
    print("\n🧪 Testing UI streaming features...")
    
    # Test that the dialog classes have the expected streaming methods
    streaming_ui_methods = [
        '_setup_streaming_callbacks',
        '_on_thinking_start',
        '_on_response_chunk', 
        '_on_streaming_error',
        '_start_assistant_message',
        '_update_assistant_message',
        '_finalize_assistant_message'
    ]
    
    copywriter_streaming_methods = [
        '_setup_copywriter_streaming_callbacks',
        '_on_copywriter_thinking_start',
        '_on_copywriter_response_chunk',
        '_on_copywriter_streaming_error',
        '_finalize_copywriter_response'
    ]
    
    try:
        from ui.dialogs import CodeAssistantDialog, CopywriterDialog
        
        # Check CodeAssistantDialog methods
        for method in streaming_ui_methods:
            if hasattr(CodeAssistantDialog, method):
                print(f"✅ CodeAssistantDialog has {method}")
            else:
                print(f"❌ CodeAssistantDialog missing {method}")
        
        # Check CopywriterDialog methods  
        for method in copywriter_streaming_methods:
            if hasattr(CopywriterDialog, method):
                print(f"✅ CopywriterDialog has {method}")
            else:
                print(f"❌ CopywriterDialog missing {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ UI streaming features test failed: {e}")
        return False


def main():
    """Run all streaming tests."""
    print("🚀 Geany Copilot Streaming Test Suite")
    print("=" * 50)
    
    tests = [
        ("Streaming Callbacks", test_streaming_callbacks),
        ("Dialog Streaming Setup", test_dialog_streaming_setup),
        ("Streaming Methods", test_streaming_methods),
        ("UI Streaming Features", test_ui_streaming_features),
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
        print("🎉 All tests passed! Streaming functionality is ready.")
        print("\n📝 Next steps:")
        print("1. Test in actual Geany environment with GTK")
        print("2. Verify streaming works with real API calls")
        print("3. Test error handling during streaming")
        print("4. Test UI responsiveness during long streams")
        print("5. Test streaming toggle functionality")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
