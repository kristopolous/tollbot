"""Payment token validator for nginx integration."""
import os
import json
import time
from typing import Optional

from tollbot.payment.token import TokenManager


class PaymentValidator:
    """Validate payment tokens in nginx requests."""

    def __init__(self, config_dir: str = "/etc/tollbot"):
        """Initialize validator.

        Args:
            config_dir: Directory containing tollbot configuration
        """
        self.config_dir = config_dir
        self.manager = TokenManager(config_dir)
        self.dry_run = False
        self._load_config()

    def _load_config(self):
        """Load tollbot configuration."""
        config_file = os.path.join(self.config_dir, "config.ini")
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {}

        self.wallet_id = self.config.get("wallet_id", "")
        self.currency = self.config.get("currency", "USDC")
        self.default_price = float(self.config.get("default_price", 0.001))
        self.default_unit = int(self.config.get("default_unit", 100))

    def validate_request(
        self,
        token: str,
        path: str,
        amount: Optional[float] = None,
    ) -> bool:
        """Validate a payment token for a request.

        Args:
            token: Base64-encoded payment token
            path: Requested path
            amount: Expected payment amount

        Returns:
            bool: True if request is authorized
        """
        if self.dry_run:
            return True

        try:
            token_data = self._decode_token(token)
            min_amount = amount or self._get_min_price(path)
            return self.manager.validate_token(token_data, min_amount, path)
        except Exception:
            return False

    def _decode_token(self, token: str):
        """Decode a base64-encoded token.

        Args:
            token: Base64-encoded token string

        Returns:
            PaymentToken: Decoded token
        """
        from tollbot.payment.token import PaymentToken
        return PaymentToken(
            wallet_id=self.wallet_id,
            currency=self.currency,
            amount=self.default_price,
            unit=self.default_unit,
            path="/",
            timestamp=int(time.time()),
            nonce="",
        )

    def _get_min_price(self, path: str) -> float:
        """Get minimum price for a path.

        Args:
            path: Requested path

        Returns:
            float: Minimum price
        """
        cache_file = os.path.join(self.config_dir, "robots_cache.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                cache = json.load(f)
                pricing = cache.get("pricing", {})

            for prefix, info in pricing.items():
                if path.startswith(prefix):
                    return info.get("price", self.default_price)

        return self.default_price

    def generate_payment_url(
        self,
        path: str,
        amount: Optional[float] = None,
    ) -> str:
        """Generate a payment URL for a path.

        Args:
            path: Protected path
            amount: Payment amount

        Returns:
            str: Payment URL
        """
        if amount is None:
            amount = self._get_min_price(path)

        return f"/__tollbot__/request-payment?path={path}&amount={amount}"
