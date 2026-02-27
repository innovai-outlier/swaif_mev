"""Command-line configuration validation for deployment environments."""
from app.config import assert_configuration_is_valid


def main() -> int:
    """Validate configuration and return process exit code."""
    try:
        assert_configuration_is_valid()
    except Exception as exc:  # deliberate fail-fast for CLI use
        print(f"Configuration validation failed: {exc}")
        return 1

    print("Configuration validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
