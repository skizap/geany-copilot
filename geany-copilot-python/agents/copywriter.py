"""
Copywriter Assistant agent for Geany Copilot Python plugin.

This module provides enhanced copywriting assistance with iterative improvements
and multi-turn conversations for writing tasks.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from core.agent import AIAgent
from core.api_client import APIResponse
from utils.security import validate_user_input, create_safe_prompt


class WritingTaskType(Enum):
    """Types of writing assistance tasks."""
    IMPROVEMENT = "improvement"
    PROOFREADING = "proofreading"
    REWRITING = "rewriting"
    EXPANSION = "expansion"
    SUMMARIZATION = "summarization"
    TONE_ADJUSTMENT = "tone_adjustment"
    FORMATTING = "formatting"
    TRANSLATION = "translation"
    CREATIVE_WRITING = "creative_writing"


@dataclass
class WritingSuggestion:
    """Represents a writing suggestion."""
    task_type: WritingTaskType
    original_text: str
    suggested_text: str
    explanation: str
    confidence: float
    changes_made: List[str]
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = None


class CopywriterAssistant:
    """
    Intelligent copywriting assistant with iterative improvement capabilities.
    
    This agent provides context-aware writing assistance, including proofreading,
    rewriting, tone adjustment, and iterative refinement of written content.
    """
    
    def __init__(self, ai_agent: AIAgent, config_manager):
        """
        Initialize the copywriter assistant.
        
        Args:
            ai_agent: Core AI agent instance
            config_manager: Configuration manager instance
        """
        self.ai_agent = ai_agent
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Assistant configuration
        self.config = config_manager.get_agent_config("copywriter")
        self.replace_selection = self.config.get("replace_selection", True)
        self.max_turns = self.config.get("max_conversation_turns", 5)
        self.iterative_improvements = self.config.get("iterative_improvements", True)
        
        # Current conversation and iteration state
        self.current_conversation_id: Optional[str] = None
        self.iteration_count = 0
        self.original_text = ""
        self.current_text = ""
    
    def get_context(self) -> str:
        """Get current writing context from the editor."""
        try:
            context = self.ai_agent.analyze_context("writing")
            return context or ""
        except Exception as e:
            self.logger.error(f"Error getting writing context: {e}")
            return ""
    
    def start_writing_session(self, text: str, initial_request: str = "") -> str:
        """
        Start a new writing assistance session.
        
        Args:
            text: Text to work with
            initial_request: Initial user request or empty for general improvement
            
        Returns:
            Conversation ID
        """
        try:
            # Store original text
            self.original_text = text
            self.current_text = text
            self.iteration_count = 0
            
            # Get current context
            context = self.get_context()
            
            # Start conversation
            conversation_id = self.ai_agent.start_conversation("copywriter", context)
            self.current_conversation_id = conversation_id
            
            # If no initial request, suggest general improvement
            if not initial_request:
                initial_request = self._generate_context_based_request(text, context)
            
            self.logger.info(f"Started writing session: {conversation_id}")
            return conversation_id
            
        except Exception as e:
            self.logger.error(f"Error starting writing session: {e}")
            raise
    
    def request_assistance(self, request: str, 
                          task_type: Optional[WritingTaskType] = None) -> APIResponse:
        """
        Request writing assistance.
        
        Args:
            request: User's request for assistance
            task_type: Type of task (optional, will be inferred if not provided)
            
        Returns:
            APIResponse with the assistant's response
        """
        try:
            # Ensure we have an active conversation
            if not self.current_conversation_id:
                raise ValueError("No active writing session. Start a session first.")
            
            # Infer task type if not provided
            if task_type is None:
                task_type = self._infer_task_type(request)
            
            # Enhance request with task-specific context
            enhanced_request = self._enhance_request(request, task_type)
            
            # Get updated context
            updated_context = self.get_context()
            
            # Continue conversation
            response = self.ai_agent.continue_conversation(
                self.current_conversation_id,
                enhanced_request,
                updated_context
            )
            
            # Update iteration count
            if response.success:
                self.iteration_count += 1
            
            return response
            
        except Exception as e:
            error_msg = f"Error requesting writing assistance: {e}"
            self.logger.error(error_msg)
            return APIResponse(success=False, content="", error=error_msg)
    
    def request_streaming_assistance(self, request: str,
                                   task_type: Optional[WritingTaskType] = None) -> APIResponse:
        """
        Request streaming writing assistance.
        
        Args:
            request: User's request for assistance
            task_type: Type of task (optional, will be inferred if not provided)
            
        Returns:
            APIResponse with streaming content
        """
        try:
            # Ensure we have an active conversation
            if not self.current_conversation_id:
                raise ValueError("No active writing session. Start a session first.")
            
            # Infer task type if not provided
            if task_type is None:
                task_type = self._infer_task_type(request)
            
            # Enhance request with task-specific context
            enhanced_request = self._enhance_request(request, task_type)
            
            # Get updated context
            updated_context = self.get_context()
            
            # Continue conversation with streaming
            response = self.ai_agent.continue_conversation(
                self.current_conversation_id,
                enhanced_request,
                updated_context,
                stream=True
            )
            
            # Update iteration count
            if response.success:
                self.iteration_count += 1
            
            return response
            
        except Exception as e:
            error_msg = f"Error requesting streaming writing assistance: {e}"
            self.logger.error(error_msg)
            return APIResponse(success=False, content="", error=error_msg)
    
    def improve_text(self, text: str, improvement_focus: str = "") -> APIResponse:
        """
        Improve the given text.
        
        Args:
            text: Text to improve
            improvement_focus: Specific area to focus on (clarity, flow, etc.)
            
        Returns:
            APIResponse with improved text
        """
        if not self.current_conversation_id:
            self.start_writing_session(text)
        
        request = f"Improve this text"
        if improvement_focus:
            request += f" focusing on {improvement_focus}"
        request += f":\n\n{text}"
        
        return self.request_assistance(request, WritingTaskType.IMPROVEMENT)
    
    def proofread_text(self, text: str) -> APIResponse:
        """
        Proofread text for grammar, spelling, and style issues.
        
        Args:
            text: Text to proofread
            
        Returns:
            APIResponse with proofreading corrections
        """
        if not self.current_conversation_id:
            self.start_writing_session(text)
        
        request = f"Proofread this text for grammar, spelling, and style issues:\n\n{text}"
        return self.request_assistance(request, WritingTaskType.PROOFREADING)
    
    def rewrite_text(self, text: str, style: str = "", target_audience: str = "") -> APIResponse:
        """
        Rewrite text in a different style or for a different audience.
        
        Args:
            text: Text to rewrite
            style: Target style (formal, casual, professional, etc.)
            target_audience: Target audience description
            
        Returns:
            APIResponse with rewritten text
        """
        if not self.current_conversation_id:
            self.start_writing_session(text)

        # Validate and sanitize the text input
        validation_result = validate_user_input(text, max_length=50000, check_injection=True)
        safe_text = validation_result['sanitized_text']

        # Create safe prompt
        context = "Rewrite the following text"
        if style:
            context += f" in a {style} style"
        if target_audience:
            context += f" for {target_audience}"
        context += " while maintaining the original meaning and improving clarity."

        request = create_safe_prompt(safe_text, context)

        return self.request_assistance(request, WritingTaskType.REWRITING)
    
    def expand_text(self, text: str, expansion_goal: str = "") -> APIResponse:
        """
        Expand text with additional details or examples.
        
        Args:
            text: Text to expand
            expansion_goal: What to focus on when expanding
            
        Returns:
            APIResponse with expanded text
        """
        if not self.current_conversation_id:
            self.start_writing_session(text)
        
        request = f"Expand this text"
        if expansion_goal:
            request += f" by adding {expansion_goal}"
        request += f":\n\n{text}"
        
        return self.request_assistance(request, WritingTaskType.EXPANSION)
    
    def summarize_text(self, text: str, summary_length: str = "brief") -> APIResponse:
        """
        Summarize text to key points.
        
        Args:
            text: Text to summarize
            summary_length: Length of summary (brief, detailed, bullet points)
            
        Returns:
            APIResponse with summarized text
        """
        if not self.current_conversation_id:
            self.start_writing_session(text)
        
        request = f"Create a {summary_length} summary of this text:\n\n{text}"
        return self.request_assistance(request, WritingTaskType.SUMMARIZATION)
    
    def adjust_tone(self, text: str, target_tone: str) -> APIResponse:
        """
        Adjust the tone of the text.
        
        Args:
            text: Text to adjust
            target_tone: Target tone (professional, friendly, formal, casual, etc.)
            
        Returns:
            APIResponse with tone-adjusted text
        """
        if not self.current_conversation_id:
            self.start_writing_session(text)
        
        request = f"Adjust the tone of this text to be more {target_tone}:\n\n{text}"
        return self.request_assistance(request, WritingTaskType.TONE_ADJUSTMENT)
    
    def format_text(self, text: str, format_type: str) -> APIResponse:
        """
        Format text according to specific requirements.
        
        Args:
            text: Text to format
            format_type: Type of formatting (markdown, HTML, academic, etc.)
            
        Returns:
            APIResponse with formatted text
        """
        if not self.current_conversation_id:
            self.start_writing_session(text)
        
        request = f"Format this text as {format_type}:\n\n{text}"
        return self.request_assistance(request, WritingTaskType.FORMATTING)
    
    def continue_iterative_improvement(self, feedback: str) -> APIResponse:
        """
        Continue iterative improvement based on user feedback.
        
        Args:
            feedback: User feedback on the current version
            
        Returns:
            APIResponse with further improvements
        """
        if not self.current_conversation_id:
            raise ValueError("No active writing session for iterative improvement")
        
        if not self.iterative_improvements:
            return APIResponse(
                success=False, 
                content="", 
                error="Iterative improvements are disabled"
            )
        
        if self.iteration_count >= self.max_turns:
            return APIResponse(
                success=False,
                content="",
                error=f"Maximum iterations ({self.max_turns}) reached"
            )
        
        request = f"Based on this feedback: '{feedback}', please improve the text further."
        return self.request_assistance(request, WritingTaskType.IMPROVEMENT)
    
    def get_writing_analysis(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and provide writing statistics and insights.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        try:
            analysis = {
                "word_count": len(text.split()),
                "character_count": len(text),
                "character_count_no_spaces": len(text.replace(" ", "")),
                "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
                "sentence_count": len(re.findall(r'[.!?]+', text)),
                "average_words_per_sentence": 0,
                "readability_issues": [],
                "tone_indicators": [],
                "improvement_suggestions": []
            }
            
            # Calculate average words per sentence
            if analysis["sentence_count"] > 0:
                analysis["average_words_per_sentence"] = round(
                    analysis["word_count"] / analysis["sentence_count"], 1
                )
            
            # Basic readability analysis
            if analysis["average_words_per_sentence"] > 20:
                analysis["readability_issues"].append("Long sentences detected")
            
            # Look for passive voice
            passive_indicators = ["was", "were", "been", "being"]
            if any(word in text.lower() for word in passive_indicators):
                analysis["improvement_suggestions"].append("Consider reducing passive voice")
            
            # Look for repetitive words
            words = text.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 4:  # Only check longer words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            repetitive_words = [word for word, count in word_freq.items() if count > 3]
            if repetitive_words:
                analysis["improvement_suggestions"].append(
                    f"Consider varying these repeated words: {', '.join(repetitive_words[:3])}"
                )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing text: {e}")
            return {"error": str(e)}
    
    def _generate_context_based_request(self, text: str, context: str) -> str:
        """Generate an initial request based on text and context."""
        if not text:
            return "I'm ready to help with your writing. Please provide some text to work with."
        
        # Analyze text characteristics
        word_count = len(text.split())
        
        if word_count < 10:
            return "I see you have a short text. Would you like me to expand it or help improve its clarity?"
        elif word_count > 500:
            return "I see you have a substantial piece of text. Would you like me to help improve its structure, clarity, or perhaps create a summary?"
        else:
            return "I'm ready to help improve your writing. Would you like me to focus on clarity, style, grammar, or overall flow?"
    
    def _infer_task_type(self, request: str) -> WritingTaskType:
        """Infer the task type from the user's request."""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["improve", "better", "enhance"]):
            return WritingTaskType.IMPROVEMENT
        elif any(word in request_lower for word in ["proofread", "grammar", "spelling", "correct"]):
            return WritingTaskType.PROOFREADING
        elif any(word in request_lower for word in ["rewrite", "rephrase", "different"]):
            return WritingTaskType.REWRITING
        elif any(word in request_lower for word in ["expand", "elaborate", "more detail"]):
            return WritingTaskType.EXPANSION
        elif any(word in request_lower for word in ["summarize", "summary", "brief", "condense"]):
            return WritingTaskType.SUMMARIZATION
        elif any(word in request_lower for word in ["tone", "formal", "casual", "professional"]):
            return WritingTaskType.TONE_ADJUSTMENT
        elif any(word in request_lower for word in ["format", "markdown", "html", "structure"]):
            return WritingTaskType.FORMATTING
        elif any(word in request_lower for word in ["translate", "translation"]):
            return WritingTaskType.TRANSLATION
        elif any(word in request_lower for word in ["creative", "story", "narrative"]):
            return WritingTaskType.CREATIVE_WRITING
        else:
            return WritingTaskType.IMPROVEMENT  # Default
    
    def _enhance_request(self, request: str, task_type: WritingTaskType) -> str:
        """Enhance the request with task-specific instructions."""
        enhancements = {
            WritingTaskType.IMPROVEMENT: "Focus on clarity, flow, and overall effectiveness while preserving the author's voice.",
            WritingTaskType.PROOFREADING: "Carefully check for grammar, spelling, punctuation, and style issues. Explain each correction.",
            WritingTaskType.REWRITING: "Maintain the core message while improving expression and adapting to the requested style.",
            WritingTaskType.EXPANSION: "Add relevant details, examples, or explanations while maintaining coherence.",
            WritingTaskType.SUMMARIZATION: "Capture the key points and main ideas while maintaining accuracy.",
            WritingTaskType.TONE_ADJUSTMENT: "Adjust the tone while preserving the essential meaning and information.",
            WritingTaskType.FORMATTING: "Apply the requested formatting while ensuring readability and proper structure.",
            WritingTaskType.TRANSLATION: "Provide accurate translation while considering cultural context and nuance.",
            WritingTaskType.CREATIVE_WRITING: "Enhance creativity, narrative flow, and engagement while maintaining consistency."
        }
        
        enhancement = enhancements.get(task_type, "")
        if enhancement:
            return f"{request}\n\nAdditional guidance: {enhancement}"
        return request
    
    def update_current_text(self, new_text: str):
        """Update the current working text."""
        self.current_text = new_text
    
    def get_iteration_count(self) -> int:
        """Get the current iteration count."""
        return self.iteration_count
    
    def can_iterate_further(self) -> bool:
        """Check if further iterations are possible."""
        return (self.iterative_improvements and 
                self.iteration_count < self.max_turns)
    
    def end_session(self):
        """End the current writing session."""
        if self.current_conversation_id:
            self.ai_agent.end_conversation(self.current_conversation_id)
            self.current_conversation_id = None
            self.iteration_count = 0
            self.original_text = ""
            self.current_text = ""
            self.logger.info("Ended writing session")
