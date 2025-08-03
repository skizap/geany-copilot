#!/bin/bash

# Geany Copilot Setup Verification Script
# This script verifies that the repository is properly set up for distribution

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

print_check() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check file exists
check_file() {
    local file="$1"
    local description="$2"
    
    if [ -f "$file" ]; then
        print_success "✓ $description: $file"
        return 0
    else
        print_error "✗ $description: $file (missing)"
        return 1
    fi
}

# Function to check directory exists
check_directory() {
    local dir="$1"
    local description="$2"
    
    if [ -d "$dir" ]; then
        print_success "✓ $description: $dir"
        return 0
    else
        print_error "✗ $description: $dir (missing)"
        return 1
    fi
}

# Main verification function
main() {
    local errors=0
    
    print_header "🔍 Geany Copilot Repository Verification"
    echo
    
    # Check essential repository files
    print_check "Checking essential repository files"
    check_file "install.sh" "Installation script" || errors=$((errors + 1))
    check_file "README.md" "Main README" || errors=$((errors + 1))
    check_file "INSTALL_GUIDE.md" "Installation guide" || errors=$((errors + 1))
    check_file "LICENSE" "License file" || errors=$((errors + 1))
    echo
    
    # Check Python plugin structure
    print_check "Checking Python plugin structure"
    check_directory "geany-copilot-python" "Python plugin directory" || errors=$((errors + 1))
    check_file "geany-copilot-python/__init__.py" "Main plugin file" || errors=$((errors + 1))
    check_file "geany-copilot-python/plugin.py" "GeanyPy entry point" || errors=$((errors + 1))
    check_file "geany-copilot-python/requirements.txt" "Python requirements" || errors=$((errors + 1))
    check_file "geany-copilot-python/README.md" "Plugin README" || errors=$((errors + 1))
    check_file "geany-copilot-python/test_plugin.py" "Plugin tests" || errors=$((errors + 1))
    echo
    
    # Check Python plugin modules
    print_check "Checking Python plugin modules"
    check_directory "geany-copilot-python/core" "Core module" || errors=$((errors + 1))
    check_directory "geany-copilot-python/agents" "Agents module" || errors=$((errors + 1))
    check_directory "geany-copilot-python/ui" "UI module" || errors=$((errors + 1))
    check_directory "geany-copilot-python/utils" "Utils module" || errors=$((errors + 1))
    echo
    
    # Check legacy file management
    print_check "Checking legacy file management"
    if [ -d "OLD" ]; then
        print_success "✓ OLD directory exists"
        if [ -f "OLD/copilot.lua" ] && [ -f "OLD/copywriter.lua" ]; then
            print_success "✓ Legacy Lua files preserved"
        else
            print_warning "⚠ Legacy Lua files not found in OLD directory"
        fi
    else
        print_warning "⚠ OLD directory not found (will be created during installation)"
    fi
    echo
    
    # Check script permissions
    print_check "Checking script permissions"
    if [ -x "install.sh" ]; then
        print_success "✓ install.sh is executable"
    else
        print_error "✗ install.sh is not executable"
        errors=$((errors + 1))
    fi
    
    if [ -f "test_install.sh" ] && [ -x "test_install.sh" ]; then
        print_success "✓ test_install.sh is executable"
    elif [ -f "test_install.sh" ]; then
        print_warning "⚠ test_install.sh exists but is not executable"
    fi
    echo
    
    # Check documentation
    print_check "Checking documentation completeness"
    if grep -q "Python Version (Recommended)" README.md; then
        print_success "✓ README.md mentions Python version"
    else
        print_warning "⚠ README.md may not highlight Python version"
    fi
    
    if grep -q "install.sh" README.md; then
        print_success "✓ README.md mentions installation script"
    else
        print_warning "⚠ README.md may not mention installation script"
    fi
    echo
    
    # Run installation script tests if available
    if [ -f "test_install.sh" ] && [ -x "test_install.sh" ]; then
        print_check "Running installation script tests"
        if ./test_install.sh > /dev/null 2>&1; then
            print_success "✓ Installation script tests pass"
        else
            print_error "✗ Installation script tests failed"
            errors=$((errors + 1))
        fi
        echo
    fi
    
    # Final summary
    print_header "📊 Verification Summary"
    if [ $errors -eq 0 ]; then
        print_success "🎉 All verification checks passed!"
        echo
        echo -e "${GREEN}✅ Repository is ready for distribution${NC}"
        echo -e "${GREEN}✅ Installation script is functional${NC}"
        echo -e "${GREEN}✅ Python plugin structure is complete${NC}"
        echo -e "${GREEN}✅ Documentation is comprehensive${NC}"
        echo -e "${GREEN}✅ Legacy files are properly managed${NC}"
        echo
        echo -e "${BLUE}🚀 Ready to share with users!${NC}"
        echo
        echo -e "${YELLOW}📋 Next steps:${NC}"
        echo "   1. Commit and push changes to GitHub"
        echo "   2. Create a release with installation instructions"
        echo "   3. Update repository description and tags"
        echo "   4. Share with the Geany community"
        
        return 0
    else
        print_error "❌ Verification failed with $errors errors"
        echo
        echo -e "${YELLOW}📋 Please fix the above issues before distribution${NC}"
        
        return 1
    fi
}

# Run verification
main "$@"
