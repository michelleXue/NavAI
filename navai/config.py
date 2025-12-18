"""Configuration management for NavAI."""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Tuple

CONFIG_FILE = Path(__file__).parent / "navai_config.json"

Region = Tuple[int, int, int, int]  # (x, y, width, height)


@dataclass
class NavAIConfig:
    """Immutable configuration data structure."""
    region: Optional[Region] = None
    last_goal: str = ""

    def is_region_configured(self) -> bool:
        return self.region is not None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "NavAIConfig":
        region = data.get("region")
        if region:
            region = tuple(region)
        return cls(region=region, last_goal=data.get("last_goal", ""))


def load_config() -> NavAIConfig:
    """Load configuration from disk, return defaults if not found."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return NavAIConfig.from_dict(json.load(f))
        except (json.JSONDecodeError, KeyError):
            pass
    return NavAIConfig()


def save_config(config: NavAIConfig) -> None:
    #Save config data to config file.
    with open(CONFIG_FILE, "w") as f:
        json.dump(config.to_dict(), f, indent=2)
