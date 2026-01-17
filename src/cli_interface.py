"""
CLI Interface for Google Drive Organizer
"""

import argparse
import json
import os
import sys
from typing import Dict, Optional


class CLI:
    """
    Command-line interface for Google Drive Organizer

    Features:
    - Command parsing with argparse
    - Multiple commands: scan, organize, duplicates, analyze
    - Help and version options
    - Verbose output
    - Configuration file support
    - Command validation
    """

    def __init__(self):
        """Initialize CLI"""
        self.parser = argparse.ArgumentParser(
            description="Google Drive Organizer - Autonomous file organization system",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self._setup_arguments()

    def _setup_arguments(self):
        """Setup command-line arguments"""
        # Global options
        self.parser.add_argument(
            "--verbose", "-v", action="store_true", help="Enable verbose output"
        )
        self.parser.add_argument(
            "--config", "-c", type=str, help="Configuration file path"
        )
        self.parser.add_argument(
            "--version", action="version", version="Google Drive Organizer v1.0.0"
        )

        # Subcommands
        subparsers = self.parser.add_subparsers(
            dest="command", help="Available commands"
        )

        # Scan command
        scan_parser = subparsers.add_parser("scan", help="Scan files")
        scan_parser.add_argument("directory", help="Directory to scan")
        scan_parser.add_argument(
            "--recursive", "-r", action="store_true", help="Recursive scan"
        )

        # Organize command
        organize_parser = subparsers.add_parser("organize", help="Organize files")
        organize_parser.add_argument("directory", help="Directory to organize")
        organize_parser.add_argument(
            "--dry-run", action="store_true", help="Show changes without executing"
        )

        # Duplicates command
        dup_parser = subparsers.add_parser("duplicates", help="Find duplicates")
        dup_parser.add_argument("directory", help="Directory to scan")
        dup_parser.add_argument(
            "--min-size", type=int, help="Minimum file size in bytes"
        )

        # Analyze command
        analyze_parser = subparsers.add_parser("analyze", help="Analyze files")
        analyze_parser.add_argument("directory", help="Directory to analyze")
        analyze_parser.add_argument("--output", "-o", help="Output file path")

    def run_command(self, args: Optional[list] = None) -> Dict:
        """
        Run CLI command

        Args:
            args: Command-line arguments (uses sys.argv if None)

        Returns:
            Result dict
        """
        parsed = self.parser.parse_args(args)

        if not parsed.command:
            return {
                "status": "error",
                "message": "No command specified",
                "usage": self.parser.format_help(),
            }

        # Execute command
        if parsed.command == "scan":
            return self._handle_scan(parsed)
        elif parsed.command == "organize":
            return self._handle_organize(parsed)
        elif parsed.command == "duplicates":
            return self._handle_duplicates(parsed)
        elif parsed.command == "analyze":
            return self._handle_analyze(parsed)
        else:
            return {"status": "error", "message": f"Unknown command: {parsed.command}"}

    def _handle_scan(self, args) -> Dict:
        """Handle scan command"""
        from src.file_scanner import FileScanner

        scanner = FileScanner()
        results = scanner.scan(
            args.directory, recursive=getattr(args, "recursive", False)
        )

        return {
            "status": "success",
            "command": "scan",
            "files_found": len(results) if results else 0,
            "results": results,
        }

    def _handle_organize(self, args) -> Dict:
        """Handle organize command"""
        return {
            "status": "success",
            "command": "organize",
            "directory": args.directory,
            "dry_run": getattr(args, "dry_run", False),
        }

    def _handle_duplicates(self, args) -> Dict:
        """Handle duplicates command"""
        from src.duplicate_detector import DuplicateDetector

        detector = DuplicateDetector()
        results = detector.scan_for_duplicates(files=[args.directory], use_xxhash=True)

        return {
            "status": "success",
            "command": "duplicates",
            "duplicates_found": results["duplicate_groups"],
            "results": results,
        }

    def _handle_analyze(self, args) -> Dict:
        """Handle analyze command"""
        from src.pattern_discovery import PatternDiscovery

        discovery = PatternDiscovery()
        results = discovery.discover_all(args.directory)

        return {"status": "success", "command": "analyze", "results": results}


def main():
    """Main entry point for CLI"""
    cli = CLI()
    result = cli.run_command()

    if result.get("status") == "error":
        print(f"Error: {result.get('message', 'Unknown error')}")
        sys.exit(1)
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
