"""Email / SMTP settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MessagingSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    email_enabled: bool = Field(default=False, validation_alias="EMAIL_ENABLED")
    email_provider: str = Field(default="noop", validation_alias="EMAIL_PROVIDER")
    email_from: str = Field(
        default="Application <noreply@localhost>",
        validation_alias="EMAIL_FROM",
    )
    email_product_name: str = Field(
        default="Application",
        validation_alias="EMAIL_PRODUCT_NAME",
    )
    email_footer: str | None = Field(default=None, validation_alias="EMAIL_FOOTER")
    app_public_url: str = Field(
        default="http://localhost:3000",
        validation_alias=AliasChoices("APP_PUBLIC_URL", "DASHBOARD_PUBLIC_URL"),
    )
    smtp_host: str = Field(default="localhost", validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    smtp_user: str = Field(default="", validation_alias="SMTP_USER")
    smtp_password: str = Field(default="", validation_alias="SMTP_PASSWORD")
    smtp_starttls: bool = Field(default=True, validation_alias="SMTP_STARTTLS")
    smtp_ssl: bool = Field(default=False, validation_alias="SMTP_SSL")
    smtp_timeout: float = Field(default=30.0, validation_alias="SMTP_TIMEOUT")

@lru_cache
def get_messaging_settings() -> MessagingSettings:
    return MessagingSettings()