"""Application configuration and startup validation."""
from functools import lru_cache
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_WEAK_SECRET_KEYS = {
    "",
    "changeme",
    "change-me",
    "secret",
    "default",
    "your-secret-key",
    "your-secret-key-change-in-production",
    "dev-secret-key",
}


def _validate_secret_strength(secret: str) -> str:
    cleaned = secret.strip()
    if cleaned.lower() in _WEAK_SECRET_KEYS:
        raise ValueError("JWT secret must not use placeholder or weak default values")
    if len(cleaned) < 32:
        raise ValueError("JWT secret must be at least 32 characters long")

    classes = [
        any(c.islower() for c in cleaned),
        any(c.isupper() for c in cleaned),
        any(c.isdigit() for c in cleaned),
        any(not c.isalnum() for c in cleaned),
    ]
    if sum(classes) < 3:
        raise ValueError(
            "JWT secret must include at least 3 character classes (upper/lower/digits/symbols)"
        )
    return cleaned


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(extra="ignore")

    jwt_secret_key: str = Field(
        validation_alias=AliasChoices("JWT_SECRET_KEY", "SECRET_KEY"),
        description="Secret used to sign JWT access tokens",
    )

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        """Enforce strong JWT signing keys for customer deployments."""
        return _validate_secret_strength(value)


@lru_cache
def get_settings() -> Settings:
    """Load and validate settings from environment."""
    return Settings()


def assert_configuration_is_valid() -> None:
    """Raise if required settings are missing or weak."""
    get_settings()
