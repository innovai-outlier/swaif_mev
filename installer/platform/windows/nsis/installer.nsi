!define APPNAME "SWAIF MEV"
!ifndef VERSION
  !define VERSION "0.1.0"
!endif
!ifndef OUTPUTDIR
  !define OUTPUTDIR "dist/installers"
!endif

OutFile "${OUTPUTDIR}\\swaif-mev-${VERSION}-setup.exe"
InstallDir "$PROGRAMFILES\\SwaifMev"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "*"
SectionEnd
