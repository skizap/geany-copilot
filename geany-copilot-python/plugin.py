#!/usr/bin/env python3
"""
Geany Copilot Python Plugin Entry Point

This file serves as the main entry point for the Geany Copilot Python plugin
when loaded by GeanyPy. It follows Geany plugin conventions and provides
the necessary plugin information and initialization.

Plugin Information:
- Name: Geany Copilot Python
- Description: AI-powered code assistant and copywriter for Geany IDE
- Version: 1.0.0
- Author: Geany Copilot Team
- License: MIT
"""

import sys
import os
from pathlib import Path

# Add the plugin directory to Python path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

# Import the main plugin class
try:
    from __init__ import GeanyCopilotPlugin
    
    # Plugin information for GeanyPy
    __plugin_name__ = "Geany Copilot Python"
    __plugin_version__ = "1.0.0"
    __plugin_description__ = "AI-powered code assistant and copywriter with agent capabilities"
    __plugin_author__ = "Geany Copilot Team"
    __plugin_key_bindings__ = ()
    
    # Create the plugin instance
    plugin = GeanyCopilotPlugin()
    
except ImportError as e:
    print(f"Failed to load Geany Copilot Python plugin: {e}")
    plugin = None


def activate():
    """Activate the plugin."""
    if plugin:
        try:
            plugin.activate()
        except Exception as e:
            print(f"Error activating Geany Copilot Python plugin: {e}")


def deactivate():
    """Deactivate the plugin."""
    if plugin:
        try:
            plugin.deactivate()
        except Exception as e:
            print(f"Error deactivating Geany Copilot Python plugin: {e}")


def cleanup():
    """Clean up the plugin."""
    if plugin:
        try:
            plugin.cleanup()
        except Exception as e:
            print(f"Error cleaning up Geany Copilot Python plugin: {e}")


# For direct execution (testing)
if __name__ == "__main__":
    print(f"Plugin: {__plugin_name__} v{__plugin_version__}")
    print(f"Description: {__plugin_description__}")
    print(f"Author: {__plugin_author__}")
    
    if plugin:
        print("Plugin loaded successfully")
        # Test basic functionality
        try:
            activate()
            print("Plugin activated successfully")
            deactivate()
            print("Plugin deactivated successfully")
            cleanup()
            print("Plugin cleaned up successfully")
        except Exception as e:
            print(f"Plugin test failed: {e}")
    else:
        print("Plugin failed to load")
