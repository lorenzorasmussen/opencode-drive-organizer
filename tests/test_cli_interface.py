# tests/test_cli_interface.py
"""
Test-driven development for Task 19: CLI Interface
"""

import pytest
import sys

sys.path.insert(0, "..")
from src.cli_interface import CLI


def test_cli_initialization():
    """Verify CLI initialization"""
    cli = CLI()
    assert cli is not None


def test_scan_command():
    """Verify scan command"""
    cli = CLI()
    result = cli.run_command(["scan", "."])
    assert result is not None


def test_organize_command():
    """Verify organize command"""
    cli = CLI()
    result = cli.run_command(["organize", "."])
    assert result is not None


def test_duplicate_command():
    """Verify duplicate detection command"""
    cli = CLI()
    result = cli.run_command(["duplicates", "."])
    assert result is not None


def test_analyze_command():
    """Verify analyze command"""
    cli = CLI()
    result = cli.run_command(["analyze", "."])
    assert result is not None


def test_help_command():
    """Verify help command returns error dict"""
    cli = CLI()
    result = cli.run_command(["--help"])
    assert result is not None
    assert result.get("status") == "error"
    assert result.get("exit_code") == 0


def test_version_command():
    """Verify version command returns error dict"""
    cli = CLI()
    result = cli.run_command(["--version"])
    assert result is not None
    assert result.get("status") == "error"
    assert result.get("exit_code") == 0


def test_command_validation():
    """Verify command validation returns error dict"""
    cli = CLI()
    result = cli.run_command(["invalid-command"])
    assert result is not None
    assert result.get("status") == "error"
    assert result.get("exit_code") == 2


def test_verbose_output():
    """Verify verbose output mode"""
    cli = CLI()
    result = cli.run_command(["--verbose", "scan", "."])
    assert result is not None


def test_config_option():
    """Verify config option"""
    cli = CLI()
    result = cli.run_command(["--config", "test.json", "scan", "."])
    assert result is not None
