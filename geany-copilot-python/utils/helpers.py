"""
Helper functions for Geany Copilot Python plugin.

This module provides utility functions for interacting with Geany's
editor and document system.
"""

import logging
from typing import Optional, Tuple, Any

try:
    import geany
    GEANY_AVAILABLE = True
except ImportError:
    GEANY_AVAILABLE = False

try:
    import gtk
    GTK_AVAILABLE = True
except ImportError:
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk as gtk
        GTK_AVAILABLE = True
    except ImportError:
        GTK_AVAILABLE = False


logger = logging.getLogger(__name__)


def get_current_document():
    """
    Get the current active document.
    
    Returns:
        Current document object or None
    """
    if not GEANY_AVAILABLE:
        logger.warning("Geany not available")
        return None
    
    try:
        return geany.document.get_current()
    except Exception as e:
        logger.error(f"Error getting current document: {e}")
        return None


def get_selected_text() -> Optional[str]:
    """
    Get the currently selected text in the editor.
    
    Returns:
        Selected text or None if no selection
    """
    if not GEANY_AVAILABLE:
        logger.warning("Geany not available")
        return None
    
    try:
        current_doc = get_current_document()
        if not current_doc or not current_doc.editor:
            return None
        
        # This is a simplified version - actual implementation would need
        # to use Scintilla editor methods to get selection
        # For now, return placeholder
        return None  # Placeholder
        
    except Exception as e:
        logger.error(f"Error getting selected text: {e}")
        return None


def replace_selected_text(new_text: str) -> bool:
    """
    Replace the currently selected text with new text.
    
    Args:
        new_text: Text to replace selection with
        
    Returns:
        True if successful, False otherwise
    """
    if not GEANY_AVAILABLE:
        logger.warning("Geany not available")
        return False
    
    try:
        current_doc = get_current_document()
        if not current_doc or not current_doc.editor:
            return False
        
        # This is a simplified version - actual implementation would need
        # to use Scintilla editor methods to replace selection
        # For now, return placeholder
        logger.info(f"Would replace selected text with: {new_text[:50]}...")
        return True  # Placeholder
        
    except Exception as e:
        logger.error(f"Error replacing selected text: {e}")
        return False


def get_cursor_position() -> Tuple[int, int]:
    """
    Get the current cursor position.
    
    Returns:
        Tuple of (line, column) or (0, 0) if unavailable
    """
    if not GEANY_AVAILABLE:
        logger.warning("Geany not available")
        return (0, 0)
    
    try:
        current_doc = get_current_document()
        if not current_doc or not current_doc.editor:
            return (0, 0)
        
        # This is a simplified version - actual implementation would need
        # to use Scintilla editor methods to get cursor position
        # For now, return placeholder
        return (1, 1)  # Placeholder
        
    except Exception as e:
        logger.error(f"Error getting cursor position: {e}")
        return (0, 0)


def get_document_text() -> Optional[str]:
    """
    Get the full text of the current document.
    
    Returns:
        Document text or None if unavailable
    """
    if not GEANY_AVAILABLE:
        logger.warning("Geany not available")
        return None
    
    try:
        current_doc = get_current_document()
        if not current_doc:
            return None
        
        # This is a simplified version - actual implementation would need
        # to use Scintilla editor methods to get document text
        # For now, return placeholder
        return ""  # Placeholder
        
    except Exception as e:
        logger.error(f"Error getting document text: {e}")
        return None


def insert_text_at_cursor(text: str) -> bool:
    """
    Insert text at the current cursor position.
    
    Args:
        text: Text to insert
        
    Returns:
        True if successful, False otherwise
    """
    if not GEANY_AVAILABLE:
        logger.warning("Geany not available")
        return False
    
    try:
        current_doc = get_current_document()
        if not current_doc or not current_doc.editor:
            return False
        
        # This is a simplified version - actual implementation would need
        # to use Scintilla editor methods to insert text
        logger.info(f"Would insert text at cursor: {text[:50]}...")
        return True  # Placeholder
        
    except Exception as e:
        logger.error(f"Error inserting text at cursor: {e}")
        return False


def get_line_text(line_number: int) -> Optional[str]:
    """
    Get the text of a specific line.
    
    Args:
        line_number: Line number (1-based)
        
    Returns:
        Line text or None if unavailable
    """
    if not GEANY_AVAILABLE:
        logger.warning("Geany not available")
        return None
    
    try:
        current_doc = get_current_document()
        if not current_doc or not current_doc.editor:
            return None
        
        # This is a simplified version - actual implementation would need
        # to use Scintilla editor methods to get line text
        return ""  # Placeholder
        
    except Exception as e:
        logger.error(f"Error getting line text: {e}")
        return None


