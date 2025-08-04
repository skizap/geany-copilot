# Geany Copilot Python Plugin — Documentation

Author: Cline (AI model: Anthropic Claude, created by Anthropic)

Version: 1.0.0  
License: MIT

---

## Overview

Geany Copilot is a Python-based plugin for the Geany IDE that brings AI-assisted coding and writing directly into your editor. It integrates with OpenAI-compatible APIs (including DeepSeek and custom providers) to provide context-aware code assistance and creative copywriting support. The plugin is built on a modular architecture with an agent core, API client, configuration management, and GTK-based dialogs.

This document explains how the plugin works end-to-end: initialization, configuration, UI flow, agent interactions, API calls, error handling, and cleanup.

---

## Architecture

Top-level components:

- Plugin Entrypoint
  - geany-copilot-python/plugin.py
  - geany-copilot-python/__init__.py (GeanyCopilotPlugin)
- Core
  - core/agent.py (AIAgent, conversation management)
  - core/api_client.py (API requests/streaming to providers)
  - core/config.py (JSON configuration, prompts)
  - core/context.py (context extraction/formatting) [inferred]
  - core/language_detector.py (language detection) [inferred]
  - core/cache.py (caching and performance) [inferred]
- Agents
  - agents/code_assistant.py
  - agents/copywriter.py
- UI
  - ui/dialogs.py (GTK dialogs for settings/assistants) [inferred]
- Utilities
  - utils/logging_setup.py (logger initialization)
  - utils/helpers.py (selection helpers, etc.) [inferred]

---

## Initialization and Lifecycle

1) Load and Register
- Geany loads geany-copilot-python/plugin.py via GeanyPy.
- plugin.py imports GeanyCopilotPlugin from __init__.py and sets plugin metadata.
- GeanyCopilotPlugin is instantiated on startup (when GeanyPy is active).

2) Plugin Setup
- Logging is initialized via utils.logging_setup.setup_plugin_logging.
- ConfigManager loads the configuration from:
  ~/.config/geany/plugins/geanylua/geany-copilot-python/config.json
  and ensures a prompts directory exists for system prompts.
- AIAgent is constructed with the ConfigManager and initializes:
  - APIClient (network access)
  - ContextAnalyzer (context extraction)
  - PerformanceManager (caching/perf, via core/cache.py)

3) UI Wiring
- GTK menu items are created and appended to Geany’s Tools menu:
  - AI Code Assistant
  - AI Copywriter
  - Copilot Settings
- Geany signals are connected (document-open/activate/save) for context awareness.

4) Activate/Deactivate/Cleanup
- activate(): logs activation (Geany may auto-activate after initialization).
- deactivate(): logs deactivation signal.
- cleanup(): destroys menu items and dialogs, and calls ai_agent.cleanup() to release resources.

---

## Configuration

Handled by core/config.py (ConfigManager):

