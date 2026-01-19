"""Configuration module for loading environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration."""

    pchome_ecwebsess: str
    slack_webhook_url: str | None
    db_path: Path

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment variables."""
        # Load .env file from project root
        project_root = Path(__file__).parent.parent
        load_dotenv(project_root / ".env")

        ecwebsess = os.getenv("PCHOME_ECWEBSESS")
        if not ecwebsess:
            raise ValueError(
                "PCHOME_ECWEBSESS environment variable is required. "
                "See docs/COOKIE_GUIDE.md for instructions."
            )

        return cls(
            pchome_ecwebsess=ecwebsess,
            slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
            db_path=project_root / "db" / "prices.db",
        )
