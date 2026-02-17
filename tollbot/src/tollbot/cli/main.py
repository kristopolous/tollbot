"""Tollbot main CLI module."""
import argparse
import sys

from tollbot import __version__


def main():
    """Main entry point for tollbot CLI."""
    parser = argparse.ArgumentParser(
        prog="tollbot",
        description="Tollbot - Pay-to-scrape enforcer for AI content access",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"tollbot {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize tollbot for a domain")
    init_parser.add_argument("--domain", required=True, help="Domain name to configure")
    init_parser.add_argument("--wallet", help="Circle wallet address for payments")
    init_parser.add_argument(
        "--dry-run", action="store_true", help="Test configuration without modifying nginx"
    )
    init_parser.add_argument(
        "--config-dir",
        default="/etc/tollbot",
        help="Configuration directory (default: /etc/tollbot)",
    )

    # run command
    run_parser = subparsers.add_parser("run", help="Start tollbot service")
    run_parser.add_argument(
        "--dry-run", action="store_true", help="Validate without enforcing payments"
    )
    run_parser.add_argument(
        "--log-level",
        choices=["debug", "info", "error"],
        default="info",
        help="Set logging verbosity",
    )

    # status command
    status_parser = subparsers.add_parser("status", help="Show tollbot status")

    # renew command
    renew_parser = subparsers.add_parser("renew", help="Renew payment configuration")
    renew_parser.add_argument(
        "--force", action="store_true", help="Force renewal regardless of key age"
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "init":
        from tollbot.cli import init_cmd
        init_cmd.handle_init(args)
    elif args.command == "run":
        from tollbot.cli import run_cmd
        run_cmd.handle_run(args)
    elif args.command == "status":
        from tollbot.cli import status_cmd
        status_cmd.handle_status(args)
    elif args.command == "renew":
        from tollbot.cli import renew_cmd
        renew_cmd.handle_renew(args)

    return 0
