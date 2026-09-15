import argparse
import datetime
import os
import sys
import json
import shutil
import subprocess
import time
from pathlib import Path

DEFAULT_GITIGNORE = """# Operating System & IDEs
.DS_Store
Thumbs.db
.idea/
.vscode/
*.swp
*.swo

# Secrets, Keys & Environment Variables
.env
.env.*
*.pem
*.key
*.token
*.secret
credentials.json
auth.json

# Antigravity CLI & AI Agents Local Memory & Artifacts
.tmp/
docs/**/.tmp/
brain/
artifacts/
scratch/
.system_generated/
.gemini/
.agents/
.antigravity/
*.transcript.*
*.jsonl

# Build & Dependency Artifacts
__pycache__/
*.pyc
node_modules/
dist/
build/
target/
.venv/
venv/

# agy-flow Lifecycle Artifacts (Local only - never pushed to git)
docs/specs/*
!docs/specs/.gitkeep
!docs/specs/README.md

docs/plans/*
!docs/plans/.gitkeep
!docs/plans/README.md

docs/context/*
!docs/context/.gitkeep
!docs/context/README.md

docs/adr/*
!docs/adr/.gitkeep
!docs/adr/README.md
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

def detect_project_stack(workspace_root: Path) -> dict:
    languages = []
    build_tools = []
    test_cmd = None
    dev_cmd = None

    # Python check
    if any((workspace_root / f).exists() for f in ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile", "poetry.lock", "uv.lock"]):
        languages.append("Python")
        if (workspace_root / "pyproject.toml").exists() or (workspace_root / "pytest.ini").exists():
            test_cmd = "pytest"
        else:
            test_cmd = "python3 -m unittest discover tests"

    # Node / TS check
    if (workspace_root / "package.json").exists():
        languages.append("TypeScript / JavaScript")
        try:
            pkg = json.loads((workspace_root / "package.json").read_text(encoding="utf-8"))
            scripts = pkg.get("scripts", {})
            if "test" in scripts:
                test_cmd = "npm test"
            if "dev" in scripts:
                dev_cmd = "npm run dev"
            elif "start" in scripts:
                dev_cmd = "npm start"
        except Exception:
            if not test_cmd:
                test_cmd = "npm test"

    # Rust check
    if (workspace_root / "Cargo.toml").exists():
        languages.append("Rust")
        build_tools.append("cargo")
        if not test_cmd:
            test_cmd = "cargo test"

    # Go check
    if (workspace_root / "go.mod").exists():
        languages.append("Go")
        build_tools.append("go")
        if not test_cmd:
            test_cmd = "go test ./..."

    # Docker check
    if any((workspace_root / f).exists() for f in ["Dockerfile", "docker-compose.yml", "compose.yaml"]):
        build_tools.append("Docker")

    # Makefile check
    if (workspace_root / "Makefile").exists():
        build_tools.append("Make")

    if not languages:
        languages.append("Generic / Markdown")
    if not test_cmd:
        test_cmd = "echo 'No automated tests configured'"

    return {
        "languages": languages,
        "build_tools": build_tools,
        "test_cmd": test_cmd,
        "dev_cmd": dev_cmd
    }

IGNORED_DIRS = {
    ".git", ".tmp", "node_modules", "dist", "build", "target",
    "__pycache__", ".venv", "venv", ".idea", ".vscode", "docs"
}

def discover_subsystems(workspace_root: Path) -> list[tuple[str, str, str]]:
    subsystems = []
    for entry in sorted(workspace_root.iterdir()):
        if entry.is_dir() and entry.name not in IGNORED_DIRS and not entry.name.startswith("."):
            sub_name = entry.name
            # Check for immediate child modules under src/ or lib/
            valid_children = [
                child for child in entry.iterdir()
                if child.is_dir() and child.name not in IGNORED_DIRS and not child.name.startswith(".")
            ]
            if sub_name in {"src", "lib", "app", "pkg"} and valid_children:
                for child in sorted(valid_children):
                    module_slug = f"{sub_name}-{child.name}"
                    subsystems.append((f"{sub_name}/{child.name}/**", f"docs/context/{module_slug}.md", f"{child.name.title()} Subsystem"))
            else:
                subsystems.append((f"{sub_name}/**", f"docs/context/{sub_name}.md", f"{sub_name.title()} Subsystem"))

    if not subsystems:
        subsystems.append(("src/**", "docs/context/core.md", "Core Application Logic"))

    return subsystems

def render_gemini_md(project_name: str, stack_info: dict, subsystems: list[tuple[str, str, str]]) -> str:
    langs = ", ".join(stack_info.get("languages", ["Generic"]))
    tools = ", ".join(stack_info.get("build_tools", [])) or "Standard CLI"
    test_cmd = stack_info.get("test_cmd", "pytest")
    dev_cmd = stack_info.get("dev_cmd", "# Start development server")

    routing_rows = "\n".join(
        f"| `{pattern}` | [`{doc}`]({doc}) | {desc} |"
        for pattern, doc, desc in subsystems
    )

    return f"""# {project_name} - Workspace Directives

