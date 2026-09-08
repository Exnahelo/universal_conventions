#!/usr/bin/env python3
"""Read-only filename checks. Exit 0: clean; 1: violations; 2: configuration/I/O error."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path, PurePosixPath

DEFAULT_IGNORES = {
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "node_modules",
    "vendor",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "build",
    "dist",
    "target",
}
EXACT_NAMES = {
    "README.md",
    "AGENTS.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "SUPPORT.md",
    "TODO.md",
    "LICENSE",
    "LICENSE.md",
    "Makefile",
    "CMakeLists.txt",
    "Cargo.toml",
    "Cargo.lock",
    "module-info.java",
    "package-info.java",
    "__init__.py",
    "__main__.py",
    "conftest.py",
    "conventions.local.md",
    "eslint.config.mjs",
    "eslint.config.js",
    "eslint.config.cjs",
    "prettier.config.js",
    "prettier.config.mjs",
    "prettier.config.cjs",
}
LIST_KEYS = {"ignore_dirs", "ignore_paths", "original_dirs", "original_paths", "allowed_names"}
SNAKE = re.compile(r"[a-z0-9]+(?:_[a-z0-9]+)*")
KEBAB = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
PASCAL = re.compile(r"[A-Z][A-Za-z0-9]*")


def load_config(root: Path) -> dict:
    path = root / ".naming-rules.json"
    if path.is_symlink():
        raise ValueError("configuration must be a regular file, not a symlink")
    config = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if not isinstance(config, dict):
        raise ValueError("configuration must be an object")
    unknown = set(config) - LIST_KEYS - {"schema_version"}
    if unknown:
        raise ValueError(f"unsupported configuration fields: {', '.join(sorted(unknown))}")
    version = config.get("schema_version", 2)
    if type(version) is not int or version != 2:
        raise ValueError("schema_version must be 2")
    for key in LIST_KEYS:
        values = config.setdefault(key, ["originals"] if key == "original_dirs" else [])
        if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
            raise ValueError(f"{key} must be a list of nonempty strings")
        for value in values:
            if key.endswith("_paths"):
                p = PurePosixPath(value)
                if p.is_absolute() or ".." in p.parts or value in {".", "./"} or "\\" in value:
                    raise ValueError(f"{key} entries must be relative paths within the project")
                if any(c in value for c in "*?[]"):
                    raise ValueError(f"{key} entries are literal paths, not glob patterns")
            elif "/" in value or "\\" in value or value in {".", ".."}:
                raise ValueError(f"{key} entries must be single names")
    config["ignore_dirs"] = set(config["ignore_dirs"]) | DEFAULT_IGNORES
    config["allowed_names"] = set(config["allowed_names"]) | EXACT_NAMES
    config["original_dirs"] = set(config["original_dirs"])
    config["excluded_paths"] = [
        PurePosixPath(p) for p in config["ignore_paths"] + config["original_paths"]
    ]
    return config


def is_excluded(relative: Path, config: dict) -> bool:
    return any(relative == p or p in relative.parents for p in config["excluded_paths"])


def filename_error(path: Path, allowed: set[str]) -> str | None:
    name = path.name
    if name in allowed:
        return None
    if any(c.isspace() for c in name):
        return "authored filename contains whitespace"
    # Tool-specific hidden configs have their own required naming conventions.
    if name.startswith("."):
        return None
    suffix = path.suffix.lower()
    stem = path.stem
    if suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
        for marker in (".d", ".test", ".spec", ".generated", ".template"):
            if stem.endswith(marker):
                stem = stem[: -len(marker)]
        if KEBAB.fullmatch(stem) or PASCAL.fullmatch(stem):
            return None
        return "JS/TS filename must be kebab-case or PascalCase (component/type file)"
    for marker in (".generated", ".template"):
        if stem.endswith(marker):
            stem = stem[: -len(marker)]
    if suffix in {".md", ".markdown", ".html", ".css", ".scss"}:
        if KEBAB.fullmatch(stem):
            return None
        return "authored document/web filename must be kebab-case"
    if suffix == ".java":
        if PASCAL.fullmatch(stem):
            return None
        return "Java filename must be PascalCase"
    if suffix in {".py", ".rs", ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".sh", ".bash"}:
        # Semantic private Python modules and explicitly marked template files.
        if stem.startswith("_") and (suffix == ".py" or stem.startswith("_template")):
            stem = stem[1:]
        if SNAKE.fullmatch(stem):
            return None
        return "source filename must be snake_case"
    return None


def check(root: Path) -> list[tuple[Path, str]]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("root must be an existing directory")
    config = load_config(root)
    errors = []

    def raise_walk_error(error: OSError) -> None:
        raise error

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=raise_walk_error):
        parent = Path(directory)
        dirs[:] = sorted(
            d
            for d in dirs
            if d not in config["ignore_dirs"] | config["original_dirs"]
            and not (parent / d).is_symlink()
            and not is_excluded((parent / d).relative_to(root), config)
        )
        for name in sorted(files):
            path = parent / name
            relative = path.relative_to(root)
            if is_excluded(relative, config):
                continue
            message = filename_error(path, config["allowed_names"])
            if message:
                errors.append((relative, message))
    return sorted(errors)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        errors = check(args.root)
    except (OSError, ValueError) as exc:
        print(f".naming-rules.json:1:1: naming configuration error: {exc}")
        return 2
    for path, message in errors:
        print(f"{path.as_posix()}:1:1: {message}")
    print(
        f"Naming check failed with {len(errors)} violation(s)."
        if errors
        else "Naming check passed."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
