"""
Geany Copilot Python Plugin

An AI-powered assistant plugin for Geany IDE that provides intelligent code assistance
and copywriting features using advanced language models.

This plugin replaces the original Lua-based implementation with enhanced agent capabilities,
multi-turn conversations, and support for DeepSeek and other OpenAI-compatible APIs.

Author: skizap
Version: 1.0.0
License: MIT
"""

import os
import sys
from typing import Optional

# Add the plugin directory to Python path for imports
plugin_dir = os.path.dirname(os.path.abspath(__file__))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

try:
    import geany
    import gtk
except ImportError as e:
    # This will happen when running outside of Geany/GeanyPy
    print(f"GeanyPy not available: {e}")
    geany = None
    gtk = None

from utils.logging_setup import setup_plugin_logging

# Setup logging first
logger = setup_plugin_logging(debug=False)

from core.config import ConfigManager
from core.agent import AIAgent
from agents.code_assistant import CodeAssistant
from agents.copywriter import CopywriterAssistant

# Import UI components with error handling
try:
    from ui.dialogs import SettingsDialog, CodeAssistantDialog, CopywriterDialog
    UI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"UI components not available: {e}")
    UI_AVAILABLE = False
    SettingsDialog = None
    CodeAssistantDialog = None
    CopywriterDialog = None


