import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.installer
def test_onprem_installer_lifecycle(tmp_path: Path):
    env_file = tmp_path / ".env.onprem"
    runtime_dir = tmp_path / "runtime"

    env = os.environ.copy()
    env.update(
        {
            "ONPREM_ENV_FILE": str(env_file),
            "ONPREM_RUNTIME_DIR": str(runtime_dir),
            "API_START_CMD": "sleep 120",
            "WEB_START_CMD": "sleep 120",
            "WORKER_START_CMD": "sleep 120",
        }
    )

    bootstrap = subprocess.run(
        ["bash", "scripts/onprem/bootstrap.sh"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert env_file.exists()
    assert "Pronto" in bootstrap.stdout

    subprocess.run(["bash", "scripts/onprem/up.sh"], cwd=ROOT, env=env, check=True)
    status = subprocess.run(
        ["bash", "scripts/onprem/status.sh"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "running" in status.stdout

    subprocess.run(["bash", "scripts/onprem/down.sh"], cwd=ROOT, env=env, check=True)

    # Uninstall validation: artifacts can be removed cleanly after shutdown.
    if runtime_dir.exists():
        for p in runtime_dir.rglob("*"):
            if p.is_file():
                p.unlink()
        for p in sorted(runtime_dir.rglob("*"), reverse=True):
            if p.is_dir():
                p.rmdir()
        runtime_dir.rmdir()
    env_file.unlink(missing_ok=True)

    assert not runtime_dir.exists()
    assert not env_file.exists()
