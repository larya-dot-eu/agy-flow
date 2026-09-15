# tests/test_flow_init_unit.py
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from scripts.flow_init import (
    inspect_git_environment,
    detect_project_stack,
    discover_subsystems,
    generate_gemini_and_agents_md,
    scaffold_context_and_adr,
)

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

class TestTopologyDetector(unittest.TestCase):
    def test_discover_standard_subsystems(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "src" / "auth").mkdir(parents=True)
            (root / "src" / "api").mkdir(parents=True)
            (root / "tests").mkdir()
            subsystems = discover_subsystems(root)
            paths = [s[0] for s in subsystems]
            self.assertTrue(any("src/auth" in p or "src" in p for p in paths))


class TestGeminiAndAgentsScaffolder(unittest.TestCase):
    def test_gemini_md_and_agents_symlink_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            stack = {"languages": ["Python"], "build_tools": ["pytest"], "test_cmd": "pytest", "dev_cmd": None}
            subsystems = [("src/**", "docs/context/src.md", "Source Code")]
            gemini_path, agents_path = generate_gemini_and_agents_md(root, "test-app", stack, subsystems, force=True)
            self.assertTrue(gemini_path.exists())
            self.assertTrue(agents_path.exists())
            content = gemini_path.read_text(encoding="utf-8")
            self.assertIn("## Stack", content)
            self.assertIn("## Context Routing Map", content)
            self.assertIn("<!-- ANCHOR: CONTEXT_ROUTING -->", content)

class TestContextAndAdrScaffolder(unittest.TestCase):
    def test_scaffold_context_and_adr_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            subsystems = [("src/auth/**", "docs/context/src-auth.md", "Auth Subsystem")]
            created = scaffold_context_and_adr(root, subsystems, force=True)
            self.assertTrue((root / "docs" / "context" / "src-auth.md").exists())
            self.assertTrue((root / "docs" / "adr" / "README.md").exists())

if __name__ == "__main__":
    unittest.main()