## Stack <!-- ANCHOR: STACK -->
- **Languages**: {langs}
- **Build / Tooling**: {tools}
- **Primary Test Runner**: `{test_cmd}`

---

## Context Routing Map <!-- ANCHOR: CONTEXT_ROUTING -->

| Path Pattern | Context Document | Description |
| :--- | :--- | :--- |
{routing_rows}

---

## Frequent Commands <!-- ANCHOR: COMMANDS -->
- **Test**: `{test_cmd}`
- **Dev**: `{dev_cmd}`

---

## Agent Directives <!-- ANCHOR: DIRECTIVES -->
- Follow the 10-Phase Engineering Lifecycle (`/flow`).
- Zero-Discovery Context Routing: Read mapped `docs/context/*.md` before scanning repository files.
- Test-Driven Development: Never write production code before tests (Red -> Green -> Refactor).
"""

def generate_gemini_and_agents_md(workspace_root: Path, project_name: str, stack_info: dict, subsystems: list[tuple[str, str, str]], force: bool = False) -> tuple[Path, Path]:
    gemini_path = workspace_root / "GEMINI.md"
    if gemini_path.exists() and not force:
        raise FileExistsError(f"{gemini_path} already exists. Pass --force to overwrite.")

    content = render_gemini_md(project_name, stack_info, subsystems)
    gemini_path.write_text(content, encoding="utf-8")

    agents_path = workspace_root / "AGENTS.md"
    if agents_path.exists() or agents_path.is_symlink():
        if force:
            if agents_path.is_symlink() or agents_path.is_file():
                agents_path.unlink()
        else:
            return gemini_path, agents_path

    try:
        agents_path.symlink_to("GEMINI.md")
    except Exception:
        shutil.copyfile(gemini_path, agents_path)

    return gemini_path, agents_path

CONTEXT_MODULE_TEMPLATE = """# {name} Context Module

- **Path Mapping**: `{path_glob}`
- **Last Verified**: {date}

---

## 1. Purpose & Responsibility <!-- ANCHOR: PURPOSE -->
{description}.

---

## 2. Public Interfaces & Contracts <!-- ANCHOR: CONTRACTS -->

| Interface / Symbol | Type | Responsibility |
| :--- | :--- | :--- |
| `[SymbolName]` | Class / Function | [Description] |

---

## 3. Current Invariants & State <!-- ANCHOR: INVARIANTS -->
- [ ] Invariant 1: [Core domain rule]
"""

ADR_README_TEMPLATE = """# Architecture Decision Records (ADR)

This directory contains records of architecturally significant decisions following the MADR / Y-Statement standard.

