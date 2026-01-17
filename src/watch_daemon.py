"""
Watch Mode Daemon, LLM Folder Structure Generation, and Learning System

Features:
1. Watch daemon - monitors filesystem for changes in real-time
2. Folder structure generator - uses LLM to propose optimal organization
3. Learning system - learns from user file operations and improves over time

Based on LlamaFS methodology with watchdog integration and behavioral learning.
"""

import os
import re
import json
import time
import queue
import threading
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Pattern
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class FileOperation(Enum):
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    MOVE = "move"
    RENAME = "rename"


@dataclass
class FileEvent:
    """Represents a filesystem event"""

    operation: FileOperation
    src_path: str
    dest_path: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    is_directory: bool = False


class WatchDaemon:
    """
    Filesystem watch daemon using watchdog library

    Features:
    - Real-time monitoring of file changes
    - Detects: create, modify, delete, move, rename
    - Configurable patterns (include/exclude)
    - Event queue for async processing
    - Non-blocking mode with callbacks
    """

    def __init__(
        self,
        watch_path: str,
        event_handler: Optional[Callable[[FileEvent], None]] = None,
        patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        ignore_directories: bool = True,
        recursive: bool = True,
    ):
        """
        Initialize watch daemon

        Args:
            watch_path: Directory to monitor
            event_handler: Callback for file events
            patterns: File patterns to watch (e.g., ['*.txt', '*.pdf'])
            ignore_patterns: Patterns to ignore
            ignore_directories: Ignore directory events
            recursive: Watch subdirectories
        """
        self.watch_path = watch_path
        self.event_handler = event_handler
        self.patterns = patterns
        self.ignore_patterns = ignore_patterns
        self.ignore_directories = ignore_directories
        self.recursive = recursive

        self._running = False
        self._observer = None
        self._event_queue = queue.Queue()
        self._processing_thread = None

    def start(self, blocking: bool = True) -> None:
        """
        Start watching

        Args:
            blocking: Block thread or run in background
        """
        if self._running:
            return

        self._running = True

        # Start event processing thread
        self._processing_thread = threading.Thread(
            target=self._process_events, daemon=True
        )
        self._processing_thread.start()

        # Try to use watchdog if available
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class Handler(FileSystemEventHandler):
                def __init__(self, daemon):
                    self.daemon = daemon

                def on_created(self, event):
                    if not event.is_directory:
                        self.daemon._on_event(FileOperation.CREATE, event.src_path)

                def on_modified(self, event):
                    if not event.is_directory:
                        self.daemon._on_event(FileOperation.MODIFY, event.src_path)

                def on_deleted(self, event):
                    if not event.is_directory:
                        self.daemon._on_event(FileOperation.DELETE, event.src_path)

                def on_moved(self, event):
                    if not event.is_directory:
                        self.daemon._on_event(
                            FileOperation.MOVE, event.src_path, event.dest_path
                        )

            self._observer = Observer()
            self._observer.schedule(
                Handler(self), self.watch_path, recursive=self.recursive
            )
            self._observer.start()

            if blocking:
                self._observer.join()

        except ImportError:
            # Fallback: Simple polling-based monitoring
            self._start_observer()

            if blocking:
                try:
                    while self._running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.stop()

    def _start_observer(self) -> None:
        """Start polling-based observer (fallback)"""
        self._running = self._running or True

        def poll():
            known_files = set()

            while self._running:
                try:
                    for root, dirs, files in os.walk(self.watch_path):
                        if not self.recursive and root != self.watch_path:
                            continue

                        for filename in files:
                            if self._should_include(filename):
                                filepath = os.path.join(root, filename)
                                if filepath not in known_files:
                                    known_files.add(filepath)
                                    self._on_event(FileOperation.CREATE, filepath)
                except Exception:
                    pass

                time.sleep(5)  # Poll every 5 seconds

        thread = threading.Thread(target=poll, daemon=True)
        thread.start()

    def stop(self) -> None:
        """Stop watching"""
        self._running = False

        if self._observer:
            self._observer.stop()
            self._observer.join()

    def is_running(self) -> bool:
        """Check if daemon is running"""
        return self._running

    def _on_event(
        self, operation: FileOperation, src_path: str, dest_path: Optional[str] = None
    ) -> None:
        """Handle file event"""
        event = FileEvent(operation=operation, src_path=src_path, dest_path=dest_path)

        # Add to queue
        self._event_queue.put(event)

        # Call handler
        if self.event_handler:
            try:
                self.event_handler(event)
            except Exception:
                pass

    def _process_events(self) -> None:
        """Process events from queue"""
        while self._running:
            try:
                event = self._event_queue.get(timeout=1)

                if self.event_handler:
                    self.event_handler(event)

            except queue.Empty:
                continue
            except Exception:
                pass

    def _should_include(self, filename: str) -> bool:
        """Check if file should be included"""
        if self.ignore_patterns:
            for pattern in self.ignore_patterns:
                if re.match(pattern, filename):
                    return False

        if self.patterns:
            for pattern in self.patterns:
                if re.match(pattern, filename):
                    return True
            return False

        return True


