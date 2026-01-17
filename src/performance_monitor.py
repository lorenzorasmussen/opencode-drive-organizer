"""
Performance Monitoring System for tracking operation metrics
"""

import os
import time
import json
from typing import Dict, List, Optional
from datetime import datetime
import psutil


class PerformanceMonitor:
    """
    Performance monitoring system for tracking operation metrics

    Features:
    - Operation timing and statistics
    - Memory usage tracking
    - System metrics (CPU, memory, disk)
    - Performance threshold alerts
    - Report generation
    - Metrics export to JSON
    """

    def __init__(self, threshold: float = 1.0):
        """
        Initialize performance monitor

        Args:
            threshold: Performance threshold in seconds for alerts
        """
        self.threshold = threshold
        self.operation_stats = {}
        self.memory_stats = {}
        self.alerts = []

    def track_operation(self, operation_name: str):
        """
        Context manager to track operation performance

        Args:
            operation_name: Name of the operation to track

        Yields:
            None
        """

        class OperationTracker:
            def __init__(self, monitor, name):
                self.monitor = monitor
                self.name = name
                self.start_time = None

            def __enter__(self):
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                end_time = time.time()
                duration = end_time - self.start_time

                self.monitor._record_operation(self.name, duration)
                return False

        return OperationTracker(self, operation_name)

    def _record_operation(self, operation_name: str, duration: float):
        """Record operation execution time"""
        if operation_name not in self.operation_stats:
            self.operation_stats[operation_name] = {
                "count": 0,
                "total_time": 0,
                "max_time": 0,
                "min_time": float("inf"),
                "times": [],
            }

        stats = self.operation_stats[operation_name]
        stats["count"] += 1
        stats["total_time"] += duration
        stats["max_time"] = max(stats["max_time"], duration)
        stats["min_time"] = min(stats["min_time"], duration)
        stats["average_time"] = stats["total_time"] / stats["count"]
        stats["times"].append(duration)

        # Check threshold
        if duration > self.threshold:
            self.alerts.append(
                {
                    "operation": operation_name,
                    "duration": duration,
                    "threshold": self.threshold,
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def track_memory(self, operation_name: str):
        """
        Context manager to track memory usage

        Args:
            operation_name: Name of the operation to track

        Yields:
            None
        """

        class MemoryTracker:
            def __init__(self, monitor, name):
                self.monitor = monitor
                self.name = name
                self.process = psutil.Process()
                self.start_memory = None

            def __enter__(self):
                self.start_memory = self.process.memory_info().rss / (1024 * 1024)
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                end_memory = self.process.memory_info().rss / (1024 * 1024)
                memory_delta = end_memory - self.start_memory

                self.monitor._record_memory(self.name, memory_delta, end_memory)
                return False

        return MemoryTracker(self, operation_name)

    def _record_memory(self, operation_name: str, delta_mb: float, peak_mb: float):
        """Record memory usage for operation"""
        if operation_name not in self.memory_stats:
            self.memory_stats[operation_name] = {
                "count": 0,
                "max_memory_mb": 0,
                "peak_memory_mb": 0,
            }

        stats = self.memory_stats[operation_name]
        stats["count"] += 1
        stats["max_memory_mb"] = max(stats["max_memory_mb"], delta_mb)
        stats["peak_memory_mb"] = max(stats["peak_memory_mb"], peak_mb)

    def get_operation_stats(self, operation_name: str) -> Dict:
        """Get statistics for a specific operation"""
        return self.operation_stats.get(
            operation_name,
            {
                "count": 0,
                "total_time": 0,
                "average_time": 0,
                "max_time": 0,
                "min_time": 0,
            },
        )

    def get_memory_stats(self, operation_name: str) -> Dict:
        """Get memory statistics for a specific operation"""
        return self.memory_stats.get(
            operation_name, {"count": 0, "max_memory_mb": 0, "peak_memory_mb": 0}
        )

    def get_system_metrics(self) -> Dict:
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage("/")

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_info.percent,
                "memory_used_mb": memory_info.used / (1024 * 1024),
                "memory_available_mb": memory_info.available / (1024 * 1024),
                "disk_usage_percent": disk_info.percent,
                "disk_used_gb": disk_info.used / (1024**3),
                "disk_free_gb": disk_info.free / (1024**3),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"⚠️  Error getting system metrics: {e}")
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_usage_percent": 0,
                "error": str(e),
            }

    def generate_report(self) -> Dict:
        """Generate performance report"""
        system_metrics = self.get_system_metrics()

        # Calculate aggregate stats
        total_operations = sum(
            stats["count"] for stats in self.operation_stats.values()
        )
        total_time = sum(stats["total_time"] for stats in self.operation_stats.values())

        return {
            "operations": self.operation_stats,
            "memory": self.memory_stats,
            "system_metrics": system_metrics,
            "alerts": self.alerts,
            "summary": {
                "total_operations": total_operations,
                "total_time": total_time,
                "average_time": total_time / total_operations
                if total_operations > 0
                else 0,
            },
            "timestamp": datetime.now().isoformat(),
        }

    def export_metrics(self, export_path: str):
        """Export metrics to JSON file"""
        report = self.generate_report()

        os.makedirs(os.path.dirname(export_path), exist_ok=True)

        with open(export_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✓ Metrics exported to {export_path}")

    def reset_stats(self):
        """Reset all statistics"""
        self.operation_stats = {}
        self.memory_stats = {}
        self.alerts = []

    def get_alerts(self) -> List[Dict]:
        """Get all performance threshold alerts"""
        return self.alerts

    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
