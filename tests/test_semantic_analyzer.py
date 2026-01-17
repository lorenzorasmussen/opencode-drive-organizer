# tests/test_semantic_analyzer.py
"""
Test-driven development for Task 3: 10-Dimensional Semantic Analysis Engine
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.semantic_analyzer import SemanticAnalyzer


def test_type_score():
    """Verify type score calculation based on file extension"""
    analyzer = SemanticAnalyzer()

    # High-risk files (executables, scripts)
    exe_score = analyzer.calculate_type_score("malware.exe")
    assert exe_score > 0.7

    # Low-risk files (text, data)
    txt_score = analyzer.calculate_type_score("notes.txt")
    assert txt_score < 0.5

    # Medium-risk files (documents, images)
    doc_score = analyzer.calculate_type_score("report.docx")
    assert 0.3 < doc_score < 0.7


def test_location_score():
    """Verify location score based on folder context"""
    analyzer = SemanticAnalyzer()

    # High-risk locations (root, downloads, temp)
    root_score = analyzer.calculate_location_score("/path/to/file.txt")
    assert root_score > 0.5

    # Low-risk locations (archived, organized)
    archive_score = analyzer.calculate_location_score("/archived/2024/file.txt")
    assert archive_score < 0.5


def test_age_score():
    """Verify age score based on file modification time"""
    analyzer = SemanticAnalyzer()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        # Old file (> 1 year)
        old_file = tmp.name
        os.utime(old_file, (1000000000, 1000000000))

        # New file (< 1 day)
        new_file = tmp.name + "_new"

    try:
        old_score = analyzer.calculate_age_score(old_file)
        new_score = analyzer.calculate_age_score(new_file)

        # Old files should have higher deletion confidence
        assert old_score > new_score
    finally:
        os.unlink(old_file)


def test_size_score():
    """Verify size score based on file size"""
    analyzer = SemanticAnalyzer()

    # Large files (> 100MB)
    large_score = analyzer.calculate_size_score(150 * 1024 * 1024)
    assert large_score > 0.7

    # Small files (< 1MB)
    small_score = analyzer.calculate_size_score(500 * 1024)
    assert small_score < 0.5


def test_risk_classification():
    """Verify risk level classification based on scores"""
    analyzer = SemanticAnalyzer()

    # Critical risk (low overall confidence)
    assert analyzer.classify_risk(0.3) == "CRITICAL"

    # High risk
    assert analyzer.classify_risk(0.6) == "HIGH"

    # Medium risk
    assert analyzer.classify_risk(0.8) == "MEDIUM"

    # Low risk (high confidence)
    assert analyzer.classify_risk(0.95) == "LOW"


def test_action_classification():
    """Verify action classification based on risk and scores"""
    analyzer = SemanticAnalyzer()

    # Critical + low confidence → DELETE_IMMEDIATE
    action1 = analyzer.classify_action(risk="CRITICAL", confidence=0.3)
    assert action1 == "DELETE_IMMEDIATE"

    # High risk + medium confidence → REVIEW_MANUAL
    action2 = analyzer.classify_action(risk="HIGH", confidence=0.6)
    assert action2 == "REVIEW_MANUAL"

    # Low risk + high confidence → KEEP_ACTIVE
    action3 = analyzer.classify_action(risk="LOW", confidence=0.95)
    assert action3 == "KEEP_ACTIVE"


def test_overall_confidence():
    """Verify overall confidence calculation from weighted dimensions"""
    analyzer = SemanticAnalyzer()

    scores = {
        "type_score": 0.8,
        "location_score": 0.7,
        "age_score": 0.9,
        "size_score": 0.6,
        "git_activity_score": 0.5,
        "reversibility_score": 0.4,
        "personal_data_score": 0.3,
        "context_score": 0.7,
        "predictive_score": 0.6,
    }

    confidence = analyzer.calculate_overall_confidence(scores)

    # Confidence should be between 0 and 1
    assert 0 <= confidence <= 1


def test_learning_system():
    """Verify learning system updates from manual corrections"""
    analyzer = SemanticAnalyzer()

    # Initial prediction
    initial_confidence = analyzer.calculate_overall_confidence({"type_score": 0.5})
    assert initial_confidence > 0

    # Learn from correction (increase confidence)
    analyzer.learn_from_correction(file_type="txt", location="archived", confidence=0.8)

    # Verify learning data is stored
    assert "learned_patterns" in dir(analyzer)


def test_batch_processing():
    """Verify batch processing handles multiple files efficiently"""
    analyzer = SemanticAnalyzer()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create 100 test files
        file_paths = []
        for i in range(100):
            file_path = os.path.join(tmpdir, f"file_{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Content {i}")
            file_paths.append(file_path)

        # Batch analyze
        results = analyzer.batch_analyze_files(file_paths)

        # Should analyze all files
        assert len(results) == 100

        # Each result should have required fields
        for result in results:
            assert "confidence" in result
            assert "risk" in result
            assert "action" in result


def test_statistics_generation():
    """Verify statistics generation for analysis runs"""
    analyzer = SemanticAnalyzer()

    stats = analyzer.generate_statistics()

    # Should have required fields
    assert "total_files_analyzed" in stats
    assert "average_confidence" in stats
    assert "risk_distribution" in stats
    assert "action_distribution" in stats
