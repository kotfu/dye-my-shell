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

import os

import pytest
import rich
import rich.text
from rich_argparse import RichHelpFormatter

from dye import Dye, DyeError
from dye import __main__ as mainmodule


#
# test output color logic
#
def test_output_color_no_color_env(dye_cmdline, mocker):
    RichHelpFormatter.styles["argparse.text"] = "#ff00ff"
    mocker.patch.dict(os.environ, {"NO_COLOR": "doesn't matter"}, clear=True)
    dye_cmdline("--help")
    assert not RichHelpFormatter.styles


def test_output_color_envs_only(dye_cmdline, mocker):
    # NO_COLOR should override DYE_COLORS
    RichHelpFormatter.styles["argparse.text"] = "#333333"
    envs = {"DYE_COLORS": "usage_text=#f0f0f0", "NO_COLOR": "doesn't matter"}
    mocker.patch.dict(os.environ, envs, clear=True)
    dye_cmdline("--help")
    assert not RichHelpFormatter.styles


def test_output_color_env_color(dye_cmdline, mocker):
    # DYE_COLORS should override default colors
    RichHelpFormatter.styles["argparse.text"] = "#333333"
    mocker.patch.dict(os.environ, {"DYE_COLORS": "usage_text=#f0f0f0"}, clear=True)
    dye_cmdline("--help")
    assert RichHelpFormatter.styles["argparse.text"] == "#f0f0f0"


def test_output_color_force(mocker):
    create_console = mocker.patch("dye.Dye._create_console")
    create_error_console = mocker.patch("dye.Dye._create_error_console")
    create_print_console = mocker.patch("dye.Dye._create_print_console")
    dye = Dye()
    # reset so we only track calls from parse_args, not the constructor
    create_console.reset_mock()
    create_error_console.reset_mock()
    create_print_console.reset_mock()
    dye.parse_args(["--force-color", "agents"])
    create_console.assert_called_once_with(True)
    create_error_console.assert_called_once_with(True)
    create_print_console.assert_called_once_with(True)


def test_output_color_env_empty(dye_cmdline, mocker):
    # DYE_COLORS should override default colors
    RichHelpFormatter.styles["argparse.text"] = "#ff00ff"
    mocker.patch.dict(os.environ, {"DYE_COLORS": ""}, clear=True)
    dye_cmdline("--help")
    assert not RichHelpFormatter.styles


def test_output_color_env_unknown_element(dye_cmdline, mocker, capsys):
    mocker.patch.dict(
        os.environ,
        {"DYE_COLORS": "homer_simpson=red bold on black:fred=white"},
    )
    msg = "It's Wednesday my dudes."
    exit_code = dye_cmdline(f"-d print {msg}")
    out, err = capsys.readouterr()
    assert "[debug]" in err
    assert "skipping invalid element" in err
    assert msg in out
    assert exit_code == 0


def test_output_color_env_parse_error(dye_cmdline, mocker, capsys):
    mocker.patch.dict(
        os.environ,
        {"DYE_COLORS": "usage_help=red:usage_args red bold on black white"},
    )
    msg = "It's Wednesday my dudes."
    exit_code = dye_cmdline(f"-d print {msg}")
    out, err = capsys.readouterr()
    assert "[debug]" in err
    assert "skipping invalid expression" in err
    assert msg in out
    assert exit_code == 0


#
# test unknown commands, no commands, help, version, and debug
#
def test_help_option(dye_cmdline, capsys):
    exit_code = dye_cmdline("--help")
    assert exit_code == Dye.EXIT_SUCCESS
    out, err = capsys.readouterr()
    assert not err
    assert "preview" in out
    assert "--force-color" in out


def test_h_option(dye_cmdline, capsys):
    exit_code = dye_cmdline("-h")
    assert exit_code == Dye.EXIT_SUCCESS
    out, err = capsys.readouterr()
    assert not err
    assert "preview" in out
    assert "--force-color" in out


def test_version_option(dye_cmdline, capsys):
    exit_code = dye_cmdline("--version")
    assert exit_code == Dye.EXIT_SUCCESS
    out, err = capsys.readouterr()
    assert not err
    assert "dye" in out


