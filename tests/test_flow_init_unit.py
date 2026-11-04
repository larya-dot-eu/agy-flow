# tests/test_flow_init_unit.py
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from scripts.flow_init import (
    inspect_git_environment,
    detect_project_stack,
    discover_subsystems,
    generate_gemini_and_agents_md,
    scaffold_context_and_adr,
    run_flow_init,
    parse_args
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

    @patch('subprocess.run')
    def test_git_config_exception_handling(self, mock_run):
        mock_run.side_effect = Exception('Git command failed')
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            info = inspect_git_environment(root, allow_git_init=False, skip_git=False)
            self.assertTrue(info['is_git_repo'])
            self.assertIsNone(info['user_name'])
            self.assertIsNone(info['user_email'])

    @patch("scripts.flow_init.subprocess.run")
    def test_gh_auth_exception_handled(self, mock_run):
        mock_run.side_effect = Exception("gh mock error")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            info = inspect_git_environment(root, allow_git_init=False, skip_git=False)
            self.assertIsNone(info["gh_auth"])

    @patch("scripts.flow_init.subprocess.run")
    def test_gh_auth_non_zero_exit(self, mock_run):
        class MockProc:
            returncode = 1
        mock_run.return_value = MockProc()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            info = inspect_git_environment(root, allow_git_init=False, skip_git=False)
            self.assertIsNone(info["gh_auth"])

class TestStackDetector(unittest.TestCase):

    def test_detect_python_no_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "main.py").write_text("print('hello')", encoding="utf-8")
            (temp_path / "tests").mkdir()
            (temp_path / "tests" / "test_main.py").write_text("print('hello')", encoding="utf-8")

            stack = detect_project_stack(temp_path)
            self.assertIn("Python", stack["languages"])
            self.assertEqual(stack["test_cmd"], "python3 -m unittest discover tests")

    def test_detect_python_no_config_without_tests_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "src").mkdir()
            (temp_path / "src" / "worker.py").write_text("x = 1\n", encoding="utf-8")
            stack = detect_project_stack(temp_path)
            self.assertIn("Python", stack["languages"])
            self.assertEqual(stack["test_cmd"], "python3 -m unittest")

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

    def test_detect_node_invalid_package_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "package.json").write_text('{ invalid json', encoding="utf-8")
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

    def test_detect_go_module(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "go.mod").write_text("module example.com/test\n\ngo 1.20\n", encoding="utf-8")
            stack = detect_project_stack(root)
            self.assertIn("Go", stack["languages"])
            self.assertEqual(stack["test_cmd"], "go test ./...")

    def test_detect_docker_taskfile_and_just(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "Dockerfile").write_text("FROM alpine\n", encoding="utf-8")
            (root / "Taskfile.yml").write_text("version: '3'\n", encoding="utf-8")
            (root / "Justfile").write_text("default:\n  @echo hi\n", encoding="utf-8")
            stack = detect_project_stack(root)
            self.assertIn("Docker", stack["build_tools"])
            self.assertIn("Taskfile", stack["build_tools"])
            self.assertIn("Just", stack["build_tools"])

    def test_detect_makefile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "Makefile").write_text("all:\n\t@echo hi\n", encoding="utf-8")
            stack = detect_project_stack(root)
            self.assertIn("Make", stack["build_tools"])

    def test_detect_python_setup_cfg(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "setup.cfg").write_text("[metadata]\nname = mypkg\n", encoding="utf-8")
            stack = detect_project_stack(root)
            self.assertIn("Python", stack["languages"])
            self.assertEqual(stack["test_cmd"], "pytest")

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

    def test_discover_file_subsystems_and_filter_non_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "main.py").write_text("print('entry')\n", encoding="utf-8")
            (root / "data_loader.py").write_text("x = 1\n", encoding="utf-8")
            (root / "test_root.py").write_text("pass\n", encoding="utf-8")
            (root / "setup.py").write_text("pass\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "__init__.py").write_text("", encoding="utf-8")
            (root / "src" / "README.md").write_text("# Doc\n", encoding="utf-8")
            (root / "src" / "config.json").write_text("{}\n", encoding="utf-8")
            (root / "src" / "auth_service.py").write_text("pass\n", encoding="utf-8")
            subsystems = discover_subsystems(root)
            self.assertIn(("main.py", "docs/context/main.md", "Main Subsystem"), subsystems)
            self.assertIn(("data_loader.py", "docs/context/data_loader.md", "Data Loader Subsystem"), subsystems)
            self.assertIn(("src/auth_service.py", "docs/context/src-auth_service.md", "Auth Service Subsystem"), subsystems)
            paths = [s[0] for s in subsystems]
            self.assertNotIn("src/README.md", paths)
            self.assertNotIn("src/config.json", paths)
            self.assertNotIn("setup.py", paths)
            self.assertNotIn("test_root.py", paths)


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
            scaffold_context_and_adr(root, subsystems, force=True)
            self.assertTrue((root / "docs" / "context" / "src-auth.md").exists())
            self.assertTrue((root / "docs" / "adr" / "README.md").exists())

class TestFlowInitCLI(unittest.TestCase):
    def test_run_flow_init_headless(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = run_flow_init(["--dir", tmpdir, "--yes", "--name", "cli-test", "--no-git"])
            self.assertEqual(exit_code, 0)
            self.assertTrue((Path(tmpdir) / "GEMINI.md").exists())
            self.assertTrue((Path(tmpdir) / "AGENTS.md").exists())

    def test_run_flow_init_preserves_existing_without_force(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gemini = Path(tmpdir) / "GEMINI.md"
            gemini.write_text("CUSTOM CONTENT", encoding="utf-8")
            exit_code = run_flow_init(["--dir", tmpdir, "--yes", "--name", "cli-test", "--no-git"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(gemini.read_text(encoding="utf-8"), "CUSTOM CONTENT")
            self.assertTrue((Path(tmpdir) / "AGENTS.md").exists())

    def test_run_flow_init_both_exist_preserves_both(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gemini = Path(tmpdir) / "GEMINI.md"
            gemini.write_text("CUSTOM GEMINI", encoding="utf-8")
            agents = Path(tmpdir) / "AGENTS.md"
            agents.write_text("CUSTOM AGENTS", encoding="utf-8")
            exit_code = run_flow_init(["--dir", tmpdir, "--yes", "--name", "cli-test", "--no-git"])
            self.assertEqual(exit_code, 0)
            self.assertEqual(gemini.read_text(encoding="utf-8"), "CUSTOM GEMINI")
            self.assertEqual(agents.read_text(encoding="utf-8"), "CUSTOM AGENTS")

    def test_run_flow_init_force_overwrites(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gemini = Path(tmpdir) / "GEMINI.md"
            gemini.write_text("OLD CONTENT", encoding="utf-8")
            exit_code = run_flow_init(["--dir", tmpdir, "--yes", "--name", "force-test", "--no-git", "--force"])
            self.assertEqual(exit_code, 0)
            self.assertNotEqual(gemini.read_text(encoding="utf-8"), "OLD CONTENT")
            self.assertIn("# force-test", gemini.read_text(encoding="utf-8"))

class TestInteractiveWizard(unittest.TestCase):
    @patch("sys.stdin.isatty", return_value=True)
    @patch("builtins.input", side_effect=["", "y", "y"])
    def test_interactive_git_prompt_defaults_to_yes(self, mock_input, mock_isatty):
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = run_flow_init(["--dir", tmpdir])
            self.assertEqual(exit_code, 0)
            self.assertTrue((Path(tmpdir) / ".git").exists())
            self.assertTrue((Path(tmpdir) / ".gitignore").exists())

    @patch("sys.stdin.isatty", return_value=False)
    def test_non_tty_skips_git_prompt_without_flags(self, mock_isatty):
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = run_flow_init(["--dir", tmpdir])
            self.assertEqual(exit_code, 0)
            self.assertFalse((Path(tmpdir) / ".git").exists())

    @patch("sys.stdin.isatty", return_value=True)
    @patch("builtins.input", side_effect=["n", "Kotlin, Java", "gradle test", "y"])
    def test_interactive_stack_rejection_prompts_custom_inputs(self, mock_input, mock_isatty):
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = run_flow_init(["--dir", tmpdir, "--no-git"])
            self.assertEqual(exit_code, 0)
            gemini_content = (Path(tmpdir) / "GEMINI.md").read_text(encoding="utf-8")
            self.assertIn("Kotlin, Java", gemini_content)
            self.assertIn("gradle test", gemini_content)

    @patch("sys.stdin.isatty", return_value=True)
    @patch("builtins.input", side_effect=["y", "n"])
    def test_interactive_subsystem_rejection_skips_context_docs(self, mock_input, mock_isatty):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "src").mkdir()
            (root / "src" / "mod_a").mkdir()
            exit_code = run_flow_init(["--dir", tmpdir, "--no-git"])
            self.assertEqual(exit_code, 0)
            self.assertFalse((root / "docs" / "context" / "src-mod_a.md").exists())
            gemini_content = (root / "GEMINI.md").read_text(encoding="utf-8")
            self.assertIn("No custom subsystem routing mapped", gemini_content)


class TestParseArgs(unittest.TestCase):
    def test_parse_args_defaults(self):
        args = parse_args([])
        self.assertEqual(args.dir, ".")
        self.assertFalse(args.yes)
        self.assertIsNone(args.name)
        self.assertFalse(args.git_init)
        self.assertFalse(args.no_git)
        self.assertFalse(args.force)

    def test_parse_args_all_flags(self):
        args = parse_args([
            "-d", "/tmp/test",
            "-y",
            "--name", "my-project",
            "--git-init",
            "--no-git",
            "-f"
        ])
        self.assertEqual(args.dir, "/tmp/test")
        self.assertTrue(args.yes)
        self.assertEqual(args.name, "my-project")
        self.assertTrue(args.git_init)
        self.assertTrue(args.no_git)
        self.assertTrue(args.force)

    def test_parse_args_long_flags(self):
        args = parse_args([
            "--dir", "/tmp/test2",
            "--yes",
            "--force"
        ])
        self.assertEqual(args.dir, "/tmp/test2")
        self.assertTrue(args.yes)
        self.assertTrue(args.force)

    def test_parse_args_invalid_argument(self):
        with self.assertRaises(SystemExit):
            parse_args(["--unknown-flag"])

if __name__ == "__main__":
    unittest.main()
