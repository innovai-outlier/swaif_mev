param(
  [Parameter(Mandatory = $true)][string]$InstallDir,
  [int]$ApiPort = 8000,
  [int]$WebPort = 3000
)

$ErrorActionPreference = 'Stop'

$apiCmd = "cmd /c cd /d $InstallDir\\services\\api && uvicorn app.main:app --host 0.0.0.0 --port $ApiPort"
$webCmd = "cmd /c cd /d $InstallDir\\services\\web && npm run start -- --port $WebPort"
$workerCmd = "cmd /c cd /d $InstallDir\\services\\worker && python -m app.main"

sc.exe create SwaifMevApi start= auto binPath= $apiCmd | Out-Null
sc.exe create SwaifMevWeb start= auto binPath= $webCmd | Out-Null
sc.exe create SwaifMevWorker start= auto binPath= $workerCmd | Out-Null

sc.exe start SwaifMevApi | Out-Null
sc.exe start SwaifMevWeb | Out-Null
sc.exe start SwaifMevWorker | Out-Null
