import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "vscode-conventions-starter/scripts/check_naming.py"
spec = importlib.util.spec_from_file_location("check_naming", SCRIPT)
naming = importlib.util.module_from_spec(spec)
spec.loader.exec_module(naming)


class NamingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, path, text=""):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def config(self, **values):
        self.put(".naming-rules.json", json.dumps(values))

    def run_checker(self):
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--root", str(self.root)],
            cwd="/",
            text=True,
            capture_output=True,
        )

    def test_originals_preserved_derivatives_checked(self):
        source = self.put("course/originals/Actual Lecture Name.pdf", "original bytes")
        self.put("course/notes/Actual Lecture Name.md", "derived")
        self.assertEqual(len(naming.check(self.root)), 1)
        self.assertEqual(source.read_text(), "original bytes")
        self.assertEqual(self.run_checker().returncode, 1)

    def test_configured_source_paths_are_literal_and_scoped(self):
        self.config(original_paths=["sources/Source File.md"])
        self.put("sources/Source File.md")
        self.put("sources/Bad Derived.md")
        self.assertEqual([str(p) for p, _ in naming.check(self.root)], ["sources/Bad Derived.md"])

    def test_nested_original_dirs_can_be_overridden(self):
        self.config(original_dirs=["imports"])
        self.put("course/imports/Original File.pdf")
        self.put("course/originals/Derived File.md")
        self.assertEqual(len(naming.check(self.root)), 1)

    def test_valid_language_names_and_tool_names(self):
        for name in [
            "_helper.py",
            "__main__.py",
            "__init__.py",
            "test_handler.py",
            "Cargo.toml",
            "CMakeLists.txt",
            "AGENTS.md",
            "docs/README.md",
            "PaymentServiceTest.java",
            "package-info.java",
            "module-info.java",
            "conventions.local.md",
            "eslint.config.mjs",
            "event_queue.cc",
            "event_queue.hpp",
            "main.rs",
            "readme.md",
            "UserCard.test.tsx",
            "session-manager.spec.js",
            "types.d.ts",
            "notes.generated.md",
            "config.template.md",
        ]:
            self.put(name)
        self.assertEqual(naming.check(self.root), [])
        self.assertEqual(self.run_checker().returncode, 0)

    def test_unknown_old_schema_fails_instead_of_silently_ignoring(self):
        for key in ["mirrored_artifacts", "root_exact_names", "origina_paths"]:
            self.config(**{key: []})
            self.assertEqual(self.run_checker().returncode, 2)

    def test_invalid_configuration_fails(self):
        for values in [
            {"schema_version": True},
            {"schema_version": 1},
            {"original_paths": ["../outside"]},
            {"original_paths": ["/tmp"]},
            {"original_paths": ["."]},
            {"original_paths": ["**/notes"]},
            {"original_dirs": "originals"},
            {"ignore_dirs": ["a/b"]},
        ]:
            self.config(**values)
            self.assertEqual(self.run_checker().returncode, 2, values)
        self.put(".naming-rules.json", "{")
        self.assertEqual(self.run_checker().returncode, 2)

    def test_existing_sage_style_configuration_is_supported(self):
        self.config(allowed_names=["SAGE_BLUEPRINT.md"], ignore_paths=["legacy"])
        self.put("docs/SAGE_BLUEPRINT.md")
        self.put("README.md")
        self.put("legacy/Bad Name.md")
        self.assertEqual(naming.check(self.root), [])

    def test_original_path_does_not_exempt_similarly_named_sibling(self):
        self.config(original_paths=["raw"])
        self.put("raw/Original File.pdf")
        self.put("raw_derived/Bad Name.md")
        self.assertEqual(len(naming.check(self.root)), 1)

    def test_does_not_traverse_symlink_directories(self):
        with tempfile.TemporaryDirectory() as external:
            Path(external, "Bad Name.md").write_text("source")
            (self.root / "linked").symlink_to(external, target_is_directory=True)
            self.assertEqual(naming.check(self.root), [])

    def test_reports_invalid_java_rust_and_typescript_names(self):
        for name in ["bad_class.java", "BadModule.rs", "bad_component.tsx"]:
            self.put(name)
        self.assertEqual(len(naming.check(self.root)), 3)

    def test_configuration_symlinks_are_rejected(self):
        self.put("config.json", "{}")
        (self.root / ".naming-rules.json").symlink_to(self.root / "config.json")
        self.assertEqual(self.run_checker().returncode, 2)


if __name__ == "__main__":
    unittest.main()
