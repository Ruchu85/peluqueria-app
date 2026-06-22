from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Google Places
    google_places_api_key: str = Field(default="")

    # Hunter.io
    hunter_api_key: str = Field(default="")

    # Brevo (email sending)
    brevo_api_key: str = Field(default="")

    # SMTP fallback
    smtp_host: str = Field(default="")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")

    # Sender identity
    sender_name: str = Field(default="Tu Nombre")
    sender_email: str = Field(default="")
    sender_reply_to: str = Field(default="")

    # WhatsApp outreach
    landing_url: str = Field(default="https://landing-gold-kappa-38.vercel.app")

    # Behavior
    # IMPORTANT: dry_run=True is the hardcoded default.
    # Emails are NEVER sent unless DRY_RUN=false is set explicitly in .env.
    dry_run: bool = Field(default=True)
    daily_email_limit: int = Field(default=50)
    request_delay_ms: int = Field(default=1500)
    max_retries: int = Field(default=3)

    # Storage
    database_url: str = Field(default="sqlite:///data/leads.db")

    # Logging
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/prospect.log")

    def google_api_configured(self) -> bool:
        return bool(self.google_places_api_key)

    def email_sending_configured(self) -> bool:
        return bool(self.brevo_api_key or (self.smtp_host and self.smtp_user))

    def assert_not_dry_run(self) -> None:
        if self.dry_run:
            raise RuntimeError(
                "DRY_RUN=true — los emails no se enviarán. "
                "Establece DRY_RUN=false en .env para habilitar el envío real."
            )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
