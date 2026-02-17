"""Parser for tollbot pricing directives in robots.txt."""
import re
import json
import os


class RobotsParser:
    """Parse tollbot pricing directives from robots.txt."""

    def __init__(self):
        """Initialize parser."""
        self.pricing = {}
        self.wallet = None
        self.currency = "USDC"

    def parse(self, content):
        """Parse robots.txt content and extract pricing directives.

        Args:
            content: robots.txt file content as string

        Returns:
            dict: Pricing directives mapping paths to price info
        """
        self.pricing = {}
        self.wallet = None
        self.currency = "USDC"

        lines = content.split("\n")

        for line in lines:
            line = line.strip()

            # Parse wallet directive
            wallet_match = re.match(r"#\s*@wallet:\s*(\S+)\s*@currency:\s*(\S+)", line)
            if wallet_match:
                self.wallet = wallet_match.group(1)
                self.currency = wallet_match.group(2)
                continue

            # Parse pricing directive
            price_match = re.search(r"#\s*@price:\s*(\d+\.?\d*)\s*@unit:\s*(\d+)", line)
            if price_match:
                # Extract the path (first Disallow or Allow directive)
                path_match = re.match(r"(Disallow|Allow):\s*(\S+)", line)
                if path_match:
                    path = path_match.group(2)
                    self.pricing[path] = {
                        "price": float(price_match.group(1)),
                        "unit": int(price_match.group(2)),
                        "currency": self.currency,
                    }

        return self.pricing

    def parse_file(self, filepath):
        """Parse robots.txt from a file.

        Args:
            filepath: Path to robots.txt file

        Returns:
            dict: Pricing directives
        """
        if not os.path.exists(filepath):
            return {}

        with open(filepath, "r") as f:
            content = f.read()

        return self.parse(content)

    def get_price(self, path):
        """Get price for a specific path.

        Args:
            path: Request path

        Returns:
            dict: Price info or None if not specified
        """
        # Exact match
        if path in self.pricing:
            return self.pricing[path]

        # Prefix match
        for prefix, info in self.pricing.items():
            if path.startswith(prefix):
                return info

        return None

    def save_cache(self, filepath):
        """Save parsed pricing to cache file.

        Args:
            filepath: Path to cache file
        """
        cache = {
            "wallet": self.wallet,
            "currency": self.currency,
            "pricing": self.pricing,
            "timestamp": int(time.time()),
        }
        with open(filepath, "w") as f:
            json.dump(cache, f, indent=2)

    def load_cache(self, filepath):
        """Load pricing from cache file.

        Args:
            filepath: Path to cache file
        """
        if not os.path.exists(filepath):
            return

        with open(filepath, "r") as f:
            cache = json.load(f)

        self.wallet = cache.get("wallet")
        self.currency = cache.get("currency", "USDC")
        self.pricing = cache.get("pricing", {})


import time
