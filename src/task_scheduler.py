"""
Task Scheduler for Google Drive Organizer

Features:
- Schedule organize runs (daily, weekly, etc.)
- Cron-like syntax support
- Background scheduling
- Log rotation
"""

import os
import json
import time
import sched
import threading
import signal
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional
from pathlib import Path


class TaskScheduler:
    """Task scheduler with cron-like syntax"""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize scheduler

        Args:
            data_dir: Directory for schedule data
        """
        self.data_dir = data_dir
        self.schedule_file = os.path.join(data_dir, "scheduler.json")
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.jobs: Dict[str, Dict] = {}
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self._load_schedule()

    def _load_schedule(self) -> None:
        """Load scheduled jobs from file"""
        if os.path.exists(self.schedule_file):
            try:
                with open(self.schedule_file, "r") as f:
                    data = json.load(f)
                    self.jobs = data.get("jobs", {})
            except Exception:
                self.jobs = {}

    def _save_schedule(self) -> None:
        """Save scheduled jobs to file"""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.schedule_file, "w") as f:
            json.dump(
                {"jobs": self.jobs, "saved_at": datetime.now().isoformat()},
                f,
                indent=2,
            )

    def _parse_time(self, time_str: str) -> datetime:
        """Parse time string to datetime"""
        now = datetime.now()
        if time_str.startswith("+"):
            # Relative time (e.g., "+1h", "+30m")
            delta = self._parse_delta(time_str[1:])
            return now + delta
        else:
            # Fixed time (e.g., "09:00", "14:30")
            parts = time_str.split(":")
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    def _parse_delta(self, delta_str: str) -> timedelta:
        """Parse delta string (e.g., '1h30m', '2d')"""
        import re

        pattern = r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?"
        match = re.match(pattern, delta_str)
        if match:
            days = int(match.group(1) or 0)
            hours = int(match.group(2) or 0)
            minutes = int(match.group(3) or 0)
            seconds = int(match.group(4) or 0)
            return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return timedelta(0)

    def _parse_interval(self, interval: str) -> timedelta:
        """Parse interval string (e.g., '1h', '30m', '1d')"""
        if interval.endswith("s"):
            return timedelta(seconds=int(interval[:-1]))
        elif interval.endswith("m"):
            return timedelta(minutes=int(interval[:-1]))
        elif interval.endswith("h"):
            return timedelta(hours=int(interval[:-1]))
        elif interval.endswith("d"):
            return timedelta(days=int(interval[:-1]))
        return timedelta(hours=1)

    def add_job(
        self,
        name: str,
        command: str,
        schedule: str,
        enabled: bool = True,
        args: Optional[List[str]] = None,
    ) -> Dict:
        """
        Add a scheduled job

        Args:
            name: Job name
            command: Command to run
            schedule: Schedule (e.g., "09:00" for daily, "30m" for interval)
            enabled: Job is enabled
            args: Additional arguments

        Returns:
            Job configuration dict
        """
        job = {
            "name": name,
            "command": command,
            "schedule": schedule,
            "enabled": enabled,
            "args": args or [],
            "created_at": datetime.now().isoformat(),
            "last_run": None,
            "next_run": None,
            "run_count": 0,
        }

        if enabled:
            job["next_run"] = self._calculate_next_run(schedule).isoformat()

        self.jobs[name] = job
        self._save_schedule()

        if enabled:
            self._schedule_job(name)

        print(f"✓ Added job: {name} ({schedule})")
        return job

    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time from schedule"""
        now = datetime.now()

        # Interval-based schedule
        if schedule.startswith("every "):
            interval = self._parse_interval(schedule.split(" ")[1])
            return now + interval

        # Daily at specific time
        if ":" in schedule and len(schedule.split(":")) <= 2:
            next_run = self._parse_time(schedule)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run

        # Relative time
        if schedule.startswith("+"):
            return now + self._parse_delta(schedule[1:])

        return now + timedelta(hours=1)

    def _schedule_job(self, name: str) -> None:
        """Schedule a job to run"""
        job = self.jobs.get(name)
        if not job or not job.get("enabled"):
            return

        next_run_str = job.get("next_run")
        if not next_run_str:
            return

        try:
            next_run = datetime.fromisoformat(next_run_str)
            delay = (next_run - datetime.now()).total_seconds()

            if delay > 0:
                self.scheduler.enter(
                    delay,
                    1,
                    self._run_job,
                    argument=(name,),
                )
        except Exception as e:
            print(f"⚠️  Error scheduling job {name}: {e}")

    def _run_job(self, name: str) -> None:
        """Execute a scheduled job"""
        job = self.jobs.get(name)
        if not job:
            return

        print(f"\n🕐 Running scheduled job: {name}")
        print(f"   Command: {job['command']}")

        try:
            # Import and run command
            from cli_interface import CLI

            cli = CLI()
            args = job["command"].split() + (job.get("args") or [])
            result = cli.run_command(args)

            job["last_run"] = datetime.now().isoformat()
            job["run_count"] = job.get("run_count", 0) + 1

            # Calculate next run
            next_run = self._calculate_next_run(job["schedule"])
            job["next_run"] = next_run.isoformat()

            print(f"   Result: {result.get('status', 'unknown')}")

        except Exception as e:
            print(f"   Error: {e}")
            job["last_run"] = datetime.now().isoformat()
            job["last_error"] = str(e)

        self._save_schedule()

        # Schedule next run
        self._schedule_job(name)

    def start(self) -> None:
        """Start the scheduler"""
        if self.running:
            return

        self.running = True
        self.scheduler_thread = threading.Thread(
            target=self._run_scheduler, daemon=True
        )
        self.scheduler_thread.start()
        print("✓ Scheduler started")

        # Schedule all enabled jobs
        for name in list(self.jobs.keys()):
            if self.jobs[name].get("enabled"):
                self._schedule_job(name)

    def _run_scheduler(self) -> None:
        """Run the scheduler loop"""
        while self.running:
            try:
                self.scheduler.run(blocking=False)
            except Exception:
                pass
            time.sleep(1)

    def stop(self) -> None:
        """Stop the scheduler"""
        self.running = False
        self.scheduler.empty()
        print("✓ Scheduler stopped")

    def list_jobs(self) -> List[Dict]:
        """List all scheduled jobs"""
        return list(self.jobs.values())

    def enable_job(self, name: str) -> bool:
        """Enable a job"""
        if name in self.jobs:
            self.jobs[name]["enabled"] = True
            self.jobs[name]["next_run"] = self._calculate_next_run(
                self.jobs[name]["schedule"]
            ).isoformat()
            self._save_schedule()
            self._schedule_job(name)
            return True
        return False

    def disable_job(self, name: str) -> bool:
        """Disable a job"""
        if name in self.jobs:
            self.jobs[name]["enabled"] = False
            self.jobs[name].pop("next_run", None)
            self._save_schedule()
            return True
        return False

    def remove_job(self, name: str) -> bool:
        """Remove a job"""
        if name in self.jobs:
            del self.jobs[name]
            self._save_schedule()
            return True
        return False

    def run_now(self, name: str) -> bool:
        """Run a job immediately"""
        if name in self.jobs:
            threading.Thread(target=self._run_job, args=(name,), daemon=True).start()
            return True
        return False

    def get_status(self) -> Dict:
        """Get scheduler status"""
        now = datetime.now()
        upcoming = []

        for name, job in self.jobs.items():
            if job.get("enabled") and job.get("next_run"):
                try:
                    next_run = datetime.fromisoformat(job["next_run"])
                    if next_run > now:
                        upcoming.append(
                            {
                                "name": name,
                                "next_run": job["next_run"],
                                "schedule": job["schedule"],
                            }
                        )
                except Exception:
                    pass

        upcoming.sort(key=lambda x: x["next_run"])

        return {
            "running": self.running,
            "jobs_count": len(self.jobs),
            "enabled_count": sum(1 for j in self.jobs.values() if j.get("enabled")),
            "upcoming": upcoming[:5],
        }


def create_scheduler(data_dir: str = "data") -> TaskScheduler:
    """Create scheduler instance"""
    return TaskScheduler(data_dir)
