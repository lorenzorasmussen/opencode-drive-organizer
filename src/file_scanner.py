"""
File Scanner with Progress Tracking
"""

import os
import hashlib
from typing import Dict, List, Optional, Callable
from datetime import datetime


class FileScanner:
    """
    File scanner with progress tracking

    Features:
    - Scan directories recursively
    - File filtering by extension, size
    - Progress tracking with callbacks
    - Extract file metadata
    - Calculate file checksums
    - Batch scanning multiple directories
    - Handle hidden files
    - Error handling
    """

    def __init__(self):
        """Initialize file scanner"""
        self.total_files_scanned = 0
        self.total_bytes_scanned = 0

    def scan(
        self,
        directory: str,
        recursive: bool = True,
        extensions: Optional[List[str]] = None,
        min_size_kb: Optional[int] = None,
        max_size_kb: Optional[int] = None,
        include_hidden: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Optional[List[Dict]]:
        """
        Scan a directory

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively
            extensions: Filter by file extensions
            min_size_kb: Minimum file size in KB
            max_size_kb: Maximum file size in KB
            include_hidden: Whether to include hidden files
            progress_callback: Function(current, total) for progress updates

        Returns:
            List of file dicts or None if error
        """
        if not os.path.isdir(directory):
            print(f"⚠️  Directory not found: {directory}")
            return None

        results = []
        file_count = 0

        # Count files first for progress tracking
        if progress_callback:
            for _ in os.walk(directory):
                pass  # Just count
            total_files = sum(1 for _ in os.walk(directory))
            progress_callback(0, total_files)

        # Walk directory
        for dirpath, dirnames, filenames in os.walk(directory):
            if not recursive and dirpath != directory:
                continue

            # Filter out hidden directories
            if not include_hidden:
                dirnames[:] = [d for d in dirnames if not d.startswith(".")]

            for filename in filenames:
                # Skip hidden files
                if not include_hidden and filename.startswith("."):
                    continue

                file_path = os.path.join(dirpath, filename)

                # Get file info
                try:
                    size = os.path.getsize(file_path)
                    _, ext = os.path.splitext(filename)
                    ext_lower = ext.lower()
                    ext_without_dot = ext_lower.lstrip(".")

                    # Filter by extension (handle both .txt and txt formats)
                    if extensions:
                        # Normalize extensions - ensure they have dots
                        normalized_exts = [
                            e if e.startswith(".") else f".{e}" for e in extensions
                        ]
                        if (
                            ext_lower not in normalized_exts
                            and ext_without_dot not in extensions
                        ):
                            continue

                    # Filter by size
                    size_kb = size / 1024
                    if min_size_kb is not None and size_kb < min_size_kb:
                        continue
                    if max_size_kb is not None and size_kb > max_size_kb:
                        continue

                    # Create result dict
                    result = {
                        "path": file_path,
                        "name": filename,
                        "directory": dirpath,
                        "extension": ext_lower,
                        "size": size,
                        "size_kb": round(size_kb, 2),
                        "modified_time": datetime.fromtimestamp(
                            os.path.getmtime(file_path)
                        ).isoformat(),
                    }

                    results.append(result)
                    file_count += 1
                    self.total_files_scanned += 1
                    self.total_bytes_scanned += size

                    # Update progress
                    if progress_callback and file_count % 10 == 0:
                        progress_callback(file_count, total_files)

                except OSError as e:
                    print(f"⚠️  Error reading {file_path}: {e}")
                    continue

        # Final progress update
        if progress_callback:
            progress_callback(file_count, file_count)

        # Add total_files to each result
        for result in results:
            result["total_files"] = file_count

        return results

    def batch_scan(self, directories: List[str], **kwargs) -> List[Dict]:
        """
        Scan multiple directories

        Args:
            directories: List of directories to scan
            **kwargs: Additional arguments for scan()

        Returns:
            Combined list of file dicts
        """
        all_results = []

        for directory in directories:
            results = self.scan(directory, **kwargs)
            if results:
                all_results.extend(results)

        return all_results

    def get_metadata(self, file_path: str) -> Optional[Dict]:
        """
        Extract file metadata

        Args:
            file_path: Path to file

        Returns:
            Metadata dict or None if error
        """
        try:
            stat = os.stat(file_path)

            _, ext = os.path.splitext(file_path)

            return {
                "path": file_path,
                "name": os.path.basename(file_path),
                "extension": ext.lower(),
                "size": stat.st_size,
                "size_kb": round(stat.st_size / 1024, 2),
                "size_mb": round(stat.st_size / (1024**2), 2),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_file": os.path.isfile(file_path),
                "is_dir": os.path.isdir(file_path),
            }
        except Exception as e:
            print(f"⚠️  Error getting metadata: {e}")
            return None

    def calculate_checksum(
        self, file_path: str, algorithm: str = "md5"
    ) -> Optional[str]:
        """
        Calculate file checksum

        Args:
            file_path: Path to file
            algorithm: Hash algorithm (md5, sha1, sha256)

        Returns:
            Checksum string or None if error
        """
        try:
            hash_func = {
                "md5": hashlib.md5,
                "sha1": hashlib.sha1,
                "sha256": hashlib.sha256,
            }.get(algorithm.lower(), hashlib.md5)

            with open(file_path, "rb") as f:
                checksum = hash_func(f.read()).hexdigest()

            return checksum

        except Exception as e:
            print(f"⚠️  Error calculating checksum: {e}")
            return None

    def get_scan_statistics(self) -> Dict:
        """Get statistics from scanning operations"""
        return {
            "total_files_scanned": self.total_files_scanned,
            "total_bytes_scanned": self.total_bytes_scanned,
            "total_mb_scanned": round(self.total_bytes_scanned / (1024**2), 2),
            "total_gb_scanned": round(self.total_bytes_scanned / (1024**3), 2),
        }

    def reset_statistics(self):
        """Reset scanning statistics"""
        self.total_files_scanned = 0
        self.total_bytes_scanned = 0

    def find_duplicates(
        self, directory: str, check_content: bool = False
    ) -> Dict[str, List[str]]:
        """
        Find duplicate files by name or content

        Args:
            directory: Directory to scan
            check_content: Whether to check file content (slower)

        Returns:
            Dict mapping checksum to list of file paths
        """
        files = self.scan(directory) or []

        duplicates = {}

        if check_content:
            # Group by checksum
            checksums = {}
            for file_info in files:
                checksum = self.calculate_checksum(file_info["path"])
                if checksum:
                    if checksum not in checksums:
                        checksums[checksum] = []
                    checksums[checksum].append(file_info["path"])

            # Find duplicates (groups with >1 file)
            duplicates = {k: v for k, v in checksums.items() if len(v) > 1}
        else:
            # Group by name and size
            file_groups = {}
            for file_info in files:
                key = f"{file_info['name']}:{file_info['size']}"
                if key not in file_groups:
                    file_groups[key] = []
                file_groups[key].append(file_info["path"])

            # Find duplicates
            duplicates = {k: v for k, v in file_groups.items() if len(v) > 1}

        return duplicates

    def find_empty_directories(self, root_directory: str) -> List[str]:
        """
        Find empty directories

        Args:
            root_directory: Root directory to scan

        Returns:
            List of empty directory paths
        """
        empty_dirs = []

        for dirpath, dirnames, filenames in os.walk(root_directory):
            if not dirnames and not filenames and dirpath != root_directory:
                empty_dirs.append(dirpath)

        return empty_dirs
