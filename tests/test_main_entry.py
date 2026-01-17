# tests/test_main_entry.py
"""
Test-driven development for main entry point
"""

import pytest
import sys
import os

sys.path.insert(0, "..")
from src.main import main


def test_cli_initialization():
    """Verify CLI initializes without errors"""
    # This test just verifies main can be imported
    import src.main

    assert True


def test_main_function_exists():
    """Verify main function exists"""
    from src.main import main

    assert callable(main)


def test_cli_module_imports():
    """Verify CLI module can be imported"""
    from src.cli_interface import CLI

    cli = CLI()
    assert cli is not None


def test_bin_script_exists():
    """Verify bin/gdo script exists"""
    bin_path = "bin/gdo"
    assert os.path.exists(bin_path)


def test_bin_script_executable():
    """Verify bin/gdo is executable"""
    import stat

    bin_path = "bin/gdo"
    st = os.stat(bin_path)
    assert st.st_mode & 0o111  # Executable by owner


def test_cli_scan_command():
    """Verify scan command works"""
    from src.cli_interface import CLI

    cli = CLI()
    result = cli.run_command(["scan", "."])
    assert result is not None
    assert "command" in result


def test_cli_organize_command():
    """Verify organize command works"""
    from src.cli_interface import CLI

    cli = CLI()
    result = cli.run_command(["organize", "."])
    assert result is not None
    assert "command" in result
