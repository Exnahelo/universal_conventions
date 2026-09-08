import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]


class ConfigurationTests(unittest.TestCase):
    def test_settings_and_starter_share_one_baseline(self):
        shared = json.loads((ROOT / "config/vscode-user-settings.json").read_text())
        starter = json.loads(
            (ROOT / "vscode-conventions-starter/.vscode/settings.json").read_text()
        )
        self.assertEqual(shared, starter)
        self.assertEqual(shared["ruff.configurationPreference"], "filesystemFirst")
        self.assertEqual(shared["ruff.configuration"]["line-length"], 100)
        self.assertEqual(shared["C_Cpp.clang_format_style"], "file")
        self.assertEqual(shared["C_Cpp.clang_format_fallbackStyle"], "Google")
        self.assertTrue(shared["files.readonlyInclude"]["**/originals/**"])
        self.assertFalse(shared["ruff.configuration"]["unsafe-fixes"])
        self.assertFalse(shared["[markdown]"]["files.trimTrailingWhitespace"])

    def test_python_project_and_editor_rules_agree(self):
        project = tomllib.loads((ROOT / "vscode-conventions-starter/pyproject.toml").read_text())
        editor = json.loads((ROOT / "config/vscode-user-settings.json").read_text())
        for key in ["line-length", "lint", "format", "extend-exclude"]:
            self.assertEqual(project["tool"]["ruff"][key], editor["ruff.configuration"][key])

    def test_configuration_syntax(self):
        for path in ROOT.rglob("*"):
            if path.suffix == ".json":
                json.loads(path.read_text())
        ET.parse(ROOT / "vscode-conventions-starter/checkstyle.xml")


if __name__ == "__main__":
    unittest.main()
