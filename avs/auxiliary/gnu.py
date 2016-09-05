# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Okko Hartikainen <okko.hartikainen@gmail.com>
#
# This file is part of audio-visualizer-screenlet, which is licensed under the
# GNU General Public License 3.0 or later. See COPYING.

"""GNU-specific code."""

import logging
from Xlib import display, Xatom
from auxiliary import utils

# pylint: disable=invalid-name, no-member
logger = logging.getLogger(__name__)


def pin_to_desktop(name, pid):
    """Set window type to desktop window."""
    # Similar to
    # os.system(
    #    "xprop -id $(wmctrl -l -p | grep {} | grep {}".format(title, pid)
    #    + " | cut -d' ' -f 1) -f _NET_WM_WINDOW_TYPE 32a "
    #    + "-set _NET_WM_WINDOW_TYPE _NET_WM_WINDOW_TYPE_DESKTOP")
    disp = display.Display()
    screen = disp.screen()
    root = screen.root

    def traverse_and_search(name, pid, window=root, level=0):
        """
        Traverse the tree of windows and store matching window id to a
        function attribute.
        """
        try:
            window_name = window.get_wm_name()
        except TypeError as e:
            logger.debug(e)
            window_name = "..."
        pid_prop = window.get_full_property(disp.intern_atom('_NET_WM_PID'), 0)
        window_pid = pid_prop.value[0] if pid_prop else ""
        # logger.debug("    "*level + "{} {}".format(window_name, window_pid))

        if window_name == name and window_pid == pid:
            traverse_and_search.result = window.id

        for child in window.query_tree().children:
            traverse_and_search(name, pid, child, level + 1)

    traverse_and_search(name, pid)
    win = disp.create_resource_object("window", traverse_and_search.result)
    atom_wm_type = disp.intern_atom('_NET_WM_WINDOW_TYPE')
    atom_wm_type_desktop = disp.intern_atom('_NET_WM_WINDOW_TYPE_DESKTOP')
    logger.debug("atom_wm_type_desktop: {}".format(atom_wm_type_desktop))
    a = str(win.get_full_property(atom_wm_type, 0))
    win.change_property(atom_wm_type, Xatom.ATOM, 32, [atom_wm_type_desktop])
    b = str(win.get_full_property(atom_wm_type, 0))
    logger.debug("\n{}\n--->\n{}".format(a, utils.highlight_changes(a, b)))
    disp.flush()
