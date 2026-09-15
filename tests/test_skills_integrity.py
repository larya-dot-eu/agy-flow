# tests/test_skills_integrity.py
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
