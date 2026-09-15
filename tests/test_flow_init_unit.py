# tests/test_flow_init_unit.py
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from scripts.flow_init import inspect_git_environment, detect_project_stack

class TestGitEnvironmentInspector(unittest.TestCase):
    def test_git_detected_in_git_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            info = inspect_git_environment(root, allow_git_init=False, skip_git=False)
            self.assertTrue(info["is_git_repo"])
            self.assertFalse(info["git_initialized"])

    def test_git_init_when_allowed_on_non_git(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            info = inspect_git_environment(root, allow_git_init=True, skip_git=False)
            self.assertTrue(info["is_git_repo"])
            self.assertTrue(info["git_initialized"])
            self.assertTrue((root / ".gitignore").exists())

    def test_git_skipped_when_requested(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            info = inspect_git_environment(root, allow_git_init=False, skip_git=True)
            self.assertFalse(info["is_git_repo"])

class TestStackDetector(unittest.TestCase):
    def test_detect_python_pytest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "pyproject.toml").write_text("[tool.pytest]\n", encoding="utf-8")
            (root / "requirements.txt").write_text("pytest\n", encoding="utf-8")
            stack = detect_project_stack(root)
            self.assertIn("Python", stack["languages"])
            self.assertEqual(stack["test_cmd"], "pytest")

    def test_detect_node_vitest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "package.json").write_text('{"scripts": {"test": "vitest run"}}', encoding="utf-8")
            stack = detect_project_stack(root)
            self.assertIn("TypeScript / JavaScript", stack["languages"])
            self.assertEqual(stack["test_cmd"], "npm test")

    def test_detect_rust_cargo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "Cargo.toml").write_text('[package]\nname = "test"\n', encoding="utf-8")
            stack = detect_project_stack(root)
            self.assertIn("Rust", stack["languages"])
            self.assertEqual(stack["test_cmd"], "cargo test")

if __name__ == "__main__":
    unittest.main()
