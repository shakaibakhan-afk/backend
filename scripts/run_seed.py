import builtins

# Force non-interactive confirmation
def _always_yes(_prompt: str = "") -> str:
    return "yes"

def main():
    original_input = builtins.input
    try:
        builtins.input = _always_yes
        # Import here so SQLAlchemy/env loads after input swap
        from .. import seed_data
        seed_data.main()
    finally:
        builtins.input = original_input


if __name__ == "__main__":
    main()


