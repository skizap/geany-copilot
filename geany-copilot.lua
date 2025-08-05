--[[
Geany Copilot - Modern Lua Plugin
AI-powered code assistant and copywriter for Geany IDE

This plugin provides a Lua-based interface that can work with:
1. Direct API calls to AI services (DeepSeek, OpenAI, etc.)
2. Python backend service for advanced features
3. Standalone operation without GeanyPy dependency

Author: Geany Copilot Team
Version: 2.0.0
License: MIT
]]

-- Try to load JSON library (prefer cjson if available, fallback to lunajson)
local json
local json_available = false

local function try_load_json()
    -- Try cjson first (commonly available on Linux systems)
    local success, json_module = pcall(require, "cjson")
    if success then
        json = json_module
        json_available = true
        return true
    end

    -- Fallback to lunajson
    success, json_module = pcall(require, "lunajson")
    if success then
        json = json_module
        json_available = true
        return true
    end

    return false
end

json_available = try_load_json()

-- Try to load HTTP libraries (may not be available on all systems)
local http_available = false
local ssl_available = false
local http, ltn12, https

local function try_load_http()
    local success1, http_module = pcall(require, "socket.http")
    local success2, ltn12_module = pcall(require, "ltn12")

    if success1 and success2 then
        http = http_module
        ltn12 = ltn12_module
        http_available = true

        -- Try to load SSL support
        local success3, https_module = pcall(require, "ssl.https")
        if success3 then
            https = https_module
            ssl_available = true
        end

        return true
    end
    return false
end

http_available = try_load_http()

-- Plugin configuration
local PLUGIN_NAME = "Geany Copilot"
local PLUGIN_VERSION = "2.0.0"
local CONFIG_DIR = geany.appinfo().configdir .. geany.dirsep .. "geany-copilot"
local CONFIG_FILE = CONFIG_DIR .. geany.dirsep .. "config.json"

-- Default configuration
local DEFAULT_CONFIG = {
    ["api-provider"] = "deepseek",
    ["deepseek-api-key"] = "",
    ["deepseek-base-url"] = "https://api.deepseek.com/v1",
    ["openai-api-key"] = "",
    ["openai-base-url"] = "https://api.openai.com/v1",
    ["custom-base-url"] = "http://localhost:11434/v1",
    ["custom-api-key"] = "",
    ["python-service-url"] = "http://localhost:8765",
    ["use-python-service"] = false,
    ["model"] = "deepseek-coder",
    ["max-tokens"] = 2048,
    ["temperature"] = 0.1,
    ["system-prompt"] = [[You are Geany Copilot, an AI programming assistant integrated into the Geany IDE.

Your role is to provide intelligent code assistance, including:
- Code completion and suggestions
- Code explanation and documentation
- Bug detection and fixes
- Code refactoring suggestions
- Best practices recommendations

Always provide practical, actionable responses that help improve code quality and developer productivity.

When providing code, preserve the original indentation and formatting style. Be concise but thorough in explanations.]],
    ["copywriter-prompt"] = [[You are an AI copywriting assistant integrated into the Geany IDE.

Your role is to help improve text content, including:
- Grammar and spelling corrections
- Style and tone improvements
- Clarity and readability enhancements
- Professional writing suggestions
- Documentation improvements

Maintain the original intent and meaning while enhancing quality and readability.]]
}

-- Global configuration
local config = {}

-- Utility functions
local function ensure_directory(path)
    local cmd = "mkdir -p '" .. path .. "'"
    os.execute(cmd)
end

local function file_exists(path)
    local file = io.open(path, "r")
    if file then
        file:close()
        return true
    end
    return false
end

local function check_dependencies()
    if not json_available then
        geany.message("Geany Copilot Error: JSON library not available. Please install lua-cjson or lunajson.")
        return false
    end
    return true
end

local function check_ssl_support(url)
    if url:match("^https://") and not ssl_available then
        geany.message("Error: HTTPS URLs require SSL support. Please install lua-sec package:\nsudo apt install lua-sec\n\nOr use HTTP URLs for testing.")
        return false
    end
    return true
end

