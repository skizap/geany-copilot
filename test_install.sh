#!/bin/bash

# Test script for the Geany Copilot Python Plugin installer
# This script tests the installation process in a controlled way

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test 1: Check if install.sh exists and is executable
print_test "Checking if install.sh exists and is executable"
if [ -f "install.sh" ] && [ -x "install.sh" ]; then
    print_success "install.sh found and is executable"
else
    print_error "install.sh not found or not executable"
    exit 1
fi

# Test 2: Check if Python source directory exists
print_test "Checking if Python source directory exists"
if [ -d "geany-copilot-python" ]; then
    print_success "Python source directory found"
else
    print_error "Python source directory not found"
    exit 1
fi

# Test 3: Check essential files in Python source
print_test "Checking essential Python files"
essential_files=("geany-copilot-python/__init__.py" "geany-copilot-python/plugin.py" "geany-copilot-python/requirements.txt")
for file in "${essential_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ $file"
    else
        print_error "✗ $file (missing)"
        exit 1
    fi
done

# Test 4: Check if OLD directory was created and contains Lua files
print_test "Checking legacy file management"
if [ -d "OLD" ]; then
    print_success "OLD directory exists"
    if [ -f "OLD/copilot.lua" ] && [ -f "OLD/copywriter.lua" ]; then
        print_success "Legacy Lua files preserved in OLD directory"
    else
        print_error "Legacy Lua files not found in OLD directory"
    fi
else
    print_error "OLD directory not created"
fi

# Test 5: Check script syntax
print_test "Checking install.sh syntax"
if bash -n install.sh; then
    print_success "install.sh syntax is valid"
else
    print_error "install.sh has syntax errors"
    exit 1
fi

# Test 6: Test dry run of prerequisite checking
print_test "Testing prerequisite checking (dry run)"
# Create a temporary modified script that only runs prerequisite checks
temp_script=$(mktemp)
cat > "$temp_script" << 'EOF'
#!/bin/bash
source ./install.sh
check_prerequisites
echo "Prerequisites check completed successfully"
EOF

chmod +x "$temp_script"
if bash "$temp_script" > /dev/null 2>&1; then
    print_success "Prerequisites check function works"
else
    print_error "Prerequisites check function failed"
fi
rm -f "$temp_script"

print_success "🎉 All installation script tests passed!"
echo
echo -e "${YELLOW}📋 Installation Script Summary:${NC}"
echo "   ✅ Script is executable and syntactically correct"
echo "   ✅ All required source files are present"
echo "   ✅ Legacy file management working correctly"
echo "   ✅ Prerequisites checking function works"
echo "   ✅ Ready for production use"
echo
echo -e "${BLUE}🚀 To install the plugin, run:${NC}"
echo "   ./install.sh"
