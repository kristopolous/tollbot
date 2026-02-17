"""Tests for tollbot payment validator."""
import pytest
import os
import tempfile

from tollbot.payment.validator import PaymentValidator


def test_init_validator():
    """Test validator initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        validator = PaymentValidator(tmpdir)
        assert validator is not None


def test_validate_request_dry_run():
    """Test validation in dry-run mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        validator = PaymentValidator(tmpdir)
        validator.dry_run = True

        # In dry-run mode, all requests should pass
        result = validator.validate_request("fake_token", "/api/data/")
        assert result is True


def test_get_min_price_default():
    """Test getting minimum price when no cache exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        validator = PaymentValidator(tmpdir)

        price = validator._get_min_price("/api/data/")
        assert price == 0.001  # Default price


def test_get_min_price_with_cache(tmp_path):
    """Test getting minimum price from cache."""
    # Create cache file
    cache_file = tmp_path / "robots_cache.json"
    cache_file.write_text('{"pricing": {"/api/data/": {"price": 0.002}}}')

    validator = PaymentValidator(str(tmp_path))
    validator.config_dir = str(tmp_path)

    # Patch the cache file path
    original_get_min = validator._get_min_price

    def patched_get_min(path):
        import json
        cache_file = os.path.join(validator.config_dir, "robots_cache.json")
        if os.path.exists(cache_file):
            with open(cache_file) as f:
                cache = json.load(f)
                pricing = cache.get("pricing", {})
                for prefix, info in pricing.items():
                    if path.startswith(prefix):
                        return info.get("price", validator.default_price)
        return validator.default_price

    validator._get_min_price = patched_get_min

    price = validator._get_min_price("/api/data/something")
    assert price == 0.002
