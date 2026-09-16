# tests/test_skills_unit.py
import unittest
import tempfile
import re
from pathlib import Path
from tests.test_skills_integrity import (
    validate_code_fences,
    validate_section_anchors,
    validate_tool_and_subagent_contracts,
    validate_tooling_discipline,
    validate_terminology,
    validate_skill_frontmatter,
    validate_skill_resources_and_references,
    validate_repo_inventory_and_permissions,
    validate_context_documents
)

class TestCodeFenceValidator(unittest.TestCase):
    def test_balanced_fences_pass(self):
        content = "# Title\n```python\nprint('hello')\n```\n"
        errors = validate_code_fences(content, Path("test.md"))
        self.assertEqual(errors, [])

    def test_unclosed_fence_fails(self):
        content = "# Title\n```python\nprint('hello')\n"
        errors = validate_code_fences(content, Path("test.md"))
        self.assertTrue(any("Unclosed code fence" in e for e in errors))

    def test_nested_fence_with_sufficient_outer_backticks_passes(self):
        # 4-backtick outer markdown fence with 3-backtick inner bash fence
        content = "````markdown\nSome text\n```bash\necho hi\n```\nMore text\n````"
        errors = validate_code_fences(content, Path("test.md"))
        self.assertEqual(errors, [])

    def test_nested_fence_without_extra_backticks_fails(self):
        # 3-backtick outer markdown fence with 3-backtick inner bash fence causes collision
        content = "```markdown\nSome text\n```bash\necho hi\n```\nMore text\n```"
        errors = validate_code_fences(content, Path("test.md"))
        self.assertTrue(any("colliding" in e or "Unclosed" in e for e in errors))

class TestSectionAnchorValidator(unittest.TestCase):
    def test_valid_unique_anchors_pass(self):
        content = "# Section 1 <!-- ANCHOR: SEC_ONE -->\n# Section 2 <!-- ANCHOR: SEC_TWO -->"
        errors = validate_section_anchors(content, Path("test.md"))
        self.assertEqual(errors, [])

    def test_invalid_anchor_naming_fails(self):
        content = "# Section <!-- ANCHOR: invalid-lowercase -->"
        errors = validate_section_anchors(content, Path("test.md"))
        self.assertTrue(any("does not conform to [A-Z0-9_]+" in e for e in errors))

    def test_duplicate_anchor_fails(self):
        content = "# Section A <!-- ANCHOR: SEC_A -->\n# Section B <!-- ANCHOR: SEC_A -->"
        errors = validate_section_anchors(content, Path("test.md"))
        self.assertTrue(any("Duplicate section anchor" in e for e in errors))

class TestToolAndSubagentValidator(unittest.TestCase):
    def test_valid_tool_and_subagent_pass(self):
        content = '{"TypeName": "self", "Role": "Code Reviewer"}\nUse `view_file` tool and `run_command` tool.'
        errors = validate_tool_and_subagent_contracts(content, Path("skills/test/SKILL.md"))
        self.assertEqual(errors, [])

    def test_invalid_subagent_typename_fails(self):
        content = '{"TypeName": "general-purpose", "Role": "Reviewer"}'
        errors = validate_tool_and_subagent_contracts(content, Path("skills/test/SKILL.md"))
        self.assertTrue(any("Invalid subagent TypeName" in e for e in errors))

    def test_deprecated_tool_fails(self):
        content = 'Call the `edit_file` tool to make changes.'
        errors = validate_tool_and_subagent_contracts(content, Path("skills/test/SKILL.md"))
        self.assertTrue(any("Deprecated" in e or "Invalid" in e for e in errors))

