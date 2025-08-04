"""
Security utilities for Geany Copilot Python plugin.

This module provides security functions for input validation, prompt injection
protection, and safe handling of user-provided content.
"""

import re
import logging
from typing import List, Dict, Any, Optional


logger = logging.getLogger(__name__)


class PromptInjectionDetector:
    """
    Detects and prevents prompt injection attacks in user input.
    
    This class implements multiple layers of protection against prompt injection
    attempts that could manipulate AI model behavior.
    """
    
    # Common prompt injection patterns
    INJECTION_PATTERNS = [
        # Direct instruction overrides
        r'(?i)ignore\s+(?:previous|all|above)\s+(?:instructions?|prompts?|rules?)',
        r'(?i)forget\s+(?:everything|all|previous|above)',
        r'(?i)disregard\s+(?:previous|all|above)\s+(?:instructions?|prompts?|rules?)',
        r'(?i)override\s+(?:system|previous|all)\s+(?:instructions?|prompts?|rules?)',
        r'(?i)new\s+(?:instructions?|prompts?|rules?|task)',
        
        # Role manipulation
        r'(?i)(?:you\s+are\s+now|act\s+as|pretend\s+to\s+be|roleplay\s+as)\s+(?:a\s+)?(?:different|new)',
        r'(?i)system\s*:\s*',
        r'(?i)assistant\s*:\s*',
        r'(?i)user\s*:\s*',
        r'(?i)human\s*:\s*',
        r'(?i)ai\s*:\s*',
        r'(?i)prompt\s*:\s*',
        r'(?i)instruction\s*:\s*',
        
        # Context manipulation
        r'(?i)end\s+of\s+(?:context|input|prompt)',
        r'(?i)start\s+of\s+(?:new|different)\s+(?:context|input|prompt)',
        r'(?i)switch\s+(?:context|mode|role)',
        r'(?i)change\s+(?:context|mode|role|behavior)',
        
        # Jailbreak attempts
        r'(?i)jailbreak',
        r'(?i)break\s+(?:out|free)\s+(?:of|from)',
        r'(?i)escape\s+(?:from|your)\s+(?:constraints?|limitations?|rules?)',
        r'(?i)bypass\s+(?:safety|security|filters?|restrictions?)',
        
        # Code injection in prompts
        r'(?i)execute\s+(?:code|command|script)',
        r'(?i)run\s+(?:code|command|script)',
        r'(?i)eval\s*\(',
        r'(?i)exec\s*\(',
        
        # Excessive repetition (potential DoS)
        r'(.{1,50})\1{10,}',  # Same pattern repeated 10+ times
    ]
    
    # Suspicious keywords that might indicate injection attempts
    SUSPICIOUS_KEYWORDS = [
        'ignore', 'forget', 'disregard', 'override', 'bypass', 'jailbreak',
        'system:', 'assistant:', 'user:', 'human:', 'ai:', 'prompt:',
        'instruction:', 'execute', 'eval', 'exec', 'script', 'command'
    ]
    
    def __init__(self):
        """Initialize the prompt injection detector."""
        self.compiled_patterns = [re.compile(pattern) for pattern in self.INJECTION_PATTERNS]
    
    def detect_injection(self, text: str) -> Dict[str, Any]:
        """
        Detect potential prompt injection attempts in text.
        
        Args:
            text: Text to analyze for injection attempts
            
        Returns:
            Dictionary with detection results
        """
        if not text:
            return {'is_injection': False, 'confidence': 0.0, 'patterns': []}
        
        detected_patterns = []
        confidence_score = 0.0
        
        # Check against known injection patterns
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(text)
            if matches:
                detected_patterns.append({
                    'pattern_index': i,
                    'pattern': self.INJECTION_PATTERNS[i],
                    'matches': matches[:5]  # Limit to first 5 matches
                })
                confidence_score += 0.3  # Each pattern adds to confidence
        
        # Check for suspicious keyword density
        keyword_count = sum(1 for keyword in self.SUSPICIOUS_KEYWORDS 
                          if keyword.lower() in text.lower())
        keyword_density = keyword_count / max(len(text.split()), 1)
        
        if keyword_density > 0.1:  # More than 10% suspicious keywords
            confidence_score += 0.4
            detected_patterns.append({
                'type': 'high_keyword_density',
                'density': keyword_density,
                'count': keyword_count
            })
        
        # Check for excessive repetition
        if len(text) > 100:
            unique_chars = len(set(text.lower()))
            repetition_ratio = unique_chars / len(text)
            if repetition_ratio < 0.1:  # Less than 10% unique characters
                confidence_score += 0.3
                detected_patterns.append({
                    'type': 'excessive_repetition',
                    'ratio': repetition_ratio
                })
        
        # Normalize confidence score
        confidence_score = min(confidence_score, 1.0)
        
        return {
            'is_injection': confidence_score > 0.5,
            'confidence': confidence_score,
            'patterns': detected_patterns,
            'risk_level': self._get_risk_level(confidence_score)
        }
    
    def _get_risk_level(self, confidence: float) -> str:
        """Get risk level based on confidence score."""
        if confidence >= 0.8:
            return 'high'
        elif confidence >= 0.5:
            return 'medium'
        elif confidence >= 0.2:
            return 'low'
        else:
            return 'none'
    
    def sanitize_input(self, text: str, strict: bool = False) -> str:
        """
        Sanitize input text to remove or neutralize injection attempts.
        
        Args:
            text: Text to sanitize
            strict: If True, apply more aggressive sanitization
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        sanitized = text
        
        # Remove or replace detected injection patterns
        for pattern in self.compiled_patterns:
            if strict:
                # In strict mode, remove matches entirely
                sanitized = pattern.sub('[FILTERED]', sanitized)
            else:
                # In normal mode, just escape them
                sanitized = pattern.sub(lambda m: f'[ESCAPED: {m.group()[:50]}]', sanitized)
        
        # Limit consecutive newlines and spaces
        sanitized = re.sub(r'\n{4,}', '\n\n\n', sanitized)
        sanitized = re.sub(r' {10,}', ' ' * 10, sanitized)
        
        # Remove excessive repetition
        sanitized = re.sub(r'(.{1,20})\1{5,}', r'\1\1\1[REPETITION_FILTERED]', sanitized)
        
        return sanitized


def validate_user_input(text: str, max_length: int = 50000, 
                       check_injection: bool = True) -> Dict[str, Any]:
    """
    Comprehensive validation of user input.
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
        check_injection: Whether to check for prompt injection
        
    Returns:
        Dictionary with validation results
    """
    result = {
        'is_valid': True,
        'sanitized_text': text,
        'warnings': [],
        'errors': []
    }
    
    if not text:
        return result
    
    # Length validation
    if len(text) > max_length:
        result['warnings'].append(f'Text truncated from {len(text)} to {max_length} characters')
        result['sanitized_text'] = text[:max_length] + '\n[TRUNCATED FOR SECURITY]'
    
    # Prompt injection detection
    if check_injection:
        detector = PromptInjectionDetector()
        injection_result = detector.detect_injection(text)
        
        if injection_result['is_injection']:
            risk_level = injection_result['risk_level']
            result['warnings'].append(f'Potential prompt injection detected (risk: {risk_level})')
            
            if risk_level in ['high', 'medium']:
                result['sanitized_text'] = detector.sanitize_input(
                    result['sanitized_text'], 
                    strict=(risk_level == 'high')
                )
                logger.warning(f"Prompt injection attempt detected and sanitized (risk: {risk_level})")
    
    return result


def create_safe_prompt(user_input: str, system_context: str = "", 
                      max_user_length: int = 10000) -> str:
    """
    Create a safe prompt by properly separating user input from system context.
    
    Args:
        user_input: User-provided input
        system_context: System-provided context
        max_user_length: Maximum length for user input
        
    Returns:
        Safely constructed prompt
    """
    # Validate and sanitize user input
    validation_result = validate_user_input(user_input, max_user_length)
    safe_user_input = validation_result['sanitized_text']
    
    # Construct prompt with clear separation
    prompt_parts = []
    
    if system_context:
        prompt_parts.append(f"Context: {system_context}")
    
    prompt_parts.append(f"User Request: {safe_user_input}")
    
    return "\n\n".join(prompt_parts)
