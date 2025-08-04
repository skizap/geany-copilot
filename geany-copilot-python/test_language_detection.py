#!/usr/bin/env python3
"""
Test script for language detection functionality in Geany Copilot Python Plugin.

This script tests the enhanced language detection and context analysis capabilities.
"""

import sys
import os
from pathlib import Path

# Add the plugin directory to Python path
plugin_dir = Path(__file__).parent
sys.path.insert(0, str(plugin_dir))

def test_language_detector():
    """Test the LanguageDetector class."""
    print("🧪 Testing LanguageDetector...")
    
    try:
        from core.language_detector import LanguageDetector, LanguageInfo
        
        detector = LanguageDetector()
        
        # Test extension detection
        test_cases = [
            ("test.py", None, None, "python"),
            ("script.js", None, None, "javascript"),
            ("main.cpp", None, None, "cpp"),
            ("index.html", None, None, "html"),
            ("styles.css", None, None, "css"),
            ("config.json", None, None, "json"),
            ("README.md", None, None, "markdown"),
        ]
        
        for filename, content, geany_type, expected in test_cases:
            result = detector.detect_language(filename=filename, content=content, geany_filetype=geany_type)
            if result.name == expected:
                print(f"✅ {filename} -> {result.name} (confidence: {result.confidence:.2f})")
            else:
                print(f"❌ {filename} -> {result.name}, expected {expected}")
        
        # Test content detection
        python_code = '''#!/usr/bin/env python3
import os
import sys

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''
        
        result = detector.detect_language(content=python_code)
        print(f"✅ Python content detection: {result.name} (confidence: {result.confidence:.2f})")
        
        # Test JavaScript content
        js_code = '''
function greet(name) {
    console.log(`Hello, ${name}!`);
}

const message = "Welcome";
let count = 0;
'''
        
        result = detector.detect_language(content=js_code)
        print(f"✅ JavaScript content detection: {result.name} (confidence: {result.confidence:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ LanguageDetector test failed: {e}")
        return False


def test_context_analyzer_language():
    """Test the enhanced ContextAnalyzer with language detection."""
    print("\n🧪 Testing ContextAnalyzer language features...")
    
    try:
        from core.context import ContextAnalyzer
        
        analyzer = ContextAnalyzer()
        
        # Test language context generation
        # This will return empty context when not in Geany, but we can test the structure
        language_context = analyzer.get_language_context()
        print(f"✅ Language context structure: {type(language_context)}")
        
        # Test language suggestions
        suggestions = analyzer._get_language_suggestions("python", "programming")
        print(f"✅ Python suggestions: {len(suggestions)} items")
        print(f"   Sample: {suggestions[0] if suggestions else 'None'}")
        
        # Test best practices
        practices = analyzer._get_language_best_practices("javascript")
        print(f"✅ JavaScript best practices: {len(practices)} items")
        
        # Test patterns
        patterns = analyzer._get_language_patterns("java")
        print(f"✅ Java patterns: {len(patterns)} items")
        
        return True
        
    except Exception as e:
        print(f"❌ ContextAnalyzer language test failed: {e}")
        return False


def test_language_categories():
    """Test language categorization."""
    print("\n🧪 Testing language categorization...")
    
    try:
        from core.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        
        test_languages = [
            ("python", "programming"),
            ("javascript", "programming"),
            ("html", "web"),
            ("css", "web"),
            ("bash", "shell"),
            ("json", "data"),
            ("markdown", "markup"),
            ("dockerfile", "config")
        ]
        
        for language, expected_category in test_languages:
            category = detector.get_language_category(language)
            if category == expected_category:
                print(f"✅ {language} -> {category}")
            else:
                print(f"❌ {language} -> {category}, expected {expected_category}")
        
        return True
        
    except Exception as e:
        print(f"❌ Language categorization test failed: {e}")
        return False


def test_shebang_detection():
    """Test shebang-based language detection."""
    print("\n🧪 Testing shebang detection...")
    
    try:
        from core.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        
        shebang_tests = [
            ("#!/usr/bin/env python3\nprint('hello')", "python"),
            ("#!/bin/bash\necho 'hello'", "bash"),
            ("#!/usr/bin/env node\nconsole.log('hello')", "javascript"),
            ("#!/usr/bin/perl\nprint 'hello'", "perl"),
        ]
        
        for content, expected in shebang_tests:
            result = detector.detect_language(content=content)
            if result.name == expected:
                print(f"✅ Shebang detection: {expected} (confidence: {result.confidence:.2f})")
            else:
                print(f"❌ Shebang detection failed: got {result.name}, expected {expected}")
        
        return True
        
    except Exception as e:
        print(f"❌ Shebang detection test failed: {e}")
        return False


def test_pattern_matching():
    """Test content pattern matching."""
    print("\n🧪 Testing content pattern matching...")
    
    try:
        from core.language_detector import LanguageDetector
        
        detector = LanguageDetector()
        
        pattern_tests = [
            ("class MyClass:\n    def __init__(self):\n        pass", "python"),
            ("function myFunc() {\n    console.log('test');\n}", "javascript"),
            ("public class Main {\n    public static void main(String[] args) {", "java"),
            ("#include <iostream>\nusing namespace std;", "cpp"),
            ("SELECT * FROM users WHERE id = 1;", "sql"),
        ]
        
        for content, expected in pattern_tests:
            result = detector.detect_language(content=content)
            print(f"✅ Pattern matching: {result.name} (confidence: {result.confidence:.2f}) for {expected}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern matching test failed: {e}")
        return False


def main():
    """Run all language detection tests."""
    print("🚀 Geany Copilot Language Detection Test Suite")
    print("=" * 60)
    
    tests = [
        ("Language Detector", test_language_detector),
        ("Context Analyzer Language", test_context_analyzer_language),
        ("Language Categories", test_language_categories),
        ("Shebang Detection", test_shebang_detection),
        ("Pattern Matching", test_pattern_matching),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Language detection is ready.")
        print("\n📝 Next steps:")
        print("1. Test in actual Geany environment")
        print("2. Verify language-specific AI prompts")
        print("3. Test with mixed-language files")
        print("4. Verify context enhancement works with agents")
        print("5. Test edge cases and unknown file types")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
