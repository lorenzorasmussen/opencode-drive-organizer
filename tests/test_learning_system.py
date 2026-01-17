# tests/test_learning_system.py
"""
Test-driven development for Task 7: Learning System from Manual Corrections
"""

import pytest
import os
import tempfile
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.learning_system import LearningSystem


def test_record_correction():
    """Verify recording manual corrections"""
    system = LearningSystem()

    system.record_correction(
        file_path="test.txt",
        original_action="DELETE_IMMEDIATE",
        corrected_action="KEEP_ACTIVE",
        reason="Important document",
    )

    assert len(system.get_corrections()) == 1


def test_learning_from_corrections():
    """Verify learning from recorded corrections"""
    system = LearningSystem()

    # Record multiple corrections
    system.record_correction("file.txt", "DELETE", "KEEP", "Important")
    system.record_correction("file.txt", "DELETE", "KEEP", "Important")
    system.record_correction("file.txt", "DELETE", "KEEP", "Important")

    # Get learned pattern
    pattern = system.get_learned_pattern("file.txt")

    assert pattern is not None
    assert pattern["recommended_action"] == "KEEP"


def test_pattern_similarity():
    """Verify pattern similarity matching"""
    system = LearningSystem()

    # Learn from .txt files
    system.record_correction("important.txt", "DELETE", "KEEP", "Important")

    # Should match similar files (lower threshold for realistic similarity)
    score = system.get_pattern_similarity("important_backup.txt")
    assert score > 0.5


def test_confidence_scoring():
    """Verify confidence scoring for learned patterns"""
    system = LearningSystem()

    # More corrections = higher confidence
    for i in range(10):
        system.record_correction("file.txt", "DELETE", "KEEP", "Important")

    pattern = system.get_learned_pattern("file.txt")
    assert pattern["confidence"] > 0.8


def test_decay_old_patterns():
    """Verify decaying old patterns"""
    system = LearningSystem(decay_rate=0.5)

    # Old correction
    system.record_correction("old.txt", "DELETE", "KEEP", "Old")
    # Simulate time passing by modifying timestamp
    corrections = system.get_corrections()
    if corrections:
        corrections[0]["timestamp"] = "2020-01-01T00:00:00"

    pattern = system.get_learned_pattern("old.txt")
    assert pattern["confidence"] < 1.0


def test_export_import_learning_data():
    """Verify exporting and importing learning data"""
    system = LearningSystem()

    system.record_correction("file.txt", "DELETE", "KEEP", "Important")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        export_path = f.name

    try:
        system.export_learning_data(export_path)
        assert os.path.exists(export_path)

        # Import and verify
        new_system = LearningSystem()
        new_system.import_learning_data(export_path)

        assert len(new_system.get_corrections()) == 1
    finally:
        os.unlink(export_path)


def test_batch_learning():
    """Verify batch learning from multiple corrections"""
    system = LearningSystem()

    corrections = [
        {
            "file_path": "file1.txt",
            "original_action": "DELETE",
            "corrected_action": "KEEP",
            "reason": "Important",
        },
        {
            "file_path": "file2.txt",
            "original_action": "DELETE",
            "corrected_action": "KEEP",
            "reason": "Important",
        },
    ]

    system.batch_learn(corrections)

    assert len(system.get_corrections()) == 2


def test_pattern_recommendation():
    """Verify pattern-based action recommendations"""
    system = LearningSystem()

    # Learn pattern
    for i in range(5):
        system.record_correction("important.txt", "DELETE", "KEEP", "Important")

    # Get recommendation
    recommendation = system.recommend_action("important.txt")
    assert recommendation["action"] == "KEEP"
    assert recommendation["confidence"] > 0.5


def test_statistics():
    """Verify learning system statistics"""
    system = LearningSystem()

    system.record_correction("file1.txt", "DELETE", "KEEP", "Reason 1")
    system.record_correction("file2.txt", "DELETE", "REVIEW", "Reason 2")

    stats = system.get_statistics()

    assert stats["total_corrections"] == 2
    assert "most_common_correction" in stats
