"""
User interface components for Geany Copilot Python plugin.

This module contains GTK-based UI components for the plugin including
dialogs, widgets, and user interaction elements.
"""

try:
    from .dialogs import CodeAssistantDialog, CopywriterDialog, SettingsDialog
    from .widgets import ChatWidget, ProgressWidget, StatusWidget

    __all__ = [
        'CodeAssistantDialog',
        'CopywriterDialog',
        'SettingsDialog',
        'ChatWidget',
        'ProgressWidget',
        'StatusWidget'
    ]
except ImportError as e:
    # Handle case where GTK is not available
    import logging
    logging.getLogger(__name__).warning(f"UI components not available: {e}")

    __all__ = []
