#!/usr/bin/env python3
"""Script to fix imports after restructuring."""

import os
from pathlib import Path

# Mapping of old imports to new imports
IMPORT_FIXES = {
    "from constants import": "from config.constants import",
    "from config import settings": "from config.settings import settings",
    "from api.models.requests import": "from models.requests import",
    "from api.models.responses import": "from models.responses import",
}

def fix_imports_in_file(file_path: Path) -> bool:
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        for old_import, new_import in IMPORT_FIXES.items():
            content = content.replace(old_import, new_import)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed imports in: {file_path}")
            return True

        return False

    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix imports in all Python files."""
    src_dir = Path(__file__).parent / "src"

    python_files = list(src_dir.rglob("*.py"))

    print(f"Found {len(python_files)} Python files\n")

    fixed_count = 0
    for py_file in python_files:
        if fix_imports_in_file(py_file):
            fixed_count += 1

    print(f"\n✓ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
