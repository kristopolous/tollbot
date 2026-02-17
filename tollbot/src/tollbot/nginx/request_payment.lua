-- Tollbot payment request handler for nginx/luajit
local cjson = require "cjson"
local uuid = require "resty.uuid"

-- Generate payment request URL
local function generate_payment_url(wallet_id, path, amount)
    local nonce = uuid.generate()
    local timestamp = ngx.time()

    local payment_data = {
        wallet_id = wallet_id,
        path = path,
        amount = amount,
        nonce = nonce,
        timestamp = timestamp,
    }

    return "/__tollbot__/payment?data=" .. base64_encode(cjson.encode(payment_data))
end

-- Base64 encode
local function base64_encode(str)
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

-- Handle payment request
local function handle_request()
    local path = ngx.var.arg_path or "/"
    local amount = tonumber(ngx.var.arg_amount) or 0.001

    local wallet_config = load_wallet_config()
    if not wallet_config then
        ngx.status = ngx.HTTP_INTERNAL_SERVER_ERROR
        ngx.say(cjson.encode({error = "Wallet not configured"}))
        ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
    end

    local payment_url = generate_payment_url(wallet_config.wallet_id, path, amount)

    ngx.status = ngx.HTTP_OK
    ngx.say(cjson.encode({
        payment_url = payment_url,
        amount = amount,
        path = path,
    }))
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

-- Main entry point
local function main()
    handle_request()
end

return {
    main = main,
    generate_payment_url = generate_payment_url,
}
