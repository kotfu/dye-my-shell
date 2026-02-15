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
"""agent implementations and their base class"""

import importlib
import pkgutil

from .base import AgentBase, LsColorsFromStyle

# auto-import all modules in this package so agents register via __init_subclass__
for _, _module_name, _ in pkgutil.walk_packages(__path__):
    if _module_name != "base":
        importlib.import_module(f".{_module_name}", __name__)

# re-export agent classes for direct access as dye.agents.ClassName
from .dye import Dye
from .environment_variables import EnvironmentVariables
from .eza import Eza
from .fzf import Fzf
from .iterm import Iterm
from .ls_colors import LsColors
from .shell import Shell
