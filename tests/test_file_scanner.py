# tests/test_file_scanner.py
"""
Test-driven development for Task 10: File Scanner (with progress tracking)
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.file_scanner import FileScanner


def test_scan_directory():
    """Verify scanning a directory"""
    scanner = FileScanner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        for i in range(5):
            file_path = os.path.join(tmpdir, f"file{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Content {i}")

        results = scanner.scan(tmpdir)

        assert len(results) == 5
        assert all("path" in r for r in results)


def test_recursive_scan():
    """Verify recursive scanning"""
    scanner = FileScanner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create nested directories
        subdir = os.path.join(tmpdir, "subdir")
        os.makedirs(subdir)

        # Create files in both directories
        open(os.path.join(tmpdir, "file1.txt"), "w").close()
        open(os.path.join(subdir, "file2.txt"), "w").close()

        results = scanner.scan(tmpdir, recursive=True)

        assert len(results) == 2


def test_file_filters():
    """Verify file filtering by extension"""
    scanner = FileScanner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files with different extensions
        open(os.path.join(tmpdir, "file.txt"), "w").close()
        open(os.path.join(tmpdir, "file.py"), "w").close()
        open(os.path.join(tmpdir, "file.md"), "w").close()

        # Filter only .txt files
        results = scanner.scan(tmpdir, extensions=["txt"])

        assert len(results) == 1
        assert results[0]["path"].endswith(".txt")


def test_size_filtering():
    """Verify filtering by file size"""
    scanner = FileScanner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files with different sizes
        small_file = os.path.join(tmpdir, "small.txt")
        large_file = os.path.join(tmpdir, "large.txt")

        with open(small_file, "w") as f:
            f.write("Small")

        with open(large_file, "w") as f:
            f.write("Large content" * 1000)

        # Filter only files > 1KB
        results = scanner.scan(tmpdir, min_size_kb=1)

        assert len(results) == 1
        assert "large.txt" in results[0]["path"]


def test_progress_tracking():
    """Verify progress tracking during scan"""
    scanner = FileScanner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files
        for i in range(10):
            file_path = os.path.join(tmpdir, f"file{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Content {i}")

        progress = []

        def progress_callback(current, total):
            progress.append((current, total))

        results = scanner.scan(tmpdir, progress_callback=progress_callback)

        # Should have received progress updates
        assert len(progress) > 0
        assert results[0]["total_files"] == 10


def test_get_file_metadata():
    """Verify extracting file metadata"""
    scanner = FileScanner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test content")
        temp_path = f.name

    try:
        metadata = scanner.get_metadata(temp_path)

        assert "size" in metadata
        assert "modified_time" in metadata
        assert "extension" in metadata
        assert metadata["size"] > 0
    finally:
        os.unlink(temp_path)


def test_calculate_checksum():
    """Verify calculating file checksums"""
    scanner = FileScanner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test content")
        temp_path = f.name

    try:
        checksum = scanner.calculate_checksum(temp_path)

        assert isinstance(checksum, str)
        assert len(checksum) > 0
    finally:
        os.unlink(temp_path)


def test_batch_scan():
    """Verify batch scanning multiple directories"""
    scanner = FileScanner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple directories
        dir1 = os.path.join(tmpdir, "dir1")
        dir2 = os.path.join(tmpdir, "dir2")

        os.makedirs(dir1)
        os.makedirs(dir2)

        # Create files
        open(os.path.join(dir1, "file1.txt"), "w").close()
        open(os.path.join(dir2, "file2.txt"), "w").close()

        results = scanner.batch_scan([dir1, dir2])

        assert len(results) == 2


def test_error_handling():
    """Verify error handling for invalid paths"""
    scanner = FileScanner()

    results = scanner.scan("/nonexistent/path/xyz")

    # Should handle gracefully
    assert results is None or len(results) == 0


def test_hidden_files():
    """Verify handling of hidden files"""
    scanner = FileScanner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create hidden file
        hidden_file = os.path.join(tmpdir, ".hidden")
        with open(hidden_file, "w") as f:
            f.write("Hidden")

        # Create regular file
        regular_file = os.path.join(tmpdir, "regular.txt")
        with open(regular_file, "w") as f:
            f.write("Regular")

        # Scan without hidden files
        results = scanner.scan(tmpdir, include_hidden=False)

        assert len(results) == 1
        assert "regular.txt" in results[0]["path"]
