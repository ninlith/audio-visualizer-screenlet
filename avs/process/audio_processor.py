# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Okko Hartikainen <okko.hartikainen@gmail.com>
#
# This file is part of audio-visualizer-screenlet, which is licensed under the
# GNU General Public License 3.0 or later. See COPYING.

"""Audio processor."""

import logging
import multiprocessing
import numpy as np
from scipy.interpolate import Akima1DInterpolator
import pyfftw
import process.generic

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


# pylint: disable=no-name-in-module, attribute-defined-outside-init, no-member
class AudioProcessor(object):
    """Process audio."""

    def __init__(self, configs, chunks, chunksize, channels, rate):
        self.configs = configs
        self.channels = channels
        self.chunksize = chunksize
        self.channel_len = chunks*chunksize
        self.fft_len = self.channel_len//2 + 1  # See numpy.fft.rfft
        self.fft_freqs_in_hertz = np.fft.rfftfreq(self.channel_len, d=1.0/rate)
        endpoint_notes = configs.settings.getmultistr('fft', 'endpoint_notes')
        self.notespace = process.generic.notespace(
            endpoint_notes[0], endpoint_notes[1],
            step=1.0/6)  # XXX
        self.window = np.hanning(self.channel_len)
        self.sensitivity = configs.settings.getfloat('fft', 'sensitivity')
        self.compute_weights(self.sensitivity)

        logger.debug("FFT length: {}".format(self.fft_len))

        # Create a pyfftw.FFTW object
        a = pyfftw.empty_aligned(
            self.channel_len, dtype='int16', n=pyfftw.simd_alignment)
        self.fft = pyfftw.builders.rfft(
            a, overwrite_input=True, threads=multiprocessing.cpu_count())

    def set_audio(self, ringbuffer_data):
        """Convert and store given audio data to instance variables."""
        audio_string = b"".join(list(ringbuffer_data))
        audio_array = np.fromstring(audio_string, dtype=np.int16)
        if self.channels == 2:
            a = np.reshape(audio_array, (self.channel_len, self.channels))
            self.audio_left = a[:, 0]
            self.audio_right = a[:, 1]
            self.audio_mono = a.mean(axis=1, dtype=np.int32).astype(np.int16)
        elif self.channels == 1:
            self.audio_left = self.audio_right = self.audio_mono = audio_array
        else:
            raise ValueError(
                "Invalid number of channels ({})".format(self.channels))

    def compute_weights(self, sensitivity):
        """Compute weights based on settings and given sensitivity."""
        logger.debug("Sensitivity: {}".format(sensitivity))
        self.weights = sensitivity/(2**20)
        self.weights *= 1/np.sqrt(self.channel_len)  # Unitary normalization
        self.weights *= self.configs.settings.getint('canvas', 'height')
        a_db = (process.generic.a_weight(self.notespace)
                * self.configs.settings.getfloat('fft', 'a-weighting'))
        self.weights *= 10**(a_db/20)  # dB to gain-multiplier

    def increase_sensitivity(self):
        """Increase sensitivity in a logarithmic fashion."""
        if self.sensitivity < 500:
            self.sensitivity *= 1.2
            self.compute_weights(self.sensitivity)

    def decrease_sensitivity(self):
        """Decrease sensitivity in a logarithmic fashion."""
        if self.sensitivity > 0.5:
            self.sensitivity /= 1.2
            self.compute_weights(self.sensitivity)

    def log_frequency_spectrum(self):
        """Return amplitude spectrum in logarithmic frequency space."""
        self.fft.input_array[:] = np.multiply(self.audio_mono, self.window)
        amplitudes = np.absolute(self.fft())
        interp = Akima1DInterpolator(self.fft_freqs_in_hertz, amplitudes)
        return np.multiply(interp(self.notespace), self.weights)

    def rms_stereo(self):
        """Return the root mean square of left and right channels."""
        rms_left = process.generic.rms(self.audio_left[:self.chunksize])
        rms_right = process.generic.rms(self.audio_right[:self.chunksize])
        return rms_left, rms_right