class TestToolingDisciplineValidator(unittest.TestCase):
    def test_clean_content_passes(self):
        content = "Track checklists via `- [ ]` in conversation.\nRun `pytest tests/`."
        errors = validate_tooling_discipline(content, Path("skills/test/SKILL.md"))
        self.assertEqual(errors, [])

    def test_negative_assertion_for_manage_task_passes(self):
        content = "Never use manage_task for todos (manage_task is for background OS processes only)."
        errors = validate_tooling_discipline(content, Path("rules/AGENTS.md"))
        self.assertEqual(errors, [])

    def test_cd_command_fails(self):
        content = 'CommandLine: "cd /tmp && run tests"'
        errors = validate_tooling_discipline(content, Path("skills/test/SKILL.md"))
        self.assertTrue(any("Prohibited 'cd' in command" in e for e in errors))

    def test_manage_task_for_todos_fails(self):
        content = "Use manage_task to manage your todo checklist."
        errors = validate_tooling_discipline(content, Path("skills/test/SKILL.md"))
        self.assertTrue(any("manage_task for todos" in e for e in errors))

class TestTerminologyValidator(unittest.TestCase):
    def test_correct_naming_passes(self):
        content = "Welcome to agy-flow and Antigravity Flow with /flow-spec and /flow-code-review."
        errors = validate_terminology(content, Path("skills/test/SKILL.md"))
        self.assertEqual(errors, [])

    def test_ag_flow_typo_fails(self):
        content = "The Ag-Flow engineering lifecycle is active."
        errors = validate_terminology(content, Path("skills/test/SKILL.md"))
        self.assertTrue(any("Prohibited term 'Ag-Flow'" in e for e in errors))

    def test_malformed_slash_command_fails(self):
        content = "Trigger with /flow_spec instead of /flow-spec."
        errors = validate_terminology(content, Path("skills/test/SKILL.md"))
        self.assertTrue(any("Malformed slash command" in e for e in errors))

class TestFrontmatterValidator(unittest.TestCase):
    def test_valid_frontmatter_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "flow-test"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: flow-test\ndescription: Test skill\nrisk: low\nsource: custom\n---\n# Content\n"
            )
            errors = validate_skill_frontmatter(skill_dir)
            self.assertEqual(errors, [])

    def test_mismatched_name_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "flow-test"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: flow-other\ndescription: Test skill\nrisk: low\nsource: custom\n---\n# Content\n"
            )
            errors = validate_skill_frontmatter(skill_dir)
            self.assertTrue(any("does not match directory" in e for e in errors))

class TestResourceAndReferenceValidator(unittest.TestCase):
    def test_existing_resource_link_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            skills_dir.mkdir()
            skill_dir = skills_dir / "flow-test"
            skill_dir.mkdir()
            (skill_dir / "resources").mkdir()
            (skill_dir / "resources" / "test.template").write_text("template")
            (skill_dir / "SKILL.md").write_text("See `resources/test.template` for scaffold.")
            errors = validate_skill_resources_and_references(skill_dir)
            self.assertEqual(errors, [])

    def test_cross_skill_resource_link_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            skills_dir.mkdir()
            skill_a = skills_dir / "flow-a"
            skill_a.mkdir()
            skill_b = skills_dir / "flow-b"
            skill_b.mkdir()
            (skill_b / "resources").mkdir()
            (skill_b / "resources" / "spec.md.template").write_text("template")
            (skill_a / "SKILL.md").write_text("See `flow-b/resources/spec.md.template` for scaffold.")
            errors = validate_skill_resources_and_references(skill_a)
            self.assertEqual(errors, [])

    def test_broken_resource_link_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "flow-test"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("See `resources/missing.template` for scaffold.")
            errors = validate_skill_resources_and_references(skill_dir)
            self.assertTrue(any("Referenced resource missing" in e for e in errors))

class TestInventoryAndPermissionsValidator(unittest.TestCase):
    def test_repo_inventory_matches_13_skills(self):
        repo_root = Path(__file__).resolve().parent.parent
        errors = validate_repo_inventory_and_permissions(repo_root)
        self.assertEqual(errors, [])

