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
# pylint: disable=protected-access, missing-function-docstring, redefined-outer-name
# pylint: disable=missing-module-docstring, unused-variable

from dye import Dye


def test_dye_single_style(dye_cmdline, capsys):
    pattern_str = """
        [scopes.my_dye]
        agent = "dye"
        style.usage_metavar = "#ffb86c"
    """
    exit_code = dye_cmdline("apply", None, pattern_str)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out.strip() == 'export DYE_COLORS="usage_metavar=#ffb86c"'


def test_dye_multiple_styles(dye_cmdline, capsys):
    pattern_str = """
        [scopes.my_dye]
        agent = "dye"
        style.usage_metavar = "#ffb86c"
        style.ui_border = "#bd93f9"
    """
    exit_code = dye_cmdline("apply", None, pattern_str)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert "usage_metavar=#ffb86c" in out
    assert "ui_border=#bd93f9" in out
    assert out.strip().startswith('export DYE_COLORS="')
    assert out.strip().endswith('"')


def test_dye_with_template(dye_cmdline, capsys):
    pattern_str = """
        [colors]
        orange = "#ffb86c"
        purple = "#bd93f9"

        [scopes.my_dye]
        agent = "dye"
        style.usage_metavar = "{{ colors.orange }}"
        style.ui_border = "{{ colors.purple }}"
    """
    exit_code = dye_cmdline("apply", None, pattern_str)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert "usage_metavar=#ffb86c" in out
    assert "ui_border=#bd93f9" in out


def test_dye_with_bold_style(dye_cmdline, capsys):
    pattern_str = """
        [scopes.my_dye]
        agent = "dye"
        style.usage_prog = "bold #50fa7b"
    """
    exit_code = dye_cmdline("apply", None, pattern_str)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out.strip() == 'export DYE_COLORS="usage_prog=bold #50fa7b"'


def test_dye_no_styles(dye_cmdline, capsys):
    pattern_str = """
        [scopes.my_dye]
        agent = "dye"
    """
    exit_code = dye_cmdline("apply", None, pattern_str)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out.strip() == 'export DYE_COLORS=""'


def test_dye_all_elements(dye_cmdline, capsys):
    pattern_str = """
        [scopes.my_dye]
        agent = "dye"
        style.usage_args = "#f8f8f2"
        style.usage_groups = "bold #ff5555"
        style.usage_help = "#6272a4"
        style.usage_metavar = "#ffb86c"
        style.usage_prog = "bold #50fa7b"
        style.usage_syntax = "#f1fa8c"
        style.usage_text = "#f8f8f2"
        style.ui_border = "#bd93f9"
        style.ui_column_header = "bold #ff79c6"
    """
    exit_code = dye_cmdline("apply", None, pattern_str)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    for element in Dye.OUTPUT_ELEMENTS:
        assert f"{element}=" in out
