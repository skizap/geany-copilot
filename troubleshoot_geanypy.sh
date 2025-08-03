#!/bin/bash

# GeanyPy Troubleshooting Script for Linux Mint
# This script diagnoses and attempts to fix GeanyPy installation issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}                                                              ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}           🔧 GeanyPy Troubleshooting Script                  ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}                                                              ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}  Diagnose and fix GeanyPy installation issues              ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}                                                              ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
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

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_fix() {
    echo -e "${GREEN}[FIX]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check package installation
check_package() {
    local package="$1"
    if dpkg -l | grep -q "^ii.*$package"; then
        return 0
    else
        return 1
    fi
}

# Main troubleshooting function
main() {
    print_header
    
    # Step 1: System Information
    print_step "Gathering System Information"
    print_info "Linux Distribution: $(lsb_release -d | cut -f2)"
    print_info "Kernel Version: $(uname -r)"
    if command_exists geany; then
        print_info "Geany Version: $(geany --version | head -1)"
    else
        print_error "Geany not found!"
        exit 1
    fi
    print_info "Python Version: $(python3 --version)"
    echo
    
    # Step 2: Check GeanyPy Package Installation
    print_step "Checking GeanyPy Package Installation"
    
    local geanypy_found=false
    local packages_to_check=("geany-plugin-py" "geany-plugins-py" "geany-plugins")
    
    for package in "${packages_to_check[@]}"; do
        print_check "Checking for package: $package"
        if check_package "$package"; then
            print_success "✓ Package $package is installed"
            geanypy_found=true
        else
            print_warning "✗ Package $package not found"
        fi
    done
    
    if [ "$geanypy_found" = false ]; then
        print_error "No GeanyPy packages found!"
        print_fix "Attempting to install GeanyPy..."
        
        # Try different package names
        for package in "${packages_to_check[@]}"; do
            print_info "Trying to install $package..."
            if sudo apt install -y "$package" 2>/dev/null; then
                print_success "Successfully installed $package"
                geanypy_found=true
                break
            else
                print_warning "Failed to install $package"
            fi
        done
        
        if [ "$geanypy_found" = false ]; then
            print_error "Could not install GeanyPy via package manager"
            print_info "You may need to:"
            print_info "  1. Update package list: sudo apt update"
            print_info "  2. Try manual installation (see GEANYPY_INSTALLATION.md)"
            print_info "  3. Use the Lua version instead"
        fi
    fi
    echo
    
    # Step 3: Check Python GTK Dependencies
    print_step "Checking Python GTK Dependencies"
    
    local gtk_deps=("python3-gi" "python3-gi-cairo" "gir1.2-gtk-3.0")
    local missing_deps=()
    
    for dep in "${gtk_deps[@]}"; do
        print_check "Checking for $dep"
        if check_package "$dep"; then
            print_success "✓ $dep is installed"
        else
            print_warning "✗ $dep is missing"
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_fix "Installing missing Python GTK dependencies..."
        if sudo apt install -y "${missing_deps[@]}"; then
            print_success "Successfully installed missing dependencies"
        else
            print_error "Failed to install some dependencies"
        fi
    fi
    echo
    
    # Step 4: Test Python GTK Import
    print_step "Testing Python GTK Import"
    print_check "Testing Python GTK bindings..."
    
    if python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK import successful')" 2>/dev/null; then
        print_success "✓ Python GTK bindings work correctly"
    else
        print_error "✗ Python GTK bindings not working"
        print_fix "Try installing: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0"
    fi
    echo
    
    # Step 5: Check Geany Plugin Directories
    print_step "Checking Geany Plugin Directories"
    
    local plugin_dirs=(
        "/usr/lib/geany"
        "/usr/lib/x86_64-linux-gnu/geany"
        "/usr/local/lib/geany"
        "$HOME/.local/lib/geany"
    )
    
    for dir in "${plugin_dirs[@]}"; do
        print_check "Checking directory: $dir"
        if [ -d "$dir" ]; then
            print_success "✓ Directory exists"
            # Look for GeanyPy files
            if find "$dir" -name "*py*.so" -o -name "*geanypy*" | grep -q .; then
                print_success "  → GeanyPy files found in $dir"
                find "$dir" -name "*py*.so" -o -name "*geanypy*" | while read file; do
                    print_info "    - $(basename "$file")"
                done
            else
                print_warning "  → No GeanyPy files found in $dir"
            fi
        else
            print_warning "✗ Directory does not exist"
        fi
    done
    echo
    
    # Step 6: Check User Plugin Directory
    print_step "Checking User Plugin Directory"
    local user_plugin_dir="$HOME/.config/geany/plugins"
    
    print_check "Checking user plugin directory: $user_plugin_dir"
    if [ -d "$user_plugin_dir" ]; then
        print_success "✓ User plugin directory exists"
        print_info "Contents:"
        ls -la "$user_plugin_dir" | while read line; do
            print_info "  $line"
        done
    else
        print_warning "✗ User plugin directory does not exist"
        print_fix "Creating user plugin directory..."
        mkdir -p "$user_plugin_dir"
        print_success "Created $user_plugin_dir"
    fi
    echo
    
    # Step 7: Create Test Plugin
    print_step "Creating Test GeanyPy Plugin"
    local test_plugin_dir="$user_plugin_dir/geanypy-test"
    
    print_info "Creating test plugin in: $test_plugin_dir"
    mkdir -p "$test_plugin_dir"
    
    cat > "$test_plugin_dir/__init__.py" << 'EOF'
"""
GeanyPy Test Plugin
This plugin tests if GeanyPy is working correctly.
"""

import geany

def plugin_init():
    """Initialize the test plugin."""
    try:
        geany.main_widgets.statusbar.push(0, "GeanyPy Test Plugin: SUCCESS! GeanyPy is working.")
        return True
    except Exception as e:
        print(f"GeanyPy Test Plugin Error: {e}")
        return False

def plugin_cleanup():
    """Cleanup the test plugin."""
    try:
        geany.main_widgets.statusbar.push(0, "GeanyPy Test Plugin: Cleaned up.")
    except:
        pass

# Plugin information
__plugin_name__ = "GeanyPy Test"
__plugin_version__ = "1.0"
__plugin_description__ = "Test plugin to verify GeanyPy functionality"
__plugin_author__ = "Geany Copilot Installer"
EOF
    
    print_success "✓ Test plugin created"
    print_info "Plugin file: $test_plugin_dir/__init__.py"
    echo
    
    # Step 8: Final Instructions
    print_step "Next Steps"
    print_info "1. Restart Geany completely:"
    print_info "   killall geany && geany"
    echo
    print_info "2. Check Plugin Manager:"
    print_info "   Tools → Plugin Manager → Look for 'GeanyPy'"
    echo
    print_info "3. Enable GeanyPy:"
    print_info "   Check the GeanyPy checkbox and click OK"
    echo
    print_info "4. Look for test message:"
    print_info "   Check Geany's status bar for 'GeanyPy Test Plugin: SUCCESS!'"
    echo
    print_info "5. Check Message Window:"
    print_info "   View → Show Message Window → Look for Python plugin messages"
    echo
    
    # Step 9: Troubleshooting Summary
    print_step "Troubleshooting Summary"
    
    if [ "$geanypy_found" = true ]; then
        print_success "✓ GeanyPy package appears to be installed"
    else
        print_error "✗ GeanyPy package installation issues detected"
    fi
    
    if python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" 2>/dev/null; then
        print_success "✓ Python GTK bindings are working"
    else
        print_error "✗ Python GTK bindings have issues"
    fi
    
    if [ -f "$test_plugin_dir/__init__.py" ]; then
        print_success "✓ Test plugin created successfully"
    else
        print_error "✗ Failed to create test plugin"
    fi
    
    echo
    print_info "📋 If GeanyPy still doesn't work:"
    print_info "   • Check GEANYPY_INSTALLATION.md for detailed instructions"
    print_info "   • Consider using the Lua version (files in OLD/ directory)"
    print_info "   • Report the issue with your system details"
    echo
    print_success "🎉 Troubleshooting complete!"
}

# Run the troubleshooting
main "$@"
