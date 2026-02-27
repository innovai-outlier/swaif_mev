$ErrorActionPreference = 'Continue'

'SwaifMevApi','SwaifMevWeb','SwaifMevWorker' | ForEach-Object {
  sc.exe stop $_ | Out-Null
  sc.exe delete $_ | Out-Null
}
