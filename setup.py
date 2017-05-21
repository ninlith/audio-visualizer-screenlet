#!/usr/bin/env python
req = ['setuptools','six','numpy','scipy','vispy','pyqt']
pipreq = ['watchdog','pyfftw','python-xlib'] 
#
import pip
try:
    import conda.cli
    conda.cli.main('install',*req)
except Exception as e:
    req = req[:-1] + ['pyqt5']  # drop pyqt for pyqt5
    pip.main(['install'] + req)
pip.main(['install'] + pipreq)
# %%
from setuptools import setup

setup(name='audio_visualizer_screenlet',
      packages=['avs'],
      author='Okko Hartikainen',
      url='https://github.com/ninlith/audio-visualizer-screenlet',
	  description='Cross-platform audio visualization desktop widget',
	  )
