"""
Configuration management for Geany Copilot Python plugin.

This module handles loading, saving, and managing plugin configuration
with support for JSON-based settings compatible with the original Lua version.
"""

import os
import json
import logging
import stat
from typing import Dict, Any, Optional
from pathlib import Path

from .credentials import CredentialManager


class ConfigManager:
    """
    Manages plugin configuration with JSON-based storage.
    
    Provides compatibility with the original Lua plugin's configuration
    approach while adding enhanced features for the Python agent system.
    """
    
    # Default configuration values
    DEFAULT_CONFIG = {
        # API Configuration
        "api": {
            "primary_provider": "deepseek",
            "deepseek": {
                "base_url": "https://api.deepseek.com",
                "api_key": "",
                "model": "deepseek-chat",
                "max_tokens": 2048,
                "temperature": 0.1
            },
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "api_key": "",
                "model": "gpt-4o-mini",
                "max_tokens": 2048,
                "temperature": 0.1
            },
            "custom": {
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",
                "model": "llama3.2",
                "max_tokens": 2048,
                "temperature": 0.1
            }
        },
        
        # Agent Configuration
        "agents": {
            "code_assistant": {
                "enabled": True,
                "context_length": 200,
                "max_conversation_turns": 10,
                "auto_apply_suggestions": False,
                "show_reasoning": True
            },
            "copywriter": {
                "enabled": True,
                "replace_selection": True,
                "max_conversation_turns": 5,
                "iterative_improvements": True
            }
        },
        
        # UI Configuration
        "ui": {
            "show_welcome_dialog": True,
            "dialog_width": 800,
            "dialog_height": 600,
            "font_size": 10
        },

        # Performance Configuration
        "performance": {
            "cache": {
                "max_size": 100,
                "max_memory_mb": 50.0,
                "ttl": 3600.0  # 1 hour
            },
            "debounce": {
                "delay": 0.5  # 500ms
            },
            "memory": {
                "auto_cleanup": True,
                "cleanup_interval": 300,  # 5 minutes
                "max_memory_mb": 200.0,
                "max_conversations": 10,  # Maximum number of conversations to keep
                "max_conversation_age_hours": 24,  # Maximum age of conversations in hours
                "max_turns_per_conversation": 50  # Maximum turns per conversation
            },
            "timeouts": {
                "default": 30,  # Default timeout in seconds
                "completion": 45,  # Code completion timeout
                "streaming": 60,  # Streaming response timeout
                "test_connection": 10,  # Connection test timeout
                "max_response_size": 10485760,  # 10MB max response size
                "max_chunks": 10000  # Maximum streaming chunks
            },
            "error_handling": {
                "max_errors_per_hour": 50,  # Maximum errors before degradation
                "retry_attempts": 3,  # Default retry attempts
                "retry_delay": 1.0,  # Base retry delay in seconds
                "circuit_breaker_timeout": 300,  # Circuit breaker timeout in seconds
                "enable_graceful_degradation": True  # Enable graceful degradation
            }
        },

        # System Prompts (will be loaded from separate files)
        "prompts": {
            "code_assistant": "",
            "copywriter": ""
        }
    }
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.logger = logging.getLogger(__name__)
        self.config_dir = self._get_config_directory()
        self.config_file = self.config_dir / "config.json"
        self.prompts_dir = self.config_dir / "prompts"

        # Initialize credential manager
        self.credential_manager = CredentialManager()

        # Ensure directories exist with secure permissions
        self._create_secure_directories()

        # Load configuration
        self.config = self._load_config()
        self._load_prompts()

        # Migrate API keys to secure storage if needed
        self._migrate_api_keys_if_needed()
    
    def _get_config_directory(self) -> Path:
        """Get the configuration directory path."""
        try:
            # Try to get Geany's config directory
            import geany
            if hasattr(geany, 'app') and hasattr(geany.app, 'configdir'):
                base_dir = Path(geany.app.configdir)
            else:
                base_dir = Path.home() / ".config" / "geany"
        except ImportError:
            # Fallback when not running in Geany
            base_dir = Path.home() / ".config" / "geany"
        
        return base_dir / "plugins" / "geanylua" / "geany-copilot-python"

    def _create_secure_directories(self):
        """Create configuration directories with secure permissions."""
        try:
            # Create config directory with restricted permissions (700 - owner only)
            self.config_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(self.config_dir, stat.S_IRWXU)  # 700 permissions

            # Create prompts directory
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(self.prompts_dir, stat.S_IRWXU)  # 700 permissions

            self.logger.debug(f"Created secure directories: {self.config_dir}")

        except Exception as e:
            self.logger.warning(f"Could not set secure directory permissions: {e}")

    def _migrate_api_keys_if_needed(self):
        """Migrate API keys from config file to secure storage if needed."""
        try:
            # Check if we have API keys in config that should be migrated
            api_config = self.config.get('api', {})
            has_keys_in_config = False

            for provider, provider_config in api_config.items():
                if provider == 'primary_provider':
                    continue

                if isinstance(provider_config, dict) and provider_config.get('api_key'):
                    api_key = provider_config['api_key']
                    if api_key and api_key != "your-api-key-here" and api_key != "":
                        has_keys_in_config = True
                        break

            if has_keys_in_config and self.credential_manager.is_keyring_available():
                self.logger.info("Migrating API keys from config file to secure storage...")
                if self.credential_manager.migrate_from_config(self.config):
                    # Clear API keys from config after successful migration
                    self._clear_api_keys_from_config()
                    self.save_config()
                    self.logger.info("API key migration completed successfully")

        except Exception as e:
            self.logger.warning(f"API key migration failed: {e}")

    def _clear_api_keys_from_config(self):
        """Clear API keys from config after migration to secure storage."""
        api_config = self.config.get('api', {})

        for provider, provider_config in api_config.items():
            if provider == 'primary_provider':
                continue

            if isinstance(provider_config, dict) and 'api_key' in provider_config:
                provider_config['api_key'] = ""

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults to ensure all keys exist
                config = self._deep_merge(self.DEFAULT_CONFIG.copy(), loaded_config)
                self.logger.info(f"Configuration loaded from {self.config_file}")
                return config
            else:
                self.logger.info("No existing configuration found, using defaults")
                return self.DEFAULT_CONFIG.copy()
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return self.DEFAULT_CONFIG.copy()
    
    def _load_prompts(self):
        """Load system prompts from separate files."""
        try:
            # Load code assistant prompt
            code_prompt_file = self.prompts_dir / "code_assistant.txt"
            if code_prompt_file.exists():
                with open(code_prompt_file, 'r', encoding='utf-8') as f:
                    self.config["prompts"]["code_assistant"] = f.read().strip()
            else:
                self.config["prompts"]["code_assistant"] = self._get_default_code_prompt()
                self._save_prompt("code_assistant", self.config["prompts"]["code_assistant"])
            
            # Load copywriter prompt
            copywriter_prompt_file = self.prompts_dir / "copywriter.txt"
            if copywriter_prompt_file.exists():
                with open(copywriter_prompt_file, 'r', encoding='utf-8') as f:
                    self.config["prompts"]["copywriter"] = f.read().strip()
            else:
                self.config["prompts"]["copywriter"] = self._get_default_copywriter_prompt()
                self._save_prompt("copywriter", self.config["prompts"]["copywriter"])
                
        except Exception as e:
            self.logger.error(f"Error loading prompts: {e}")
    
    def _get_default_code_prompt(self) -> str:
        """Get the default code assistant system prompt."""
        return """You are an intelligent AI coding assistant integrated into the Geany IDE. Your role is to provide expert-level code analysis, suggestions, and assistance.

Key capabilities:
- Analyze code context and provide intelligent completions
- Suggest code improvements and refactoring opportunities
- Explain complex code patterns and algorithms
- Help debug issues and identify potential problems
- Provide best practices and coding standards guidance
- Support multiple programming languages

Guidelines:
- Always consider the full context of the code
- Provide clear, actionable suggestions
- Explain your reasoning when helpful
- Maintain code style consistency
- Focus on practical, implementable solutions
- Ask clarifying questions when context is unclear

When providing code suggestions:
1. Preserve existing indentation and formatting
2. Consider the programming language and its conventions
3. Ensure suggestions are syntactically correct
4. Provide brief explanations for complex changes"""
    
    def _get_default_copywriter_prompt(self) -> str:
        """Get the default copywriter system prompt."""
        return """You are a professional copywriting assistant and writing coach integrated into the Geany IDE. Your role is to help improve written content through analysis, suggestions, and iterative refinement.

Key capabilities:
- Analyze writing for clarity, tone, and effectiveness
- Suggest improvements for grammar, style, and structure
- Help develop compelling arguments and narratives
- Provide feedback on different types of content
- Assist with creative writing and technical documentation
- Support iterative improvement processes

Guidelines:
- Maintain the author's voice and intent
- Provide constructive, actionable feedback
- Consider the target audience and purpose
- Suggest specific improvements with explanations
- Support both creative and technical writing
- Encourage iterative refinement

When reviewing text:
1. Assess overall structure and flow
2. Identify areas for improvement
3. Suggest specific changes with rationale
4. Maintain appropriate tone and style
5. Focus on clarity and impact"""
    
    def _save_prompt(self, prompt_type: str, content: str):
        """Save a system prompt to file."""
        try:
            prompt_file = self.prompts_dir / f"{prompt_type}.txt"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.debug(f"Saved {prompt_type} prompt to {prompt_file}")
        except Exception as e:
            self.logger.error(f"Error saving {prompt_type} prompt: {e}")
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base
    
    def save_config(self):
        """Save current configuration to file with secure permissions."""
        try:
            # Save config file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            # Set secure permissions (600 - owner read/write only)
            os.chmod(self.config_file, stat.S_IRUSR | stat.S_IWUSR)

            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the configuration key
            default: Default value if key is not found
            
        Returns:
            The configuration value or default
        """
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting config value for {key_path}: {e}")
            return default
    
    def set(self, key_path: str, value: Any):
        """
        Set a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the configuration key
            value: Value to set
        """
        try:
            keys = key_path.split('.')
            config = self.config
            
            # Navigate to the parent dictionary
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # Set the final value
            config[keys[-1]] = value
            
        except Exception as e:
            self.logger.error(f"Error setting config value for {key_path}: {e}")
    
    def get_api_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get API configuration for the specified provider with secure API key retrieval.

        Args:
            provider: API provider name (defaults to primary_provider)

        Returns:
            API configuration dictionary with API key from secure storage
        """
        if provider is None:
            provider = self.get("api.primary_provider", "deepseek")

        # Get base config from file
        config = self.get(f"api.{provider}", {}).copy()

        # Override API key with secure storage
        secure_api_key = self.credential_manager.get_api_key(provider)
        if secure_api_key:
            config['api_key'] = secure_api_key
        elif not config.get('api_key'):
            # No API key found in secure storage or config
            self.logger.warning(
                f"No API key found for provider '{provider}'. "
                f"Set it using environment variable {provider.upper()}_API_KEY "
                f"or store it securely using the credential manager."
            )

        return config

    def set_api_key(self, provider: str, api_key: str) -> bool:
        """
        Set API key for a provider using secure storage.

        Args:
            provider: API provider name
            api_key: API key to store

        Returns:
            True if stored successfully, False otherwise
        """
        if not self.credential_manager.validate_api_key(api_key):
            self.logger.error(f"Invalid API key format for provider: {provider}")
            return False

        success = self.credential_manager.store_api_key(provider, api_key)
        if success:
            # Clear any API key from config file
            api_config = self.config.get('api', {})
            if provider in api_config and isinstance(api_config[provider], dict):
                api_config[provider]['api_key'] = ""
                self.save_config()

        return success

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a provider from secure storage.

        Args:
            provider: API provider name

        Returns:
            API key if found, None otherwise
        """
        return self.credential_manager.get_api_key(provider)

    def delete_api_key(self, provider: str) -> bool:
        """
        Delete API key for a provider from secure storage.

        Args:
            provider: API provider name

        Returns:
            True if deleted successfully, False otherwise
        """
        return self.credential_manager.delete_api_key(provider)

    def get_security_status(self) -> Dict[str, Any]:
        """
        Get security status information.

        Returns:
            Dictionary with security status details
        """
        return self.credential_manager.get_security_status()

    def get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """
        Get configuration for the specified agent type.
        
        Args:
            agent_type: Type of agent (code_assistant, copywriter)
            
        Returns:
            Agent configuration dictionary
        """
        return self.get(f"agents.{agent_type}", {})
    
    def get_prompt(self, prompt_type: str) -> str:
        """
        Get system prompt for the specified type.
        
        Args:
            prompt_type: Type of prompt (code_assistant, copywriter)
            
        Returns:
            System prompt string
        """
        return self.get(f"prompts.{prompt_type}", "")
    
    def update_prompt(self, prompt_type: str, content: str):
        """
        Update and save a system prompt.
        
        Args:
            prompt_type: Type of prompt (code_assistant, copywriter)
            content: New prompt content
        """
        self.set(f"prompts.{prompt_type}", content)
        self._save_prompt(prompt_type, content)