local function load_config()
    ensure_directory(CONFIG_DIR)

    if not json_available then
        geany.message("Warning: JSON library not available. Using default configuration.")
        return DEFAULT_CONFIG
    end

    if file_exists(CONFIG_FILE) then
        local file = io.open(CONFIG_FILE, "r")
        if file then
            local content = file:read("*a")
            file:close()
            local success, parsed = pcall(json.decode, content)
            if success and parsed then
                -- Merge with defaults
                for key, value in pairs(DEFAULT_CONFIG) do
                    if parsed[key] == nil then
                        parsed[key] = value
                    end
                end
                return parsed
            end
        end
    end

    -- Return defaults and save them
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG
end

local function save_config(new_config)
    if not json_available then
        geany.message("Warning: JSON library not available. Cannot save configuration.")
        return false
    end

    ensure_directory(CONFIG_DIR)
    local file = io.open(CONFIG_FILE, "w")
    if file then
        local success, encoded = pcall(json.encode, new_config)
        if success then
            file:write(encoded)
            file:close()
            return true
        end
        file:close()
    end
    return false
end

local function get_current_selection()
    local doc = geany.document()
    if not doc then return nil end
    
    local selection = geany.selection()
    if selection and selection ~= "" then
        return selection
    end
    
    -- If no selection, get current line
    local line_num = geany.caret().line
    local line_text = doc:get_line(line_num)
    return line_text
end

local function get_file_context()
    local doc = geany.document()
    if not doc then return "" end
    
    local filename = doc.file_name or "untitled"
    local filetype = doc.file_type and doc.file_type.name or "unknown"
    local content = doc:get_text()
    
    return {
        filename = filename,
        filetype = filetype,
        content = content,
        selection = get_current_selection()
    }
end

local function make_python_service_request(prompt, is_copywriter)
    if not http_available then
        geany.message("Error: HTTP libraries not available for Python service")
        return nil
    end

    local context = get_file_context()
    local endpoint = is_copywriter and "/api/copywriter" or "/api/code-assist"
    local url = config["python-service-url"] .. endpoint

    local request_body
    if is_copywriter then
        request_body = {
            text = context.selection or "",
            prompt = prompt
        }
    else
        request_body = {
            prompt = prompt,
            code = context.selection or "",
            filename = context.filename or "",
            filetype = context.filetype or ""
        }
    end

    local request_json = json.encode(request_body)
    local response_body = {}

    local result, status = http.request{
        url = url,
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json",
            ["Content-Length"] = tostring(#request_json)
        },
        source = ltn12.source.string(request_json),
        sink = ltn12.sink.table(response_body)
    }

    if status == 200 then
        local response_text = table.concat(response_body)
        local success, response_data = pcall(json.decode, response_text)
        if success and response_data and response_data.response then
            return response_data.response
        end
    end

    geany.message("Error: Python service request failed (status: " .. tostring(status) .. ")")
    return nil
end

local function make_direct_api_request(prompt, is_copywriter)
    if not http_available then
        geany.message("Error: HTTP libraries not available. Please install lua-socket or use Python service.")
        return nil
    end

    if not json_available then
        geany.message("Error: JSON library not available. Please install lua-cjson or lunajson.")
        return nil
    end

    local provider = config["api-provider"]
    local base_url, api_key, model

    if provider == "deepseek" then
        base_url = config["deepseek-base-url"]
        api_key = config["deepseek-api-key"]
        model = config["model"]
    elseif provider == "openai" then
        base_url = config["openai-base-url"]
        api_key = config["openai-api-key"]
        model = "gpt-4"
    else
        base_url = config["custom-base-url"]
        api_key = config["custom-api-key"]
        model = config["model"]
    end

    if not api_key or api_key == "" then
        geany.message("Error: API key not configured for " .. provider)
        return nil
    end

    local system_prompt = is_copywriter and config["copywriter-prompt"] or config["system-prompt"]
    local context = get_file_context()

    local full_prompt = prompt
    if context.selection and context.selection ~= "" then
        full_prompt = "Context: " .. context.filetype .. " file\n\nSelected code:\n" .. context.selection .. "\n\nRequest: " .. prompt
    end

    local request_body = {
        model = model,
        messages = {
            {role = "system", content = system_prompt},
            {role = "user", content = full_prompt}
        },
        max_tokens = config["max-tokens"],
        temperature = config["temperature"]
    }

    local request_json = json.encode(request_body)
    local response_body = {}

    local api_url = base_url .. "/chat/completions"
    if not check_ssl_support(api_url) then
        return nil
    end

    local result, status = http.request{
        url = api_url,
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json",
            ["Authorization"] = "Bearer " .. api_key,
            ["Content-Length"] = tostring(#request_json)
        },
        source = ltn12.source.string(request_json),
        sink = ltn12.sink.table(response_body)
    }

    if status == 200 then
        local response_text = table.concat(response_body)
        local success, response_data = pcall(json.decode, response_text)
        if success and response_data and response_data.choices and response_data.choices[1] then
            return response_data.choices[1].message.content
        end
    end

    geany.message("Error: API request failed (status: " .. tostring(status) .. ")")
    return nil
