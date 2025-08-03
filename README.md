# Geany Copilot

**Geany Copilot** is an AI-powered assistant integrated into the [Geany](https://www.geany.org/) IDE. Inspired by GitHub Copilot, it leverages advanced language models to provide context-aware code completions and creative copywriting assistance, enhancing your productivity and creativity directly within the Geany editor.

## 🚀 **Quick Start - Python Version (Recommended)**

**New Enhanced Python Implementation with Agent Capabilities!**

```bash
git clone https://github.com/skizap/geany-copilot.git
cd geany-copilot
./install.sh
```

The automated installer handles everything: dependency installation, legacy file management, and plugin setup. See [INSTALL_GUIDE.md](INSTALL_GUIDE.md) for detailed instructions.

### **✨ Python Version Features**
- 🤖 **Agent Intelligence**: Multi-turn conversations with context retention
- 🔌 **Enhanced API Support**: DeepSeek, OpenAI, and custom providers
- 🎨 **Modern UI**: GTK-based dialogs with comprehensive functionality
- 🛡️ **Robust Error Handling**: Graceful degradation and recovery
- 📊 **Comprehensive Testing**: Complete validation and logging
- 🔧 **Easy Installation**: Automated setup with one command

### **📁 Version Comparison**

| Feature | Python Version | Lua Version (Legacy) |
|---------|----------------|----------------------|
| **Agent Conversations** | ✅ Multi-turn with context | ❌ Single requests only |
| **API Support** | ✅ DeepSeek + OpenAI + Custom | ✅ OpenAI compatible |
| **User Interface** | ✅ Modern GTK dialogs | ✅ Basic dialogs |
| **Error Handling** | ✅ Comprehensive | ✅ Basic |
| **Installation** | ✅ Automated script | ⚠️ Manual setup |
| **Testing** | ✅ Full test suite | ❌ No tests |
| **Maintenance** | ✅ Active development | 🔒 Legacy support |

**💡 Recommendation**: Use the Python version for new installations. Legacy Lua files are preserved in the `OLD/` directory.

## Table of Contents

- [Quick Start - Python Version](#-quick-start---python-version-recommended)
- [Features](#features)
- [Installation](#installation)
  - [Python Version (Recommended)](#python-version-recommended)
  - [Lua Version (Legacy)](#lua-version-legacy)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Code Assistance](#code-assistance)
  - [Copywriting Assistance](#copywriting-assistance)
- [Migration Guide](#migration-guide)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

## Features

- **AI-Powered Code Completions:** Intelligent code suggestions based on your current context within the Geany editor.
- **Creative Copywriting Assistance:** Generate and refine creative content, offering constructive feedback and suggestions.
- **Customizable Settings:** Easily configure API endpoints, remote API keys, system prompts, and behavior preferences to tailor the assistant to your needs.
- **Seamless Integration:** Works directly within Geany, maintaining your workflow without the need to switch between tools.
- **Error Handling:** Provides informative error dialogs to help troubleshoot issues with API interactions.
- **Selection Replacement:** Option to replace selected text with AI-generated suggestions, streamlining the editing process.

## Installation

### **Python Version (Recommended)**

**🚀 Automated Installation:**

```bash
git clone https://github.com/skizap/geany-copilot.git
cd geany-copilot
./install.sh
```

The installation script automatically:
- ✅ Checks prerequisites (Python 3.6+, pip, Geany)
- ✅ Moves legacy Lua files to `OLD/` directory
- ✅ Installs Python dependencies
- ✅ Copies plugin files to appropriate Geany directory
- ✅ Sets proper file permissions
- ✅ Verifies installation and runs tests

**📋 Prerequisites:**
- **Geany IDE** with GeanyPy plugin support
- **Python 3.6+** (Python 3.8+ recommended)
- **pip** package manager

**📚 Detailed Instructions:** See [INSTALL_GUIDE.md](INSTALL_GUIDE.md) for comprehensive installation guide.

### **Lua Version (Legacy)**

**⚠️ Note**: The Lua version is preserved for compatibility but is no longer actively developed. New users should use the Python version.

**Prerequisites:**
- **Geany IDE** with Lua scripting support
- **Dependencies**: `lunajson` library and `cURL`

**Steps:**

1. **Restore Legacy Files** (if you want to use the Lua version):
   ```bash
   cp OLD/*.lua ./
   ```

2. **Install Dependencies:**

   Ensure that the `lunajson` library is available. You can install it using LuaRocks:

   ```bash
   luarocks install lunajson
   ```

   Additionally, ensure that `cURL` is installed on your system:

   ```bash
   # For Debian/Ubuntu
   sudo apt-get install curl

   # For macOS using Homebrew
   brew install curl
   ```

4. **Place the Plugins in Geany's Plugin Directory:**

   Copy the Lua scripts (`copilot.lua` and `copywriter.lua`) to Geany's plugin or script directory, typically located at `~/.config/geany/plugins/` or a similar path depending on your operating system.

   ```bash
   mkdir -p ~/.config/geany/plugins/geanylua/geany-copilot/
   cp copilot.lua copywriter.lua ~/.config/geany/plugins/geanylua/geany-copilot/
   ```

5. **Restart Geany:**

   After placing the plugins, restart Geany in case the lua scripts didn't load automatically.

## Configuration

Geany Copilot uses JSON settings files to manage its configurations for both code assistance and copywriting assistance. The settings include the OpenAI API base URL, API key, system prompts, and behavior preferences.

### Settings File Locations

- **Code Assistance Settings:**

  ```
  ~/.config/geany/plugins/geanylua/geany-copilot/copilot.json
  ```

- **Copywriting Assistance Settings:**

  ```
  ~/.config/geany/plugins/geanylua/geany-copilot/copywriter.json
  ```

### Setting Up
1. **(Optional): Setup shortcuts**
   Open the Keybindings section under Geany Preferences. Scroll down to "Lua Script" sub-section and set the shortcut for both "Copilot" and "Copywriter". For example: <Super>backslash and <Super>Return respectively.

2. **Open Geany Copilot Settings Dialog:**

   In Geany, you can access the settings dialog through either a plugin menu or a keyboard shortcut. The initial dialog will feature a "Settings" button. Alternatively, you can directly invoke the settings dialog by typing and selecting ".gc conf" anywhere within the editor, followed by activating the keyboard shortcut.

3. **Configure API Settings:**

   - **Base URL:** Enter your OpenAI API base URL (e.g., `https://api.openai.com`).
   - **API Key:** Enter your OpenAI API key. This key is required to authenticate requests to the API.

   Note: Any compatible OpenAI API (OAI) is supported (i.e: ollama, llama-server, etc.)

4. **Customize System Prompt:**

   - **Code Assistance:** Defines the behavior of the AI assistant for coding tasks.
   - **Copywriting Assistance:** Defines the behavior of the AI assistant for copywriting tasks.

5. **Behavior Preferences:**

   - **Replace Selection:** Choose whether the AI-generated suggestion should replace the currently selected text.

6. **Save Settings:**

   Click the **Save** button to apply your configurations.

## Usage

Once installed and configured, Geany Copilot is ready to assist you with both code completions and copywriting tasks.

### Code Assistance

**Geany Copilot** for code assistance operates similarly to GitHub Copilot, providing intelligent code suggestions based on your current context within the Geany editor.

#### Triggering Code Completions

1. **Select Code Context:**

   Highlight the code snippet you want the AI to analyze and complete. If no text is selected, Geany Copilot will automatically determine a context around the current caret position.

2. **Invoke Geany Copilot:**

   - Use a designated keyboard shortcut.
   - Access via the plugin menu.

3. **Review Suggestions:**

   Geany Copilot will display a dialog with AI-generated code completion options (usually 1). Review the suggestions, select the one that best fits your needs and click Accept.

4. **Apply Completion:**

   Upon selection, the chosen code snippet will replace the original selection.

### Copywriting Assistance

**Geany Copilot** also offers creative copywriting assistance, helping you generate and refine written content directly within the Geany editor.

#### Performing Copywriting Tasks

1. **Select Text or Position Caret:**

   - To generate new content, place the caret where you want the text to be inserted.
   - To review or refine existing text, highlight the text you wish to work on.

2. **Invoke Copywriting Assistant:**

   - Use a designated keyboard shortcut.
   - Access via the plugin menu.

3. **Choose an Action:**

   - **Generate Content:** Create new text based on the provided context.
   - **Review Text:** Get constructive feedback and suggestions for improvement.

4. **Review and Apply Suggestions:**

   The assistant will display a dialog with AI-generated suggestions. Choose the appropriate option to insert or replace text, depending on your configuration.

## Migration Guide

### **From Lua to Python Version**

If you're currently using the Lua version and want to upgrade to the Python version:

1. **Backup Your Configuration** (optional):
   ```bash
   cp ~/.config/geany/plugins/geanylua/geany-copilot-python/config.json ~/geany-copilot-backup.json
   ```

2. **Run the Installation Script**:
   ```bash
   ./install.sh
   ```
   The script automatically moves your Lua files to the `OLD/` directory and installs the Python version.

3. **Reconfigure API Settings**:
   - Go to **Tools → Copilot → Settings** in Geany
   - Enter your API key and configure preferences
   - The Python version supports additional providers like DeepSeek

4. **Test the New Features**:
   - Try the enhanced code assistant with multi-turn conversations
   - Explore the improved copywriting interface
   - Experience better error handling and logging

### **Reverting to Lua Version**

If you need to revert to the Lua version:

1. **Remove Python Plugin**:
   ```bash
   rm -rf ~/.config/geany/plugins/geany-copilot-python/
   ```

2. **Restore Lua Files**:
   ```bash
   cp OLD/*.lua ./
   ```

3. **Reconfigure Geany** to use the Lua scripts as before.

## Dependencies

### **Python Version Dependencies**
- **Python 3.6+** (automatically checked by installer)
- **pip** package manager (automatically checked)
- **requests** library (automatically installed)
- **GTK+ 3.0+** (usually system-provided)
- **GeanyPy** plugin (see [GeanyPy Installation Guide](#geanypy-installation-guide) below)

### **Lua Version Dependencies (Legacy)**

- **Lua:** Ensure that Lua is installed and properly configured with Geany.
- **lunajson:** A Lua library for JSON encoding and decoding. Install via LuaRocks:

  ```bash
  luarocks install lunajson
  ```

- **cURL:** The plugin uses `cURL` to make HTTP requests to the OpenAI API. Ensure that `cURL` is installed on your system.

  ```bash
  # For Debian/Ubuntu
  sudo apt-get install curl

  # For macOS using Homebrew
  brew install curl
  ```

## GeanyPy Installation Guide

### **For Linux Mint Users (Your System)**

Since you're using **Linux Mint with Geany 2.1.0**, here are the specific steps to install GeanyPy:

#### **Quick Installation**
```bash
# Update package list
sudo apt update

# Install GeanyPy (try these in order)
sudo apt install geany-plugin-py
# OR if the above fails:
sudo apt install geany-plugins

# Install Python GTK dependencies
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

#### **Verification Steps**
1. **Restart Geany completely**: `killall geany && geany`
2. **Open Plugin Manager**: Tools → Plugin Manager
3. **Look for GeanyPy**: Should appear in the plugin list
4. **Enable GeanyPy**: Check the checkbox and click OK
5. **Test**: Look for Python plugin support

#### **Troubleshooting Script**
If GeanyPy doesn't appear, run our troubleshooting script:
```bash
./troubleshoot_geanypy.sh
```

This script will:
- ✅ Detect your exact Linux Mint version
- ✅ Check for GeanyPy packages
- ✅ Install missing dependencies
- ✅ Test Python GTK bindings
- ✅ Create a test plugin to verify functionality
- ✅ Provide specific fixes for your system

#### **Alternative Package Names**
Different Linux distributions use different package names:

| Distribution | Package Name |
|--------------|--------------|
| **Linux Mint/Ubuntu/Debian** | `geany-plugin-py` or `geany-plugins` |
| **Fedora/CentOS** | `geany-plugins-geanypy` |
| **Arch Linux** | `geany-plugins` |
| **openSUSE** | `geany-plugin-geanypy` |

#### **Manual Verification**
Check if GeanyPy is installed:
```bash
# Check installed packages
dpkg -l | grep geany-plugin

# Look for GeanyPy files
find /usr -name "*geanypy*" 2>/dev/null
find /usr -name "*py.so" 2>/dev/null

# Test Python GTK
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK OK')"
```

#### **If GeanyPy Still Doesn't Work**
1. **Check detailed guide**: See [GEANYPY_INSTALLATION.md](GEANYPY_INSTALLATION.md)
2. **Use troubleshooting script**: `./troubleshoot_geanypy.sh`
3. **Fallback to Lua version**: Files preserved in `OLD/` directory
4. **Report issue**: Include your system details and error messages

### **Understanding GeanyPy vs Other Plugins**

**GeanyPy** is special because it's a "plugin framework" that allows Python scripts to act as Geany plugins:

- **Regular Geany plugins**: Written in C/C++, compiled as `.so` files
- **GeanyPy plugins**: Written in Python, loaded through GeanyPy framework
- **GeanyLua plugins**: Written in Lua (what we're migrating from)

**Why GeanyPy is Required:**
- Our Python plugin uses GeanyPy's API to integrate with Geany
- Without GeanyPy, Python plugins cannot access Geany's interface
- GeanyPy provides the bridge between Python and Geany's C API

## Contributing

Contributions are welcome! If you'd like to contribute to Geany Copilot, please follow these guidelines:

1. **Fork the Repository:**

   Click the **Fork** button at the top of this page to create a personal copy of the repository.

2. **Create a Feature Branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Commit Your Changes:**

   ```bash
   git commit -m "Add your detailed description of the changes"
   ```

4. **Push to Your Fork:**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request:**

   Navigate to the original repository and click **New Pull Request**. Provide a clear description of your changes and submit the pull request.

### Reporting Issues

If you encounter any issues or have suggestions for improvements, please [open an issue](https://github.com/yourusername/geany-copilot/issues) on GitHub.

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software in accordance with the terms of the license.

---

**Disclaimer:** Geany Copilot interacts with external APIs to provide code completions and copywriting assistance. Ensure that you handle your API keys securely and be aware of any costs associated with API usage.

## Acknowledgements

- Inspired by [Geany IDE](https://www.geany.org/) and [GitHub Copilot](https://github.com/features/copilot).
- Utilizes the [lunajson](https://github.com/grafi-tt/lunajson) library for JSON handling.
- Powered by OpenAI's language models.

## Contact

For any queries or support, please reach out to [DevElCuy](https://x.com/DevElCuy).

---

*Happy Coding and Writing! 🚀*
