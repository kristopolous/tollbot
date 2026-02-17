"""Tollbot init command handler."""
import os
import sys

from tollbot.robots_parser import RobotsParser
from tollbot.payment.token import TokenManager
from tollbot.nginx.configurator import NginxConfigurator


def handle_init(args):
    """Handle tollbot init command."""
    print(f"Initializing tollbot for domain: {args.domain}")
    print(f"Configuration directory: {args.config_dir}")

    # Create config directory
    os.makedirs(args.config_dir, exist_ok=True)

    # Parse robots.txt if exists
    robots_path = f"/var/www/{args.domain}/robots.txt"
    if os.path.exists(robots_path):
        parser = RobotsParser()
        pricing = parser.parse_file(robots_path)
        print(f"Found {len(pricing)} pricing directives in robots.txt")
        for path, info in pricing.items():
            print(f"  {path}: {info['price']} {info['currency']} per {info['unit']} requests")
    else:
        print(f"Warning: robots.txt not found at {robots_path}")

    # Generate wallet configuration
    if args.wallet:
        token_manager = TokenManager()
        wallet_config = {
            "wallet_id": args.wallet,
            "currency": "USDC",
            "public_key": token_manager.generate_keypair(),
        }
        wallet_path = os.path.join(args.config_dir, "wallet.conf")
        with open(wallet_path, "w") as f:
            for k, v in wallet_config.items():
                f.write(f"{k}={v}\n")
        print(f"Wallet configuration saved to {wallet_path}")

    # Generate nginx configuration
    if not args.dry_run:
        nginx_conf = NginxConfigurator(args.domain, args.config_dir)
        nginx_conf.generate()
        print("Nginx configuration generated")
    else:
        print("Dry run mode - skipping nginx configuration")

    print("Tollbot initialized successfully")
