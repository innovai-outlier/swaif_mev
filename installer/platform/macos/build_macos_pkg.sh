#!/usr/bin/env bash
set -euo pipefail

VERSION="0.1.0"
OUTPUT_DIR="dist/installers"
INSTALL_LOCATION="/Applications/swaif_mev"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --install-location) INSTALL_LOCATION="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

mkdir -p "$OUTPUT_DIR"
PKGROOT="$(mktemp -d)"
trap 'rm -rf "$PKGROOT"' EXIT

mkdir -p "$PKGROOT$INSTALL_LOCATION"
rsync -a --exclude '.git' --exclude 'dist' ./ "$PKGROOT$INSTALL_LOCATION/"

if command -v pkgbuild >/dev/null 2>&1; then
  pkgbuild --root "$PKGROOT" --identifier com.swaif.mev --version "$VERSION" \
    "$OUTPUT_DIR/swaif-mev-${VERSION}.pkg"
else
  tar -C "$PKGROOT" -czf "$OUTPUT_DIR/swaif-mev-${VERSION}-macos.tar.gz" .
fi
