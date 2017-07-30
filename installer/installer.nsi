Name "audio-visualizer-screenlet"
Outfile "avs-..-x64-net_installer.exe"
InstallDir "$PROGRAMFILES64"
ShowInstDetails show

!include "MUI2.nsh"
!include "x64.nsh"
!define MUI_INSTFILESPAGE_COLORS "FFFFFF 012456"
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

#######
Section

Var /GLOBAL PYTHON
StrCpy $PYTHON "$LOCALAPPDATA\$(^Name)\miniconda\envs\py35\pythonw.exe"
StrCpy $INSTDIR "$INSTDIR\$(^Name)"
 
SetOutPath $INSTDIR
File /r "..\*.*"
CreateShortCut "$DESKTOP\$(^Name).lnk" "$PYTHON" "avs\avs.py" "$INSTDIR\avs.ico"
${DisableX64FSRedirection}
nsExec::ExecToLog 'powershell -ExecutionPolicy Bypass -File "$INSTDIR\setup.ps1"'
${EnableX64FSRedirection}
 
SectionEnd