class GeanyCopilotPlugin(geany.Plugin if geany else object):
    """
    Main plugin class for Geany Copilot Python.
    
    This class integrates with Geany's plugin system and provides the main
    entry point for AI-powered code assistance and copywriting features.
    """
    
    __plugin_name__ = "Geany Copilot Python"
    __plugin_version__ = "1.0.0"
    __plugin_description__ = "AI-powered code assistance and copywriting with agent capabilities"
    __plugin_author__ = "AI Assistant <ai@example.com>"
    
    def __init__(self):
        """Initialize the plugin."""
        if geany:
            geany.Plugin.__init__(self)
            self.logger = logger
            self.logger.info("Initializing Geany Copilot Python plugin")
        else:
            # Use the already configured logger
            self.logger = logger
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.ai_agent = AIAgent(self.config_manager)
        
        # Initialize specialized agents
        self.code_assistant = CodeAssistant(self.ai_agent, self.config_manager)
        self.copywriter = CopywriterAssistant(self.ai_agent, self.config_manager)
        
        # UI components
        self.settings_dialog = None
        self.code_assistant_dialog = None
        self.copywriter_dialog = None
        
        # Menu items
        self.code_menu_item = None
        self.copywriter_menu_item = None
        self.settings_menu_item = None
        
        if geany:
            self._setup_ui()
            self._connect_signals()
    
    def _setup_ui(self):
        """Setup the user interface components."""
        try:
            # Create menu items
            self.code_menu_item = gtk.MenuItem("AI Code Assistant")
            self.code_menu_item.show()
            self.code_menu_item.connect("activate", self._on_code_assistant_activated)
            
            self.copywriter_menu_item = gtk.MenuItem("AI Copywriter")
            self.copywriter_menu_item.show()
            self.copywriter_menu_item.connect("activate", self._on_copywriter_activated)
            
            self.settings_menu_item = gtk.MenuItem("Copilot Settings")
            self.settings_menu_item.show()
            self.settings_menu_item.connect("activate", self._on_settings_activated)
            
            # Add to Tools menu
            if hasattr(geany, 'main_widgets') and geany.main_widgets.tools_menu:
                geany.main_widgets.tools_menu.append(self.code_menu_item)
                geany.main_widgets.tools_menu.append(self.copywriter_menu_item)
                geany.main_widgets.tools_menu.append(gtk.SeparatorMenuItem())
                geany.main_widgets.tools_menu.append(self.settings_menu_item)
            
            self.logger.info("UI components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup UI: {e}")
    
    def _connect_signals(self):
        """Connect to Geany signals."""
        try:
            if hasattr(geany, 'signals'):
                # Connect to document signals for context awareness
                geany.signals.connect('document-open', self._on_document_open)
                geany.signals.connect('document-activate', self._on_document_activate)
                geany.signals.connect('document-save', self._on_document_save)
                
            self.logger.info("Signals connected successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to connect signals: {e}")
    
    def _on_code_assistant_activated(self, widget):
        """Handle code assistant menu activation."""
        _ = widget  # Unused parameter
        try:
            # Check for special configuration trigger
            current_doc = geany.document.get_current()
            if current_doc:
                selection = self._get_current_selection()
                if selection and selection.strip() == ".gc conf":
                    self._show_settings_dialog()
                    return
            
            # Show code assistant dialog
            self._show_code_assistant_dialog()
            
        except Exception as e:
            self.logger.error(f"Error in code assistant: {e}")
            self._show_error_dialog(f"Code Assistant Error: {e}")
    
    def _on_copywriter_activated(self, widget):
        """Handle copywriter menu activation."""
        _ = widget  # Unused parameter
        try:
            # Check for special configuration trigger
            current_doc = geany.document.get_current()
            if current_doc:
                selection = self._get_current_selection()
                if selection and selection.strip() == ".gc conf":
                    self._show_settings_dialog()
                    return
            
            # Show copywriter dialog
            self._show_copywriter_dialog()
            
        except Exception as e:
            self.logger.error(f"Error in copywriter: {e}")
            self._show_error_dialog(f"Copywriter Error: {e}")
    
    def _on_settings_activated(self, widget):
        """Handle settings menu activation."""
        _ = widget  # Unused parameter
        self._show_settings_dialog()
    
    def _show_settings_dialog(self):
        """Show the settings configuration dialog."""
        try:
            if not UI_AVAILABLE or not SettingsDialog:
                self._show_error_dialog("UI components not available")
                return

            if not self.settings_dialog:
                self.settings_dialog = SettingsDialog(self.config_manager)

            self.settings_dialog.show()

        except Exception as e:
            self.logger.error(f"Error showing settings dialog: {e}")
            self._show_error_dialog(f"Settings Error: {e}")

    def _show_code_assistant_dialog(self):
        """Show the code assistant dialog."""
        try:
            if not UI_AVAILABLE or not CodeAssistantDialog:
                self._show_error_dialog("UI components not available")
                return

            if not self.code_assistant_dialog:
                self.code_assistant_dialog = CodeAssistantDialog(self.code_assistant)

            self.code_assistant_dialog.show()

        except Exception as e:
            self.logger.error(f"Error showing code assistant dialog: {e}")
            self._show_error_dialog(f"Code Assistant Error: {e}")

    def _show_copywriter_dialog(self):
        """Show the copywriter dialog."""
        try:
            if not UI_AVAILABLE or not CopywriterDialog:
                self._show_error_dialog("UI components not available")
                return

            # Get selected text for copywriter
            selected_text = self._get_current_selection()
            if not selected_text or not selected_text.strip():
                self._show_error_dialog("Please select some text for copywriting assistance.")
                return

            if not self.copywriter_dialog:
                self.copywriter_dialog = CopywriterDialog(self.copywriter)

            self.copywriter_dialog.set_text(selected_text)
            self.copywriter_dialog.show()

        except Exception as e:
            self.logger.error(f"Error showing copywriter dialog: {e}")
            self._show_error_dialog(f"Copywriter Error: {e}")
    
    def _get_current_selection(self) -> Optional[str]:
        """Get the currently selected text in the editor."""
        try:
            from utils.helpers import get_selected_text
            return get_selected_text()
        except Exception as e:
            self.logger.error(f"Error getting selection: {e}")
            return None
    

    
    def _show_error_dialog(self, message: str):
        """Show an error dialog to the user."""
        try:
            if geany and hasattr(geany, 'dialogs'):
                geany.dialogs.show_msgbox(message, gtk.MESSAGE_ERROR)
            else:
                print(f"Error: {message}")
        except Exception as e:
            self.logger.error(f"Error showing error dialog: {e}")
    
    def _on_document_open(self, document):
        """Handle document open signal."""
        self.logger.debug(f"Document opened: {document.file_name if document else 'Unknown'}")
    
    def _on_document_activate(self, document):
        """Handle document activate signal."""
        self.logger.debug(f"Document activated: {document.file_name if document else 'Unknown'}")
    
    def _on_document_save(self, document):
        """Handle document save signal."""
        self.logger.debug(f"Document saved: {document.file_name if document else 'Unknown'}")
    
    def cleanup(self):
        """Cleanup when plugin is unloaded."""
        try:
            self.logger.info("Cleaning up Geany Copilot Python plugin")
            
            # Remove menu items
            if self.code_menu_item:
                self.code_menu_item.destroy()
            if self.copywriter_menu_item:
                self.copywriter_menu_item.destroy()
            if self.settings_menu_item:
                self.settings_menu_item.destroy()
            
            # Cleanup dialogs
            if self.settings_dialog:
                self.settings_dialog.destroy()
            if self.code_assistant_dialog:
                self.code_assistant_dialog.destroy()
            if self.copywriter_dialog:
                self.copywriter_dialog.destroy()
            
            # Cleanup agents
            if self.ai_agent:
                self.ai_agent.cleanup()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def activate(self):
        """Activate the plugin (for GeanyPy compatibility)."""
        # Plugin is automatically activated on initialization
        self.logger.info("Plugin activated")

    def deactivate(self):
        """Deactivate the plugin (for GeanyPy compatibility)."""
        # Cleanup is handled in cleanup() method
        self.logger.info("Plugin deactivated")


# Plugin instance - this is what GeanyPy will load
if geany:
    # Only create the plugin instance when running in Geany
    plugin_instance = GeanyCopilotPlugin()
else:
    # For testing outside of Geany
    plugin_instance = None
