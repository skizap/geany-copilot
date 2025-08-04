# Geany Copilot Python Plugin

An AI-powered assistant plugin for Geany IDE that provides intelligent code assistance and copywriting features using advanced language models. This plugin replaces the original Lua-based implementation with enhanced agent capabilities, multi-turn conversations, and support for DeepSeek and other OpenAI-compatible APIs.

## Features

### 🤖 AI Code Assistant
- **Intelligent Code Analysis**: Context-aware code understanding and suggestions
- **Multi-turn Conversations**: Engage in detailed discussions about your code
- **Code Completion**: Smart code completion based on context
- **Code Explanation**: Get detailed explanations of complex code sections
- **Refactoring Suggestions**: Receive recommendations for code improvements
- **Bug Detection**: Identify potential issues and get fixing suggestions
- **Documentation Generation**: Auto-generate comments and documentation

### ✍️ AI Copywriter
- **Text Improvement**: Enhance writing quality and clarity
- **Proofreading**: Detect and fix grammar, spelling, and style issues
- **Rewriting**: Rephrase content for better readability
- **Tone Adjustment**: Adapt writing style for different audiences
- **Iterative Refinement**: Continuously improve text through conversation
- **Multi-format Support**: Works with code comments, documentation, and plain text

### 🔧 Advanced Features
- **Context Awareness**: Understands your current file, selection, and cursor position
- **Streaming Responses**: Real-time response generation for better user experience
- **Conversation History**: Maintains context across multiple interactions
- **Configurable Providers**: Support for DeepSeek, OpenAI, and custom API endpoints
- **Flexible Configuration**: JSON-based settings with easy customization
- **Error Handling**: Robust error handling with graceful degradation

## Installation

### Prerequisites

1. **Geany IDE** with GeanyPy plugin enabled
2. **Python 3.6+** with the following system packages:
   - GTK+ 3.x or 2.x (depending on your Geany version)
   - PyGTK or PyGObject (for UI components)
3. **Python packages** (install via pip):
   ```bash
   pip install requests
   ```

### Installation Steps

1. **Clone or download** this plugin to your Geany plugins directory:
   ```bash
   # Standard user plugin directory (recommended):
   cd ~/.config/geany/plugins/
   git clone https://github.com/skizap/geany-copilot.git
   cd geany-copilot/geany-copilot-python/

   # Or use the automated installer:
   python3 install.py
   ```

2. **Install Python dependencies**:
   ```bash
   cd geany-copilot-python
   pip install -r requirements.txt
   ```

3. **Enable GeanyPy** in Geany:
   - Go to `Tools` → `Plugin Manager`
   - Check the box next to "GeanyPy"
   - Click "OK"

4. **Restart Geany** to load the plugin

5. **Configure the plugin**:
   - Go to `Tools` → `Copilot Settings`
   - Enter your API key for your preferred provider
   - Adjust settings as needed

## Configuration

### API Providers

The plugin supports multiple AI providers:

