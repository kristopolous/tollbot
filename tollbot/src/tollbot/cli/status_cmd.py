"""Tollbot status command handler."""
import os

from tollbot.nginx.configurator import NginxConfigurator


def handle_status(args):
    """Handle tollbot status command."""
    config_dir = "/etc/tollbot"

    print("Tollbot Status")
    print("=" * 40)

    # Check config
    config_file = os.path.join(config_dir, "config.ini")
    if os.path.exists(config_file):
        print(f"Config file: {config_file}")
        print("Status: Configured")
    else:
        print(f"Config file: {config_file}")
        print("Status: Not configured")

    # Check nginx config
    nginx_include = os.path.join(config_dir, "nginx", "tollbot-include.conf")
    if os.path.exists(nginx_include):
        print(f"Nginx include: {nginx_include}")
        print("Nginx: Configured")
    else:
        print(f"Nginx include: {nginx_include}")
        print("Nginx: Not configured")

    # Check wallet
    wallet_file = os.path.join(config_dir, "wallet.conf")
    if os.path.exists(wallet_file):
        print("Wallet: Configured")
    else:
        print("Wallet: Not configured")

    # Check payment endpoints
    print("Payment endpoints:")
    print(f"  /__tollbot__/validate - Validates payment tokens")
    print(f"  /__tollbot__/request-payment - Requests payment tokens")
