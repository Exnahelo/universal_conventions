\
#!/usr/bin/env python3
"""Generic repository naming checker.

Reads optional repo-local configuration from .naming-rules.json.
Prints diagnostics in a VS Code-friendly format:

relative/path:line:column: message
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path.cwd()
CONFIG_PATH = ROOT / ".naming-rules.json"

SNAKE_CASE_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PASCAL_CASE_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")

ROOT_DOC_EXACT = {
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
}
ROOT_EXACT_DEFAULT = ROOT_DOC_EXACT | {
    "LICENSE",
    "LICENSE.md",
    "CODE_OF_CONDUCT.md",
    "SUPPORT.md",
    "Makefile",
}

IGNORE_DIRS_DEFAULT = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
}

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {
            "ignore_dirs": sorted(IGNORE_DIRS_DEFAULT),
            "root_exact_names": sorted(ROOT_EXACT_DEFAULT),
            "mirrored_artifacts": [],
        }
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    data.setdefault("ignore_dirs", sorted(IGNORE_DIRS_DEFAULT))
    data.setdefault("root_exact_names", sorted(ROOT_EXACT_DEFAULT))
    data.setdefault("mirrored_artifacts", [])
    return data

def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()

def emit(path: Path, message: str, line: int = 1, column: int = 1) -> None:
    print(f"{rel(path)}:{line}:{column}: {message}")

def iter_files(ignore_dirs: set[str]) -> Iterable[Path]:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignore_dirs for part in path.relative_to(ROOT).parts[:-1]):
            continue
        yield path

def stem_without_suffixes(path: Path) -> str:
    name = path.name
    for suffix in path.suffixes:
        name = name[: -len(suffix)]
    return name

def is_root_file(path: Path) -> bool:
    return path.parent == ROOT

def check_filename_spaces(path: Path) -> None:
    if " " in path.name:
        emit(path, "filename contains spaces")

def check_python_file(path: Path) -> None:
    name = path.name
    stem = path.stem
    if name in {"__init__.py", "conftest.py"}:
        return
    if stem.startswith("test_"):
        if not SNAKE_CASE_RE.fullmatch(stem):
            emit(path, "Python test file must be snake_case with test_ prefix")
        return
    if not SNAKE_CASE_RE.fullmatch(stem):
        emit(path, "Python module filename must be snake_case")

def check_markdown_file(path: Path, root_exact_names: set[str], mirrored_paths: set[Path]) -> None:
    name = path.name
    stem = path.stem
    if path in mirrored_paths:
        return
    if is_root_file(path) and name in root_exact_names:
        return
    if not KEBAB_CASE_RE.fullmatch(stem):
        emit(path, "general Markdown filename must be kebab-case")

def check_shell_file(path: Path) -> None:
    stem = path.stem
    if not SNAKE_CASE_RE.fullmatch(stem):
        emit(path, "shell script filename must be snake_case")

def check_js_file(path: Path) -> None:
    stem = path.stem
    if PASCAL_CASE_RE.fullmatch(stem):
        return
    if KEBAB_CASE_RE.fullmatch(stem):
        return
    emit(path, "JavaScript filename must be kebab-case or PascalCase for component files")

def build_mirror_map(config: dict) -> tuple[dict[Path, Path], set[Path]]:
    mapping: dict[Path, Path] = {}
    mirror_paths: set[Path] = set()

    for rule in config.get("mirrored_artifacts", []):
        canonical_root = ROOT / rule["canonical_root"]
        mirror_root = ROOT / rule["mirror_root"]
        canonical_exts = set(rule.get("canonical_extensions", []))
        mirror_exts = set(rule.get("mirror_extensions", []))

        if not canonical_root.exists() or not mirror_root.exists():
            continue

        canonical_index: dict[str, Path] = {}
        for path in canonical_root.rglob("*"):
            if path.is_file() and path.suffix in canonical_exts:
                relative = path.relative_to(canonical_root)
                key = str(relative.with_suffix(""))
                canonical_index[key] = path

        for path in mirror_root.rglob("*"):
            if path.is_file() and path.suffix in mirror_exts:
                relative = path.relative_to(mirror_root)
                key = str(relative.with_suffix(""))
                if key in canonical_index:
                    mapping[path] = canonical_index[key]
                    mirror_paths.add(path)
    return mapping, mirror_paths

def check_mirrors(mapping: dict[Path, Path]) -> None:
    for mirror, canonical in mapping.items():
        if mirror.stem != canonical.stem:
            emit(
                mirror,
                f"mirrored artifact stem must match canonical source stem '{canonical.stem}'"
            )

def main() -> int:
    config = load_config()
    ignore_dirs = set(config["ignore_dirs"])
    root_exact_names = set(config["root_exact_names"])
    mirror_map, mirrored_paths = build_mirror_map(config)

    for path in iter_files(ignore_dirs):
        check_filename_spaces(path)

        if path.suffix == ".py":
            check_python_file(path)
        elif path.suffix in {".md", ".markdown"}:
            check_markdown_file(path, root_exact_names, mirrored_paths)
        elif path.suffix in {".sh", ".bash"}:
            check_shell_file(path)
        elif path.suffix in {".js", ".jsx"}:
            check_js_file(path)

    check_mirrors(mirror_map)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