#### DeepSeek (Recommended)
- **Base URL**: `https://api.deepseek.com`
- **Models**: `deepseek-chat`, `deepseek-reasoner`
- **API Key**: Get from [DeepSeek Platform](https://platform.deepseek.com/)

#### OpenAI
- **Base URL**: `https://api.openai.com/v1`
- **Models**: `gpt-4`, `gpt-3.5-turbo`, etc.
- **API Key**: Get from [OpenAI Platform](https://platform.openai.com/)

#### Custom Provider
- Configure any OpenAI-compatible API endpoint
- Set custom base URL, model names, and API key

### Configuration File

Settings are stored in JSON format at:
```
~/.config/geany/plugins/geany-copilot-python/config.json
```

Example configuration:
```json
{
  "api": {
    "primary_provider": "deepseek",
    "deepseek": {
      "api_key": "your-deepseek-api-key",
      "base_url": "https://api.deepseek.com",
      "model": "deepseek-chat"
    }
  },
  "agents": {
    "code_assistant": {
      "enabled": true,
      "max_context_lines": 100,
      "include_imports": true
    },
    "copywriter": {
      "enabled": true,
      "max_iterations": 5
    }
  },
  "ui": {
    "dialog_width": 900,
    "dialog_height": 700
  }
}
```

## Usage

### Code Assistant

1. **Open a code file** in Geany
2. **Position your cursor** or **select code** you want help with
3. **Access the assistant**:
   - Menu: `Tools` → `AI Code Assistant`
   - Or type `.gc conf` and select it, then use the menu to configure
4. **Ask questions** like:
   - "Explain this function"
   - "How can I optimize this code?"
   - "Find bugs in this implementation"
   - "Add error handling to this code"
   - "Generate documentation for this class"

### Copywriter

1. **Select text** you want to improve (code comments, documentation, etc.)
2. **Access the copywriter**:
   - Menu: `Tools` → `AI Copywriter`
3. **Choose an action**:
   - **Improve Text**: General enhancement
   - **Proofread**: Fix grammar and spelling
   - **Rewrite**: Rephrase for clarity
4. **Review and apply** the suggestions

### Special Commands

- **Configuration Trigger**: Select `.gc conf` and use either menu item to open settings
- **Context Analysis**: The assistant automatically analyzes your current file context
- **Multi-turn Conversations**: Continue asking follow-up questions in the same session

## Architecture

### Core Components

- **ConfigManager**: Handles all configuration and settings
- **APIClient**: Manages communication with AI providers
- **ContextAnalyzer**: Extracts and analyzes code/text context
- **AIAgent**: Core conversation and response handling

### Specialized Agents

- **CodeAssistant**: Specialized for programming tasks
- **CopywriterAssistant**: Specialized for text improvement

### UI Components

- **CodeAssistantDialog**: Interactive code assistance interface
- **CopywriterDialog**: Text improvement interface
- **SettingsDialog**: Configuration management

## Development

### Project Structure

```
geany-copilot-python/
├── __init__.py              # Main plugin entry point
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── api_client.py       # API communication
│   ├── context.py          # Context analysis
│   └── agent.py            # Core AI agent
├── agents/                 # Specialized agents
│   ├── __init__.py
│   ├── code_assistant.py   # Code assistance agent
│   └── copywriter.py       # Copywriting agent
├── ui/                     # User interface
│   ├── __init__.py
│   └── dialogs.py          # GTK dialogs
└── utils/                  # Utilities
    ├── __init__.py
    ├── logging_setup.py    # Logging configuration
    └── helpers.py          # Helper functions
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Testing

```bash
# Run the plugin outside of Geany for basic testing
cd geany-copilot-python
python -c "import __init__; print('Plugin loaded successfully')"
```

## Troubleshooting

### Common Issues

1. **Plugin not loading**:
   - Ensure GeanyPy is enabled
   - Check Python path and dependencies
   - Look at Geany's debug output

2. **UI not working**:
   - Verify GTK/PyGTK installation
   - Check for import errors in logs

3. **API errors**:
   - Verify API key configuration
   - Check internet connection
   - Review API provider status

4. **Context not detected**:
   - Ensure you have a document open
   - Try selecting text explicitly
   - Check file type support

### Logging

Logs are written to:
```
~/.config/geany/plugins/geany-copilot-python/logs/geany-copilot-python.log
```

Enable debug logging by modifying the plugin initialization:
```python
logger = setup_plugin_logging(debug=True)
```

## License

MIT License - see LICENSE file for details.

## References

- **Geany Plugin Development**: [Official Hacking Guide](https://geany.org/manual/hacking.html)
- **Geany Plugin API**: [API Documentation](https://www.geany.org/manual/reference/)
- **GeanyPy**: Python plugin system for Geany IDE
- **Your Repository**: [https://github.com/skizap/geany-copilot](https://github.com/skizap/geany-copilot)

## Acknowledgments

- Original Geany Copilot Lua implementation
- Geany IDE and GeanyPy plugin system
- DeepSeek and OpenAI for AI capabilities
- GTK+ for UI framework
- https://github.com/DevElCuy/geany-copilot