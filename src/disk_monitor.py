"""
Disk Usage Monitoring Daemon
"""

import os
import json
import time
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime
import shutil


class DiskMonitor:
    """
    Disk usage monitoring daemon

    Features:
    - Get disk usage for filesystems
    - Calculate directory sizes
    - Continuous monitoring
    - Threshold alerts
    - Find large directories
    - Track usage trends
    - Export usage reports
    - Cleanup old measurements
    - Calculate growth rates
    """

    def __init__(self, threshold: float = 90.0, max_history: int = 100):
        """
        Initialize disk monitor

        Args:
            threshold: Disk usage percentage threshold for alerts (default: 90%)
            max_history: Maximum number of measurements to keep
        """
        self.threshold = threshold
        self.max_history = max_history
        self.usage_history = []
        self.monitoring = False
        self.monitor_thread = None
        self.alert_callback = None

    def get_disk_usage(self, path: str = "/") -> Dict:
        """
        Get disk usage for a path

        Args:
            path: Filesystem path to check (default: /)

        Returns:
            Dict with total_gb, used_gb, free_gb, usage_percent
        """
        try:
            usage = shutil.disk_usage(path)

            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)
            usage_percent = (usage.used / usage.total) * 100

            return {
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "usage_percent": round(usage_percent, 2),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"⚠️  Error getting disk usage: {e}")
            return {
                "total_gb": 0,
                "used_gb": 0,
                "free_gb": 0,
                "usage_percent": 0,
                "error": str(e),
            }

    def get_directory_size(self, directory: str) -> int:
        """
        Calculate total size of a directory

        Args:
            directory: Path to directory

        Returns:
            Size in bytes
        """
        total_size = 0

        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except OSError:
                        continue

            return total_size
        except Exception as e:
            print(f"⚠️  Error calculating directory size: {e}")
            return 0

    def start_monitoring(self, path: str = "/", interval: int = 60):
        """
        Start continuous monitoring in background thread

        Args:
            path: Filesystem path to monitor (default: /)
            interval: Check interval in seconds (default: 60)
        """
        if self.monitoring:
            print("⚠️  Monitoring already running")
            return

        self.monitoring = True

        def monitor_loop():
            while self.monitoring:
                self.record_measurement(path)
                time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        print(f"✓ Started monitoring {path} every {interval}s")

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.monitoring:
            return

        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("✓ Stopped monitoring")

    def record_measurement(self, path: str = "/"):
        """
        Record a disk usage measurement

        Args:
            path: Filesystem path to measure
        """
        usage = self.get_disk_usage(path)
        self.usage_history.append(usage)

        # Trim history to max_history
        if len(self.usage_history) > self.max_history:
            self.usage_history = self.usage_history[-self.max_history :]

        # Check threshold
        self.check_threshold(usage)

    def set_alert_callback(self, callback: Callable[[Dict], None]):
        """
        Set callback function for threshold alerts

        Args:
            callback: Function to call when threshold is exceeded
        """
        self.alert_callback = callback

    def check_threshold(self, usage: Optional[Dict] = None):
        """
        Check if threshold is exceeded and trigger alert

        Args:
            usage: Usage dict to check (uses latest if None)
        """
        if usage is None and self.usage_history:
            usage = self.usage_history[-1]

        if usage and usage["usage_percent"] >= self.threshold:
            alert = {
                "threshold": self.threshold,
                "usage_percent": usage["usage_percent"],
                "timestamp": usage["timestamp"],
            }

            print(
                f"🚨 Disk usage alert: {usage['usage_percent']}% >= {self.threshold}%"
            )

            if self.alert_callback:
                self.alert_callback(alert)

    def get_usage_history(self) -> List[Dict]:
        """Get all recorded usage measurements"""
        return self.usage_history

    def get_large_directories(
        self, root_path: str, min_size_mb: float = 100.0
    ) -> List[Dict]:
        """
        Find directories larger than minimum size

        Args:
            root_path: Root directory to search
            min_size_mb: Minimum size in MB

        Returns:
            List of directory dicts with path and size_mb
        """
        large_dirs = []

        try:
            for dirpath, dirnames, filenames in os.walk(root_path):
                # Calculate size
                total_size = 0
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except OSError:
                        continue

                # Convert to MB
                size_mb = total_size / (1024**2)

                if size_mb >= min_size_mb:
                    large_dirs.append(
                        {
                            "path": dirpath,
                            "size_mb": round(size_mb, 2),
                            "size_bytes": total_size,
                        }
                    )

            # Sort by size (largest first)
            large_dirs.sort(key=lambda x: x["size_mb"], reverse=True)

            return large_dirs[:20]  # Return top 20
        except Exception as e:
            print(f"⚠️  Error finding large directories: {e}")
            return []

    def get_usage_trend(self, days: int = 7) -> Dict:
        """
        Calculate disk usage trend over time

        Args:
            days: Number of days to analyze

        Returns:
            Dict with slope and direction (increasing/decreasing/stable)
        """
        if len(self.usage_history) < 2:
            return {"slope": 0.0, "direction": "insufficient_data"}

        # Get recent measurements
        recent = self.usage_history[-min(len(self.usage_history), 10) :]

        # Calculate slope
        values = [u["usage_percent"] for u in recent]
        x = list(range(len(values)))

        # Simple linear regression
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(xi * yi for xi, yi in zip(x, values))
        sum_x2 = sum(xi**2 for xi in x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)

        # Determine direction
        if slope > 0.1:
            direction = "increasing"
        elif slope < -0.1:
            direction = "decreasing"
        else:
            direction = "stable"

        return {
            "slope": round(slope, 4),
            "direction": direction,
            "data_points": n,
            "start_value": values[0],
            "end_value": values[-1],
        }

    def export_usage_report(self, export_path: str):
        """
        Export usage report to JSON file

        Args:
            export_path: Path to export file
        """
        report = {
            "usage_history": self.usage_history,
            "trend": self.get_usage_trend(),
            "threshold": self.threshold,
            "exported_at": datetime.now().isoformat(),
        }

        os.makedirs(os.path.dirname(export_path), exist_ok=True)

        with open(export_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"✓ Usage report exported to {export_path}")

    def get_disk_info(self, path: str = "/") -> Dict:
        """
        Get detailed disk information

        Args:
            path: Filesystem path

        Returns:
            Dict with detailed disk info
        """
        usage = shutil.disk_usage(path)

        return {
            "filesystem": path,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "total_gb": round(usage.total / (1024**3), 2),
            "used_gb": round(usage.used / (1024**3), 2),
            "free_gb": round(usage.free / (1024**3), 2),
            "usage_percent": round((usage.used / usage.total) * 100, 2),
        }

    def calculate_growth_rate(
        self, initial_usage: float, final_usage: float, days: int
    ) -> float:
        """
        Calculate growth rate

        Args:
            initial_usage: Initial usage percentage
            final_usage: Final usage percentage
            days: Number of days between measurements

        Returns:
            Growth rate in percent per day
        """
        if days == 0:
            return 0.0

        change = final_usage - initial_usage
        growth_rate = change / days

        return round(growth_rate, 4)
