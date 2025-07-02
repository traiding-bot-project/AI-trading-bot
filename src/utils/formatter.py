"""Custom formatter."""

import logging
import os
import shutil
from datetime import datetime
from typing import Any

import colorama

colorama.init()


class Formatter(logging.Formatter):
    """Custom formatter with dynamic terminal width and clickable file:line."""

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    DATE_FORMAT = "%d/%m/%y %H:%M:%S"

    FORMATS = {
        logging.DEBUG: grey,
        logging.INFO: grey,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: bold_red,
    }

    def get_terminal_width(self, fallback: int = 100) -> int:
        """Get width of the terminal."""
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return fallback

    def format(self, record: Any) -> str:
        """Custom formating for the logs."""
        line_width = self.get_terminal_width()

        timestamp = datetime.fromtimestamp(record.created).strftime(self.DATE_FORMAT)
        server = getattr(record, "server", "GENERIC")
        level = f"{record.levelname:<8}"
        message = record.getMessage()

        prefix = f"[{timestamp}] [{server}] {level} {message}"

        file_path = os.path.relpath(record.pathname)
        file_link = f"{file_path}:{record.lineno}"

        space = max(line_width - len(prefix) - len(file_link), 1)
        formatted = prefix + " " * space + file_link

        color = self.FORMATS.get(record.levelno, "")
        return f"{color}{formatted}{self.reset}"
