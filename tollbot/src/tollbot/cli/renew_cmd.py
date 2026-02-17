"""Tollbot renew command handler."""
import os

from tollbot.payment.token import TokenManager
from tollbot.nginx.configurator import NginxConfigurator


def handle_renew(args):
    """Handle tollbot renew command."""
    config_dir = "/etc/tollbot"

    print("Tollbot renewal")

    # Renew payment keys
    token_manager = TokenManager()
    if os.path.exists(os.path.join(config_dir, "wallet.conf")):
        token_manager.rotate_keys(config_dir)
        print("Payment keys rotated")

    # Reload nginx
    if os.path.exists("/etc/nginx/nginx.conf"):
        nginx_conf = NginxConfigurator("default", config_dir)
        nginx_conf.reload()
        print("Nginx reloaded")

    print("Renewal complete")
