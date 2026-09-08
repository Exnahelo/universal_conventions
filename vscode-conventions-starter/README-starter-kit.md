# VS Code conventions starter kit

This is a set of files to select and merge, not a bulk overwrite installer.
The shared policy is [conventions.md](../conventions.md), version 2.0.

## Included files

- `.vscode/settings.json`: explicit formatter owners and fallback settings.
- `.vscode/extensions.json`: recommended extensions; not automatic installation.
- `.vscode/tasks.json`: `check:naming` task with Problems-panel diagnostics.
- `.editorconfig`: basic whitespace settings.
- `.naming-rules.json` and `scripts/check_naming.py`: original exclusions and filename checks.
- `pyproject.toml`: Ruff sections; merge with existing project metadata.
- `.clang-format` and `.clang-tidy`: C++ baseline; select only for C++ projects.
- `checkstyle.xml`: optional Java naming checks; wire into the chosen project build.
- `.prettierrc.json` and `.prettierignore`: formatting and original exclusions.
- `.markdownlint-cli2.jsonc`: Markdown structure checks and exclusions.
- `eslint.config.mjs`: optional JavaScript-only ESLint baseline; requires `eslint`
  and `@eslint/js`. JSX/TypeScript/frameworks need their own parser/configuration.
- `conventions.local.md`: place to explain project overrides.

No pre-commit hook, SQL dialect, build system, or AI-provider instruction file is
silently installed. Existing configurations and dependencies must be merged,
not replaced. Python's supported version belongs to each project, not this kit.

## Adoption

1. Review [adoption and coverage](../docs/adoption.md).
2. Select and merge files applicable to the project; preserve existing rules.
3. Identify original-only folders; keep derivatives outside them.
4. Run `python3 scripts/check_naming.py --root .` to review filename diagnostics.
5. Add that command to project CI after reviewing legacy names and exceptions.
6. Reference the shared policy and writing style in the project's agent guidance.

The script reports only: exit 0 means clean, 1 means violations, 2 means invalid
configuration or an I/O failure. It never renames or edits files. Its optional
`--root` removes dependence on where the terminal happens to be open.
