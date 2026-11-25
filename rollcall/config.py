"""Settings, read once from the environment and checked before anything starts.

Every problem is collected and reported together, naming the variable but never echoing a
value, because the database URL and the secret key are secrets.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

MIN_SECRET_KEY_LENGTH = 32
POOL_SIZE_RANGE = range(1, 51)
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
DATABASE_SCHEMES = ("postgresql://", "postgres://")


class ConfigError(Exception):
    """One or more settings are missing or invalid. The message lists each problem."""


@dataclass(frozen=True)
class Settings:
    database_url: str = field(repr=False)
    secret_key: str = field(repr=False)
    shop_timezone: ZoneInfo
    data_dir: Path = Path("/data")
    log_level: str = "INFO"
    db_pool_size: int = 10
    mockups: bool = False  # the /mockups gallery of page designs with sample data


def load_settings(env: Mapping[str, str]) -> Settings:
    """Build Settings from an environment mapping (normally os.environ), or raise ConfigError."""
    problems: list[str] = []

    def get(name: str) -> str | None:
        value = env.get(name, "").strip()
        return value or None

    database_url = get("DATABASE_URL")
    if database_url is None:
        problems.append("DATABASE_URL is required")
    elif not database_url.startswith(DATABASE_SCHEMES):
        problems.append("DATABASE_URL must start with postgresql://")

    secret_key = get("SECRET_KEY")
    if secret_key is None:
        problems.append("SECRET_KEY is required")
    elif len(secret_key) < MIN_SECRET_KEY_LENGTH:
        problems.append(f"SECRET_KEY is too short: use at least {MIN_SECRET_KEY_LENGTH} characters")

    zone_name = get("SHOP_TIMEZONE")
    shop_timezone = None
    if zone_name is None:
        problems.append("SHOP_TIMEZONE is required, for example America/Chicago")
    else:
        try:
            shop_timezone = ZoneInfo(zone_name)
        except (ZoneInfoNotFoundError, ValueError):
            problems.append("SHOP_TIMEZONE is not a known time zone, for example America/Chicago")

    data_dir = Path(get("DATA_DIR") or "/data")
    if not data_dir.is_absolute():
        problems.append("DATA_DIR must be an absolute path, for example /data")

    log_level = (get("LOG_LEVEL") or "INFO").upper()
    if log_level not in LOG_LEVELS:
        problems.append(f"LOG_LEVEL must be one of {', '.join(LOG_LEVELS)}")

    pool_size_text = get("DB_POOL_SIZE") or "10"
    db_pool_size = int(pool_size_text) if pool_size_text.lstrip("-").isdigit() else 0
    if db_pool_size not in POOL_SIZE_RANGE:
        problems.append(
            f"DB_POOL_SIZE must be a whole number from {POOL_SIZE_RANGE.start} "
            f"to {POOL_SIZE_RANGE.stop - 1}"
        )

    mockups_text = (get("MOCKUPS") or "off").lower()
    if mockups_text not in ("on", "off"):
        problems.append("MOCKUPS must be on or off")

    if problems:
        raise ConfigError("Rollcall cannot start:\n  - " + "\n  - ".join(problems))

    return Settings(
        database_url=database_url,
        secret_key=secret_key,
        shop_timezone=shop_timezone,
        data_dir=data_dir,
        log_level=log_level,
        db_pool_size=db_pool_size,
        mockups=mockups_text == "on",
    )
