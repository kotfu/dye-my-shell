#
# Copyright (c) 2023 Jared Crapo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
"""iTerm terminal emulator agent"""

import contextlib

from ..exceptions import DyeSyntaxError
from .base import AgentBase


class Iterm(AgentBase):
    "Send escape sequences to iTerm terminal emulator"

    def run(self, comments=False):
        """send escape sequences to iTerm to make it do stuff"""
        output = []

        # set the profile
        self._iterm_profile(output)

        # set the tab or window title color
        self._iterm_tab(output)

        # set foreground and background colors
        self._iterm_render_style(output, "foreground", "fg")
        self._iterm_render_style(output, "background", "bg")

        # set the cursor shape and color
        self._iterm_cursor(output)

        return "\n".join(output)

    def _iterm_profile(self, output):
        """add commands to output to tell iterm to change to a profile"""
        try:
            profile = self.scope.definition["profile"]
            cmd = r'builtin echo -en "\e]1337;'
            cmd += f"SetProfile={profile}"
            cmd += r'\a"'
            output.append(cmd)
        except KeyError:
            # no profile directive given
            pass

    def _iterm_tab(self, output):
        """add commands to output to change the tab or window title background color"""
        with contextlib.suppress(KeyError):
            style = self.scope.styles["tab"]
            if style.color.is_default:
                # set the command to change the tab color back to the default,
                # meaning whatever is set in the profile.
                # gotta use raw strings here so the \e and \a don't get
                # interpreted by python, they need to be passed through
                # to the echo command
                cmd = r'builtin echo -en "\e]6;1;bg;*;default\a"'
                output.append(cmd)
            else:
                clr = style.color.get_truecolor()
                # in iterm you have to send different escape sequences
                #
                # gotta use raw strings here so the \e and \a don't get
                # interpreted by python, they need to be passed through
                # to the echo command
                cmd = r'builtin echo -en "\e]6;1;bg;red;brightness;'
                cmd += f"{clr.red}"
                cmd += r'\a"'
                output.append(cmd)
                cmd = r'builtin echo -en "\e]6;1;bg;green;brightness;'
                cmd += f"{clr.green}"
                cmd += r'\a"'
                output.append(cmd)
                cmd = r'builtin echo -en "\e]6;1;bg;blue;brightness;'
                cmd += f"{clr.blue}"
                cmd += r'\a"'
                output.append(cmd)

    CURSOR_MAP = {
        "block": "0",
        "box": "0",
        "vertical_bar": "1",
        "vertical": "1",
        "bar": "1",
        "pipe": "1",
        "underline": "2",
    }

    def _iterm_cursor(self, output):
        """create echo commands to change the cursor shape,
        foreground, and background colors
        """
        # check the cursor shape
        try:
            cursor = self.scope.definition["cursor"]
        except KeyError:
            cursor = None
        if cursor:
            if cursor == "profile":
                cmd = r'builtin echo -en "\e[0q"'
                output.append(cmd)
            elif cursor in self.CURSOR_MAP:
                cmd = r'builtin echo -en "\e]1337;'
                cmd += f"CursorShape={self.CURSOR_MAP[cursor]}"
                cmd += r'\a"'
                output.append(cmd)
            else:
                raise DyeSyntaxError(
                    f"unknown cursor '{cursor}' while processing scope '{self.scope}'"
                )
        # render the cursor color
        # iterm has curbg and curfg color codes, but as far as I can tell
        # the curfg is a noop
        self._iterm_render_style(output, "cursor", "curbg")

    def _iterm_render_style(self, output, style_name, iterm_key):
        """append an iterm escape sequence to change the color palette to output"""
        try:
            style = self.scope.styles[style_name]
            clr = style.color.get_truecolor()
            # gotta use raw strings here so the \e and \a don't get
            # interpreted by python, they need to be passed through
            # to the echo command
            cmd = r'builtin echo -en "\e]1337;'
            cmd += f"SetColors={iterm_key}={clr.hex.replace('#', '')}"
            cmd += r'\a"'
            output.append(cmd)
        except KeyError:
            # the given style doesn't exist
            pass
