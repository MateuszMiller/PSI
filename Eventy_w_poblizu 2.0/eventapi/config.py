"""A module providing configuration variables."""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict as SettingsConfigDict


class BaseConfig(BaseSettings):
    """A class containing base settings configuration."""
    model_config = SettingsConfigDict(extra="ignore")


class AppConfig(BaseConfig):
    """A class containing app's configuration."""
    DB_HOST: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None


config = AppConfig()