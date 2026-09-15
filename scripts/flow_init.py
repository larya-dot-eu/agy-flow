# scripts/flow_init.py
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

DEFAULT_GITIGNORE = """# agy-flow local artifacts
.tmp/
docs/**/.tmp/
__pycache__/
*.pyc
node_modules/
dist/
build/
target/
.env
.DS_Store
"""

def inspect_git_environment(workspace_root: Path, allow_git_init: bool = False, skip_git: bool = False) -> dict:
    if skip_git:
        return {"is_git_repo": False, "git_initialized": False, "user_name": None, "user_email": None, "gh_auth": None}

    git_dir = workspace_root / ".git"
    is_git_repo = git_dir.exists() and git_dir.is_dir()
    git_initialized = False

    if not is_git_repo and allow_git_init:
        res = subprocess.run(["git", "init"], cwd=str(workspace_root), capture_output=True, text=True)
        if res.returncode == 0:
            is_git_repo = True
            git_initialized = True
            gitignore = workspace_root / ".gitignore"
            if not gitignore.exists():
                gitignore.write_text(DEFAULT_GITIGNORE, encoding="utf-8")

    user_name = None
    user_email = None
    gh_auth = None

    if is_git_repo:
        try:
            name_res = subprocess.run(["git", "config", "user.name"], cwd=str(workspace_root), capture_output=True, text=True)
            if name_res.returncode == 0 and name_res.stdout.strip():
                user_name = name_res.stdout.strip()
            email_res = subprocess.run(["git", "config", "user.email"], cwd=str(workspace_root), capture_output=True, text=True)
            if email_res.returncode == 0 and email_res.stdout.strip():
                user_email = email_res.stdout.strip()
        except Exception:
            pass

    # Check GitHub CLI if available
    try:
        gh_res = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        if gh_res.returncode == 0:
            gh_auth = "Logged in"
    except Exception:
        pass

    return {
        "is_git_repo": is_git_repo,
        "git_initialized": git_initialized,
        "user_name": user_name,
        "user_email": user_email,
        "gh_auth": gh_auth
    }
