#!/usr/bin/env bash
set -euo pipefail

API_URL="${1:-https://friendly-guide-jj7g669x6qpp2p6qr-8000.app.github.dev/}"
WEB_URL="${2:-https://friendly-guide-jj7g669x6qpp2p6qr-3000.app.github.dev/}"

echo "==> API: $API_URL/health"
curl -fsS "$API_URL/health" && echo

echo "==> WEB: $WEB_URL"
curl -fsS "$WEB_URL" >/dev/null && echo "WEB OK"
