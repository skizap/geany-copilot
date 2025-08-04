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
from datetime import datetime, timedelta

from .api_client import APIClient, ChatMessage, APIResponse
from .context import ContextAnalyzer
from .cache import PerformanceManager
from ..utils.error_handling import ErrorRecoveryManager, ErrorCategory, ErrorSeverity, with_error_handling
from ..utils.monitoring import PerformanceMonitor


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
    """Represents a multi-turn conversation with memory management."""
    id: str
    agent_type: str
    state: ConversationState
    turns: List[ConversationTurn] = field(default_factory=list)
    context: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    max_turns: int = 50  # Maximum number of turns to keep in memory
    
    def add_turn(self, user_message: str, assistant_response: str,
                 context: Optional[str] = None, reasoning: Optional[str] = None,
                 **metadata):
        """Add a new turn to the conversation with memory management."""
        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_message=user_message,
            assistant_response=assistant_response,
            context=context,
            reasoning=reasoning,
            metadata=metadata
        )
        self.turns.append(turn)

        # Update timestamps
        now = datetime.now()
        self.updated_at = now
        self.last_activity = now

        # Trim old turns if we exceed the maximum
        if len(self.turns) > self.max_turns:
            # Keep the most recent turns and remove the oldest
            excess_turns = len(self.turns) - self.max_turns
            self.turns = self.turns[excess_turns:]
            logging.getLogger(__name__).debug(
                f"Trimmed {excess_turns} old turns from conversation {self.id}"
            )
    
    def get_messages_for_api(self, system_prompt: str,
                           include_context: bool = True) -> List[ChatMessage]:
        """
        Convert conversation to API messages format with secure context handling.

        SECURITY: User-provided context is never treated as system messages to prevent
        privilege escalation and prompt injection attacks.
        """
        messages = [ChatMessage(role="system", content=system_prompt)]

        # Add conversation turns with context embedded in user messages
        for turn in self.turns:
            user_content = turn.user_message

            # Embed context in user message (not as system message) for security
            if include_context and turn.context:
                user_content = f"[Context: {turn.context}]\n\n{user_content}"

            messages.append(ChatMessage(role="user", content=user_content))
            messages.append(ChatMessage(role="assistant", content=turn.assistant_response))

        return messages

    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics for this conversation."""
        total_chars = 0
        total_turns = len(self.turns)

        # Calculate total character count
        for turn in self.turns:
            total_chars += len(turn.user_message) + len(turn.assistant_response)
            if turn.context:
                total_chars += len(turn.context)
            if turn.reasoning:
                total_chars += len(turn.reasoning)

        if self.context:
            total_chars += len(self.context)

        # Estimate memory usage (rough approximation)
        estimated_bytes = total_chars * 4  # Assuming UTF-8 encoding

        return {
            'total_turns': total_turns,
            'total_characters': total_chars,
            'estimated_bytes': estimated_bytes,
            'estimated_mb': estimated_bytes / (1024 * 1024),
            'max_turns': self.max_turns,
            'turns_remaining': max(0, self.max_turns - total_turns)
        }

    def trim_to_size(self, max_turns: Optional[int] = None):
        """Trim conversation to specified size."""
        if max_turns is None:
            max_turns = self.max_turns

        if len(self.turns) > max_turns:
            excess_turns = len(self.turns) - max_turns
            self.turns = self.turns[excess_turns:]
            self.updated_at = datetime.now()
            logging.getLogger(__name__).info(
                f"Trimmed {excess_turns} turns from conversation {self.id}"
            )


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

        # Performance management
        performance_config = config_manager.get('performance', {})
        self.performance_manager = PerformanceManager(performance_config)

        # Error recovery management
        max_errors_per_hour = config_manager.get('performance.error_handling.max_errors_per_hour', 50)
        self.error_manager = ErrorRecoveryManager(max_errors_per_hour)

        # Performance monitoring
        self.monitor = PerformanceMonitor()

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
    
    @with_error_handling(
        category=ErrorCategory.API,
        severity=ErrorSeverity.HIGH,
        retry_count=2,
        retry_delay=1.0,
        circuit_breaker="conversation_api"
    )
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

            # Monitor conversation start
            self.monitor.increment_counter("conversation.started")

            if self.on_thinking_start:
                self.on_thinking_start()
            
            # Get system prompt for the agent type
            system_prompt = self.config_manager.get_prompt(conversation.agent_type)
            
            # Prepare messages with secure context handling
            messages = conversation.get_messages_for_api(system_prompt)

            # Embed context in user message for security (never as system message)
            final_user_message = user_message
            if updated_context:
                final_user_message = f"[Context: {updated_context}]\n\n{user_message}"

            messages.append(ChatMessage(role="user", content=final_user_message))

            # Check cache for non-streaming requests with intelligent caching
            cache_key = None
            if not stream:
                # Use smart cache key generation
                cache_key = self.performance_manager.smart_cache_key(
                    conversation.agent_type, user_message, conversation.context or ""
                )
                cached_response = self.performance_manager.get_cached_response(cache_key)
                if cached_response:
                    self.logger.debug("Using cached response")
                    self.monitor.increment_counter("conversation.cache_hit")

                    # Add cached response to conversation
                    conversation.add_turn(
                        user_message=user_message,
                        assistant_response=cached_response.content,
                        context=conversation.context,
                        model=cached_response.model,
                        usage=cached_response.usage
                    )
                    conversation.state = ConversationState.WAITING_FOR_INPUT

                    # Trigger preloading for likely next requests
                    self.performance_manager.preload_likely_requests(
                        conversation.context or "", conversation.agent_type
                    )

                    return cached_response
                else:
                    self.monitor.increment_counter("conversation.cache_miss")

            # Get response
            if stream:
                return self._handle_streaming_response(conversation, user_message, messages)
            else:
                return self._handle_single_response(conversation, user_message, messages, cache_key)
                
        except Exception as e:
            # Record error with comprehensive context
            error_context = {
                'conversation_id': conversation_id,
                'user_message_length': len(user_message),
                'stream': stream,
                'has_context': bool(updated_context),
                'conversation_turns': len(conversation.turns) if conversation else 0
            }

            self.error_manager.record_error(
                e, ErrorCategory.API, ErrorSeverity.HIGH, error_context
            )

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
                               messages: List[ChatMessage],
                               cache_key: Optional[str] = None) -> APIResponse:
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

            # Cache successful response with intelligent features
            if cache_key:
                # Generate related cache keys for similar contexts
                related_keys = []
                if conversation.context:
                    # Create related keys for similar contexts
                    base_key = self.performance_manager.smart_cache_key(
                        conversation.agent_type, user_message, "", include_context_hash=False
                    )
                    related_keys.append(base_key)

                self.performance_manager.cache_response_with_relations(
                    cache_key, response, related_keys
                )
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

    def cleanup(self):
        """Cleanup agent resources and perform comprehensive maintenance."""
        try:
            self.logger.info("Starting agent cleanup")

            # Performance cleanup with auto-optimization
            self.performance_manager.cleanup()
            optimization_result = self.performance_manager.auto_optimize()
            if optimization_result:
                self.logger.info(f"Auto-optimization completed: {optimization_result}")

            # Memory management for conversations
            self._cleanup_conversations()

            # Error manager cleanup (if needed)
            if hasattr(self.error_manager, 'cleanup'):
                self.error_manager.cleanup()

            # API client cleanup
            if self.api_client:
                self.api_client.cleanup()

            # Reset agent state
            self.is_busy = False
            self.last_error = None

            self.logger.info("Agent cleanup completed")

        except Exception as e:
            self.error_manager.record_error(
                e, ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM,
                {'operation': 'cleanup'}
            )
            self.logger.error(f"Error during agent cleanup: {e}")

    def emergency_cleanup(self):
        """Emergency cleanup for critical failures."""
        try:
            self.logger.warning("Performing emergency cleanup")

            # Force reset agent state
            self.is_busy = False
            self.last_error = None

            # Clear all conversations to free memory
            self.conversations.clear()

            # Force API client cleanup
            if self.api_client and hasattr(self.api_client, 'session'):
                try:
                    self.api_client.session.close()
                except:
                    pass

            # Trigger graceful degradation
            if hasattr(self, 'error_manager'):
                self.error_manager._trigger_graceful_degradation()

            self.logger.warning("Emergency cleanup completed")

        except Exception as e:
            # Last resort logging
            self.logger.critical(f"Emergency cleanup failed: {e}")

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of the agent."""
        try:
            error_stats = self.error_manager.get_error_stats()
            memory_stats = self.get_memory_stats()

            # Determine overall health
            total_errors = error_stats['total_errors']
            degraded_features = len(error_stats['degraded_features'])

            if total_errors > 30 or degraded_features > 2:
                health_status = 'critical'
            elif total_errors > 15 or degraded_features > 0:
                health_status = 'warning'
            elif total_errors > 5:
                health_status = 'caution'
            else:
                health_status = 'healthy'

            return {
                'status': health_status,
                'is_busy': self.is_busy,
                'last_error': self.last_error,
                'active_conversations': len(self.conversations),
                'error_stats': error_stats,
                'memory_stats': memory_stats['memory'],
                'recommendations': self._get_health_recommendations(health_status, error_stats)
            }

        except Exception as e:
            self.logger.error(f"Error getting health status: {e}")
            return {
                'status': 'unknown',
                'error': str(e)
            }

    def _get_health_recommendations(self, status: str, error_stats: Dict[str, Any]) -> List[str]:
        """Get health recommendations based on current status."""
        recommendations = []

        if status == 'critical':
            recommendations.append("Consider restarting the plugin")
            recommendations.append("Check network connectivity")
            recommendations.append("Verify API key configuration")
        elif status == 'warning':
            recommendations.append("Monitor error patterns")
            recommendations.append("Consider reducing request frequency")
        elif status == 'caution':
            recommendations.append("Monitor system resources")

        if error_stats['degraded_features']:
            recommendations.append(f"Features degraded: {', '.join(error_stats['degraded_features'])}")

        return recommendations

    def _cleanup_conversations(self):
        """Clean up conversations with memory management."""
        initial_count = len(self.conversations)

        # Configuration for conversation limits
        max_conversations = self.config_manager.get('performance.memory.max_conversations', 10)
        max_conversation_age_hours = self.config_manager.get('performance.memory.max_conversation_age_hours', 24)
        max_total_memory_mb = self.config_manager.get('performance.memory.max_memory_mb', 200.0)

        # Remove old conversations based on age
        cutoff_time = datetime.now() - timedelta(hours=max_conversation_age_hours)
        aged_out = []

        for conv_id, conversation in list(self.conversations.items()):
            if conversation.last_activity < cutoff_time:
                aged_out.append(conv_id)
                del self.conversations[conv_id]

        if aged_out:
            self.logger.info(f"Removed {len(aged_out)} aged conversations")

        # Calculate total memory usage
        total_memory_mb = 0
        conversation_sizes = []

        for conv_id, conversation in self.conversations.items():
            memory_stats = conversation.get_memory_usage()
            total_memory_mb += memory_stats['estimated_mb']
            conversation_sizes.append((conv_id, conversation, memory_stats['estimated_mb']))

        # If we exceed memory limits, remove largest conversations first
        if total_memory_mb > max_total_memory_mb:
            conversation_sizes.sort(key=lambda x: x[2], reverse=True)  # Sort by size, largest first

            while total_memory_mb > max_total_memory_mb and conversation_sizes:
                conv_id, conversation, size_mb = conversation_sizes.pop(0)
                if conv_id in self.conversations:
                    del self.conversations[conv_id]
                    total_memory_mb -= size_mb
                    self.logger.info(f"Removed large conversation {conv_id} ({size_mb:.2f}MB)")

        # If we still have too many conversations, keep only the most recent
        if len(self.conversations) > max_conversations:
            # Sort by last activity and keep only the most recent
            sorted_conversations = sorted(
                self.conversations.items(),
                key=lambda x: x[1].last_activity,
                reverse=True
            )

            # Keep only the most recent conversations
            conversations_to_remove = len(self.conversations) - max_conversations
            for conv_id, _ in sorted_conversations[max_conversations:]:
                del self.conversations[conv_id]

            self.logger.info(f"Removed {conversations_to_remove} excess conversations")

        # Trim individual conversations that are too large
        for conversation in self.conversations.values():
            conversation.trim_to_size()

        final_count = len(self.conversations)
        if initial_count != final_count:
            self.logger.info(f"Conversation cleanup: {initial_count} -> {final_count} conversations")

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics including memory usage and monitoring data."""
        stats = self.performance_manager.get_performance_stats()

        # Add memory statistics
        memory_stats = self.get_memory_stats()
        stats.update(memory_stats)

        # Add monitoring statistics
        if hasattr(self, 'monitor'):
            monitoring_stats = self.monitor.get_performance_summary()
            stats['monitoring'] = monitoring_stats

            # Add cache efficiency report
            cache_efficiency = self.performance_manager.get_cache_efficiency_report()
            stats['cache_efficiency'] = cache_efficiency

        return stats

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get detailed memory usage statistics."""
        total_conversations = len(self.conversations)
        total_turns = sum(len(conv.turns) for conv in self.conversations.values())
        total_memory_mb = 0

        conversation_details = []
        for conv_id, conversation in self.conversations.items():
            memory_usage = conversation.get_memory_usage()
            total_memory_mb += memory_usage['estimated_mb']
            conversation_details.append({
                'id': conv_id,
                'agent_type': conversation.agent_type,
                'turns': memory_usage['total_turns'],
                'memory_mb': memory_usage['estimated_mb'],
                'last_activity': conversation.last_activity.isoformat()
            })

        # Sort by memory usage, largest first
        conversation_details.sort(key=lambda x: x['memory_mb'], reverse=True)

        return {
            'memory': {
                'total_conversations': total_conversations,
                'total_turns': total_turns,
                'total_memory_mb': round(total_memory_mb, 2),
                'average_memory_per_conversation_mb': round(total_memory_mb / max(total_conversations, 1), 2),
                'largest_conversations': conversation_details[:5],  # Top 5 largest
                'limits': {
                    'max_conversations': self.config_manager.get('performance.memory.max_conversations', 10),
                    'max_memory_mb': self.config_manager.get('performance.memory.max_memory_mb', 200.0),
                    'max_conversation_age_hours': self.config_manager.get('performance.memory.max_conversation_age_hours', 24)
                }
            }
        }
    
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
    

