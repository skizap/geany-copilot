#!/bin/bash

# Geany Copilot Python Plugin Installation Script
# This script installs the Python version and manages legacy Lua files
# Author: Geany Copilot Team
# License: MIT

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_NAME="geany-copilot-python"
PYTHON_SOURCE_DIR="$SCRIPT_DIR/geany-copilot-python"
OLD_DIR="$SCRIPT_DIR/OLD"
LOG_FILE="/tmp/geany-copilot-install.log"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
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

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Python version
get_python_version() {
    if command_exists python3; then
        python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    elif command_exists python; then
        python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    else
        echo "0.0"
    fi
}

# Function to compare version numbers
version_ge() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Function to find Geany plugin directories
find_geany_plugin_dirs() {
    local dirs=()
    
    # User-specific directories (preferred)
    if [ -d "$HOME/.config/geany/plugins" ]; then
        dirs+=("$HOME/.config/geany/plugins")
    fi
    
    if [ -d "$HOME/.geany/plugins" ]; then
        dirs+=("$HOME/.geany/plugins")
    fi
    
    # Legacy GeanyLua directories
    if [ -d "$HOME/.config/geany/plugins/geanylua" ]; then
        dirs+=("$HOME/.config/geany/plugins/geanylua")
    fi
    
    if [ -d "$HOME/.geany/plugins/geanylua" ]; then
        dirs+=("$HOME/.geany/plugins/geanylua")
    fi
    
    # System-wide directories (if writable)
    for dir in "/usr/local/lib/geany" "/usr/lib/geany" "/usr/local/share/geany/plugins" "/usr/share/geany/plugins"; do
        if [ -d "$dir" ] && [ -w "$dir" ]; then
            dirs+=("$dir")
        fi
    done
    
    printf '%s\n' "${dirs[@]}"
}