end

local function make_api_request(prompt, is_copywriter)
    if config["use-python-service"] then
        return make_python_service_request(prompt, is_copywriter)
    else
        return make_direct_api_request(prompt, is_copywriter)
    end
end

local function show_response_dialog(title, response)
    if not response then return end
    
    -- Create a simple dialog to show the response
    local dialog_content = string.format([[
%s

Response:
%s

Would you like to replace the selected text with this response?
]], title, response)
    
    local result = geany.confirm(dialog_content, "Yes", "No")
    if result then
        local doc = geany.document()
        if doc then
            local selection = geany.selection()
            if selection and selection ~= "" then
                doc:replace_selection(response)
            else
                doc:insert_text(geany.caret().pos, response)
            end
        end
    end
end

-- Main plugin functions
local function code_assistant()
    local selection = get_current_selection()
    if not selection or selection == "" then
        geany.message("Please select some code or place cursor on a line for code assistance.")
        return
    end
    
    local prompt = geany.input("Code Assistant", "What would you like help with?", "Explain this code")
    if not prompt then return end
    
    geany.message("Requesting code assistance...")
    local response = make_api_request(prompt, false)
    show_response_dialog("Code Assistant", response)
end

local function copywriter_assistant()
    local selection = get_current_selection()
    if not selection or selection == "" then
        geany.message("Please select some text for copywriting assistance.")
        return
    end
    
    local prompt = geany.input("Copywriter Assistant", "How would you like to improve this text?", "Improve grammar and clarity")
    if not prompt then return end
    
    geany.message("Requesting copywriting assistance...")
    local response = make_api_request(prompt, true)
    show_response_dialog("Copywriter Assistant", response)
end

local function show_settings()
    -- Simple settings dialog using input dialogs
    local new_config = {}
    for key, value in pairs(config) do
        new_config[key] = value
    end

    -- Service Mode
    local use_service = geany.input("Settings: Use Python Service", "Use Python service? (true/false):", tostring(new_config["use-python-service"]))
    if use_service then
        new_config["use-python-service"] = (use_service:lower() == "true")
    end

    if new_config["use-python-service"] then
        -- Python Service URL
        local service_url = geany.input("Settings: Python Service URL", "Enter Python service URL:", new_config["python-service-url"])
        if service_url then new_config["python-service-url"] = service_url end
    else
        -- API Provider
        local provider = geany.input("Settings: API Provider", "Enter API provider (deepseek/openai/custom):", new_config["api-provider"])
        if provider then new_config["api-provider"] = provider end

        -- API Key based on provider
        if new_config["api-provider"] == "deepseek" then
            local key = geany.input("Settings: DeepSeek API Key", "Enter DeepSeek API key:", new_config["deepseek-api-key"])
            if key then new_config["deepseek-api-key"] = key end
        elseif new_config["api-provider"] == "openai" then
            local key = geany.input("Settings: OpenAI API Key", "Enter OpenAI API key:", new_config["openai-api-key"])
            if key then new_config["openai-api-key"] = key end
        else
            local key = geany.input("Settings: Custom API Key", "Enter custom API key:", new_config["custom-api-key"])
            if key then new_config["custom-api-key"] = key end
            local url = geany.input("Settings: Custom Base URL", "Enter custom base URL:", new_config["custom-base-url"])
            if url then new_config["custom-base-url"] = url end
        end
    end

    -- Save configuration
    if save_config(new_config) then
        config = new_config
        geany.message("Settings saved successfully!")
    else
        geany.message("Error: Failed to save settings.")
    end
end

-- Initialize plugin
config = load_config()

-- Register menu items
geany.menu("AI Code Assistant", code_assistant)
geany.menu("AI Copywriter", copywriter_assistant)
geany.menu("Copilot Settings", show_settings)

geany.message(PLUGIN_NAME .. " v" .. PLUGIN_VERSION .. " loaded successfully!")
