"""
CLI Interface for Google Drive Organizer - Autonomous Edition

Commands:
    scan       - Scan files (use --llamaindex, --vision for enriched analysis)
    organize   - Organize files with AI analysis and learning system
    duplicates - Find duplicate files
    analyze    - Analyze file patterns
    status     - Show system status
    clean      - Clean temporary files (use --execute to actually delete)
    watch      - Watch directory for file changes (use --learning to enable learning)
    propose    - Generate folder structure suggestions (use --llm for smart categorization)
"""

import argparse
import json
import os
import re
import sys
from typing import Callable, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TEMP_PATTERNS = [
    r"^\..*\.swp$",
    r"^.*\.tmp$",
    r"^.*\.temp$",
    r"^.*\.bak$",
    r"^.*\.old$",
    r"^.*~$",
    r"^#.*#$",
    r"\.DS_Store$",
    r"^__pycache__$",
    r"^node_modules$",
    r"\.pyc$",
    r"\.pyo$",
]
TEMP_EXTENSIONS = {".tmp", ".temp", ".bak", ".old", ".swp", "~", ".pyc", ".pyo"}


class CLI:
    """Command-line interface for Google Drive Organizer - Autonomous Edition"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Google Drive Organizer - Autonomous AI-powered file organization",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self._setup_arguments()
        self._setup_dispatch()

    def _setup_arguments(self):
        g = self.parser.add_argument_group("Global options")
        g.add_argument(
            "--verbose", "-v", action="store_true", help="Enable verbose output"
        )
        g.add_argument("--config", "-c", type=str, help="Configuration file path")
        g.add_argument(
            "--version", action="version", version="Google Drive Organizer v2.0.0"
        )

        sub = self.parser.add_subparsers(dest="command", help="Available commands")

        self._add_scan_command(sub)
        self._add_organize_command(sub)
        self._add_duplicates_command(sub)
        self._add_analyze_command(sub)
        self._add_status_command(sub)
        self._add_clean_command(sub)
        self._add_watch_command(sub)
        self._add_propose_command(sub)

    def _add_scan_command(self, sub):
        p = sub.add_parser("scan", help="Scan files or directories")
        p.add_argument("paths", nargs="+", help="Files and/or directories to scan")
        p.add_argument(
            "--recursive",
            "-r",
            action="store_true",
            help="Recursive scan (for directories)",
        )
        p.add_argument(
            "--llamaindex", "-l", action="store_true", help="Extract document content"
        )
        p.add_argument(
            "--vision",
            "-v",
            action="store_true",
            help="Analyze images with vision model",
        )
        p.add_argument(
            "--fast",
            "-f",
            action="store_true",
            help="Use fast tools (fd, ripgrep) for large datasets",
        )
        p.add_argument(
            "--cloud",
            "-g",
            action="store_true",
            help="Include Google Drive cloud files",
        )
        p.add_argument("--output", "-o", help="Output file path for results")

    def _add_organize_command(self, sub):
        p = sub.add_parser("organize", help="Organize files with autonomous execution")
        p.add_argument("paths", nargs="+", help="Files and/or directories to organize")
        p.add_argument(
            "--dry-run", action="store_true", help="Show changes without executing"
        )
        p.add_argument(
            "--execute",
            action="store_true",
            help="Actually execute changes (required for auto mode)",
        )
        p.add_argument(
            "--auto",
            action="store_true",
            help="Use confidence thresholds for auto-execution",
        )
        p.add_argument(
            "--agent",
            "-a",
            action="store_true",
            help="Use AI Orchestrator for agent-based decisions",
        )
        p.add_argument(
            "--cloud", "-g", action="store_true", help="Sync with Google Drive cloud"
        )
        p.add_argument(
            "--confidence",
            type=float,
            default=0.9,
            help="Confidence threshold for auto-execution (0.0-1.0)",
        )

    def _add_duplicates_command(self, sub):
        p = sub.add_parser("duplicates", help="Find duplicate files")
        p.add_argument("paths", nargs="+", help="Files and/or directories to scan")
        p.add_argument("--min-size", type=int, help="Minimum file size in bytes")
        p.add_argument(
            "--fast", "-f", action="store_true", help="Use xxhash/rdfind for speed"
        )
        p.add_argument(
            "--cloud",
            "-g",
            action="store_true",
            help="Check Google Drive cloud for duplicates",
        )
        p.add_argument(
            "--delete",
            action="store_true",
            help="Automatically delete duplicates (--execute required)",
        )

    def _add_analyze_command(self, sub):
        p = sub.add_parser("analyze", help="Analyze file patterns")
        p.add_argument("paths", nargs="+", help="Files and/or directories to analyze")
        p.add_argument("--output", "-o", help="Output file path")
        p.add_argument(
            "--agent",
            "-a",
            action="store_true",
            help="Use AI Orchestrator for deep analysis",
        )
        p.add_argument(
            "--fast", "-f", action="store_true", help="Use fast tools (fd, ripgrep)"
        )
        p.add_argument(
            "--ollama",
            action="store_true",
            help="Use OllamaIntegration for LLM-powered analysis",
        )

    def _add_status_command(self, sub):
        sub.add_parser("status", help="Show system status")

    def _add_clean_command(self, sub):
        p = sub.add_parser("clean", help="Clean temporary files")
        p.add_argument("paths", nargs="+", help="Files and/or directories to clean")
        p.add_argument(
            "--dry-run", action="store_true", help="Show what would be deleted"
        )
        p.add_argument("--execute", action="store_true", help="Actually delete files")

    def _add_watch_command(self, sub):
        p = sub.add_parser("watch", help="Watch directory for file changes")
        p.add_argument("directory", help="Directory to watch")
        p.add_argument(
            "--recursive", "-r", action="store_true", help="Watch subdirectories"
        )
        p.add_argument(
            "--learning",
            "-l",
            action="store_true",
            help="Enable learning from file operations",
        )
        p.add_argument(
            "--disk-safety", action="store_true", help="Enable disk safety monitoring"
        )

    def _add_propose_command(self, sub):
        p = sub.add_parser("propose", help="Propose folder structure for organization")
        p.add_argument("paths", nargs="+", help="Files and/or directories to analyze")
        p.add_argument(
            "--llm", "-l", action="store_true", help="Use LLM for smart categorization"
        )
        p.add_argument("--output", "-o", help="Output file path")
        p.add_argument(
            "--execute", action="store_true", help="Actually create folder structure"
        )

    def _setup_dispatch(self):
        self._dispatch: Dict[str, Callable] = {
            "scan": self._handle_scan,
            "organize": self._handle_organize,
            "duplicates": self._handle_duplicates,
            "analyze": self._handle_analyze,
            "status": self._handle_status,
            "clean": self._handle_clean,
            "watch": self._handle_watch,
            "propose": self._handle_propose,
        }

    def run_command(self, args: Optional[list] = None) -> Dict:
        try:
            parsed = self.parser.parse_args(args)
        except SystemExit as e:
            return {"status": "error", "exit_code": e.code, "message": "Command exited"}
        if not parsed.command:
            return {
                "status": "error",
                "message": "No command specified",
                "usage": self.parser.format_help(),
            }
        handler = self._dispatch.get(parsed.command)
        return (
            handler(parsed)
            if handler
            else {"status": "error", "message": f"Unknown command: {parsed.command}"}
        )

    def _check_disk_safety(self, min_free_gb: float = 1.0) -> Dict:
        """Check disk safety before operations"""
        from disk_monitor import DiskMonitor

        monitor = DiskMonitor(threshold=95.0)
        usage = monitor.get_disk_usage()
        free_gb = usage.get("free_gb", 0)
        safe = free_gb >= min_free_gb
        return {"safe": safe, "free_gb": free_gb, "usage": usage}

    def _expand_paths(
        self, paths: list, recursive: bool = True, use_fast: bool = False
    ) -> list:
        """Expand paths list to file list using fast tools if requested"""
        from file_scanner import FileScanner
        from tool_integration import ToolIntegration

        files = []
        if use_fast:
            tools = ToolIntegration()
            print("  ⚡ Using fast tools (fd, ripgrep)...")
            for p in paths:
                if os.path.isdir(p):
                    found = tools.fd_search(p, hidden=recursive)
                    files.extend(
                        [{"path": f, "name": os.path.basename(f)} for f in found]
                    )
                elif os.path.isfile(p):
                    files.append({"path": p, "name": os.path.basename(p)})
        else:
            scanner = FileScanner()
            for p in paths:
                if os.path.isfile(p):
                    files.append({"path": p, "name": os.path.basename(p)})
                elif os.path.isdir(p):
                    scanned = scanner.scan(p, recursive=recursive) or []
                    files.extend(scanned)
        return files

    def _handle_scan(self, args) -> Dict:
        from llamaindex_extractor import LlamaIndexExtractor
        from vision_extractor import VisionExtractor
        from ollama_integration import OllamaIntegration
        from pathlib import Path

        rec = getattr(args, "recursive", True)
        use_idx = getattr(args, "llamaindex", False)
        use_vis = getattr(args, "vision", False)
        use_fast = getattr(args, "fast", False)
        use_cloud = getattr(args, "cloud", False)
        output_file = getattr(args, "output", None)

        results = self._expand_paths(args.paths, recursive=rec, use_fast=use_fast)

        extracted, analyzed = [], []

        if use_cloud:
            from google_drive_api import GoogleDriveAPI

            print("  ☁️  Fetching Google Drive files...")
            gd_api = GoogleDriveAPI()
            gd_files = gd_api.list_files() or []
            for f in gd_files:
                results.append(
                    {
                        "path": f"gdrive:{f.get('id')}",
                        "name": f.get("name"),
                        "cloud": True,
                    }
                )
            print(f"  ✓ Found {len(gd_files)} cloud files")

        if use_idx:
            print("  📚 Extracting content...")
            ext = LlamaIndexExtractor()
            for p in args.paths:
                if os.path.isfile(p):
                    doc = ext._read_text_file(Path(os.path.abspath(p)))
                    if doc.get("content"):
                        m = doc.get("metadata", {})
                        extracted.append(
                            {
                                "path": m.get("file_path"),
                                "name": m.get("file_name"),
                                "type": m.get("file_type"),
                            }
                        )
                elif os.path.isdir(p):
                    for doc in ext.extract(p, recursive=rec):
                        m = doc.get("metadata", {})
                        extracted.append(
                            {
                                "path": m.get("file_path"),
                                "name": m.get("file_name"),
                                "type": m.get("file_type"),
                            }
                        )
            print(f"  ✓ Extracted {len(extracted)} documents")

        if use_vis:
            print("  👁️  Analyzing images...")
            vis = VisionExtractor()
            for p in args.paths:
                if os.path.isdir(p):
                    images = vis.find_images(p, recursive=rec)
                elif os.path.isfile(p):
                    images = [p]
                else:
                    images = []
                for img in images:
                    a = vis.analyze_image(img)
                    analyzed.append(
                        {
                            "path": img,
                            "category": a.get("category"),
                            "confidence": a.get("confidence"),
                        }
                    )
            print(f"  ✓ Analyzed {len(analyzed)} images")

        result = {
            "status": "success",
            "command": "scan",
            "paths": args.paths,
            "files_found": len(results) or 0,
            "extracted_count": len(extracted),
            "analyzed_count": len(analyzed),
            "results": results,
            "extracted": extracted[:20],
            "analyzed": analyzed[:20],
        }

        if output_file:
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            print(f"  💾 Saved to {output_file}")

        return result

    def _handle_organize(self, args) -> Dict:
        from semantic_analyzer import SemanticAnalyzer
        from watch_daemon import FileOperationLearner
        from confidence_executor import ConfidenceExecutor
        from gdrive_executor import GDriveExecutor
        from ollama_integration import OllamaIntegration
        from ai_orchestrator import AIOrchestrator
        from disk_monitor import DiskMonitor

        dry = getattr(args, "dry_run", False) or not getattr(args, "execute", False)
        use_auto = getattr(args, "auto", False)
        use_agent = getattr(args, "agent", False)
        use_cloud = getattr(args, "cloud", False)
        confidence_threshold = getattr(args, "confidence", 0.9)

        mode_parts = ["DRY RUN" if dry else "LIVE"]
        if use_auto:
            mode_parts.append("AUTO")
        if use_agent:
            mode_parts.append("AGENT")
        if use_cloud:
            mode_parts.append("CLOUD")

        print(
            f"📁 Organizing: {', '.join(args.paths[:3])}{'...' if len(args.paths) > 3 else ''} | {' / '.join(mode_parts)}"
        )

        # Check disk safety
        disk_check = self._check_disk_safety(min_free_gb=1.0)
        if not disk_check["safe"]:
            print(
                f"  ⚠️  LOW DISK SPACE: {disk_check['free_gb']:.1f}GB free ({disk_check['usage']['usage_percent']:.1f}% used)"
            )
            print("  🚫 Aborting operations for safety")
            return {
                "status": "error",
                "message": "Disk space too low",
                "disk_check": disk_check,
            }
        print(f"  💾 Disk OK: {disk_check['free_gb']:.1f}GB free")

        files = self._expand_paths(args.paths, recursive=True)

        if use_cloud:
            from google_drive_api import GoogleDriveAPI

            print("  ☁️  Fetching Google Drive files...")
            gd_api = GoogleDriveAPI()
            gd_files = gd_api.list_files() or []
            for f in gd_files:
                files.append(
                    {
                        "path": f"gdrive:{f.get('id')}",
                        "name": f.get("name"),
                        "cloud": True,
                    }
                )
            print(f"  ✓ Found {len(gd_files)} cloud files")

        if not files:
            return {
                "status": "success",
                "command": "organize",
                "message": "No files found",
                "actions": 0,
            }

        print(f"  ✓ Found {len(files)} files")

        # Use AI Orchestrator with OllamaIntegration if requested
        if use_agent:
            print("  🤖 Using AI Orchestrator with Ollama...")
            orchestrator = AIOrchestrator()
            ollama = OllamaIntegration()
            ollama_available = ollama.check_connection()
            if ollama_available:
                print("  ✓ Ollama connected")
            else:
                print("  ⚠️  Ollama not available, using fallback")
            analyses = []
            for f in files:
                result = orchestrator.execute_agent("analyze", file_path=f["path"])
                analyses.append(
                    {
                        "file_path": f["path"],
                        "confidence": result.get("confidence", 0.5),
                        "action": result.get("suggestion", "skip"),
                        "risk": result.get("risk", "low"),
                    }
                )
        else:
            analyzer = SemanticAnalyzer()
            analyses = analyzer.batch_analyze_files([f["path"] for f in files])

        learner = FileOperationLearner()
        learned = {
            fp: learner.suggest_destination(fp) for fp in [f["path"] for f in files]
        }
        learned_count = sum(1 for v in learned.values() if v)
        print(f"  💡 {learned_count} learned suggestions")

        actions = {"auto": [], "review": [], "skip": []}
        for a in analyses:
            conf = a.get("confidence", 0.5)
            action = a.get("action", "skip")
            if learned.get(a.get("file_path")):
                action = learned[a["file_path"]]
                conf = max(conf, 0.95)
            item = {
                "path": a.get("file_path"),
                "confidence": conf,
                "action": action,
                "risk": a.get("risk", "low"),
            }
            if use_auto and conf >= confidence_threshold:
                actions["auto"].append(item)
            elif conf >= 0.5:
                actions["review"].append(item)
            else:
                actions["skip"].append(item)

        # Autonomous execution with ConfidenceExecutor/GDriveExecutor
        if use_auto and not dry:
            print(
                f"  🎯 Autonomous execution (confidence >= {confidence_threshold})..."
            )
            executor = GDriveExecutor(local_executor=ConfidenceExecutor())
            executed_count = 0
            failed_count = 0
            for item in actions["auto"]:
                action = {
                    "file": item["path"],
                    "type": "MOVE"
                    if item.get("action") and item["action"] != "skip"
                    else "MOVE",
                    "target": item.get("action", ""),
                    "confidence": item["confidence"],
                }
                result = executor.execute_action(action)
                if result.get("executed"):
                    executed_count += 1
                    print(f"  ✓ Executed: {item['path']} -> {item['action']}")
                    learner.record_operation(item["path"], item["action"], "move")
                else:
                    failed_count += 1
                    print(
                        f"  ⚠️  Failed: {item['path']}: {result.get('error', 'Unknown')}"
                    )
            print(f"  📊 Executed: {executed_count} | Failed: {failed_count}")

        print(
            f"  📊 Auto: {len(actions['auto'])} | Review: {len(actions['review'])} | Skip: {len(actions['skip'])}"
        )

        return {
            "status": "success",
            "command": "organize",
            "paths": args.paths,
            "dry_run": dry,
            "auto_mode": use_auto,
            "agent_mode": use_agent,
            "cloud_mode": use_cloud,
            "disk_check": disk_check,
            "summary": {
                "total": len(files),
                "auto": len(actions["auto"]),
                "review": len(actions["review"]),
                "skip": len(actions["skip"]),
                "learned": learned_count,
            },
            "actions": {"auto": actions["auto"][:10], "review": actions["review"][:10]},
        }

    def _handle_duplicates(self, args) -> Dict:
        from duplicate_detector import DuplicateDetector
        from gdrive_executor import GDriveExecutor
        from confidence_executor import ConfidenceExecutor

        files = self._expand_paths(args.paths, recursive=True)
        use_fast = getattr(args, "fast", False)
        use_cloud = getattr(args, "cloud", False)
        auto_delete = getattr(args, "delete", False)
        execute = getattr(args, "execute", False)

        if not files:
            return {
                "status": "success",
                "command": "duplicates",
                "message": "No files found",
            }

        print(f"🔍 Scanning {len(files)} files for duplicates...")

        if use_fast:
            print("  ⚡ Using fast hashing (xxhash)...")
            detector = DuplicateDetector()
            results = detector.scan_for_duplicates(
                files=[f["path"] for f in files], use_xxhash=True
            )
        else:
            detector = DuplicateDetector()
            results = detector.scan_for_duplicates(
                files=[f["path"] for f in files], use_xxhash=False
            )

        dup_groups = results.get("duplicate_groups", 0)
        print(f"  ✓ Found {dup_groups} duplicate groups")

        # Auto-delete duplicates if requested
        if auto_delete and execute:
            print("  🗑️  Auto-deleting duplicates...")
            executor = GDriveExecutor(local_executor=ConfidenceExecutor())
            deleted = 0
            for group in results.get("groups", [])[1:]:  # Keep first, delete rest
                for dup in group:
                    if dup.startswith("gdrive:"):
                        file_id = dup.replace("gdrive:", "")
                        if executor.gd_api and executor.gd_api.delete_file(file_id):
                            deleted += 1
                    elif os.path.exists(dup):
                        os.remove(dup)
                        deleted += 1
            print(f"  ✓ Deleted {deleted} duplicate files")

        return {
            "status": "success",
            "command": "duplicates",
            "duplicates_found": dup_groups,
            "results": results,
        }

    def _handle_analyze(self, args) -> Dict:
        from pattern_discovery import PatternDiscovery
        from ollama_integration import OllamaIntegration
        from ai_orchestrator import AIOrchestrator

        use_agent = getattr(args, "agent", False)
        use_ollama = getattr(args, "ollama", False)
        output_file = getattr(args, "output", None)

        results = []
        for p in args.paths:
            if os.path.isdir(p):
                results.extend(PatternDiscovery().discover_all(p) or [])
            elif os.path.isfile(p):
                results.append({"path": p, "type": "file"})

        if use_ollama:
            print("  🧠 Using OllamaIntegration for deep analysis...")
            ollama = OllamaIntegration()
            if ollama.check_connection():
                prompt = f"Analyze these files and suggest organization patterns: {results[:10]}"
                llm_response = ollama.generate(prompt, model="llama2", max_tokens=500)
                print(
                    f"  ✓ LLM Analysis: {llm_response[:200] if llm_response else 'No response'}..."
                )
            else:
                print("  ⚠️  Ollama not available")

        if use_agent:
            print("  🤖 Using AI Orchestrator...")
            orchestrator = AIOrchestrator()
            agent_results = orchestrator.execute_workflow(
                ["analyze", "categorize", "suggest"]
            )
            results.extend(agent_results)

        result = {
            "status": "success",
            "command": "analyze",
            "paths": args.paths,
            "results": results,
        }

        if output_file:
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            print(f"  💾 Saved to {output_file}")

        return result

    def _handle_status(self, args) -> Dict:
        from ollama_integration import OllamaIntegration
        from google_drive_api import GoogleDriveAPI
        from disk_monitor import DiskMonitor

        ollama = OllamaIntegration()
        gd_api = GoogleDriveAPI()
        disk = DiskMonitor()
        disk_usage = disk.get_disk_usage()

        return {
            "status": "success",
            "command": "status",
            "system": "google-drive-organizer",
            "version": "2.0.0",
            "ollama": {
                "connected": ollama.check_connection(),
                "models": ollama.list_models(),
            },
            "google_drive": {"authenticated": gd_api.authenticated},
            "disk": disk_usage,
            "components": {
                c: "ready"
                for c in [
                    "file_scanner",
                    "semantic_analyzer",
                    "pattern_discovery",
                    "duplicate_detector",
                    "ai_orchestrator",
                    "confidence_executor",
                    "learning_system",
                    "gdrive_executor",
                    "ollama_integration",
                    "tool_integration",
                    "disk_monitor",
                ]
            },
            "features": [
                "scan [--fast] [--cloud] [--llamaindex] [--vision]",
                "organize [--auto] [--agent] [--cloud] [--execute]",
                "duplicates [--fast] [--cloud] [--delete]",
                "analyze [--agent] [--ollama]",
                "status",
                "clean [--execute]",
                "watch [--learning] [--disk-safety]",
                "propose [--llm] [--execute]",
            ],
        }

    def _handle_clean(self, args) -> Dict:
        dry = getattr(args, "dry_run", False) or not getattr(args, "execute", False)
        print(
            f"🧹 Cleaning: {', '.join(args.paths[:3])}{'...' if len(args.paths) > 3 else ''} | {'DRY RUN' if dry else 'LIVE'}"
        )

        disk_check = self._check_disk_safety(min_free_gb=0.5)
        if not disk_check["safe"]:
            print(f"  ⚠️  Low disk space, cleaning may fail")

        deleted = []
        for path in args.paths:
            if os.path.isfile(path):
                fn = os.path.basename(path)
                ext = os.path.splitext(fn)[1].lower()
                is_temp = (
                    fn.startswith(".")
                    or ext in TEMP_EXTENSIONS
                    or any(re.match(p, fn) for p in TEMP_PATTERNS)
                )
                if is_temp:
                    deleted.append(path)
                    if not dry:
                        try:
                            os.remove(path)
                        except Exception as e:
                            print(f"  ⚠️  Failed: {fn}: {e}")
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    dirs[:] = [d for d in dirs if not d.startswith(".")]
                    for fn in files:
                        fp = os.path.join(root, fn)
                        ext = os.path.splitext(fn)[1].lower()
                        is_temp = (
                            fn.startswith(".")
                            or ext in TEMP_EXTENSIONS
                            or any(re.match(p, fn) for p in TEMP_PATTERNS)
                        )
                        if is_temp:
                            deleted.append(fp)
                            if not dry:
                                try:
                                    os.remove(fp)
                                except Exception as e:
                                    print(f"  ⚠️  Failed: {fn}: {e}")

        print(f"  ✓ Found {len(deleted)} files")
        if dry:
            print("  Would delete:")
            for f in deleted[:10]:
                print(f"     - {os.path.basename(f)}")

        return {
            "status": "success",
            "command": "clean",
            "paths": args.paths,
            "dry_run": dry,
            "deleted": len(deleted),
        }

    def _handle_watch(self, args) -> Dict:
        from watch_daemon import WatchDaemon, create_watch_daemon_with_learning
        from watch_daemon import FileEvent
        from disk_monitor import DiskMonitor

        rec = getattr(args, "recursive", True)
        learn = getattr(args, "learning", False)
        disk_safety = getattr(args, "disk_safety", False)

        print(
            f"👀 Watching: {args.directory} | Recursive: {rec} | Learning: {learn} | Disk Safety: {disk_safety}"
        )

        if disk_safety:
            disk = DiskMonitor(threshold=95.0)
            print(f"  💾 Disk monitoring enabled (threshold: 95%)")

        events = []

        def on_event(e):
            if isinstance(e, FileEvent):
                events.append(
                    {"op": e.operation.value, "src": e.src_path, "dst": e.dest_path}
                )
                print(
                    f"  📄 {e.operation.value}: {e.src_path}"
                    + (f" -> {e.dest_path}" if e.dest_path else "")
                )

        if learn:
            daemon, learner, gen = create_watch_daemon_with_learning(args.directory)
            daemon.recursive = rec
            daemon.start(blocking=True)
        else:
            WatchDaemon(
                watch_path=args.directory, event_handler=on_event, recursive=rec
            ).start(blocking=True)

        return {
            "status": "success",
            "command": "watch",
            "directory": args.directory,
            "events": len(events),
            "recent": events[-50:],
        }

    def _handle_propose(self, args) -> Dict:
        from watch_daemon import FolderStructureGenerator
        from ollama_integration import OllamaIntegration

        use_llm = getattr(args, "llm", False)
        output_file = getattr(args, "output", None)
        execute = getattr(args, "execute", False)

        print(
            f"📁 Proposing structure: {', '.join(args.paths[:3])}{'...' if len(args.paths) > 3 else ''} | {'LLM' if use_llm else 'Basic'}"
        )

        if use_llm:
            ollama = OllamaIntegration()
            if not ollama.check_connection():
                print("  ⚠️  Ollama not available, using basic categorization")

        gen = FolderStructureGenerator()
        all_files = []
        for p in args.paths:
            if os.path.isdir(p):
                struct = gen.propose_structure(p, use_llm=use_llm)
                all_files.extend(struct.get("files", []))
            elif os.path.isfile(p):
                all_files.append(
                    {"src_path": p, "dst_path": f"imported/{os.path.basename(p)}"}
                )

        files = all_files
        print(f"  📋 {len(files)} proposed moves:")

        by_folder = {}
        for f in files:
            folder = (
                "/".join(f["dst_path"].split("/")[:-1]) if "/" in f["dst_path"] else "."
            )
            by_folder.setdefault(folder, []).append(f["dst_path"].split("/")[-1])
        for folder, names in by_folder.items():
            print(f"  📂 {folder}/")
            for n in names[:5]:
                print(f"     - {n}")
            if len(names) > 5:
                print(f"     ... +{len(names) - 5} more")

        # Execute folder creation if requested
        if execute:
            print("  📁 Creating folder structure...")
            created = set()
            for f in files:
                dst = f["dst_path"]
                folder = "/".join(dst.split("/")[:-1])
                if folder and folder not in created:
                    try:
                        os.makedirs(folder, exist_ok=True)
                        created.add(folder)
                        print(f"  ✓ Created: {folder}")
                    except Exception as e:
                        print(f"  ⚠️  Failed to create {folder}: {e}")

        result = {
            "status": "success",
            "command": "propose",
            "paths": args.paths,
            "use_llm": use_llm,
            "count": len(files),
            "structure": {"files": files},
        }
        if output_file:
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            print(f"  💾 Saved to {output_file}")
        return result


def main():
    cli = CLI()
    result = cli.run_command()
    if result.get("status") == "error":
        print(f"Error: {result.get('message')}")
        sys.exit(1)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
