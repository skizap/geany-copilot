--[[
Simple test script to verify GeanyLua functionality
Place this in ~/.config/geany/plugins/geanylua/ and restart Geany
It should create a "Test GeanyLua" menu item under Tools
]]

-- Test basic GeanyLua functionality
local function test_geanylua()
    geany.message("GeanyLua is working correctly!")
    
    -- Test JSON library
    local json_ok, json = pcall(require, "cjson")
    if json_ok then
        geany.message("JSON library (cjson) is available")
        
        -- Test JSON encoding/decoding
        local test_data = {message = "Hello from GeanyLua", version = "1.0"}
        local encoded = json.encode(test_data)
        local decoded = json.decode(encoded)
        geany.message("JSON test successful: " .. decoded.message)
    else
        geany.message("JSON library not available")
    end
    
    -- Test socket library
    local socket_ok, socket = pcall(require, "socket")
    if socket_ok then
        geany.message("Socket library is available")
    else
        geany.message("Socket library not available")
    end
end

-- Create menu item
geany.menu("Test GeanyLua", test_geanylua)
