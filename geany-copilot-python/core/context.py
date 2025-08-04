"""
Context analysis for Geany Copilot Python plugin.

This module provides intelligent context extraction and analysis capabilities
for better AI assistance in code and writing tasks.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

from .language_detector import LanguageDetector, LanguageInfo


@dataclass
class FileInfo:
    """Information about the current file."""
    filename: str
    extension: str
    language: str
    encoding: str
    line_count: int
    is_modified: bool


@dataclass
class CodeContext:
    """Context information for code assistance."""
    selected_text: str
    surrounding_text: str
    cursor_position: int
    line_number: int
    column_number: int
    function_context: Optional[str]
    class_context: Optional[str]
    imports: List[str]
    file_info: FileInfo


@dataclass
class WritingContext:
    """Context information for writing assistance."""
    selected_text: str
    surrounding_text: str
    document_type: str
    word_count: int
    paragraph_count: int
    file_info: FileInfo


class ContextAnalyzer:
    """
    Analyzes editor context to provide relevant information for AI assistance.
    
    This class extracts and analyzes context from the current editor state,
    including code structure, file information, and surrounding content.
    """
    
    def __init__(self):
        """Initialize the context analyzer."""
        self.logger = logging.getLogger(__name__)
        self.language_detector = LanguageDetector()
        
        # Language detection patterns
        self.language_patterns = {
            'python': [r'def\s+\w+\(', r'class\s+\w+', r'import\s+\w+', r'from\s+\w+\s+import'],
            'javascript': [r'function\s+\w+\(', r'const\s+\w+\s*=', r'let\s+\w+\s*=', r'var\s+\w+\s*='],
            'java': [r'public\s+class\s+\w+', r'private\s+\w+', r'public\s+static\s+void\s+main'],
            'c': [r'#include\s*<', r'int\s+main\s*\(', r'void\s+\w+\s*\('],
            'cpp': [r'#include\s*<', r'class\s+\w+', r'namespace\s+\w+', r'std::'],
            'html': [r'<html', r'<head>', r'<body>', r'<!DOCTYPE'],
            'css': [r'\w+\s*{', r'@media', r'@import'],
            'sql': [r'SELECT\s+', r'INSERT\s+INTO', r'CREATE\s+TABLE', r'UPDATE\s+'],
        }
    
    def get_file_info(self) -> Optional[FileInfo]:
        """
        Get information about the current file with enhanced language detection.

        Returns:
            FileInfo object or None if no file is open
        """
        try:
            from utils.helpers import get_current_document, get_document_text

            current_doc = get_current_document()
            if not current_doc:
                return None

            filename = current_doc.file_name or "Untitled"
            extension = Path(filename).suffix.lower() if filename != "Untitled" else ""

            # Get Geany's filetype detection
            geany_filetype = None
            if hasattr(current_doc, 'file_type') and current_doc.file_type:
                geany_filetype = current_doc.file_type.name

            # Get document content for language detection
            content = get_document_text()

            # Use advanced language detection
            language_info = self.language_detector.detect_language(
                filename=filename if filename != "Untitled" else None,
                content=content,
                geany_filetype=geany_filetype
            )

            encoding = getattr(current_doc, 'encoding', 'utf-8')
            is_modified = getattr(current_doc, 'text_changed', False)

            # Get accurate line count
            line_count = 0
            if current_doc.editor and current_doc.editor.scintilla:
                line_count = current_doc.editor.scintilla.get_line_count()

            return FileInfo(
                filename=filename,
                extension=extension,
                language=language_info.name,
                encoding=encoding,
                line_count=line_count,
                is_modified=is_modified
            )

        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return None

    def get_language_info(self) -> Optional[LanguageInfo]:
        """
        Get detailed language information for the current file.

        Returns:
            LanguageInfo object with detection details
        """
        try:
            from utils.helpers import get_current_document, get_document_text

            current_doc = get_current_document()
            if not current_doc:
                return None

            filename = current_doc.file_name or "Untitled"

            # Get Geany's filetype detection
            geany_filetype = None
            if hasattr(current_doc, 'file_type') and current_doc.file_type:
                geany_filetype = current_doc.file_type.name

            # Get document content for language detection
            content = get_document_text()

            # Use advanced language detection
            language_info = self.language_detector.detect_language(
                filename=filename if filename != "Untitled" else None,
                content=content,
                geany_filetype=geany_filetype
            )

            return language_info

        except Exception as e:
            self.logger.error(f"Error getting language info: {e}")
            return None

    def get_language_context(self) -> Dict[str, Any]:
        """
        Get language-specific context for AI prompts.

        Returns:
            Dictionary with language context information
        """
        try:
            language_info = self.get_language_info()
            if not language_info:
                return {}

            language = language_info.name
            category = self.language_detector.get_language_category(language)

            context = {
                'language': language,
                'category': category,
                'confidence': language_info.confidence,
                'features': language_info.features,
                'suggestions': self._get_language_suggestions(language, category),
                'best_practices': self._get_language_best_practices(language),
                'common_patterns': self._get_language_patterns(language)
            }

            return context

        except Exception as e:
            self.logger.error(f"Error getting language context: {e}")
            return {}

    def _get_language_suggestions(self, language: str, category: str) -> List[str]:
        """Get language-specific suggestions for AI assistance."""
        suggestions = {
            'python': [
                "Follow PEP 8 style guidelines",
                "Use type hints for better code clarity",
                "Consider using list comprehensions where appropriate",
                "Use context managers (with statements) for resource handling",
                "Follow the principle of least surprise"
            ],
            'javascript': [
                "Use const/let instead of var",
                "Consider using arrow functions for concise syntax",
                "Use async/await for asynchronous operations",
                "Follow consistent naming conventions",
                "Use strict mode ('use strict')"
            ],
            'java': [
                "Follow Java naming conventions",
                "Use proper exception handling",
                "Consider using generics for type safety",
                "Use StringBuilder for string concatenation in loops",
                "Follow SOLID principles"
            ],
            'c': [
                "Always check return values of functions",
                "Use proper memory management (malloc/free)",
                "Initialize variables before use",
                "Use const for read-only data",
                "Avoid buffer overflows"
            ],
            'cpp': [
                "Use RAII (Resource Acquisition Is Initialization)",
                "Prefer smart pointers over raw pointers",
                "Use const correctness",
                "Follow the rule of three/five/zero",
                "Use STL containers and algorithms"
            ],
            'html': [
                "Use semantic HTML elements",
                "Include proper DOCTYPE declaration",
                "Use alt attributes for images",
                "Ensure proper nesting of elements",
                "Use meaningful class and id names"
            ],
            'css': [
                "Use consistent naming conventions",
                "Organize CSS with logical structure",
                "Use CSS Grid or Flexbox for layouts",
                "Minimize use of !important",
                "Consider mobile-first responsive design"
            ]
        }

        return suggestions.get(language, [
            f"Follow {language} best practices",
            "Write clean, readable code",
            "Use consistent formatting",
            "Add appropriate comments"
        ])

    def _get_language_best_practices(self, language: str) -> List[str]:
        """Get language-specific best practices."""
        practices = {
            'python': [
                "Use virtual environments",
                "Write docstrings for functions and classes",
                "Use meaningful variable names",
                "Keep functions small and focused"
            ],
            'javascript': [
                "Use ESLint for code quality",
                "Avoid global variables",
                "Use proper error handling",
                "Keep functions pure when possible"
            ],
            'java': [
                "Use proper package structure",
                "Write unit tests",
                "Use dependency injection",
                "Follow MVC pattern where appropriate"
            ]
        }

        return practices.get(language, [
            "Write maintainable code",
            "Use version control",
            "Test your code",
            "Document your work"
        ])

    def _get_language_patterns(self, language: str) -> List[str]:
        """Get common patterns for the language."""
        patterns = {
            'python': [
                "if __name__ == '__main__':",
                "with open(filename) as f:",
                "try/except blocks",
                "List comprehensions",
                "Generator expressions"
            ],
            'javascript': [
                "Module imports/exports",
                "Promise chains",
                "Event listeners",
                "Callback functions",
                "Object destructuring"
            ],
            'java': [
                "try-with-resources",
                "Builder pattern",
                "Factory pattern",
                "Singleton pattern",
                "Observer pattern"
            ]
        }

        return patterns.get(language, [])
    
    def get_selection_info(self) -> Tuple[str, int, int]:
        """
        Get current selection information.

        Returns:
            Tuple of (selected_text, start_pos, end_pos)
        """
        try:
            from utils.helpers import get_selected_text, get_current_document

            selected_text = get_selected_text()
            if not selected_text:
                return "", 0, 0

            # Get selection positions
            current_doc = get_current_document()
            if not current_doc or not current_doc.editor:
                return selected_text, 0, 0

            editor = current_doc.editor
            scintilla = editor.scintilla

            start_pos = scintilla.get_selection_start()
            end_pos = scintilla.get_selection_end()

            return selected_text, start_pos, end_pos

        except Exception as e:
            self.logger.error(f"Error getting selection info: {e}")
            return "", 0, 0
    
    def get_surrounding_text(self, position: int, context_length: int = 200) -> str:
        """
        Get text surrounding the specified position.

        Args:
            position: Cursor position
            context_length: Number of characters to include on each side

        Returns:
            Surrounding text
        """
        try:
            from utils.helpers import get_current_document

            current_doc = get_current_document()
            if not current_doc or not current_doc.editor:
                return ""

            # Get the Scintilla editor object
            editor = current_doc.editor
            scintilla = editor.scintilla

            # Calculate start and end positions
            start_pos = max(0, position - context_length)
            end_pos = min(scintilla.get_length(), position + context_length)

            # Get the surrounding text
            surrounding_text = scintilla.get_text_range(start_pos, end_pos)

            return surrounding_text

        except Exception as e:
            self.logger.error(f"Error getting surrounding text: {e}")
            return ""
    
    def analyze_code_context(self, context_length: int = 200) -> Optional[CodeContext]:
        """
        Analyze the current code context.
        
        Args:
            context_length: Length of context to analyze
            
        Returns:
            CodeContext object or None if analysis fails
        """
        try:
            file_info = self.get_file_info()
            if not file_info:
                return None
            
            selected_text, start_pos, end_pos = self.get_selection_info()
            
            # If no selection, create context around cursor
            if not selected_text:
                cursor_pos = self._get_cursor_position()
                selected_text = self.get_surrounding_text(cursor_pos, context_length // 2)
                start_pos = cursor_pos - len(selected_text) // 2
                end_pos = cursor_pos + len(selected_text) // 2
            
            surrounding_text = self.get_surrounding_text(start_pos, context_length)
            line_number, column_number = self._get_cursor_line_column()
            
            # Analyze code structure
            function_context = self._find_function_context(surrounding_text, file_info.language)
            class_context = self._find_class_context(surrounding_text, file_info.language)
            imports = self._extract_imports(surrounding_text, file_info.language)
            
            return CodeContext(
                selected_text=selected_text,
                surrounding_text=surrounding_text,
                cursor_position=start_pos,
                line_number=line_number,
                column_number=column_number,
                function_context=function_context,
                class_context=class_context,
                imports=imports,
                file_info=file_info
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing code context: {e}")
            return None
    
    def analyze_writing_context(self) -> Optional[WritingContext]:
        """
        Analyze the current writing context.
        
        Returns:
            WritingContext object or None if analysis fails
        """
        try:
            file_info = self.get_file_info()
            if not file_info:
                return None
            
            selected_text, start_pos, end_pos = self.get_selection_info()
            
            if not selected_text:
                return None  # Writing assistance requires selected text
            
            surrounding_text = self.get_surrounding_text(start_pos, 500)
            
            # Analyze writing characteristics
            document_type = self._detect_document_type(file_info, surrounding_text)
            word_count = len(selected_text.split())
            paragraph_count = len([p for p in selected_text.split('\n\n') if p.strip()])
            
            return WritingContext(
                selected_text=selected_text,
                surrounding_text=surrounding_text,
                document_type=document_type,
                word_count=word_count,
                paragraph_count=paragraph_count,
                file_info=file_info
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing writing context: {e}")
            return None
    
    def _get_cursor_position(self) -> int:
        """Get current cursor position."""
        try:
            import geany
            
            current_doc = geany.document.get_current()
            if current_doc and current_doc.editor:
                # Placeholder - would need Scintilla editor access
                return 0
            return 0
            
        except Exception as e:
            self.logger.error(f"Error getting cursor position: {e}")
            return 0
    
    def _get_cursor_line_column(self) -> Tuple[int, int]:
        """Get current cursor line and column."""
        try:
            import geany
            
            current_doc = geany.document.get_current()
            if current_doc and current_doc.editor:
                # Placeholder - would need Scintilla editor access
                return 1, 1
            return 1, 1
            
        except Exception as e:
            self.logger.error(f"Error getting cursor line/column: {e}")
            return 1, 1
    
    def _find_function_context(self, text: str, language: str) -> Optional[str]:
        """Find the current function context."""
        try:
            if language == 'python':
                match = re.search(r'def\s+(\w+)\s*\([^)]*\):', text)
                return match.group(1) if match else None
            elif language in ['javascript', 'typescript']:
                match = re.search(r'function\s+(\w+)\s*\(|(\w+)\s*:\s*function\s*\(|(\w+)\s*=\s*\([^)]*\)\s*=>', text)
                return match.group(1) or match.group(2) or match.group(3) if match else None
            elif language in ['java', 'c', 'cpp']:
                match = re.search(r'\w+\s+(\w+)\s*\([^)]*\)\s*{', text)
                return match.group(1) if match else None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding function context: {e}")
            return None
    
    def _find_class_context(self, text: str, language: str) -> Optional[str]:
        """Find the current class context."""
        try:
            if language == 'python':
                match = re.search(r'class\s+(\w+)', text)
                return match.group(1) if match else None
            elif language in ['java', 'cpp', 'csharp']:
                match = re.search(r'class\s+(\w+)', text)
                return match.group(1) if match else None
            elif language == 'javascript':
                match = re.search(r'class\s+(\w+)', text)
                return match.group(1) if match else None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding class context: {e}")
            return None
    
    def _extract_imports(self, text: str, language: str) -> List[str]:
        """Extract import statements from the text."""
        try:
            imports = []
            
            if language == 'python':
                imports.extend(re.findall(r'import\s+(\w+(?:\.\w+)*)', text))
                imports.extend(re.findall(r'from\s+(\w+(?:\.\w+)*)\s+import', text))
            elif language in ['javascript', 'typescript']:
                imports.extend(re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', text))
                imports.extend(re.findall(r'require\s*\(\s*[\'"]([^\'"]+)[\'"]', text))
            elif language in ['java', 'csharp']:
                imports.extend(re.findall(r'import\s+([^;]+);', text))
            elif language in ['c', 'cpp']:
                imports.extend(re.findall(r'#include\s*[<"]([^>"]+)[>"]', text))
            
            return imports
            
        except Exception as e:
            self.logger.error(f"Error extracting imports: {e}")
            return []
    
    def _detect_document_type(self, file_info: FileInfo, text: str) -> str:
        """Detect the type of document being edited."""
        try:
            # Check file extension first
            if file_info.extension in ['.md', '.markdown']:
                return 'markdown'
            elif file_info.extension in ['.txt']:
                return 'plain_text'
            elif file_info.extension in ['.html', '.htm']:
                return 'html'
            elif file_info.extension in ['.tex']:
                return 'latex'
            elif file_info.extension in ['.rst']:
                return 'restructuredtext'
            
            # Check content patterns
            if re.search(r'^#+\s+', text, re.MULTILINE):
                return 'markdown'
            elif re.search(r'<[^>]+>', text):
                return 'html'
            elif re.search(r'\\[a-zA-Z]+{', text):
                return 'latex'
            
            return 'plain_text'
            
        except Exception as e:
            self.logger.error(f"Error detecting document type: {e}")
            return 'plain_text'
    
    def format_context_for_ai(self, context: Any) -> str:
        """
        Format context information for AI consumption.
        
        Args:
            context: CodeContext or WritingContext object
            
        Returns:
            Formatted context string
        """
        try:
            if isinstance(context, CodeContext):
                return self._format_code_context(context)
            elif isinstance(context, WritingContext):
                return self._format_writing_context(context)
            else:
                return str(context)
                
        except Exception as e:
            self.logger.error(f"Error formatting context: {e}")
            return ""
    
    def _format_code_context(self, context: CodeContext) -> str:
        """Format code context for AI with enhanced language information."""
        parts = []

        # File information
        parts.append(f"File: {context.file_info.filename}")
        parts.append(f"Language: {context.file_info.language}")
        parts.append(f"Position: Line {context.line_number}, Column {context.column_number}")

        # Enhanced language context
        language_context = self.get_language_context()
        if language_context:
            parts.append(f"Language Category: {language_context.get('category', 'unknown')}")
            if language_context.get('confidence', 0) < 0.8:
                parts.append(f"Language Detection Confidence: {language_context.get('confidence', 0):.2f}")

        # Code structure context
        if context.class_context:
            parts.append(f"Class: {context.class_context}")
        if context.function_context:
            parts.append(f"Function: {context.function_context}")

        # Imports
        if context.imports:
            parts.append(f"Imports: {', '.join(context.imports[:5])}")  # Limit to first 5

        # Language-specific suggestions
        if language_context and language_context.get('suggestions'):
            suggestions = language_context['suggestions'][:3]  # Limit to top 3
            parts.append(f"Language Guidelines: {'; '.join(suggestions)}")

        # Selected/surrounding text
        if context.selected_text:
            parts.append(f"\nSelected code:\n```{context.file_info.language}\n{context.selected_text}\n```")

        if context.surrounding_text and context.surrounding_text != context.selected_text:
            parts.append(f"\nSurrounding context:\n```{context.file_info.language}\n{context.surrounding_text}\n```")

        return "\n".join(parts)
    
    def _format_writing_context(self, context: WritingContext) -> str:
        """Format writing context for AI."""
        parts = []
        
        # Document information
        parts.append(f"Document: {context.file_info.filename}")
        parts.append(f"Type: {context.document_type}")
        parts.append(f"Selected text: {context.word_count} words, {context.paragraph_count} paragraphs")
        
        # Selected text
        parts.append(f"\nSelected text:\n{context.selected_text}")
        
        # Surrounding context if different
        if context.surrounding_text and context.surrounding_text != context.selected_text:
            parts.append(f"\nSurrounding context:\n{context.surrounding_text}")
        
        return "\n".join(parts)
