# tests/test_confidence_executor.py
"""
Test-driven development for Task 14: Confidence-Based Executor
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, "..")
from src.confidence_executor import ConfidenceExecutor


def test_execute_high_confidence():
    """Verify executing high confidence actions"""
    executor = ConfidenceExecutor(thresholds={"auto_execute": 0.9})

    # Create test file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        temp_path = f.name
        f.write("Test content")

    try:
        action = {"type": "DELETE", "file": temp_path, "confidence": 0.95}

        result = executor.execute_action(action)

        assert result["executed"] == True
        assert result["method"] == "automatic"
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_execute_medium_confidence():
    """Verify requiring review for medium confidence"""
    executor = ConfidenceExecutor(thresholds={"auto_execute": 0.9})

    action = {"type": "DELETE", "file": "test.txt", "confidence": 0.7}

    result = executor.execute_action(action)

    assert result["executed"] == False
    assert result["method"] == "manual_review"


def test_execute_low_confidence():
    """Verify skipping low confidence actions"""
    executor = ConfidenceExecutor(thresholds={"auto_execute": 0.5})

    action = {"type": "DELETE", "file": "test.txt", "confidence": 0.3}

    result = executor.execute_action(action)

    assert result["executed"] == False
    assert result["method"] == "skipped"


def test_rollback_action():
    """Verify rolling back executed actions"""
    executor = ConfidenceExecutor()

    # Create test file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        temp_path = f.name
        f.write("Test content")

    try:
        action = {"type": "DELETE", "file": temp_path, "confidence": 0.95}

        result = executor.execute_action(action)

        if result.get("executed"):
            success = executor.rollback_action(result["id"])

            assert success == True or os.path.exists(temp_path)
        else:
            # If action wasn't executed, rollback should fail gracefully
            success = executor.rollback_action(0)
            assert success == False
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_batch_execute():
    """Verify batch executing actions"""
    executor = ConfidenceExecutor(thresholds={"auto_execute": 0.9})

    # Create temp files
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "file1.txt")
        file2 = os.path.join(tmpdir, "file2.txt")
        file3 = os.path.join(tmpdir, "file3.txt")

        with open(file1, "w") as f:
            f.write("content1")
        with open(file2, "w") as f:
            f.write("content2")
        with open(file3, "w") as f:
            f.write("content3")

        actions = [
            {"type": "DELETE", "file": file1, "confidence": 0.95},
            {"type": "DELETE", "file": file2, "confidence": 0.4},
            {"type": "DELETE", "file": file3, "confidence": 0.92},
        ]

        results = executor.batch_execute(actions)

        assert len(results) == 3
        executed_count = sum(1 for r in results if r.get("executed"))
        assert executed_count == 2


def test_get_execution_history():
    """Verify getting execution history"""
    executor = ConfidenceExecutor()

    history = executor.get_execution_history()

    assert isinstance(history, list)


def test_clear_history():
    """Verify clearing execution history"""
    executor = ConfidenceExecutor()

    executor.clear_history()
    history = executor.get_execution_history()

    assert len(history) == 0


def test_action_validation():
    """Verify validating actions before execution"""
    executor = ConfidenceExecutor()

    valid_action = {"type": "DELETE", "file": "test.txt", "confidence": 0.9}

    is_valid = executor.validate_action(valid_action)

    assert is_valid == True


def test_get_statistics():
    """Verify getting executor statistics"""
    executor = ConfidenceExecutor()

    stats = executor.get_statistics()

    assert "total_actions" in stats
    assert "executed_actions" in stats
    assert "skipped_actions" in stats