class TestContextDocumentValidator(unittest.TestCase):
    def test_valid_context_documents_pass(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs_ctx = root / "docs" / "context"
            docs_ctx.mkdir(parents=True)
            scripts_dir = root / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "tool.py").write_text("print('hello')")
            
            gemini_md = root / "GEMINI.md"
            gemini_md.write_text(
                "# Project\n## Context Routing Map\n| `scripts/**` | `docs/context/scripts.md` |\n"
            )
            
            (docs_ctx / "scripts.md").write_text(
                "# Scripts Context\n"
                "## 1. Purpose & Responsibility <!-- ANCHOR: PURPOSE -->\nAutomation.\n"
                "## 2. Public Interfaces & Contracts <!-- ANCHOR: CONTRACTS -->\n"
                "| Interface | Type | Responsibility |\n| `scripts/tool.py` | Script | Runs tool |\n"
                "## 3. Current Invariants & State <!-- ANCHOR: INVARIANTS -->\n"
                "- [x] Invariant 1\n"
            )
            errors = validate_context_documents(root)
            self.assertEqual(errors, [])

    def test_missing_anchors_fail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs_ctx = root / "docs" / "context"
            docs_ctx.mkdir(parents=True)
            (root / "GEMINI.md").write_text("# Project\n## Context Routing Map\n| `core/**` | `docs/context/core.md` |\n")
            (docs_ctx / "core.md").write_text("# Core Context\nNo anchors here.")
            errors = validate_context_documents(root)
            self.assertTrue(any("Missing required anchor" in e for e in errors))

    def test_unpopulated_placeholders_fail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs_ctx = root / "docs" / "context"
            docs_ctx.mkdir(parents=True)
            (root / "GEMINI.md").write_text("# Project\n## Context Routing Map\n| `core/**` | `docs/context/core.md` |\n")
            (docs_ctx / "core.md").write_text(
                "# Core Context\n"
                "## 1. Purpose & Responsibility <!-- ANCHOR: PURPOSE -->\nCore.\n"
                "## 2. Public Interfaces & Contracts <!-- ANCHOR: CONTRACTS -->\n"
                "| `[SymbolName]` | Class | [Description] |\n"
                "## 3. Current Invariants & State <!-- ANCHOR: INVARIANTS -->\n"
                "- [ ] Invariant 1: [Core domain rule]\n"
            )
            errors = validate_context_documents(root)
            self.assertTrue(any("Unpopulated placeholder" in e for e in errors))

    def test_missing_docs_context_dir_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            errors = validate_context_documents(root)
            self.assertEqual(errors, [])

    def test_docs_context_with_only_readme_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs_ctx = root / "docs" / "context"
            docs_ctx.mkdir(parents=True)
            (docs_ctx / "README.md").write_text("# Context Index\n")
            errors = validate_context_documents(root)
            self.assertEqual(errors, [])

    def test_directory_traversal_reference_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs_ctx = root / "docs" / "context"
            docs_ctx.mkdir(parents=True)
            (docs_ctx / "security.md").write_text(
                "# Security Context\n"
                "## 1. Purpose & Responsibility <!-- ANCHOR: PURPOSE -->\nSecurity.\n"
                "## 2. Public Interfaces & Contracts <!-- ANCHOR: CONTRACTS -->\n"
                "| `scripts/../../etc/passwd` | File | Leaked |\n"
                "## 3. Current Invariants & State <!-- ANCHOR: INVARIANTS -->\n"
                "- [x] Invariant 1\n"
            )
            errors = validate_context_documents(root)
            self.assertTrue(any("Directory traversal prohibited" in e for e in errors))

    def test_expanded_template_placeholders_fail(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            docs_ctx = root / "docs" / "context"
            docs_ctx.mkdir(parents=True)
            (docs_ctx / "core.md").write_text(
                "# Core Context\n"
                "## 1. Purpose & Responsibility <!-- ANCHOR: PURPOSE -->\n"
                "[Module / Subsystem Name] - [Short description]\n"
                "## 2. Public Interfaces & Contracts <!-- ANCHOR: CONTRACTS -->\n"
                "| `tests/test_unit.py` | Test | Suite |\n"
                "## 3. Current Invariants & State <!-- ANCHOR: INVARIANTS -->\n"
                "- [x] Invariant 1\n"
            )
            errors = validate_context_documents(root)
            self.assertTrue(any("Unpopulated placeholder" in e for e in errors))

class TestReviewDirectoryAndToolDiscipline(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent

    def test_flow_review_orchestrator_preflight_and_subagent_directives(self):
        skill_path = self.repo_root / "skills" / "flow-review" / "SKILL.md"
        prompt_path = self.repo_root / "skills" / "flow-review" / "references" / "auditor-prompt.md"

        self.assertTrue(skill_path.exists(), f"Missing {skill_path}")
        self.assertTrue(prompt_path.exists(), f"Missing {prompt_path}")

        skill_text = skill_path.read_text(encoding="utf-8")
        prompt_text = prompt_path.read_text(encoding="utf-8")

        # Orchestrator pre-flight in flow-review/SKILL.md
        self.assertIn("docs/plans/.tmp", skill_text)
        self.assertIn("list_dir", skill_text)
        self.assertIn("write_to_file", skill_text)

        # Subagent tool discipline in prompt and SKILL.md
        for text, source in [(skill_text, "SKILL.md"), (prompt_text, "auditor-prompt.md")]:
            self.assertIn("write_to_file", text, f"{source} must mandate write_to_file")
            self.assertTrue(
                bool(re.search(r'(?:do not|must not|never|prohibit|forbid).*mkdir', text, re.IGNORECASE)),
                f"{source} must explicitly forbid mkdir"
            )
            self.assertTrue(
                bool(re.search(r'(?:do not|must not|never|prohibit|forbid).*(?:touch|bash)', text, re.IGNORECASE)),
                f"{source} must explicitly forbid touch or bash"
            )

    def test_flow_code_review_orchestrator_preflight_and_subagent_directives(self):
        skill_path = self.repo_root / "skills" / "flow-code-review" / "SKILL.md"
        prompt_path = self.repo_root / "skills" / "flow-code-review" / "references" / "reviewer-prompt.md"

        self.assertTrue(skill_path.exists(), f"Missing {skill_path}")
        self.assertTrue(prompt_path.exists(), f"Missing {prompt_path}")

        skill_text = skill_path.read_text(encoding="utf-8")
        prompt_text = prompt_path.read_text(encoding="utf-8")

        # Orchestrator pre-flight in flow-code-review/SKILL.md
        self.assertIn("docs/plans/.tmp", skill_text)
        self.assertIn("list_dir", skill_text)
        self.assertIn("write_to_file", skill_text)

        # Subagent tool discipline in prompt and SKILL.md
        for text, source in [(skill_text, "SKILL.md"), (prompt_text, "reviewer-prompt.md")]:
            self.assertIn("write_to_file", text, f"{source} must mandate write_to_file")
            self.assertTrue(
                bool(re.search(r'(?:do not|must not|never|prohibit|forbid).*mkdir', text, re.IGNORECASE)),
                f"{source} must explicitly forbid mkdir"
            )
            self.assertTrue(
                bool(re.search(r'(?:do not|must not|never|prohibit|forbid).*(?:touch|bash)', text, re.IGNORECASE)),
                f"{source} must explicitly forbid touch or bash"
            )

    def test_gitignore_contains_tmp_exclusion(self):
        gitignore_path = self.repo_root / ".gitignore"
        self.assertTrue(gitignore_path.exists(), "Missing .gitignore")
        gitignore_text = gitignore_path.read_text(encoding="utf-8")
        self.assertIn("docs/**/.tmp/", gitignore_text, ".gitignore must retain exclusion of docs/**/.tmp/")

if __name__ == "__main__":
    unittest.main()

