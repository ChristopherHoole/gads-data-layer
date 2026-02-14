"""
Code cleanup utility.
Removes commented code, unused imports, and debug statements.
"""

import re
import sys
from pathlib import Path
from typing import List, Set


def find_python_files(directory: str) -> List[Path]:
    """Find all Python files in directory."""
    path = Path(directory)
    return list(path.rglob("*.py"))


def remove_debug_prints(content: str) -> tuple[str, int]:
    """
    Remove debug print statements.

    Returns:
        (cleaned_content, num_removed)
    """
    lines = content.split("\n")
    cleaned = []
    removed = 0

    for line in lines:
        stripped = line.strip()

        # Skip debug prints
        if stripped.startswith("print(") and any(
            debug in stripped.lower()
            for debug in ["debug", "test", "temp", "###", "TODO"]
        ):
            removed += 1
            continue

        # Skip commented debug lines
        if stripped.startswith("#") and any(
            debug in stripped.lower()
            for debug in ["debug", "test", "temp", "todo", "fixme"]
        ):
            if "TODO" in stripped or "FIXME" in stripped:
                # Keep TODO/FIXME comments
                cleaned.append(line)
            else:
                removed += 1
            continue

        cleaned.append(line)

    return "\n".join(cleaned), removed


def remove_trailing_whitespace(content: str) -> tuple[str, int]:
    """
    Remove trailing whitespace from lines.

    Returns:
        (cleaned_content, num_lines_cleaned)
    """
    lines = content.split("\n")
    cleaned = []
    count = 0

    for line in lines:
        stripped = line.rstrip()
        if len(stripped) != len(line):
            count += 1
        cleaned.append(stripped)

    return "\n".join(cleaned), count


def standardize_docstrings(content: str) -> str:
    """
    Ensure all functions have docstrings.
    (Just reports missing, doesn't auto-add)
    """
    lines = content.split("\n")

    in_function = False
    func_name = None
    has_docstring = False
    missing = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect function definition
        if stripped.startswith("def "):
            in_function = True
            func_name = stripped.split("(")[0].replace("def ", "")
            has_docstring = False

        # Check for docstring
        elif in_function and (stripped.startswith('"""') or stripped.startswith("'''")):
            has_docstring = True
            in_function = False

        # If we hit code without docstring
        elif in_function and stripped and not stripped.startswith("#"):
            if not has_docstring and not func_name.startswith("_"):
                missing.append((i + 1, func_name))
            in_function = False

    if missing:
        print(f"\n  Missing docstrings:")
        for line_no, name in missing[:5]:  # Show first 5
            print(f"    Line {line_no}: {name}()")

    return content


def cleanup_file(filepath: Path, dry_run: bool = True) -> dict:
    """
    Clean up a single Python file.

    Returns:
        Stats dict
    """
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content

        # Apply cleanups
        content, debug_removed = remove_debug_prints(content)
        content, whitespace_cleaned = remove_trailing_whitespace(content)
        content = standardize_docstrings(content)

        stats = {
            "file": str(filepath),
            "debug_prints_removed": debug_removed,
            "trailing_whitespace_cleaned": whitespace_cleaned,
            "changed": content != original,
        }

        # Write back if changed and not dry-run
        if not dry_run and stats["changed"]:
            filepath.write_text(content, encoding="utf-8")

        return stats

    except Exception as e:
        return {"file": str(filepath), "error": str(e)}


def main():
    """Main cleanup script."""
    import argparse

    parser = argparse.ArgumentParser(description="Code cleanup utility")
    parser.add_argument("directory", help="Directory to clean")
    parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default: dry-run)"
    )
    args = parser.parse_args()

    print("=" * 80)
    print("CODE CLEANUP")
    print("=" * 80)
    print(f"Mode: {'APPLY CHANGES' if args.apply else 'DRY-RUN (preview only)'}")
    print()

    # Find all Python files
    files = find_python_files(args.directory)
    print(f"Found {len(files)} Python files")
    print()

    # Clean each file
    total_debug = 0
    total_whitespace = 0
    files_changed = 0

    for filepath in files:
        # Skip __pycache__ and .venv
        if "__pycache__" in str(filepath) or ".venv" in str(filepath):
            continue

        stats = cleanup_file(filepath, dry_run=not args.apply)

        if "error" in stats:
            print(f"❌ ERROR: {stats['file']}")
            print(f"   {stats['error']}")
            continue

        if (
            stats["changed"]
            or stats["debug_prints_removed"] > 0
            or stats["trailing_whitespace_cleaned"] > 0
        ):
            print(f"{'✅' if args.apply else '📝'} {filepath.name}")
            if stats["debug_prints_removed"] > 0:
                print(f"   - Removed {stats['debug_prints_removed']} debug prints")
            if stats["trailing_whitespace_cleaned"] > 0:
                print(
                    f"   - Cleaned {stats['trailing_whitespace_cleaned']} lines (trailing whitespace)"
                )

            total_debug += stats["debug_prints_removed"]
            total_whitespace += stats["trailing_whitespace_cleaned"]
            if stats["changed"]:
                files_changed += 1

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files changed: {files_changed}")
    print(f"Debug prints removed: {total_debug}")
    print(f"Lines cleaned (whitespace): {total_whitespace}")

    if not args.apply:
        print()
        print("⚠️  DRY-RUN MODE: No files were modified")
        print("   Run with --apply to make changes")
    else:
        print()
        print("✅ Changes applied")

    print("=" * 80)


if __name__ == "__main__":
    main()
