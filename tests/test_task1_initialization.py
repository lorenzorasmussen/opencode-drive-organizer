# tests/test_task1_initialization.py
"""
Test-driven development for Task 1: Project Initialization
"""

import os
import pytest
import yaml
import pandas as pd


def test_readme_exists():
    """Verify README.md exists and contains required sections"""
    readme_path = "README.md"

    assert os.path.exists(readme_path), "README.md should exist"

    with open(readme_path, "r") as f:
        content = f.read()

    # Check for required sections
    assert "# Google Drive Autonomous Organization System" in content, (
        "Missing project title"
    )
    assert "## Features" in content or "### Features" in content, (
        "Missing features section"
    )
    assert "## Installation" in content, "Missing installation section"
    assert "## Usage" in content, "Missing usage section"


def test_readme_research_integration():
    """Verify README mentions all 4 research documents"""
    readme_path = "README.md"

    with open(readme_path, "r") as f:
        content = f.read()

    assert "File Organization Research" in content, "Missing research document 1"
    assert "Semantic Analysis Report" in content, "Missing research document 2"
    assert "Google Drive Organization" in content, "Missing research document 3"
    assert "Advanced Features" in content, "Missing advanced features"


def test_gitignore_exists():
    """Verify .gitignore exists and blocks sensitive files"""
    gitignore_path = ".gitignore"

    assert os.path.exists(gitignore_path), ".gitignore should exist"

    with open(gitignore_path, "r") as f:
        content = f.read()

    # Check for critical blocks
    assert "credentials.json" in content, "Should block credentials"
    assert "*.token" in content, "Should block tokens"
    assert "data/cache/" in content, "Should block cache directory"
    assert "logs/" in content, "Should block logs"
    assert "output/" in content, "Should block output"
    assert "**/*personal*" in content, "Should block personal files"


def test_gitignore_blocks_secrets():
    """Verify .gitignore blocks various secret patterns"""
    gitignore_path = ".gitignore"

    with open(gitignore_path, "r") as f:
        content = f.read()

    # Should block multiple secret patterns
    secret_patterns = ["credentials", "secrets", ".env"]
    blocked_count = sum(1 for pattern in secret_patterns if pattern in content)

    assert blocked_count >= 2, (
        f"Should block at least 2 secret patterns, found {blocked_count}"
    )


def test_requirements_exists():
    """Verify requirements.txt exists and contains required packages"""
    requirements_path = "requirements.txt"

    assert os.path.exists(requirements_path), "requirements.txt should exist"

    with open(requirements_path, "r") as f:
        content = f.read()

    # Check for required packages
    assert "google-api-python-client" in content, "Missing google-api-python-client"
    assert "pandas" in content, "Missing pandas"
    assert "pyyaml" in content, "Missing pyyaml"


def test_requirements_advanced_features():
    """Verify requirements.txt includes advanced features from research"""
    requirements_path = "requirements.txt"

    with open(requirements_path, "r") as f:
        content = f.read()

    # Should include fast duplicate detection
    assert "xxhash" in content, "Missing xxhash for fast duplicate detection"

    # Should include performance monitoring
    assert "psutil" in content, "Missing psutil for performance monitoring"

    # Should include Ollama
    assert "ollama" in content, "Missing ollama for local LLM"


def test_project_structure_created():
    """Verify project directories are created"""
    directories = [
        "src/",
        "tests/",
        "config/",
        "data/",
        "logs/",
        "output/",
        "agent/",
        "docs/",
        "bin/",
    ]

    for directory in directories:
        assert os.path.exists(directory), f"Directory {directory} should exist"


def test_readme_architecture_section():
    """Verify README includes architecture section"""
    readme_path = "README.md"

    with open(readme_path, "r") as f:
        content = f.read()

    # Should mention the 5-layer architecture
    assert "Sync Layer" in content or "## Architecture" in content, (
        "Missing architecture details"
    )


def test_readme_confidence_thresholds():
    """Verify README mentions confidence-based execution"""
    readme_path = "README.md"

    with open(readme_path, "r") as f:
        content = f.read()

    # Should mention confidence thresholds
    assert "0.9-1.0" in content or "0.9" in content, "Missing high confidence threshold"
    assert "0.7" in content, "Missing medium confidence threshold"


def test_requirements_version_constraints():
    """Verify requirements.txt has version constraints"""
    requirements_path = "requirements.txt"

    with open(requirements_path, "r") as f:
        content = f.read()

        # Should have version constraints for stability
        assert ">=" in content or "==" in content, "Should have version constraints"
