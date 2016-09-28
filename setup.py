#!/usr/bin/env python
from setuptools import setup
import subprocess

try:
    subprocess.call(['conda','install','--file','requirements.txt'])
except Exception as e:
    pass

setup(name='audio_visualizer_screenlet',
	  description='Cross-platform audio visualization desktop widget',
      install_requires=['watchdog','pyfftw','python-xlib','pyqt5'],
      packages=['avs']
	  )
