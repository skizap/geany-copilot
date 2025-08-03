# 🐍 GeanyPy Installation Guide

This guide helps you install and configure GeanyPy, which is required for the Geany Copilot Python plugin to work.

## 🔍 **What is GeanyPy?**

**GeanyPy** is a plugin for Geany that provides Python scripting support. It allows Python plugins to integrate with Geany's interface and functionality. It's different from regular Geany plugins because:

- **Regular Geany plugins**: Written in C/C++ and compiled as shared libraries (.so files)
- **GeanyPy plugins**: Written in Python and loaded through the GeanyPy framework
- **GeanyLua plugins**: Written in Lua (legacy approach we're migrating from)

## 🖥️ **Installation by Linux Distribution**

### **Linux Mint / Ubuntu / Debian**

#### **Method 1: Package Manager (Recommended)**
```bash
# Update package list
sudo apt update

# Install GeanyPy plugin
sudo apt install geany-plugin-py

# Alternative package name on some systems
sudo apt install geany-plugins-py

# Install all Geany plugins (includes GeanyPy)
sudo apt install geany-plugins
```

#### **Method 2: Check Available Packages**
```bash
# Search for GeanyPy packages
apt search geany | grep -i py
apt search geany-plugin

# List all available Geany plugins
apt list | grep geany-plugin
```

### **Fedora / CentOS / RHEL**

```bash
# Install GeanyPy plugin
sudo dnf install geany-plugins-geanypy

# Alternative: Install all Geany plugins
sudo dnf install geany-plugins

# On older systems (CentOS 7, etc.)
sudo yum install geany-plugins-geanypy
```

### **Arch Linux / Manjaro**

```bash
# Install all Geany plugins (includes GeanyPy)
sudo pacman -S geany-plugins

# Or use AUR for specific versions
yay -S geany-plugins-git
```

### **openSUSE**

```bash
# Install GeanyPy plugin
sudo zypper install geany-plugin-geanypy

# Alternative: Install all plugins
sudo zypper install geany-plugins
```

### **Generic Linux / From Source**

If package manager installation fails:

```bash
# Install build dependencies
sudo apt install build-essential python3-dev libgtk-3-dev geany-dev

# Clone GeanyPy source
git clone https://github.com/geany/geany-plugins.git
cd geany-plugins

# Configure and build
./autogen.sh
./configure --enable-geanypy
make
sudo make install
```

## ✅ **Verification Steps**

### **Step 1: Check if GeanyPy Package is Installed**

```bash
# Ubuntu/Debian/Linux Mint
dpkg -l | grep geany-plugin
apt list --installed | grep geany

# Fedora/CentOS
rpm -qa | grep geany
dnf list installed | grep geany

# Arch Linux
pacman -Q | grep geany

# openSUSE
zypper search --installed-only geany
```

### **Step 2: Check Geany Plugin Directory**

```bash
# Check system plugin directories
ls -la /usr/lib/geany/
ls -la /usr/lib/x86_64-linux-gnu/geany/
ls -la /usr/local/lib/geany/

# Look for GeanyPy files
find /usr -name "*geanypy*" 2>/dev/null
find /usr -name "*py.so" 2>/dev/null
```

### **Step 3: Check Geany Plugin Manager**

1. **Start Geany**
2. **Go to Tools → Plugin Manager**
3. **Look for "GeanyPy"** in the list
4. **Enable it** by checking the checkbox
5. **Click OK** to apply

### **Step 4: Verify GeanyPy is Working**

```bash
# Check if GeanyPy creates its directory
ls -la ~/.config/geany/plugins/

# Look for Python plugin support
geany --help | grep -i python
```

## 🐛 **Troubleshooting Common Issues**

### **Issue 1: GeanyPy Not in Plugin Manager**

**Possible Causes:**
- GeanyPy package not installed
- Wrong package installed
- Geany version incompatibility
- Missing Python development libraries

**Solutions:**
```bash
# Reinstall with all dependencies
sudo apt install --reinstall geany-plugin-py python3-dev

# Check Geany version compatibility
geany --version
apt show geany-plugin-py

# Install missing Python libraries
sudo apt install python3-gi python3-gi-dev
```

### **Issue 2: GeanyPy Installed but Not Loading**

**Check Geany's Message Window:**
1. **View → Show Message Window**
2. **Look for error messages** about GeanyPy or Python plugins
3. **Common errors:**
   - "Could not load plugin"
   - "Python initialization failed"
   - "Missing dependencies"

**Solutions:**
```bash
# Install missing Python GTK bindings
sudo apt install python3-gi-cairo gir1.2-gtk-3.0

# Check Python path issues
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK OK')"

# Restart Geany completely
killall geany
geany
```

### **Issue 3: Wrong Geany Version**

**Check Compatibility:**
```bash
# Your Geany version
geany --version

# GeanyPy package version
apt show geany-plugin-py | grep Version
```

**Solutions:**
- Update Geany: `sudo apt update && sudo apt upgrade geany`
- Use compatible GeanyPy version
- Consider building from source for exact compatibility

### **Issue 4: Permission Issues**

```bash
# Fix plugin directory permissions
chmod 755 ~/.config/geany/plugins/
chmod -R 644 ~/.config/geany/plugins/*

# Check system plugin permissions
ls -la /usr/lib/geany/
```

## 🔧 **Alternative Installation Methods**

### **Method 1: Manual Plugin Installation**

If package manager fails, try manual installation:

```bash
# Download GeanyPy plugin manually
wget https://github.com/geany/geany-plugins/releases/latest

# Extract and install to user directory
mkdir -p ~/.local/lib/geany/
cp geanypy.so ~/.local/lib/geany/
```

### **Method 2: Flatpak Geany**

If using Flatpak Geany:

```bash
# Install Geany with plugins via Flatpak
flatpak install flathub org.geany.Geany

# GeanyPy should be included in Flatpak version
```

### **Method 3: AppImage Geany**

Some AppImage versions include GeanyPy by default.

### **Method 4: Build Custom Geany**

For advanced users:

```bash
# Build Geany with Python support
git clone https://github.com/geany/geany.git
cd geany
./autogen.sh
./configure --enable-plugins
make
sudo make install
```

## 🧪 **Testing GeanyPy Installation**

### **Create Test Python Plugin**

1. **Create test directory:**
   ```bash
   mkdir -p ~/.config/geany/plugins/test-py/
   ```

2. **Create test plugin file:**
   ```bash
   cat > ~/.config/geany/plugins/test-py/__init__.py << 'EOF'
   import geany
   
   def plugin_init():
       geany.main_widgets.statusbar.push(0, "GeanyPy is working!")
       return True
   
   def plugin_cleanup():
       pass
   EOF
   ```

3. **Restart Geany** and check if message appears in status bar

### **Verify Python Plugin Loading**

```bash
# Check Geany's message window for Python plugin messages
# Look for: "Loading Python plugin: test-py"
```

## 📋 **System-Specific Notes**

### **Linux Mint 21.x (Ubuntu 22.04 base)**
```bash
sudo apt install geany-plugin-py python3-gi python3-gi-cairo
```

### **Linux Mint 20.x (Ubuntu 20.04 base)**
```bash
sudo apt install geany-plugins python3-gi python3-gi-cairo
```

### **Older Linux Mint Versions**
May need to build from source or use PPA:
```bash
sudo add-apt-repository ppa:geany-dev/ppa
sudo apt update
sudo apt install geany geany-plugins
```

## 🎯 **Final Verification Checklist**

- [ ] **GeanyPy package installed**: `dpkg -l | grep geany-plugin`
- [ ] **GeanyPy appears in Plugin Manager**: Tools → Plugin Manager
- [ ] **GeanyPy is enabled**: Checkbox checked in Plugin Manager
- [ ] **Python GTK bindings work**: `python3 -c "from gi.repository import Gtk"`
- [ ] **Plugin directory exists**: `~/.config/geany/plugins/`
- [ ] **No errors in Message Window**: View → Show Message Window
- [ ] **Test plugin loads**: Create simple test plugin

## 🆘 **Still Having Issues?**

If GeanyPy still doesn't work after following this guide:

1. **Check Geany version compatibility**
2. **Try building from source**
3. **Consider using the Lua version** (preserved in `OLD/` directory)
4. **Report issue** with full system details:
   - Linux distribution and version
   - Geany version (`geany --version`)
   - Python version (`python3 --version`)
   - Error messages from Geany's Message Window

## 🔄 **Fallback to Lua Version**

If GeanyPy cannot be installed, you can use the legacy Lua version:

```bash
# Restore Lua files
cp OLD/*.lua ./

# Install Lua dependencies
sudo apt install lua5.3 lua-json

# Configure Geany to use Lua scripts
```

The Lua version provides basic functionality but lacks the advanced agent capabilities of the Python version.
