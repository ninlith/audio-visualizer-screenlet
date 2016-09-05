# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Okko Hartikainen <okko.hartikainen@gmail.com>
#
# This file is part of audio-visualizer-screenlet, which is licensed under the
# GNU General Public License 3.0 or later. See COPYING.

"""General-purpose utility classes and functions."""

from difflib import Differ
import os
import sys
try:
    from threading import _Timer as Timer
except ImportError:
    from threading import Timer


# https://gist.github.com/alexbw/1187132#gistcomment-1408433
class RepeatingTimer(Timer):
    """
    See: https://hg.python.org/cpython/file/2.7/Lib/threading.py#l1079
    """

    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)

        self.finished.set()


# https://stackoverflow.com/a/10775310
def highlight_changes(s1, s2):
    """Highlight words that are changed."""
    # pylint: disable=invalid-name
    l1 = s1.split(' ')
    l2 = s2.split(' ')
    dif = list(Differ().compare(l1, l2))
    return " ".join(["\033[1m" + i[2:] + "\033[0m" if i[:1] == "+" else i[2:]
                     for i in dif if not i[:1] in "-?"])


def restart_program():
    """Restart the current program."""
    python = sys.executable
    os.execl(python, python, *sys.argv)
