$Title = "audio-visualizer-screenlet"
$TempDir = [System.IO.Path]::GetTempPath()
$LocalAppData = [Environment]::GetFolderPath('LocalApplicationData')
$Prefix = "$LocalAppData\$Title\miniconda"
$MinicondaInstaller = "$TempDir\miniconda.exe"
$ScriptName = $MyInvocation.MyCommand.Name

"[$ScriptName] Downloading Miniconda..."
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe `
    -OutFile $MinicondaInstaller

"[$ScriptName] Installing Miniconda..."
& $MinicondaInstaller /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 `
    /S /D=$Prefix | out-null
rm $MinicondaInstaller

"[$ScriptName] Activating root environment..."
$env:Path = "$Prefix;$Prefix\Scripts;" + $env:Path

"[$ScriptName] Installing dependencies from repositories..."
conda install --yes --json numpy pywin32 scipy
pip install pyfftw pyqt5 vispy watchdog

if (pip show vispy | out-string -stream | select-string "Version: 0.4.0") {
    "[$ScriptName] Patching Vispy 0.4.0..."
    wget https://github.com/vispy/vispy/raw/515c66497ce4e76f917acb6a344e9ff49ae72898/vispy/app/backends/_qt.py `
        -OutFile $Prefix\Lib\site-packages\vispy\app\backends\_qt.py
}

"[$ScriptName] Installing extended PyAudio with PortAudio..."
wget https://github.com/intxcc/pyaudio_portaudio/releases/download/1.0c/Windows.Installer.Python.3.5.PyAudio.0.2.7.amd64.exe `
    -OutFile $TempDir\pp.exe
wget http://www.7-zip.org/a/7za920.zip -OutFile $TempDir\7z.zip
Expand-Archive -Path $TempDir\7z.zip -DestinationPath $TempDir\7z
& $TempDir\7z\7za.exe e -o"$Prefix\Lib\site-packages" $TempDir\pp.exe
rm $TempDir\pp.exe

"[$ScriptName] Removing unused packages and caches..."
conda clean --yes --all
