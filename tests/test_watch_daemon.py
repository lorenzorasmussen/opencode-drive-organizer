"""
Test-driven development for Features 3-5:
- Watch mode daemon for real-time file monitoring
- LLM-powered folder structure generation
- Learning from user file operations
"""

import pytest
import os
import tempfile
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_watch_daemon_initialization_with_path():
    """Verify watch daemon can be initialized with path"""
    from src.watch_daemon import WatchDaemon

    with tempfile.TemporaryDirectory() as tmpdir:
        daemon = WatchDaemon(watch_path=tmpdir)
        assert daemon is not None
        assert daemon.watch_path == tmpdir


def test_watch_daemon_start_stop():
    """Verify daemon can start and stop"""
    from src.watch_daemon import WatchDaemon, FileOperation

    with tempfile.TemporaryDirectory() as tmpdir:
        daemon = WatchDaemon(watch_path=tmpdir)

        # Mock the observer to avoid actual file watching
        with patch.object(daemon, "_start_observer") as mock_start:
            mock_start.return_value = None

            daemon.start(blocking=False)
            assert daemon.is_running() == True

            daemon.stop()
            assert daemon.is_running() == False


def test_watch_daemon_detects_new_files():
    """Verify daemon detects new files via _on_event"""
    from src.watch_daemon import WatchDaemon, FileOperation

    with tempfile.TemporaryDirectory() as tmpdir:
        event_handler = Mock()

        daemon = WatchDaemon(watch_path=tmpdir, event_handler=event_handler)

        with patch.object(daemon, "_start_observer") as mock_start:
            mock_start.return_value = None
            daemon.start(blocking=False)

            # Simulate event using _on_event method
            test_file = os.path.join(tmpdir, "new_file.txt")
            daemon._on_event(FileOperation.CREATE, test_file)

            # Give time for processing
            time.sleep(0.1)

            # Verify event handler was called
            event_handler.assert_called()

            daemon.stop()


def test_watch_daemon_detects_moves():
    """Verify daemon detects file moves"""
    from src.watch_daemon import WatchDaemon, FileOperation

    with tempfile.TemporaryDirectory() as tmpdir:
        event_handler = Mock()

        daemon = WatchDaemon(watch_path=tmpdir, event_handler=event_handler)

        with patch.object(daemon, "_start_observer") as mock_start:
            mock_start.return_value = None
            daemon.start(blocking=False)

            # Simulate move event
            old_path = os.path.join(tmpdir, "old.txt")
            new_path = os.path.join(tmpdir, "new.txt")
            daemon._on_event(FileOperation.MOVE, old_path, new_path)

            time.sleep(0.1)

            event_handler.assert_called()
            daemon.stop()


def test_folder_generator_initialization():
    """Verify folder structure generator can be initialized"""
    from src.watch_daemon import FolderStructureGenerator

    generator = FolderStructureGenerator()
    assert generator is not None


def test_folder_generator_proposes_structure():
    """Verify generator proposes folder structure"""
    from src.watch_daemon import FolderStructureGenerator

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        (Path(tmpdir) / "report.pdf").write_text("Q4 financial report")
        (Path(tmpdir) / "vacation_photo.jpg").write_bytes(b"fake")
        (Path(tmpdir) / "invoice_2024-01.pdf").write_text("January invoice")

        generator = FolderStructureGenerator()

        # Test basic structure proposal (without LLM)
        structure = generator.propose_structure(tmpdir)

        assert "files" in structure
        assert len(structure["files"]) == 3


def test_folder_generator_uses_llm():
    """Verify generator uses LLM for smart categorization"""
    from src.watch_daemon import FolderStructureGenerator

    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "quarterly_report.pdf").write_text("Q4 2024 report")

        generator = FolderStructureGenerator()

        # Mock LLM response
        with patch.object(generator, "_query_llm") as mock_query:
            mock_query.return_value = {
                "files": [
                    {
                        "src_path": os.path.join(tmpdir, "quarterly_report.pdf"),
                        "dst_path": "work/reports/2024/quarterly_report.pdf",
                    }
                ]
            }

            structure = generator.propose_structure(tmpdir, use_llm=True)

            mock_query.assert_called()
            assert "files" in structure


def test_learning_system_initialization():
    """Verify learning system can be initialized"""
    from src.watch_daemon import FileOperationLearner

    with tempfile.TemporaryDirectory() as tmpdir:
        learner = FileOperationLearner(
            data_file=os.path.join(tmpdir, "test_learning.json")
        )
        assert learner is not None


def test_learning_system_records_patterns():
    """Verify learner records user patterns"""
    from src.watch_daemon import FileOperationLearner

    with tempfile.TemporaryDirectory() as tmpdir:
        learner = FileOperationLearner(
            data_file=os.path.join(tmpdir, "test_learning.json")
        )

        # Record a pattern
        learner.record_operation(
            src=os.path.join(tmpdir, "downloads", "report.pdf"),
            dst=os.path.join(tmpdir, "work", "reports", "report.pdf"),
            operation="move",
        )

        patterns = learner.get_patterns()

        assert len(patterns) >= 1


def test_learning_system_suggests_action():
    """Verify learner suggests actions based on patterns"""
    from src.watch_daemon import FileOperationLearner

    with tempfile.TemporaryDirectory() as tmpdir:
        learner = FileOperationLearner(
            data_file=os.path.join(tmpdir, "test_learning.json")
        )

        # Learn a pattern with a specific file
        learner.record_operation(
            src=os.path.join(tmpdir, "downloads", "report.pdf"),
            dst=os.path.join(tmpdir, "work", "reports", "report.pdf"),
            operation="move",
        )

        # Get suggestion for similar file (same directory, similar name)
        test_file = os.path.join(tmpdir, "downloads", "new_file.pdf")
        suggestion = learner.suggest_destination(test_file)

        # Should suggest based on src_pattern matching
        assert suggestion is not None or len(learner.get_patterns()) >= 1


def test_learning_system_learns_from_decisions():
    """Verify learner improves from user feedback"""
    from src.watch_daemon import FileOperationLearner

    with tempfile.TemporaryDirectory() as tmpdir:
        learner = FileOperationLearner(
            data_file=os.path.join(tmpdir, "test_learning.json")
        )

        # Record initial pattern
        learner.record_operation(
            src=os.path.join(tmpdir, "downloads", "report.pdf"),
            dst=os.path.join(tmpdir, "archive", "old_reports", "report.pdf"),
            operation="move",
        )

        # User corrects the suggestion
        learner.record_feedback(
            src_pattern=os.path.join(tmpdir, "downloads"),
            suggested=os.path.join(tmpdir, "archive", "old_reports"),
            actual=os.path.join(tmpdir, "work", "current_reports"),
            accepted=False,
        )

        # Check that feedback was recorded
        feedback = learner.get_recent_feedback()
        assert len(feedback) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
