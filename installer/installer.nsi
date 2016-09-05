Name "audio-visualizer-screenlet"
Outfile "avs-0.1-x64-net_installer.exe"
InstallDir "$PROGRAMFILES64"
ShowInstDetails show

!include "MUI2.nsh"
!define MUI_INSTFILESPAGE_COLORS "FFFFFF 012456"
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

#######
Section

Var /GLOBAL PYTHON
StrCpy $PYTHON "$LOCALAPPDATA\$(^Name)\miniconda\pythonw.exe"
StrCpy $INSTDIR "$INSTDIR\$(^Name)"
 
SetOutPath $INSTDIR
File /r "..\*.*"
CreateShortCut "$DESKTOP\$(^Name).lnk" "$PYTHON" "avs\avs.py" "$INSTDIR\avs.ico"
nsExec::ExecToLog 'powershell -ExecutionPolicy Bypass -File "$INSTDIR\setup.ps1"'
 
SectionEnd