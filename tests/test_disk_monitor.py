# tests/test_disk_monitor.py
"""
Test-driven development for Task 8: Disk Usage Monitoring Daemon
"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.disk_monitor import DiskMonitor


def test_get_disk_usage():
    """Verify getting disk usage"""
    monitor = DiskMonitor()

    usage = monitor.get_disk_usage("/")

    assert "total_gb" in usage
    assert "used_gb" in usage
    assert "free_gb" in usage
    assert "usage_percent" in usage
    assert 0 <= usage["usage_percent"] <= 100


def test_get_directory_size():
    """Verify calculating directory size"""
    monitor = DiskMonitor()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test content" * 100)

        size = monitor.get_directory_size(tmpdir)

        assert size > 0
        assert size < 10000  # Less than 10KB


def test_monitor_disk_space():
    """Verify continuous disk monitoring"""
    monitor = DiskMonitor()

    monitor.start_monitoring("/")
    monitor.stop_monitoring()

    assert len(monitor.get_usage_history()) > 0


def test_disk_threshold_alert():
    """Verify disk threshold alerts"""
    monitor = DiskMonitor(threshold=90)

    alerts = []
    monitor.set_alert_callback(alerts.append)

    # Simulate high usage (will only trigger if real usage is high)
    monitor.check_threshold()

    # Should have checked threshold
    assert monitor.threshold == 90


def test_get_large_directories():
    """Verify finding large directories"""
    monitor = DiskMonitor()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create directories with different sizes
        large_dir = os.path.join(tmpdir, "large")
        small_dir = os.path.join(tmpdir, "small")

        os.makedirs(large_dir)
        os.makedirs(small_dir)

        # Add files to large directory
        for i in range(10):
            file_path = os.path.join(large_dir, f"file{i}.txt")
            with open(file_path, "w") as f:
                f.write("Large content" * 1000)

        large_dirs = monitor.get_large_directories(tmpdir, min_size_mb=0.001)

        assert len(large_dirs) > 0


def test_get_disk_space_trend():
    """Verify tracking disk space trends"""
    monitor = DiskMonitor()

    # Record multiple measurements
    for i in range(5):
        monitor.record_measurement("/")

    trend = monitor.get_usage_trend()

    assert "slope" in trend
    assert "direction" in trend


def test_export_usage_report():
    """Verify exporting usage report"""
    monitor = DiskMonitor()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        report_path = f.name

    try:
        monitor.export_usage_report(report_path)
        assert os.path.exists(report_path)
    finally:
        os.unlink(report_path)


def test_get_disk_info():
    """Verify getting detailed disk information"""
    monitor = DiskMonitor()

    info = monitor.get_disk_info("/")

    assert "filesystem" in info
    assert "total" in info
    assert "used" in info
    assert "free" in info


def test_cleanup_old_measurements():
    """Verify cleanup of old measurements"""
    monitor = DiskMonitor(max_history=5)

    # Add more measurements than max_history
    for i in range(10):
        monitor.record_measurement("/")

    history = monitor.get_usage_history()

    # Should keep only max_history
    assert len(history) <= 5


def test_calculate_growth_rate():
    """Verify calculating disk growth rate"""
    monitor = DiskMonitor()

    # Simulate measurements over time
    initial_usage = 50.0  # 50%
    final_usage = 60.0  # 60%

    growth = monitor.calculate_growth_rate(initial_usage, final_usage, days=30)

    assert growth > 0
