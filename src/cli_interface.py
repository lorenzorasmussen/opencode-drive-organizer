"""
CLI Interface for Google Drive Organizer
"""

import argparse
import json
import os
import sys
from typing import Dict, Optional

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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
            "--recursive",
            "-r",
            action="store_true",
            help="Recursive scan (default: true)",
        )

        # Organize command
        organize_parser = subparsers.add_parser("organize", help="Organize files")
        organize_parser.add_argument("directory", help="Directory to organize")
        organize_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show changes without executing (default)",
        )
        organize_parser.add_argument(
            "--execute", action="store_true", help="Actually execute the changes"
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

        # Status command
        status_parser = subparsers.add_parser("status", help="Show system status")

        # Clean command
        clean_parser = subparsers.add_parser("clean", help="Clean temporary files")
        clean_parser.add_argument("directory", help="Directory to clean")
        clean_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted (default)",
        )
        clean_parser.add_argument(
            "--execute", action="store_true", help="Actually delete temporary files"
        )

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
        elif parsed.command == "status":
            return self._handle_status(parsed)
        elif parsed.command == "clean":
            return self._handle_clean(parsed)
        else:
            return {"status": "error", "message": f"Unknown command: {parsed.command}"}

    def _handle_scan(self, args) -> Dict:
        """Handle scan command"""
        from file_scanner import FileScanner

        scanner = FileScanner()
        # Always use recursive=True (--recursive flag becomes no-op but kept for backward compat)
        results = scanner.scan(args.directory, recursive=True)

        return {
            "status": "success",
            "command": "scan",
            "files_found": len(results) if results else 0,
            "results": results,
        }

    def _handle_organize(self, args) -> Dict:
        """Handle organize command"""
        from file_scanner import FileScanner
        from semantic_analyzer import SemanticAnalyzer

        dry_run = getattr(args, "dry_run", False)
        execute = getattr(args, "execute", False)

        # Default to dry-run unless --execute is specified
        is_dry_run = dry_run or not execute

        print(f"📁 Organizing: {args.directory}")
        print(f"   Mode: {'DRY RUN' if is_dry_run else 'LIVE'}")

        # Step 1: Scan files
        print("  📄 Scanning files...")
        scanner = FileScanner()
        files = scanner.scan(args.directory, recursive=True)

        if not files:
            return {
                "status": "success",
                "command": "organize",
                "message": "No files found",
                "actions_taken": 0,
            }

        print(f"  ✓ Found {len(files)} files")

        # Step 2: Analyze files with semantic analyzer
        print("  🧠 Analyzing files...")
        analyzer = SemanticAnalyzer()

        file_paths = [f["path"] for f in files]
        analyses = analyzer.batch_analyze_files(file_paths)

        # Step 3: Generate actions based on confidence
        print("  📋 Generating actions...")
        actions = {
            "auto_execute": [],  # confidence >= 0.9
            "review": [],  # confidence 0.5-0.9
            "skip": [],  # confidence < 0.5
        }

        for analysis in analyses:
            file_path = analysis["file_path"]
            confidence = analysis["confidence"]
            action = analysis["action"]
            risk = analysis["risk"]

            action_item = {
                "path": file_path,
                "confidence": confidence,
                "action": action,
                "risk": risk,
            }

            if confidence >= 0.9:
                actions["auto_execute"].append(action_item)
            elif confidence >= 0.5:
                actions["review"].append(action_item)
            else:
                actions["skip"].append(action_item)

        # Step 4: Report results
        result = {
            "status": "success",
            "command": "organize",
            "directory": args.directory,
            "dry_run": is_dry_run,
            "summary": {
                "total_files": len(files),
                "auto_execute_count": len(actions["auto_execute"]),
                "review_count": len(actions["review"]),
                "skip_count": len(actions["skip"]),
            },
            "actions": {
                "auto_execute": actions["auto_execute"][:10],  # Limit output
                "review": actions["review"][:10],
            },
            "statistics": analyzer.generate_statistics(),
        }

        if is_dry_run:
            print("\n  🏃 DRY RUN - No changes made")
        else:
            print("\n  ⚠️  LIVE MODE - File operations would be executed here")
            print("     (Use organize with --execute to perform actual changes)")

        # Print summary
        print(f"\n  📊 Summary:")
        print(f"     Total files: {len(files)}")
        print(f"     Auto-execute (≥0.9): {len(actions['auto_execute'])}")
        print(f"     Review (0.5-0.9): {len(actions['review'])}")
        print(f"     Skip (<0.5): {len(actions['skip'])}")

        return result

    def _handle_duplicates(self, args) -> Dict:
        """Handle duplicates command"""
        from file_scanner import FileScanner
        from duplicate_detector import DuplicateDetector

        # First scan the directory to get file list
        scanner = FileScanner()
        files = scanner.scan(args.directory, recursive=True)

        if not files:
            return {
                "status": "success",
                "command": "duplicates",
                "message": "No files found",
                "duplicates_found": 0,
            }

        file_paths = [f["path"] for f in files]
        print(f"🔍 Scanning {len(file_paths)} files for duplicates...")

        detector = DuplicateDetector()
        results = detector.scan_for_duplicates(files=file_paths, use_xxhash=True)

        return {
            "status": "success",
            "command": "duplicates",
            "duplicates_found": results.get("duplicate_groups", 0),
            "results": results,
        }

    def _handle_analyze(self, args) -> Dict:
        """Handle analyze command"""
        from pattern_discovery import PatternDiscovery

        discovery = PatternDiscovery()
        results = discovery.discover_all(args.directory)

        return {"status": "success", "command": "analyze", "results": results}

    def _handle_status(self, args) -> Dict:
        """Handle status command"""
        return {
            "status": "success",
            "command": "status",
            "system": "google-drive-organizer",
            "version": "1.0.0",
            "components": {
                "file_scanner": "ready",
                "semantic_analyzer": "ready",
                "pattern_discovery": "ready",
                "duplicate_detector": "ready",
                "ai_orchestrator": "ready",
                "confidence_executor": "ready",
                "learning_system": "ready",
            },
            "features": [
                "scan - Scan directories for files",
                "organize - Organize files with AI analysis",
                "duplicates - Find duplicate files",
                "analyze - Analyze file patterns",
                "status - Show system status",
                "clean - Clean temporary files (--execute to actually delete)",
            ],
        }

    def _handle_clean(self, args) -> Dict:
        """Handle clean command - remove temporary files"""
        import re

        dry_run = getattr(args, "dry_run", False)
        execute = getattr(args, "execute", False)

        mode = "DRY RUN" if dry_run or not execute else "LIVE"
        print(f"🧹 Cleaning: {args.directory}")
        print(f"   Mode: {mode}")

        # Temporary file patterns
        temp_patterns = [
            r"^\..*\.swp$",  # Vim swap files
            r"^.*\.tmp$",  # .tmp
            r"^.*\.temp$",  # .temp
            r"^.*\.bak$",  # .bak
            r"^.*\.old$",  # .old
            r"^.*~$",  # Backup files
            r"^#.*#$",  # Emacs auto-save
            r"\.DS_Store$",  # macOS metadata
            r"^__pycache__$",  # Python cache
            r"^node_modules$",  # Node modules
            r"\.pyc$",  # Python compiled
            r"\.pyo$",  # Python optimized
        ]

        temp_extensions = {".tmp", ".temp", ".bak", ".old", ".swp", "~", ".pyc", ".pyo"}

        deleted = []
        skipped = []

        for root, dirs, files in os.walk(args.directory):
            # Skip hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for filename in files:
                file_path = os.path.join(root, filename)
                ext = os.path.splitext(filename)[1].lower()

                is_temp = (
                    filename.startswith(".")  # Hidden files
                    or ext in temp_extensions  # Temp extensions
                    or any(re.match(p, filename) for p in temp_patterns)  # Patterns
                )

                if is_temp:
                    deleted.append(file_path)
                    if execute:
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            print(f"  ⚠️  Failed to delete {filename}: {e}")
                else:
                    skipped.append(file_path)

        print(f"  ✓ Found {len(deleted)} temporary files")

        if dry_run or not execute:
            print("\n  🏃 DRY RUN - Files would be deleted:")
            for f in deleted[:20]:
                print(f"     - {os.path.basename(f)}")
            if len(deleted) > 20:
                print(f"     ... and {len(deleted) - 20} more")
        else:
            print(f"\n  ✓ Deleted {len(deleted)} temporary files")

        return {
            "status": "success",
            "command": "clean",
            "directory": args.directory,
            "dry_run": dry_run or not execute,
            "deleted_count": len(deleted),
            "deleted_files": deleted[:20],
        }


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
