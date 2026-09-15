# tests/test_skills_unit.py
import unittest
from pathlib import Path
from tests.test_skills_integrity import validate_code_fences

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
        # 3-backtick outer markdown fence with 3-backtick inner bash fence causes premature close
        content = "```markdown\nSome text\n```bash\necho hi\n```\nMore text\n```"
        errors = validate_code_fences(content, Path("test.md"))
        self.assertTrue(any("Prematurely closed or colliding" in e or "Unclosed" in e for e in errors))

if __name__ == "__main__":
    unittest.main()