def test_v_option(dye_cmdline, capsys):
    exit_code = dye_cmdline("-v")
    assert exit_code == Dye.EXIT_SUCCESS
    out, err = capsys.readouterr()
    assert not err
    assert "dye" in out


def test_h_and_v_option(dye_cmdline, capsys):
    exit_code = dye_cmdline("-h -v")
    assert exit_code == Dye.EXIT_USAGE
    out, err = capsys.readouterr()
    assert not out
    # this message comes from argparse, we can't modify it
    assert "not allowed with argument" in err


def test_no_command(dye_cmdline, capsys):
    # this should show the usage message
    exit_code = dye_cmdline(None)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_USAGE
    assert not out
    # if you don't give a command, that's a usage error
    # so the usage message goes on standard error
    # check a few things in the usage message
    assert "apply" in err
    assert "preview" in err
    assert "--force-color" in err
    assert "-v" in err


def test_help_command(dye_cmdline, capsys):
    # this should show the usage message
    exit_code = dye_cmdline("help")
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    # if you ask for help, help should be on standard output
    assert "apply" in out
    assert "preview" in out
    assert "--force-color" in out
    assert "-v" in out


def test_unknown_command(dye_cmdline, capsys):
    # these errors are all raised and generated by argparse
    exit_code = dye_cmdline("unknowncommand")
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_USAGE
    assert not out
    assert "error" in err
    assert "invalid choice" in err


def test_debug(capsys):
    # we don't use the dye_cmdline fixture because the debug output
    # is generated during dispatch, before the fixture can capture it;
    # we use --no-theme and --no-pattern to make sure the test isn't
    # reading any theme/pattern files the developer has set in their
    # environment
    msg = "Hello there. General Kenobi."
    dye = Dye()
    argv = ["-d", "print", "--no-theme", "--no-pattern", msg]
    (_, args) = dye.parse_args(argv)
    exit_code = dye.dispatch("dye", args)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert "[debug]" in err
    assert out == f"{msg}\n"


#
# test dye_dir() property
#
def test_dye_dir_environment_variable(mocker, tmp_path):
    dye = Dye()
    mocker.patch.dict(os.environ, {"DYE_DIR": str(tmp_path)})
    # dye_dir should be a Path object
    assert dye.dye_dir == tmp_path


def test_dye_dir_no_environment_variable(mocker):
    # ensure no DYE_DIR environment variable exists
    mocker.patch.dict(os.environ, {}, clear=True)
    dye = Dye()
    assert not dye.dye_dir


def test_dye_dir_invalid_directory(mocker, tmp_path):
    invalid = tmp_path / "doesntexist"
    mocker.patch.dict(os.environ, {"DYE_DIR": str(invalid)})
    dye = Dye()
    assert dye.dye_dir == invalid


#
# test Dye.main(), the entry point for the command line script
#
def test_dye_main(mocker):
    # we are just testing main() here, as long as it dispatches, we don't
    # care what the dispatch_list() function returns in this test
    dmock = mocker.patch("dye.Dye.command_agents")
    dmock.return_value = Dye.EXIT_SUCCESS
    assert Dye.main(["agents"]) == Dye.EXIT_SUCCESS


def test_dye_main_unknown_command():
    assert Dye.main(["unknowncommand"]) == Dye.EXIT_USAGE


def test_dispatch_unknown_command(capsys):
    # but by calling dispatch() directly, we can get our own errors
    # first we have to parse valid args
    dye = Dye()
    parser = dye.argparser()
    args = parser.parse_args(["agents"])
    # and then substitute a fake command
    args.command = "fredflintstone"
    exit_code = dye.dispatch("dye", args)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_USAGE
    assert not out
    assert "unknown command" in err


def test_error_styled_unknown_command(mocker, capsys):
    create_error_console = mocker.patch("dye.Dye._create_error_console")
    create_error_console.return_value = rich.console.Console(
        stderr=True,
        soft_wrap=True,
        markup=False,
        emoji=False,
        highlight=False,
        color_system="truecolor",
        width=2048,
    )
    mocker.patch.dict(
        os.environ,
        {"DYE_COLORS": "error_progname=red:error_text=#00ff00"},
        clear=True,
    )
    dye = Dye()
    argv = ["agents"]
    (_, args) = dye.parse_args(argv)
    args.command = "fredflintstone"
    exit_code = dye.dispatch("dye", args)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_USAGE
    assert not out
    assert "unknown command" in err
    # ANSI escape codes should be present because styles are applied
    assert "\x1b[" in err


