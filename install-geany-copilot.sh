#!/bin/bash

# Geany Copilot Installation Script
# Automated installation and setup for Geany Copilot Lua plugin

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PLUGIN_NAME="geany-copilot.lua"
CONFIG_DIR="$HOME/.config/geany/geany-copilot"
PLUGIN_DIR="$HOME/.config/geany/plugins/geanylua"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}=== Geany Copilot Installation Script ===${NC}"
echo "This script will install and configure the Geany Copilot plugin."
echo

# Function to print status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "This script should not be run as root. Please run as a regular user."
    exit 1
fi

# Step 1: Check system requirements
print_status "Checking system requirements..."

# Check if Geany is installed
if ! command -v geany &> /dev/null; then
    print_error "Geany is not installed. Please install Geany first:"
    echo "sudo apt install geany"
    exit 1
fi

# Check if GeanyLua plugin is installed
if ! dpkg -l | grep -q geany-plugin-lua; then
    print_warning "GeanyLua plugin not found. Installing..."
    sudo apt update
    sudo apt install -y geany-plugin-lua
    print_status "GeanyLua plugin installed successfully"
else
    print_status "GeanyLua plugin is already installed"
fi

# Step 2: Install Lua dependencies
print_status "Installing Lua dependencies..."

# Check and install required packages
PACKAGES=("lua-cjson" "lua-socket" "lua-sec")
MISSING_PACKAGES=()

for package in "${PACKAGES[@]}"; do
    if ! dpkg -l | grep -q "^ii.*$package"; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    print_status "Installing missing packages: ${MISSING_PACKAGES[*]}"
    sudo apt update
    sudo apt install -y "${MISSING_PACKAGES[@]}"
    print_status "Lua dependencies installed successfully"
else
    print_status "All Lua dependencies are already installed"
fi

# Step 3: Clean up old plugin files
print_status "Cleaning up old plugin files..."

# Remove old conflicting files
OLD_FILES=("$PLUGIN_DIR/copilot.lua" "$PLUGIN_DIR/copywriter.lua")
for file in "${OLD_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_warning "Removing old plugin file: $file"
        rm "$file"
    fi
done

# Step 4: Create necessary directories
print_status "Creating configuration directories..."
mkdir -p "$CONFIG_DIR"
mkdir -p "$PLUGIN_DIR"

# Step 5: Install the plugin
print_status "Installing Geany Copilot plugin..."

if [ -f "$SCRIPT_DIR/$PLUGIN_NAME" ]; then
    cp "$SCRIPT_DIR/$PLUGIN_NAME" "$PLUGIN_DIR/"
    chmod 644 "$PLUGIN_DIR/$PLUGIN_NAME"
    print_status "Plugin installed to $PLUGIN_DIR/$PLUGIN_NAME"
else
    print_error "Plugin file $PLUGIN_NAME not found in script directory"
    exit 1
fi

# Step 6: Test Lua dependencies
print_status "Testing Lua dependencies..."

lua -e "
local function test_module(name)
    local success, module = pcall(require, name)
    if success then
        print('✓ ' .. name .. ' - OK')
        return true
    else
        print('✗ ' .. name .. ' - FAILED')
        return false
    end
end

local all_ok = true
all_ok = test_module('cjson') and all_ok
all_ok = test_module('socket') and all_ok
all_ok = test_module('ssl.https') and all_ok

if all_ok then
    print('All dependencies are working correctly!')
else
    print('Some dependencies failed to load.')
    os.exit(1)
end
"

if [ $? -eq 0 ]; then
    print_status "All Lua dependencies are working correctly"
else
    print_warning "Some Lua dependencies may not be working properly"
fi

# Step 7: Create default configuration
print_status "Creating default configuration..."

if [ ! -f "$CONFIG_DIR/config.json" ]; then
    cat > "$CONFIG_DIR/config.json" << 'EOF'
{
    "api-provider": "deepseek",
    "deepseek-api-key": "",
    "deepseek-base-url": "https://api.deepseek.com/v1",
    "openai-api-key": "",
    "openai-base-url": "https://api.openai.com/v1",
    "custom-base-url": "http://localhost:11434/v1",
    "custom-api-key": "",
    "model": "deepseek-coder",
    "temperature": 0.7,
    "max-tokens": 2048,
    "use-python-service": false,
    "python-service-url": "http://localhost:8000",
    "system-prompt": "You are a helpful coding assistant. Provide clear, concise, and accurate code suggestions.",
    "copywriter-prompt": "You are a professional copywriter. Help improve and refine text content."
}
EOF
    print_status "Default configuration created at $CONFIG_DIR/config.json"
else
    print_status "Configuration file already exists"
fi

# Step 8: Installation summary
echo
echo -e "${GREEN}=== Installation Complete! ===${NC}"
echo
print_status "Next steps:"
echo "1. Restart Geany completely (close and reopen)"
echo "2. Go to Tools → Plugin Manager"
echo "3. Ensure 'GeanyLua' is enabled (checked)"
echo "4. Look for these new menu items under Tools:"
echo "   - AI Code Assistant"
echo "   - AI Copywriter"
echo "   - Copilot Settings"
echo "5. Configure your API keys in Tools → Copilot Settings"
echo
print_status "Configuration file location: $CONFIG_DIR/config.json"
print_status "Plugin file location: $PLUGIN_DIR/$PLUGIN_NAME"
echo
print_warning "Important: You need to configure API keys before using the plugin!"
echo "Edit $CONFIG_DIR/config.json or use the Copilot Settings menu."
echo

# Step 9: Verification
echo -e "${BLUE}=== Verification ===${NC}"
echo "Run this command to verify the installation:"
echo "lua -e \"require('cjson'); require('socket'); print('Dependencies OK')\""
echo
echo "If you encounter SSL/HTTPS errors, ensure lua-sec is properly installed:"
echo "sudo apt install lua-sec"
echo

print_status "Installation script completed successfully!"
