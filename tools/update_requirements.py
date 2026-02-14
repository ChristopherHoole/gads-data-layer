"""
Update requirements.txt with all installed packages.
"""

import subprocess
import sys
from pathlib import Path


def get_installed_packages():
    """Get list of installed packages from pip."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True
    )
    return result.stdout.strip().split("\n")


def main():
    """Update requirements.txt."""
    print("=" * 80)
    print("UPDATE REQUIREMENTS.TXT")
    print("=" * 80)
    print()

    # Get installed packages
    packages = get_installed_packages()
    print(f"Found {len(packages)} installed packages")

    # Filter out local packages and common dev tools
    filtered = []
    skip_prefixes = ["gads-data-layer", "-e git", "pip==", "setuptools==", "wheel=="]

    for pkg in packages:
        if any(pkg.startswith(prefix) for prefix in skip_prefixes):
            continue
        filtered.append(pkg)

    print(f"Filtered to {len(filtered)} production packages")
    print()

    # Sort alphabetically
    filtered.sort()

    # Write to requirements.txt
    req_file = Path("requirements.txt")
    req_file.write_text("\n".join(filtered) + "\n")

    print(f"✅ Written to {req_file}")
    print()
    print("Key packages:")
    for pkg in filtered[:10]:
        print(f"  - {pkg}")

    if len(filtered) > 10:
        print(f"  ... and {len(filtered) - 10} more")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