def test_error_styled_exception(mocker, capsys):
    create_error_console = mocker.patch("dye.Dye._create_error_console")
    create_error_console.return_value = rich.console.Console(
        stderr=True,
        soft_wrap=True,
        markup=False,
        emoji=False,
        highlight=False,
        color_system="truecolor",
        width=2048,
    )
    mocker.patch.dict(
        os.environ,
        {"DYE_COLORS": "error_progname=red:error_text=#00ff00"},
        clear=True,
    )
    dye = Dye()
    argv = ["agents"]
    (_, args) = dye.parse_args(argv)
    # mock command_agents to raise a DyeError
    mocker.patch.object(dye, "command_agents", side_effect=DyeError("test error"))
    exit_code = dye.dispatch("dye", args)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_ERROR
    assert not out
    assert "test error" in err
    assert "dye: " in err
    # ANSI escape codes should be present because styles are applied
    assert "\x1b[" in err


def test_debug_styled_output(mocker, capsys):
    create_error_console = mocker.patch("dye.Dye._create_error_console")
    create_error_console.return_value = rich.console.Console(
        stderr=True,
        soft_wrap=True,
        markup=False,
        emoji=False,
        highlight=False,
        color_system="truecolor",
        width=2048,
    )
    mocker.patch.dict(
        os.environ,
        {"DYE_COLORS": "debug_label=red:debug_text=#00ff00"},
        clear=True,
    )
    dye = Dye()
    msg = "Hello there. General Kenobi."
    argv = ["-d", "print", "--no-theme", "--no-pattern", msg]
    (_, args) = dye.parse_args(argv)
    exit_code = dye.dispatch("dye", args)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert "[debug]" in err
    assert msg in out
    # ANSI escape codes should be present because styles are applied
    assert "\x1b[" in err


def test___main__(mocker):
    mocker.patch("dye.Dye.main", return_value=42)
    mocker.patch.object(mainmodule, "__name__", "__main__")
    with pytest.raises(SystemExit) as excinfo:
        mainmodule.bootstrap()
    # unpack the exception to see if got the return value
    assert excinfo.value.code == 42


#
# test all the variations of load_theme_from_args()
#
# I gave up trying to descriptively name these tests, there are too
# many combinations. The test names would have been 90 characters long.
# at the top of each test is a comment describing the combination this
# test validates
LOAD_THEME1_ARGVS = [
    "apply",
    "preview",
]


@pytest.mark.parametrize("argv", LOAD_THEME1_ARGVS)
def test_load_theme_from_args_apply1(argv, mocker):
    # no environment
    # argv = "apply"
    # required = True and False
    mocker.patch.dict(os.environ, {}, clear=True)
    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    with pytest.raises(DyeError):
        dye.load_theme_from_args(args, required=True)

    theme = dye.load_theme_from_args(args, required=False)
    assert not theme


def test_load_theme_from_args_apply2(mocker):
    # no environment
    # argv = "apply --no-theme"
    # required = False
    argv = "apply --no-theme"
    mocker.patch.dict(os.environ, {}, clear=True)
    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    with pytest.raises(DyeError):
        dye.load_theme_from_args(args, required=True)

    theme = dye.load_theme_from_args(args, required=False)
    assert theme.colors == {}
    assert theme.styles == {}


def test_load_theme_from_args_apply3(mocker, tmp_path):
    # no environment
    # argv = "apply --theme-file {exists}"
    # required = True and False

    mocker.patch.dict(os.environ, {}, clear=True)

    # go write a theme file that we can actually open
    themefile = tmp_path / "sometheme.toml"
    toml = """
    [styles]
    text = "#ffcc00 on #003322"
    """
    with open(themefile, "w", encoding="utf8") as fvar:
        fvar.write(toml)

    argv = f"apply --theme-file {themefile}"

    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    theme = dye.load_theme_from_args(args, required=True)
    assert isinstance(theme.styles["text"], rich.style.Style)

    theme = dye.load_theme_from_args(args, required=False)
    assert isinstance(theme.styles["text"], rich.style.Style)


