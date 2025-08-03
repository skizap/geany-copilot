# 🔧 GeanyPy Troubleshooting Summary for Linux Mint

## 🎯 **Your Specific Situation**

**System**: Linux Mint  
**Geany Version**: 2.1.0 GTK+ v3.24.41 and GLib v2.80.0  
**Issue**: GeanyPy plugin not appearing in Geany's Plugin Manager  
**Required For**: Geany Copilot Python plugin to work  

## 🚀 **Quick Fix (Most Likely Solution)**

### **Step 1: Install GeanyPy Package**
```bash
# Update package list first
sudo apt update

# Try the most common package name for Linux Mint
sudo apt install geany-plugin-py

# If that fails, try the broader package
sudo apt install geany-plugins
```

### **Step 2: Install Python GTK Dependencies**
```bash
# These are often missing and cause GeanyPy to not load
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

### **Step 3: Restart Geany Completely**
```bash
# Kill any running Geany processes
killall geany

# Start Geany fresh
geany
```

### **Step 4: Enable GeanyPy**
1. In Geany: **Tools → Plugin Manager**
2. Look for **"GeanyPy"** in the list
3. **Check the checkbox** next to it
4. Click **OK**

## 🔍 **Automated Troubleshooting**

We've created a comprehensive troubleshooting script specifically for your situation:

```bash
# Run the automated troubleshooter
./troubleshoot_geanypy.sh
```

**This script will:**
- ✅ Detect your exact Linux Mint version
- ✅ Check if GeanyPy packages are installed
- ✅ Automatically install missing packages
- ✅ Verify Python GTK bindings work
- ✅ Create a test plugin to verify functionality
- ✅ Provide specific error messages and fixes
- ✅ Generate a detailed report of what's working/broken

## 📋 **Manual Verification Steps**

### **Check 1: Verify GeanyPy Package Installation**
```bash
# Check if GeanyPy package is installed
dpkg -l | grep geany-plugin

# Expected output should include something like:
# ii  geany-plugin-py  1.38-1  amd64  Python bindings for Geany
```

### **Check 2: Look for GeanyPy Files**
```bash
# Find GeanyPy plugin files
find /usr -name "*geanypy*" 2>/dev/null
find /usr -name "*py.so" 2>/dev/null

# Should find files like:
# /usr/lib/x86_64-linux-gnu/geany/geanypy.so
```

### **Check 3: Test Python GTK Bindings**
```bash
# This should run without errors
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK bindings work!')"
```

### **Check 4: Verify Geany Plugin Directories**
```bash
# Check system plugin directory
ls -la /usr/lib/x86_64-linux-gnu/geany/

# Check user plugin directory
ls -la ~/.config/geany/plugins/
```

## 🐛 **Common Issues and Solutions**

### **Issue 1: "GeanyPy not in Plugin Manager"**

**Cause**: GeanyPy package not installed or wrong package name

**Solution**:
```bash
# Try different package names
sudo apt install geany-plugin-py
sudo apt install geany-plugins-py  
sudo apt install geany-plugins
```

### **Issue 2: "GeanyPy installed but not loading"**

**Cause**: Missing Python GTK dependencies

**Solution**:
```bash
# Install missing Python libraries
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0

# Test if they work
python3 -c "from gi.repository import Gtk"
```

### **Issue 3: "Permission denied" or "Cannot load plugin"**

**Cause**: File permissions or plugin directory issues

**Solution**:
```bash
# Fix plugin directory permissions
chmod 755 ~/.config/geany/plugins/
chmod -R 644 ~/.config/geany/plugins/*

# Create user plugin directory if missing
mkdir -p ~/.config/geany/plugins/
```

### **Issue 4: "Python initialization failed"**

**Cause**: Python version incompatibility or missing Python development files

**Solution**:
```bash
# Install Python development files
sudo apt install python3-dev python3-gi-dev

# Check Python version (should be 3.6+)
python3 --version
```

## 🔄 **Alternative Installation Methods**

### **Method 1: Install All Geany Plugins**
```bash
# This installs ALL Geany plugins including GeanyPy
sudo apt install geany-plugins
```

### **Method 2: Build from Source** (Advanced)
```bash
# Install build dependencies
sudo apt install build-essential python3-dev libgtk-3-dev geany-dev

# Clone and build GeanyPy
git clone https://github.com/geany/geany-plugins.git
cd geany-plugins
./autogen.sh
./configure --enable-geanypy
make
sudo make install
```

### **Method 3: Use Flatpak Geany**
```bash
# Flatpak version often includes GeanyPy by default
flatpak install flathub org.geany.Geany
```

## 🧪 **Test GeanyPy Installation**

### **Create a Simple Test Plugin**
```bash
# Create test plugin directory
mkdir -p ~/.config/geany/plugins/geanypy-test/

# Create test plugin file
cat > ~/.config/geany/plugins/geanypy-test/__init__.py << 'EOF'
import geany

def plugin_init():
    geany.main_widgets.statusbar.push(0, "GeanyPy is working!")
    return True

def plugin_cleanup():
    pass
EOF

# Restart Geany and look for "GeanyPy is working!" in status bar
```

## 📞 **Getting Help**

### **If Nothing Works**
1. **Run our troubleshooting script**: `./troubleshoot_geanypy.sh`
2. **Check detailed guide**: [GEANYPY_INSTALLATION.md](GEANYPY_INSTALLATION.md)
3. **Use Lua version as fallback**: Files in `OLD/` directory
4. **Report issue** with these details:
   - Output of `lsb_release -a`
   - Output of `geany --version`
   - Output of `dpkg -l | grep geany`
   - Any error messages from Geany's Message Window

### **Fallback Option: Use Lua Version**
If GeanyPy cannot be installed, you can use the legacy Lua version:
```bash
# Restore Lua files
cp OLD/*.lua ./

# The Lua version works without GeanyPy but has fewer features
```

## ✅ **Success Indicators**

You'll know GeanyPy is working when:
- ✅ **GeanyPy appears** in Tools → Plugin Manager
- ✅ **GeanyPy checkbox** can be enabled without errors
- ✅ **No error messages** in View → Show Message Window
- ✅ **Test plugin works** (shows message in status bar)
- ✅ **Python plugin directory** is created: `~/.config/geany/plugins/`

## 🎉 **Next Steps After GeanyPy Works**

Once GeanyPy is working:
1. **Install Geany Copilot**: `./install.sh`
2. **Configure API settings**: Tools → Copilot → Settings
3. **Test functionality**: Tools → Copilot → Code Assistant
4. **Enjoy enhanced Geany** with AI agent capabilities!

---

**💡 Pro Tip**: The automated troubleshooting script (`./troubleshoot_geanypy.sh`) is your best bet for a quick resolution. It handles most common issues automatically and provides detailed diagnostics.
