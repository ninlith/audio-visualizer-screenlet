# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Okko Hartikainen <okko.hartikainen@gmail.com>
#
# This file is part of audio-visualizer-screenlet, which is licensed under the
# GNU General Public License 3.0 or later. See COPYING.

# Based on
# http://www.swharden.com/wp/2013-05-09-realtime-fft-audio-visualization-with-python/  # noqa pylint: disable=line-too-long
# by Scott W Harden

"""
Record soundcard output using WASAPI loopback capture. Requires forked PyAudio
and PortAudio: <https://github.com/intxcc/pyaudio_portaudio>.
"""

import collections
import threading
import pyaudio


class Portrecorder(object):
    """Record audio to a ring buffer."""

    def __init__(self, name, chunks, chunksize=1024, channels=2, rate="auto"):
        self.elements_per_ringbuffer = chunks
        self.frames_per_element = chunksize
        self.samples_per_frame = channels
        self.bytes_per_sample = 2  # int16
        self.name = name
        self.channels = channels
        self._ringbuffer = collections.deque(
            [b"0"*self.bytes_per_sample*channels*chunksize]*chunks,
            maxlen=self.elements_per_ringbuffer)

        self.p = pyaudio.PyAudio()  # pylint: disable=invalid-name
        default_output = self.p.get_default_output_device_info()
        self.deviceindex = default_output['index']
        if rate == "auto":
            self.rate = default_output['defaultSampleRate']
        else:
            self.rate = rate
        self.has_new_audio = False

    def start(self):
        """Start recording."""
        stream = self.p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=int(self.rate),
            input=True,
            frames_per_buffer=self.frames_per_element,
            input_device_index=int(self.deviceindex),
            as_loopback=True
            )

        def record():
            """Continuously read data and append to the ring buffer."""
            while True:
                audio_string = stream.read(self.frames_per_element)
                self._ringbuffer.append(audio_string)
                self.has_new_audio = True

        thread = threading.Thread(target=record)
        thread.start()

    @property
    def ringbuffer(self):
        """Get the ring buffer."""
        self.has_new_audio = False
        return self._ringbuffer
