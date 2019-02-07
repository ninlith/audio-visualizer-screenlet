# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Okko Hartikainen <okko.hartikainen@gmail.com>
#
# This file is part of audio-visualizer-screenlet, which is licensed under the
# GNU General Public License 3.0 or later. See COPYING.

# Based on
# https://github.com/gooofy/nlp/blob/185466517c291a300dd0950548d4793401c32b01/pulseclient.py  # noqa pylint: disable=line-too-long
# by Guenter Bartsch

"""Record soundcard output using PulseAudio simple API."""

import collections
import ctypes
import logging
import os
import re
import threading

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


# pylint: disable=missing-docstring, too-few-public-methods, protected-access
pa = ctypes.cdll.LoadLibrary("libpulse-simple.so.0")

PA_STREAM_RECORD = 2
PA_SAMPLE_S16LE = 3


class struct_pa_sample_spec(ctypes.Structure):
    __slots__ = [
        'format',
        'rate',
        'channels',
    ]

struct_pa_sample_spec._fields_ = [
    ('format', ctypes.c_int),
    ('rate', ctypes.c_uint32),
    ('channels', ctypes.c_uint8),
]

pa_sample_spec = struct_pa_sample_spec  # /usr/include/pulse/sample.h:174


class struct_pa_buffer_attr(ctypes.Structure):
    __slots__ = [
        'maxlength',
        'tlength',
        'prebuf',
        'minreq',
        'fragsize',
    ]

struct_pa_buffer_attr._fields_ = [
    ('maxlength', ctypes.c_uint32),
    ('tlength', ctypes.c_uint32),
    ('prebuf', ctypes.c_uint32),
    ('minreq', ctypes.c_uint32),
    ('fragsize', ctypes.c_uint32),
]

pa_buffer_attr = struct_pa_buffer_attr  # /usr/include/pulse/def.h:221


class Pulserecorder(object):
    """Record audio to a ring buffer."""

    def __init__(self, name, chunks, chunksize=1024, channels=2, rate=44100):
        self.elements_per_ringbuffer = chunks
        self.frames_per_element = chunksize
        self.samples_per_frame = channels
        self.bytes_per_sample = 2  # int16
        self.name = name.encode('ascii')
        self.channels = channels
        self.has_new_audio = False
        self.bytes_per_element = chunksize*channels*self.bytes_per_sample
        self.buf = ctypes.create_string_buffer(self.bytes_per_element)
        self._ringbuffer = collections.deque(
            [self.buf.raw]*chunks, maxlen=self.elements_per_ringbuffer)

        def pacmd_stat(o):
            """Get PulseAudio memory block statistics."""
            command = "pacmd stat | awk -F': ' '/^" + o + ": /{print $2}'"
            ret = os.popen(command).readline()
            return ret.rstrip()

        default_sample_spec = pacmd_stat("Default sample spec").split()
        default_rate = int(re.sub("[^0-9]", "", default_sample_spec[2]))
        self.rate = default_rate if rate == "auto" else rate
        self.device = (
            pacmd_stat("Default sink name") + ".monitor").encode('ascii')
        logger.debug("{}, rate: {} Hz".format(self.device, self.rate))

    # pylint: disable=attribute-defined-outside-init
    def start(self):
        """Start recording."""
        ss = struct_pa_sample_spec()
        ss.rate = self.rate
        ss.channels = self.channels
        ss.format = PA_SAMPLE_S16LE

        error = ctypes.c_int(0)

        # pylint: disable=bad-whitespace
        ba = struct_pa_buffer_attr()
        ba.maxlength = -1
        ba.tlength   = -1
        ba.prebuf    = -1
        ba.minreq    = -1
        ba.fragsize  = -1

        class struct_pa_simple(ctypes.Structure):
            pass
        pa.pa_simple_new.restype = ctypes.POINTER(struct_pa_simple)

        stream = pa.pa_simple_new(
            None,                # Server name, or NULL for default.
            self.name,           # Client name.
            PA_STREAM_RECORD,    # Record or playback.
            self.device,         # Sink name, or NULL for default.
            b"record",           # Stream name.
            ctypes.byref(ss),    # Sample format.
            None,                # Channel map, or NULL for default.
            ctypes.byref(ba),    # Buffering attributes, or NULL for default.
            ctypes.byref(error)  # A pointer where the error code is stored.
        )

        if not stream:
            raise Exception("pa_simple_new() failed: {}".format(
                pa.strerror(ctypes.byref(error))))

        def record():
            """Continuously read data and append to the ring buffer."""
            while True:
                if pa.pa_simple_read(
                        stream, self.buf, self.bytes_per_element, error):
                    raise Exception("pa_simple_read() failed")
                self._ringbuffer.append(self.buf.raw)
                self.has_new_audio = True

        thread = threading.Thread(target=record)
        thread.start()

    @property
    def ringbuffer(self):
        """Get the ring buffer."""
        self.has_new_audio = False
        return self._ringbuffer
