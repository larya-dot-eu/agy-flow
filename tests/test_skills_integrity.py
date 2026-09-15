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
