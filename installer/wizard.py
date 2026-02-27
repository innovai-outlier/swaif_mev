#!/usr/bin/env python3
"""Interactive installer wizard for on-prem runtime bootstrap."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import socket
import sys
from pathlib import Path
from string import Template

PROFILES = ("local", "staging", "production")


class WizardError(RuntimeError):
    pass


def ask(prompt: str, default: str | None = None, secret: bool = False) -> str:
    suffix = f" [{default}]" if default else ""
    text = f"{prompt}{suffix}: "
    while True:
        value = getpass.getpass(text) if secret else input(text)
        value = value.strip()
        if not value and default is not None:
            return default
        if value:
            return value
        print("Value required.")


def ask_int(prompt: str, default: int) -> int:
    while True:
        raw = ask(prompt, str(default))
        try:
            value = int(raw)
            if value < 1 or value > 65535:
                raise ValueError
            return value
        except ValueError:
            print("Provide a valid TCP port between 1 and 65535.")


def check_tcp(host: str, port: int, timeout: float = 3.0) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, "ok"
    except OSError as exc:
        return False, str(exc)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SWAIF MEV installer wizard")
    parser.add_argument("--output-dir", default=".runtime/install", help="Directory for generated runtime configs")
    parser.add_argument("--profile", choices=PROFILES, default="production", help="Environment profile")
    parser.add_argument("--non-interactive-json", help="Path to JSON input with wizard values")
    parser.add_argument("--skip-connectivity-check", action="store_true", help="Skip DB/Redis endpoint checks")
    return parser.parse_args()


def load_template(name: str) -> Template:
    template_path = Path(__file__).parent / "templates" / "env" / name
    return Template(template_path.read_text(encoding="utf-8"))


def build_context(values: dict[str, str]) -> dict[str, str]:
    return {
        "APP_ENV": values["profile"],
        "DB_HOST": values["db_host"],
        "DB_PORT": str(values["db_port"]),
        "POSTGRES_DB": values["db_name"],
        "POSTGRES_USER": values["db_user"],
        "POSTGRES_PASSWORD": values["db_password"],
        "REDIS_HOST": values["redis_host"],
        "REDIS_PORT": str(values["redis_port"]),
        "API_PORT": str(values["api_port"]),
        "WEB_PORT": str(values["web_port"]),
        "WORKER_CONCURRENCY": str(values["worker_concurrency"]),
        "ADMIN_EMAIL": values["admin_email"],
        "ADMIN_PASSWORD": values["admin_password"],
        "INSTALL_DIR": values["install_dir"],
        "DATABASE_URL": (
            f"postgresql+psycopg://{values['db_user']}:{values['db_password']}"
            f"@{values['db_host']}:{values['db_port']}/{values['db_name']}"
        ),
        "REDIS_URL": f"redis://{values['redis_host']}:{values['redis_port']}",
        "NEXT_PUBLIC_API_BASE_URL": f"http://localhost:{values['api_port']}",
    }


def gather_interactive(profile: str) -> dict[str, str]:
    print("== SWAIF MEV setup wizard ==")
    install_dir = ask("Install directory", "/opt/swaif_mev")
    db_host = ask("Database host", "localhost")
    db_port = ask_int("Database port", 5432)
    db_name = ask("Database name", "mevdb")
    db_user = ask("Database user", "mevuser")
    db_password = ask("Database password", "mevpass", secret=True)
    redis_host = ask("Redis host", "localhost")
    redis_port = ask_int("Redis port", 6379)
    api_port = ask_int("API port", 8000)
    web_port = ask_int("Web port", 3000)
    worker_concurrency = ask_int("Worker concurrency", 2)
    admin_email = ask("Admin bootstrap email", "admin@example.com")
    admin_password = ask("Admin bootstrap password", "changeme", secret=True)

    return {
        "profile": profile,
        "install_dir": install_dir,
        "db_host": db_host,
        "db_port": db_port,
        "db_name": db_name,
        "db_user": db_user,
        "db_password": db_password,
        "redis_host": redis_host,
        "redis_port": redis_port,
        "api_port": api_port,
        "web_port": web_port,
        "worker_concurrency": worker_concurrency,
        "admin_email": admin_email,
        "admin_password": admin_password,
    }


def gather_non_interactive(path: str) -> dict[str, str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    required = [
        "profile",
        "install_dir",
        "db_host",
        "db_port",
        "db_name",
        "db_user",
        "db_password",
        "redis_host",
        "redis_port",
        "api_port",
        "web_port",
        "worker_concurrency",
        "admin_email",
        "admin_password",
    ]
    missing = [key for key in required if key not in payload]
    if missing:
        raise WizardError(f"missing keys in non-interactive json: {', '.join(missing)}")
    return payload


def write_env_files(out_dir: Path, context: dict[str, str]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    mapping = {
        "api.env": "api.env.tmpl",
        "web.env": "web.env.tmpl",
        "worker.env": "worker.env.tmpl",
    }
    for out_name, tmpl_name in mapping.items():
        content = load_template(tmpl_name).safe_substitute(context)
        out_file = out_dir / out_name
        out_file.write_text(content, encoding="utf-8")
        os.chmod(out_file, 0o600)


def validate_connectivity(values: dict[str, str]) -> None:
    targets = [
        ("database", values["db_host"], int(values["db_port"])),
        ("redis", values["redis_host"], int(values["redis_port"])),
    ]
    for label, host, port in targets:
        ok, detail = check_tcp(host, port)
        if not ok:
            raise WizardError(f"connectivity check failed for {label} ({host}:{port}): {detail}")
        print(f"Connectivity check passed: {label} ({host}:{port})")


def write_manifest(out_dir: Path, values: dict[str, str]) -> None:
    manifest_path = out_dir / "install-manifest.json"
    manifest_path.write_text(json.dumps(values, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        values = (
            gather_non_interactive(args.non_interactive_json)
            if args.non_interactive_json
            else gather_interactive(args.profile)
        )
        out_dir = Path(args.output_dir)
        if not args.skip_connectivity_check:
            validate_connectivity(values)
        context = build_context(values)
        write_env_files(out_dir, context)
        write_manifest(out_dir, values)
        print(f"Generated runtime config files in {out_dir}")
        return 0
    except WizardError as exc:
        print(f"[wizard] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