class FolderStructureGenerator:
    """
    LLM-powered folder structure generator

    Features:
    - Analyzes files and proposes optimal organization
    - Uses LLM for semantic categorization
    - Respects existing naming conventions
    - Generates destination paths with new folder names
    """

    DEFAULT_PROMPT = """
You will be provided with a list of files and their content summaries.
Propose an optimal folder structure for organizing these files.

Guidelines:
1. Use known conventions (work/, personal/, projects/, etc.)
2. Group related files together
3. Use semantic folder names
4. Include dates where appropriate (YYYY-MM/)
5. Keep file names descriptive

Response must be JSON with schema:
{
  "files": [
    {
      "src_path": "original path",
      "dst_path": "proposed new path under folder structure"
    }
  ]
}
"""

    def __init__(
        self, ollama_url: str = "http://localhost:11434", model: str = "llama3.2"
    ):
        """
        Initialize folder structure generator

        Args:
            ollama_url: Ollama server URL
            model: LLM model for analysis
        """
        self.ollama_url = ollama_url
        self.model = model

    def propose_structure(
        self,
        directory: str,
        file_summaries: Optional[List[Dict]] = None,
        use_llm: bool = False,
    ) -> Dict[str, Any]:
        """
        Propose folder structure for files in directory

        Args:
            directory: Path to analyze
            file_summaries: Optional pre-computed file summaries
            use_llm: Use LLM for smart categorization

        Returns:
            Dict with file -> proposed path mappings
        """
        if file_summaries is None:
            file_summaries = self._get_file_summaries(directory)

        if not file_summaries:
            return {"files": []}

        if use_llm:
            return self._query_llm(file_summaries)

        # Basic categorization without LLM
        return self._basic_categorization(file_summaries)

    def _get_file_summaries(self, directory: str) -> List[Dict]:
        """Get basic file summaries"""
        summaries = []

        for root, dirs, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                stat = os.stat(filepath)

                summaries.append(
                    {
                        "src_path": filepath,
                        "file_name": filename,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    }
                )

        return summaries

    def _basic_categorization(self, files: List[Dict]) -> Dict[str, Any]:
        """Basic file categorization without LLM"""
        categories = {
            "work": [],
            "personal": [],
            "projects": [],
            "archives": [],
            "uncategorized": [],
        }

        category_keywords = {
            "work": ["report", "invoice", "presentation", "meeting", "work", "office"],
            "personal": ["photo", "vacation", "family", "personal", "medical"],
            "projects": ["project", "code", "development", "github"],
            "archives": ["old", "archive", "backup", "2023", "2022"],
        }

        for f in files:
            filename = f["file_name"].lower()
            categorized = False

            for cat, keywords in category_keywords.items():
                if any(kw in filename for kw in keywords):
                    categories[cat].append(f)
                    categorized = True
                    break

            if not categorized:
                categories["uncategorized"].append(f)

        # Generate destination paths
        result_files = []
        timestamp = datetime.now().strftime("%Y-%m")

        for cat, cat_files in categories.items():
            if cat == "uncategorized" and not cat_files:
                continue

            for f in cat_files:
                src_path = f["src_path"]
                filename = f["file_name"]

                # Generate new path
                if cat == "uncategorized":
                    dst_path = f"{timestamp}/{filename}"
                else:
                    dst_path = f"{cat}/{timestamp}/{filename}"

                result_files.append({"src_path": src_path, "dst_path": dst_path})

        return {"files": result_files}

    def _query_llm(self, files: List[Dict]) -> Dict[str, Any]:
        """Query LLM for smart categorization"""
        try:
            import requests

            # Prepare file list for LLM
            file_list = "\n".join(
                [
                    f"- {f['src_path']}: {f.get('summary', f['file_name'])}"
                    for f in files[:20]  # Limit to avoid token limits
                ]
            )

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": self.DEFAULT_PROMPT + "\n\nFiles:\n" + file_list,
                    "stream": False,
                    "format": "json",
                },
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                return json.loads(result.get("response", '{"files": []}'))

        except Exception:
            pass

        # Fallback to basic
        return self._basic_categorization(files)


