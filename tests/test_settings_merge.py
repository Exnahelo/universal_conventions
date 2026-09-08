import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "settings_merge", ROOT / "scripts/apply_vscode_settings.py"
)
settings_merge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings_merge)


class SettingsMergeTests(unittest.TestCase):
    def test_preserves_unrelated_nested_settings(self):
        current = {"personal": 42, "[python]": {"editor.codeActionsOnSave": {"custom": "explicit"}}}
        baseline = {"[python]": {"editor.codeActionsOnSave": {"source.fixAll.ruff": "explicit"}}}
        result = settings_merge.merge(current, baseline)
        self.assertEqual(result["personal"], 42)
        self.assertEqual(result["[python]"]["editor.codeActionsOnSave"]["custom"], "explicit")
        self.assertNotIn("source.fixAll.ruff", current["[python]"]["editor.codeActionsOnSave"])

    def test_preview_does_not_write_and_apply_backs_up_exact_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            original = '{"personal":42}\n'
            path.write_text(original)
            settings_merge.apply(path, {"editor.formatOnSave": True})
            self.assertEqual(path.read_text(), original)
            self.assertEqual(len(list(Path(directory).iterdir())), 1)
            settings_merge.apply(path, {"editor.formatOnSave": True}, write=True)
            self.assertEqual(json.loads(path.read_text())["personal"], 42)
            self.assertEqual(next(Path(directory).glob("*.backup-*")).read_text(), original)
            self.assertEqual(settings_merge.apply(path, {"editor.formatOnSave": True}), [])

    def test_invalid_json_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text("{ // comment\n}")
            with self.assertRaises(ValueError):
                settings_merge.apply(path, {}, write=True)
            self.assertEqual(path.read_text(), "{ // comment\n}")


if __name__ == "__main__":
    unittest.main()
