# Universal conventions

Version 2.0 — reviewed September 8, 2026.

This is the shared policy for new authored code and documents. It covers naming,
formatting, and the boundary between automatic checks and human review. Detailed
prose guidance is in [writing-style.md](writing-style.md). Machine configurations
live in [the starter kit](vscode-conventions-starter/README-starter-kit.md).

## Precedence and local differences

1. Follow explicit task/assignment requirements and required language, tool,
   framework, and external-interface contracts.
2. Follow documented project overrides in `conventions.local.md` and the matching
   native configuration files.
3. Use this shared policy for everything else.

A Markdown policy file does not configure a tool. Record each override's scope,
reason, and corresponding setting. Preserve established public names unless a
separate compatibility change is authorized. Do not rename external API keys,
framework callbacks, generated identifiers, or required filenames for appearance.

## Naming by category

| Category                                        | Default                                                                                   |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------- |
| General authored directories                    | `snake_case`; ecosystem-required paths take precedence                                    |
| Python files, modules, functions, variables     | `snake_case`; semantic leading underscores allowed                                        |
| Python classes and exceptions                   | `PascalCase`                                                                              |
| Python constants                                | `UPPER_SNAKE_CASE`                                                                        |
| Java packages                                   | lowercase dot notation                                                                    |
| Java types and source files                     | `PascalCase`; public type matches filename                                                |
| Java methods, fields, local variables           | `camelCase`                                                                               |
| Java constants                                  | `UPPER_SNAKE_CASE`                                                                        |
| C++ types                                       | `PascalCase`                                                                              |
| C++ functions                                   | `PascalCase`; accessor and standard-library-compatible names may use `snake_case`         |
| C++ variables and namespaces                    | `snake_case`; class data members have a trailing underscore                               |
| C++ named constants and enum values             | `kPascalCase`                                                                             |
| C++ files                                       | `snake_case.cc` / `snake_case.h`; `.cpp` / `.hpp` accepted for project/tool compatibility |
| C functions, variables, files                   | `snake_case`; macros `UPPER_SNAKE_CASE`                                                   |
| Rust modules, files, functions, variables       | `snake_case`                                                                              |
| Rust types, traits, enum variants               | `PascalCase`                                                                              |
| Rust constants and statics                      | `UPPER_SNAKE_CASE`                                                                        |
| JavaScript / TypeScript variables and functions | `camelCase`                                                                               |
| JavaScript / TypeScript types and components    | `PascalCase`                                                                              |
| JavaScript / TypeScript true named constants    | `UPPER_SNAKE_CASE`; ordinary `const` bindings remain `camelCase`                          |
| JS/TS component files                           | `PascalCase`; other files `kebab-case`                                                    |
| Shell functions, variables, scripts             | `snake_case`; exported variables and constants `UPPER_SNAKE_CASE`                         |
| Internal JSON, YAML, TOML keys                  | `snake_case`; schemas/tool contracts override this                                        |
| SQL tables, columns, indexes                    | `snake_case`; plural table names by default                                               |
| HTML/CSS classes, web assets, URL slugs         | `kebab-case`                                                                              |
| General authored Markdown                       | `kebab-case.md`                                                                           |
| Branches                                        | descriptive `kebab-case` after a purpose prefix, including `codex/`                       |

