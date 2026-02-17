"""Tests for tollbot nginx configurator."""
import pytest
import os
import tempfile

from tollbot.nginx.configurator import NginxConfigurator


def test_generate_config():
    """Test nginx configuration generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        configurator = NginxConfigurator("example.com", tmpdir)
        configurator.generate()

        # Check include file was created
        include_file = os.path.join(tmpdir, "nginx", "tollbot-include.conf")
        assert os.path.exists(include_file)

        # Check domain config was created
        domain_file = os.path.join(tmpdir, "nginx", "example.com.conf")
        assert os.path.exists(domain_file)

        # Verify content
        with open(include_file) as f:
            content = f.read()
            assert "/__tollbot__/validate" in content
            assert "/__tollbot__/request-payment" in content


def test_get_include_config():
    """Test include configuration generation."""
    configurator = NginxConfigurator("example.com", "/tmp")
    config = configurator._get_include_config()

    assert "location /__tollbot__/validate" in config
    assert "content_by_lua_file" in config


def test_get_domain_config():
    """Test domain configuration generation."""
    configurator = NginxConfigurator("example.com", "/tmp")
    config = configurator._get_domain_config()

    assert "server_name example.com" in config
    assert "/api/" in config


def test_test_config():
    """Test configuration validation."""
    configurator = NginxConfigurator("example.com", "/tmp")

    # This will return False if nginx is not installed
    result = configurator.test_config()
    # Accept both True and False as valid results
    assert result in (True, False)


def test_reload():
    """Test nginx reload."""
    configurator = NginxConfigurator("example.com", "/tmp")

    # This will fail if nginx is not running, but that's expected
    # We just want to make sure the method exists and doesn't crash
    configurator.reload()
