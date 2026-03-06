import os
import socket
import subprocess
import textwrap
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.mark.integration
def test_onprem_smoke_api_db_redis_web(tmp_path: Path):
    api_port = _free_port()
    web_port = _free_port()
    redis_port = _free_port()

    redis_proc = None
    if subprocess.run(["bash", "-lc", "command -v redis-server"], capture_output=True).returncode == 0:
        redis_proc = subprocess.Popen(
            ["redis-server", "--port", str(redis_port), "--save", "", "--appendonly", "no"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    api_script = tmp_path / "api_service.py"
    api_script.write_text(
        textwrap.dedent(
            f"""
            import os, sqlite3
            from http.server import BaseHTTPRequestHandler, HTTPServer
            import redis

            db_path = os.environ['SMOKE_DB_PATH']
            conn = sqlite3.connect(db_path)
            conn.execute('create table if not exists smoke_runs (id integer primary key, ok integer not null)')
            conn.execute('insert into smoke_runs (ok) values (1)')
            conn.commit()
            conn.close()

            redis.from_url(os.environ['REDIS_URL']).ping()

            class Handler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/health':
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(b'{{"status":"ok"}}')
                    else:
                        self.send_response(404)
                        self.end_headers()

            HTTPServer(('0.0.0.0', int(os.environ['API_PORT'])), Handler).serve_forever()
            """
        )
    )

    web_script = tmp_path / "web_service.py"
    web_script.write_text(
        textwrap.dedent(
            """
            import os
            from http.server import BaseHTTPRequestHandler, HTTPServer

            class Handler(BaseHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'web-ok')

            HTTPServer(('0.0.0.0', int(os.environ['WEB_PORT'])), Handler).serve_forever()
            """
        )
    )

    env_file = tmp_path / ".env.onprem"
    env_file.write_text(f"API_PORT={api_port}\nWEB_PORT={web_port}\n")

    env = os.environ.copy()
    env.update(
        {
            "ONPREM_ENV_FILE": str(env_file),
            "ONPREM_RUNTIME_DIR": str(tmp_path / "runtime"),
            "API_PORT": str(api_port),
            "WEB_PORT": str(web_port),
            "SMOKE_DB_PATH": str(tmp_path / "smoke.db"),
            "REDIS_URL": f"redis://localhost:{redis_port}/0",
            "API_START_CMD": f"python {api_script}",
            "WEB_START_CMD": f"python {web_script}",
            "WORKER_START_CMD": "sleep 120",
        }
    )

    try:
        if redis_proc is None:
            pytest.skip("redis-server is required for on-prem smoke test")

        subprocess.run(["bash", "scripts/onprem/up.sh"], cwd=ROOT, check=True, env=env)
        health = subprocess.run(
            ["bash", "scripts/health.sh", f"http://localhost:{api_port}", f"http://localhost:{web_port}"],
            cwd=ROOT,
            check=True,
            env=env,
            capture_output=True,
            text=True,
        )
        assert "WEB OK" in health.stdout
        assert (tmp_path / "smoke.db").exists()
    finally:
        subprocess.run(["bash", "scripts/onprem/down.sh"], cwd=ROOT, env=env, check=False)
        if redis_proc is not None:
            redis_proc.terminate()
            redis_proc.wait(timeout=5)
