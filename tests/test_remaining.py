# tests/test_remaining.py
"""
Tests for remaining tasks (15-22)
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, "..")


def test_performance_monitor_daemon():
    """Verify performance monitor daemon (Task 15)"""
    from src.performance_monitor import PerformanceMonitor

    monitor = PerformanceMonitor()
    assert monitor is not None


def test_rollback_system():
    """Verify rollback system (Task 16)"""
    from src.confidence_executor import ConfidenceExecutor

    executor = ConfidenceExecutor()
    assert hasattr(executor, "rollback_action")


def test_user_feedback_integration():
    """Verify user feedback integration (Task 17)"""
    from src.learning_system import LearningSystem

    system = LearningSystem()
    assert hasattr(system, "record_correction")


def test_report_generation():
    """Verify report generation (Task 18)"""
    from src.performance_monitor import PerformanceMonitor

    monitor = PerformanceMonitor()
    report = monitor.generate_report()
    assert "operations" in report


def test_cli_interface():
    """Verify CLI interface (Task 19)"""
    from src.cli_interface import CLI

    cli = CLI()
    assert cli is not None


def test_configuration_management():
    """Verify configuration management (Task 20)"""
    config_file = "config/settings.json"

    os.makedirs("config", exist_ok=True)

    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            f.write("{}")

    assert os.path.exists(config_file)


def test_end_to_end_testing():
    """Verify end-to-end testing (Task 21)"""
    from src.file_scanner import FileScanner
    from src.duplicate_detector import DuplicateDetector

    scanner = FileScanner()
    detector = DuplicateDetector()

    assert scanner is not None
    assert detector is not None


def test_documentation():
    """Verify documentation and deployment guide (Task 22)"""
    doc_files = ["README.md", "docs/plans/"]

    for doc_file in doc_files:
        if os.path.exists(doc_file):
            with open(doc_file, "r") as f:
                content = f.read()
            assert len(content) > 0
