"""
Specialized agents for Geany Copilot Python plugin.

This module contains specialized AI agents for different types of assistance,
including code analysis and copywriting.
"""

from .code_assistant import CodeAssistant
from .copywriter import CopywriterAssistant

__all__ = [
    'CodeAssistant',
    'CopywriterAssistant'
]
