"""
Non-interactive seed script runner
Run: python scripts/run_seed.py
"""
import builtins
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Force non-interactive confirmation
def _always_yes(_prompt: str = "") -> str:
    return "yes"

def main():
    original_input = builtins.input
    try:
        builtins.input = _always_yes
        # Import seed_data from parent directory
        import seed_data
        seed_data.main()
    finally:
        builtins.input = original_input


if __name__ == "__main__":
    main()
