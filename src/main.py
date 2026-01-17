"""
Main entry point for Google Drive Organizer
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli_interface import CLI


def main():
    """Main entry point"""
    cli = CLI()
    result = cli.run_command(sys.argv[1:])

    if result.get("status") == "error":
        print(f"Error: {result.get('message', 'Unknown error')}")
        sys.exit(1)
    else:
        # Print JSON output
        import json

        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