- Default Config
  - api: primary_provider, provider configs (deepseek/openai/custom), models, tokens, temperature
  - agents: code_assistant and copywriter feature toggles and limits
  - ui: dialog sizes, font, welcome dialog
  - performance: cache size/TTL, debounce, memory thresholds
  - prompts: code_assistant and copywriter (loaded from prompts/*.txt)

- Files/Directories
  - Config file: ~/.config/geany/plugins/geanylua/geany-copilot-python/config.json
  - Prompts: ~/.config/geany/plugins/geanylua/geany-copilot-python/prompts/
    - code_assistant.txt
    - copywriter.txt

- Get/Set Methods
  - get(key_path, default)
  - set(key_path, value)
  - get_api_config(provider)
  - get_agent_config(agent_type)
  - get_prompt(prompt_type)
  - update_prompt(prompt_type, content)
  - save_config()

Notes:
- API keys are stored in plaintext JSON by default. Consider using environment variables or OS keyring.
- Ensure config directory and file permissions are restrictive (700/600).

---

## User Interface

Menu actions:

1) Copilot Settings
- Opens a GTK dialog to configure API providers, keys, models, and behavior.
- System prompts can be edited and saved to prompt files.

2) AI Code Assistant
- Opens a dialog that uses the CodeAssistant agent.
- Can operate with or without a selection; the agent will gather context from the current document if needed.
- Displays responses, with options to insert or replace text (depending on UI implementation).

3) AI Copywriter
- Requires a text selection. If none is selected, an error dialog is shown.
- Opens a dialog connected to the Copywriter agent, prefilled with the selected text.
- Presents suggestions for rewriting, improving, or generating content.

Dialogs are created lazily and reused while the plugin runs. Errors are shown via Geany’s message box when Geany is present, or printed to stdout when testing outside of Geany.

---

## Agent Flow

AIAgent (core/agent.py) handles state and multi-turn conversations:

- Conversation model:
  - Conversation with multiple ConversationTurn entries
  - State: IDLE, THINKING, RESPONDING, WAITING_FOR_INPUT, COMPLETED, ERROR
  - Context is collected and formatted via ContextAnalyzer
- Workflow:
  1. start_conversation(agent_type, initial_context) -> conversation_id
  2. continue_conversation(conversation_id, user_message, updated_context=None, stream=False)
     - Builds messages (system + context + prior turns + new user input)
     - Calls APIClient for either streaming or single response
     - Appends response turn to the conversation
  3. get_conversation(), get_conversation_summary(), export_conversation()
  4. cleanup(), clear_conversations(), end_conversation()

Callbacks:
- on_thinking_start/on_thinking_end: UI can indicate busy state.
- on_response_chunk: stream partial outputs to UI as they arrive.
- on_error: UI can display errors.

---

## API Client and Networking

APIClient (core/api_client.py) sends OpenAI-compatible chat requests to configured providers.

Key methods:
- chat_completion(messages, provider=None, **kwargs) -> APIResponse
  - POST /v1/chat/completions (or constructed endpoint)
  - Returns first choice content, usage, model
- chat_completion_stream(messages, provider=None, **kwargs) -> Iterator[APIResponse]
  - POST with stream=True and iterates SSE-like lines, yielding chunks as APIResponse(success=True, content=...)
- test_connection(provider=None) -> APIResponse
  - Sends a small request to verify connectivity and credentials

Data classes:
- ChatMessage: {role, content}
- APIResponse: {success, content, error, usage, model, reasoning}

Provider configuration:
- base_url, api_key, model, temperature, max_tokens from config.
- Automatic construction of /v1/chat/completions if needed.

Security and reliability notes:
- Provide per-request timeouts to avoid hangs.
- Never log API keys; redact payloads in logs.
- Prefer HTTPS for remote providers.

---

## Context and Language Detection

ContextAnalyzer and LanguageDetector (inferred from imports):

- ContextAnalyzer builds an AI-friendly context from:
  - current selection
  - nearby lines or entire file snips bounded by config.agents.code_assistant.context_length
  - language metadata from LanguageDetector
- Formatting guidelines are embedded in the default code assistant prompt.
- LanguageDetector helps tailor prompts for the detected filetype.

---

## Copywriter vs. Code Assistant

- Code Assistant
  - Analyzes code context
  - Generates improvements, completions, explanations
  - Multi-turn conversations supported
- Copywriter
  - Works with selected text
  - Rewrites, improves clarity/grammar/style
  - Can perform iterative improvements

Both agents use the same AIAgent core and APIClient. Prompts differ and are independently configurable.

---

## Error Handling

- plugin.py wraps activate/deactivate/cleanup calls with try/except to avoid crashing Geany.
- __init__.py methods catch exceptions in UI creation and signal registration, logging errors and showing dialogs as needed.
- api_client.py catches RequestException and generic exceptions, returning APIResponse with error details.
- AIAgent transitions conversation state to ERROR and surfaces errors via on_error callback.

---

## Cleanup and Resource Management

- UI: Menu items and dialogs are destroyed in GeanyCopilotPlugin.cleanup().
- Agent: ai_agent.cleanup() clears conversations and closes API sessions.
- APIClient: session is closed in cleanup().

Recommended improvements (already analyzed):
- Ensure only a single cleanup implementation in AIAgent and enforce conversation trimming by updated_at/time.
- Disconnect any Geany signals explicitly on cleanup if GeanyPy requires handler IDs.
- Apply cache TTLs and limits in PerformanceManager.

---

## Security Considerations

- API Keys
  - Stored in config.json by default; ensure file permissions are strict (600).
  - Environment variable overrides are recommended where possible.
  - Logs must never contain API keys.

- Prompt Injection Mitigation
  - Treat user/file context as user content, not as system role.
  - Limit context length and sanitize/escape untrusted text.
  - Prefer fenced code blocks when embedding raw code into prompts.

- Network
  - Use HTTPS whenever contacting a remote server.
  - Configure reasonable connect/read timeouts; handle retries cautiously.

- Filesystem
  - The plugin writes to ~/.config/geany/plugins/... only.
  - Prompts are plain text files. Avoid executing or interpreting their content beyond static prompts.

---

## Performance Tips

- Use the performance.cache config to bound memory/time-to-live for cached responses.
- Debounce interactions that could trigger repeated calls in rapid succession (keypress-driven flows).
- Avoid large blocking calls on the UI thread; offload API calls to a worker thread and update UI via GTK-safe callbacks.

---

## Installation and Verification

Quick install:
- ./install.sh handles dependency installation, file placement, and tests.
- Ensure GeanyPy is installed and enabled in Geany.
- Open Tools → Copilot → Settings to configure provider, key, and model.

Linux environment specifics (summarized):
- Install GeanyPy: e.g., apt install geany-plugin-py or geany-plugins
- Install Python GTK dependencies: python3-gi, python3-gi-cairo, gir1.2-gtk-3.0
- Troubleshoot with ./troubleshoot_geanypy.sh if GeanyPy isn’t detected.

---

## How to Use

1) Code Assistant
- Select relevant code or place the cursor where help is needed.
- Tools → AI Code Assistant.
- Review suggestions and insert/replace as appropriate.

2) Copywriter
- Select text to improve.
- Tools → AI Copywriter.
- Choose rewrite/improve actions, then insert/replace.

3) Settings
- Tools → Copilot Settings to set provider, API key, model, and dialog options.
- Edit prompts via the UI or by modifying the corresponding files under prompts/.

---

## Versioning and Legacy Support

- Current: Python Geany Copilot (active development)
- Legacy: Lua implementation preserved under OLD/ for reference
- Migration paths and installation scripts are provided in the repository README and INSTALL_GUIDE.

---

## Credits

- Geany IDE and GeanyPy ecosystem
- OpenAI-compatible providers (e.g., DeepSeek, OpenAI, custom local servers)
- Author of this document: Cline (AI model: Anthropic Claude, created by Anthropic)
