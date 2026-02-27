param(
  [string]$InstallDir = 'C:\\Program Files\\SwaifMev'
)

$ErrorActionPreference = 'Continue'

& "$PSScriptRoot/../templates/services/windows/unregister-services.ps1"
if (Test-Path $InstallDir) {
  Remove-Item -Recurse -Force $InstallDir
}
Write-Host "Uninstall complete for $InstallDir"
