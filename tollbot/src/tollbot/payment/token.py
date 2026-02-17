"""Payment token generation and validation."""
import os
import time
import uuid
import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class PaymentToken:
    """Payment token data structure."""
    wallet_id: str
    currency: str
    amount: float
    unit: int
    path: str
    timestamp: int
    nonce: str
    signature: Optional[str] = None


class TokenManager:
    """Manage payment token generation and validation."""

    def __init__(self, config_dir: str = "/etc/tollbot"):
        """Initialize token manager.

        Args:
            config_dir: Directory containing wallet configuration
        """
        self.config_dir = config_dir
        self._private_key = None
        self._public_key = None
        self._used_nonces = set()

    def generate_keypair(self) -> str:
        """Generate a new keypair for signing tokens.

        Returns:
            str: Base64-encoded public key
        """
        private_key = uuid.uuid4().hex + uuid.uuid4().hex
        public_key = hashlib.sha256(private_key.encode()).hexdigest()

        self._private_key = private_key
        self._public_key = public_key

        return public_key

    def load_wallet(self, wallet_file: Optional[str] = None) -> bool:
        """Load wallet configuration from file.

        Args:
            wallet_file: Path to wallet config file

        Returns:
            bool: True if loading succeeded
        """
        if wallet_file is None:
            wallet_file = os.path.join(self.config_dir, "wallet.conf")

        if not os.path.exists(wallet_file):
            return False

        try:
            with open(wallet_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("public_key="):
                        self._public_key = line.split("=", 1)[1]
            return True
        except Exception:
            return False

    def sign_token(self, token: PaymentToken) -> str:
        """Sign a payment token.

        Args:
            token: PaymentToken to sign

        Returns:
            str: Base64-encoded signature
        """
        if self._private_key is None:
            raise ValueError("Private key not available")

        token_data = json.dumps({
            "wallet_id": token.wallet_id,
            "currency": token.currency,
            "amount": token.amount,
            "unit": token.unit,
            "path": token.path,
            "timestamp": token.timestamp,
            "nonce": token.nonce,
        }, sort_keys=True)

        signature = hmac.new(
            self._private_key.encode(),
            token_data.encode(),
            hashlib.sha256
        ).digest()

        return base64.b64encode(signature).decode()

    def create_token(
        self,
        wallet_id: str,
        currency: str,
        amount: float,
        unit: int,
        path: str,
        ttl: int = 3600,
    ) -> PaymentToken:
        """Create a new payment token.

        Args:
            wallet_id: Wallet identifier
            currency: Currency code (e.g., USDC)
            amount: Payment amount
            unit: Unit definition
            path: Protected path
            ttl: Token time-to-live in seconds

        Returns:
            PaymentToken: Generated token
        """
        timestamp = int(time.time())
        nonce = uuid.uuid4().hex
        expiration = timestamp + ttl

        token = PaymentToken(
            wallet_id=wallet_id,
            currency=currency,
            amount=amount,
            unit=unit,
            path=path,
            timestamp=timestamp,
            nonce=nonce,
        )

        token.signature = self.sign_token(token)

        return token

    def validate_token(
        self,
        token: PaymentToken,
        min_amount: float,
        requested_path: str,
    ) -> bool:
        """Validate a payment token.

        Args:
            token: PaymentToken to validate
            min_amount: Minimum required payment amount
            requested_path: Path being requested

        Returns:
            bool: True if token is valid
        """
        expected_signature = self.sign_token(token)
        if not hmac.compare_digest(token.signature, expected_signature):
            return False

        if token.timestamp < int(time.time()) - 3600:
            return False

        if not requested_path.startswith(token.path):
            return False

        if token.amount < min_amount:
            return False

        if token.nonce in self._used_nonces:
            return False

        self._used_nonces.add(token.nonce)

        return True

    def rotate_keys(self, config_dir: Optional[str] = None):
        """Rotate wallet keys.

        Args:
            config_dir: Configuration directory
        """
        if config_dir is None:
            config_dir = self.config_dir

        new_public_key = self.generate_keypair()
        wallet_file = os.path.join(config_dir, "wallet.conf")

        with open(wallet_file, "a") as f:
            f.write(f"public_key={new_public_key}\n")
            f.write(f"rotation_timestamp={int(time.time())}\n")