def get_document_info() -> dict:
    """
    Get information about the current document.
    
    Returns:
        Dictionary with document information
    """
    if not GEANY_AVAILABLE:
        logger.warning("Geany not available")
        return {}
    
    try:
        current_doc = get_current_document()
        if not current_doc:
            return {}
        
        info = {
            "filename": getattr(current_doc, 'file_name', 'Untitled'),
            "is_modified": getattr(current_doc, 'text_changed', False),
            "encoding": getattr(current_doc, 'encoding', 'utf-8'),
            "has_selection": False,  # Placeholder
            "cursor_line": 1,  # Placeholder
            "cursor_column": 1,  # Placeholder
            "total_lines": 0,  # Placeholder
        }
        
        # Get file type information
        if hasattr(current_doc, 'file_type') and current_doc.file_type:
            info["language"] = current_doc.file_type.name
            info["file_extension"] = current_doc.file_type.extension
        else:
            info["language"] = "text"
            info["file_extension"] = ""
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting document info: {e}")
        return {}


def show_message_dialog(title: str, message: str, message_type: str = "info"):
    """
    Show a message dialog to the user.
    
    Args:
        title: Dialog title
        message: Message to display
        message_type: Type of message (info, warning, error)
    """
    if not GTK_AVAILABLE:
        logger.warning("GTK not available for dialogs")
        logger.info(f"{title}: {message}")
        return
    
    try:
        # Map message types to GTK message types
        type_map = {
            "info": gtk.MESSAGE_INFO,
            "warning": gtk.MESSAGE_WARNING,
            "error": gtk.MESSAGE_ERROR,
            "question": gtk.MESSAGE_QUESTION
        }
        
        gtk_type = type_map.get(message_type, gtk.MESSAGE_INFO)
        
        dialog = gtk.MessageDialog(
            parent=None,
            flags=gtk.DIALOG_MODAL,
            type=gtk_type,
            buttons=gtk.BUTTONS_OK,
            message_format=message
        )
        
        dialog.set_title(title)
        dialog.run()
        dialog.destroy()
        
    except Exception as e:
        logger.error(f"Error showing message dialog: {e}")
        logger.info(f"{title}: {message}")


def show_error_dialog(title: str, error_message: str):
    """
    Show an error dialog to the user.
    
    Args:
        title: Dialog title
        error_message: Error message to display
    """
    show_message_dialog(title, error_message, "error")


def show_confirmation_dialog(title: str, message: str) -> bool:
    """
    Show a confirmation dialog to the user.
    
    Args:
        title: Dialog title
        message: Message to display
        
    Returns:
        True if user confirmed, False otherwise
    """
    if not GTK_AVAILABLE:
        logger.warning("GTK not available for dialogs")
        logger.info(f"{title}: {message}")
        return False
    
    try:
        dialog = gtk.MessageDialog(
            parent=None,
            flags=gtk.DIALOG_MODAL,
            type=gtk.MESSAGE_QUESTION,
            buttons=gtk.BUTTONS_YES_NO,
            message_format=message
        )
        
        dialog.set_title(title)
        response = dialog.run()
        dialog.destroy()
        
        return response == gtk.RESPONSE_YES
        
    except Exception as e:
        logger.error(f"Error showing confirmation dialog: {e}")
        return False


def get_plugin_data_dir() -> str:
    """
    Get the plugin data directory path.
    
    Returns:
        Plugin data directory path
    """
    try:
        # Try to get Geany's config directory
        if GEANY_AVAILABLE and hasattr(geany, 'app') and hasattr(geany.app, 'configdir'):
            from pathlib import Path
            base_dir = Path(geany.app.configdir)
        else:
            from pathlib import Path
            base_dir = Path.home() / ".config" / "geany"
        
        plugin_dir = base_dir / "plugins" / "geanylua" / "geany-copilot-python"
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        return str(plugin_dir)
        
    except Exception as e:
        logger.error(f"Error getting plugin data directory: {e}")
        from pathlib import Path
        fallback_dir = Path.home() / ".geany-copilot-python"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return str(fallback_dir)


def is_geany_available() -> bool:
    """
    Check if Geany is available.
    
    Returns:
        True if Geany is available, False otherwise
    """
    return GEANY_AVAILABLE


def is_gtk_available() -> bool:
    """
    Check if GTK is available.
    
    Returns:
        True if GTK is available, False otherwise
    """
    return GTK_AVAILABLE


def safe_execute(func, *args, **kwargs):
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or None if error occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {e}")
        return None
