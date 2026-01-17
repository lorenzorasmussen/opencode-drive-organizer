"""
Test-driven development for Feature 1: LlamaIndex Content Extraction
"""

import pytest
import os
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.llamaindex_extractor import LlamaIndexExtractor


def test_llamaindex_extractor_initialization():
    """Verify LlamaIndex content extractor can be initialized"""
    extractor = LlamaIndexExtractor()
    assert extractor is not None


def test_llamaindex_extracts_text_content():
    """Verify extractor can read text file content"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("This is a test document with some content.")

        extractor = LlamaIndexExtractor()
        documents = extractor.extract(tmpdir)

        assert len(documents) == 1
        assert "test document" in documents[0]["content"].lower()
        assert documents[0]["metadata"]["file_path"] == str(test_file)


def test_llamaindex_extracts_metadata():
    """Verify extractor extracts file metadata"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "document.pdf"
        test_file.write_text("PDF content here")

        extractor = LlamaIndexExtractor()
        documents = extractor.extract(tmpdir)

        assert len(documents) == 1
        metadata = documents[0]["metadata"]
        assert "file_path" in metadata
        assert "file_name" in metadata
        assert "file_size" in metadata
        assert "file_type" in metadata


def test_llamaindex_recursive_scan():
    """Verify extractor scans subdirectories"""
    with tempfile.TemporaryDirectory() as tmpdir:
        subdir = Path(tmpdir) / "subdir"
        subdir.mkdir()

        (Path(tmpdir) / "root.txt").write_text("root file")
        (subdir / "nested.txt").write_text("nested file")

        extractor = LlamaIndexExtractor()
        documents = extractor.extract(tmpdir, recursive=True)

        assert len(documents) == 2


def test_llamaindex_handles_multiple_formats():
    """Verify extractor handles various file formats"""
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "test.txt").write_text("Text content")
        (Path(tmpdir) / "test.md").write_text("# Markdown")
        (Path(tmpdir) / "test.json").write_text('{"key": "value"}')

        extractor = LlamaIndexExtractor()
        documents = extractor.extract(tmpdir)

        assert len(documents) == 3


def test_llamaindex_summarizes_content():
    """Verify extractor can summarize content using LLM"""
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "report.txt").write_text(
            "This is a quarterly financial report showing revenue growth."
        )

        extractor = LlamaIndexExtractor()
        documents = extractor.extract_with_summaries(tmpdir, summarize=True)

        assert len(documents) == 1
        assert "summary" in documents[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
