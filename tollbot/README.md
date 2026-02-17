# Tollbot

Pay-to-scrape enforcer for AI content access

Tollbot is a fork of Certbot designed for site operators who want to monetize access to their content for AI scrapers. It integrates with Circle/USDC payments on Arc, enabling a seamless flow for technical users and admins to enforce a "pay-to-scrape" policy.

## Features

* **Certbot-style CLI experience** - Familiar commands for technical users
* **USDC / Circle integration** - Accept payments directly via Circle
* **Robots.txt-based policy** - Define pricing in robots.txt comments
* **nginx integration** - Automatic configuration with Lua validation modules
* **Audit & logs** - Track paid accesses with CSV/JSON export

## Installation

```bash
pip install tollbot
```

## Basic Usage

Initialize Tollbot for your site:

```bash
sudo tollbot init --domain example.com --wallet YOUR_CIRCLE_WALLET_ID
```

To run:

```bash
sudo tollbot run
```

## robots.txt Integration

Tollbot uses **robots.txt comments** to define pay-to-scrape policies:

```
# @wallet: CIRCLE_WALLET_ID @currency: USDC
User-agent: *
Disallow: /cgi-bin/  # @price: 0.001 @unit: 100
Disallow: /tmp/      # @price: 0.003 @unit: 100
```

## License

MIT
