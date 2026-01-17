# tests/test_performance_monitor.py
"""
Test-driven development for Task 4: Performance Monitoring System
"""

import pytest
import os
import tempfile
import sys
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.performance_monitor import PerformanceMonitor


def test_performance_tracking():
    """Verify performance metrics are tracked"""
    monitor = PerformanceMonitor()

    # Track operation
    with monitor.track_operation("test_operation"):
        time.sleep(0.01)

    stats = monitor.get_operation_stats("test_operation")

    assert "count" in stats
    assert "total_time" in stats
    assert "average_time" in stats
    assert stats["count"] == 1


def test_multiple_operations():
    """Verify multiple operations are tracked separately"""
    monitor = PerformanceMonitor()

    with monitor.track_operation("operation_a"):
        time.sleep(0.01)

    with monitor.track_operation("operation_b"):
        time.sleep(0.02)

    stats_a = monitor.get_operation_stats("operation_a")
    stats_b = monitor.get_operation_stats("operation_b")

    assert stats_a["count"] == 1
    assert stats_b["count"] == 1
    assert stats_a["average_time"] != stats_b["average_time"]


def test_average_calculation():
    """Verify average time is calculated correctly"""
    monitor = PerformanceMonitor()

    with monitor.track_operation("test"):
        time.sleep(0.01)

    with monitor.track_operation("test"):
        time.sleep(0.01)

    stats = monitor.get_operation_stats("test")

    assert stats["count"] == 2
    assert stats["average_time"] > 0.01


def test_performance_thresholds():
    """Verify performance threshold alerts"""
    monitor = PerformanceMonitor(threshold=0.05)

    # Fast operation (no alert)
    with monitor.track_operation("fast"):
        time.sleep(0.001)

    # Slow operation (alert triggered)
    with monitor.track_operation("slow"):
        time.sleep(0.1)

    stats = monitor.get_operation_stats("slow")

    assert stats["count"] == 1
    assert stats["total_time"] > monitor.threshold


def test_memory_tracking():
    """Verify memory usage is tracked"""
    monitor = PerformanceMonitor()

    with monitor.track_memory("memory_test"):
        # Allocate some memory
        data = [0] * 1000

    stats = monitor.get_memory_stats("memory_test")

    assert "max_memory_mb" in stats
    assert "peak_memory_mb" in stats


def test_system_metrics():
    """Verify system metrics (CPU, memory, disk) are captured"""
    monitor = PerformanceMonitor()

    metrics = monitor.get_system_metrics()

    assert "cpu_percent" in metrics
    assert "memory_percent" in metrics
    assert "disk_usage_percent" in metrics
    assert 0 <= metrics["cpu_percent"] <= 100
    assert 0 <= metrics["memory_percent"] <= 100
    assert 0 <= metrics["disk_usage_percent"] <= 100


def test_performance_report():
    """Verify performance report generation"""
    monitor = PerformanceMonitor()

    with monitor.track_operation("test"):
        time.sleep(0.01)

    report = monitor.generate_report()

    assert "operations" in report
    assert "system_metrics" in report
    assert "timestamp" in report


def test_performance_export():
    """Verify performance metrics can be exported"""
    monitor = PerformanceMonitor()

    with monitor.track_operation("test"):
        time.sleep(0.01)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        export_path = f.name

    try:
        monitor.export_metrics(export_path)

        assert os.path.exists(export_path)

        # Verify file is valid JSON
        with open(export_path, "r") as f:
            data = json.load(f)

        assert "operations" in data
    finally:
        os.unlink(export_path)


def test_reset_stats():
    """Verify stats can be reset"""
    monitor = PerformanceMonitor()

    with monitor.track_operation("test"):
        time.sleep(0.01)

    monitor.reset_stats()

    stats = monitor.get_operation_stats("test")

    assert stats["count"] == 0
    assert stats["total_time"] == 0


def test_concurrent_operations():
    """Verify tracking works for concurrent operations"""
    monitor = PerformanceMonitor()

    with monitor.track_operation("concurrent"):
        time.sleep(0.01)

    with monitor.track_operation("concurrent"):
        time.sleep(0.01)

    stats = monitor.get_operation_stats("concurrent")

    assert stats["count"] == 2
