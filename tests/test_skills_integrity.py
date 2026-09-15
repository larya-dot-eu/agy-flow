# tests/test_skills_integrity.py
import os
import sys
import json
import re
from pathlib import Path

FENCE_REGEX = re.compile(r"^([`~]{3,})(.*)$")

def validate_code_fences(content: str, file_path: Path) -> list[str]:
    errors = []
    lines = content.splitlines()
    fence_stack = []

    for idx, line in enumerate(lines, start=1):
        match = FENCE_REGEX.match(line.strip())
        if match:
            fence_chars, info = match.group(1), match.group(2).strip()
            fence_char = fence_chars[0]
            fence_len = len(fence_chars)

            if not fence_stack:
                # Opening fence
                fence_stack.append((idx, fence_char, fence_len, info))
            else:
                top_idx, top_char, top_len, top_info = fence_stack[-1]
                # In CommonMark, a valid closing fence has NO info string and length >= top_len
                if fence_char == top_char and fence_len >= top_len and not info:
                    fence_stack.pop()
                elif info:
                    # An opening fence encountered while already inside a code block
                    if "markdown" in top_info.lower() and fence_len < top_len:
                        pass  # Valid nested code block
                    else:
                        errors.append(
                            f"{file_path}:{idx}: Nested code fence ({fence_char * fence_len} {info}) colliding with outer fence opened at line {top_idx}"
                        )
                elif fence_char == top_char and fence_len < top_len:
                    # Inner closing fence inside markdown
                    if "markdown" in top_info.lower() or not top_info:
                        pass
                    else:
                        errors.append(f"{file_path}:{idx}: Unexpected fence delimiter inside code block opened at line {top_idx}")

    for top_idx, top_char, top_len, top_info in fence_stack:
        errors.append(f"{file_path}:{top_idx}: Unclosed code fence ({top_char * top_len})")

    return errors

ANTIGRAVITY_TOOLS = {
    "view_file", "write_to_file", "replace_file_content", "run_command",
    "invoke_subagent", "manage_task", "define_subagent", "manage_subagents",
    "send_message", "schedule", "generate_image", "read_url_content",
    "search_web", "find_by_name", "grep_search", "list_dir", "ask_question"
}

DEPRECATED_OR_INVALID_TOOLS = {
    "edit_file", "read_file", "str_replace_editor", "execute_command", "bash_command"
}

SUBAGENT_TYPENAME_REGEX = re.compile(r'"TypeName"\s*:\s*"([^"]+)"')
TOOL_MENTION_REGEX = re.compile(r'`([a-z_]+)`\s+tool\b')

def validate_tool_and_subagent_contracts(content: str, file_path: Path) -> list[str]:
    errors = []
    lines = content.splitlines()

    for idx, line in enumerate(lines, start=1):
        # Subagent TypeName check
        match = SUBAGENT_TYPENAME_REGEX.search(line)
        if match:
            type_name = match.group(1)
            if type_name not in {"self", "research"}:
                errors.append(f"{file_path}:{idx}: Invalid subagent TypeName '{type_name}'. Must be 'self' or 'research'.")

        # Explicit tool mention checks
        for match in TOOL_MENTION_REGEX.finditer(line):
            tool_name = match.group(1)
            if tool_name in DEPRECATED_OR_INVALID_TOOLS or tool_name not in ANTIGRAVITY_TOOLS:
                errors.append(f"{file_path}:{idx}: Invalid or unrecognized Antigravity tool name '{tool_name}'.")

        # Deprecated tool direct mentions
        for bad_tool in DEPRECATED_OR_INVALID_TOOLS:
            if re.search(rf"\b{bad_tool}\b", line) and not re.search(rf"deprecated|invalid|banned|do not use\s+{bad_tool}", line, re.IGNORECASE):
                errors.append(f"{file_path}:{idx}: Deprecated tool name '{bad_tool}' detected.")

    return errors

CD_IN_CMD_REGEX = re.compile(r'(?:CommandLine|Run|bash|sh)[:\s`]+"?cd\s+[^\n&;|]+(?:&&|;|\n|")', re.IGNORECASE)
MANAGE_TASK_TODO_REGEX = re.compile(r'manage_task\s+(?:to\s+manage\s+(?:the\s+|your\s+)?|for\s+(?:the\s+|your\s+)?)(?:todo|checklist|tasks)', re.IGNORECASE)

def validate_tooling_discipline(content: str, file_path: Path) -> list[str]:
    errors = []
    lines = content.splitlines()

    for idx, line in enumerate(lines, start=1):
        if CD_IN_CMD_REGEX.search(line) and not re.search(r'never propose a cd|do not use cd', line, re.IGNORECASE):
            errors.append(f"{file_path}:{idx}: Prohibited 'cd' in command detected. Use Cwd parameter or relative paths.")
        if MANAGE_TASK_TODO_REGEX.search(line):
            # Verify line does not explicitly state "Never" or "Do not"
            if not re.search(r'\b(never|do not|don\'t|avoid)\b.*manage_task', line, re.IGNORECASE):
                errors.append(f"{file_path}:{idx}: Misuse of manage_task for todos detected. manage_task is strictly for background OS processes.")

    return errors

AG_FLOW_TYPO_REGEX = re.compile(r'\bAg-Flow\b')
SLASH_COMMAND_TYPO_REGEX = re.compile(r'/flow_[a-z]+')

