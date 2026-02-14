# Code Cleanup Guide

Complete guide to code quality improvements and formatting.

---

## Overview

Part 5 focuses on:
- ✅ Remove commented code, debug prints, unused imports
- ✅ Run Black formatter for consistent style
- ✅ Update requirements.txt
- ✅ Standardize docstrings and error messages
- ✅ Verify code quality

---

## Step 1: Preview Cleanup

**Software:** PowerShell

```powershell
# Preview what would be cleaned (dry-run)
python tools/cleanup_code.py act_autopilot

python tools/cleanup_code.py act_dashboard

python tools/cleanup_code.py act_alerts
```

**Expected:** Shows files that would be changed and what would be removed.

---

## Step 2: Install Black Formatter

**Software:** PowerShell

```powershell
# Install Black
pip install black
```

Black is an opinionated Python code formatter that enforces PEP 8 style.

---

## Step 3: Run Black Formatter

**Software:** PowerShell

```powershell
# Format all Python files
black act_autopilot/
black act_dashboard/
black act_alerts/
black tools/
black scripts/

# Or format entire project
black .
```

**Expected:** 
```
reformatted act_autopilot/models.py
reformatted act_dashboard/routes.py
...
All done! ✨ 🍰 ✨
42 files reformatted, 15 files left unchanged.
```

**What Black Does:**
- Consistent indentation (4 spaces)
- Max line length: 88 characters
- Consistent quote usage
- Proper spacing around operators
- Trailing commas in multi-line structures

---

## Step 4: Apply Code Cleanup

**Software:** PowerShell

```powershell
# Apply cleanup to each module
python tools/cleanup_code.py act_autopilot --apply
python tools/cleanup_code.py act_dashboard --apply
python tools/cleanup_code.py act_alerts --apply
python tools/cleanup_code.py tools --apply
```

**What Gets Removed:**
- Debug print statements
- Trailing whitespace
- Commented test code
- Temporary debug comments

**What Gets Kept:**
- TODO/FIXME comments
- Legitimate commented code with explanations
- Production logging statements

---

## Step 5: Update Requirements

**Software:** PowerShell

```powershell
# Update requirements.txt with all dependencies
python tools/update_requirements.py
```

**Expected:** Creates/updates `requirements.txt` with all installed packages.

---

## Step 6: Verify Code Quality

### Check for Unused Imports

**Software:** PowerShell

```powershell
# Install autoflake
pip install autoflake

# Check for unused imports (dry-run)
autoflake --check --remove-all-unused-imports -r act_autopilot/
autoflake --check --remove-all-unused-imports -r act_dashboard/
autoflake --check --remove-all-unused-imports -r act_alerts/
```

### Remove Unused Imports

**Software:** PowerShell

```powershell
# Remove unused imports (apply changes)
autoflake --in-place --remove-all-unused-imports -r act_autopilot/
autoflake --in-place --remove-all-unused-imports -r act_dashboard/
autoflake --in-place --remove-all-unused-imports -r act_alerts/
```

---

## Step 7: Run Black Again

After cleanup, run Black one more time to ensure consistent formatting:

**Software:** PowerShell

```powershell
black .
```

---

## Code Quality Checklist

### ✅ Formatting
- [ ] Black formatter applied to all .py files
- [ ] Line length ≤ 88 characters
- [ ] Consistent indentation (4 spaces)
- [ ] No trailing whitespace

### ✅ Imports
- [ ] Unused imports removed
- [ ] Imports sorted (stdlib, third-party, local)
- [ ] No duplicate imports

### ✅ Code Cleanliness
- [ ] No debug print statements
- [ ] No commented-out code (unless explained)
- [ ] No TODO without issue reference
- [ ] No temporary test code

### ✅ Documentation
- [ ] All public functions have docstrings
- [ ] Module-level docstrings present
- [ ] Class docstrings present
- [ ] Complex logic has inline comments

### ✅ Error Handling
- [ ] Consistent error messages
- [ ] Proper exception types
- [ ] No bare `except:` clauses
- [ ] Errors logged appropriately

