"""Wrapper to start dashboard with UTF-8 stdout encoding on Windows."""
import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from act_dashboard.app import main
main()
