"""Tollbot run command handler."""
import time
import logging

from tollbot.robots_parser import RobotsParser
from tollbot.payment.validator import PaymentValidator


def handle_run(args):
    """Handle tollbot run command."""
    log_level = getattr(logging, args.log_level.upper())
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    config_dir = "/etc/tollbot"
    robots_path = f"{config_dir}/robots_cache.json"

    print("Starting tollbot service...")
    print("Press Ctrl+C to stop")

    validator = PaymentValidator(config_dir)

    if args.dry_run:
        print("Dry run mode - will validate but not block requests")
        validator.dry_run = True

    try:
        while True:
            if os.path.exists(robots_path):
                parser = RobotsParser()
                parser.load_cache(robots_path)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping tollbot service...")
