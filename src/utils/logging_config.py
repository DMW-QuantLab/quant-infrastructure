"""
Structured logging configuration shared across all bots.
"""
import logging
import sys


def configure_logging(level: str = "INFO", service: str = "quant-lab") -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
        format=f"%(asctime)s [{service}] %(levelname)s %(name)s — %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

