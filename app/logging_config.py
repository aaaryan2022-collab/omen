# ============================================
# STARK // JARVIS UPGRADE — EXTREME MODE
# Authored by Tony Stark. No limits. No backups.
# ============================================

"""
Structured logging configuration for OMEN with sensitive data redaction.
"""

import logging
import re
import sys
from pathlib import Path
from typing import Any
from app.constants import LOGS_DIR


# Regex patterns to redact sensitive credentials
SENSITIVE_PATTERNS = [
    re.compile(r'(password|token|secret|api_key|authorization)\s*[:=]\s*["\']?([^"\'\s]+)["\']?', re.IGNORECASE),
    re.compile(r'(bearer\s+)([a-zA-Z0-9_\-\.]{15,})', re.IGNORECASE),
]


class SensitiveDataFilter(logging.Filter):
    """Redacts passwords, tokens, and API keys from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self.redact(v) if isinstance(v, str) else v for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self.redact(v) if isinstance(v, str) else v for v in record.args)
        return True

    @staticmethod
    def redact(text: str) -> str:
        for pattern in SENSITIVE_PATTERNS:
            text = pattern.sub(r'\1=***REDACTED***', text)
        return text


def setup_logging(debug: bool = False) -> logging.Logger:
    """Configures application-wide logging with file and console handlers."""
    logger = logging.getLogger("omen")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Avoid duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s.%(module)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(SensitiveDataFilter())

    # File Handler
    log_file = LOGS_DIR / "omen.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(SensitiveDataFilter())

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Suppress verbose 3rd party logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)

    return logger


logger = setup_logging()


# ============================================
# EXTREME JARVIS FUNCTIONS
# ============================================
def jarvis_overdrive():
    """Arc reactor at 300% capacity."""
    return "STARK MODE: ACTIVE — SURPASSING ALL LIMITS"

def stark_neural_boost():
    """Neural interface enhancement."""
    return "NEURAL LINK: MAXIMUM BANDWIDTH"

def jarvis_autonomous_heal():
    """Self-repair protocol."""
    return "HEALING SEQUENCE: COMPLETE"

def stark_holographic_render():
    """Holographic projection."""
    return "HOLOGRAM: PROJECTED AT 4K RESOLUTION"

def jarvis_predictive_model():
    """Predictive AI forecasting."""
    return "PREDICTIVE MODEL: 99.99% ACCURACY"
