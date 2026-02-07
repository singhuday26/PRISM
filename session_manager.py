#!/usr/bin/env python3
"""
PRISM Session Manager
=====================
Manages Claude planning sessions by backing up temporary plan files
to permanent markdown files in the planning/ directory, maintaining
a searchable index, and providing CLI commands to manage sessions.

Usage:
    python session_manager.py new "Session Title"
    python session_manager.py save [--source PATH]
    python session_manager.py list [--verbose]
    python session_manager.py load <session_id>
    python session_manager.py cleanup
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
PLANNING_DIR = PROJECT_ROOT / "planning"
INDEX_FILE = PLANNING_DIR / "session_index.json"

# Default locations where Claude stores plan files
CLAUDE_PLANS_DIR = Path.home() / ".claude" / "plans"
TMPCLAUDE_PATTERN = "tmpclaude-*"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_planning_dir() -> None:
    """Create the planning/ directory if it doesn't exist."""
    PLANNING_DIR.mkdir(parents=True, exist_ok=True)


def _load_index() -> dict:
    """Load the session index from disk, or return an empty structure."""
    if INDEX_FILE.exists():
        try:
            return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"Warning: could not read index ({exc}); starting fresh.")
    return {"sessions": [], "last_updated": None}


def _save_index(index: dict) -> None:
    """Persist the session index to disk."""
    _ensure_planning_dir()
    index["last_updated"] = datetime.now().isoformat()
    INDEX_FILE.write_text(
        json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _generate_session_id(title: str) -> str:
    """Create a filesystem-safe session id from a title and timestamp."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}_{slug}"


def _extract_title_from_markdown(text: str) -> str:
    """Try to pull a title from the first markdown heading."""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line.lstrip("# ").strip()
    return "Untitled Session"


def _find_claude_plan_files() -> list[Path]:
    """Return all .md files in the Claude plans directory, newest first."""
    if not CLAUDE_PLANS_DIR.exists():
        return []
    files = sorted(CLAUDE_PLANS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def _find_temp_cwd_files() -> list[Path]:
    """Return all tmpclaude-*-cwd temp files in the project root."""
    return sorted(PROJECT_ROOT.glob(TMPCLAUDE_PATTERN))


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_new(args: argparse.Namespace) -> int:
    """Create a new empty planning session."""
    _ensure_planning_dir()
    title = args.title
    session_id = _generate_session_id(title)
    filename = f"{session_id}.md"
    filepath = PLANNING_DIR / filename

    header = (
        f"# {title}\n\n"
        f"**Session ID:** {session_id}\n"
        f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"**Status:** active\n\n"
        "---\n\n"
        "## Notes\n\n"
        "_Start writing your session notes here._\n"
    )
    filepath.write_text(header, encoding="utf-8")

    # Update index
    index = _load_index()
    index["sessions"].append(
        {
            "id": session_id,
            "title": title,
            "file": filename,
            "created": datetime.now().isoformat(),
            "source": "manual",
            "status": "active",
        }
    )
    _save_index(index)

    print(f"Created new session: {filepath}")
    print(f"Session ID: {session_id}")
    return 0


def cmd_save(args: argparse.Namespace) -> int:
    """Backup Claude plan files into the planning/ directory."""
    _ensure_planning_dir()

    source_dir = Path(args.source) if args.source else CLAUDE_PLANS_DIR

    if not source_dir.exists():
        print(f"Error: source directory does not exist: {source_dir}")
        return 1

    plan_files = sorted(source_dir.glob("*.md"), key=lambda p: p.stat().st_mtime)
    if not plan_files:
        print(f"No markdown plan files found in {source_dir}")
        return 1

    index = _load_index()
    existing_sources = {s.get("original_file") for s in index["sessions"]}
    saved_count = 0

    for plan_file in plan_files:
        # Skip files already saved (by original filename)
        if plan_file.name in existing_sources:
            print(f"  Skipping (already saved): {plan_file.name}")
            continue

        content = plan_file.read_text(encoding="utf-8", errors="replace")
        title = _extract_title_from_markdown(content)
        session_id = _generate_session_id(title)
        dest_filename = f"{session_id}.md"
        dest_path = PLANNING_DIR / dest_filename

        # Prepend metadata header
        mtime = datetime.fromtimestamp(plan_file.stat().st_mtime)
        metadata = (
            f"<!-- Session Manager Metadata\n"
            f"session_id: {session_id}\n"
            f"original_file: {plan_file.name}\n"
            f"saved_at: {datetime.now().isoformat()}\n"
            f"original_modified: {mtime.isoformat()}\n"
            f"-->\n\n"
        )
        dest_path.write_text(metadata + content, encoding="utf-8")

        index["sessions"].append(
            {
                "id": session_id,
                "title": title,
                "file": dest_filename,
                "created": mtime.isoformat(),
                "saved_at": datetime.now().isoformat(),
                "source": str(source_dir),
                "original_file": plan_file.name,
                "status": "saved",
            }
        )
        saved_count += 1
        print(f"  Saved: {plan_file.name} -> {dest_filename}")

    _save_index(index)
    print(f"\n{saved_count} session(s) saved to {PLANNING_DIR}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List all tracked sessions."""
    index = _load_index()
    sessions = index.get("sessions", [])

    if not sessions:
        print("No sessions found. Run 'save' to import Claude plans or 'new' to create one.")
        return 0

    # Header
    print(f"\n{'#':<4} {'Status':<8} {'Created':<20} {'Title'}")
    print("-" * 80)

    for i, session in enumerate(sessions, 1):
        created = session.get("created", "")[:19].replace("T", " ")
        status = session.get("status", "?")
        title = session.get("title", "Untitled")
        print(f"{i:<4} {status:<8} {created:<20} {title}")

        if args.verbose:
            print(f"     ID:   {session.get('id', 'n/a')}")
            print(f"     File: {session.get('file', 'n/a')}")
            if session.get("original_file"):
                print(f"     From: {session['original_file']}")
            print()

    print(f"\nTotal: {len(sessions)} session(s)")
    if index.get("last_updated"):
        print(f"Index updated: {index['last_updated'][:19].replace('T', ' ')}")
    return 0


def cmd_load(args: argparse.Namespace) -> int:
    """Load and display a session by ID, number, or search term."""
    index = _load_index()
    sessions = index.get("sessions", [])
    query = args.session_id

    match = None

    # Try as a 1-based list number
    try:
        num = int(query)
        if 1 <= num <= len(sessions):
            match = sessions[num - 1]
    except ValueError:
        pass

    # Try exact ID match
    if match is None:
        for s in sessions:
            if s.get("id") == query:
                match = s
                break

    # Try substring search on title or ID
    if match is None:
        query_lower = query.lower()
        candidates = [s for s in sessions if query_lower in s.get("title", "").lower() or query_lower in s.get("id", "").lower()]
        if len(candidates) == 1:
            match = candidates[0]
        elif len(candidates) > 1:
            print(f"Ambiguous query '{query}'. Matches:")
            for c in candidates:
                print(f"  - {c['id']}: {c['title']}")
            return 1

    if match is None:
        print(f"No session found for: {query}")
        print("Use 'list' to see available sessions.")
        return 1

    filepath = PLANNING_DIR / match["file"]
    if not filepath.exists():
        print(f"Error: session file missing: {filepath}")
        return 1

    content = filepath.read_text(encoding="utf-8")
    print(f"=== Session: {match['title']} ===")
    print(f"ID: {match['id']}")
    print(f"File: {filepath}")
    print(f"Created: {match.get('created', 'unknown')}")
    print("=" * 60)
    print(content)
    return 0


def cmd_cleanup(args: argparse.Namespace) -> int:
    """Remove tmpclaude-* temporary files from the project root."""
    temp_files = _find_temp_cwd_files()
    nul_file = PROJECT_ROOT / "nul"

    targets = list(temp_files)
    if nul_file.exists() and nul_file.is_file():
        targets.append(nul_file)

    if not targets:
        print("No temporary files found to clean up.")
        return 0

    print(f"Found {len(targets)} temporary file(s):")
    for f in targets:
        print(f"  {f.name}")

    if not args.yes:
        confirm = input("\nDelete these files? [y/N] ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return 0

    deleted = 0
    for f in targets:
        try:
            if f.is_dir():
                shutil.rmtree(f)
            else:
                f.unlink()
            deleted += 1
        except OSError as exc:
            print(f"  Failed to delete {f.name}: {exc}")

    print(f"\nDeleted {deleted}/{len(targets)} file(s).")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Show a summary of session state: plans, temp files, index health."""
    print("=== PRISM Session Manager Status ===\n")

    # Claude plans directory
    plan_files = _find_claude_plan_files()
    print(f"Claude plans directory: {CLAUDE_PLANS_DIR}")
    print(f"  Plan files found: {len(plan_files)}")
    for pf in plan_files:
        mtime = datetime.fromtimestamp(pf.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"    {pf.name} ({mtime})")

    # Planning directory
    print(f"\nPlanning directory: {PLANNING_DIR}")
    if PLANNING_DIR.exists():
        saved = list(PLANNING_DIR.glob("*.md"))
        print(f"  Saved sessions: {len(saved)}")
    else:
        print("  Not created yet")

    # Index
    index = _load_index()
    sessions = index.get("sessions", [])
    print(f"\nSession index: {len(sessions)} entries")

    # Unsaved plans
    existing_sources = {s.get("original_file") for s in sessions}
    unsaved = [pf for pf in plan_files if pf.name not in existing_sources]
    if unsaved:
        print(f"\n  ** {len(unsaved)} unsaved plan(s) detected:")
        for u in unsaved:
            print(f"     {u.name}")

    # Temp files
    temp_files = _find_temp_cwd_files()
    print(f"\nTemp tmpclaude-* files: {len(temp_files)}")
    if temp_files:
        print("  Run 'cleanup' to remove them.")

    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="session_manager",
        description="PRISM Session Manager - backup & manage Claude planning sessions.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # new
    p_new = subparsers.add_parser("new", help="Create a new planning session")
    p_new.add_argument("title", help="Title for the new session")

    # save
    p_save = subparsers.add_parser("save", help="Backup Claude plan files to planning/")
    p_save.add_argument(
        "--source",
        default=None,
        help=f"Source directory containing plan .md files (default: {CLAUDE_PLANS_DIR})",
    )

    # list
    p_list = subparsers.add_parser("list", help="List all tracked sessions")
    p_list.add_argument("-v", "--verbose", action="store_true", help="Show full session details")

    # load
    p_load = subparsers.add_parser("load", help="Load and display a session")
    p_load.add_argument("session_id", help="Session number, ID, or search term")

    # cleanup
    p_cleanup = subparsers.add_parser("cleanup", help="Remove tmpclaude-* temp files")
    p_cleanup.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")

    # status
    subparsers.add_parser("status", help="Show overall session status summary")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    commands = {
        "new": cmd_new,
        "save": cmd_save,
        "list": cmd_list,
        "load": cmd_load,
        "cleanup": cmd_cleanup,
        "status": cmd_status,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
