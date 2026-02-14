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
"""eza agent for EZA_COLORS"""

import contextlib

from ..exceptions import DyeSyntaxError
from .base import AgentBase, LsColorsFromStyle


class Eza(AgentBase, LsColorsFromStyle):
    "Create EZA_COLORS environment variable for use with ls replacement eza"

    EZA_COLORS_BASE_MAP = {
        # create a map of friendly names to real codes.
        # we use the same friendly names as the theme.yml
        # file used by eza
        #
        "filekinds:normal": "fi",
        "filekinds:directory": "di",
        "filekinds:symlink": "ln",
        "filekinds:pipe": "pi",
        "filekinds:block_device": "bd",
        "filekinds:char_device": "cd",
        "filekinds:socket": "so",
        "filekinds:special": "sp",
        "filekinds:executable": "ex",
        "filekinds:mount_point": "mp",
        #
        "perms:user_read": "ur",
        "perms:user_write": "uw",
        "perms:user_executable_file": "ux",
        "perms:user_execute_other": "ue",
        "perms:group_read": "gr",
        "perms:group_write": "gw",
        "perms:group_execute": "gx",
        "perms:other_read": "tr",
        "perms:other_write": "tw",
        "perms:other_execute": "tx",
        "perms:special_user_file": "su",
        "perms:special_other": "sf",
        "perms:attribute": "xa",
        #
        "size:major": "df",
        "size:minor": "ds",
        "size:number_style": "sn",
        "size:number_byte": "nb",
        "size:number_kilo": "nk",
        "size:number_mega": "nm",
        "size:number_giga": "ng",
        "size:number_huge": "nt",
        "size:unit_style": "sb",
        "size:unit_byte": "ub",
        "size:unit_kilo": "uk",
        "size:unit_mega": "um",
        "size:unit_giga": "ug",
        "size:unit_huge": "ut",
        #
        "users:user_you": "uu",
        "users:user_other": "un",
        "users:user_root": "uR",
        "users:group_yours": "gu",
        "users:group_other": "gn",
        "users:group_root": "gR",
        #
        "links:normal": "lc",
        "links:multi_link_file": "lm",
        #
        "git:new": "ga",
        "git:modified": "gm",
        "git:deleted": "gd",
        "git:renamed": "gv",
        "git:typechange": "gt",
        "git:ignored": "gi",
        "git:conflicted": "gc",
        #
        "git_repo:branch_main": "Gm",
        "git_repo:branch_other": "Go",
        "git_repo:git_clean": "Gc",
        "git_repo:git_dirty": "Gd",
        #
        "selinux:colon": "Sn",
        "selinux:user": "Su",
        "selinux:role": "Sr",
        "selinux:typ": "St",
        "selinux:range": "Sl",
        #
        "file_type:image": "im",
        "file_type:video": "vi",
        "file_type:music": "mu",
        "file_type:lossless": "lo",
        "file_type:crypto": "cr",
        "file_type:document": "do",
        "file_type:compressed": "co",
        "file_type:temp": "tm",
        "file_type:compiled": "cm",
        "file_type:build": "bu",
        "file_type:source": "sc",
        #
        "punctuation": "xx",
        "date": "da",
        "inode": "in",
        "blocks": "bl",
        "header": "hd",
        "octal": "oc",
        "flags": "ff",
        "symlink_path": "lp",
        "control_char": "cc",
        "broken_path_overlay": "b0",
        "broken_symlink": "or",
    }
    # this map allows you to either use the 'native' eza code, or the
    # 'friendly' name defined by shell-themer
    EZA_COLORS_MAP = {}
    for friendly, actual in EZA_COLORS_BASE_MAP.items():
        EZA_COLORS_MAP[friendly] = actual
        EZA_COLORS_MAP[actual] = actual

    def run(self, comments=False):
        "Render a EZA_COLORS variable suitable for eza"
        outlist = []
        # figure out if we are clearing builtin styles
        with contextlib.suppress(KeyError):
            clear_builtin = self.scope.definition["clear_builtin"]
            if not isinstance(clear_builtin, bool):
                raise DyeSyntaxError(
                    f"scope '{self.scope}' requires 'clear_builtin' to be true or false"
                )
            if clear_builtin:
                # this tells exa to not use any built-in/hardcoded colors
                outlist.append("reset")

        # iterate over the styles given in our configuration
        for name, style in self.scope.styles.items():
            if style:
                _, render = self.ls_colors_from_style(
                    name,
                    style,
                    self.EZA_COLORS_MAP,
                    allow_unknown=True,
                    scope_name=self.scope,
                )
                outlist.append(render)

        # process the filesets

        # figure out which environment variable to put it in
        try:
            varname = self.scope.definition["environment_variable"]
        except KeyError:
            varname = "EZA_COLORS"

        # even if outlist is empty, we have to set the variable, because
        # when we are switching a theme, there may be contents in the
        # environment variable already, and we need to tromp over them
        # we chose to set the variable to empty instead of unsetting it
        print(f'''export {varname}="{":".join(outlist)}"''')
