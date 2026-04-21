# VS Code Conventions Starter Kit

This folder is a ready-to-drop baseline for enforcing the naming rules from `CONVENTIONS.md`.

## What is included

- `.vscode/settings.json` — workspace editor defaults
- `.vscode/tasks.json` — a `check:naming` task that reports into Problems
- `.vscode/extensions.json` — recommended extensions
- `.editorconfig` — whitespace and newline normalization
- `pyproject.toml` — Ruff config for Python
- `eslint.config.mjs` — ESLint config for JavaScript
- `.prettierrc.json` — Prettier config
- `.markdownlint.jsonc` — Markdown lint config
- `.sqlfluff` — SQLFluff starter config
- `.pre-commit-config.yaml` — local commit gate
- `.github/copilot-instructions.md` — AI instructions
- `.github/prompts/naming-review.prompt.md` — reusable prompt
- `.naming-rules.json` — project-local naming and mirror mapping config
- `scripts/check_naming.py` — generic repository naming checker

## How to use

1. Copy these files into the root of your repo.
2. Edit `.naming-rules.json` to match your project structure.
3. Install tool dependencies:
   - Python: `pip install ruff pre-commit`
   - JavaScript: `npm install --save-dev eslint @eslint/js prettier`
   - Optional SQL: install `sqlfluff`
4. Run `pre-commit install`
5. In VS Code, run the task: **Tasks: Run Task** → `check:naming`

## Notes

- The naming checker is intentionally generic. It enforces:
  - no spaces in filenames
  - Python module names are `snake_case`
  - general Markdown docs are `kebab-case`
  - shell scripts are `snake_case`
  - JS files are `kebab-case`, or `PascalCase` for component-style files
  - mirrored artifact stem consistency where configured

- For project-specific schema rules, keep those in a separate policy file and extend the checker as needed.