## Index <!-- ANCHOR: ADR_INDEX -->
- [0000-template.md](0000-template.md): Canonical ADR Template
"""

def scaffold_context_and_adr(workspace_root: Path, subsystems: list[tuple[str, str, str]], force: bool = False) -> list[Path]:
    created = []
    context_dir = workspace_root / "docs" / "context"
    adr_dir = workspace_root / "docs" / "adr"

    context_dir.mkdir(parents=True, exist_ok=True)
    adr_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.date.today().isoformat()

    for path_glob, doc_rel, desc in subsystems:
        doc_path = workspace_root / doc_rel
        if not doc_path.exists() or force:
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            content = CONTEXT_MODULE_TEMPLATE.format(
                name=desc,
                path_glob=path_glob,
                date=today,
                description=desc
            )
            doc_path.write_text(content, encoding="utf-8")
            created.append(doc_path)

    adr_readme = adr_dir / "README.md"
    if not adr_readme.exists() or force:
        adr_readme.write_text(ADR_README_TEMPLATE, encoding="utf-8")
        created.append(adr_readme)

    return created

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Universal /flow-init Bootstrap & Project Onboarding Suite")
    parser.add_argument("-d", "--dir", default=".", help="Target workspace root directory")
    parser.add_argument("-y", "--yes", action="store_true", help="Non-interactive execution with defaults")
    parser.add_argument("--name", default=None, help="Project name override")
    parser.add_argument("--git-init", action="store_true", help="Explicitly enable git init in non-interactive mode")
    parser.add_argument("--no-git", action="store_true", help="Skip git detection and initialization")
    parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing GEMINI.md and scaffolds")
    return parser.parse_args(argv)

def run_flow_init(argv: list[str] | None = None) -> int:
    start_time = time.time()
    args = parse_args(argv)
    workspace_root = Path(args.dir).resolve()

    if not workspace_root.exists():
        print(f"❌ Error: Workspace directory '{workspace_root}' does not exist.")
        return 1

    project_name = args.name or workspace_root.name

    print("=" * 65)
    print(" 🚀 Initializing Antigravity Project Memory (/flow-init)")
    print(f" Target: {workspace_root}")
    print("=" * 65)

    # 1. Git probe
    allow_git = args.git_init
    if not args.no_git and not (workspace_root / ".git").exists() and not args.yes:
        try:
            ans = input("No git repository detected. Initialize git in this directory? (y/N): ").strip().lower()
            if ans in {"y", "yes"}:
                allow_git = True
        except EOFError:
            pass

    git_info = inspect_git_environment(workspace_root, allow_git_init=allow_git, skip_git=args.no_git)
    if git_info["git_initialized"]:
        print("  [+] Initialized git repository and starter .gitignore")
    elif git_info["is_git_repo"]:
        print("  [+] Git repository detected")

    if git_info["user_name"] and git_info["user_email"]:
        print(f"  [+] Git identity: {git_info['user_name']} <{git_info['user_email']}>")
    elif git_info["is_git_repo"]:
        print("  [!] Notice: git user.name / user.email not configured locally")

    if git_info["gh_auth"]:
        print(f"  [+] GitHub CLI: {git_info['gh_auth']}")

    # 2. Stack probe
    stack_info = detect_project_stack(workspace_root)
    print(f"  [+] Detected Stack: {', '.join(stack_info['languages'])}")
    print(f"  [+] Discovered Test Command: {stack_info['test_cmd']}")

    # 3. Topology probe
    subsystems = discover_subsystems(workspace_root)
    print(f"  [+] Discovered {len(subsystems)} subsystem boundaries for Context Routing")

    # 4. Scaffolding
    try:
        gemini_path, agents_path = generate_gemini_and_agents_md(
            workspace_root, project_name, stack_info, subsystems, force=args.force
        )
        print(f"  [+] Generated {gemini_path.name}")
        print(f"  [+] Created {agents_path.name} (symlink -> GEMINI.md)")
    except FileExistsError as e:
        print(f"  [!] Notice: {e}")

    scaffolded = scaffold_context_and_adr(workspace_root, subsystems, force=args.force)
    for p in scaffolded:
        print(f"  [+] Scaffolded {p.relative_to(workspace_root)}")

    elapsed_ms = (time.time() - start_time) * 1000
    print("=" * 65)
    print(f"✅ [SUCCESS] Antigravity project memory initialized in {elapsed_ms:.1f}ms (SLA: <= 200ms)")
    print("=" * 65)
    return 0

if __name__ == "__main__":
    sys.exit(run_flow_init())


