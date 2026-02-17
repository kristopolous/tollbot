"""Tests for tollbot robots.txt parser."""
import pytest
import os
import tempfile

from tollbot.robots_parser import RobotsParser


def test_parse_basic_pricing():
    """Test parsing basic pricing directives."""
    content = """
# @wallet: CIRCLE_WALLET_ID @currency: USDC
User-agent: *
Disallow: /api/data/  # @price: 0.001 @unit: 100
Disallow: /api/models/  # @price: 0.003 @unit: 100
"""
    parser = RobotsParser()
    pricing = parser.parse(content)

    assert parser.wallet == "CIRCLE_WALLET_ID"
    assert parser.currency == "USDC"
    assert "/api/data/" in pricing
    assert pricing["/api/data/"]["price"] == 0.001
    assert pricing["/api/data/"]["unit"] == 100
    assert pricing["/api/models/"]["price"] == 0.003


def test_parse_with_allow_directives():
    """Test parsing with Allow directives."""
    content = """
# @wallet: CIRCLE_WALLET_ID @currency: USDC
User-agent: *
Allow: /api/public/
Disallow: /api/private/  # @price: 0.002 @unit: 100
"""
    parser = RobotsParser()
    pricing = parser.parse(content)

    assert "/api/private/" in pricing
    assert pricing["/api/private/"]["price"] == 0.002


def test_parse_no_pricing():
    """Test parsing robots.txt without pricing directives."""
    content = """
User-agent: *
Disallow: /admin/
Disallow: /private/
"""
    parser = RobotsParser()
    pricing = parser.parse(content)

    assert len(pricing) == 0
    assert parser.wallet is None


def test_parse_file(tmp_path):
    """Test parsing from file."""
    robots_file = tmp_path / "robots.txt"
    robots_file.write_text("""
# @wallet: CIRCLE_WALLET_ID @currency: USDC
User-agent: *
Disallow: /api/  # @price: 0.001 @unit: 100
""")

    parser = RobotsParser()
    pricing = parser.parse_file(str(robots_file))

    assert len(pricing) == 1
    assert "/api/" in pricing


def test_get_price_exact_match():
    """Test getting price for exact path match."""
    content = """
# @wallet: CIRCLE_WALLET_ID @currency: USDC
User-agent: *
Disallow: /api/data/  # @price: 0.001 @unit: 100
"""
    parser = RobotsParser()
    parser.parse(content)

    price = parser.get_price("/api/data/")
    assert price is not None
    assert price["price"] == 0.001


def test_get_price_prefix_match():
    """Test getting price for prefix match."""
    content = """
# @wallet: CIRCLE_WALLET_ID @currency: USDC
User-agent: *
Disallow: /api/  # @price: 0.001 @unit: 100
"""
    parser = RobotsParser()
    parser.parse(content)

    price = parser.get_price("/api/data/")
    assert price is not None
    assert price["price"] == 0.001


def test_save_and_load_cache(tmp_path):
    """Test saving and loading cache."""
    content = """
# @wallet: CIRCLE_WALLET_ID @currency: USDC
User-agent: *
Disallow: /api/  # @price: 0.001 @unit: 100
"""
    parser = RobotsParser()
    parser.parse(content)

    cache_file = tmp_path / "cache.json"
    parser.save_cache(str(cache_file))

    # Load cache
    parser2 = RobotsParser()
    parser2.load_cache(str(cache_file))

    assert parser2.wallet == "CIRCLE_WALLET_ID"
    assert "/api/" in parser2.pricing
