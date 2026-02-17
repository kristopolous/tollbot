-- Tollbot payment validation filter for nginx/luajit
local cjson = require "cjson"
local hmac = require "resty.hmac"
local sha256 = require "resty.sha256"
local lrucache = require "resty.lrucache"

-- Cache for payment tokens
local cache, err = lrucache.new(1000)
if not cache then
    ngx.log(ngx.ERR, "failed to create cache: ", err)
end

-- Load wallet configuration
local function load_wallet_config()
    local f = io.open("/etc/tollbot/wallet.conf", "r")
    if not f then
        return nil
    end
    local content = f:read("*a")
    f:close()

    local config = {}
    for line in content:gmatch("[^\r\n]+") do
        local key, value = line:match("^([^=]+)=(.*)$")
        if key then
            config[key] = value
        end
    end
    return config
end

-- Validate payment token
local function validate_token(token, path)
    -- Parse token (JWT format)
    local parts = {}
    for part in token:gmatch("[^%.]+") do
        table.insert(parts, part)
    end

    if #parts ~= 3 then
        ngx.log(ngx.WARN, "Invalid token format")
        return false
    end

    -- Decode header
    local header_b64 = parts[1]
    local header = cjson.decode(base64_decode(header_b64))

    -- Decode payload
    local payload_b64 = parts[2]
    local payload = cjson.decode(base64_decode(payload_b64))

    -- Verify signature
    local signature_b64 = parts[3]
    local wallet_config = load_wallet_config()
    if not wallet_config then
        ngx.log(ngx.ERR, "Failed to load wallet config")
        return false
    end

    -- TODO: Implement signature verification
    -- For now, just check if token exists in cache
    local cache_key = "token:" .. payload.nonce
    if cache:get(cache_key) then
        ngx.log(ngx.WARN, "Token already used (replay attack)")
        return false
    end

    -- Mark token as used
    cache:set(cache_key, true, 3600)  -- 1 hour TTL

    -- Check path matches
    if payload.path ~= path then
        ngx.log(ngx.WARN, "Path mismatch: expected ", path, " got ", payload.path)
        return false
    end

    -- Check amount
    local min_amount = get_min_price(path)
    if payload.amount < min_amount then
        ngx.log(ngx.WARN, "Insufficient payment: ", payload.amount, " < ", min_amount)
        return false
    end

    return true
end

-- Get minimum price for path
local function get_min_price(path)
    -- Load from robots_cache.json
    local f = io.open("/etc/tollbot/robots_cache.json", "r")
    if not f then
        return 0.001  -- Default price
    end

    local content = f:read("*a")
    f:close()

    local cache = cjson.decode(content)
    local pricing = cache.pricing

    for prefix, info in pairs(pricing) do
        if path:sub(1, #prefix) == prefix then
            return info.price
        end
    end

    return 0.001  -- Default price
end

-- Base64 decode
local function base64_decode(str)
    local chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    local result = ""
    local padding = ""

    for i = 1, #str, 3 do
        local a = str:sub(i, i):byte() or 0
        local b = str:sub(i + 1, i + 1):byte() or 0
        local c = str:sub(i + 2, i + 2):byte() or 0

        result = result .. chars:sub(math.floor(a / 4) + 1, math.floor(a / 4) + 1)
        result = result .. chars:sub(math.floor(a % 4 * 16 + b / 16) + 1, math.floor(a % 4 * 16 + b / 16) + 1)
        result = result .. chars:sub(math.floor(b % 16 * 4 + c / 64) + 1, math.floor(b % 16 * 4 + c / 64) + 1)
        result = result .. chars:sub(c % 64 + 1, c % 64 + 1)
    end

    local mod = #str % 3
    if mod == 1 then
        result = result:sub(1, -2) .. "=="
    elseif mod == 2 then
        result = result:sub(1, -1) .. "="
    end

    return result
end

-- Main validation function
local function validate()
    local auth_header = ngx.req.get_headers()["Authorization"]
    local token = nil

    if auth_header and auth_header:sub(1, 7) == "Bearer " then
        token = auth_header:sub(8)
    else
        token = ngx.var.arg_token
    end

    if not token then
        ngx.status = ngx.HTTP_PAYMENT_REQUIRED
        ngx.say(cjson.encode({error = "Payment required"}))
        ngx.exit(ngx.HTTP_PAYMENT_REQUIRED)
    end

    local path = ngx.var.uri
    if validate_token(token, path) then
        return
    else
        ngx.status = ngx.HTTP_FORBIDDEN
        ngx.say(cjson.encode({error = "Invalid payment token"}))
        ngx.exit(ngx.HTTP_FORBIDDEN)
    end
end

-- Export functions
return {
    validate = validate,
    validate_token = validate_token,
    get_min_price = get_min_price,
}
