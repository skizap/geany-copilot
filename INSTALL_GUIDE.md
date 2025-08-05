# 🚀 Geany Copilot - Installation Guide

This guide provides comprehensive instructions for installing the Geany Copilot plugin. Due to GeanyPy compatibility issues with modern Linux distributions, we now offer both Lua and Python-based solutions.

## ⚠️ **Important Notice: GeanyPy Compatibility Issue**

**GeanyPy is not available in modern Linux distributions** (Ubuntu 24.04+, Linux Mint 22+) and is incompatible with Python 3 and modern GTK. This affects the Python plugin version.

**Available Solutions:**
- **🔥 Lua Plugin (Recommended)**: Works immediately with GeanyLua (included in geany-plugins)
- **🐍 Python Backend**: Standalone Python service that can be called from Lua or external tools
- **🔧 Hybrid Approach**: Lua frontend with Python backend for best of both worlds

## 📋 **Quick Start**

### **Option 1: Lua Plugin (Recommended)**

1. **Download or clone** this repository:
   ```bash
   git clone https://github.com/skizap/geany-copilot.git
   cd geany-copilot
   ```

2. **Install GeanyLua** (if not already installed):
   ```bash
   sudo apt install geany-plugins
   ```

3. **Copy Lua files**:
   ```bash
   cp *.lua ~/.config/geany/plugins/geanylua/
   ```

4. **Enable GeanyLua** in Geany: Tools → Plugin Manager → GeanyLua

### **Option 2: Python Backend Service**

1. **Install Python dependencies**:
   ```bash
   cd geany-copilot-python
   pip3 install --user -r requirements.txt
   ```

2. **Run as standalone service**:
   ```bash
   python3 geany-copilot-python/service.py
   ```

## 🔧 **Available Solutions Explained**

### **🔥 Lua Plugin (Recommended)**
- **Works immediately** with GeanyLua (included in geany-plugins)
- **Direct API integration** with DeepSeek, OpenAI, and custom endpoints
- **No Python dependencies** required
- **Lightweight and fast** execution
- **Full feature compatibility** with original functionality

### **🐍 Python Service Backend**
- **Advanced agent capabilities** with multi-turn conversations
- **Enhanced context awareness** and code analysis
- **HTTP API** for integration with external tools
- **Standalone operation** or as backend for Lua plugin
- **Full Python ecosystem** access for advanced features

### **� Hybrid Approach**
- **Lua frontend** for immediate response and UI integration
- **Python backend** for advanced processing when needed
- **Best of both worlds** - speed and advanced capabilities
- **Fallback support** - works even if Python service is unavailable

## 🎯 **Why This Approach Works Better**

### **✅ No GeanyPy Dependency**
- GeanyPy is **not available** in modern Linux distributions
- GeanyPy requires **Python 2** and **PyGTK 2.0** (obsolete)
- Our solution uses **modern technologies** and **current standards**

### **✅ Better Performance**
- Lua plugin provides **instant response** for simple operations
- Python service handles **complex processing** efficiently
- **No plugin loading delays** or compatibility issues

### **✅ Enhanced Reliability**
- **Multiple fallback options** ensure functionality
- **Independent operation** - each component works standalone
- **Easy troubleshooting** with clear separation of concerns

## 🖥️ **System Requirements**

### **For Lua Plugin (Recommended)**
- **Geany IDE** (any recent version)
- **GeanyLua plugin** (included in geany-plugins package)
- **lua-json** library (for JSON parsing)
- **lua-socket** library (optional, for HTTP requests)

### **For Python Service (Optional)**
- **Python 3.8+** (for advanced features)
- **pip** package manager
- **Flask** and **requests** libraries (for HTTP service)

### **Installation Commands**
```bash
# Install Geany and plugins
sudo apt install geany geany-plugins

# Install Lua libraries (optional, for direct API calls)
sudo apt install lua-cjson lua-socket

# Install Python dependencies (optional, for service mode)
pip3 install --user flask flask-cors requests
```

## 📂 **Installation Locations**

### **Lua Plugin Files**
```
~/.config/geany/plugins/geanylua/geany-copilot.lua
```
- Single file installation
- Loaded automatically by GeanyLua
- User-specific, no root privileges required

### **Python Service (Optional)**
```
~/geany-copilot/geany-copilot-python/
```
- Standalone service directory
- Can run independently
- Full Python environment access

### **Configuration Files**
```
~/.config/geany/geany-copilot/config.json
```
- Shared configuration for both Lua and Python components
- JSON format for easy editing
- Automatic creation with defaults

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
