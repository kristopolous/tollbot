"""Custom log formatters for tollbot."""
import json
from logging import Formatter


class JsonFormatter(Formatter):
    """JSON log formatter."""

    def format(self, record):
        """Format log record as JSON.

        Args:
            record: Log record

        Returns:
            str: JSON formatted log entry
        """
        # If message is already JSON, use it directly
        message = record.getMessage()
        try:
            # Try to parse as JSON
            json.loads(message)
            return message
        except json.JSONDecodeError:
            # Not JSON, create our own structure
            log_entry = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "logger": record.name,
                "message": message,
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }

            if record.exc_info:
                log_entry["exception"] = self.formatException(record.exc_info)

            return json.dumps(log_entry)
