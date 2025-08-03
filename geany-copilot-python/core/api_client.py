"""
API client for Geany Copilot Python plugin.

This module provides a flexible API client that supports DeepSeek and other
OpenAI-compatible APIs with automatic failover and configuration management.
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional, Iterator, Union
from dataclasses import dataclass
from enum import Enum


class APIProvider(Enum):
    """Supported API providers."""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    CUSTOM = "custom"


@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format for API calls."""
        return {"role": self.role, "content": self.content}


@dataclass
class APIResponse:
    """Represents an API response."""
    success: bool
    content: str
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None
    reasoning: Optional[str] = None  # For reasoning models like DeepSeek-R1


class APIClient:
    """
    Flexible API client supporting multiple OpenAI-compatible providers.
    
    Provides automatic failover, request/response handling, and streaming support
    for AI model interactions.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the API client.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # Set default timeout and headers
        self.session.timeout = 30
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Geany-Copilot-Python/1.0.0'
        })
    
    def _get_provider_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for the specified provider."""
        if provider is None:
            provider = self.config_manager.get("api.primary_provider", "deepseek")
        
        return self.config_manager.get_api_config(provider)
    
    def _prepare_request(self, messages: List[ChatMessage], 
                        provider: Optional[str] = None,
                        **kwargs) -> tuple[str, Dict[str, str], Dict[str, Any]]:
        """
        Prepare API request parameters.
        
        Args:
            messages: List of chat messages
            provider: API provider to use
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (url, headers, payload)
        """
        config = self._get_provider_config(provider)
        
        if not config:
            raise ValueError(f"No configuration found for provider: {provider}")
        
        # Build URL
        base_url = config.get("base_url", "").rstrip('/')
        if not base_url.endswith('/chat/completions'):
            if base_url.endswith('/v1'):
                url = f"{base_url}/chat/completions"
            else:
                url = f"{base_url}/v1/chat/completions"
        else:
            url = base_url
        
        # Build headers
        headers = {
            'Authorization': f'Bearer {config.get("api_key", "")}',
            'Content-Type': 'application/json'
        }
        
        # Build payload
        payload = {
            'model': kwargs.get('model', config.get('model', 'gpt-3.5-turbo')),
            'messages': [msg.to_dict() for msg in messages],
            'temperature': kwargs.get('temperature', config.get('temperature', 0.1)),
            'max_tokens': kwargs.get('max_tokens', config.get('max_tokens', 2048)),
            'stream': kwargs.get('stream', False)
        }
        
        # Add additional parameters if provided
        for key in ['top_p', 'frequency_penalty', 'presence_penalty', 'stop']:
            if key in kwargs:
                payload[key] = kwargs[key]
        
        return url, headers, payload
    
    def chat_completion(self, messages: List[ChatMessage], 
                       provider: Optional[str] = None,
                       **kwargs) -> APIResponse:
        """
        Send a chat completion request.
        
        Args:
            messages: List of chat messages
            provider: API provider to use
            **kwargs: Additional parameters
            
        Returns:
            APIResponse object
        """
        try:
            url, headers, payload = self._prepare_request(messages, provider, **kwargs)
            
            self.logger.debug(f"Sending request to {url}")
            self.logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = self.session.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_response(data)
            else:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg += f": {error_data['error'].get('message', 'Unknown error')}"
                except:
                    error_msg += f": {response.text}"
                
                self.logger.error(error_msg)
                return APIResponse(success=False, content="", error=error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.logger.error(error_msg)
            return APIResponse(success=False, content="", error=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            return APIResponse(success=False, content="", error=error_msg)
    
    def chat_completion_stream(self, messages: List[ChatMessage],
                              provider: Optional[str] = None,
                              **kwargs) -> Iterator[APIResponse]:
        """
        Send a streaming chat completion request.
        
        Args:
            messages: List of chat messages
            provider: API provider to use
            **kwargs: Additional parameters
            
        Yields:
            APIResponse objects for each chunk
        """
        try:
            kwargs['stream'] = True
            url, headers, payload = self._prepare_request(messages, provider, **kwargs)
            
            self.logger.debug(f"Sending streaming request to {url}")
            
            response = self.session.post(url, headers=headers, json=payload, stream=True)
            
            if response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg += f": {error_data['error'].get('message', 'Unknown error')}"
                except:
                    error_msg += f": {response.text}"
                
                yield APIResponse(success=False, content="", error=error_msg)
                return
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            chunk_response = self._parse_stream_chunk(data)
                            if chunk_response:
                                yield chunk_response
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.logger.error(error_msg)
            yield APIResponse(success=False, content="", error=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            yield APIResponse(success=False, content="", error=error_msg)
    
    def _parse_response(self, data: Dict[str, Any]) -> APIResponse:
        """Parse a complete API response."""
        try:
            if 'choices' in data and len(data['choices']) > 0:
                choice = data['choices'][0]
                message = choice.get('message', {})
                content = message.get('content', '')
                
                # Extract reasoning for reasoning models
                reasoning = None
                if 'reasoning_content' in message:
                    reasoning = message['reasoning_content']
                
                # Extract usage information
                usage = data.get('usage', {})
                model = data.get('model', '')
                
                return APIResponse(
                    success=True,
                    content=content,
                    usage=usage,
                    model=model,
                    reasoning=reasoning
                )
            else:
                return APIResponse(
                    success=False,
                    content="",
                    error="No choices in response"
                )
                
        except Exception as e:
            return APIResponse(
                success=False,
                content="",
                error=f"Error parsing response: {str(e)}"
            )
    
    def _parse_stream_chunk(self, data: Dict[str, Any]) -> Optional[APIResponse]:
        """Parse a streaming response chunk."""
        try:
            if 'choices' in data and len(data['choices']) > 0:
                choice = data['choices'][0]
                delta = choice.get('delta', {})
                content = delta.get('content', '')
                
                if content:
                    return APIResponse(
                        success=True,
                        content=content,
                        model=data.get('model', '')
                    )
            
            return None
            
        except Exception as e:
            return APIResponse(
                success=False,
                content="",
                error=f"Error parsing stream chunk: {str(e)}"
            )
    
    def test_connection(self, provider: Optional[str] = None) -> APIResponse:
        """
        Test connection to the API provider.
        
        Args:
            provider: API provider to test
            
        Returns:
            APIResponse indicating success or failure
        """
        test_messages = [
            ChatMessage(role="user", content="Hello, this is a connection test.")
        ]
        
        try:
            response = self.chat_completion(
                messages=test_messages,
                provider=provider,
                max_tokens=10
            )
            
            if response.success:
                return APIResponse(
                    success=True,
                    content="Connection test successful",
                    model=response.model
                )
            else:
                return response
                
        except Exception as e:
            return APIResponse(
                success=False,
                content="",
                error=f"Connection test failed: {str(e)}"
            )
    
    def get_available_providers(self) -> List[str]:
        """Get list of configured API providers."""
        providers = []
        
        for provider in APIProvider:
            config = self._get_provider_config(provider.value)
            if config and config.get('api_key'):
                providers.append(provider.value)
        
        return providers
    
    def cleanup(self):
        """Cleanup resources."""
        if self.session:
            self.session.close()
