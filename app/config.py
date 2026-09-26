"""Application configuration loaded from environment variables."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from environs import Env

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(slots=True)
class Config:
    token: str
    default_timezone: str
    database_url: str


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        token=env.str("BOT_TOKEN"),
        default_timezone=env.str("DEFAULT_TIMEZONE", "Asia/Tashkent"),
        database_url=env.str(
            "DATABASE_URL", "sqlite+aiosqlite:///skeddy.db"
        ),
    )
