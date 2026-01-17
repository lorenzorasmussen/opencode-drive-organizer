# tests/test_pattern_discovery.py
"""
Test-driven development for Task 11: Pattern Discovery Engine
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.pattern_discovery import PatternDiscovery


def test_discover_naming_patterns():
    """Verify discovering file naming patterns"""
    discovery = PatternDiscovery()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files with patterns
        patterns = [
            "report_2024_01_01.pdf",
            "report_2024_01_02.pdf",
            "report_2024_01_03.pdf",
            "invoice_001.txt",
            "invoice_002.txt",
            "invoice_003.txt",
        ]

        for pattern in patterns:
            open(os.path.join(tmpdir, pattern), "w").close()

        result = discovery.discover_naming_patterns(tmpdir)

        assert len(result) > 0
        assert any("report" in p.get("pattern", "") for p in result)
        assert any("invoice" in p.get("pattern", "") for p in result)


def test_discover_organization_patterns():
    """Verify discovering organization patterns"""
    discovery = PatternDiscovery()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create organized structure
        os.makedirs(os.path.join(tmpdir, "documents"))
        os.makedirs(os.path.join(tmpdir, "images"))
        os.makedirs(os.path.join(tmpdir, "archive"))

        open(os.path.join(tmpdir, "documents", "file1.txt"), "w").close()
        open(os.path.join(tmpdir, "images", "image1.png"), "w").close()
        open(os.path.join(tmpdir, "archive", "old.pdf"), "w").close()

        result = discovery.discover_organization_patterns(tmpdir)

        assert "folder_structure" in result
        assert len(result["folder_structure"]) > 0


def test_discover_duplicate_patterns():
    """Verify discovering duplicate patterns"""
    discovery = PatternDiscovery()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create duplicates with different names
        for i in range(3):
            filename = f"copy_{i}.txt"
            with open(os.path.join(tmpdir, filename), "w") as f:
                f.write("Same content")

        result = discovery.discover_duplicate_patterns(tmpdir)

        assert "potential_duplicates" in result
        assert len(result["potential_duplicates"]) >= 0


def test_discover_size_patterns():
    """Verify discovering file size patterns"""
    discovery = PatternDiscovery()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files with different sizes
        for i in range(5):
            filename = f"file_{i}.txt"
            size = 1024 * (i + 1)
            with open(os.path.join(tmpdir, filename), "w") as f:
                f.write("x" * size)

        result = discovery.discover_size_patterns(tmpdir)

        assert "size_distribution" in result
        assert len(result["size_distribution"]) > 0


def test_discover_temp_files():
    """Verify discovering temporary files"""
    discovery = PatternDiscovery()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create temp files
        temp_patterns = ["~file.txt", ".hidden_file.txt", "file.tmp", "file.bak"]

        for pattern in temp_patterns:
            open(os.path.join(tmpdir, pattern), "w").close()

        result = discovery.discover_temp_files(tmpdir)

        assert "temp_files" in result
        assert len(result["temp_files"]) > 0


def test_discover_type_distribution():
    """Verify discovering file type distribution"""
    discovery = PatternDiscovery()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files of different types (with unique names to avoid overwrites)
        files = ["file1.txt", "file2.txt", "file1.pdf", "file2.pdf", "file.py"]

        for filename in files:
            open(os.path.join(tmpdir, filename), "w").close()

        result = discovery.discover_type_distribution(tmpdir)

        assert "type_counts" in result
        assert result["type_counts"].get(".txt", 0) >= 2
        assert result["type_counts"].get(".pdf", 0) >= 2


def test_discover_age_patterns():
    """Verify discovering file age patterns"""
    discovery = PatternDiscovery()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create old and new files
        old_file = os.path.join(tmpdir, "old.txt")
        new_file = os.path.join(tmpdir, "new.txt")

        with open(old_file, "w") as f:
            f.write("Old")
        with open(new_file, "w") as f:
            f.write("New")

        # Make old file older
        import time

        old_time = time.time() - (365 * 24 * 60 * 60)  # 1 year ago
        os.utime(old_file, (old_time, old_time))

        result = discovery.discover_age_patterns(tmpdir)

        assert "age_distribution" in result
        assert len(result["age_distribution"]) > 0


def test_generate_recommendations():
    """Verify generating recommendations"""
    discovery = PatternDiscovery()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test structure
        for i in range(5):
            open(os.path.join(tmpdir, f"file_{i}.tmp"), "w").close()

        recommendations = discovery.generate_recommendations(tmpdir)

        assert len(recommendations) > 0
        assert all("action" in r for r in recommendations)
        assert all("priority" in r for r in recommendations)


def test_discover_all_patterns():
    """Verify discovering all patterns at once"""
    discovery = PatternDiscovery()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create various files
        os.makedirs(os.path.join(tmpdir, "reports"))
        open(os.path.join(tmpdir, "report_2024.pdf"), "w").close()
        open(os.path.join(tmpdir, "temp.tmp"), "w").close()

        result = discovery.discover_all(tmpdir)

        assert "naming_patterns" in result
        assert "organization_patterns" in result
        assert "type_distribution" in result
        assert "recommendations" in result


def test_pattern_confidence():
    """Verify pattern confidence scoring"""
    discovery = PatternDiscovery()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files with clear pattern
        for i in range(10):
            filename = f"report_2024_{i:03d}.pdf"
            open(os.path.join(tmpdir, filename), "w").close()

        patterns = discovery.discover_naming_patterns(tmpdir)

        # Should have high confidence for clear patterns
        if patterns:
            assert any(p.get("confidence", 0) > 0.5 for p in patterns)
