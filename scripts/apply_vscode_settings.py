#!/usr/bin/env python3
"""Preview shared VS Code settings; use --apply to merge with a timestamped backup."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

BASELINE = Path(__file__).resolve().parents[1] / "config/vscode-user-settings.json"


def default_settings() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/Code/User/settings.json"
    if sys.platform == "win32":
        return Path(os.environ["APPDATA"]) / "Code/User/settings.json"
    return (
        Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "Code/User/settings.json"
    )


def merge(current: dict, baseline: dict) -> dict:
    result = dict(current)
    for key, value in baseline.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = value
    return result


def apply(settings: Path, baseline: dict, *, write: bool = False) -> list[str]:
    if settings.is_symlink():
        raise ValueError("settings path is a symlink; review its target before updating")
    original = settings.read_bytes() if settings.exists() else None
    current = json.loads(original) if original is not None else {}
    if not isinstance(current, dict):
        raise ValueError("VS Code settings must be an object")
    updated = merge(current, baseline)
    changed = sorted(k for k in updated if current.get(k) != updated[k])
    if not write or not changed:
        return changed
    settings.parent.mkdir(parents=True, exist_ok=True)
    # Refuse a concurrent change rather than overwriting new edits.
    if (settings.read_bytes() if settings.exists() else None) != original:
        raise ValueError("settings changed during review; rerun the command")
    if original is not None:
        suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = settings.with_name(settings.name + ".backup-" + suffix)
        with backup.open("xb") as stream:
            stream.write(original)
        shutil.copymode(settings, backup)
        print(f"Backup: {backup}")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=settings.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(updated, stream, indent=4)
            stream.write("\n")
        if settings.exists():
            shutil.copymode(settings, temporary)
        temporary.replace(settings)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", type=Path, default=default_settings())
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        baseline = json.loads(BASELINE.read_text())
        changed = apply(args.settings, baseline, write=args.apply)
    except (OSError, ValueError) as exc:
        print(f"No update completed: {exc}", file=sys.stderr)
        print(
            "Commented JSON/JSONC settings require a manual merge; do not strip comments blindly.",
            file=sys.stderr,
        )
        return 2
    print("Applied:" if args.apply else "Preview only; would update:")
    for key in changed:
        print(f"  {key}")
    if not changed:
        print("  No differences.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
