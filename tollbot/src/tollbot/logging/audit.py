"""Audit logging for tollbot payment validation."""
import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from tollbot.logging.formatters import JsonFormatter


class AuditLogger:
    """Audit logger for payment validation events."""

    def __init__(
        self,
        log_dir: str = "/var/log/tollbot",
        log_format: str = "json",
        retention_days: int = 30,
    ):
        """Initialize audit logger.

        Args:
            log_dir: Directory for log files
            log_format: Log format (json, csv, or combined)
            retention_days: Number of days to retain logs
        """
        self.log_dir = log_dir
        self.log_format = log_format
        self.retention_days = retention_days

        os.makedirs(log_dir, exist_ok=True)

        self.logger = logging.getLogger("tollbot.audit")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(os.path.join(log_dir, "payments.log"))
        handler.setLevel(logging.INFO)

        if log_format == "json":
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_validation(
        self,
        path: str,
        wallet_id: Optional[str],
        amount: float,
        is_valid: bool,
        client_ip: Optional[str] = None,
        error: Optional[str] = None,
    ):
        """Log a payment validation event.

        Args:
            path: Requested path
            wallet_id: Wallet ID (if provided)
            amount: Payment amount
            is_valid: Whether validation succeeded
            client_ip: Client IP address
            error: Error message (if validation failed)
        """
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": path,
            "wallet_id": wallet_id,
            "amount": amount,
            "is_valid": is_valid,
            "client_ip": client_ip,
            "error": error,
        }

        if self.log_format == "json":
            self.logger.info(json.dumps(event))
        else:
            self.logger.info(
                f"path={path} wallet={wallet_id} amount={amount} "
                f"valid={is_valid} ip={client_ip} error={error}"
            )

    def log_request(
        self,
        path: str,
        amount_due: float,
        client_ip: Optional[str] = None,
    ):
        """Log a payment request.

        Args:
            path: Requested path
            amount_due: Amount due
            client_ip: Client IP address
        """
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "payment_request",
            "path": path,
            "amount_due": amount_due,
            "client_ip": client_ip,
        }

        if self.log_format == "json":
            self.logger.info(json.dumps(event))
        else:
            self.logger.info(
                f"payment_request path={path} amount_due={amount_due} ip={client_ip}"
            )

    def export_to_csv(self, output_file: str, start_date: Optional[str] = None):
        """Export logs to CSV format.

        Args:
            output_file: Output file path
            start_date: Start date for filtering (ISO format)
        """
        logs = self._read_logs(start_date)

        with open(output_file, "w") as f:
            f.write("timestamp,path,wallet_id,amount,is_valid,client_ip,error\n")
            for log in logs:
                f.write(
                    f"{log.get('timestamp','')},"
                    f"{log.get('path','')},"
                    f"{log.get('wallet_id','')},"
                    f"{log.get('amount','')},"
                    f"{log.get('is_valid','')},"
                    f"{log.get('client_ip','')},"
                    f"{log.get('error','')}\n"
                )

    def export_to_json(self, output_file: str, start_date: Optional[str] = None):
        """Export logs to JSON format.

        Args:
            output_file: Output file path
            start_date: Start date for filtering (ISO format)
        """
        logs = self._read_logs(start_date)

        with open(output_file, "w") as f:
            json.dump(logs, f, indent=2)

    def _read_logs(self, start_date: Optional[str] = None) -> list:
        """Read logs from file.

        Args:
            start_date: Start date for filtering

        Returns:
            list: List of log entries
        """
        log_file = os.path.join(self.log_dir, "payments.log")
        if not os.path.exists(log_file):
            return []

        logs = []
        with open(log_file, "r") as f:
            for line in f:
                try:
                    log = json.loads(line.strip())
                    if start_date is None or log.get("timestamp", "") >= start_date:
                        logs.append(log)
                except json.JSONDecodeError:
                    continue

        return logs
