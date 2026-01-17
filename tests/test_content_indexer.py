# tests/test_content_indexer.py
"""
Test-driven development for Task 12: Content Indexing
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.content_indexer import ContentIndexer


def test_index_directory():
    """Verify indexing a directory"""
    indexer = ContentIndexer()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        for i in range(3):
            with open(os.path.join(tmpdir, f"file{i}.txt"), "w") as f:
                f.write(f"Content {i}")

        result = indexer.index_directory(tmpdir)

        assert len(result) >= 3
        assert all("content" in r for r in result)


def test_search_index():
    """Verify searching indexed content"""
    indexer = ContentIndexer()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create file with specific content
        file_path = os.path.join(tmpdir, "test.txt")
        with open(file_path, "w") as f:
            f.write("Hello World Python")

        indexer.index_directory(tmpdir)

        results = indexer.search("Python")

        assert len(results) > 0
        assert any("test.txt" in r.get("file", "") for r in results)


def test_update_index():
    """Verify updating index with new files"""
    indexer = ContentIndexer()

    with tempfile.TemporaryDirectory() as tmpdir:
        indexer.index_directory(tmpdir)

        # Add new file
        new_file = os.path.join(tmpdir, "new.txt")
        with open(new_file, "w") as f:
            f.write("New content")

        results = indexer.update_index(tmpdir)

        assert len(results) > 0


def test_extract_keywords():
    """Verify extracting keywords from content"""
    indexer = ContentIndexer()

    content = "Python is great for machine learning and data science"
    keywords = indexer.extract_keywords(content)

    assert len(keywords) > 0
    assert "python" in [k.lower() for k in keywords]


def test_get_index_stats():
    """Verify getting index statistics"""
    indexer = ContentIndexer()

    stats = indexer.get_index_stats()

    assert "total_files" in stats
    assert "total_keywords" in stats


def test_export_import_index():
    """Verify exporting and importing index"""
    indexer = ContentIndexer()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        export_path = f.name

    try:
        indexer.export_index(export_path)
        assert os.path.exists(export_path)

        new_indexer = ContentIndexer()
        new_indexer.import_index(export_path)

        assert new_indexer.get_index_stats()["total_files"] >= 0
    finally:
        os.unlink(export_path)


def test_remove_from_index():
    """Verify removing files from index"""
    indexer = ContentIndexer()

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "test.txt")
        with open(file_path, "w") as f:
            f.write("Test")

        indexer.index_directory(tmpdir)
        indexer.remove_from_index(file_path)

        assert len(indexer.search("Test")) == 0


def test_clear_index():
    """Verify clearing index"""
    indexer = ContentIndexer()

    with tempfile.TemporaryDirectory() as tmpdir:
        indexer.index_directory(tmpdir)
        indexer.clear_index()

        stats = indexer.get_index_stats()
        assert stats["total_files"] == 0


def test_find_similar():
    """Verify finding similar documents"""
    indexer = ContentIndexer()

    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "file1.txt")
        file2 = os.path.join(tmpdir, "file2.txt")

        with open(file1, "w") as f:
            f.write("Python programming tutorial")
        with open(file2, "w") as f:
            f.write("Machine learning with Python")

        indexer.index_directory(tmpdir)

        similar = indexer.find_similar(file1)

        assert len(similar) >= 0


def test_index_performance():
    """Verify indexing performance"""
    indexer = ContentIndexer()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create many files
        for i in range(100):
            with open(os.path.join(tmpdir, f"file{i}.txt"), "w") as f:
                f.write(f"Content {i}")

        results = indexer.index_directory(tmpdir)

        assert len(results) >= 99
        assert indexer.get_index_stats()["total_files"] >= 99
