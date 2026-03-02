#!/usr/bin/env bash
set -euo pipefail

API_URL="${1:-http://localhost:8000}"
WEB_URL="${2:-http://localhost:3000}"

echo "==> API: $API_URL/health"
curl -fsS "$API_URL/health" && echo

echo "==> WEB: $WEB_URL"
curl -fsS "$WEB_URL" >/dev/null && echo "WEB OK"
