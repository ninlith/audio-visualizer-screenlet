$Title = "audio-visualizer-screenlet"
$TempDir = [System.IO.Path]::GetTempPath()
$LocalAppData = [Environment]::GetFolderPath('LocalApplicationData')
$ProgramFiles = [Environment]::GetFolderPath('ProgramFiles')
$RootEnv = "$LocalAppData\$Title\miniconda"
$MinicondaInstaller = "$TempDir\miniconda.exe"
$ScriptName = $MyInvocation.MyCommand.Name

"[$ScriptName] Downloading Miniconda..."
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe `
    -OutFile $MinicondaInstaller

"[$ScriptName] Installing Miniconda..."
& $MinicondaInstaller /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 `
    /S /D=$RootEnv | out-null
rm $MinicondaInstaller

"[$ScriptName] Activating root environment..."
$env:Path = "$RootEnv;$RootEnv\Scripts;" + $env:Path

"[$ScriptName] Creating and populating a sub-environment..."
conda env create -f environment.yml

"[$ScriptName] Installing extended PyAudio with PortAudio..."
Expand-Archive -Path "$ProgramFiles\$Title\installer\pyaudio_portaudio_py35.zip" -DestinationPath "$RootEnv\envs\py35\Lib\site-packages"

"[$ScriptName] Removing unused packages and caches..."
conda clean --yes --all