class FileOperationLearner:
    """
    Learning system that records and learns from user file operations

    Features:
    - Records user file operations (move, copy, delete)
    - Extracts patterns from operations
    - Suggests destinations for new files based on learned patterns
    - Improves from user feedback
    """

    def __init__(self, data_file: str = "data/learning-data.json"):
        """
        Initialize learning system

        Args:
            data_file: Path to store learned patterns
        """
        self.data_file = data_file
        self._ensure_data_file()

        self.patterns = self._load_patterns()
        self.feedback_history = []

    def _ensure_data_file(self) -> None:
        """Ensure data file exists"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w") as f:
                json.dump({"patterns": [], "feedback": []}, f)

    def _load_patterns(self) -> List[Dict]:
        """Load patterns from file"""
        try:
            with open(self.data_file, "r") as f:
                data = json.load(f)
                return data.get("patterns", [])
        except Exception:
            return []

    def _save_patterns(self) -> None:
        """Save patterns to file"""
        try:
            with open(self.data_file, "w") as f:
                json.dump(
                    {"patterns": self.patterns, "feedback": self.feedback_history},
                    f,
                    indent=2,
                )
        except Exception:
            pass

    def record_operation(self, src: str, dst: Optional[str], operation: str) -> None:
        """
        Record a file operation

        Args:
            src: Source path
            dst: Destination path (None for delete)
            operation: Operation type (move, copy, delete)
        """
        # Check for GDrive path
        is_gdrive_src = src.startswith("gdrive:")
        is_gdrive_dst = dst and dst.startswith("gdrive:")

        if is_gdrive_src or is_gdrive_dst:
            self._record_gdrive_pattern(src, dst, operation)
            return

        # Local path handling (existing logic)
        src_path = Path(src)
        dst_path = Path(dst) if dst else None

        pattern = {
            "src_pattern": str(src_path.parent),
            "src_filename": src_path.name,
            "dst_pattern": str(dst_path.parent) if dst_path else None,
            "dst_filename": dst_path.name if dst_path else None,
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "count": 1,
        }

        for existing in self.patterns:
            if (
                existing["src_pattern"] == pattern["src_pattern"]
                and existing["dst_pattern"] == pattern["dst_pattern"]
            ):
                existing["count"] += 1
                existing["timestamp"] = pattern["timestamp"]
                self._save_patterns()
                return

        self.patterns.append(pattern)
        self._save_patterns()

    def _record_gdrive_pattern(
        self, src: str, dst: Optional[str], operation: str
    ) -> None:
        """Record a GDrive file operation"""
        is_gdrive = src.startswith("gdrive:")
        src_id = src.replace("gdrive:", "") if is_gdrive else None
        src_name = Path(src).name if not is_gdrive else "unknown"

        pattern = {
            "src_pattern": "gdrive:",
            "src_filename": src_name,
            "dst_pattern": Path(dst).name
            if dst and not dst.startswith("gdrive:")
            else dst,
            "dst_folder_id": dst.replace("gdrive:", "")
            if dst and dst.startswith("gdrive:")
            else None,
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "count": 1,
            "is_gdrive": True,
        }

        for existing in self.patterns:
            if existing.get("is_gdrive") and existing.get("dst_pattern") == pattern.get(
                "dst_pattern"
            ):
                existing["count"] += 1
                existing["timestamp"] = pattern["timestamp"]
                self._save_patterns()
                return

        self.patterns.append(pattern)
        self._save_patterns()

    def get_patterns(self) -> List[Dict]:
        """Get all learned patterns"""
        return self.patterns

    def suggest_destination(self, file_path: str) -> Optional[str]:
        """
        Suggest destination for a file based on learned patterns

        Args:
            file_path: Path to file

        Returns:
            Suggested destination path or None
        """
        # Check for GDrive path
        if file_path.startswith("gdrive:"):
            return self._suggest_gdrive_destination(file_path)

        # Local path handling (existing logic)
        file_p = Path(file_path)
        filename = file_p.name
        src_dir = str(file_p.parent)

        matches = []
        for p in self.patterns:
            if p.get("is_gdrive"):
                continue
            if p["operation"] == "move" and p["dst_pattern"]:
                if src_dir == p["src_pattern"] or src_dir.startswith(p["src_pattern"]):
                    if self._match_pattern(filename, p["src_filename"]):
                        matches.append(p)

        if not matches:
            return None

        matches.sort(key=lambda x: x["count"], reverse=True)
        best = matches[0]

        if "*" in best["dst_pattern"]:
            dst = best["dst_pattern"].replace("*", file_p.stem)
        else:
            dst = os.path.join(best["dst_pattern"], filename)

        return dst

    def _suggest_gdrive_destination(self, file_path: str) -> Optional[str]:
        """Suggest destination for GDrive file"""
        filename = Path(file_path).name

        # Find GDrive patterns
        matches = []
        for p in self.patterns:
            if p.get("is_gdrive") and p.get("dst_folder_id"):
                matches.append(p)

        if not matches:
            return None

        matches.sort(key=lambda x: x["count"], reverse=True)
        best = matches[0]

        # Return the learned destination folder
        return best.get("dst_pattern", "")

    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches pattern"""
        if pattern == "*" or pattern == filename:
            return True

        # Convert glob to regex
        regex = pattern.replace(".", "\\.").replace("*", ".*")
        return bool(re.match(f"^{regex}$", filename))

    def record_feedback(
        self, src_pattern: str, suggested: str, actual: str, accepted: bool
    ) -> None:
        """
        Record user feedback on suggestion

        Args:
            src_pattern: Source pattern
            suggested: Suggested destination
            actual: Actual destination chosen by user
            accepted: Whether suggestion was accepted
        """
        feedback = {
            "src_pattern": src_pattern,
            "suggested": suggested,
            "actual": actual,
            "accepted": accepted,
            "timestamp": datetime.now().isoformat(),
        }

        self.feedback_history.append(feedback)

        if not accepted:
            # Adjust pattern based on feedback
            for p in self.patterns:
                if p["src_pattern"] == src_pattern:
                    p["dst_pattern"] = os.path.dirname(actual)
                    p["count"] = max(0, p["count"] - 1)

        self._save_patterns()

    def get_recent_feedback(self) -> List[Dict]:
        """Get recent feedback entries"""
        return self.feedback_history[-10:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        return {
            "total_patterns": len(self.patterns),
            "total_feedback": len(self.feedback_history),
            "accepted_suggestions": sum(
                1 for f in self.feedback_history if f["accepted"]
            ),
            "top_patterns": sorted(
                self.patterns, key=lambda x: x["count"], reverse=True
            )[:5],
        }


def create_watch_daemon_with_learning(
    watch_path: str, on_new_file: Optional[Callable[[str], None]] = None
) -> tuple:
    """
    Create a watch daemon that learns from user file operations

    Returns:
        Tuple of (daemon, learner, generator)
    """
    learner = FileOperationLearner()
    generator = FolderStructureGenerator()

    def handle_event(event: FileEvent):
        if event.operation == FileOperation.CREATE:
            # Suggest destination for new file
            suggestion = learner.suggest_destination(event.src_path)
            if suggestion and on_new_file:
                on_new_file(f"New file: {event.src_path} -> suggested: {suggestion}")

        elif event.operation == FileOperation.MOVE:
            # Learn from user move operation
            if event.dest_path:
                learner.record_operation(event.src_path, event.dest_path, "move")

    daemon = WatchDaemon(watch_path=watch_path, event_handler=handle_event)

    return daemon, learner, generator


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python watch_daemon.py <directory> [--learn]")
        sys.exit(1)

    daemon, learner, generator = create_watch_daemon_with_learning(sys.argv[1])

    if "--learn" in sys.argv:
        print(f"Starting watch daemon on {sys.argv[1]} with learning enabled...")
        print("Press Ctrl+C to stop")
        daemon.start(blocking=True)
    else:
        # Just propose structure
        structure = generator.propose_structure(sys.argv[1])
        print(json.dumps(structure, indent=2))

        print("\nLearned patterns:")
        for p in learner.get_patterns()[:5]:
            print(f"  {p['src_pattern']} -> {p['dst_pattern']} ({p['count']} times)")
