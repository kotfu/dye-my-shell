#
# Copyright (c) 2025 Jared Crapo
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


#
# test the elements command (which shows the list of output elements)
#
def test_elements(dye_cmdline, capsys):
    exit_code = dye_cmdline("elements")
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    for element in Dye.OUTPUT_ELEMENTS:
        assert element in out
    # the elements command outputs a rich table with a header row and a line
    # under the header
    lines = out.splitlines()
    # this is the header row
    assert "Element" in lines[1]
    assert "Description" in lines[1]
    # +4 for the top border, bottom border, header words, and line under
    # the header words
    assert len(lines) == len(Dye.OUTPUT_ELEMENTS) + 4


def test_elements_descriptions(dye_cmdline, capsys):
    exit_code = dye_cmdline("elements")
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    for _element, description in Dye.OUTPUT_ELEMENTS.items():
        assert description in out


def test_elements_sorted(dye_cmdline, capsys):
    exit_code = dye_cmdline("elements")
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    lines = out.splitlines()
    # extract element names from table rows (skip header area: top border,
    # header row, separator, then data rows until bottom border)
    element_names = []
    for line in lines[3:-1]:
        # each table row has the element name in the first column
        parts = line.split("│")
        if len(parts) >= 2:
            name = parts[1].strip()
            if name:
                element_names.append(name)
    assert element_names == sorted(element_names)