def test_load_theme_from_args_apply4(mocker, tmp_path):
    # no environment
    # argv = "apply --theme-file {doesn't exist}"
    # required = True and False

    mocker.patch.dict(os.environ, {}, clear=True)

    # a theme file that doesn't exist
    themefile = tmp_path / "doesntexisttheme.toml"

    argv = f"apply --theme-file {themefile}"

    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    with pytest.raises(FileNotFoundError):
        dye.load_theme_from_args(args, required=True)
    with pytest.raises(FileNotFoundError):
        dye.load_theme_from_args(args, required=False)


def test_load_theme_from_args_apply5(mocker, tmp_path):
    # DYE_THEME_FILE exists
    # argv = "apply"
    # required = True and False

    # go write a theme file that we can actually open
    themefile = tmp_path / "sometheme.toml"
    toml = """
    [styles]
    text = "#ffcc00 on #003322"
    """
    with open(themefile, "w", encoding="utf8") as fvar:
        fvar.write(toml)

    mocker.patch.dict(os.environ, {"DYE_THEME_FILE": f"{themefile}"}, clear=True)

    argv = "apply"
    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    theme = dye.load_theme_from_args(args, required=True)
    assert isinstance(theme.styles["text"], rich.style.Style)
    theme = dye.load_theme_from_args(args, required=False)
    assert isinstance(theme.styles["text"], rich.style.Style)


def test_load_theme_from_args_apply6(mocker, tmp_path):
    # DYE_THEME_FILE exists
    # argv = "apply --theme-file {exists}"
    # required = True and False

    # go write a theme file that we can actually open
    envfile = tmp_path / "sometheme.toml"
    toml = """
    [styles]
    text = "#ffcc00 on #003322"
    """
    with open(envfile, "w", encoding="utf8") as fvar:
        fvar.write(toml)

    mocker.patch.dict(os.environ, {"DYE_THEME_FILE": f"{envfile}"}, clear=True)

    cmdfile = tmp_path / "othertheme.toml"
    toml = """
    [styles]
    current_line = "#ffcc00 on #003322"
    """
    with open(cmdfile, "w", encoding="utf8") as fvar:
        fvar.write(toml)

    argv = f"apply --theme-file {cmdfile}"
    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    theme = dye.load_theme_from_args(args, required=True)
    assert isinstance(theme.styles["current_line"], rich.style.Style)
    assert "text" not in theme.styles

    theme = dye.load_theme_from_args(args, required=False)
    assert isinstance(theme.styles["current_line"], rich.style.Style)
    assert "text" not in theme.styles


def test_load_theme_from_args_apply7(mocker, tmp_path):
    # DYE_THEME_FILE exists
    # argv = "apply --no-theme"
    # required = True and False

    # go write a theme file that we can actually open
    themefile = tmp_path / "sometheme.toml"
    toml = """
    [styles]
    text = "#ffcc00 on #003322"
    """
    with open(themefile, "w", encoding="utf8") as fvar:
        fvar.write(toml)

    mocker.patch.dict(os.environ, {"DYE_THEME_FILE": f"{themefile}"}, clear=True)

    argv = "apply --no-theme"
    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    with pytest.raises(DyeError):
        dye.load_theme_from_args(args, required=True)
    theme = dye.load_theme_from_args(args, required=False)
    assert theme.styles == {}


#
# test all the variations of load_pattern_from_args()
#
# I gave up trying to descriptively name these tests, there are too
# many combinations. The test names would have been 90 characters long.
# at the top of each test is a comment describing the combination this
# test validates
def test_load_pattern_from_args1(mocker):
    # no environment
    # argv = "print"
    # required = True and False
    argv = "print"
    mocker.patch.dict(os.environ, {}, clear=True)
    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    with pytest.raises(DyeError):
        dye.load_pattern_from_args(args, required=True)

    pattern = dye.load_pattern_from_args(args, required=False)
    assert pattern.colors == {}
    assert pattern.styles == {}


def test_load_pattern_from_args2(mocker):
    # no environment
    # argv = "print --no-pattern"
    # required = False
    argv = "print --no-pattern"
    mocker.patch.dict(os.environ, {}, clear=True)
    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    with pytest.raises(DyeError):
        dye.load_pattern_from_args(args, required=True)

    pattern = dye.load_pattern_from_args(args, required=False)
    assert pattern.colors == {}
    assert pattern.styles == {}


