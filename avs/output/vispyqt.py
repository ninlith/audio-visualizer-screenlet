# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Okko Hartikainen <okko.hartikainen@gmail.com>
#
# This file is part of audio-visualizer-screenlet, which is licensed under the
# GNU General Public License 3.0 or later. See COPYING.

"""Visual output module that uses Vispy with Qt5 app backend."""

import logging
import os
import random
import time
import numpy as np
from vispy import app, scene

# pylint: disable=invalid-name, no-member
logger = logging.getLogger(__name__)


class Visualizer(object):
    """Visualize audio."""

    def __init__(self, title, configs, audio_processor):
        self.configs = configs
        self.audio_processor = audio_processor
        number_of_spectrum_samples = len(audio_processor.notespace)
        self.mouse_pressed = None
        self.mouse_press_x = None
        self.mouse_press_y = None

        # canvas
        self.canvas_width = configs.settings.getint('canvas', 'width')
        self.canvas_height = configs.settings.getint('canvas', 'height')
        self.canvas_padding = configs.settings.getint('canvas', 'padding')
        self.canvas_background_color = configs.settings.getmultifloat(
            'canvas', 'background_color')
        self.canvas = scene.SceneCanvas(
            title=title,
            size=(self.canvas_width, self.canvas_height),
            keys='interactive',
            decorate=False,
            bgcolor=self.canvas_background_color,
            app='PyQt5',
            )
        self.canvas.connect(self.on_mouse_press)
        self.canvas.connect(self.on_mouse_release)
        self.canvas.connect(self.on_mouse_move)
        self.canvas.connect(self.on_mouse_wheel)
        self.canvas.connect(self.on_key_press)
        self.canvas.show()
        self.canvas.measure_fps(1, callback=lambda x: None)
        try:
            self.canvas_x = int(configs.load_state_value('canvas', 'x'))
            self.canvas_y = int(configs.load_state_value('canvas', 'y'))
        except ValueError as e:
            logger.warning(e)
        else:
            self.canvas.position = (self.canvas_x, self.canvas_y)

        # spectrum
        self.spectrum_x = self.canvas_padding
        self.spectrum_y = self.canvas_height - self.canvas_padding
        self.spectrum_width = self.canvas_width - 2*self.canvas_padding
        self.spectrum_color = configs.settings.getmultifloat(
            'spectrum', 'color')
        self.spectrum_pos = np.empty(
            (number_of_spectrum_samples, 2), np.float32)
        self.spectrum_pos[:, 0] = self.spectrum_x + np.linspace(
            0, self.spectrum_width, number_of_spectrum_samples)
        self.spectrum_pos[:, 1] = self.spectrum_y
        self.spectrum = scene.visuals.Line(
            pos=self.spectrum_pos,
            color=self.spectrum_color,
            parent=self.canvas.scene,
            antialias=True,
            method='agg',
            width=configs.settings.getfloat('spectrum', 'line_width'))

    @staticmethod
    def run():
        """Enter the native GUI event loop."""
        app.run()

    def set_data(self, fft_amplitudes):
        """Update visuals."""
        self.spectrum_pos[:, 1] = self.spectrum_y - fft_amplitudes
        self.spectrum.set_data(pos=self.spectrum_pos)

    def on_mouse_press(self, event):
        """Handle mouse press events."""
        # Initiate mouse drag.
        self.mouse_pressed = True
        self.mouse_press_x = event.native.globalX() - self.canvas.position[0]
        self.mouse_press_y = event.native.globalY() - self.canvas.position[1]

    def on_mouse_release(self, event):  # pylint: disable=unused-argument
        """Handle mouse release events."""
        # Complete mouse drag.
        self.mouse_pressed = False
        self.configs.save_state_value(
            'canvas', 'x', str(self.canvas.position[0]))
        self.configs.save_state_value(
            'canvas', 'y', str(self.canvas.position[1]))

    def on_mouse_move(self, event):
        """Handle mouse move events."""
        # Drag canvas.
        if self.mouse_pressed:
            diff_x = event.native.globalX() - self.mouse_press_x
            diff_y = event.native.globalY() - self.mouse_press_y
            self.canvas.position = (diff_x, diff_y)
            if os.environ.get('XDG_SESSION_TYPE') == "wayland":
                time.sleep(0.07)  # XXX: Jumpy otherwise.

    def on_mouse_wheel(self, event):
        """Handle mouse wheel events."""
        if event.delta[1] == 1:
            self.audio_processor.increase_sensitivity()
        else:
            self.audio_processor.decrease_sensitivity()

    def on_key_press(self, event):
        """Handle key press events."""
        modifiers = [key.name for key in event.modifiers]
        logger.debug("Key pressed - text: {}, key: {}, modifiers: {}".format(
            event.text, event.key.name, modifiers))
        if event.text == "f":
            logger.debug("{:.1f} FPS".format(self.canvas.fps))
        elif event.text == "c":
            self.spectrum.set_data(
                color=(random.random(), random.random(), random.random(), 1))
        elif event.text == "C":
            self.spectrum.set_data(
                color=self.spectrum_color)
