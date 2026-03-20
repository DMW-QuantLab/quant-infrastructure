"""
API key management — loads from environment only.
Never from config files. Never hardcoded.
"""
from __future__ import annotations
from dataclasses import dataclass
from src.utils.config_loader import require_env


@dataclass(frozen=True)
class PolymarketCredentials:
    private_key: str
    api_key: str
    api_secret: str
    passphrase: str

    @classmethod
    def from_env(cls) -> "PolymarketCredentials":
        return cls(
            private_key = require_env("POLY_PRIVATE_KEY"),
            api_key     = require_env("POLY_API_KEY"),
            api_secret  = require_env("POLY_API_SECRET"),
            passphrase  = require_env("POLY_PASSPHRASE"),
        )


@dataclass(frozen=True)
class AnthropicCredentials:
    api_key: str

    @classmethod
    def from_env(cls) -> "AnthropicCredentials":
        return cls(api_key=require_env("ANTHROPIC_API_KEY"))

