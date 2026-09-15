# tests/test_flow_init_unit.py
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from scripts.flow_init import inspect_git_environment

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

if __name__ == "__main__":
    unittest.main()
