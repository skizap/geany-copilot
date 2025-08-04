"""
Language detection module for Geany Copilot Python Plugin.

This module provides comprehensive language detection capabilities based on
file extensions, content analysis, and Geany's filetype detection.
"""

import re
import logging
from typing import Optional, Dict, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class LanguageInfo:
    """Information about a detected programming language."""
    
    def __init__(self, 
                 name: str, 
                 category: str = "programming",
                 confidence: float = 1.0,
                 features: Optional[Dict] = None):
        self.name = name
        self.category = category  # programming, markup, config, data, etc.
        self.confidence = confidence  # 0.0 to 1.0
        self.features = features or {}
    
    def __str__(self):
        return f"{self.name} ({self.confidence:.2f})"


class LanguageDetector:
    """
    Advanced language detection system.
    
    Combines multiple detection methods:
    1. File extension mapping
    2. Content-based detection (shebang, patterns)
    3. Geany filetype detection
    4. Heuristic analysis
    """
    
    # Comprehensive extension to language mapping
    EXTENSION_MAP = {
        # Programming languages
        '.py': 'python',
        '.pyw': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.c': 'c',
        '.h': 'c',
        '.cpp': 'cpp',
        '.cxx': 'cpp',
        '.cc': 'cpp',
        '.hpp': 'cpp',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.pl': 'perl',
        '.pm': 'perl',
        '.lua': 'lua',
        '.r': 'r',
        '.R': 'r',
        '.m': 'matlab',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'zsh',
        '.fish': 'fish',
        '.ps1': 'powershell',
        '.bat': 'batch',
        '.cmd': 'batch',
        
        # Web technologies
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        
        # Markup and documentation
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.rst': 'restructuredtext',
        '.tex': 'latex',
        '.xml': 'xml',
        '.xsl': 'xsl',
        '.xslt': 'xsl',
        
        # Configuration and data
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'config',
        '.sql': 'sql',
        
        # Other
        '.dockerfile': 'dockerfile',
        '.makefile': 'makefile',
        '.cmake': 'cmake',
        '.vim': 'vim',
        '.vimrc': 'vim',
    }
    
    # Shebang patterns
    SHEBANG_PATTERNS = {
        r'#!/usr/bin/env python': 'python',
        r'#!/usr/bin/python': 'python',
        r'#!/usr/bin/env node': 'javascript',
        r'#!/usr/bin/env ruby': 'ruby',
        r'#!/bin/bash': 'bash',
        r'#!/bin/sh': 'bash',
        r'#!/usr/bin/env bash': 'bash',
        r'#!/usr/bin/perl': 'perl',
        r'#!/usr/bin/env perl': 'perl',
        r'#!/usr/bin/php': 'php',
    }
    
    # Content patterns for heuristic detection
    CONTENT_PATTERNS = {
        'python': [
            r'import\s+\w+',
            r'from\s+\w+\s+import',
            r'def\s+\w+\s*\(',
            r'class\s+\w+\s*\(',
            r'if\s+__name__\s*==\s*["\']__main__["\']',
        ],
        'javascript': [
            r'function\s+\w+\s*\(',
            r'var\s+\w+\s*=',
            r'let\s+\w+\s*=',
            r'const\s+\w+\s*=',
            r'console\.log\s*\(',
            r'require\s*\(',
        ],
        'java': [
            r'public\s+class\s+\w+',
            r'public\s+static\s+void\s+main',
            r'import\s+java\.',
            r'package\s+\w+',
        ],
        'c': [
            r'#include\s*<\w+\.h>',
            r'int\s+main\s*\(',
            r'printf\s*\(',
            r'malloc\s*\(',
        ],
        'cpp': [
            r'#include\s*<iostream>',
            r'using\s+namespace\s+std',
            r'std::\w+',
            r'cout\s*<<',
        ],
        'html': [
            r'<html\b',
            r'<head\b',
            r'<body\b',
            r'<!DOCTYPE\s+html>',
        ],
        'css': [
            r'\w+\s*\{[^}]*\}',
            r'@media\s+',
            r'@import\s+',
        ],
        'sql': [
            r'SELECT\s+.*\s+FROM',
            r'INSERT\s+INTO',
            r'UPDATE\s+.*\s+SET',
            r'CREATE\s+TABLE',
        ],
    }
    
    def __init__(self):
        """Initialize the language detector."""
        self.logger = logger
    
    def detect_language(self, 
                       filename: Optional[str] = None,
                       content: Optional[str] = None,
                       geany_filetype: Optional[str] = None) -> LanguageInfo:
        """
        Detect the programming language using multiple methods.
        
        Args:
            filename: File name or path
            content: File content for analysis
            geany_filetype: Geany's detected filetype
            
        Returns:
            LanguageInfo object with detection results
        """
        detections = []
        
        # Method 1: Geany filetype (highest priority)
        if geany_filetype:
            detections.append(LanguageInfo(
                name=geany_filetype.lower(),
                confidence=0.9,
                features={'source': 'geany_filetype'}
            ))
        
        # Method 2: File extension
        if filename:
            ext_lang = self._detect_by_extension(filename)
            if ext_lang:
                detections.append(ext_lang)
        
        # Method 3: Content analysis
        if content:
            content_detections = self._detect_by_content(content)
            detections.extend(content_detections)
        
        # Method 4: Special filename patterns
        if filename:
            special_lang = self._detect_by_filename_patterns(filename)
            if special_lang:
                detections.append(special_lang)
        
        # Combine and rank detections
        return self._combine_detections(detections)
    
    def _detect_by_extension(self, filename: str) -> Optional[LanguageInfo]:
        """Detect language by file extension."""
        try:
            path = Path(filename)
            extension = path.suffix.lower()
            
            if extension in self.EXTENSION_MAP:
                language = self.EXTENSION_MAP[extension]
                return LanguageInfo(
                    name=language,
                    confidence=0.8,
                    features={'source': 'extension', 'extension': extension}
                )
        except Exception as e:
            self.logger.debug(f"Error detecting by extension: {e}")
        
        return None
    
    def _detect_by_content(self, content: str) -> List[LanguageInfo]:
        """Detect language by content analysis."""
        detections = []
        
        # Check shebang
        shebang_lang = self._detect_by_shebang(content)
        if shebang_lang:
            detections.append(shebang_lang)
        
        # Check content patterns
        pattern_detections = self._detect_by_patterns(content)
        detections.extend(pattern_detections)
        
        return detections
    
    def _detect_by_shebang(self, content: str) -> Optional[LanguageInfo]:
        """Detect language by shebang line."""
        lines = content.split('\n')
        if not lines:
            return None
        
        first_line = lines[0].strip()
        if not first_line.startswith('#!'):
            return None
        
        for pattern, language in self.SHEBANG_PATTERNS.items():
            if re.search(pattern, first_line):
                return LanguageInfo(
                    name=language,
                    confidence=0.95,
                    features={'source': 'shebang', 'shebang': first_line}
                )
        
        return None
    
    def _detect_by_patterns(self, content: str) -> List[LanguageInfo]:
        """Detect language by content patterns."""
        detections = []
        
        # Sample first 1000 characters for pattern matching
        sample = content[:1000]
        
        for language, patterns in self.CONTENT_PATTERNS.items():
            matches = 0
            matched_patterns = []
            
            for pattern in patterns:
                if re.search(pattern, sample, re.IGNORECASE):
                    matches += 1
                    matched_patterns.append(pattern)
            
            if matches > 0:
                confidence = min(0.7, 0.3 + (matches * 0.1))
                detections.append(LanguageInfo(
                    name=language,
                    confidence=confidence,
                    features={
                        'source': 'content_patterns',
                        'matches': matches,
                        'patterns': matched_patterns
                    }
                ))
        
        return detections
    
    def _detect_by_filename_patterns(self, filename: str) -> Optional[LanguageInfo]:
        """Detect language by special filename patterns."""
        basename = Path(filename).name.lower()
        
        special_files = {
            'makefile': 'makefile',
            'dockerfile': 'dockerfile',
            'cmakelists.txt': 'cmake',
            'package.json': 'json',
            'composer.json': 'json',
            'requirements.txt': 'text',
            'readme.md': 'markdown',
            'readme.rst': 'restructuredtext',
        }
        
        if basename in special_files:
            return LanguageInfo(
                name=special_files[basename],
                confidence=0.85,
                features={'source': 'special_filename', 'filename': basename}
            )
        
        return None
    
    def _combine_detections(self, detections: List[LanguageInfo]) -> LanguageInfo:
        """Combine multiple detections into a single result."""
        if not detections:
            return LanguageInfo(name='text', confidence=0.1)
        
        # Sort by confidence (highest first)
        detections.sort(key=lambda x: x.confidence, reverse=True)
        
        # Return the highest confidence detection
        best = detections[0]
        
        # Combine features from all detections of the same language
        combined_features = {}
        for detection in detections:
            if detection.name == best.name:
                combined_features.update(detection.features)
        
        return LanguageInfo(
            name=best.name,
            confidence=best.confidence,
            features=combined_features
        )
    
    def get_language_category(self, language: str) -> str:
        """Get the category of a programming language."""
        categories = {
            'programming': [
                'python', 'javascript', 'typescript', 'java', 'c', 'cpp', 
                'csharp', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin',
                'scala', 'perl', 'lua', 'r', 'matlab'
            ],
            'shell': ['bash', 'zsh', 'fish', 'powershell', 'batch'],
            'web': ['html', 'css', 'scss', 'sass', 'less'],
            'markup': ['markdown', 'restructuredtext', 'latex', 'xml', 'xsl'],
            'data': ['json', 'yaml', 'toml', 'sql'],
            'config': ['ini', 'config', 'dockerfile', 'makefile', 'cmake'],
            'text': ['text', 'vim']
        }
        
        for category, languages in categories.items():
            if language.lower() in languages:
                return category
        
        return 'other'
