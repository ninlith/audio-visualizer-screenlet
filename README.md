# audio-visualizer-screenlet
Visualizes sound card output (PulseAudio monitor or WASAPI loopback).

![screenshot](screenshot.png?raw=true)

## Installation
###Debian Stretch
git clone https://github.com/ninlith/audio-visualizer-screenlet.git
sudo apt-get install python3-numpy python3-pyfftw python3-pyqt5 python3-scipy \
python3-vispy python3-watchdog python3-xlib

###Windows (64-bit)
Use the [installer](https://github.com/ninlith/audio-visualizer-screenlet/releases/).

## Controls
| Binding | Action |
| ------- | ------ |
| Mouse Wheel | adjust sensitivity |

## Usage
```
usage: avs.py [-h] [-d]

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  enable DEBUG logging level
```
## Configuration
`settings.ini` file inside `audio-visualizer-screenlet` folder inside `%LOCALAPPDATA%` (Windows) or `$XDG_CONFIG_HOME` or `$HOME/.config`.

## License
GNU GPLv3
