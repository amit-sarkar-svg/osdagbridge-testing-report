# [Docs/CLI] README documents CLI usage but installed CLI entrypoint is a stub that ignores arguments

**Filed:** [Nidhikhare12/OsdagBridge#101](https://github.com/Nidhikhare12/OsdagBridge/issues/101) — open (filed 2026-11-15)

**Environment**
- OsdagBridge `dev` @ `d74f56d` (2026-07-26)
- macOS (Intel), conda env `osdagbridge-env`, Python 3.12.16
- Finding type: **T6 (documentation/usage vs actual behavior)**

**Description**
`README.md` presents the project as supporting a CLI interface and documents example CLI commands, but the installed console script resolves to a stub implementation that prints a fixed message and ignores all arguments (including `--help`). This makes the documented CLI workflow unusable as written and can confuse users/contributors.

**README claims/examples**
- `README.md:4` — "It supports desktop (PySide6), web (Django + React), and CLI interfaces through a unified Python core."
- `README.md:18` — "The desktop GUI, web app, and CLI all reuse the same core for consistent behavior."
- `README.md:102` — documents `osdagbridge analyze project.yaml --solver native`
- `README.md:108` — documents `osdagbridge report project.yaml report.pdf`
- `README.md:154` — lists CLI code location: `src/osdagbridge/cli/`

**Actual behavior (evidence)**
- `pyproject.toml:85` declares console script: `osdagbridge-cli = "osdagbridge.cli.__main__:main"`
- `src/osdagbridge/cli/__main__.py`:
  ```py
  """CLI entrypoint."""
  def main():
      print("osdagbridge CLI (stub)")

  if __name__ == "__main__":
      main()
  ```
- Invocations print the stub and ignore arguments/flags (exit 0), e.g.:
  - `osdagbridge-cli --help` → `osdagbridge CLI (stub)`
  - `osdagbridge-cli analyze project.yaml` → `osdagbridge CLI (stub)`
  (recorded in `evidence/logs/phase1_entrypoints.txt`; `tests/test_phase1_packaging.py::test_cli_stub_ignores_args` confirms stub behavior)

**Expected behavior**
Either (a) the CLI should implement (or clearly route to) the documented commands/flags, or (b) the README should clearly mark the CLI as unimplemented/stub and avoid presenting non-functional command examples as usable.

**Actual behavior**
README documents CLI support and example commands, but the CLI entrypoint is a stub that ignores arguments and provides no help/command handling.

**Impact**
- Users following README CLI examples cannot run analysis/report generation via the documented CLI.
- Misleading contributor/user expectations about available interfaces (desktop/web/CLI parity).

**Suggested fix**
- Implement argument parsing and the documented commands (`analyze`, `report`, etc.) in the CLI entrypoint, **or**
- Update README to clearly label the CLI as a stub/WIP, remove or annotate non-functional examples, and document the actual supported way to run/analyze (if any) until CLI is implemented.
- Consider aligning the documented executable name/usage (`osdagbridge ...` in README) with the installed console script name (`osdagbridge-cli` in `pyproject.toml`) if both are intended.

**Duplicate check**
Searched existing OsdagBridge issues (open+closed, full titles/bodies) for README/CLI/`osdagbridge-cli`/stub terms — no matching issue found (CLI-related UI "click" mentions in other issues are unrelated). (Not #96.)

**Notes**
`src/osdagbridge/cli/commands.py` exists in the source tree; this report is limited to the installed/documented entrypoint behavior observed at `dev @ d74f56d`.
