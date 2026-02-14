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
"""GNU ls agent for LS_COLORS"""

import rich.style

from ..exceptions import DyeSyntaxError
from .base import AgentBase, LsColorsFromStyle


class GnuLs(AgentBase, LsColorsFromStyle):
    "Create LS_COLORS environment variable for use with GNU ls"

    LS_COLORS_BASE_MAP = {
        # map both a friendly name and the "real" name
        "text": "no",
        "file": "fi",
        "directory": "di",
        "symlink": "ln",
        "multi_hard_link": "mh",
        "pipe": "pi",
        "socket": "so",
        "door": "do",
        "block_device": "bd",
        "character_device": "cd",
        "broken_symlink": "or",
        "missing_symlink_target": "mi",
        "setuid": "su",
        "setgid": "sg",
        "sticky": "st",
        "other_writable": "ow",
        "sticky_other_writable": "tw",
        "executable_file": "ex",
        "file_with_capability": "ca",
    }
    # this map allows you to either use the 'native' color code, or the
    # 'friendly' name defined by shell-themer
    LS_COLORS_MAP = {}
    for friendly, actual in LS_COLORS_BASE_MAP.items():
        LS_COLORS_MAP[friendly] = actual
        LS_COLORS_MAP[actual] = actual

    def run(self, comments=False):
        "Render a LS_COLORS variable suitable for GNU ls"
        outlist = []
        havecodes = []
        # figure out if we are clearing builtin styles
        try:
            clear_builtin = self.scope.definition["clear_builtin"]
            if not isinstance(clear_builtin, bool):
                raise DyeSyntaxError(
                    f"scope '{self.scope}' requires 'clear_builtin' to be true or false"
                )
        except KeyError:
            clear_builtin = False

        # iterate over the styles given in our configuration
        for name, style in self.scope.styles.items():
            if style:
                mapcode, render = self.ls_colors_from_style(
                    name,
                    style,
                    self.LS_COLORS_MAP,
                    self.scope.name,
                    allow_unknown=False,
                )
                havecodes.append(mapcode)
                outlist.append(render)

        if clear_builtin:
            style = rich.style.Style.parse("default")
            # go through all the color codes, and render them with the
            # 'default' style and add them to the output
            for name, code in self.LS_COLORS_BASE_MAP.items():
                if code not in havecodes:
                    _, render = self.ls_colors_from_style(
                        name,
                        style,
                        self.LS_COLORS_MAP,
                        allow_unknown=False,
                        scope_name=self.scope,
                    )
                    outlist.append(render)

        # process the filesets

        # figure out which environment variable to put it in
        try:
            varname = self.scope.definition["environment_variable"]
        except KeyError:
            varname = "LS_COLORS"

        # even if outlist is empty, we have to set the variable, because
        # when we are switching a theme, there may be contents in the
        # environment variable already, and we need to tromp over them
        # we chose to set the variable to empty instead of unsetting it
        return f'''export {varname}="{":".join(outlist)}"'''
