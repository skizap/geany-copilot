# Geany Copilot Troubleshooting Guide

## Quick Fix Summary

The main issue you encountered was a **missing `lunajson` dependency**. This has been resolved by:

1. ✅ **Updated plugin** to use `cjson` (already available on your system)
2. ✅ **Added dependency checking** with helpful error messages
3. ✅ **Created installation script** for automated setup
4. ✅ **Added SSL support detection** for HTTPS API calls

## Installation Steps

### Automated Installation (Recommended)
```bash
cd /home/robotcowboy808/Documents/geany-copilot
./install-geany-copilot.sh
```

### Manual Installation
If the automated script doesn't work:

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install geany-plugin-lua lua-cjson lua-socket lua-sec
   ```

2. **Copy plugin file:**
   ```bash
   cp geany-copilot.lua ~/.config/geany/plugins/geanylua/
   ```

3. **Create config directory:**
   ```bash
   mkdir -p ~/.config/geany/geany-copilot
   ```

4. **Restart Geany and enable GeanyLua plugin**

## Common Issues and Solutions

### 1. "module 'lunajson' not found" Error
**Status:** ✅ FIXED
- **Cause:** Plugin was trying to load `lunajson` but system has `cjson`
- **Solution:** Plugin updated to use `cjson` with fallback to `lunajson`

### 2. "JSON library not available" Error
```bash
sudo apt install lua-cjson
```

### 3. "HTTP libraries not available" Error
```bash
sudo apt install lua-socket
```

### 4. "HTTPS URLs require SSL support" Error
```bash
sudo apt install lua-sec
```

### 5. GeanyLua Plugin Not Found
```bash
sudo apt install geany-plugin-lua
```

### 6. Menu Items Not Appearing
1. Restart Geany completely
2. Go to `Tools → Plugin Manager`
3. Ensure `GeanyLua` is checked/enabled
4. Check `View → Show Message Window` for error messages

### 7. Plugin Not Loading
Check the Message Window (`View → Show Message Window`) for specific error messages.

## Verification Steps

### 1. Test Lua Dependencies
```bash
lua -e "
local ok1, cjson = pcall(require, 'cjson')
local ok2, socket = pcall(require, 'socket')
local ok3, ssl = pcall(require, 'ssl.https')

print('cjson:', ok1 and 'OK' or 'MISSING')
print('socket:', ok2 and 'OK' or 'MISSING')
print('ssl.https:', ok3 and 'OK' or 'MISSING')
"
```

### 2. Check Plugin Installation
```bash
ls -la ~/.config/geany/plugins/geanylua/geany-copilot.lua
```

### 3. Check Configuration
```bash
ls -la ~/.config/geany/geany-copilot/config.json
```

### 4. Test GeanyLua
1. Open Geany
2. Look for `Tools → Test GeanyLua` menu item
3. Click it to test basic functionality

## Expected Menu Items

After successful installation, you should see these menu items under `Tools`:
- ✅ **AI Code Assistant** - For code completion and assistance
- ✅ **AI Copywriter** - For text improvement and writing help
- ✅ **Copilot Settings** - For configuration management
- ✅ **Test GeanyLua** - For testing basic functionality

## Configuration

### API Key Setup
Edit `~/.config/geany/geany-copilot/config.json`:

```json
{
    "api-provider": "deepseek",
    "deepseek-api-key": "YOUR_DEEPSEEK_API_KEY_HERE",
    "deepseek-base-url": "https://api.deepseek.com/v1",
    "model": "deepseek-coder",
    "temperature": 0.7,
    "max-tokens": 2048
}
```

### Supported Providers
- **DeepSeek** (recommended): `deepseek-coder` model
- **OpenAI**: `gpt-4` and other models
- **Custom**: Any OpenAI-compatible API

## File Locations

- **Plugin:** `~/.config/geany/plugins/geanylua/geany-copilot.lua`
- **Config:** `~/.config/geany/geany-copilot/config.json`
- **Test Script:** `~/.config/geany/plugins/geanylua/test-geanylua.lua`

## System Requirements

- **OS:** Linux Mint 22.1 (Ubuntu-based) ✅
- **Geany:** Any recent version ✅
- **GeanyLua Plugin:** `geany-plugin-lua` package ✅
- **Lua Libraries:** `lua-cjson`, `lua-socket`, `lua-sec` ✅

## Getting Help

If you encounter issues:

1. **Check Message Window:** `View → Show Message Window` in Geany
2. **Test Dependencies:** Run the verification commands above
3. **Check Logs:** Look for error messages in Geany's output
4. **Restart Geany:** Sometimes a complete restart resolves issues

## Success Indicators

✅ **Plugin Loaded:** "Geany Copilot v2.0.0 loaded successfully!" message
✅ **Menu Items:** All three menu items appear under Tools
✅ **Dependencies:** All Lua modules load without errors
✅ **Configuration:** Config file created with default values
✅ **SSL Support:** HTTPS API calls work (with lua-sec installed)

## Next Steps

1. **Configure API Keys:** Add your DeepSeek or OpenAI API key
2. **Test Functionality:** Try the AI Code Assistant with some code
3. **Customize Settings:** Adjust temperature, max tokens, etc.
4. **Enjoy Coding:** Use AI assistance directly in Geany!

---

**Note:** The plugin now includes comprehensive error handling and will provide helpful messages if any dependencies are missing or if there are configuration issues.
