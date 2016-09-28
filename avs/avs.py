#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Okko Hartikainen <okko.hartikainen@gmail.com>
#
# This file is part of audio-visualizer-screenlet, which is licensed under the
# GNU General Public License 3.0 or later. See COPYING.

"""Cross-platform audio visualizer desktop widget."""

# pylint: disable=wrong-import-position, ungrouped-imports
from __future__ import division
import sys
sys.dont_write_bytecode = True  # noqa
import logging
import os
import signal
import output.vispyqt
from auxiliary import conf, utils
from process.audio_processor import AudioProcessor
if os.name == "nt":
    from input.portaudio import Portrecorder as Recorder
    from auxiliary import windows
else:
    from input.pulseaudio import Pulserecorder as Recorder
    from auxiliary import gnu

TITLE = "audio-visualizer-screenlet"


def main():
    """Main function."""
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    args = conf.parse_command_line_args()
    conf.setup_logging(args.loglevel)
    logger = logging.getLogger(__name__)
    configs = conf.Configs(TITLE)

    recorder = Recorder(
        TITLE,
        chunks=configs.settings.getint('recorder', 'chunks'),
        chunksize=configs.settings.getint('recorder', 'chunksize'),
        channels=configs.settings.getint('recorder', 'channels'),
        rate=configs.settings.get('recorder', 'rate'),
        )
    audio_processor = AudioProcessor(
        configs,
        chunks=recorder.elements_per_ringbuffer,
        chunksize=recorder.frames_per_element,
        channels=recorder.channels,
        rate=recorder.rate,
        )
    visualizer = output.vispyqt.Visualizer(
        TITLE,
        configs,
        audio_processor,
        )

    # Pin to desktop
    pid = os.getpid()
    logger.debug("PID: {}".format(pid))
    if os.name == "nt":
        win_kludges = windows.Kludges(TITLE)
        win_kludges.remove_taskbar_button()
        win_timer = utils.RepeatingTimer(
            interval=0.1,
            function=win_kludges.stay_on_bottom)
        win_timer.start()
    else:
        gnu.pin_to_desktop(TITLE, pid)

    def update():
        """Pass data from recorder via processor to visualizer."""
        if recorder.has_new_audio:
            audio_processor.set_audio(recorder.ringbuffer)
            fft_amplitudes = audio_processor.log_frequency_spectrum()
            visualizer.set_data(fft_amplitudes)

    # Run
    recorder.start()
    timer = utils.RepeatingTimer(
        interval=1.0/configs.settings.getfloat('main', 'timer_frequency'),
        function=update
        )
    timer.start()
    visualizer.run()


if __name__ == "__main__" and sys.flags.interactive == 0:
    main()