def test_load_pattern_from_args3(mocker, tmp_path):
    # no environment
    # argv = "print --pattern-file {exists}"
    # required = True and False

    mocker.patch.dict(os.environ, {}, clear=True)

    pattern_file = tmp_path / "pattern.toml"
    toml = """
    [styles]
    text = "#ffcc00 on #003322"
    """
    with open(pattern_file, "w", encoding="utf8") as fvar:
        fvar.write(toml)

    argv = f"print --pattern-file {pattern_file}"
    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    theme = dye.load_pattern_from_args(args, required=True)
    assert isinstance(theme.styles["text"], rich.style.Style)

    theme = dye.load_pattern_from_args(args, required=False)
    assert isinstance(theme.styles["text"], rich.style.Style)


def test_load_pattern_from_args4(mocker, tmp_path):
    # no environment
    # argv = "print --pattern-file {doesn't exist}"
    # required = True and False

    mocker.patch.dict(os.environ, {}, clear=True)

    pattern_file = tmp_path / "doesntexistpattern.toml"

    argv = f"print --pattern-file {pattern_file} something"
    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    with pytest.raises(FileNotFoundError):
        dye.load_pattern_from_args(args, required=True)
    with pytest.raises(FileNotFoundError):
        dye.load_pattern_from_args(args, required=False)


def test_load_pattern_from_args5(mocker, tmp_path):
    # DYE_PATTERN_FILE exists
    # argv = "print"
    # required = True and False

    pattern_file = tmp_path / "pattern.toml"
    toml = """
    [styles]
    text = "#ffcc00 on #003322"
    """
    with open(pattern_file, "w", encoding="utf8") as fvar:
        fvar.write(toml)

    mocker.patch.dict(os.environ, {"DYE_PATTERN_FILE": f"{pattern_file}"}, clear=True)

    argv = "apply"
    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    theme = dye.load_pattern_from_args(args, required=True)
    assert isinstance(theme.styles["text"], rich.style.Style)
    theme = dye.load_pattern_from_args(args, required=False)
    assert isinstance(theme.styles["text"], rich.style.Style)


def test_load_pattern_from_args6(mocker, tmp_path):
    # DYE_PATTERN_FILE exists
    # argv = "apply --pattern-file {exists}"
    # required = True and False

    envfile = tmp_path / "envpattern.toml"
    toml = """
    [styles]
    text = "#ffcc00 on #003322"
    """
    with open(envfile, "w", encoding="utf8") as fvar:
        fvar.write(toml)

    mocker.patch.dict(os.environ, {"DYE_PATTERN_FILE": f"{envfile}"}, clear=True)

    cmdfile = tmp_path / "cmdpattern.toml"
    toml = """
    [styles]
    current_line = "#ffcc00 on #003322"
    """
    with open(cmdfile, "w", encoding="utf8") as fvar:
        fvar.write(toml)

    argv = f"print --pattern-file {cmdfile}"
    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    theme = dye.load_pattern_from_args(args, required=True)
    assert isinstance(theme.styles["current_line"], rich.style.Style)
    assert "text" not in theme.styles

    theme = dye.load_pattern_from_args(args, required=False)
    assert isinstance(theme.styles["current_line"], rich.style.Style)
    assert "text" not in theme.styles


def test_load_pattern_from_args7(mocker, tmp_path):
    # DYE_PATTERN_FILE exists
    # argv = "print --no-pattern"
    # required = True and False

    pattern_file = tmp_path / "sometheme.toml"
    toml = """
    [styles]
    text = "#ffcc00 on #003322"
    """
    with open(pattern_file, "w", encoding="utf8") as fvar:
        fvar.write(toml)

    mocker.patch.dict(os.environ, {"DYE_PATTERN_FILE": f"{pattern_file}"}, clear=True)

    argv = "print --no-pattern"
    dye = Dye()
    (_, args) = dye.parse_args(argv.split())

    with pytest.raises(DyeError):
        dye.load_pattern_from_args(args, required=True)
    theme = dye.load_pattern_from_args(args, required=False)
    assert theme.styles == {}
