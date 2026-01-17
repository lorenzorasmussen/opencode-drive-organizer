"""
Parallel File Scanner - Multi-threaded file operations

Features:
- Parallel file scanning with ThreadPoolExecutor
- Progress tracking
- Batch processing
- Thread-safe operations
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict, List, Optional, Any
from pathlib import Path


class ParallelScanner:
    """Multi-threaded file scanner with progress tracking"""

    def __init__(self, max_workers: int = 4):
        """
        Initialize parallel scanner

        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
        }

    def scan_files(
        self,
        paths: List[str],
        recursive: bool = True,
        callback: Optional[Callable] = None,
        show_progress: bool = True,
    ) -> List[Dict]:
        """
        Scan files in parallel

        Args:
            paths: List of directories to scan
            recursive: Scan subdirectories
            callback: Optional callback for each file
            show_progress: Show progress bar

        Returns:
            List of file dictionaries
        """
        from tqdm import tqdm

        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "errors": 0,
            "start_time": time.time(),
        }

        # Collect all files first
        all_files = []
        for path in paths:
            if os.path.isfile(path):
                all_files.append({"path": path, "name": os.path.basename(path)})
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    dirs[:] = dirs[:] if recursive else []
                    for f in files:
                        fp = os.path.join(root, f)
                        all_files.append({"path": fp, "name": f})

        self.stats["total_files"] = len(all_files)

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._process_file, f, callback): f for f in all_files
            }

            for future in tqdm(
                as_completed(futures),
                total=len(all_files),
                disable=not show_progress,
                desc="Scanning",
            ):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    self.stats["processed_files"] += 1
                except Exception as e:
                    self.stats["errors"] += 1

        self.stats["end_time"] = time.time()
        return results

    def _process_file(
        self, file_info: Dict, callback: Optional[Callable] = None
    ) -> Optional[Dict]:
        """Process a single file"""
        try:
            path = file_info["path"]
            result = {
                "path": path,
                "name": file_info["name"],
                "size": os.path.getsize(path) if os.path.exists(path) else 0,
                "mtime": os.path.getmtime(path) if os.path.exists(path) else 0,
            }
            if callback:
                return callback(result)
            return result
        except Exception:
            return None

    def batch_analyze(
        self,
        files: List[str],
        analyzer_func: Callable,
        show_progress: bool = True,
    ) -> List[Dict]:
        """
        Analyze files in parallel

        Args:
            files: List of file paths
            analyzer_func: Function to analyze each file
            show_progress: Show progress bar

        Returns:
            List of analysis results
        """
        from tqdm import tqdm

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(analyzer_func, f): f for f in files}

            for future in tqdm(
                as_completed(futures),
                total=len(files),
                disable=not show_progress,
                desc="Analyzing",
            ):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"⚠️  Analysis error: {e}")

        return results

    def get_stats(self) -> Dict:
        """Get scan statistics"""
        elapsed = (
            self.stats["end_time"] - self.stats["start_time"]
            if self.stats.get("end_time") and self.stats.get("start_time")
            else 0
        )
        return {
            **self.stats,
            "elapsed_seconds": round(elapsed, 2),
            "files_per_second": round(self.stats["processed_files"] / elapsed, 2)
            if elapsed > 0
            else 0,
        }


def parallel_scan(
    paths: List[str],
    recursive: bool = True,
    max_workers: int = 4,
    show_progress: bool = True,
) -> List[Dict]:
    """Quick parallel file scan"""
    scanner = ParallelScanner(max_workers=max_workers)
    return scanner.scan_files(paths, recursive, show_progress=show_progress)
