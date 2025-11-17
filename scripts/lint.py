#!/usr/bin/env python3
"""
Lint script for backend using Black.
Run: python scripts/lint.py
"""
import subprocess
import sys
import os

def main():
    """Run Black linter on backend code."""
    # Get the backend directory (parent of scripts)
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(backend_dir)
    
    # Files/directories to lint
    paths = [
        "app",
        "alembic",
        "scripts",
        "seed_data.py"
    ]
    
    # Run Black in check mode (dry run)
    print("🔍 Running Black linter (check mode)...")
    print("=" * 60)
    
    cmd = ["black", "--check", "--diff"] + paths
    
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print("\n✅ All files are properly formatted!")
            return 0
        else:
            print("\n❌ Some files need formatting. Run 'black' to auto-fix.")
            print("\nTo auto-fix, run: black " + " ".join(paths))
            return 1
    except FileNotFoundError:
        print("❌ Error: Black not found. Install it with: pip install black")
        return 1

if __name__ == "__main__":
    sys.exit(main())