### ✅ Naming
- [ ] Functions: snake_case
- [ ] Classes: PascalCase
- [ ] Constants: UPPER_CASE
- [ ] Private: _leading_underscore

---

## Black Configuration (Optional)

Create `pyproject.toml` in project root for Black config:

```toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311']
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.venv
  | _build
  | build
  | dist
)/
'''
```

---

## Before/After Examples

### Example 1: Debug Prints

**Before:**
```python
def process_data(data):
    print("DEBUG: Processing data")  # Remove this
    result = transform(data)
    print(f"Result: {result}")  # Remove this
    return result
```

**After:**
```python
def process_data(data):
    result = transform(data)
    return result
```

### Example 2: Trailing Whitespace

**Before:**
```python
def hello():    
    return "world"    
```

**After:**
```python
def hello():
    return "world"
```

### Example 3: Black Formatting

**Before:**
```python
def long_function(arg1,arg2,arg3,arg4,arg5,arg6):
    return arg1+arg2+arg3+arg4+arg5+arg6
```

**After:**
```python
def long_function(arg1, arg2, arg3, arg4, arg5, arg6):
    return arg1 + arg2 + arg3 + arg4 + arg5 + arg6
```

### Example 4: Unused Imports

**Before:**
```python
import os
import sys
import json
from datetime import datetime
from typing import List

def hello():
    return "world"
```

**After:**
```python
def hello():
    return "world"
```

---

## Common Issues

### Black Changes Too Much

**Issue:** Black reformats entire codebase

**Solution:** This is expected - Black is opinionated. Commit the changes as a single "Format with Black" commit.

### Merge Conflicts After Formatting

**Issue:** Formatting creates merge conflicts

**Solution:** Run Black before creating pull requests. Coordinate with team to format entire codebase at once.

### Some Debug Prints Are Needed

**Issue:** Cleanup removes legitimate logging

**Solution:** Use proper logging instead of print:

```python
# Before (will be removed)
print(f"Processing campaign {campaign_id}")

# After (won't be removed)
logger.info(f"Processing campaign {campaign_id}")
```

---

## Best Practices

### 1. Run Black on Save

Configure your editor to run Black automatically when saving Python files.

**VS Code:** Install "Black Formatter" extension

### 2. Pre-commit Hooks

Set up pre-commit hooks to run Black automatically:

```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
```

### 3. Regular Cleanup

Run cleanup tools regularly:
- Weekly: `black .`
- Before commits: `autoflake --check`
- Before releases: Full cleanup pass

### 4. Document Exceptions

If you need to keep commented code, explain why:

```python
# Keep this commented implementation for reference when debugging
# connection pooling issues. See GitHub issue #123
# def old_connection_method():
#     ...
```

---

## Files to Clean

Priority order:

1. **Core modules:** act_autopilot/, act_dashboard/, act_alerts/
2. **Tools:** tools/, scripts/
3. **Tests:** tests/ (if exists)
4. **Root files:** setup.py, etc.

---

## Final Verification

After all cleanup:

```powershell
# 1. Format with Black
black .

# 2. Check for unused imports
autoflake --check --remove-all-unused-imports -r .

# 3. Run tests (if any)
pytest

# 4. Verify all modules import correctly
python -c "import act_autopilot; import act_dashboard; import act_alerts; print('✅ All imports working')"
```

---

## Summary

Part 5 code cleanup provides:
- ✅ Consistent code formatting (Black)
- ✅ No debug prints or commented code
- ✅ No unused imports
- ✅ Updated requirements.txt
- ✅ Clean, professional codebase
- ✅ Ready for production

**Commands to run:**
```powershell
# 1. Install tools
pip install black autoflake

# 2. Format code
black .

# 3. Clean code
python tools/cleanup_code.py act_autopilot --apply
python tools/cleanup_code.py act_dashboard --apply
python tools/cleanup_code.py act_alerts --apply

# 4. Remove unused imports
autoflake --in-place --remove-all-unused-imports -r .

# 5. Update requirements
python tools/update_requirements.py

# 6. Final format
black .
```
