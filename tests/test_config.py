"""Settings are read once from the environment and checked before anything starts (spec:
Configuration from the environment)."""

import dataclasses
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from rollcall.config import ConfigError, Settings, load_settings

SECRET = "s3cret-" + "x" * 25  # 32 characters
DB_PASSWORD = "db-pa55word"


def valid_env(**overrides):
    env = {
        "DATABASE_URL": f"postgresql://rollcall:{DB_PASSWORD}@db:5432/rollcall",
        "SECRET_KEY": SECRET,
        "SHOP_TIMEZONE": "America/Chicago",
    }
    env.update(overrides)
    return {key: value for key, value in env.items() if value is not None}


def error_for(**overrides) -> str:
    with pytest.raises(ConfigError) as caught:
        load_settings(valid_env(**overrides))
    return str(caught.value)


# --- valid settings -------------------------------------------------------------------------


def test_valid_environment_loads():
    settings = load_settings(valid_env(DATA_DIR="/srv/rollcall", LOG_LEVEL="WARNING"))
    assert isinstance(settings, Settings)
    assert settings.database_url == f"postgresql://rollcall:{DB_PASSWORD}@db:5432/rollcall"
    assert settings.secret_key == SECRET
    assert settings.shop_timezone == ZoneInfo("America/Chicago")
    assert settings.data_dir == Path("/srv/rollcall")
    assert settings.log_level == "WARNING"


def test_defaults():
    settings = load_settings(valid_env())
    assert settings.data_dir == Path("/data")
    assert settings.log_level == "INFO"
    assert settings.db_pool_size == 10
    assert settings.mockups is False


def test_settings_cannot_be_changed_after_loading():
    settings = load_settings(valid_env())
    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.db_pool_size = 20


def test_settings_never_show_secrets_when_printed():
    shown = repr(load_settings(valid_env()))
    assert SECRET not in shown
    assert DB_PASSWORD not in shown


# --- DATABASE_URL ---------------------------------------------------------------------------


def test_missing_database_url_is_named():
    assert "DATABASE_URL" in error_for(DATABASE_URL=None)


def test_empty_value_counts_as_missing():
    assert "DATABASE_URL" in error_for(DATABASE_URL="  ")


def test_database_url_must_be_postgresql_without_echoing_it():
    message = error_for(DATABASE_URL=f"mysql://root:{DB_PASSWORD}@db/rollcall")
    assert "DATABASE_URL" in message
    assert DB_PASSWORD not in message


def test_postgres_scheme_alias_is_accepted():
    settings = load_settings(valid_env(DATABASE_URL="postgres://u:p@db/rollcall"))
    assert settings.database_url == "postgres://u:p@db/rollcall"


# --- SECRET_KEY -----------------------------------------------------------------------------


def test_missing_secret_key_is_named():
    assert "SECRET_KEY" in error_for(SECRET_KEY=None)


def test_secret_key_of_31_characters_is_too_short_and_not_echoed():
    short = "k" * 31
    message = error_for(SECRET_KEY=short)
    assert "SECRET_KEY" in message
    assert "too short" in message
    assert short not in message


def test_secret_key_of_32_characters_is_accepted():
    assert load_settings(valid_env(SECRET_KEY="k" * 32)).secret_key == "k" * 32


# --- SHOP_TIMEZONE --------------------------------------------------------------------------


def test_missing_time_zone_is_named():
    assert "SHOP_TIMEZONE" in error_for(SHOP_TIMEZONE=None)


@pytest.mark.parametrize("zone", ["Mars/Base", "Chicago", "../../etc/passwd"])
def test_unknown_time_zone_is_named(zone):
    assert "SHOP_TIMEZONE" in error_for(SHOP_TIMEZONE=zone)


# --- optional settings ----------------------------------------------------------------------


@pytest.mark.parametrize("size", ["0", "51", "-1", "ten", "2.5"])
def test_pool_size_out_of_range_is_rejected(size):
    assert "DB_POOL_SIZE" in error_for(DB_POOL_SIZE=size)


@pytest.mark.parametrize("size", ["1", "50"])
def test_pool_size_limits_are_accepted(size):
    assert load_settings(valid_env(DB_POOL_SIZE=size)).db_pool_size == int(size)


def test_log_level_is_case_insensitive():
    assert load_settings(valid_env(LOG_LEVEL="debug")).log_level == "DEBUG"


def test_unknown_log_level_is_rejected():
    assert "LOG_LEVEL" in error_for(LOG_LEVEL="LOUD")


def test_data_dir_must_be_absolute():
    assert "DATA_DIR" in error_for(DATA_DIR="data")


# --- several problems at once ---------------------------------------------------------------


def test_every_problem_is_reported_together():
    message = error_for(DATABASE_URL=None, SECRET_KEY="short", SHOP_TIMEZONE="Nowhere")
    assert "DATABASE_URL" in message
    assert "SECRET_KEY" in message
    assert "SHOP_TIMEZONE" in message


# --- mockup gallery (spec: Mockup gallery) ---------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"), [("on", True), ("off", False), ("ON", True), ("", False)]
)
def test_mockups_setting(text, expected):
    assert load_settings(valid_env(MOCKUPS=text)).mockups is expected


@pytest.mark.parametrize("text", ["maybe", "yes", "1", "true"])
def test_mockups_setting_rejects_anything_but_on_or_off(text):
    message = error_for(MOCKUPS=text)
    assert "MOCKUPS must be on or off" in message
