"""Tests for tollbot payment tokens."""
import pytest
import time
import os
import tempfile

from tollbot.payment.token import TokenManager, PaymentToken


def test_generate_keypair():
    """Test keypair generation."""
    manager = TokenManager()
    public_key = manager.generate_keypair()

    assert public_key is not None
    assert len(public_key) > 0


def test_create_token():
    """Test token creation."""
    manager = TokenManager()
    manager.generate_keypair()

    token = manager.create_token(
        wallet_id="TEST_WALLET",
        currency="USDC",
        amount=0.001,
        unit=100,
        path="/api/data/",
    )

    assert token.wallet_id == "TEST_WALLET"
    assert token.currency == "USDC"
    assert token.amount == 0.001
    assert token.unit == 100
    assert token.path == "/api/data/"
    assert token.signature is not None
    assert token.nonce is not None


def test_sign_token():
    """Test token signing."""
    manager = TokenManager()
    manager.generate_keypair()

    token = PaymentToken(
        wallet_id="TEST_WALLET",
        currency="USDC",
        amount=0.001,
        unit=100,
        path="/api/data/",
        timestamp=int(time.time()),
        nonce="test_nonce",
    )

    signature = manager.sign_token(token)
    assert signature is not None
    assert len(signature) > 0


def test_validate_token():
    """Test token validation."""
    manager = TokenManager()
    manager.generate_keypair()

    token = manager.create_token(
        wallet_id="TEST_WALLET",
        currency="USDC",
        amount=0.001,
        unit=100,
        path="/api/data/",
    )

    is_valid = manager.validate_token(token, 0.001, "/api/data/")
    assert is_valid is True


def test_validate_token_invalid_signature():
    """Test validation with invalid signature."""
    manager = TokenManager()
    manager.generate_keypair()

    token = PaymentToken(
        wallet_id="TEST_WALLET",
        currency="USDC",
        amount=0.001,
        unit=100,
        path="/api/data/",
        timestamp=int(time.time()),
        nonce="test_nonce",
        signature="invalid_signature",
    )

    is_valid = manager.validate_token(token, 0.001, "/api/data/")
    assert is_valid is False


def test_validate_token_expired():
    """Test validation with expired token."""
    manager = TokenManager()
    manager.generate_keypair()

    old_timestamp = int(time.time()) - 7200

    token = PaymentToken(
        wallet_id="TEST_WALLET",
        currency="USDC",
        amount=0.001,
        unit=100,
        path="/api/data/",
        timestamp=old_timestamp,
        nonce="test_nonce",
    )

    token.signature = manager.sign_token(token)

    is_valid = manager.validate_token(token, 0.001, "/api/data/")
    assert is_valid is False


def test_validate_token_replay():
    """Test replay protection."""
    manager = TokenManager()
    manager.generate_keypair()

    token = manager.create_token(
        wallet_id="TEST_WALLET",
        currency="USDC",
        amount=0.001,
        unit=100,
        path="/api/data/",
    )

    is_valid = manager.validate_token(token, 0.001, "/api/data/")
    assert is_valid is True

    is_valid = manager.validate_token(token, 0.001, "/api/data/")
    assert is_valid is False


def test_rotate_keys():
    """Test key rotation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = TokenManager(tmpdir)
        manager.generate_keypair()
        old_public_key = manager._public_key

        manager.rotate_keys(tmpdir)

        assert manager._public_key != old_public_key

        wallet_file = os.path.join(tmpdir, "wallet.conf")
        assert os.path.exists(wallet_file)
