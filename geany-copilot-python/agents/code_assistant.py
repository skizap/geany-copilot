"""
Code Assistant agent for Geany Copilot Python plugin.

This module provides intelligent code analysis, suggestions, refactoring,
and optimization features with agent-based intelligence.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from core.agent import AIAgent
from core.api_client import APIResponse
from utils.security import validate_user_input, create_safe_prompt


class CodeTaskType(Enum):
    """Types of code assistance tasks."""
    COMPLETION = "completion"
    EXPLANATION = "explanation"
    REFACTORING = "refactoring"
    OPTIMIZATION = "optimization"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    REVIEW = "review"


@dataclass
class CodeSuggestion:
    """Represents a code suggestion."""
    task_type: CodeTaskType
    original_code: str
    suggested_code: str
    explanation: str
    confidence: float
    reasoning: Optional[str] = None
    metadata: Dict[str, Any] = None


class CodeAssistant:
    """
    Intelligent code assistant with advanced analysis capabilities.
    
    This agent provides context-aware code completions, refactoring suggestions,
    optimization recommendations, and other code-related assistance.
    """
    
    def __init__(self, ai_agent: AIAgent, config_manager):
        """
        Initialize the code assistant.
        
        Args:
            ai_agent: Core AI agent instance
            config_manager: Configuration manager instance
        """
        self.ai_agent = ai_agent
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Assistant configuration
        self.config = config_manager.get_agent_config("code_assistant")
        self.context_length = self.config.get("context_length", 200)
        self.max_turns = self.config.get("max_conversation_turns", 10)
        self.auto_apply = self.config.get("auto_apply_suggestions", False)
        self.show_reasoning = self.config.get("show_reasoning", True)
        
        # Current conversation
        self.current_conversation_id: Optional[str] = None
    
    def get_context(self) -> str:
        """Get current code context from the editor."""
        try:
            context = self.ai_agent.analyze_context("code")
            return context or ""
        except Exception as e:
            self.logger.error(f"Error getting code context: {e}")
            return ""
    
    def start_assistance_session(self, initial_request: str = "") -> str:
        """
        Start a new code assistance session.
        
        Args:
            initial_request: Initial user request or empty for context-based assistance
            
        Returns:
            Conversation ID
        """
        try:
            # Get current context
            context = self.get_context()
            
            # Start conversation
            conversation_id = self.ai_agent.start_conversation("code_assistant", context)
            self.current_conversation_id = conversation_id
            
            # If no initial request, analyze context and suggest actions
            if not initial_request:
                initial_request = self._generate_context_based_request(context)
            
            self.logger.info(f"Started code assistance session: {conversation_id}")
            return conversation_id
            
        except Exception as e:
            self.logger.error(f"Error starting assistance session: {e}")
            raise
    
    def request_assistance(self, request: str, 
                          task_type: Optional[CodeTaskType] = None) -> APIResponse:
        """
        Request code assistance.
        
        Args:
            request: User's request for assistance
            task_type: Type of task (optional, will be inferred if not provided)
            
        Returns:
            APIResponse with the assistant's response
        """
        try:
            # Ensure we have an active conversation
            if not self.current_conversation_id:
                self.start_assistance_session()
            
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
            
            return response
            
        except Exception as e:
            error_msg = f"Error requesting assistance: {e}"
            self.logger.error(error_msg)
            return APIResponse(success=False, content="", error=error_msg)
    
    def request_streaming_assistance(self, request: str,
                                   task_type: Optional[CodeTaskType] = None) -> APIResponse:
        """
        Request streaming code assistance.
        
        Args:
            request: User's request for assistance
            task_type: Type of task (optional, will be inferred if not provided)
            
        Returns:
            APIResponse with streaming content
        """
        try:
            # Ensure we have an active conversation
            if not self.current_conversation_id:
                self.start_assistance_session()
            
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
            
            return response

        except Exception as e:
            error_msg = f"Error requesting streaming assistance: {e}"
            self.logger.error(error_msg)
            return APIResponse(success=False, content="", error=error_msg)

    def request_assistance_debounced(self, request: str,
                                   callback: callable,
                                   task_type: Optional[CodeTaskType] = None,
                                   delay: float = 1.0):
        """
        Request code assistance with debouncing to prevent excessive API calls.

        Args:
            request: User's request for assistance
            callback: Function to call with the response
            task_type: Type of task (optional, will be inferred if not provided)
            delay: Debounce delay in seconds
        """
        try:
            # Generate debounce key based on request content
            debounce_key = f"code_assist_{hash(request)}"

            # Define the actual request function
            def make_request():
                try:
                    response = self.request_assistance(request, task_type)
                    callback(response)
                except Exception as e:
                    error_response = APIResponse(success=False, content="", error=str(e))
                    callback(error_response)

            # Use the AI agent's performance manager for debouncing
            if hasattr(self.ai_agent, 'performance_manager'):
                self.ai_agent.performance_manager.debounce_request(
                    debounce_key, make_request
                )
            else:
                # Fallback to immediate execution if no performance manager
                make_request()

        except Exception as e:
            error_msg = f"Error in debounced assistance request: {e}"
            self.logger.error(error_msg)
            error_response = APIResponse(success=False, content="", error=error_msg)
            callback(error_response)
    
    def analyze_code(self, code: str, language: str = "") -> List[CodeSuggestion]:
        """
        Analyze code and provide suggestions.
        
        Args:
            code: Code to analyze
            language: Programming language (optional)
            
        Returns:
            List of code suggestions
        """
        try:
            suggestions = []
            
            # Basic analysis patterns
            if self._has_potential_bugs(code):
                suggestions.append(self._create_bug_suggestion(code))
            
            if self._can_be_optimized(code):
                suggestions.append(self._create_optimization_suggestion(code))
            
            if self._needs_documentation(code):
                suggestions.append(self._create_documentation_suggestion(code))
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Error analyzing code: {e}")
            return []
    
    def complete_code(self, partial_code: str, cursor_position: int = -1) -> APIResponse:
        """
        Complete partial code with security validation.

        Args:
            partial_code: Partial code to complete
            cursor_position: Position of cursor in the code

        Returns:
            APIResponse with code completion
        """
        # Validate and sanitize the code input
        validation_result = validate_user_input(partial_code, max_length=20000, check_injection=True)
        safe_code = validation_result['sanitized_text']

        # Create safe prompt
        context = "Complete the following code snippet while maintaining proper syntax and style."
        user_request = f"```\n{safe_code}\n```"
        if cursor_position >= 0:
            user_request += f"\n\nCursor position: {cursor_position}"

        request = create_safe_prompt(user_request, context)

        return self.request_assistance(request, CodeTaskType.COMPLETION)
    
    def explain_code(self, code: str) -> APIResponse:
        """
        Explain what the code does with security validation.

        Args:
            code: Code to explain

        Returns:
            APIResponse with explanation
        """
        # Validate and sanitize the code input
        validation_result = validate_user_input(code, max_length=20000, check_injection=True)
        safe_code = validation_result['sanitized_text']

        # Create safe prompt
        context = "Provide a clear explanation of what the following code does, including its purpose, logic, and key concepts."
        user_request = f"```\n{safe_code}\n```"

        request = create_safe_prompt(user_request, context)
        return self.request_assistance(request, CodeTaskType.EXPLANATION)
    
    def refactor_code(self, code: str, refactoring_goal: str = "") -> APIResponse:
        """
        Suggest code refactoring.
        
        Args:
            code: Code to refactor
            refactoring_goal: Specific refactoring goal
            
        Returns:
            APIResponse with refactoring suggestions
        """
        request = f"Refactor this code"
        if refactoring_goal:
            request += f" to {refactoring_goal}"
        request += f":\n\n```\n{code}\n```"
        
        return self.request_assistance(request, CodeTaskType.REFACTORING)
    
    def optimize_code(self, code: str) -> APIResponse:
        """
        Suggest code optimizations.
        
        Args:
            code: Code to optimize
            
        Returns:
            APIResponse with optimization suggestions
        """
        request = f"Optimize this code for better performance:\n\n```\n{code}\n```"
        return self.request_assistance(request, CodeTaskType.OPTIMIZATION)
    
    def debug_code(self, code: str, error_message: str = "") -> APIResponse:
        """
        Help debug code issues.
        
        Args:
            code: Code with potential issues
            error_message: Error message if available
            
        Returns:
            APIResponse with debugging help
        """
        request = f"Help debug this code"
        if error_message:
            request += f" (Error: {error_message})"
        request += f":\n\n```\n{code}\n```"
        
        return self.request_assistance(request, CodeTaskType.DEBUGGING)
    
    def generate_tests(self, code: str) -> APIResponse:
        """
        Generate tests for the code.
        
        Args:
            code: Code to generate tests for
            
        Returns:
            APIResponse with test suggestions
        """
        request = f"Generate unit tests for this code:\n\n```\n{code}\n```"
        return self.request_assistance(request, CodeTaskType.TESTING)
    
    def review_code(self, code: str) -> APIResponse:
        """
        Perform code review.
        
        Args:
            code: Code to review
            
        Returns:
            APIResponse with code review
        """
        request = f"Review this code for best practices, potential issues, and improvements:\n\n```\n{code}\n```"
        return self.request_assistance(request, CodeTaskType.REVIEW)
    
    def _generate_context_based_request(self, context: str) -> str:
        """Generate an initial request based on current context."""
        if not context:
            return "I'm ready to help with your code. What would you like assistance with?"
        
        # Analyze context to suggest appropriate assistance
        if "TODO" in context or "FIXME" in context:
            return "I notice there are TODO or FIXME comments. Would you like help implementing or fixing these items?"
        elif "def " in context and context.count("def ") > context.count("return"):
            return "I see function definitions that might need implementation. Would you like help completing them?"
        elif "class " in context:
            return "I see class definitions. Would you like help with implementation, documentation, or testing?"
        else:
            return "I'm analyzing your code context. How can I assist you with your current code?"
    
    def _infer_task_type(self, request: str) -> CodeTaskType:
        """Infer the task type from the user's request."""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["complete", "finish", "continue"]):
            return CodeTaskType.COMPLETION
        elif any(word in request_lower for word in ["explain", "what does", "how does"]):
            return CodeTaskType.EXPLANATION
        elif any(word in request_lower for word in ["refactor", "restructure", "reorganize"]):
            return CodeTaskType.REFACTORING
        elif any(word in request_lower for word in ["optimize", "performance", "faster", "efficient"]):
            return CodeTaskType.OPTIMIZATION
        elif any(word in request_lower for word in ["debug", "fix", "error", "bug", "issue"]):
            return CodeTaskType.DEBUGGING
        elif any(word in request_lower for word in ["document", "comment", "docstring"]):
            return CodeTaskType.DOCUMENTATION
        elif any(word in request_lower for word in ["test", "unit test", "testing"]):
            return CodeTaskType.TESTING
        elif any(word in request_lower for word in ["review", "check", "analyze", "improve"]):
            return CodeTaskType.REVIEW
        else:
            return CodeTaskType.COMPLETION  # Default
    
    def _enhance_request(self, request: str, task_type: CodeTaskType) -> str:
        """Enhance the request with task-specific instructions."""
        enhancements = {
            CodeTaskType.COMPLETION: "Focus on completing the code while maintaining consistency with existing patterns and style.",
            CodeTaskType.EXPLANATION: "Provide a clear, detailed explanation that covers the purpose, logic, and key concepts.",
            CodeTaskType.REFACTORING: "Suggest refactoring improvements while preserving functionality and explaining the benefits.",
            CodeTaskType.OPTIMIZATION: "Focus on performance improvements, efficiency gains, and best practices.",
            CodeTaskType.DEBUGGING: "Identify potential issues, explain the problems, and provide solutions.",
            CodeTaskType.DOCUMENTATION: "Generate comprehensive documentation including docstrings, comments, and usage examples.",
            CodeTaskType.TESTING: "Create thorough unit tests covering edge cases and different scenarios.",
            CodeTaskType.REVIEW: "Provide a comprehensive code review covering style, best practices, potential issues, and improvements."
        }
        
        enhancement = enhancements.get(task_type, "")
        if enhancement:
            return f"{request}\n\nAdditional guidance: {enhancement}"
        return request
    
    def _has_potential_bugs(self, code: str) -> bool:
        """Check if code has potential bugs."""
        # Simple heuristics - could be enhanced with more sophisticated analysis
        bug_patterns = [
            r'if\s+\w+\s*=\s*',  # Assignment in if condition
            r'==\s*None',        # Should use 'is None'
            r'!=\s*None',        # Should use 'is not None'
        ]
        
        return any(re.search(pattern, code) for pattern in bug_patterns)
    
    def _can_be_optimized(self, code: str) -> bool:
        """Check if code can be optimized."""
        # Simple heuristics
        optimization_opportunities = [
            r'for\s+\w+\s+in\s+range\(len\(',  # Can use enumerate
            r'\.append\(\w+\)\s*$',             # Might benefit from list comprehension
        ]
        
        return any(re.search(pattern, code, re.MULTILINE) for pattern in optimization_opportunities)
    
    def _needs_documentation(self, code: str) -> bool:
        """Check if code needs documentation."""
        # Check for functions/classes without docstrings
        has_functions = bool(re.search(r'def\s+\w+\s*\(', code))
        has_classes = bool(re.search(r'class\s+\w+', code))
        has_docstrings = bool(re.search(r'""".*?"""', code, re.DOTALL))
        
        return (has_functions or has_classes) and not has_docstrings
    
    def _create_bug_suggestion(self, code: str) -> CodeSuggestion:
        """Create a bug fix suggestion."""
        return CodeSuggestion(
            task_type=CodeTaskType.DEBUGGING,
            original_code=code,
            suggested_code="",  # Would be filled by AI analysis
            explanation="Potential bug detected in the code",
            confidence=0.7
        )
    
    def _create_optimization_suggestion(self, code: str) -> CodeSuggestion:
        """Create an optimization suggestion."""
        return CodeSuggestion(
            task_type=CodeTaskType.OPTIMIZATION,
            original_code=code,
            suggested_code="",  # Would be filled by AI analysis
            explanation="Code can be optimized for better performance",
            confidence=0.8
        )
    
    def _create_documentation_suggestion(self, code: str) -> CodeSuggestion:
        """Create a documentation suggestion."""
        return CodeSuggestion(
            task_type=CodeTaskType.DOCUMENTATION,
            original_code=code,
            suggested_code="",  # Would be filled by AI analysis
            explanation="Code would benefit from documentation",
            confidence=0.9
        )
    
    def end_session(self):
        """End the current assistance session."""
        if self.current_conversation_id:
            self.ai_agent.end_conversation(self.current_conversation_id)
            self.current_conversation_id = None
            self.logger.info("Ended code assistance session")
