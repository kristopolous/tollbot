# Tollbot


Tollbot is a **fork of Certbot** designed for site operators who want to **monetize access to their content for AI scrapers**. It integrates with **Circle / USDC payments on Arc**, enabling a seamless flow for technical users and admins to enforce a “pay-to-scrape” policy.

Tollbot follows the familiar **Certbot experience** — simple CLI commands, automated TLS handling, and a step-by-step flow — but replaces the certificate issuance workflow with **payment policy enforcement**.

---

## Features

* **Certbot-style CLI experience**

  * Familiar commands for technical users and system admins
  * Step-by-step configuration
* **USDC / Circle integration**

  * Accept payments directly via Circle
  * Generate and verify payment tokens for scrapers
* **Robots.txt-based policy**

  * Read and parse pricing directives in `robots.txt`
  * Enforce per-path access pricing
* **nginx integration**

  * Automatically configures nginx to enforce paid scraping
  * Lightweight Go/Lua modules handle request validation
* **Audit & logs**

  * Track paid accesses
  * Optional CSV/JSON export for analytics

---

## Installation

Tollbot is distributed as a single Go binary and requires:

* Linux (Debian / Ubuntu recommended)
* nginx installed and accessible
* `robots.txt` configured with tollbot directives

Download:

```bash
git clone https://github.com/kristopolous/tollbot.git
cd tollbot
make build
sudo cp bin/tollbot /usr/local/bin/
```

---

## Basic Usage

Initialize Tollbot for your site:

```bash
sudo tollbot init --domain example.com
```

This will:

1. Detect nginx configuration
2. Read pricing directives from `robots.txt`
3. Generate payment endpoints and keys
4. Configure nginx to validate USDC payment tokens

To run:

```bash
sudo tollbot run
```

Optional flags:

```bash
--dry-run       # Test payment verification without blocking
--log-level     # Set verbosity: info, debug, error
--wallet        # Circle wallet address for payments
```

---

## robots.txt Integration

Tollbot uses **robots.txt comments** to define pay-to-scrape policies:

```
# @wallet: xxxxxx @currency: USDC
User-agent: *
Disallow: /cgi-bin/  # @price: 0.001 @unit: 100
Disallow: /tmp/      # @price: 0.003 @unit: 100
```

* `@wallet` – Circle wallet for receiving payments
* `@currency` – Currently supported: `USDC`
* `@price` – Amount per unit
* `@unit` – Unit definition (requests, tokens, etc.)

Tollbot reads this file and enforces payment before allowing access to paths marked with pricing directives.