Use descriptive names. Avoid unnecessary abbreviations. Prefer conventional
acronyms such as ID and URL, rendered according to each language's conventions.
Use exact tool names: `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `LICENSE`,
`Makefile`, `CMakeLists.txt`, `Cargo.toml`, `Cargo.lock`, and similar contracts.
No blanket lowercasing of test classes: `PaymentServiceTest.java` is valid.
Python tests use `test_<subject>.py`; JS/TS tests may use `.test` or `.spec`.

## C++ decision

C++ has no single mandatory industry naming/formatting standard. Adopt the
published Google C++ naming and formatting conventions as this policy's concrete
default. Use the C++ Core Guidelines for broader correctness and design advice.
This does not import Google's project-specific bans or architecture decisions;
C++ language version, exceptions, RTTI, dependencies, and build system remain
project decisions. Keep standard-library-compatible APIs and external callbacks.

Google formatting uses two-space indentation and an 80-column target. These are
language-specific conventions, not a claim that every language needs the same
line width. Existing projects may document a different established style.

## Formatting and checks

| Language                        | Formatter / checker                                              | Default                                       |
| ------------------------------- | ---------------------------------------------------------------- | --------------------------------------------- |
| Python                          | Ruff formatter and linter                                        | 100 columns, four spaces, double quotes, LF   |
| C/C++                           | Clang-Format; Clang-Tidy when compilation context exists         | Google formatting; selected C++ naming checks |
| Java                            | Oracle Java formatter; optional project Checkstyle naming config | formatter defaults; Java naming rules         |
| Rust                            | rustfmt; compiler and Clippy                                     | standard rustfmt defaults                     |
| JS/TS, JSON, HTML/CSS, Markdown | Prettier                                                         | two spaces; preserve prose wrapping           |
| YAML                            | Red Hat YAML formatter and schema support                        | two spaces                                    |
| TOML                            | Even Better TOML                                                 | native formatting                             |
| Shell                           | ShellCheck/shfmt when a project uses shell code                  | select and pin tools in that project          |
| SQL                             | dialect-aware project tooling                                    | do not guess a SQL dialect globally           |

One formatter owns each language on save. Linters report problems; only safe
Python fixes and import sorting run automatically. Identifier and file renames
require review. JSON/YAML/TOML formatting does not enforce key naming: use the
actual schema or project validation. A generic key renamer would break tools.

The Python baseline uses E4/E7/E9, F, I, B, UP, and N. Do not enable all style
rules: formatter-incompatible checks and line-length warnings can fight valid
formatter output. Each project declares its own supported Python version.

## Originals and derived documents

Reserve directories named `originals` for unmodified imported source material.
Preserve source filenames exactly as imported, even if they contain spaces,
capitalization, or download-generated names. Classification is explicit: do not
infer whether a filename is meaningful. Record a descriptive title separately.

Only originals are exempt. Place summaries, extracted Markdown, OCR output,
notes, and other derivatives outside `originals`, with the naming convention
for their own file type. Example:

- `originals/Module 2 - Lecture Slides.pdf`
- `notes/module-2-lecture-slides.md`

The old same-stem mirror rule is retired. Preserve provenance through a source
reference, not a naming exception: source path/original filename, source URL or
identifier when available, and an optional checksum for exact identity. Avoid
collisions with descriptive suffixes or stable source IDs. Do not overwrite one
derivative because two different sources normalize to the same name.

The checker skips original directories and explicitly configured original paths.
The shared editor marks `**/originals/**` read-only. Formatter/linter exclusions
are defense in depth, not permission to put derived work in the exempt directory.
Project-specific original paths need matching editor and tool exclusions.

## Existing projects and migrations

Adopt gradually. Formatting happens on save; check naming when developing and in
CI after the project's exceptions are reviewed. Never automatically rename on
open/save. Rename authored files as a separate reviewed change, updating imports,
links, manifests, citations, and tests. Preserve original source files throughout.
For a large legacy project, start with a documented baseline rather than blocking
unrelated work on every historical filename. Do not silently accumulate exceptions.

## Source retention

Keep originals during active coursework. Semester closeout is a separate,
user-triggered review, not a scheduled deletion or formatter operation. See
[the proposed closeout protocol](docs/semester-closeout.md). No deletion command,
retention scheduler, or closeout automation is included in this release.

## Sources and scope

- [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines.html)
- [Python PEP 8](https://peps.python.org/pep-0008/)
- [Ruff formatter compatibility](https://docs.astral.sh/ruff/formatter/)
- [Rust Style Guide](https://doc.rust-lang.org/style-guide/)
- [VS Code settings precedence](https://code.visualstudio.com/docs/configure/settings)

These references inform the baseline; this repository does not claim a universal
industry standard for choices on which established projects differ.
