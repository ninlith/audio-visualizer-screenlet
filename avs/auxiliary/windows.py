# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Okko Hartikainen <okko.hartikainen@gmail.com>
#
# This file is part of audio-visualizer-screenlet, which is licensed under the
# GNU General Public License 3.0 or later. See COPYING.

"""Windows-specific code."""

# pylint: disable=import-error
import win32api
import win32con
import win32gui


class Kludges(object):
    """Workarounds."""

    def __init__(self, title):
        self.topmost = not self.is_desktop_on_foreground()
        self.hwnd = win32gui.FindWindow(None, title)

    def is_desktop_on_foreground(self):  # pylint: disable=no-self-use
        """Detect "show desktop" or something close enough."""
        foreground = win32gui.GetForegroundWindow()
        return bool(
            foreground and win32gui.GetClassName(foreground) == "WorkerW")

    def stay_on_bottom(self):
        """Pin to desktop or something close enough (call repeatedly)."""
        if self.is_desktop_on_foreground():
            if self.topmost is False:
                win32gui.SetWindowPos(
                    self.hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                self.topmost = True
        else:
            if self.topmost is True:
                win32gui.SetWindowPos(
                    self.hwnd, win32con.HWND_BOTTOM, 0, 0, 0, 0,
                    win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                self.topmost = False

    # "To prevent the window button from being placed on the taskbar, create
    # the unowned window with the WS_EX_TOOLWINDOW extended style. As an
    # alternative, you can create a hidden window and make this hidden window
    # the owner of your visible window. The Shell will remove a window's button
    # from the taskbar only if the window's style supports visible taskbar
    # buttons. If you want to dynamically change a window's style to one that
    # doesn't support visible taskbar buttons, you must hide the window first
    # (by calling ShowWindow with SW_HIDE), change the window style, and then
    # show the window."
    # -- https://msdn.microsoft.com/en-us/library/bb776822%28v=vs.85%29.aspx
    def remove_taskbar_button(self):
        """Hide window from taskbar and ALT+TAB dialog."""
        win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)
        win32api.SetWindowLong(
            self.hwnd, win32con.GWL_EXSTYLE,
            win32api.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
            | win32con.WS_EX_NOACTIVATE
            | win32con.WS_EX_TOOLWINDOW)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
