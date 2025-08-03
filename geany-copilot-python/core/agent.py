"""
AI Agent core for Geany Copilot Python plugin.

This module provides the intelligent agent system with context analysis,
multi-turn conversations, and decision-making capabilities.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .api_client import APIClient, ChatMessage, APIResponse
from .context import ContextAnalyzer


class ConversationState(Enum):
    """States of a conversation."""
    IDLE = "idle"
    THINKING = "thinking"
    RESPONDING = "responding"
    WAITING_FOR_INPUT = "waiting_for_input"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ConversationTurn:
    """Represents a single turn in a conversation."""
    timestamp: datetime
    user_message: str
    assistant_response: str
    context: Optional[str] = None
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """Represents a multi-turn conversation."""
    id: str
    agent_type: str
    state: ConversationState
    turns: List[ConversationTurn] = field(default_factory=list)
    context: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_turn(self, user_message: str, assistant_response: str, 
                 context: Optional[str] = None, reasoning: Optional[str] = None,
                 **metadata):
        """Add a new turn to the conversation."""
        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_message=user_message,
            assistant_response=assistant_response,
            context=context,
            reasoning=reasoning,
            metadata=metadata
        )
        self.turns.append(turn)
        self.updated_at = datetime.now()
    
    def get_messages_for_api(self, system_prompt: str, 
                           include_context: bool = True) -> List[ChatMessage]:
        """Convert conversation to API messages format."""
        messages = [ChatMessage(role="system", content=system_prompt)]
        
        # Add initial context if available
        if include_context and self.context:
            messages.append(ChatMessage(
                role="system", 
                content=f"Context:\n{self.context}"
            ))
        
        # Add conversation turns
        for turn in self.turns:
            if include_context and turn.context:
                messages.append(ChatMessage(
                    role="system",
                    content=f"Updated context:\n{turn.context}"
                ))
            
            messages.append(ChatMessage(role="user", content=turn.user_message))
            messages.append(ChatMessage(role="assistant", content=turn.assistant_response))
        
        return messages


class AIAgent:
    """
    Intelligent AI agent with context awareness and conversation management.
    
    This class provides the core agent functionality including multi-turn
    conversations, context analysis, and intelligent decision-making.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the AI agent.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.api_client = APIClient(config_manager)
        self.context_analyzer = ContextAnalyzer()
        
        # Conversation management
        self.conversations: Dict[str, Conversation] = {}
        self.active_conversation: Optional[str] = None
        
        # Agent state
        self.is_busy = False
        self.last_error: Optional[str] = None
        
        # Callbacks for UI updates
        self.on_thinking_start: Optional[Callable] = None
        self.on_thinking_end: Optional[Callable] = None
        self.on_response_chunk: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
    
    def start_conversation(self, agent_type: str, initial_context: str = "") -> str:
        """
        Start a new conversation.
        
        Args:
            agent_type: Type of agent (code_assistant, copywriter)
            initial_context: Initial context for the conversation
            
        Returns:
            Conversation ID
        """
        conversation_id = f"{agent_type}_{int(time.time())}"
        
        conversation = Conversation(
            id=conversation_id,
            agent_type=agent_type,
            state=ConversationState.IDLE,
            context=initial_context
        )
        
        self.conversations[conversation_id] = conversation
        self.active_conversation = conversation_id
        
        self.logger.info(f"Started new conversation: {conversation_id}")
        return conversation_id
    
    def continue_conversation(self, conversation_id: str, 
                            user_message: str,
                            updated_context: Optional[str] = None,
                            stream: bool = False) -> APIResponse:
        """
        Continue an existing conversation.
        
        Args:
            conversation_id: ID of the conversation to continue
            user_message: User's message
            updated_context: Updated context information
            stream: Whether to stream the response
            
        Returns:
            APIResponse object
        """
        if conversation_id not in self.conversations:
            error_msg = f"Conversation {conversation_id} not found"
            self.logger.error(error_msg)
            return APIResponse(success=False, content="", error=error_msg)
        
        conversation = self.conversations[conversation_id]
        conversation.state = ConversationState.THINKING
        
        if updated_context:
            conversation.context = updated_context
        
        try:
            self.is_busy = True
            if self.on_thinking_start:
                self.on_thinking_start()
            
            # Get system prompt for the agent type
            system_prompt = self.config_manager.get_prompt(conversation.agent_type)
            
            # Prepare messages
            messages = conversation.get_messages_for_api(system_prompt)
            messages.append(ChatMessage(role="user", content=user_message))
            
            # Get response
            if stream:
                return self._handle_streaming_response(conversation, user_message, messages)
            else:
                return self._handle_single_response(conversation, user_message, messages)
                
        except Exception as e:
            error_msg = f"Error in conversation: {str(e)}"
            self.logger.error(error_msg)
            conversation.state = ConversationState.ERROR
            
            if self.on_error:
                self.on_error(error_msg)
            
            return APIResponse(success=False, content="", error=error_msg)
        finally:
            self.is_busy = False
            if self.on_thinking_end:
                self.on_thinking_end()
    
    def _handle_single_response(self, conversation: Conversation, 
                               user_message: str, 
                               messages: List[ChatMessage]) -> APIResponse:
        """Handle a single (non-streaming) response."""
        conversation.state = ConversationState.RESPONDING
        
        response = self.api_client.chat_completion(messages)
        
        if response.success:
            conversation.add_turn(
                user_message=user_message,
                assistant_response=response.content,
                context=conversation.context,
                reasoning=response.reasoning,
                model=response.model,
                usage=response.usage
            )
            conversation.state = ConversationState.WAITING_FOR_INPUT
        else:
            conversation.state = ConversationState.ERROR
            if self.on_error:
                self.on_error(response.error or "Unknown error")
        
        return response
    
    def _handle_streaming_response(self, conversation: Conversation,
                                  user_message: str,
                                  messages: List[ChatMessage]) -> APIResponse:
        """Handle a streaming response."""
        conversation.state = ConversationState.RESPONDING
        
        full_response = ""
        last_response = None
        
        try:
            for chunk_response in self.api_client.chat_completion_stream(messages):
                if chunk_response.success:
                    full_response += chunk_response.content
                    if self.on_response_chunk:
                        self.on_response_chunk(chunk_response.content)
                    last_response = chunk_response
                else:
                    conversation.state = ConversationState.ERROR
                    if self.on_error:
                        self.on_error(chunk_response.error or "Streaming error")
                    return chunk_response
            
            # Add completed turn to conversation
            if full_response:
                conversation.add_turn(
                    user_message=user_message,
                    assistant_response=full_response,
                    context=conversation.context,
                    model=last_response.model if last_response else None
                )
                conversation.state = ConversationState.WAITING_FOR_INPUT
                
                return APIResponse(
                    success=True,
                    content=full_response,
                    model=last_response.model if last_response else None
                )
            else:
                error_msg = "No response received from streaming"
                conversation.state = ConversationState.ERROR
                return APIResponse(success=False, content="", error=error_msg)
                
        except Exception as e:
            error_msg = f"Streaming error: {str(e)}"
            conversation.state = ConversationState.ERROR
            if self.on_error:
                self.on_error(error_msg)
            return APIResponse(success=False, content="", error=error_msg)
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.conversations.get(conversation_id)
    
    def get_active_conversation(self) -> Optional[Conversation]:
        """Get the currently active conversation."""
        if self.active_conversation:
            return self.conversations.get(self.active_conversation)
        return None
    
    def end_conversation(self, conversation_id: str):
        """End a conversation."""
        if conversation_id in self.conversations:
            self.conversations[conversation_id].state = ConversationState.COMPLETED
            if self.active_conversation == conversation_id:
                self.active_conversation = None
            self.logger.info(f"Ended conversation: {conversation_id}")
    
    def clear_conversations(self):
        """Clear all conversations."""
        self.conversations.clear()
        self.active_conversation = None
        self.logger.info("Cleared all conversations")
    
    def analyze_context(self, context_type: str = "code") -> Optional[str]:
        """
        Analyze current editor context.
        
        Args:
            context_type: Type of context to analyze (code, writing)
            
        Returns:
            Formatted context string or None
        """
        try:
            if context_type == "code":
                context = self.context_analyzer.analyze_code_context()
                if context:
                    return self.context_analyzer.format_context_for_ai(context)
            elif context_type == "writing":
                context = self.context_analyzer.analyze_writing_context()
                if context:
                    return self.context_analyzer.format_context_for_ai(context)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error analyzing context: {e}")
            return None
    
    def test_connection(self) -> APIResponse:
        """Test connection to the API."""
        return self.api_client.test_connection()
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[str]:
        """Get a summary of a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        if not conversation.turns:
            return "No messages in conversation"
        
        turn_count = len(conversation.turns)
        last_turn = conversation.turns[-1]
        
        return f"Conversation with {turn_count} turns. Last message: {last_turn.user_message[:50]}..."
    
    def export_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Export a conversation to a dictionary."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        return {
            "id": conversation.id,
            "agent_type": conversation.agent_type,
            "state": conversation.state.value,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "context": conversation.context,
            "turns": [
                {
                    "timestamp": turn.timestamp.isoformat(),
                    "user_message": turn.user_message,
                    "assistant_response": turn.assistant_response,
                    "context": turn.context,
                    "reasoning": turn.reasoning,
                    "metadata": turn.metadata
                }
                for turn in conversation.turns
            ],
            "metadata": conversation.metadata
        }
    
    def cleanup(self):
        """Cleanup resources."""
        self.clear_conversations()
        if self.api_client:
            self.api_client.cleanup()