# Function to select installation directory
select_install_dir() {
    local dirs
    mapfile -t dirs < <(find_geany_plugin_dirs)
    
    if [ ${#dirs[@]} -eq 0 ]; then
        print_warning "No existing Geany plugin directories found."
        local default_dir="$HOME/.config/geany/plugins"
        print_status "Creating default directory: $default_dir"
        mkdir -p "$default_dir"
        echo "$default_dir"
        return
    fi
    
    if [ ${#dirs[@]} -eq 1 ]; then
        echo "${dirs[0]}"
        return
    fi
    
    print_status "Multiple Geany plugin directories found:"
    for i in "${!dirs[@]}"; do
        echo "  $((i+1)). ${dirs[i]}"
    done
    
    while true; do
        read -p "Select installation directory (1-${#dirs[@]}): " choice
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#dirs[@]} ]; then
            echo "${dirs[$((choice-1))]}"
            return
        else
            print_error "Invalid selection. Please choose 1-${#dirs[@]}."
        fi
    done
}

# Function to check GeanyPy installation
check_geanypy() {
    print_status "Checking GeanyPy plugin availability"

    # Check if GeanyPy packages are installed
    local geanypy_packages=("geany-plugin-py" "geany-plugins-py" "geany-plugins")
    local geanypy_found=false

    for package in "${geanypy_packages[@]}"; do
        if command_exists dpkg && dpkg -l | grep -q "^ii.*$package"; then
            print_success "GeanyPy package found: $package"
            geanypy_found=true
            break
        elif command_exists rpm && rpm -qa | grep -q "$package"; then
            print_success "GeanyPy package found: $package"
            geanypy_found=true
            break
        elif command_exists pacman && pacman -Q | grep -q "$package"; then
            print_success "GeanyPy package found: $package"
            geanypy_found=true
            break
        fi
    done

    if [ "$geanypy_found" = false ]; then
        print_warning "GeanyPy package not detected"
        print_status "Attempting to install GeanyPy..."

        # Try to install GeanyPy based on the package manager
        if command_exists apt; then
            for package in "${geanypy_packages[@]}"; do
                if sudo apt install -y "$package" 2>/dev/null; then
                    print_success "Successfully installed $package"
                    geanypy_found=true
                    break
                fi
            done
        elif command_exists dnf; then
            if sudo dnf install -y geany-plugins-geanypy 2>/dev/null; then
                print_success "Successfully installed geany-plugins-geanypy"
                geanypy_found=true
            fi
        elif command_exists pacman; then
            if sudo pacman -S --noconfirm geany-plugins 2>/dev/null; then
                print_success "Successfully installed geany-plugins"
                geanypy_found=true
            fi
        fi

        if [ "$geanypy_found" = false ]; then
            print_warning "Could not automatically install GeanyPy"
            print_warning "Please install GeanyPy manually or use the troubleshooting script:"
            print_warning "  ./troubleshoot_geanypy.sh"
            print_warning "Or see GEANYPY_INSTALLATION.md for detailed instructions"
        fi
    fi

    # Check Python GTK dependencies
    print_status "Checking Python GTK dependencies"
    if python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" 2>/dev/null; then
        print_success "Python GTK bindings are working"
    else
        print_warning "Python GTK bindings may have issues"
        print_status "Installing Python GTK dependencies..."
        if command_exists apt; then
            sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 2>/dev/null || true
        fi
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_header "🔍 Checking Prerequisites"
    
    local errors=0
    
    # Check Python version
    local python_version
    python_version=$(get_python_version)
    if version_ge "$python_version" "3.6"; then
        print_success "Python $python_version found"
    else
        print_error "Python 3.6+ is required (found: $python_version)"
        errors=$((errors + 1))
    fi
    
    # Check pip
    if command_exists pip3 || command_exists pip; then
        print_success "pip found"
    else
        print_error "pip is required but not found"
        errors=$((errors + 1))
    fi
    
    # Check if Geany is installed
    if command_exists geany; then
        print_success "Geany found"
    else
        print_warning "Geany not found in PATH (may still be installed)"
    fi

    # Check GeanyPy
    check_geanypy
    
    # Check for source directory
    if [ ! -d "$PYTHON_SOURCE_DIR" ]; then
        print_error "Python plugin source directory not found: $PYTHON_SOURCE_DIR"
        errors=$((errors + 1))
    else
        print_success "Python plugin source found"
    fi
    
    if [ $errors -gt 0 ]; then
        print_error "Prerequisites check failed. Please resolve the above issues."
        exit 1
    fi
    
    log_message "Prerequisites check passed"
}

# Function to manage legacy Lua files
manage_legacy_files() {
    print_header "📁 Managing Legacy Lua Files"
    
    # Create OLD directory if it doesn't exist
    if [ ! -d "$OLD_DIR" ]; then
        mkdir -p "$OLD_DIR"
        print_status "Created OLD directory: $OLD_DIR"
    fi
    
    # List of Lua files to move
    local lua_files=("copilot.lua" "copywriter.lua")
    local moved_files=0
    
    for file in "${lua_files[@]}"; do
        local source_file="$SCRIPT_DIR/$file"
        local dest_file="$OLD_DIR/$file"
        
        if [ -f "$source_file" ]; then
            if [ ! -f "$dest_file" ]; then
                mv "$source_file" "$dest_file"
                print_success "Moved $file to OLD directory"
                moved_files=$((moved_files + 1))
            else
                print_warning "$file already exists in OLD directory, skipping"
            fi
        fi
    done
    
    # Move any other .lua files
    for lua_file in "$SCRIPT_DIR"/*.lua; do
        if [ -f "$lua_file" ]; then
            local filename=$(basename "$lua_file")
            local dest_file="$OLD_DIR/$filename"
            
            if [ ! -f "$dest_file" ]; then
                mv "$lua_file" "$dest_file"
                print_success "Moved $filename to OLD directory"
                moved_files=$((moved_files + 1))
            fi
        fi
    done
    
    if [ $moved_files -gt 0 ]; then
        print_success "Moved $moved_files legacy Lua files to OLD directory"
        echo -e "${CYAN}Legacy files are preserved in: $OLD_DIR${NC}"
    else
        print_status "No legacy Lua files found to move"
    fi
    
    log_message "Legacy file management completed"
}

# Function to install Python dependencies
install_dependencies() {
    print_header "📦 Installing Python Dependencies"

    local requirements_file="$PYTHON_SOURCE_DIR/requirements.txt"

    if [ ! -f "$requirements_file" ]; then
        print_warning "requirements.txt not found, skipping dependency installation"
        return
    fi

    print_status "Installing Python dependencies..."

    # Determine pip command
    local pip_cmd
    if command_exists pip3; then
        pip_cmd="pip3"
    elif command_exists pip; then
        pip_cmd="pip"
    else
        print_error "pip not found"
        exit 1
    fi

    # Install dependencies
    if $pip_cmd install --user -r "$requirements_file" >> "$LOG_FILE" 2>&1; then
        print_success "Python dependencies installed successfully"
    else
        print_warning "Some dependencies may have failed to install (check log: $LOG_FILE)"
        print_status "This is often normal for system-provided packages like GTK"
    fi

    log_message "Python dependencies installation completed"
}

# Function to install plugin files
install_plugin_files() {
    print_header "🚀 Installing Plugin Files"

    local install_dir
    install_dir=$(select_install_dir)
    local plugin_dir="$install_dir/$PLUGIN_NAME"

    echo  # Add blank line for better formatting
    print_status "Installing to: $plugin_dir"

    # Create plugin directory
    if [ ! -d "$plugin_dir" ]; then
        mkdir -p "$plugin_dir"
        print_status "Created plugin directory"
    fi

    # Copy plugin files
    print_status "Copying plugin files..."
    if cp -r "$PYTHON_SOURCE_DIR"/* "$plugin_dir/" >> "$LOG_FILE" 2>&1; then
        print_success "Plugin files copied successfully"
    else
        print_error "Failed to copy plugin files"
        exit 1
    fi

    # Set proper permissions
    print_status "Setting file permissions..."
    find "$plugin_dir" -type f -name "*.py" -exec chmod 644 {} \;
    find "$plugin_dir" -type d -exec chmod 755 {} \;

    # Make install script executable
    if [ -f "$plugin_dir/install.py" ]; then
        chmod +x "$plugin_dir/install.py"
    fi

    print_success "File permissions set correctly"

    # Store installation path for later use
    echo "$plugin_dir" > "/tmp/geany-copilot-install-path"

    log_message "Plugin files installation completed: $plugin_dir"
}

# Function to verify installation
verify_installation() {
    print_header "✅ Verifying Installation"

    local plugin_dir
    plugin_dir=$(cat "/tmp/geany-copilot-install-path" 2>/dev/null || echo "")

    if [ -z "$plugin_dir" ] || [ ! -d "$plugin_dir" ]; then
        print_error "Plugin directory not found"
        return 1
    fi

    # Check essential files
    local essential_files=("__init__.py" "plugin.py" "requirements.txt")
    local missing_files=0

    for file in "${essential_files[@]}"; do
        if [ -f "$plugin_dir/$file" ]; then
            print_success "✓ $file"
        else
            print_error "✗ $file (missing)"
            missing_files=$((missing_files + 1))
        fi
    done

    # Check directories
    local essential_dirs=("core" "agents" "ui" "utils")
    for dir in "${essential_dirs[@]}"; do
        if [ -d "$plugin_dir/$dir" ]; then
            print_success "✓ $dir/ directory"
        else
            print_error "✗ $dir/ directory (missing)"
            missing_files=$((missing_files + 1))
        fi
    done

    if [ $missing_files -eq 0 ]; then
        print_success "Installation verification passed"
        return 0
    else
        print_error "Installation verification failed ($missing_files missing files/directories)"
        return 1
    fi
}

# Function to run plugin tests
run_tests() {
    print_header "🧪 Running Plugin Tests"

    local plugin_dir
    plugin_dir=$(cat "/tmp/geany-copilot-install-path" 2>/dev/null || echo "")

    if [ -z "$plugin_dir" ] || [ ! -f "$plugin_dir/test_plugin.py" ]; then
        print_warning "Test file not found, skipping tests"
        return
    fi

    print_status "Running plugin tests..."

    # Change to plugin directory and run tests
    if (cd "$plugin_dir" && python3 test_plugin.py) >> "$LOG_FILE" 2>&1; then
        print_success "All plugin tests passed"
    else
        print_warning "Some tests may have failed (check log: $LOG_FILE)"
        print_status "This is often normal when GeanyPy is not available outside Geany"
    fi

    log_message "Plugin tests completed"
}

# Function to provide post-installation instructions
show_post_install_instructions() {
    print_header "🎉 Installation Complete!"

    local plugin_dir
    plugin_dir=$(cat "/tmp/geany-copilot-install-path" 2>/dev/null || echo "")

    echo
    print_success "Geany Copilot Python plugin has been installed successfully!"
    echo
    echo -e "${CYAN}📍 Installation Location:${NC}"
    echo "   $plugin_dir"
    echo
    echo -e "${CYAN}🔧 Next Steps:${NC}"
    echo "   1. Start or restart Geany IDE"
    echo "   2. Go to Tools → Plugin Manager"
    echo "   3. Enable 'GeanyPy' if not already enabled"
    echo "   4. The Geany Copilot Python plugin should load automatically"
    echo "   5. Look for 'Copilot' menu items in the Tools menu"
    echo
    echo -e "${CYAN}⚙️  Configuration:${NC}"
    echo "   1. Go to Tools → Copilot → Settings"
    echo "   2. Configure your API provider (DeepSeek recommended)"
    echo "   3. Enter your API key"
    echo "   4. Adjust other settings as needed"
    echo
    echo -e "${CYAN}🔑 API Key Setup:${NC}"
    echo "   • DeepSeek: Get your key from https://platform.deepseek.com/"
    echo "   • OpenAI: Get your key from https://platform.openai.com/"
    echo "   • Custom: Configure your own OpenAI-compatible endpoint"
    echo
    echo -e "${CYAN}📚 Documentation:${NC}"
    echo "   • Plugin README: $plugin_dir/README.md"
    echo "   • Integration Guide: $plugin_dir/INTEGRATION.md"
    echo "   • Legacy Lua files: $OLD_DIR"
    echo
    echo -e "${CYAN}🐛 Troubleshooting:${NC}"
    echo "   • Installation log: $LOG_FILE"
    echo "   • Plugin logs: ~/.config/geany/plugins/$PLUGIN_NAME/logs/"
    echo "   • If plugin doesn't appear, check GeanyPy is enabled"
    echo "   • For issues, check: https://github.com/skizap/geany-copilot"
    echo

    log_message "Post-installation instructions displayed"
}

# Function to handle errors
handle_error() {
    local exit_code=$?
    print_error "Installation failed with exit code $exit_code"
    echo
    echo -e "${YELLOW}📋 Troubleshooting Information:${NC}"
    echo "   • Check the installation log: $LOG_FILE"
    echo "   • Ensure you have Python 3.6+ and pip installed"
    echo "   • Make sure you have write permissions to Geany plugin directories"
    echo "   • Try running the script with sudo if permission issues persist"
    echo "   • For help, visit: https://github.com/skizap/geany-copilot"
    echo
    log_message "Installation failed with exit code $exit_code"
    exit $exit_code
}

# Function to cleanup temporary files
cleanup() {
    rm -f "/tmp/geany-copilot-install-path" 2>/dev/null || true
}

# Main installation function
main() {
    # Set up error handling
    trap handle_error ERR
    trap cleanup EXIT

    # Clear log file
    > "$LOG_FILE"

    # Print banner
    echo
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                                                              ║${NC}"
    echo -e "${PURPLE}║           🤖 Geany Copilot Python Plugin Installer          ║${NC}"
    echo -e "${PURPLE}║                                                              ║${NC}"
    echo -e "${PURPLE}║  AI-powered code assistant with agent capabilities          ║${NC}"
    echo -e "${PURPLE}║                                                              ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo

    log_message "Installation started"

    # Check if running as root (warn but don't prevent)
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root. Consider running as regular user for user-local installation."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Installation cancelled by user"
            exit 0
        fi
    fi

    # Run installation steps
    check_prerequisites
    manage_legacy_files
    install_dependencies
    install_plugin_files

    # Verify installation
    if verify_installation; then
        run_tests
        show_post_install_instructions

        print_success "🎉 Installation completed successfully!"
        log_message "Installation completed successfully"
    else
        print_error "Installation verification failed"
        exit 1
    fi
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed directly
    main "$@"
fi
