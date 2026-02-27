#!/usr/bin/env bash
set -euo pipefail

VERSION="0.1.0"
OUTPUT_DIR="dist/installers"
INSTALL_PREFIX="/opt/swaif_mev"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --install-prefix) INSTALL_PREFIX="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

mkdir -p "$OUTPUT_DIR"
STAGING="$(mktemp -d)"
trap 'rm -rf "$STAGING"' EXIT

mkdir -p "$STAGING$INSTALL_PREFIX"
rsync -a --exclude '.git' --exclude 'dist' ./ "$STAGING$INSTALL_PREFIX/"

if command -v fpm >/dev/null 2>&1; then
  fpm -s dir -t deb -n swaif-mev -v "$VERSION" -C "$STAGING" \
    --prefix / "$INSTALL_PREFIX"="$INSTALL_PREFIX" --package "$OUTPUT_DIR/swaif-mev_${VERSION}_amd64.deb"
  fpm -s dir -t rpm -n swaif-mev -v "$VERSION" -C "$STAGING" \
    --prefix / "$INSTALL_PREFIX"="$INSTALL_PREFIX" --package "$OUTPUT_DIR/swaif-mev-${VERSION}.x86_64.rpm"
else
  tar -C "$STAGING" -czf "$OUTPUT_DIR/swaif-mev-${VERSION}-linux.tar.gz" .
fi
