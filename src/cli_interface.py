"""
CLI Interface for Google Drive Organizer

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
    """Command-line interface for Google Drive Organizer"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Google Drive Organizer - Autonomous file organization system",
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
            "--version", action="version", version="Google Drive Organizer v1.0.0"
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
            "--fast", "-f", action="store_true", help="Use fast tools (fd, ripgrep)"
        )
        p.add_argument(
            "--cloud",
            "-g",
            action="store_true",
            help="Include Google Drive cloud files",
        )

    def _add_organize_command(self, sub):
        p = sub.add_parser("organize", help="Organize files")
        p.add_argument("paths", nargs="+", help="Files and/or directories to organize")
        p.add_argument(
            "--dry-run", action="store_true", help="Show changes without executing"
        )
        p.add_argument(
            "--execute", action="store_true", help="Actually execute changes"
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

    def _add_duplicates_command(self, sub):
        p = sub.add_parser("duplicates", help="Find duplicate files")
        p.add_argument("paths", nargs="+", help="Files and/or directories to scan")
        p.add_argument("--min-size", type=int, help="Minimum file size in bytes")
        p.add_argument(
            "--fast", "-f", action="store_true", help="Use fast tools (xxhash, rdfind)"
        )
        p.add_argument(
            "--cloud",
            "-g",
            action="store_true",
            help="Check Google Drive cloud for duplicates",
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
            help="Enable learning from operations",
        )
        p.add_argument(
            "--blocking", "-b", action="store_true", help="Block until Ctrl+C"
        )

    def _add_propose_command(self, sub):
        p = sub.add_parser("propose", help="Propose folder structure for organization")
        p.add_argument("paths", nargs="+", help="Files and/or directories to analyze")
        p.add_argument(
            "--llm", "-l", action="store_true", help="Use LLM for smart categorization"
        )
        p.add_argument("--output", "-o", help="Output file path")

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

    def _expand_paths(self, paths: list, recursive: bool = True) -> list:
        """Expand paths list to file list (files as-is, directories scanned)"""
        from file_scanner import FileScanner

        scanner = FileScanner()
        files = []
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
        from tool_integration import ToolIntegration
        from ollama_integration import OllamaIntegration
        from pathlib import Path

        rec = getattr(args, "recursive", True)
        use_idx = getattr(args, "llamaindex", False)
        use_vis = getattr(args, "vision", False)
        use_fast = getattr(args, "fast", False)
        use_cloud = getattr(args, "cloud", False)

        results = []

        if use_fast:
            tools = ToolIntegration()
            print("  ⚡ Using fast tools (fd, ripgrep)...")
            for p in args.paths:
                if os.path.isdir(p):
                    found = tools.fd_search(p, hidden=rec)
                    results.extend(
                        [{"path": f, "name": os.path.basename(f)} for f in found]
                    )
                elif os.path.isfile(p):
                    results.append({"path": p, "name": os.path.basename(p)})
        else:
            results = self._expand_paths(args.paths, recursive=rec)

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

        extracted, analyzed = [], []

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
                elif os.path.isfile(p) and vis.find_images(os.path.dirname(p) or "."):
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

        return {
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

    def _handle_organize(self, args) -> Dict:
        from semantic_analyzer import SemanticAnalyzer
        from watch_daemon import FileOperationLearner
        from confidence_executor import ConfidenceExecutor
        from ai_orchestrator import AIOrchestrator

        dry = getattr(args, "dry_run", False) or not getattr(args, "execute", False)
        use_auto = getattr(args, "auto", False)
        use_agent = getattr(args, "agent", False)
        use_cloud = getattr(args, "cloud", False)

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

        files = self._expand_paths(args.paths, recursive=True)

        # Include Google Drive cloud files if requested
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

        # Use AI Orchestrator if requested
        if use_agent:
            print("  🤖 Using AI Orchestrator for decisions...")
            orchestrator = AIOrchestrator()
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
            if use_auto and conf >= 0.9:
                actions["auto"].append(item)
            elif conf >= 0.5:
                actions["review"].append(item)
            else:
                actions["skip"].append(item)

        # Auto-execute if requested
        if use_auto and not dry:
            executor = ConfidenceExecutor()
            for item in actions["auto"]:
                result = executor.execute_action(item)
                print(f"  ✓ Executed: {item['path']} -> {item['action']}")

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

        files = self._expand_paths(args.paths, recursive=True)
        if not files:
            return {
                "status": "success",
                "command": "duplicates",
                "message": "No files found",
            }

        print(f"🔍 Scanning {len(files)} files...")
        detector = DuplicateDetector()
        results = detector.scan_for_duplicates(
            files=[f["path"] for f in files], use_xxhash=True
        )

        return {
            "status": "success",
            "command": "duplicates",
            "duplicates_found": results.get("duplicate_groups", 0),
            "results": results,
        }

    def _handle_analyze(self, args) -> Dict:
        from pattern_discovery import PatternDiscovery

        results = []
        for p in args.paths:
            if os.path.isdir(p):
                results.extend(PatternDiscovery().discover_all(p) or [])
            elif os.path.isfile(p):
                results.append({"path": p, "type": "file"})

        return {
            "status": "success",
            "command": "analyze",
            "paths": args.paths,
            "results": results,
        }

    def _handle_status(self, args) -> Dict:
        return {
            "status": "success",
            "command": "status",
            "system": "google-drive-organizer",
            "version": "1.0.0",
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
                ]
            },
            "features": [
                "scan [--llamaindex] [--vision]",
                "organize",
                "duplicates",
                "analyze",
                "status",
                "clean [--execute]",
                "watch [--learning]",
                "propose [--llm]",
            ],
        }

    def _handle_clean(self, args) -> Dict:
        dry = getattr(args, "dry_run", False) or not getattr(args, "execute", False)
        print(
            f"🧹 Cleaning: {', '.join(args.paths[:3])}{'...' if len(args.paths) > 3 else ''} | {'DRY RUN' if dry else 'LIVE'}"
        )

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

        rec = getattr(args, "recursive", True)
        learn = getattr(args, "learning", False)
        block = getattr(args, "blocking", True)

        print(
            f"👀 Watching: {args.directory} | Recursive: {rec} | Learning: {learn} | Ctrl+C to stop"
        )

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
            daemon.start(blocking=block)
        else:
            WatchDaemon(
                watch_path=args.directory, event_handler=on_event, recursive=rec
            ).start(blocking=block)

        return {
            "status": "success",
            "command": "watch",
            "directory": args.directory,
            "events": len(events),
            "recent": events[-50:],
        }

    def _handle_propose(self, args) -> Dict:
        from watch_daemon import FolderStructureGenerator

        use_llm = getattr(args, "llm", False)
        out = getattr(args, "output", None)

        print(
            f"📁 Proposing structure: {', '.join(args.paths[:3])}{'...' if len(args.paths) > 3 else ''} | {'LLM' if use_llm else 'Basic'}"
        )

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

        result = {
            "status": "success",
            "command": "propose",
            "paths": args.paths,
            "use_llm": use_llm,
            "count": len(files),
            "structure": {"files": files},
        }
        if out:
            with open(out, "w") as f:
                json.dump(result, f, indent=2)
            print(f"  💾 Saved to {out}")
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
