# CLAUDE.md

## Project Overview

`dye-your-shell` is a Python CLI tool that applies color themes to shell tools (fzf, bat, eza, GNU ls, iTerm, etc.) using TOML pattern/theme files with Jinja2 templating. Entry point: `dye = "dye.dye:Dye.main"`.

## Development Setup

```bash
uv pip install -e .[dev]     # install in editable mode with dev deps
```

Python 3.9+ required. Virtual env at `.venv/` (managed with uv).

## Common Commands

```bash
pytest                     # run tests (includes coverage via addopts)
invoke check               # run ALL checks: pytest, ruff check, ruff format check
invoke format              # format code with ruff
ruff check *.py tests src  # lint with ruff
ruff format *.py tests src # format with ruff
```

Always run `invoke check` before committing. All checks must pass.

## Testing

- Framework: pytest with pytest-mock and pytest-cov
- Test directory: `tests/`
- 100% test coverage required — PRs that reduce coverage will not be merged
- Test files follow `test_*.py` naming
- Key fixture: `dye_cmdline()` in `conftest.py` for simulating CLI execution

## Code Style

- Formatter/linter: ruff (line length 88, indent 4)
- Ruff rules: E, F, UP, B, SIM, I (isort)
- Imports: standard library, third-party, local (enforced by isort)
- No type annotations enforcement but follow existing patterns

## Writing Conventions

- Usage messages and error messages: lowercase, no periods
- Multi-phrase help text: separate with semicolons
- Argparse epilogs: capitalized sentences

## Git Workflow

- `main` — latest release (tagged with version numbers)
- `develop` — active development branch
- Feature branches merge into `develop`
- Releases: merge `develop` → `main`, tag, push to PyPI
- Versioning: semantic versioning via setuptools-scm (git tags)

## Project Structure

```
src/dye/          # source code
  dye.py          # main CLI class with arg parsing and command dispatch
  agents.py       # agent implementations (Fzf, Eza, LsColors, Iterm, Shell, etc.)
  pattern.py      # TOML pattern file loading and Jinja2 processing
  theme.py        # TOML theme file loading
  scope.py        # scope class for pattern sections
  filters.py      # Jinja2 custom filters (fg_hex, bg_hex, ansi_on, etc.)
  exceptions.py   # DyeError, DyeSyntaxError
  utils.py        # utility functions
tests/            # test suite (mirrors source structure)
themes/           # example theme files
tasks.py          # invoke task definitions
```

## Architecture Notes

- Agents use a plugin registry pattern via `AgentBase.__init_subclass__()` — new agents auto-register
- Agent names derived from class names (e.g., `LsColors` → `ls_colors`)
- Pattern/theme files are TOML with Jinja2 template support
- Rich library used for all terminal output (tables, panels, styled text)

## Dependencies

Core: rich, rich_argparse, tomlkit, Jinja2, python-benedict
Dev: pytest, pytest-mock, pytest-cov, ruff, invoke, build, twine
