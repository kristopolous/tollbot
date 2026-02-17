"""Tests for tollbot audit logger."""
import pytest
import os
import tempfile
import json
import logging

from tollbot.logging.audit import AuditLogger


def test_init_logger():
    """Test logger initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(tmpdir)
        assert logger is not None


def test_log_validation():
    """Test logging validation events."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(tmpdir, log_format="json")

        logger.log_validation(
            path="/api/data/",
            wallet_id="W123",
            amount=0.001,
            is_valid=True,
            client_ip="192.168.1.1",
        )

        log_file = os.path.join(tmpdir, "payments.log")
        assert os.path.exists(log_file)

        with open(log_file) as f:
            line = f.readline()
            log = json.loads(line)
            assert log["path"] == "/api/data/"
            assert log["wallet_id"] == "W123"
            assert log["is_valid"] is True


def test_log_validation_invalid():
    """Test logging invalid validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(tmpdir, log_format="json")

        logger.log_validation(
            path="/api/data/",
            wallet_id="W123",
            amount=0.0005,
            is_valid=False,
            client_ip="192.168.1.1",
            error="Insufficient payment",
        )

        log_file = os.path.join(tmpdir, "payments.log")
        with open(log_file) as f:
            line = f.readline()
            log = json.loads(line)
            assert log["is_valid"] is False
            assert log["error"] == "Insufficient payment"


def test_log_request():
    """Test logging payment requests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(tmpdir, log_format="json")

        logger.log_request(
            path="/api/data/",
            amount_due=0.001,
            client_ip="192.168.1.1",
        )

        log_file = os.path.join(tmpdir, "payments.log")
        with open(log_file) as f:
            line = f.readline()
            log = json.loads(line)
            assert log["event_type"] == "payment_request"
            assert log["amount_due"] == 0.001


def test_export_to_csv():
    """Test CSV export."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(tmpdir, log_format="json")

        logger.log_validation(
            path="/api/data/",
            wallet_id="W123",
            amount=0.001,
            is_valid=True,
        )

        csv_file = os.path.join(tmpdir, "export.csv")
        logger.export_to_csv(csv_file)

        assert os.path.exists(csv_file)

        with open(csv_file) as f:
            lines = f.readlines()
            assert "timestamp,path" in lines[0]


def test_export_to_json():
    """Test JSON export."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(tmpdir, log_format="json")

        logger.log_validation(
            path="/api/data/",
            wallet_id="W123",
            amount=0.001,
            is_valid=True,
        )

        json_file = os.path.join(tmpdir, "export.json")
        logger.export_to_json(json_file)

        assert os.path.exists(json_file)

        with open(json_file) as f:
            logs = json.load(f)
            assert len(logs) > 0
