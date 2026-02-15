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
"""base class and mixin for all agents"""

import abc
import re

import rich.color

from ..exceptions import DyeError


class AgentBase(abc.ABC):
    """Abstract Base Class for all agents

    Subclass and implement `run()`. The first line of the class docstring
    is displayed by `shell-themer agents` as the description of the agent

    Creates a registry of all subclasses in cls.agents

    The string to use in your theme configuration file is the underscored
    class name, ie:

    EnvironmentVariables -> environment_variables
    LsColors -> ls_colors
    """

    classmap = {}

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        # make a registry of subclasses as they are defined
        cls.classmap[cls._name_of(cls.__name__)] = cls

    def __init__(self, scope):
        super().__init__()
        self.agent_name = self._name_of(self.__class__.__name__)
        self.scope = scope

    @classmethod
    def _name_of(cls, name: str) -> str:
        """Make an underscored, lowercase form of the given class name."""
        name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
        name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
        name = name.replace("-", "_")
        return name.lower()

    @abc.abstractmethod
    def run(self, comments=False) -> str:
        """Do agent work. Anything returned will be sourced by the shell"""


class LsColorsFromStyle:
    """Generator mixin to create ls_colors type styles"""

    def ls_colors_from_style(self, name, style, mapp, scope_name, allow_unknown=False):
        """create an entry suitable for LS_COLORS from a style

        name should be a valid LS_COLORS entry, could be a code representing
        a file type, or a glob representing a file extension

        style is a style object

        mapp is a dictionary of friendly color names to native color names
            ie map['directory'] = 'di'

        allow_unknown - whether to allow [name] that is not in [mapp]. If false,
        an error will be generated if you use a [name] that is not in [mapp]. If
        true, [mapp] will only be used as a "friendly" name lookup.

        **msgdata - used for generating useful error messages
        prog = the name of the program
        scope_name = is the scope where this mapped occured

        returns a tuple of the mapped name and a phrase to add to LS_COLORS
        """
        ansicodes = ""
        if not style:
            return "", ""
        try:
            mapname = mapp[name]
        except KeyError as exc:
            if allow_unknown:
                # no problem if we didn't find name in mapp, we'll just use name
                # as is
                mapname = name
            else:
                # they used a style for a file attribute that isn't in the map
                # which is not allowed
                raise DyeError(
                    f"unknown style '{name}' while processing scope '{scope_name}'"
                ) from exc

        if style.color.type == rich.color.ColorType.DEFAULT:
            ansicodes = "0"
        else:
            # this works, but it uses a protected method
            #   ansicodes = style._make_ansi_codes(rich.color.ColorSystem.TRUECOLOR)
            # here's another approach, we ask the style to render a string, then
            # go peel the ansi codes out of the generated escape sequence
            ansistring = style.render("-----")
            # style.render uses this string to build it's output
            # f"\x1b[{attrs}m{text}\x1b[0m"
            # so let's go split it apart
            match = re.match(r"^\x1b\[([;\d]*)m", ansistring)
            # and get the numeric codes
            ansicodes = match.group(1)
        return mapname, f"{mapname}={ansicodes}"
