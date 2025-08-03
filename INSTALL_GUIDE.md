# 🚀 Geany Copilot Python Plugin - Installation Guide

This guide provides comprehensive instructions for installing the Geany Copilot Python plugin using the automated installation script.

## 📋 **Quick Start**

### **Automated Installation (Recommended)**

1. **Download or clone** this repository:
   ```bash
   git clone https://github.com/skizap/geany-copilot.git
   cd geany-copilot
   ```

2. **Run the installation script**:
   ```bash
   ./install.sh
   ```

3. **Follow the prompts** and restart Geany when complete.

That's it! The script handles everything automatically.

## 🔧 **What the Installation Script Does**

### **✅ Prerequisites Check**
- Verifies Python 3.6+ is installed
- Checks for pip package manager
- Detects Geany IDE installation
- Validates plugin source files

### **📁 Legacy File Management**
- Creates an `OLD/` directory in the repository root
- Moves existing Lua files (`copilot.lua`, `copywriter.lua`) to `OLD/`
- Preserves original files for users who want to continue using them
- Ensures clean transition from Lua to Python version

### **📦 Dependency Installation**
- Installs Python dependencies using pip
- Uses `--user` flag for user-local installation
- Handles system-provided packages gracefully (GTK, etc.)
- Provides clear feedback on installation status

### **🎯 Plugin Installation**
- Detects appropriate Geany plugin directories
- Supports multiple installation locations:
  - `~/.config/geany/plugins/` (preferred)
  - `~/.geany/plugins/`
  - Legacy GeanyLua directories
  - System-wide locations (if writable)
- Copies all plugin files with proper permissions
- Creates necessary directory structure

### **✅ Verification & Testing**
- Verifies all essential files are installed
- Runs plugin test suite to ensure functionality
- Provides detailed installation summary
- Logs all activities for troubleshooting

## 🖥️ **System Requirements**

### **Operating System**
- Linux (Ubuntu, Debian, Fedora, openSUSE, Arch, etc.)
- Other Unix-like systems with bash support

### **Software Requirements**
- **Python 3.6+** (Python 3.8+ recommended)
- **pip** package manager
- **Geany IDE** with GeanyPy plugin support
- **bash** shell (usually pre-installed)

### **Optional Dependencies**
- **GTK+ 3.0+** (usually system-provided)
- **PyGTK/PyGObject** (usually system-provided)

## 📂 **Installation Locations**

The script automatically detects and offers these installation locations:

### **User-Local (Recommended)**
```
~/.config/geany/plugins/geany-copilot-python/
```
- No root privileges required
- User-specific installation
- Easy to manage and update

### **Legacy GeanyLua Directory**
```
~/.config/geany/plugins/geanylua/geany-copilot-python/
```
- Compatible with existing GeanyLua setups
- Maintains existing plugin structure

### **System-Wide (Advanced)**
```
/usr/local/lib/geany/geany-copilot-python/
/usr/share/geany/plugins/geany-copilot-python/
```
- Requires root privileges
- Available to all users
- Managed by system administrator

## 🎮 **Interactive Installation Process**

### **Step 1: Prerequisites**
```
🔍 Checking Prerequisites
[SUCCESS] Python 3.12 found
[SUCCESS] pip found
[SUCCESS] Geany found
[SUCCESS] Python plugin source found
```

### **Step 2: Legacy Management**
```
📁 Managing Legacy Lua Files
[SUCCESS] Moved copilot.lua to OLD directory
[SUCCESS] Moved copywriter.lua to OLD directory
Legacy files are preserved in: /path/to/geany-copilot/OLD
```

### **Step 3: Dependencies**
```
📦 Installing Python Dependencies
[INFO] Installing Python dependencies...
[SUCCESS] Python dependencies installed successfully
```

### **Step 4: Directory Selection**
```
🚀 Installing Plugin Files
Multiple Geany plugin directories found:
  1. /home/user/.config/geany/plugins
  2. /home/user/.config/geany/plugins/geanylua
Select installation directory (1-2): 1
```

