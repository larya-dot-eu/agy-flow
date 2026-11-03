import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

from scripts.flow_prcheck import (
    ChangeRiskProfile,
    FileStats,
    PRAnalysis,
    PREligibility,
    ProbeResult,
    ReviewCompleteness,
    RiskSignal,
    TestSignals,
    WorkloadProfile,
    acquire_local_diff,
    analyze_pr,
    analyze_test_signals,
    compute_change_risk,
    compute_completeness,
    compute_workload,
    discover_context_and_specialists,
    extract_companion_refs,
    extract_invariants,
    generate_suggestions,
    is_line_commentable,
    parse_args,
    parse_diff,
    probe_github_pr,
    redact_secrets,
    run_flow_prcheck,
    run_sandboxed_probe,
    validate_target,
    verify_snapshot,
)


SAMPLE_DIFF = """diff --git a/scripts/flow_init.py b/scripts/flow_init.py
index 1111111..2222222 100644
--- a/scripts/flow_init.py
+++ b/scripts/flow_init.py
@@ -10,4 +10,6 @@ def detect_stack(root: Path) -> dict:
     existing_line = 1
-    removed_line = 2
+    added_line_1 = 3
+    added_line_2 = 4
+    added_line_3 = 5
     trailing_context = 6
diff --git a/tests/test_flow_init_unit.py b/tests/test_flow_init_unit.py
index 3333333..4444444 100644
--- a/tests/test_flow_init_unit.py
+++ b/tests/test_flow_init_unit.py
@@ -1,3 +1,5 @@ def test_stack():
     x = 1
+    assert x == 1
+    self.assertEqual(x, 1)
"""


class TestFlowPrcheckCore(unittest.TestCase):
    def test_ac01_validate_target_and_cli_flags(self):
        args_num = parse_args(["42"])
        self.assertEqual(validate_target(args_num), ("pr", "pr-42", 42))
        args_hash = parse_args(["#42"])
        self.assertEqual(validate_target(args_hash), ("pr", "pr-42", 42))
        args_url = parse_args(["https://github.com/larya-dot-eu/agy-flow/pull/99"])
        self.assertEqual(validate_target(args_url), ("pr", "pr-99", 99))
        args_local = parse_args([])
        self.assertEqual(validate_target(args_local), ("local", "local", None))
        self.assertEqual(run_flow_prcheck(["scripts/flow_init.py"]), 2)
        self.assertEqual(run_flow_prcheck(["src/app.ts"]), 2)
        self.assertEqual(run_flow_prcheck(["--threshold", "105"]), 2)
        self.assertEqual(run_flow_prcheck(["--threshold", "-5"]), 2)
        self.assertEqual(run_flow_prcheck(["--staged", "--committed"]), 2)
        self.assertEqual(run_flow_prcheck(["--draft-review"]), 2)
        self.assertEqual(run_flow_prcheck(["--comment"]), 2)
        self.assertEqual(run_flow_prcheck(["42", "--fix"]), 2)

    def test_ac02_parse_diff_hunk_intervals_and_scope_coverage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            files, filtered_diff, ledger = parse_diff(SAMPLE_DIFF, scope="scripts/", workspace_root=root)
            self.assertEqual(len(files), 1)
            fstat = files[0]
            self.assertEqual(fstat.filename, "scripts/flow_init.py")
            self.assertEqual(fstat.additions, 3)
            self.assertEqual(fstat.deletions, 1)
            self.assertEqual(fstat.hunks_count, 1)
            self.assertEqual(fstat.language, "Python")
            self.assertFalse(fstat.is_test)
            self.assertEqual(fstat.commentable_ranges, [[10, 14]])
            self.assertTrue(is_line_commentable(fstat, 10))
            self.assertTrue(is_line_commentable(fstat, 12))
            self.assertTrue(is_line_commentable(fstat, 14))
            self.assertFalse(is_line_commentable(fstat, 9))
            self.assertFalse(is_line_commentable(fstat, 15))
            self.assertNotIn("tests/test_flow_init_unit.py", filtered_diff)
            self.assertEqual(
                ledger,
                {
                    "scripts/flow_init.py": "reviewed",
                    "tests/test_flow_init_unit.py": "excluded_by_scope",
                },
            )
            # Path traversal outside workspace_root is blocked from reading external files
            traversal_diff = (
                "diff --git a/../outside.py b/../outside.py\n"
                "--- a/../outside.py\n"
                "+++ b/../outside.py\n"
                "@@ -1,1 +1,1 @@\n"
                "+x = 1\n"
            )
            t_files, _, _ = parse_diff(traversal_diff, workspace_root=root)
            self.assertIsNone(t_files[0].content_sha256)

    def test_ac06_secret_redaction_json_output_and_sla(self):
        secret_diff = (
            "diff --git a/config.py b/config.py\n"
            "--- a/config.py\n"
            "+++ b/config.py\n"
            "@@ -1,1 +1,2 @@\n"
            " DEBUG = False\n"
            "+TOKEN = 'ghp_1234567890abcdefghijklmnopqrstuv'\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            diff_file = root / "input.diff"
            diff_file.write_text(secret_diff, encoding="utf-8")
            out_dir = root / "out"
            start = time.monotonic()
            rc = run_flow_prcheck(
                ["--dir", str(root), "--diff-file", str(diff_file), "--output-dir", str(out_dir), "--json"]
            )
            elapsed_ms = (time.monotonic() - start) * 1000.0
            self.assertEqual(rc, 0)
            self.assertLessEqual(elapsed_ms, 200.0)
            ctx_json = (out_dir / "prcheck-context.json").read_text(encoding="utf-8")
            sliced_diff = (out_dir / "prcheck-sliced.diff").read_text(encoding="utf-8")
            self.assertNotIn("ghp_1234567890abcdefghijklmnopqrstuv", ctx_json)
            self.assertNotIn("ghp_1234567890abcdefghijklmnopqrstuv", sliced_diff)
            self.assertIn("[REDACTED_SECRET]", sliced_diff)
            payload = json.loads(ctx_json)
            self.assertEqual(payload["change_risk"]["level"], "CRITICAL")


if __name__ == "__main__":
    unittest.main()
