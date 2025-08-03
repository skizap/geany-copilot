"""
Core module for Geany Copilot Python plugin.

This module contains the fundamental components for the AI agent system,
including configuration management, API clients, and context analysis.
"""

from .config import ConfigManager
from .agent import AIAgent
from .api_client import APIClient
from .context import ContextAnalyzer

__all__ = [
    'ConfigManager',
    'AIAgent', 
    'APIClient',
    'ContextAnalyzer'
]
