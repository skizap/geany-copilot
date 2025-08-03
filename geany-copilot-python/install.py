#!/usr/bin/env python3
"""
Installation script for Geany Copilot Python Plugin.

This script helps set up the plugin in the correct location and
verifies that all dependencies are available.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def get_geany_plugin_dir():
    """Get the Geany plugin directory."""
    # Common locations for Geany plugin directories
    possible_dirs = [
        Path.home() / ".config" / "geany" / "plugins" / "geanylua",
        Path.home() / ".geany" / "plugins" / "geanylua",
        Path("/usr/local/share/geany/plugins/geanylua"),
        Path("/usr/share/geany/plugins/geanylua"),
    ]
    
    for plugin_dir in possible_dirs:
        if plugin_dir.exists():
            return plugin_dir
    
    # Default to the most common location
    default_dir = Path.home() / ".config" / "geany" / "plugins" / "geanylua"
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 or higher is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True


def check_dependencies():
    """Check if required dependencies are available."""
    dependencies = ["requests"]
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} is available")
        except ImportError:
            print(f"❌ {dep} is missing")
            missing.append(dep)
    
    return missing


def install_dependencies(missing_deps):
    """Install missing dependencies."""
    if not missing_deps:
        return True
    
    print(f"\n📦 Installing missing dependencies: {', '.join(missing_deps)}")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--user"
        ] + missing_deps)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_geany_requirements():
    """Check Geany-specific requirements."""
    print("\n🔍 Checking Geany requirements...")
    
    # Check for GTK
    gtk_available = False
    try:
        import gtk
        gtk_available = True
        print("✅ GTK (PyGTK) is available")
    except ImportError:
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            gtk_available = True
            print("✅ GTK (PyGObject) is available")
        except ImportError:
            print("❌ GTK bindings not found (PyGTK or PyGObject required)")
    
    # Check for Geany (will only work when running inside Geany)
    try:
        import geany
        print("✅ Geany Python bindings are available")
    except ImportError:
        print("ℹ️  Geany Python bindings not available (normal when running outside Geany)")
    
    return gtk_available


def copy_plugin_files(source_dir, target_dir):
    """Copy plugin files to the target directory."""
    plugin_name = "geany-copilot-python"
    target_plugin_dir = target_dir / plugin_name
    
    print(f"\n📁 Installing plugin to: {target_plugin_dir}")
    
    # Remove existing installation
    if target_plugin_dir.exists():
        print("🗑️  Removing existing installation...")
        shutil.rmtree(target_plugin_dir)
    
    # Copy plugin files
    try:
        shutil.copytree(source_dir, target_plugin_dir)
        print("✅ Plugin files copied successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to copy plugin files: {e}")
        return False


def create_config_template(plugin_dir):
    """Create a configuration template."""
    config_file = plugin_dir / "config.json"
    
    if config_file.exists():
        print("ℹ️  Configuration file already exists, skipping template creation")
        return
    
    config_template = {
        "api": {
            "primary_provider": "deepseek",
            "deepseek": {
                "api_key": "your-deepseek-api-key-here",
                "base_url": "https://api.deepseek.com",
                "model": "deepseek-chat"
            },
            "openai": {
                "api_key": "your-openai-api-key-here",
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4"
            }
        },
        "agents": {
            "code_assistant": {
                "enabled": True,
                "max_context_lines": 100,
                "include_imports": True
            },
            "copywriter": {
                "enabled": True,
                "max_iterations": 5
            }
        },
        "ui": {
            "dialog_width": 900,
            "dialog_height": 700
        }
    }
    
    try:
        import json
        with open(config_file, 'w') as f:
            json.dump(config_template, f, indent=2)
        print(f"✅ Configuration template created: {config_file}")
    except Exception as e:
        print(f"❌ Failed to create configuration template: {e}")


def main():
    """Main installation function."""
    print("🚀 Geany Copilot Python Plugin Installer")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check and install dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        if not install_dependencies(missing_deps):
            print("\n❌ Installation failed due to missing dependencies")
            sys.exit(1)
    
    # Check Geany requirements
    if not check_geany_requirements():
        print("\n⚠️  Some Geany requirements are missing. The plugin may not work properly.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Get directories
    source_dir = Path(__file__).parent
    target_dir = get_geany_plugin_dir()
    
    print(f"\n📂 Source directory: {source_dir}")
    print(f"📂 Target directory: {target_dir}")
    
    # Copy plugin files
    if not copy_plugin_files(source_dir, target_dir):
        sys.exit(1)
    
    # Create configuration template
    plugin_dir = target_dir / "geany-copilot-python"
    create_config_template(plugin_dir)
    
    print("\n🎉 Installation completed successfully!")
    print("\nNext steps:")
    print("1. Restart Geany")
    print("2. Enable GeanyPy plugin in Tools → Plugin Manager")
    print("3. Configure your API key in Tools → Copilot Settings")
    print("4. Start using AI Code Assistant and Copywriter!")
    
    print(f"\n📝 Configuration file: {plugin_dir / 'config.json'}")
    print(f"📋 Log file: {plugin_dir / 'logs' / 'geany-copilot-python.log'}")


if __name__ == "__main__":
    main()
