# Universal conventions

A maintained personal baseline for consistent code, filenames, editor behavior,
and writing. Version 2.0 keeps original source material intact and applies naming
rules to derivatives. Projects can override defaults explicitly.

- [Shared conventions](conventions.md)
- [Writing style](writing-style.md)
- [Adoption, precedence, and enforcement coverage](docs/adoption.md)
- [VS Code user settings to merge](config/vscode-user-settings.json)
- [Project starter kit](vscode-conventions-starter/README-starter-kit.md)
- [Semester closeout proposal](docs/semester-closeout.md)

Use the shared settings across projects. Select and merge starter configurations
when a project needs reproducible checks; explain differences in
`conventions.local.md`. A local prose file does not configure the tools itself.

Formatting runs on save. Naming problems are reported, never automatically
renamed. Directories named `originals` contain preserved imports; derived notes
and Markdown belong elsewhere and follow their own naming conventions.

## Apply shared VS Code settings

```sh
python3 scripts/apply_vscode_settings.py
python3 scripts/apply_vscode_settings.py --apply
```

The first command previews changed keys. The second merges them into the default
VS Code user settings and makes a timestamped backup. Unrelated settings are
preserved. Use `--settings PATH` for another profile. JSONC files with comments
need a manual merge; the script refuses to discard comments. This changes editor
settings only, not project files or installed extensions.

## Repository validation

```sh
python3 -m unittest discover -s tests -v
python3 vscode-conventions-starter/scripts/check_naming.py --root .
```

Tests use temporary fixtures and the standard library. No user data, external
model, or credentials are required. Optional language tools are documented in the
coverage table; their presence is not assumed by these tests.
