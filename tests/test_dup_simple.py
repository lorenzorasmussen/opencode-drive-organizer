# tests/test_duplicate_detector.py
"""
Test-driven development for Task 2: Fast Duplicate Detection with xxHash/Blake3
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.duplicate_detector import DuplicateDetector


def test_xxhash_speed():
    """Verify xxHash is fast for initial scan"""
    detector = DuplicateDetector()

    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "test-files")
        os.makedirs(test_dir)

        # Create test files
        for i in range(10):
            content = "Test content " + str(i) + "\n" * 100
            file_path = os.path.join(test_dir, "file_" + str(i) + ".txt")

            with open(file_path, "w") as f:
                f.write(content)

        # Scan with xxHash
        results = detector.scan_for_duplicates(files=[test_dir], use_xxhash=True)

        assert "duplicates" in results
        assert "scan_time" in results
        assert results["scan_time"] < 10  # Should be fast


def test_blake3_verification():
    """Verify Blake3 or SHA256 is used for verification"""
    detector = DuplicateDetector()

    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "test-files")
        os.makedirs(test_dir)

        # Create duplicate files
        content = "Duplicate content\n" * 100
        file1 = os.path.join(test_dir, "dup_1.txt")
        file2 = os.path.join(test_dir, "dup_2.txt")

        with open(file1, "w") as f:
            f.write(content)
        with open(file2, "w") as f:
            f.write(content)

        # Verify with Blake3
        results = detector.verify_files(files=[file1, file2], use_blake3=True)

        assert "verified_duplicates" in results
        assert results["algorithm"] in ["blake3", "sha256"]


def test_tiered_scanning():
    """Verify two-tier hashing: xxHash (fast) -> Blake3 (verification)"""
    detector = DuplicateDetector()

    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "test-files")
        os.makedirs(test_dir)

        # Create duplicate files
        content = "Duplicate content\n" * 100
        file1 = os.path.join(test_dir, "dup_1.txt")
        file2 = os.path.join(test_dir, "dup_2.txt")

        with open(file1, "w") as f:
            f.write(content)
        with open(file2, "w") as f:
            f.write(content)

        # Two-tier scanning
        file_list = [file1, file2]
        initial_scan = detector.tiered_scan(files=file_list)

        assert initial_scan["algorithm"] == "xxhash"
        assert "potential_duplicates" in initial_scan


def test_size_threshold():
    """Verify size threshold filters out small files"""
    detector = DuplicateDetector()

    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "test-files")
        os.makedirs(test_dir)

        # Large files (> 1000 bytes)
        large_file = os.path.join(test_dir, "large.txt")
        with open(large_file, "w") as f:
            f.write("Large content\n" * 2000)

        # Small file (< 1000 bytes)
        small_file = os.path.join(test_dir, "small.txt")
        with open(small_file, "w") as f:
            f.write("Small")

        # Scan with threshold (pass actual file paths)
        results = detector.scan_for_duplicates(
            files=[large_file, small_file], use_xxhash=True, threshold=1000
        )

        # Small file should be skipped
        assert results["files_scanned"] == 1  # Only large file counted


def test_duplicate_grouping():
    """Verify duplicates are grouped correctly"""
    detector = DuplicateDetector()

    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "test-files")
        os.makedirs(test_dir)

        # Create duplicate files and collect paths
        all_files = []
        for i in range(3):
            # Unique content for each group
            content = f"Duplicate content {i}\n" * 100
            file1 = os.path.join(test_dir, "dup_" + str(i) + "_1.txt")
            file2 = os.path.join(test_dir, "dup_" + str(i) + "_2.txt")

            with open(file1, "w") as f:
                f.write(content)
            with open(file2, "w") as f:
                f.write(content)

            all_files.extend([file1, file2])

        # Scan (pass actual file paths)
        results = detector.scan_for_duplicates(files=all_files, use_xxhash=True)

        # Should find at least 3 duplicate groups
        assert results["duplicate_groups"] >= 3

        # Each duplicate group should have at least 2 files
        for file_hash, files in results["duplicates"].items():
            assert len(files) >= 2
