"""
Utility modules for Geany Copilot Python plugin.

This module contains helper functions, logging setup, and other
utility components used throughout the plugin.
"""

from .logging_setup import setup_logging
from .helpers import (
    get_selected_text,
    replace_selected_text,
    get_cursor_position,
    get_current_document,
    show_message_dialog,
    show_error_dialog
)

__all__ = [
    'setup_logging',
    'get_selected_text',
    'replace_selected_text', 
    'get_cursor_position',
    'get_current_document',
    'show_message_dialog',
    'show_error_dialog'
]