### **Step 5: Installation**
```
[INFO] Installing to: /home/user/.config/geany/plugins/geany-copilot-python
[SUCCESS] Plugin files copied successfully
[SUCCESS] File permissions set correctly
```

### **Step 6: Verification**
```
✅ Verifying Installation
[SUCCESS] ✓ __init__.py
[SUCCESS] ✓ plugin.py
[SUCCESS] ✓ requirements.txt
[SUCCESS] ✓ core/ directory
[SUCCESS] ✓ agents/ directory
[SUCCESS] ✓ ui/ directory
[SUCCESS] ✓ utils/ directory
[SUCCESS] Installation verification passed
```

## 🔧 **Post-Installation Setup**

### **1. Enable GeanyPy in Geany**
1. Start Geany IDE
2. Go to **Tools → Plugin Manager**
3. Find and enable **GeanyPy** if not already enabled
4. Click **OK** to apply changes

### **2. Verify Plugin Loading**
1. Restart Geany
2. Check **Tools** menu for **Copilot** submenu
3. If not visible, check Geany's message window for errors

### **3. Configure API Settings**
1. Go to **Tools → Copilot → Settings**
2. Select your preferred API provider:
   - **DeepSeek** (recommended): Fast, affordable, high-quality
   - **OpenAI**: Industry standard, reliable
   - **Custom**: Your own OpenAI-compatible endpoint
3. Enter your API key
4. Adjust other settings as needed

### **4. Test Functionality**
1. Open a code file in Geany
2. Select some code or place cursor
3. Go to **Tools → Copilot → Code Assistant**
4. Ask for help with your code

## 🐛 **Troubleshooting**

### **Common Issues**

#### **"GeanyPy not found" Error**
```bash
# Install GeanyPy plugin (Ubuntu/Debian)
sudo apt install geany-plugin-py

# Install GeanyPy plugin (Fedora)
sudo dnf install geany-plugins-geanypy

# Install GeanyPy plugin (Arch)
sudo pacman -S geany-plugins
```

#### **"Permission denied" Error**
```bash
# Make script executable
chmod +x install.sh

# Or run with bash directly
bash install.sh
```

#### **"Python dependencies failed" Warning**
This is usually normal for system-provided packages like GTK. The plugin will still work.

#### **Plugin doesn't appear in Tools menu**
1. Check that GeanyPy is enabled in Plugin Manager
2. Restart Geany completely
3. Check Geany's message window for error messages
4. Verify installation location is correct

### **Log Files**
- **Installation log**: `/tmp/geany-copilot-install.log`
- **Plugin logs**: `~/.config/geany/plugins/geany-copilot-python/logs/`

### **Manual Verification**
```bash
# Check if plugin files exist
ls -la ~/.config/geany/plugins/geany-copilot-python/

# Test plugin loading
cd ~/.config/geany/plugins/geany-copilot-python/
python3 test_plugin.py
```

## 🔄 **Uninstallation**

To remove the Python plugin:

```bash
# Remove plugin directory
rm -rf ~/.config/geany/plugins/geany-copilot-python/

# Restore legacy Lua files (optional)
cp OLD/*.lua ./
```

## 📞 **Support**

- **GitHub Issues**: [https://github.com/skizap/geany-copilot/issues](https://github.com/skizap/geany-copilot/issues)
- **Documentation**: Check `geany-copilot-python/README.md` after installation
- **Legacy Version**: Lua files are preserved in `OLD/` directory

## 🎉 **Success!**

Once installed successfully, you'll have:
- ✅ AI-powered code assistance with multi-turn conversations
- ✅ Intelligent copywriting and text improvement
- ✅ DeepSeek, OpenAI, and custom API support
- ✅ Modern GTK-based user interface
- ✅ Comprehensive error handling and logging
- ✅ Legacy Lua files safely preserved

Enjoy your enhanced Geany IDE experience with AI agent capabilities! 🚀
