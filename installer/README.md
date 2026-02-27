# Installer Packaging Layer

This directory provides a cross-platform packaging and installation framework for the SWAIF MEV stack.

## What it includes

- **Platform packagers**
  - Linux: `installer/platform/linux/build_linux_packages.sh` (fpm-based with tarball fallback)
  - macOS: `installer/platform/macos/build_macos_pkg.sh` (`pkgbuild`)
  - Windows: `installer/platform/windows/build_windows_installers.ps1` (WiX/NSIS hooks)
- **Interactive setup wizard**
  - `installer/wizard.py` asks for install path, DB/Redis endpoints, service ports, admin bootstrap credentials, and runtime profile.
- **Runtime config generation**
  - Generates `api.env`, `web.env`, and `worker.env` from templates.
  - Validates database/redis endpoint connectivity before finishing.
- **Service registration + uninstall assets**
  - systemd service unit templates
  - launchd plist templates
  - Windows service registration scripts
  - uninstall scripts for Linux/macOS/Windows

## Typical flow

```bash
python3 installer/wizard.py --output-dir "$PWD/.runtime/install" --profile production
bash installer/platform/linux/build_linux_packages.sh --version 0.1.0 --output-dir dist/installers
```

## CI outputs

The workflow `.github/workflows/installers.yml` builds versioned installers and writes checksums under `dist/installers/`.
