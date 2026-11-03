#!/usr/bin/env python3
"""Deterministic Pre-Flight Triage, Context Router & Sandboxed Probe Engine for /flow-prcheck."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
import tempfile
import time
from typing import Any

SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"Bearer\s+[A-Za-z0-9_\-\.=]{20,}"),
]

LANGUAGE_MAP = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript/React",
    ".js": "JavaScript",
    ".jsx": "JavaScript/React",
    ".rs": "Rust",
    ".go": "Go",
    ".sql": "SQL",
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".h": "C/C++",
    ".hpp": "C++",
    ".sh": "Shell",
    ".bash": "Shell",
    ".md": "Markdown",
    ".json": "JSON",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
}

CONFIG_FILENAMES = {
    "pyproject.toml",
    "package.json",
    "tsconfig.json",
    "Cargo.toml",
    "go.mod",
    "plugin.json",
    "hooks.json",
    ".mcp.json",
    "Makefile",
    "Dockerfile",
}

INSTRUCTION_PATTERNS = (
    "GEMINI.md",
    "AGENTS.md",
    "CLAUDE.md",
    "SKILL.md",
    "hooks.json",
    "plugin.json",
    ".mcp.json",
)

LANGUAGE_SUGGESTIONS = {
    "Python": "Check for mutable default arguments, subprocess timeout/shell safety, and broad exception handlers",
    "TypeScript": "Check for strict typing (avoid 'any'), unhandled promises, and null safety",
    "TypeScript/React": "Check for strict typing (avoid 'any'), unhandled promises, and null safety",
    "Rust": "Check for unwrap()/expect() panics, unsafe blocks, and async cancellation safety",
    "Go": "Check for unchecked error returns, goroutine leaks, and context propagation",
    "SQL": "Check for SQL injection, N+1 query patterns, and missing index coverage",
    "C": "Check for memory safety, bounds checks, and undefined behavior",
    "C++": "Check for memory safety, bounds checks, and undefined behavior",
    "C/C++": "Check for memory safety, bounds checks, and undefined behavior",
    "Shell": "Check for unquoted variable expansions, command injection, and set -e error handling",
}


@dataclass
class FileStats:
    filename: str
    status: str = "modified"
    additions: int = 0
    deletions: int = 0
    hunks_count: int = 0
    symbols_changed: int = 0
    is_test: bool = False
    is_config: bool = False
    language: str = "unknown"
    commentable_ranges: list[list[int]] = field(default_factory=list)
    added_lines: list[str] = field(default_factory=list)
    removed_lines: list[str] = field(default_factory=list)
    content_sha256: str | None = None


@dataclass
class TestSignals:
    tests_added: list[str] = field(default_factory=list)
    tests_modified: list[str] = field(default_factory=list)
    tests_removed: list[str] = field(default_factory=list)
    assertions_added: int = 0
    assertions_removed: int = 0
    assertions_weakened: bool = False
    changed_code_with_existing_tests: list[str] = field(default_factory=list)
    changed_code_without_test_evidence: list[str] = field(default_factory=list)


@dataclass
class RiskSignal:
    category: str
    severity: str
    filename: str
    reason: str


@dataclass
class WorkloadProfile:
    total_files: int
    total_hunks: int
    total_additions: int
    total_deletions: int
    changed_symbols_estimate: int
    size_category: str
    estimated_review_minutes: int
    suggested_scopes: list[str] = field(default_factory=list)
    semantic_groups: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class ChangeRiskProfile:
    level: str
    signals: list[RiskSignal] = field(default_factory=list)
    test_signals: TestSignals = field(default_factory=TestSignals)


@dataclass
class ReviewCompleteness:
    review_status: str = "COMPLETE"
    local_state_mode: str = "working-tree"
    completed_checks: list[str] = field(default_factory=list)
    dispatched_specialists: list[str] = field(default_factory=list)
    skipped_checks: list[str] = field(default_factory=list)
    missing_dependencies: list[str] = field(default_factory=list)
    mixed_staged_unstaged_files: list[str] = field(default_factory=list)
    coverage_ledger: dict[str, str] = field(default_factory=dict)


@dataclass
class ProbeResult:
    command: list[str]
    exit_code: int
    timed_out: bool
    duration_ms: float
    sanitized_output: str


@dataclass
class PREligibility:
    mode: str
    target_id: str
    pr_number: int | None = None
    title: str = ""
    state: str = "OPEN"
    is_draft: bool = False
    already_reviewed_by_viewer: bool = False
    eligible: bool = True
    ineligible_reason: str | None = None
    companion_refs: list[str] = field(default_factory=list)
    failed_checks: list[str] = field(default_factory=list)
    base_ref: str | None = None
    merge_base: str | None = None
    head_ref: str | None = None


@dataclass
class PRAnalysis:
    mode: str
    target_id: str
    scope: str | None
    threshold: int
    eligibility: PREligibility
    workload: WorkloadProfile
    change_risk: ChangeRiskProfile
    completeness: ReviewCompleteness
    files: list[FileStats]
    suggestions: list[str]
    context_docs: list[str]
    spec_docs: list[str]
    adr_docs: list[str]
    standard_docs: list[str]
    untrusted_instruction_changes: list[str]
    discovered_invariants: list[str]
    recommended_specialists: list[str]
    flags: dict[str, bool]


def redact_secrets(text: str) -> str:
    sanitized = text
    for pattern in SECRET_PATTERNS:
        sanitized = pattern.sub("[REDACTED_SECRET]", sanitized)
    return sanitized


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="flow-prcheck",
        description="Deterministic pre-flight triage & sandboxed probe engine for /flow-prcheck.",
    )
    parser.add_argument("target", nargs="?", default=None, help="PR number (42, #42), PR URL, or omit for Local Mode")
    parser.add_argument("--dir", "-d", default=".", help="Target workspace root directory")
    parser.add_argument("--base", default=None, help="Explicit base ref for Local Mode merge-base resolution")
    parser.add_argument("--staged", action="store_true", help="Inspect only staged index changes (git diff --cached)")
    parser.add_argument("--committed", action="store_true", help="Inspect only committed branch changes")
    parser.add_argument("--scope", default=None, help="Path prefix subtree filter (e.g. scripts/)")
    parser.add_argument("--threshold", type=int, default=75, help="Confidence threshold (0-100, default 75)")
    parser.add_argument("--diff-file", "-f", default=None, help="Explicit unified diff file path")
    parser.add_argument("--stats", "-s", action="store_true", help="Render per-file stats breakdown")
    parser.add_argument("--json", action="store_true", help="Emit PRAnalysis JSON payload to stdout")
    parser.add_argument("--output-dir", default=None, help="Directory to write prcheck-context.json & prcheck-sliced.diff")
    parser.add_argument("--fix", action="store_true", help="Enable guarded repair mode in Local Mode")
    parser.add_argument("--draft-review", "--pending", dest="draft_review", action="store_true", help="Create pending GitHub review in PR Mode")
    parser.add_argument("--comment", action="store_true", help="Submit COMMENT GitHub review in PR Mode")
    parser.add_argument("--allow-probes", action="store_true", help="Authorize sandboxed probes in PR Mode")
    parser.add_argument("--run-probe", default=None, help="Execute a probe script inside the credential-stripped sandbox")
    parser.add_argument("--verify-snapshot", default=None, help="Verify working-tree SHA-256 hashes against prcheck-context.json")
    parser.add_argument("--cleanup-target", default=None, help="Remove intermediate .tmp files for target_id while preserving prcheck-[target_id].md")
    return parser.parse_args(argv)


def validate_target(args: argparse.Namespace) -> tuple[str, str, int | None]:
    if args.threshold < 0 or args.threshold > 100:
        raise ValueError("Invalid --threshold: must be between 0 and 100.")
    if args.staged and args.committed:
        raise ValueError("Flags --staged and --committed are mutually exclusive.")
    if args.diff_file:
        return ("file", "file", None)
    target = args.target
    if target is None or target.strip() == "":
        if args.draft_review or args.comment:
            raise ValueError("--draft-review and --comment are only valid in PR Mode.")
        return ("local", "local", None)
    raw = target.strip()
    pr_url_match = re.match(r"^https?://github\.com/[^/]+/[^/]+/pull/(\d+)(?:/.*)?$", raw)
    if pr_url_match:
        pr_num = int(pr_url_match.group(1))
        if args.fix:
            raise ValueError("--fix is only valid in Local Mode; refusing to mutate checkout in PR Mode.")
        return ("pr", f"pr-{pr_num}", pr_num)
    pr_num_match = re.match(r"^#?(\d+)$", raw)
    if pr_num_match:
        pr_num = int(pr_num_match.group(1))
        if args.fix:
            raise ValueError("--fix is only valid in Local Mode; refusing to mutate checkout in PR Mode.")
        return ("pr", f"pr-{pr_num}", pr_num)
    raise ValueError(
        f"Invalid positional target '{raw}'. Pass a PR number/URL or use '--scope {raw}' to filter local paths."
    )


def _classify_file(filename: str) -> tuple[str, bool, bool]:
    p = Path(filename)
    ext = p.suffix.lower()
    lang = LANGUAGE_MAP.get(ext, "unknown")
    lower_name = filename.lower()
    is_test = (
        lower_name.startswith("tests/")
        or "/tests/" in lower_name
        or p.name.startswith("test_")
        or p.name.endswith("_test.py")
        or p.name.endswith(".test.ts")
        or p.name.endswith(".spec.ts")
        or p.name.endswith("_test.go")
    )
    is_config = (
        p.name in CONFIG_FILENAMES
        or p.name.startswith(".env")
        or lower_name.startswith(".github/workflows/")
        or ext in {".json", ".yml", ".yaml", ".toml"}
    )
    return lang, is_test, is_config


def _merge_lines_to_ranges(lines: list[int]) -> list[list[int]]:
    if not lines:
        return []
    sorted_lines = sorted(set(lines))
    ranges: list[list[int]] = [[sorted_lines[0], sorted_lines[0]]]
    for ln in sorted_lines[1:]:
        if ln == ranges[-1][1] + 1:
            ranges[-1][1] = ln
        else:
            ranges.append([ln, ln])
    return ranges


def is_line_commentable(file_stats: FileStats, line: int) -> bool:
    return any(start <= line <= end for start, end in file_stats.commentable_ranges)


def _resolve_within_workspace(workspace_root: Path, rel_path: str) -> Path | None:
    try:
        root_resolved = workspace_root.resolve()
        candidate = (root_resolved / rel_path).resolve()
        if candidate.is_relative_to(root_resolved):
            return candidate
    except (OSError, ValueError):
        return None
    return None


def parse_diff(
    diff_content: str, scope: str | None = None, workspace_root: Path | None = None
) -> tuple[list[FileStats], str, dict[str, str]]:
    norm_scope = scope.lstrip("./") if scope else None
    raw_blocks = re.split(r"(?=^diff --git )", diff_content, flags=re.MULTILINE)
    files: list[FileStats] = []
    kept_blocks: list[str] = []
    coverage_ledger: dict[str, str] = {}

    for block in raw_blocks:
        if not block.strip() or not block.startswith("diff --git "):
            continue
        lines = block.splitlines()
        header_match = re.match(r"^diff --git a/(.+?) b/(.+)$", lines[0])
        if not header_match:
            continue
        b_path = header_match.group(2).strip()
        header_lines: list[str] = []
        for l in lines[1:]:
            if l.startswith("@@ "):
                break
            header_lines.append(l)
        if any(l.startswith("Binary files ") or l == "GIT binary patch" for l in header_lines):
            coverage_ledger[b_path] = "blocked"
            continue
        if norm_scope and not b_path.startswith(norm_scope):
            coverage_ledger[b_path] = "excluded_by_scope"
            continue

        coverage_ledger[b_path] = "reviewed"
        kept_blocks.append(block if block.endswith("\n") else block + "\n")

        status = "modified"
        if any(l.startswith("new file mode") for l in lines[:6]):
            status = "added"
        elif any(l.startswith("deleted file mode") or l.startswith("+++ /dev/null") for l in lines[:6]):
            status = "deleted"
        elif any(l.startswith("rename from ") for l in lines[:6]):
            status = "renamed"

        lang, is_test, is_config = _classify_file(b_path)
        additions = 0
        deletions = 0
        hunks_count = 0
        symbols = set()
        commentable_lines: list[int] = []
        added_lines: list[str] = []
        removed_lines: list[str] = []
        right_line: int | None = None

        for line in lines[1:]:
            hunk_m = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@(.*)$", line)
            if hunk_m:
                hunks_count += 1
                right_line = int(hunk_m.group(1))
                ctx_sym = hunk_m.group(3).strip()
                if ctx_sym:
                    symbols.add(ctx_sym)
                continue
            if right_line is None:
                continue
            if line.startswith("+") and not line.startswith("+++"):
                additions += 1
                added_text = line[1:]
                added_lines.append(added_text)
                commentable_lines.append(right_line)
                sym_m = re.search(r"\b(?:def|class|function|fn|func)\s+([A-Za-z_][A-Za-z0-9_]*)", added_text)
                if sym_m:
                    symbols.add(sym_m.group(1))
                right_line += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1
                removed_lines.append(line[1:])
            elif line.startswith(" "):
                commentable_lines.append(right_line)
                right_line += 1

        sha256_hex: str | None = None
        if workspace_root is not None and status != "deleted":
            disk_path = _resolve_within_workspace(workspace_root, b_path)
            if disk_path is not None and disk_path.is_file():
                sha256_hex = hashlib.sha256(disk_path.read_bytes()).hexdigest()

        files.append(
            FileStats(
                filename=b_path,
                status=status,
                additions=additions,
                deletions=deletions,
                hunks_count=hunks_count,
                symbols_changed=max(len(symbols), 1 if hunks_count > 0 else 0),
                is_test=is_test,
                is_config=is_config,
                language=lang,
                commentable_ranges=_merge_lines_to_ranges(commentable_lines),
                added_lines=added_lines,
                removed_lines=removed_lines,
                content_sha256=sha256_hex,
            )
        )

    return files, "".join(kept_blocks), coverage_ledger


def extract_companion_refs(text: str) -> list[str]:
    if not text:
        return []
    refs: set[str] = set()
    for m in re.finditer(r"#(\d+)", text):
        refs.add(f"#{m.group(1)}")
    for m in re.finditer(r"(?:depends on|stacked on|docs for|part of)\s+(#[0-9]+|[a-zA-Z0-9_.\-/]+)", text, re.IGNORECASE):
        refs.add(m.group(1))
    return sorted(refs)


def probe_github_pr(workspace_root: Path, pr_ref: str, pr_number: int | None = None) -> tuple[PREligibility, str]:
    target_id = f"pr-{pr_number}" if pr_number is not None else f"pr-{pr_ref}"
    elig = PREligibility(mode="pr", target_id=target_id, pr_number=pr_number)
    view_cmd = [
        "gh",
        "pr",
        "view",
        str(pr_ref),
        "--json",
        "number,title,body,state,isDraft,baseRefName,headRefName,reviews,statusCheckRollup",
    ]
    try:
        res = subprocess.run(view_cmd, cwd=workspace_root, capture_output=True, text=True, timeout=5)
    except (subprocess.SubprocessError, OSError) as exc:
        elig.eligible = False
        elig.ineligible_reason = f"gh pr view failed: {exc}"
        return elig, ""
    if res.returncode != 0:
        elig.eligible = False
        elig.ineligible_reason = f"gh pr view failed: {res.stderr.strip() or 'unknown error'}"
        return elig, ""

    try:
        data = json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        elig.eligible = False
        elig.ineligible_reason = f"gh pr view returned invalid JSON: {exc}"
        return elig, ""
    elig.pr_number = data.get("number", pr_number)
    elig.target_id = f"pr-{elig.pr_number}"
    elig.title = data.get("title") or ""
    elig.state = (data.get("state") or "OPEN").upper()
    elig.is_draft = bool(data.get("isDraft", False))
    elig.already_reviewed_by_viewer = bool(data.get("reviews"))
    elig.base_ref = data.get("baseRefName")
    elig.head_ref = data.get("headRefName")
    elig.companion_refs = extract_companion_refs(f"{elig.title}\n{data.get('body') or ''}")

    for check in data.get("statusCheckRollup") or []:
        conclusion = (check.get("conclusion") or check.get("state") or "").upper()
        if conclusion in {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED"}:
            name = check.get("name") or check.get("context") or "unknown-check"
            elig.failed_checks.append(name)

    if elig.is_draft:
        elig.eligible = False
        elig.ineligible_reason = "PR is a draft"
        return elig, ""
    if elig.state != "OPEN":
        elig.eligible = False
        elig.ineligible_reason = f"PR state is {elig.state}"
        return elig, ""

    try:
        diff_res = subprocess.run(
            ["gh", "pr", "diff", str(pr_ref)],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        elig.eligible = False
        elig.ineligible_reason = f"gh pr diff failed: {exc}"
        return elig, ""
    if diff_res.returncode != 0 or not diff_res.stdout.strip():
        elig.eligible = False
        elig.ineligible_reason = "Empty or unavailable PR diff"
        return elig, ""
    return elig, diff_res.stdout


def _resolve_base_ref(workspace_root: Path, explicit_base: str | None) -> str:
    if explicit_base:
        return explicit_base
    sym = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "symbolic-ref", "refs/remotes/origin/HEAD"],
        cwd=workspace_root,
        capture_output=True,
        text=True,
        timeout=5,
    )
    if sym.returncode == 0 and sym.stdout.strip():
        return sym.stdout.strip().replace("refs/remotes/", "")
    for candidate in ("origin/main", "main", "origin/master", "master", "@{upstream}", "HEAD"):
        chk = subprocess.run(
            ["git", "-c", "core.fsmonitor=false", "rev-parse", "--verify", candidate],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if chk.returncode == 0:
            return candidate
    return "HEAD"


def acquire_local_diff(
    workspace_root: Path, base_ref: str | None = None, local_state_mode: str = "working-tree"
) -> tuple[PREligibility, str, list[str]]:
    elig = PREligibility(mode="local", target_id="local", head_ref="HEAD")
    resolved_base = _resolve_base_ref(workspace_root, base_ref)
    elig.base_ref = resolved_base

    mb_res = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "merge-base", "HEAD", resolved_base],
        cwd=workspace_root,
        capture_output=True,
        text=True,
        timeout=5,
    )
    merge_base = mb_res.stdout.strip() if mb_res.returncode == 0 and mb_res.stdout.strip() else "HEAD"
    elig.merge_base = merge_base

    git_base_flags = ["git", "-c", "core.fsmonitor=false", "diff", "--no-ext-diff", "--no-textconv"]
    if local_state_mode == "staged":
        diff_res = subprocess.run(
            [*git_base_flags, "--cached"], cwd=workspace_root, capture_output=True, text=True, timeout=5
        )
        net_diff = diff_res.stdout
    elif local_state_mode == "committed":
        diff_res = subprocess.run(
            [*git_base_flags, f"{merge_base}..HEAD"], cwd=workspace_root, capture_output=True, text=True, timeout=5
        )
        net_diff = diff_res.stdout
    else:
        diff_res = subprocess.run(
            [*git_base_flags, merge_base], cwd=workspace_root, capture_output=True, text=True, timeout=5
        )
        net_diff = diff_res.stdout
        untracked_res = subprocess.run(
            ["git", "-c", "core.fsmonitor=false", "ls-files", "--others", "--exclude-standard"],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if untracked_res.returncode == 0:
            synthetic_blocks: list[str] = []
            for rel in sorted(untracked_res.stdout.splitlines()):
                rel = rel.strip()
                if not rel:
                    continue
                raw_path = workspace_root / rel
                if raw_path.is_symlink():
                    continue
                fpath = _resolve_within_workspace(workspace_root, rel)
                if fpath is None or not fpath.is_file():
                    continue
                try:
                    raw_bytes = fpath.read_bytes()
                    if b"\x00" in raw_bytes:
                        continue
                    text_lines = raw_bytes.decode("utf-8").splitlines()
                except UnicodeDecodeError:
                    continue
                count = len(text_lines)
                body = "\n".join(f"+{ln}" for ln in text_lines)
                if body:
                    body += "\n"
                synthetic_blocks.append(
                    f"diff --git a/{rel} b/{rel}\n"
                    f"new file mode 100644\n"
                    f"--- /dev/null\n"
                    f"+++ b/{rel}\n"
                    f"@@ -0,0 +1,{count} @@\n"
                    f"{body}"
                )
            if synthetic_blocks:
                if net_diff and not net_diff.endswith("\n"):
                    net_diff += "\n"
                net_diff += "".join(synthetic_blocks)

    staged_names_res = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "diff", "--no-ext-diff", "--no-textconv", "--cached", "--name-only"],
        cwd=workspace_root,
        capture_output=True,
        text=True,
        timeout=5,
    )
    unstaged_names_res = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "diff", "--no-ext-diff", "--no-textconv", "--name-only"],
        cwd=workspace_root,
        capture_output=True,
        text=True,
        timeout=5,
    )
    staged_set = {s.strip() for s in staged_names_res.stdout.splitlines() if s.strip()}
    unstaged_set = {s.strip() for s in unstaged_names_res.stdout.splitlines() if s.strip()}
    mixed_files = sorted(staged_set & unstaged_set)

    if not net_diff.strip():
        elig.eligible = False
        elig.ineligible_reason = "No changes to review"
    return elig, net_diff, mixed_files


def _stem_for_grouping(filename: str) -> str:
    stem = Path(filename).stem.lower()
    for prefix in ("test_",):
        if stem.startswith(prefix):
            stem = stem[len(prefix) :]
    for suffix in ("_unit", "_test", ".test", ".spec"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    return stem.replace("-", "_")


def compute_workload(files: list[FileStats]) -> WorkloadProfile:
    total_files = len(files)
    total_hunks = sum(f.hunks_count for f in files)
    total_add = sum(f.additions for f in files)
    total_del = sum(f.deletions for f in files)
    total_changes = total_add + total_del
    changed_symbols = sum(f.symbols_changed for f in files)

    if total_changes < 50:
        size_cat = "XS (Extra Small)"
    elif total_changes < 200:
        size_cat = "S (Small)"
    elif total_changes < 400:
        size_cat = "M (Medium)"
    elif total_changes < 800:
        size_cat = "L (Large)"
    else:
        size_cat = "XL (Extra Large) - Split Recommended"

    est_minutes = max(1, ((total_changes + 19) // 20) + total_files)
    suggested_scopes: list[str] = []
    if total_changes >= 400 or total_files > 10:
        top_dirs = sorted({f"{Path(f.filename).parts[0]}/" for f in files if len(Path(f.filename).parts) > 1})
        suggested_scopes = top_dirs

    groups: dict[str, list[str]] = {}
    for f in files:
        key = _stem_for_grouping(f.filename)
        groups.setdefault(key, []).append(f.filename)

    return WorkloadProfile(
        total_files=total_files,
        total_hunks=total_hunks,
        total_additions=total_add,
        total_deletions=total_del,
        changed_symbols_estimate=changed_symbols,
        size_category=size_cat,
        estimated_review_minutes=est_minutes,
        suggested_scopes=suggested_scopes,
        semantic_groups=groups,
    )


def analyze_test_signals(workspace_root: Path, files: list[FileStats]) -> TestSignals:
    signals = TestSignals()
    assertion_re = re.compile(r"(?:\bassert\b|self\.assert|\bexpect\s*\(|\bshould\b|\brequire\.)")
    diff_test_stems = {_stem_for_grouping(f.filename) for f in files if f.is_test and f.status != "deleted"}

    for f in files:
        if f.is_test:
            if f.status == "deleted" or (f.additions == 0 and f.deletions > 0):
                signals.tests_removed.append(f.filename)
            elif f.status == "added" or (f.additions > 0 and f.deletions == 0):
                signals.tests_added.append(f.filename)
            elif f.additions > 0 and f.deletions > 0:
                signals.tests_modified.append(f.filename)

            for ln in f.added_lines:
                if assertion_re.search(ln):
                    signals.assertions_added += 1
            for ln in f.removed_lines:
                if assertion_re.search(ln):
                    signals.assertions_removed += 1

    has_code_changes = any(not f.is_test and not f.is_config and f.language != "Markdown" for f in files)
    if signals.assertions_removed > signals.assertions_added or (signals.tests_removed and has_code_changes):
        signals.assertions_weakened = True

    for f in files:
        if f.is_test or f.is_config or f.language in {"Markdown", "unknown"}:
            continue
        stem = _stem_for_grouping(f.filename)
        candidates = [
            workspace_root / "tests" / f"test_{stem}.py",
            workspace_root / "tests" / f"test_{stem}_unit.py",
            workspace_root / "tests" / f"test_{stem}.sh",
            workspace_root / f"test_{stem}.py",
        ]
        if stem in diff_test_stems or any(c.exists() for c in candidates):
            signals.changed_code_with_existing_tests.append(f.filename)
        else:
            signals.changed_code_without_test_evidence.append(f.filename)

    return signals


def compute_change_risk(workspace_root: Path, files: list[FileStats]) -> ChangeRiskProfile:
    test_signals = analyze_test_signals(workspace_root, files)
    signals: list[RiskSignal] = []

    auth_re = re.compile(r"\b(?:auth|permission|permission_allow_admin|role|token|secret|jwt|oauth|sudo|chmod)\b", re.IGNORECASE)
    exec_re = re.compile(r"(?:\bsubprocess\b|shell\s*=\s*True|\bos\.system\b|\beval\s*\(|\bexec\s*\()")
    data_re = re.compile(r"\b(?:migration|ALTER\s+TABLE|DROP\s+TABLE|DELETE\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET)\b", re.IGNORECASE)

    for f in files:
        joined_lines = "\n".join(f.added_lines + f.removed_lines)
        added_joined = "\n".join(f.added_lines)

        if any(pat.search(added_joined) for pat in SECRET_PATTERNS):
            signals.append(
                RiskSignal(
                    category="SECRET_EXPOSURE",
                    severity="CRITICAL",
                    filename=f.filename,
                    reason="Potential secret or private key pattern detected in added diff lines",
                )
            )

        if any(
            f.filename == pat
            or f.filename.endswith(f"/{pat}")
            or f.filename.startswith(("rules/", ".gemini/", ".agents/"))
            for pat in INSTRUCTION_PATTERNS
        ):
            signals.append(
                RiskSignal(
                    category="AGENT_INSTRUCTION_OR_HOOK_CHANGE",
                    severity="HIGH",
                    filename=f.filename,
                    reason="Agent instruction, skill, rule, or lifecycle hook file modified",
                )
            )

        if auth_re.search(f.filename) or auth_re.search(joined_lines):
            signals.append(
                RiskSignal(
                    category="AUTH_AND_PERMISSIONS",
                    severity="HIGH",
                    filename=f.filename,
                    reason="Authentication, authorization, or permission logic touched",
                )
            )

        if (
            f.filename.startswith("scripts/")
            or f.filename.endswith(".sh")
            or f.filename in {"install-skills.sh", "hooks.json"}
            or exec_re.search(joined_lines)
        ):
            signals.append(
                RiskSignal(
                    category="EXECUTION_AND_SHELL",
                    severity="MEDIUM",
                    filename=f.filename,
                    reason="Executable CLI script, shell script, or subprocess execution touched",
                )
            )

        if data_re.search(f.filename) or data_re.search(joined_lines):
            signals.append(
                RiskSignal(
                    category="DATA_AND_MIGRATIONS",
                    severity="HIGH",
                    filename=f.filename,
                    reason="Persistence, migration, or destructive SQL statement touched",
                )
            )

        if (
            f.filename.startswith("docs/context/")
            or f.filename.endswith("SKILL.md")
            or "add_argument(" in joined_lines
        ):
            signals.append(
                RiskSignal(
                    category="PUBLIC_API_AND_CONTRACTS",
                    severity="MEDIUM",
                    filename=f.filename,
                    reason="Public CLI flags, skill contract, or module interface modified",
                )
            )

        if f.is_config:
            signals.append(
                RiskSignal(
                    category="DEPENDENCY_AND_CONFIG",
                    severity="MEDIUM",
                    filename=f.filename,
                    reason="Configuration or manifest file modified",
                )
            )

    if test_signals.tests_removed or test_signals.assertions_weakened or test_signals.changed_code_without_test_evidence:
        reason_parts = []
        if test_signals.tests_removed:
            reason_parts.append(f"removed tests ({len(test_signals.tests_removed)})")
        if test_signals.assertions_weakened:
            reason_parts.append("weakened assertions")
        if test_signals.changed_code_without_test_evidence:
            reason_parts.append(f"code without test evidence ({len(test_signals.changed_code_without_test_evidence)})")
        target_fn = (
            test_signals.tests_removed[0]
            if test_signals.tests_removed
            else test_signals.changed_code_without_test_evidence[0]
            if test_signals.changed_code_without_test_evidence
            else files[0].filename
            if files
            else "unknown"
        )
        signals.append(
            RiskSignal(
                category="TEST_INTEGRITY",
                severity="HIGH",
                filename=target_fn,
                reason="Test integrity signal: " + ", ".join(reason_parts),
            )
        )

    severity_rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    max_rank = max((severity_rank.get(s.severity, 1) for s in signals), default=1)
    inv_rank = {1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}
    return ChangeRiskProfile(level=inv_rank[max_rank], signals=signals, test_signals=test_signals)


def extract_invariants(workspace_root: Path, doc_paths: list[str]) -> list[str]:
    invariants: list[str] = []
    for rel in doc_paths:
        p = _resolve_within_workspace(workspace_root, rel)
        if p is None or not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        lines = text.splitlines()
        in_section = False
        for ln in lines:
            if ln.lstrip().startswith("#") and "<!-- ANCHOR: INVARIANTS -->" in ln:
                in_section = True
                continue
            if in_section:
                if ln.lstrip().startswith("#") and "<!-- ANCHOR: INVARIANTS -->" not in ln:
                    in_section = False
                    continue
                item_m = re.match(r"^\s*-[ \t]+(?:\[[xX ]\]\s*)?(.+)$", ln)
                if item_m:
                    cleaned = item_m.group(1).strip()
                    if cleaned and cleaned not in invariants:
                        invariants.append(cleaned)
    return invariants


def _read_trusted_gemini_md(workspace_root: Path, merge_base: str | None, gemini_modified: bool) -> str:
    if gemini_modified:
        if merge_base:
            res = subprocess.run(
                ["git", "-c", "core.fsmonitor=false", "show", f"{merge_base}:GEMINI.md"],
                cwd=workspace_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0:
                return res.stdout
        return ""
    gemini_path = _resolve_within_workspace(workspace_root, "GEMINI.md")
    if gemini_path is not None and gemini_path.is_file():
        return gemini_path.read_text(encoding="utf-8")
    return ""


def discover_context_and_specialists(
    workspace_root: Path,
    files: list[FileStats],
    change_risk: ChangeRiskProfile,
    merge_base: str | None = None,
) -> dict[str, list[str]]:
    untrusted_instruction_changes: list[str] = []
    changed_filenames = {f.filename for f in files}
    for fn in sorted(changed_filenames):
        if any(
            fn == pat
            or fn.endswith(f"/{pat}")
            or fn.startswith(("rules/", ".gemini/", ".agents/"))
            for pat in INSTRUCTION_PATTERNS
        ):
            untrusted_instruction_changes.append(fn)

    standard_docs: list[str] = []
    for doc_name in ("GEMINI.md", "AGENTS.md", "CLAUDE.md"):
        if (workspace_root / doc_name).exists() and doc_name not in untrusted_instruction_changes:
            standard_docs.append(doc_name)

    gemini_text = _read_trusted_gemini_md(workspace_root, merge_base, "GEMINI.md" in untrusted_instruction_changes)
    routing_rows: list[tuple[str, str]] = []
    for ln in gemini_text.splitlines():
        m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*(?:\[[^\]]+\]\(([^)]+)\)|`([^`]+)`)?", ln.strip())
        if m:
            pattern = m.group(1).strip()
            target_doc = (m.group(2) or m.group(3) or "").strip()
            if pattern and target_doc:
                routing_rows.append((pattern, target_doc))

    context_docs: list[str] = []
    unmapped_code_files: list[str] = []
    for f in files:
        matched_any = False
        for pat, doc_rel in routing_rows:
            prefix = pat.replace("/**", "/").replace("*", "")
            if fnmatch.fnmatch(f.filename, pat) or (prefix and f.filename.startswith(prefix)):
                resolved_doc = _resolve_within_workspace(workspace_root, doc_rel)
                if resolved_doc is not None and resolved_doc.is_file():
                    matched_any = True
                    if doc_rel not in context_docs:
                        context_docs.append(doc_rel)
        if not matched_any and f.filename == "install-skills.sh" and (workspace_root / "docs" / "context" / "scripts.md").is_file():
            matched_any = True
            if "docs/context/scripts.md" not in context_docs:
                context_docs.append("docs/context/scripts.md")
        if routing_rows and not matched_any and not f.is_test and not f.is_config and f.language not in {"Markdown", "unknown"}:
            unmapped_code_files.append(f.filename)

    spec_docs: list[str] = []
    specs_dir = workspace_root / "docs" / "specs"
    if specs_dir.is_dir():
        for sp in sorted(specs_dir.glob("*.md")):
            if sp.name != "README.md":
                spec_docs.append(f"docs/specs/{sp.name}")

    adr_docs: list[str] = []
    adr_dir = workspace_root / "docs" / "adr"
    if adr_dir.is_dir():
        for ap in sorted(adr_dir.glob("*.md")):
            if ap.name != "README.md":
                adr_docs.append(f"docs/adr/{ap.name}")

    trusted_invariant_docs = [doc for doc in (context_docs + spec_docs) if doc not in changed_filenames]
    for doc in sorted((set(context_docs) | set(spec_docs)) & changed_filenames):
        if doc not in untrusted_instruction_changes:
            untrusted_instruction_changes.append(doc)
    discovered_invariants = extract_invariants(workspace_root, trusted_invariant_docs)

    specialists = ["bugs_and_behavior", "fit_and_standards"]
    risk_categories = {s.category for s in change_risk.signals}
    ts = change_risk.test_signals

    if (
        context_docs
        or spec_docs
        or adr_docs
        or discovered_invariants
        or "DATA_AND_MIGRATIONS" in risk_categories
        or "PUBLIC_API_AND_CONTRACTS" in risk_categories
    ):
        specialists.append("spec_and_context")

    if ts.tests_added or ts.tests_modified or ts.tests_removed or "TEST_INTEGRITY" in risk_categories:
        specialists.append("test_quality")

    if risk_categories & {
        "AUTH_AND_PERMISSIONS",
        "EXECUTION_AND_SHELL",
        "DEPENDENCY_AND_CONFIG",
        "AGENT_INSTRUCTION_OR_HOOK_CHANGE",
        "SECRET_EXPOSURE",
    }:
        specialists.append("security_and_config")

    return {
        "context_docs": context_docs,
        "spec_docs": spec_docs,
        "adr_docs": adr_docs,
        "standard_docs": standard_docs,
        "untrusted_instruction_changes": untrusted_instruction_changes,
        "discovered_invariants": discovered_invariants,
        "recommended_specialists": specialists,
        "unmapped_code_files": unmapped_code_files,
    }


def compute_completeness(
    local_state_mode: str,
    coverage_ledger: dict[str, str],
    eligibility: PREligibility,
    recommended_specialists: list[str],
    mixed_staged_unstaged_files: list[str],
    allow_probes: bool,
    mode: str,
    unmapped_code_files: list[str] | None = None,
) -> ReviewCompleteness:
    missing_deps: list[str] = []
    for ref in eligibility.companion_refs:
        missing_deps.append(f"Companion reference {ref} not fetched")
    for chk in eligibility.failed_checks:
        missing_deps.append(f"Failing CI check: {chk}")
    for unmapped in unmapped_code_files or []:
        missing_deps.append(f"Modified code file lacks mapped context module: {unmapped}")

    skipped: list[str] = []
    if mode == "pr" and not allow_probes:
        skipped.append("runtime_probes_disabled_by_default_in_pr_mode")

    has_unreviewed = any(status != "reviewed" for status in coverage_ledger.values())
    status = "PARTIAL" if (has_unreviewed or missing_deps) else "COMPLETE"

    return ReviewCompleteness(
        review_status=status,
        local_state_mode=local_state_mode,
        completed_checks=["diff_parse", "hunk_intervals", "test_signals", "risk_scan", "context_routing"],
        dispatched_specialists=list(recommended_specialists),
        skipped_checks=skipped,
        missing_dependencies=missing_deps,
        mixed_staged_unstaged_files=mixed_staged_unstaged_files,
        coverage_ledger=coverage_ledger,
    )


def generate_suggestions(
    files: list[FileStats], workload: WorkloadProfile, change_risk: ChangeRiskProfile
) -> list[str]:
    suggestions: list[str] = []
    seen_langs: set[str] = set()
    for f in files:
        if f.language in LANGUAGE_SUGGESTIONS and f.language not in seen_langs:
            seen_langs.add(f.language)
            suggestions.append(LANGUAGE_SUGGESTIONS[f.language])
    if workload.suggested_scopes:
        suggestions.append(
            "Large diff detected; consider reviewing by --scope: " + ", ".join(workload.suggested_scopes)
        )
    if change_risk.test_signals.assertions_weakened:
        suggestions.append("Assertions were removed or weakened; verify test suite still proves intended behavior")
    return suggestions


def analyze_pr(
    workspace_root: Path,
    mode: str,
    target_id: str,
    scope: str | None,
    threshold: int,
    eligibility: PREligibility,
    diff_content: str,
    local_state_mode: str,
    mixed_files: list[str],
    flags: dict[str, bool],
) -> tuple[PRAnalysis, str]:
    files, filtered_diff, coverage_ledger = parse_diff(diff_content, scope=scope, workspace_root=workspace_root)
    workload = compute_workload(files)
    change_risk = compute_change_risk(workspace_root, files)
    routed = discover_context_and_specialists(workspace_root, files, change_risk, merge_base=eligibility.merge_base)
    completeness = compute_completeness(
        local_state_mode=local_state_mode,
        coverage_ledger=coverage_ledger,
        eligibility=eligibility,
        recommended_specialists=routed["recommended_specialists"],
        mixed_staged_unstaged_files=mixed_files,
        allow_probes=flags.get("allow_probes", False),
        mode=mode,
        unmapped_code_files=routed.get("unmapped_code_files", []),
    )
    suggestions = generate_suggestions(files, workload, change_risk)

    for f in files:
        f.added_lines = [redact_secrets(ln) for ln in f.added_lines]
        f.removed_lines = [redact_secrets(ln) for ln in f.removed_lines]

    analysis = PRAnalysis(
        mode=mode,
        target_id=target_id,
        scope=scope,
        threshold=threshold,
        eligibility=eligibility,
        workload=workload,
        change_risk=change_risk,
        completeness=completeness,
        files=files,
        suggestions=suggestions,
        context_docs=routed["context_docs"],
        spec_docs=routed["spec_docs"],
        adr_docs=routed["adr_docs"],
        standard_docs=routed["standard_docs"],
        untrusted_instruction_changes=routed["untrusted_instruction_changes"],
        discovered_invariants=routed["discovered_invariants"],
        recommended_specialists=routed["recommended_specialists"],
        flags=flags,
    )
    return analysis, redact_secrets(filtered_diff)


def verify_snapshot(manifest_path: Path, workspace_root: Path) -> tuple[bool, list[str]]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    drifted: list[str] = []
    for fentry in data.get("files", []):
        expected_sha = fentry.get("content_sha256")
        filename = fentry.get("filename")
        if not expected_sha or not filename:
            continue
        disk_path = _resolve_within_workspace(workspace_root, filename)
        if disk_path is None or not disk_path.is_file():
            drifted.append(filename)
            continue
        actual_sha = hashlib.sha256(disk_path.read_bytes()).hexdigest()
        if actual_sha != expected_sha:
            drifted.append(filename)
    return (len(drifted) == 0, drifted)


def _apply_probe_rlimits() -> None:
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
        resource.setrlimit(resource.RLIMIT_FSIZE, (1048576, 1048576))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    except (ValueError, OSError):
        pass


def run_sandboxed_probe(script_path: Path, workspace_root: Path, timeout_sec: int = 5) -> ProbeResult:
    resolved_script = script_path.resolve()
    interpreter = "bash" if resolved_script.suffix == ".sh" else sys.executable
    cmd = [interpreter, str(resolved_script)]
    start = time.monotonic()

    with tempfile.TemporaryDirectory(prefix="prcheck-probe-") as scratch_dir:
        clean_env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "HOME": scratch_dir,
            "TMPDIR": scratch_dir,
            "WORKSPACE_ROOT": str(workspace_root.resolve()),
        }
        try:
            proc = subprocess.run(
                cmd,
                cwd=scratch_dir,
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                preexec_fn=_apply_probe_rlimits if os.name == "posix" else None,
            )
            duration_ms = (time.monotonic() - start) * 1000.0
            combined = (proc.stdout or "") + (proc.stderr or "")
            sanitized = redact_secrets(combined)[:8192]
            return ProbeResult(
                command=cmd,
                exit_code=proc.returncode,
                timed_out=False,
                duration_ms=round(duration_ms, 2),
                sanitized_output=sanitized,
            )
        except subprocess.TimeoutExpired as exc:
            duration_ms = (time.monotonic() - start) * 1000.0
            out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
            err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
            sanitized = redact_secrets(out + err)[:8192]
            return ProbeResult(
                command=cmd,
                exit_code=124,
                timed_out=True,
                duration_ms=round(duration_ms, 2),
                sanitized_output=sanitized,
            )


def run_flow_prcheck(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    workspace_root = Path(args.dir).resolve()

    if args.cleanup_target:
        out_path = Path(args.output_dir or "docs/plans/.tmp")
        tid = args.cleanup_target.strip()
        for intermediate_name in (
            f"prcheck-context-{tid}.json",
            f"prcheck-sliced-{tid}.diff",
            f"prcheck-candidates-{tid}.json",
            "prcheck-context.json",
            "prcheck-sliced.diff",
        ):
            (out_path / intermediate_name).unlink(missing_ok=True)
        return 0

    if args.verify_snapshot:
        ok, drifted = verify_snapshot(Path(args.verify_snapshot), workspace_root)
        if not ok:
            print(f"STALE_SNAPSHOT: files modified since review snapshot: {', '.join(drifted)}", file=sys.stderr)
            return 3
        return 0

    if args.run_probe:
        probe_res = run_sandboxed_probe(Path(args.run_probe), workspace_root, timeout_sec=5)
        print(json.dumps(asdict(probe_res), indent=2))
        return 0 if not probe_res.timed_out else 124

    try:
        mode, target_id, pr_number = validate_target(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    local_state_mode = "working-tree"
    mixed_files: list[str] = []
    if mode == "file":
        local_state_mode = "file"
        diff_path = Path(args.diff_file)
        if not diff_path.is_file():
            print(f"Error: diff file not found: {diff_path}", file=sys.stderr)
            return 2
        diff_content = diff_path.read_text(encoding="utf-8")
        eligibility = PREligibility(mode="file", target_id="file", eligible=bool(diff_content.strip()))
        if not eligibility.eligible:
            eligibility.ineligible_reason = "No changes to review"
    elif mode == "pr":
        local_state_mode = "pr"
        eligibility, diff_content = probe_github_pr(workspace_root, args.target, pr_number=pr_number)
    else:
        if args.staged:
            local_state_mode = "staged"
        elif args.committed:
            local_state_mode = "committed"
        eligibility, diff_content, mixed_files = acquire_local_diff(
            workspace_root, base_ref=args.base, local_state_mode=local_state_mode
        )

    flags = {
        "fix": bool(args.fix),
        "draft_review": bool(args.draft_review),
        "comment": bool(args.comment),
        "allow_probes": bool(args.allow_probes or mode != "pr"),
    }

    analysis, sanitized_diff = analyze_pr(
        workspace_root=workspace_root,
        mode=mode,
        target_id=target_id,
        scope=args.scope,
        threshold=args.threshold,
        eligibility=eligibility,
        diff_content=diff_content,
        local_state_mode=local_state_mode,
        mixed_files=mixed_files,
        flags=flags,
    )

    serialized = redact_secrets(json.dumps(asdict(analysis), indent=2))
    if args.output_dir:
        out_path = Path(args.output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        tid = analysis.target_id
        for stale_name in (
            f"prcheck-candidates-{tid}.json",
            f"prcheck-{tid}.md",
            f"prcheck-context-{tid}.json",
            f"prcheck-sliced-{tid}.diff",
        ):
            (out_path / stale_name).unlink(missing_ok=True)
        (out_path / f"prcheck-context-{tid}.json").write_text(serialized + "\n", encoding="utf-8")
        (out_path / f"prcheck-sliced-{tid}.diff").write_text(sanitized_diff, encoding="utf-8")
        (out_path / "prcheck-context.json").write_text(serialized + "\n", encoding="utf-8")
        (out_path / "prcheck-sliced.diff").write_text(sanitized_diff, encoding="utf-8")

    if args.json:
        print(serialized)
    else:
        print(
            f"[flow-prcheck] mode={analysis.mode} target={analysis.target_id} "
            f"eligible={analysis.eligibility.eligible} size='{analysis.workload.size_category}' "
            f"risk={analysis.change_risk.level} status={analysis.completeness.review_status}"
        )
        if args.stats:
            for f in analysis.files:
                role = "test" if f.is_test else "config" if f.is_config else "code"
                print(f"  - {f.filename} ({f.language}, {role}): +{f.additions}/-{f.deletions}")
    return 0


if __name__ == "__main__":
    sys.exit(run_flow_prcheck())