def validate_terminology(content: str, file_path: Path) -> list[str]:
    errors = []
    lines = content.splitlines()

    for idx, line in enumerate(lines, start=1):
        if AG_FLOW_TYPO_REGEX.search(line):
            errors.append(f"{file_path}:{idx}: Prohibited term 'Ag-Flow' detected. Use 'agy-flow' or 'Antigravity Flow'.")
        if SLASH_COMMAND_TYPO_REGEX.search(line):
            errors.append(f"{file_path}:{idx}: Malformed slash command with underscore detected. Use kebab-case (e.g. /flow-spec).")

    return errors

def validate_skill_frontmatter(skill_dir: Path) -> list[str]:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return [f"{skill_dir}: Missing SKILL.md file"]

    content = skill_file.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return [f"{skill_file}:1: Missing YAML frontmatter leading '---'"]

    parts = content.split("---", 2)
    if len(parts) < 3:
        return [f"{skill_file}:1: Unclosed YAML frontmatter"]

    frontmatter = parts[1]
    errors = []
    metadata = {}

    for line in frontmatter.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            metadata[k.strip()] = v.strip().strip('"').strip("'")

    required_keys = {"name", "description", "risk", "source"}
    missing = required_keys - set(metadata.keys())
    if missing:
        errors.append(f"{skill_file}: Missing required frontmatter keys: {', '.join(sorted(missing))}")

    if "name" in metadata and metadata["name"] != skill_dir.name:
        errors.append(f"{skill_file}: Frontmatter name '{metadata['name']}' does not match directory '{skill_dir.name}'")

    if "risk" in metadata and metadata["risk"] not in {"low", "medium", "high", "critical"}:
        errors.append(f"{skill_file}: Invalid risk '{metadata['risk']}'. Must be low, medium, high, or critical.")

    return errors

RESOURCE_REF_REGEX = re.compile(r'(?:[a-zA-Z0-9_\-]+/)?(?:resources|references)/[a-zA-Z0-9_\-\.]+')

def validate_skill_resources_and_references(skill_dir: Path) -> list[str]:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return []

    content = skill_file.read_text(encoding="utf-8")
    errors = []
    lines = content.splitlines()
    skills_root = skill_dir.parent
    repo_root = skills_root.parent

    for idx, line in enumerate(lines, start=1):
        for match in RESOURCE_REF_REGEX.finditer(line):
            rel_path = match.group(0)
            # Resolve: 1. Relative to skill_dir, 2. Relative to skills_root, 3. Relative to repo_root
            candidates = [
                skill_dir / rel_path,
                skills_root / rel_path,
                repo_root / rel_path,
                repo_root / "skills" / rel_path
            ]
            # Also check if it's a generic canonical template filename under any skill's resources
            if not any(c.exists() for c in candidates):
                # Search across all skills/ for resources/filename
                base_name = Path(rel_path).name
                found_in_any_skill = any((s / "resources" / base_name).exists() for s in skills_root.iterdir() if s.is_dir())
                if not found_in_any_skill:
                    errors.append(f"{skill_file}:{idx}: Referenced resource missing on disk: '{rel_path}'")

    return errors

def validate_repo_inventory_and_permissions(repo_root: Path) -> list[str]:
    errors = []
    skills_dir = repo_root / "skills"
    if not skills_dir.exists():
        return [f"{repo_root}: Missing skills/ directory"]

    discovered_skills = {p.name for p in skills_dir.iterdir() if p.is_dir() and (p / "SKILL.md").exists()}

    # Verify exact 12 flow skills exist
    if len(discovered_skills) < 12:
        errors.append(f"Expected at least 12 flow skills, but found {len(discovered_skills)}: {sorted(discovered_skills)}")

    # Check README.md, HOWTO.md, and flow-master/SKILL.md
    check_files = [
        repo_root / "README.md",
        repo_root / "HOWTO.md",
        repo_root / "skills" / "flow-master" / "SKILL.md"
    ]

    for cf in check_files:
        if cf.exists():
            content = cf.read_text(encoding="utf-8")
            for skill in discovered_skills:
                # 'flow-master' can be mentioned as 'flow-master' or '/flow '
                if skill == "flow-master":
                    if "flow-master" not in content and "/flow" not in content:
                        errors.append(f"{cf}: Missing mention of skill 'flow-master' / '/flow'")
                else:
                    if skill not in content:
                        errors.append(f"{cf}: Missing mention of skill '{skill}'")

    # Check install-skills.sh copies skills directory
    installer = repo_root / "install-skills.sh"
    if installer.exists():
        content = installer.read_text(encoding="utf-8")
        if "skills" not in content:
            errors.append(f"{installer}: Missing skills directory copy logic in installer")

    # Check script executable permissions
    scripts = [
        repo_root / "install-skills.sh",
        repo_root / "scripts" / "context-guard.sh"
    ]
    for script in scripts:
        if script.exists():
            if not os.access(script, os.X_OK):
                errors.append(f"{script}: Script is not executable (+x)")

    # Check json syntax
    for json_file in [repo_root / "plugin.json", repo_root / "hooks.json"]:
        if json_file.exists():
            try:
                json.loads(json_file.read_text(encoding="utf-8"))
            except Exception as e:
                errors.append(f"{json_file}: Invalid JSON syntax: {e}")

    return errors
