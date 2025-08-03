"""
Dialog components for Geany Copilot Python plugin.

This module provides GTK-based dialog windows for code assistance,
copywriting, and plugin configuration.
"""

import logging
from typing import Optional, Callable, Any

try:
    import gtk
    import gobject
    GTK_AVAILABLE = True
except ImportError:
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk as gtk, GObject as gobject
        GTK_AVAILABLE = True
    except ImportError:
        GTK_AVAILABLE = False
        logging.getLogger(__name__).warning("GTK not available for UI components")


class BaseDialog:
    """Base class for plugin dialogs."""
    
    def __init__(self, title: str, parent=None, width: int = 800, height: int = 600):
        """
        Initialize base dialog.
        
        Args:
            title: Dialog title
            parent: Parent window
            width: Dialog width
            height: Dialog height
        """
        if not GTK_AVAILABLE:
            raise RuntimeError("GTK is not available")
        
        self.logger = logging.getLogger(__name__)
        
        # Create dialog window
        self.dialog = gtk.Dialog(
            title=title,
            parent=parent,
            flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
        )
        
        self.dialog.set_default_size(width, height)
        self.dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
        # Add standard buttons
        self.dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        
        # Get content area
        self.content_area = self.dialog.get_content_area()
        
        # Initialize UI
        self._setup_ui()
        
        # Connect signals
        self.dialog.connect("response", self._on_response)
        self.dialog.connect("delete-event", self._on_delete)
    
    def _setup_ui(self):
        """Setup the dialog UI. Override in subclasses."""
        pass
    
    def _on_response(self, dialog, response_id):
        """Handle dialog response."""
        if response_id == gtk.RESPONSE_OK:
            self._on_ok()
        elif response_id == gtk.RESPONSE_CANCEL:
            self._on_cancel()
        else:
            self._on_close()
    
    def _on_ok(self):
        """Handle OK button click. Override in subclasses."""
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle Cancel button click. Override in subclasses."""
        self.dialog.destroy()
    
    def _on_close(self):
        """Handle dialog close. Override in subclasses."""
        self.dialog.destroy()
    
    def _on_delete(self, widget, event):
        """Handle delete event."""
        return False  # Allow deletion
    
    def show(self):
        """Show the dialog."""
        self.dialog.show_all()
        return self.dialog.run()
    
    def hide(self):
        """Hide the dialog."""
        self.dialog.hide()
    
    def destroy(self):
        """Destroy the dialog."""
        self.dialog.destroy()


class CodeAssistantDialog(BaseDialog):
    """Dialog for code assistance interactions."""
    
    def __init__(self, code_assistant, parent=None):
        """
        Initialize code assistant dialog.
        
        Args:
            code_assistant: CodeAssistant instance
            parent: Parent window
        """
        self.code_assistant = code_assistant
        self.conversation_active = False
        
        super().__init__("Code Assistant", parent, 900, 700)
    
    def _setup_ui(self):
        """Setup the code assistant UI."""
        # Create main container
        main_vbox = gtk.VBox(spacing=10)
        main_vbox.set_border_width(10)
        self.content_area.pack_start(main_vbox, True, True, 0)
        
        # Context display area
        context_frame = gtk.Frame("Current Context")
        self.context_text = gtk.TextView()
        self.context_text.set_editable(False)
        self.context_text.set_wrap_mode(gtk.WRAP_WORD)
        
        context_scroll = gtk.ScrolledWindow()
        context_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        context_scroll.add(self.context_text)
        context_scroll.set_size_request(-1, 150)
        
        context_frame.add(context_scroll)
        main_vbox.pack_start(context_frame, False, True, 0)
        
        # Chat area
        chat_frame = gtk.Frame("Conversation")
        self.chat_text = gtk.TextView()
        self.chat_text.set_editable(False)
        self.chat_text.set_wrap_mode(gtk.WRAP_WORD)
        
        chat_scroll = gtk.ScrolledWindow()
        chat_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        chat_scroll.add(self.chat_text)
        
        chat_frame.add(chat_scroll)
        main_vbox.pack_start(chat_frame, True, True, 0)
        
        # Input area
        input_frame = gtk.Frame("Your Request")
        input_vbox = gtk.VBox(spacing=5)
        input_vbox.set_border_width(5)
        
        self.input_text = gtk.TextView()
        self.input_text.set_wrap_mode(gtk.WRAP_WORD)
        
        input_scroll = gtk.ScrolledWindow()
        input_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        input_scroll.add(self.input_text)
        input_scroll.set_size_request(-1, 100)
        
        input_vbox.pack_start(input_scroll, True, True, 0)
        
        # Input buttons
        button_hbox = gtk.HBox(spacing=5)
        
        self.send_button = gtk.Button("Send Request")
        self.send_button.connect("clicked", self._on_send_request)
        button_hbox.pack_start(self.send_button, False, False, 0)
        
        self.clear_button = gtk.Button("Clear Chat")
        self.clear_button.connect("clicked", self._on_clear_chat)
        button_hbox.pack_start(self.clear_button, False, False, 0)
        
        self.analyze_button = gtk.Button("Analyze Context")
        self.analyze_button.connect("clicked", self._on_analyze_context)
        button_hbox.pack_start(self.analyze_button, False, False, 0)
        
        input_vbox.pack_start(button_hbox, False, False, 0)
        input_frame.add(input_vbox)
        main_vbox.pack_start(input_frame, False, True, 0)
        
        # Status bar
        self.status_bar = gtk.Statusbar()
        main_vbox.pack_start(self.status_bar, False, False, 0)
        
        # Initialize context
        self._update_context()
    
    def _update_context(self):
        """Update the context display."""
        try:
            context = self.code_assistant.get_context()
            buffer = self.context_text.get_buffer()
            buffer.set_text(context or "No context available")
        except Exception as e:
            self.logger.error(f"Error updating context: {e}")
    
    def _on_send_request(self, button):
        """Handle send request button click."""
        try:
            # Get input text
            buffer = self.input_text.get_buffer()
            start, end = buffer.get_bounds()
            request = buffer.get_text(start, end, False).strip()
            
            if not request:
                self._show_status("Please enter a request")
                return
            
            # Clear input
            buffer.set_text("")
            
            # Add request to chat
            self._add_to_chat(f"You: {request}")
            
            # Show thinking status
            self._show_status("Thinking...")
            self.send_button.set_sensitive(False)
            
            # Start or continue conversation
            if not self.conversation_active:
                self.code_assistant.start_assistance_session(request)
                self.conversation_active = True
            else:
                response = self.code_assistant.request_assistance(request)
                self._handle_response(response)
            
        except Exception as e:
            self.logger.error(f"Error sending request: {e}")
            self._show_status(f"Error: {e}")
            self.send_button.set_sensitive(True)
    
    def _handle_response(self, response):
        """Handle assistant response."""
        try:
            if response.success:
                self._add_to_chat(f"Assistant: {response.content}")
                self._show_status("Ready")
            else:
                self._add_to_chat(f"Error: {response.error}")
                self._show_status("Error occurred")
            
        except Exception as e:
            self.logger.error(f"Error handling response: {e}")
            self._show_status(f"Error: {e}")
        finally:
            self.send_button.set_sensitive(True)
    
    def _add_to_chat(self, message: str):
        """Add message to chat display."""
        buffer = self.chat_text.get_buffer()
        end_iter = buffer.get_end_iter()
        
        if buffer.get_char_count() > 0:
            buffer.insert(end_iter, "\n\n")
            end_iter = buffer.get_end_iter()
        
        buffer.insert(end_iter, message)
        
        # Scroll to bottom
        mark = buffer.get_insert()
        self.chat_text.scroll_mark_onscreen(mark)
    
    def _on_clear_chat(self, button):
        """Handle clear chat button click."""
        buffer = self.chat_text.get_buffer()
        buffer.set_text("")
        
        # End current conversation
        if self.conversation_active:
            self.code_assistant.end_session()
            self.conversation_active = False
        
        self._show_status("Chat cleared")
    
    def _on_analyze_context(self, button):
        """Handle analyze context button click."""
        self._update_context()
        self._show_status("Context updated")
    
    def _show_status(self, message: str):
        """Show status message."""
        context_id = self.status_bar.get_context_id("main")
        self.status_bar.pop(context_id)
        self.status_bar.push(context_id, message)
    
    def _on_ok(self):
        """Handle OK button - apply any changes."""
        # End conversation if active
        if self.conversation_active:
            self.code_assistant.end_session()
        super()._on_ok()
    
    def _on_cancel(self):
        """Handle Cancel button."""
        # End conversation if active
        if self.conversation_active:
            self.code_assistant.end_session()
        super()._on_cancel()


class CopywriterDialog(BaseDialog):
    """Dialog for copywriting assistance interactions."""
    
    def __init__(self, copywriter_assistant, parent=None):
        """
        Initialize copywriter dialog.
        
        Args:
            copywriter_assistant: CopywriterAssistant instance
            parent: Parent window
        """
        self.copywriter_assistant = copywriter_assistant
        self.session_active = False
        self.original_text = ""
        
        super().__init__("Copywriter Assistant", parent, 900, 700)
    
    def _setup_ui(self):
        """Setup the copywriter UI."""
        # Create main container
        main_vbox = gtk.VBox(spacing=10)
        main_vbox.set_border_width(10)
        self.content_area.pack_start(main_vbox, True, True, 0)
        
        # Original text area
        original_frame = gtk.Frame("Original Text")
        self.original_text_view = gtk.TextView()
        self.original_text_view.set_wrap_mode(gtk.WRAP_WORD)
        
        original_scroll = gtk.ScrolledWindow()
        original_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        original_scroll.add(self.original_text_view)
        original_scroll.set_size_request(-1, 150)
        
        original_frame.add(original_scroll)
        main_vbox.pack_start(original_frame, False, True, 0)
        
        # Improved text area
        improved_frame = gtk.Frame("Improved Text")
        self.improved_text_view = gtk.TextView()
        self.improved_text_view.set_wrap_mode(gtk.WRAP_WORD)
        
        improved_scroll = gtk.ScrolledWindow()
        improved_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        improved_scroll.add(self.improved_text_view)
        
        improved_frame.add(improved_scroll)
        main_vbox.pack_start(improved_frame, True, True, 0)
        
        # Control buttons
        button_hbox = gtk.HBox(spacing=5)
        
        self.improve_button = gtk.Button("Improve Text")
        self.improve_button.connect("clicked", self._on_improve_text)
        button_hbox.pack_start(self.improve_button, False, False, 0)
        
        self.proofread_button = gtk.Button("Proofread")
        self.proofread_button.connect("clicked", self._on_proofread)
        button_hbox.pack_start(self.proofread_button, False, False, 0)
        
        self.rewrite_button = gtk.Button("Rewrite")
        self.rewrite_button.connect("clicked", self._on_rewrite)
        button_hbox.pack_start(self.rewrite_button, False, False, 0)
        
        main_vbox.pack_start(button_hbox, False, False, 0)
        
        # Status bar
        self.status_bar = gtk.Statusbar()
        main_vbox.pack_start(self.status_bar, False, False, 0)
    
    def set_text(self, text: str):
        """Set the original text to work with."""
        self.original_text = text
        buffer = self.original_text_view.get_buffer()
        buffer.set_text(text)
    
    def _get_original_text(self) -> str:
        """Get the original text."""
        buffer = self.original_text_view.get_buffer()
        start, end = buffer.get_bounds()
        return buffer.get_text(start, end, False)
    
    def _set_improved_text(self, text: str):
        """Set the improved text."""
        buffer = self.improved_text_view.get_buffer()
        buffer.set_text(text)
    
    def _on_improve_text(self, button):
        """Handle improve text button click."""
        self._process_text("improve")
    
    def _on_proofread(self, button):
        """Handle proofread button click."""
        self._process_text("proofread")
    
    def _on_rewrite(self, button):
        """Handle rewrite button click."""
        self._process_text("rewrite")
    
    def _process_text(self, action: str):
        """Process text with the specified action."""
        try:
            text = self._get_original_text().strip()
            if not text:
                self._show_status("Please enter some text to work with")
                return
            
            # Start session if not active
            if not self.session_active:
                self.copywriter_assistant.start_writing_session(text)
                self.session_active = True
            
            # Show processing status
            self._show_status(f"Processing ({action})...")
            
            # Process based on action
            if action == "improve":
                response = self.copywriter_assistant.improve_text(text)
            elif action == "proofread":
                response = self.copywriter_assistant.proofread_text(text)
            elif action == "rewrite":
                response = self.copywriter_assistant.rewrite_text(text)
            else:
                response = self.copywriter_assistant.improve_text(text)
            
            # Handle response
            if response.success:
                self._set_improved_text(response.content)
                self._show_status("Processing complete")
            else:
                self._show_status(f"Error: {response.error}")
            
        except Exception as e:
            self.logger.error(f"Error processing text: {e}")
            self._show_status(f"Error: {e}")
    
    def _show_status(self, message: str):
        """Show status message."""
        context_id = self.status_bar.get_context_id("main")
        self.status_bar.pop(context_id)
        self.status_bar.push(context_id, message)
    
    def _on_ok(self):
        """Handle OK button - apply changes."""
        if self.session_active:
            self.copywriter_assistant.end_session()
        super()._on_ok()
    
    def _on_cancel(self):
        """Handle Cancel button."""
        if self.session_active:
            self.copywriter_assistant.end_session()
        super()._on_cancel()


class SettingsDialog(BaseDialog):
    """Dialog for plugin settings configuration."""
    
    def __init__(self, config_manager, parent=None):
        """
        Initialize settings dialog.
        
        Args:
            config_manager: ConfigManager instance
            parent: Parent window
        """
        self.config_manager = config_manager
        super().__init__("Geany Copilot Settings", parent, 600, 500)
    
    def _setup_ui(self):
        """Setup the settings UI."""
        # Create notebook for tabbed interface
        notebook = gtk.Notebook()
        self.content_area.pack_start(notebook, True, True, 0)
        
        # API Settings tab
        api_page = self._create_api_settings_page()
        notebook.append_page(api_page, gtk.Label("API Settings"))
        
        # Agent Settings tab
        agent_page = self._create_agent_settings_page()
        notebook.append_page(agent_page, gtk.Label("Agent Settings"))
        
        # UI Settings tab
        ui_page = self._create_ui_settings_page()
        notebook.append_page(ui_page, gtk.Label("UI Settings"))
    
    def _create_api_settings_page(self):
        """Create API settings page."""
        vbox = gtk.VBox(spacing=10)
        vbox.set_border_width(10)
        
        # Provider selection
        provider_hbox = gtk.HBox(spacing=5)
        provider_hbox.pack_start(gtk.Label("Primary Provider:"), False, False, 0)
        
        self.provider_combo = gtk.combo_box_new_text()
        self.provider_combo.append_text("deepseek")
        self.provider_combo.append_text("openai")
        self.provider_combo.append_text("custom")
        
        current_provider = self.config_manager.get("api.primary_provider", "deepseek")
        if current_provider == "deepseek":
            self.provider_combo.set_active(0)
        elif current_provider == "openai":
            self.provider_combo.set_active(1)
        else:
            self.provider_combo.set_active(2)
        
        provider_hbox.pack_start(self.provider_combo, False, False, 0)
        vbox.pack_start(provider_hbox, False, False, 0)
        
        # API Key entry
        key_hbox = gtk.HBox(spacing=5)
        key_hbox.pack_start(gtk.Label("API Key:"), False, False, 0)
        
        self.api_key_entry = gtk.Entry()
        self.api_key_entry.set_visibility(False)  # Hide password
        current_key = self.config_manager.get(f"api.{current_provider}.api_key", "")
        self.api_key_entry.set_text(current_key)
        
        key_hbox.pack_start(self.api_key_entry, True, True, 0)
        vbox.pack_start(key_hbox, False, False, 0)
        
        return vbox
    
    def _create_agent_settings_page(self):
        """Create agent settings page."""
        vbox = gtk.VBox(spacing=10)
        vbox.set_border_width(10)
        
        # Code assistant settings
        code_frame = gtk.Frame("Code Assistant")
        code_vbox = gtk.VBox(spacing=5)
        code_vbox.set_border_width(5)
        
        self.code_enabled_check = gtk.CheckButton("Enable Code Assistant")
        code_enabled = self.config_manager.get("agents.code_assistant.enabled", True)
        self.code_enabled_check.set_active(code_enabled)
        code_vbox.pack_start(self.code_enabled_check, False, False, 0)
        
        code_frame.add(code_vbox)
        vbox.pack_start(code_frame, False, False, 0)
        
        # Copywriter settings
        writer_frame = gtk.Frame("Copywriter")
        writer_vbox = gtk.VBox(spacing=5)
        writer_vbox.set_border_width(5)
        
        self.writer_enabled_check = gtk.CheckButton("Enable Copywriter")
        writer_enabled = self.config_manager.get("agents.copywriter.enabled", True)
        self.writer_enabled_check.set_active(writer_enabled)
        writer_vbox.pack_start(self.writer_enabled_check, False, False, 0)
        
        writer_frame.add(writer_vbox)
        vbox.pack_start(writer_frame, False, False, 0)
        
        return vbox
    
    def _create_ui_settings_page(self):
        """Create UI settings page."""
        vbox = gtk.VBox(spacing=10)
        vbox.set_border_width(10)
        
        # Dialog size settings
        size_frame = gtk.Frame("Dialog Settings")
        size_vbox = gtk.VBox(spacing=5)
        size_vbox.set_border_width(5)
        
        # Width setting
        width_hbox = gtk.HBox(spacing=5)
        width_hbox.pack_start(gtk.Label("Dialog Width:"), False, False, 0)
        
        self.width_spin = gtk.SpinButton()
        self.width_spin.set_range(400, 1600)
        self.width_spin.set_increments(50, 100)
        current_width = self.config_manager.get("ui.dialog_width", 800)
        self.width_spin.set_value(current_width)
        
        width_hbox.pack_start(self.width_spin, False, False, 0)
        size_vbox.pack_start(width_hbox, False, False, 0)
        
        size_frame.add(size_vbox)
        vbox.pack_start(size_frame, False, False, 0)
        
        return vbox
    
    def _on_ok(self):
        """Handle OK button - save settings."""
        try:
            # Save API settings
            provider_index = self.provider_combo.get_active()
            providers = ["deepseek", "openai", "custom"]
            selected_provider = providers[provider_index]
            
            self.config_manager.set("api.primary_provider", selected_provider)
            
            api_key = self.api_key_entry.get_text()
            self.config_manager.set(f"api.{selected_provider}.api_key", api_key)
            
            # Save agent settings
            self.config_manager.set("agents.code_assistant.enabled", 
                                  self.code_enabled_check.get_active())
            self.config_manager.set("agents.copywriter.enabled", 
                                  self.writer_enabled_check.get_active())
            
            # Save UI settings
            self.config_manager.set("ui.dialog_width", int(self.width_spin.get_value()))
            
            # Save configuration
            self.config_manager.save_config()
            
            self.logger.info("Settings saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
        
        super()._on_ok()
