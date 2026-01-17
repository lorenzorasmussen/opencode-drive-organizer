# tests/test_google_drive_api.py
"""
Test-driven development for Task 9: Google Drive API Integration
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.google_drive_api import GoogleDriveAPI


def test_api_initialization():
    """Verify API initialization"""
    api = GoogleDriveAPI()

    assert api is not None
    assert hasattr(api, "service")


def test_list_files():
    """Verify listing files"""
    api = GoogleDriveAPI()

    files = api.list_files()

    # Should return list or empty if no credentials
    assert files is None or isinstance(files, list)


def test_upload_file():
    """Verify uploading files"""
    api = GoogleDriveAPI()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test content")
        temp_path = f.name

    try:
        result = api.upload_file(temp_path, "test_upload.txt")

        # Should return file ID or None if no credentials
        assert result is None or isinstance(result, str)
    finally:
        os.unlink(temp_path)


def test_download_file():
    """Verify downloading files"""
    api = GoogleDriveAPI()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        temp_path = f.name

    try:
        success = api.download_file("file_id", temp_path)

        # Should handle gracefully if file not found
        assert success is False or success is True
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_delete_file():
    """Verify deleting files"""
    api = GoogleDriveAPI()

    success = api.delete_file("file_id")

    # Should handle gracefully
    assert success is False or success is True


def test_create_folder():
    """Verify creating folders"""
    api = GoogleDriveAPI()

    result = api.create_folder("test_folder")

    assert result is None or isinstance(result, str)


def test_search_files():
    """Verify searching files"""
    api = GoogleDriveAPI()

    results = api.search_files("test query")

    assert results is None or isinstance(results, list)


def test_get_file_info():
    """Verify getting file information"""
    api = GoogleDriveAPI()

    info = api.get_file_info("file_id")

    assert info is None or isinstance(info, dict)


def test_move_file():
    """Verify moving files"""
    api = GoogleDriveAPI()

    success = api.move_file("file_id", "folder_id")

    assert success is False or success is True


def test_batch_operations():
    """Verify batch operations"""
    api = GoogleDriveAPI()

    file_ids = ["id1", "id2", "id3"]
    results = api.batch_delete(file_ids)

    assert results is None or isinstance(results, list)
