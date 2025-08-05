#!/bin/bash

# Geany Copilot Lua Plugin Installation Script
# This script installs the Lua-based Geany Copilot plugin

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
    echo -e "${PURPLE}║${NC}           🚀 Geany Copilot Lua Plugin Installer             ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}                                                              ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}  Modern AI-powered code assistance without GeanyPy         ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}                                                              ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
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

main() {
    print_header
    
    # Step 1: Check prerequisites
    print_step "Checking Prerequisites"
    
    if ! command_exists geany; then
        print_error "Geany not found! Please install Geany first:"
        print_info "  sudo apt install geany"
        exit 1
    fi
    print_success "✓ Geany found"
    
    if ! check_package "geany-plugins"; then
        print_warning "GeanyLua not found. Installing geany-plugins..."
        if sudo apt install -y geany-plugins; then
            print_success "✓ GeanyLua installed"
        else
            print_error "Failed to install geany-plugins"
            exit 1
        fi
    else
        print_success "✓ GeanyLua available"
    fi
    
    # Step 2: Create directories
    print_step "Creating Plugin Directories"
    
    local plugin_dir="$HOME/.config/geany/plugins/geanylua"
    local config_dir="$HOME/.config/geany/geany-copilot"
    
    mkdir -p "$plugin_dir"
    mkdir -p "$config_dir"
    
    print_success "✓ Plugin directories created"
    
    # Step 3: Install Lua plugin
    print_step "Installing Lua Plugin"
    
    if [ -f "geany-copilot.lua" ]; then
        cp "geany-copilot.lua" "$plugin_dir/"
        chmod 644 "$plugin_dir/geany-copilot.lua"
        print_success "✓ Lua plugin installed to $plugin_dir/"
    else
        print_error "geany-copilot.lua not found in current directory"
        exit 1
    fi
    
    # Step 4: Check optional dependencies
    print_step "Checking Optional Dependencies"
    
    # Check for Lua JSON library
    if lua -e "require('lunajson')" 2>/dev/null; then
        print_success "✓ Lua JSON library available"
    else
        print_warning "Lua JSON library not found. Installing..."
        if sudo apt install -y lua-cjson; then
            print_success "✓ Lua JSON library installed"
        else
            print_warning "Could not install lua-cjson. JSON parsing may not work."
        fi
    fi
    
    # Check for Lua socket library
    if lua -e "require('socket.http')" 2>/dev/null; then
        print_success "✓ Lua socket library available"
    else
        print_warning "Lua socket library not found. Installing..."
        if sudo apt install -y lua-socket; then
            print_success "✓ Lua socket library installed"
        else
            print_warning "Could not install lua-socket. Direct API calls may not work."
            print_info "  You can still use the Python service backend."
        fi
    fi
    
    # Step 5: Optional Python service setup
    print_step "Python Service Setup (Optional)"
    
    if command_exists python3; then
        print_info "Python 3 found. Would you like to set up the Python service? (y/n)"
        read -r setup_python
        
        if [[ "$setup_python" =~ ^[Yy]$ ]]; then
            if [ -d "geany-copilot-python" ]; then
                print_info "Installing Python dependencies..."
                if pip3 install --user -r geany-copilot-python/requirements.txt; then
                    print_success "✓ Python dependencies installed"
                    print_info "You can start the Python service with:"
                    print_info "  python3 geany-copilot-python/service.py"
                else
                    print_warning "Failed to install Python dependencies"
                fi
            else
                print_warning "geany-copilot-python directory not found"
            fi
        fi
    else
        print_info "Python 3 not found. Skipping Python service setup."
    fi
    
    # Step 6: Final instructions
    print_step "Installation Complete!"
    
    print_success "🎉 Geany Copilot Lua plugin installed successfully!"
    echo
    print_info "Next steps:"
    print_info "1. Restart Geany completely:"
    print_info "   killall geany && geany"
    echo
    print_info "2. Enable GeanyLua in Plugin Manager:"
    print_info "   Tools → Plugin Manager → Check 'GeanyLua' → OK"
    echo
    print_info "3. Look for new menu items:"
    print_info "   Tools → AI Code Assistant"
    print_info "   Tools → AI Copywriter"
    print_info "   Tools → Copilot Settings"
    echo
    print_info "4. Configure your API settings:"
    print_info "   Tools → Copilot Settings"
    print_info "   - Choose API provider (DeepSeek recommended)"
    print_info "   - Enter your API key"
    print_info "   - Optionally enable Python service"
    echo
    
    if [ ! -f "$HOME/.config/geany/geany-copilot/config.json" ]; then
        print_info "5. Configuration file will be created automatically on first use"
    fi
    
    echo
    print_success "Installation completed successfully! 🚀"
    print_info "Enjoy your AI-powered Geany IDE experience!"
}

# Run the installation
main "$@"
