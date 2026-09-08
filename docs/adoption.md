# Adoption and overrides

The repository is the shared source. The VS Code user settings file is an applied
copy, not an automatically synchronized subscription. Review updates before
merging them; retain backups. Do not copy a complete settings file over unrelated
personal settings.

For a new project, select applicable starter files and merge existing files by
section. Never overwrite `pyproject.toml`, `.vscode/settings.json`, or build files.
Use `conventions.local.md` to explain each deviation, and configure the actual
tool in its native file. Pin formatter/checker versions in that project's build
or environment if repeatable CI formatting is required. Personal extensions can
update independently, so editor defaults alone are not a reproducible CI contract.

The starter kit is intentionally opt-in for existing projects. In particular,
SAGE has a different legacy naming configuration and checker. Do not replace only
one half. The v2 checker supports `allowed_names`, `ignore_dirs`, and
`ignore_paths` but deliberately rejects `root_exact_names` and
`mirrored_artifacts` from the older starter: migrate those explicitly. Convert
old mirror exceptions into source provenance plus independently named derivatives.

## Settings precedence

- VS Code workspace language settings may override personal settings. Keep a
  single-language block for each formatter to make precedence predictable.
- Ruff uses filesystem-first configuration; a local Ruff configuration takes
  precedence over the shared inline configuration. Copy/merge the shared baseline
  if a project needs to retain those checks while overriding one setting.
- Clang-Format reads `.clang-format`; the global Google style is only a fallback.
- Clang-Tidy reads `.clang-tidy`; the global fallback checks correctness only, because the C/C++ extension does not
  support a separate language override for this setting. C++ naming is enabled
  by adopting the project `.clang-tidy`, without imposing C++ naming on C.
- Prettier uses project configuration and EditorConfig ahead of editor fallback
  options. Rustfmt and other tools read their native project configurations.
- A `conventions.local.md` file explains policy but is not loaded by formatters.

## Migration strategy

Format authored files when saved. Report names through the naming task; do not
rename automatically. Review rename batches with all affected imports, links,
frontmatter references, and tests. Do not bulk reformat every old repository as
part of installing personal settings.

Use `originals` folders only for source material. Put derived Markdown elsewhere.
For imports stored in other locations, configure `original_paths` in the checker
and matching editor/formatter exclusions. The checker cannot infer provenance.

## Enforcement coverage

| Rule                  | Implementation / limitation                                                                                                   |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| File names            | v2 naming checker, VS Code task, optional project CI                                                                          |
| Original files        | checker exclusions; read-only editor pattern; Ruff/Prettier/Markdownlint/ESLint exclusions                                    |
| Python identifiers    | Ruff N rules, not all semantic distinctions such as true constants                                                            |
| C++ identifiers       | Clang-Tidy type, variable, namespace, enum, constexpr and private-member checks; function/accessor distinctions remain review |
| Java identifiers      | starter Checkstyle XML, must be wired into the project's chosen build/CI; editor formatter alone does not enforce naming      |
| Rust identifiers      | compiler naming diagnostics and Clippy; compiler settings can override severity                                               |
| JS identifiers        | optional ESLint config, camelcase warnings and correctness checks                                                             |
| TS identifiers        | formatter plus review; use the framework's TypeScript-aware lint setup                                                        |
| JSON/YAML/TOML keys   | actual project schema or validation; no generic rewrite                                                                       |
| Prose voice/citations | shared writing guidance and review, not a formatter                                                                           |
| SQL/shell             | project-specific tooling; no globally installed dialect/compiler stack                                                        |

The checker checks files, not arbitrary directory names, Git branch names, source
code identifiers, content provenance, or whether a derivative is complete. These
remain explicit review/schema/build responsibilities.
