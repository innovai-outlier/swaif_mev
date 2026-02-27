param(
  [string]$Version = '0.1.0',
  [string]$OutputDir = 'dist/installers'
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$wix = Get-Command candle.exe -ErrorAction SilentlyContinue
$nsis = Get-Command makensis.exe -ErrorAction SilentlyContinue

if ($wix) {
  candle.exe installer/platform/windows/wix/Product.wxs -dVersion=$Version -out "$OutputDir/"
  light.exe "$OutputDir/Product.wixobj" -out "$OutputDir/swaif-mev-$Version.msi"
}

if ($nsis) {
  makensis.exe /DVERSION=$Version /DOUTPUTDIR=$OutputDir installer/platform/windows/nsis/installer.nsi
}

if (-not $wix -and -not $nsis) {
  Compress-Archive -Path * -DestinationPath "$OutputDir/swaif-mev-$Version-windows.zip" -Force
}
