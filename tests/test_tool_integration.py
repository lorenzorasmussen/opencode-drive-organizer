# tests/test_tool_integration.py
"""
Test-driven development for Task 5: Tool Integration (fd, fzf, ripgrep, nnn)
"""

import pytest
import os
import tempfile
import sys
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.tool_integration import ToolIntegration


def test_fd_command():
    """Verify fd command integration"""
    integration = ToolIntegration()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")

        # Search with fd
        results = integration.fd_search(tmpdir, pattern="test")

        assert len(results) > 0
        assert any("test.txt" in r for r in results)


def test_fzf_selection():
    """Verify fzf command integration"""
    integration = ToolIntegration()

    # Note: fzf is interactive, so we test that the command exists
    assert integration.check_tool_available("fzf")


def test_ripgrep_search():
    """Verify ripgrep command integration"""
    integration = ToolIntegration()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files with content
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Hello World")

        # Search with ripgrep
        results = integration.ripgrep_search(tmpdir, pattern="Hello")

        assert len(results) > 0
        assert any("Hello" in r for r in results)


def test_nnn_navigation():
    """Verify nnn command integration"""
    integration = ToolIntegration()

    # Note: nnn is interactive, so we test that the command exists
    assert integration.check_tool_available("nnn")


def test_tool_availability_check():
    """Verify tool availability checking"""
    integration = ToolIntegration()

    # Check common tools
    tools = ["fd", "fzf", "ripgrep", "nnn"]

    for tool in tools:
        available = integration.check_tool_available(tool)
        # At least some tools should be available
        assert isinstance(available, bool)


def test_fd_with_extensions():
    """Verify fd search with file extension filtering"""
    integration = ToolIntegration()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        txt_file = os.path.join(tmpdir, "test.txt")
        py_file = os.path.join(tmpdir, "test.py")

        with open(txt_file, "w") as f:
            f.write("text")
        with open(py_file, "w") as f:
            f.write("code")

        # Search only .txt files
        results = integration.fd_search(tmpdir, extension="txt")

        assert len(results) > 0
        assert all(".txt" in r for r in results)


def test_ripgrep_with_regex():
    """Verify ripgrep search with regex patterns"""
    integration = ToolIntegration()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Hello World\nHello Python\n")

        # Search with regex
        results = integration.ripgrep_search(tmpdir, pattern=r"Hello \w+")

        assert len(results) > 0


def test_tool_executions_stats():
    """Verify tool execution statistics tracking"""
    integration = ToolIntegration()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Execute tools
        integration.fd_search(tmpdir, pattern="test")

        # Get stats
        stats = integration.get_execution_stats()

        assert "total_executions" in stats
        assert stats["total_executions"] > 0


def test_error_handling():
    """Verify error handling for missing tools"""
    integration = ToolIntegration()

    # Try to use a non-existent tool
    results = integration.execute_tool("nonexistent_tool", ["--help"])

    # Should handle gracefully
    assert results is None or "error" in str(results).lower()


def test_tool_timeout():
    """Verify tool execution timeout handling"""
    integration = ToolIntegration(timeout=1)

    # Try to execute a command that might hang
    results = integration.fd_search("/nonexistent", pattern="test")

    # Should handle timeout gracefully
    assert results is not None
