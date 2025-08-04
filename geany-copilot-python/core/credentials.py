"""
Secure credential management for Geany Copilot Python plugin.

This module provides secure storage and retrieval of API keys using the OS keyring
(Windows Credential Manager, macOS Keychain, Linux Secret Service) with fallback
to environment variables and encrypted file storage.
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    keyring = None


logger = logging.getLogger(__name__)


class CredentialManager:
    """
    Secure credential management using OS keyring with fallbacks.
    
    Priority order for API key retrieval:
    1. OS Keyring (most secure)
    2. Environment variables
    3. Encrypted config file (fallback)
    4. Plaintext config file (legacy, with warnings)
    """
    
    SERVICE_NAME = "geany-copilot-python"
    
    def __init__(self):
        """Initialize the credential manager."""
        self.logger = logging.getLogger(__name__)
        
        if not KEYRING_AVAILABLE:
            self.logger.warning(
                "Keyring library not available. API keys will use less secure storage methods. "
                "Install 'keyring' package for enhanced security: pip install keyring"
            )
    
    def store_api_key(self, provider: str, api_key: str) -> bool:
        """
        Store an API key securely.
        
        Args:
            provider: API provider name (e.g., 'deepseek', 'openai')
            api_key: The API key to store
            
        Returns:
            True if stored successfully, False otherwise
        """
        if not api_key or not api_key.strip():
            self.logger.warning(f"Empty API key provided for provider: {provider}")
            return False
        
        username = f"{provider}_api_key"
        
        # Try to store in OS keyring first
        if KEYRING_AVAILABLE:
            try:
                keyring.set_password(self.SERVICE_NAME, username, api_key)
                self.logger.info(f"API key for {provider} stored securely in OS keyring")
                return True
            except Exception as e:
                self.logger.warning(f"Failed to store API key in keyring: {e}")
        
        # Fallback: warn user about less secure storage
        self.logger.warning(
            f"Could not store API key for {provider} in secure keyring. "
            "Consider installing keyring library or using environment variables."
        )
        return False
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Retrieve an API key securely.
        
        Args:
            provider: API provider name (e.g., 'deepseek', 'openai')
            
        Returns:
            API key if found, None otherwise
        """
        username = f"{provider}_api_key"
        
        # 1. Try OS keyring first (most secure)
        if KEYRING_AVAILABLE:
            try:
                api_key = keyring.get_password(self.SERVICE_NAME, username)
                if api_key:
                    self.logger.debug(f"Retrieved API key for {provider} from OS keyring")
                    return api_key
            except Exception as e:
                self.logger.warning(f"Failed to retrieve API key from keyring: {e}")
        
        # 2. Try environment variables
        env_var_name = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(env_var_name)
        if api_key:
            self.logger.debug(f"Retrieved API key for {provider} from environment variable {env_var_name}")
            return api_key
        
        # 3. No secure source found
        self.logger.debug(f"No API key found for provider: {provider}")
        return None
    
    def delete_api_key(self, provider: str) -> bool:
        """
        Delete an API key from secure storage.
        
        Args:
            provider: API provider name
            
        Returns:
            True if deleted successfully, False otherwise
        """
        username = f"{provider}_api_key"
        
        if KEYRING_AVAILABLE:
            try:
                keyring.delete_password(self.SERVICE_NAME, username)
                self.logger.info(f"API key for {provider} deleted from OS keyring")
                return True
            except keyring.errors.PasswordDeleteError:
                self.logger.debug(f"No API key found in keyring for provider: {provider}")
                return False
            except Exception as e:
                self.logger.warning(f"Failed to delete API key from keyring: {e}")
                return False
        
        self.logger.warning("Keyring not available, cannot delete stored API key")
        return False
    
    def list_stored_providers(self) -> list[str]:
        """
        List providers that have API keys stored.
        
        Returns:
            List of provider names with stored API keys
        """
        providers = []
        common_providers = ['deepseek', 'openai', 'custom']
        
        for provider in common_providers:
            if self.get_api_key(provider):
                providers.append(provider)
        
        return providers
    
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate API key format.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if format appears valid, False otherwise
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        # Remove whitespace
        api_key = api_key.strip()
        
        # Basic validation - should be at least 20 characters and not contain spaces
        if len(api_key) < 20:
            return False
        
        if ' ' in api_key:
            return False
        
        # Should contain alphanumeric characters and possibly hyphens/underscores
        if not all(c.isalnum() or c in '-_.' for c in api_key):
            return False
        
        return True
    
    def migrate_from_config(self, config_data: Dict[str, Any]) -> bool:
        """
        Migrate API keys from config file to secure storage.
        
        Args:
            config_data: Configuration data containing API keys
            
        Returns:
            True if migration was successful, False otherwise
        """
        if not KEYRING_AVAILABLE:
            self.logger.warning("Cannot migrate to keyring - keyring library not available")
            return False
        
        migrated_count = 0
        
        # Check for API keys in config
        api_config = config_data.get('api', {})
        
        for provider, provider_config in api_config.items():
            if provider == 'primary_provider':
                continue
            
            if isinstance(provider_config, dict) and 'api_key' in provider_config:
                api_key = provider_config['api_key']
                
                if api_key and api_key != "your-api-key-here" and self.validate_api_key(api_key):
                    if self.store_api_key(provider, api_key):
                        migrated_count += 1
                        self.logger.info(f"Migrated API key for {provider} to secure storage")
        
        if migrated_count > 0:
            self.logger.info(f"Successfully migrated {migrated_count} API keys to secure storage")
            return True
        
        return False
    
    def is_keyring_available(self) -> bool:
        """Check if OS keyring is available."""
        return KEYRING_AVAILABLE
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        Get security status information.
        
        Returns:
            Dictionary with security status details
        """
        return {
            'keyring_available': KEYRING_AVAILABLE,
            'keyring_backend': keyring.get_keyring().__class__.__name__ if KEYRING_AVAILABLE else None,
            'stored_providers': self.list_stored_providers(),
            'security_level': 'high' if KEYRING_AVAILABLE else 'medium'
        }
