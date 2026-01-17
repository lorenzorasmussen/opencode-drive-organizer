"""
Desktop Notifications for Google Drive Organizer

Features:
- Cross-platform notification support
- macOS Notification Center
- Linux libnotify
- Windows toast
- Sound alerts
"""

import os
import subprocess
from typing import Optional


class NotificationManager:
    """Cross-platform notification manager"""

    def __init__(self, enabled: bool = False, sound: bool = True):
        """
        Initialize notification manager

        Args:
            enabled: Enable notifications
            sound: Play sound with notifications
        """
        self.enabled = enabled
        self.sound = sound
        self.platform = self._detect_platform()

    def _detect_platform(self) -> str:
        """Detect current platform"""
        if os.sys.platform == "darwin":
            return "macos"
        elif os.sys.platform == "linux":
            return "linux"
        elif os.sys.platform == "win32":
            return "windows"
        return "unknown"

    def notify(
        self,
        title: str,
        message: str,
        subtitle: Optional[str] = None,
        sound_name: Optional[str] = None,
    ) -> bool:
        """
        Send a notification

        Args:
            title: Notification title
            message: Notification message
            subtitle: Optional subtitle (macOS)
            sound_name: Optional sound to play

        Returns:
            True if notification was sent
        """
        if not self.enabled:
            return False

        try:
            if self.platform == "macos":
                return self._notify_macos(title, message, subtitle, sound_name)
            elif self.platform == "linux":
                return self._notify_linux(title, message)
            elif self.platform == "windows":
                return self._notify_windows(title, message)
        except Exception as e:
            print(f"⚠️  Notification error: {e}")
        return False

    def _notify_macos(
        self,
        title: str,
        message: str,
        subtitle: Optional[str] = None,
        sound_name: Optional[str] = None,
    ) -> bool:
        """Send macOS notification"""
        try:
            cmd = [
                "osascript",
                "-e",
                f'display notification "{message}" with title "{title}"',
            ]
            if subtitle:
                cmd[2] = (
                    f'display notification "{message}" with title "{title}" '
                    f'subtitle "{subtitle}"'
                )
            if sound_name or self.sound:
                cmd[2] += f' sound name "{sound_name or "default"}"'

            subprocess.run(cmd, capture_output=True)
            return True
        except Exception:
            return False

    def _notify_linux(self, title: str, message: str) -> bool:
        """Send Linux notification"""
        try:
            cmd = ["notify-send", title, message]
            subprocess.run(cmd, capture_output=True)
            return True
        except Exception:
            return False

    def _notify_windows(self, title: str, message: str) -> bool:
        """Send Windows notification"""
        try:
            from win10toast import ToastNotifier

            toaster = ToastNotifier()
            toaster.show_toast(title, message, duration=5)
            return True
        except Exception:
            return False

    def play_sound(self, sound_type: str = "default") -> bool:
        """Play a sound"""
        if not self.sound:
            return False

        try:
            if self.platform == "macos":
                sounds = {
                    "default": "Glass",
                    "success": "Blow",
                    "error": "Basso",
                    "warning": "Funk",
                }
                sound = sounds.get(sound_type, "Glass")
                subprocess.run(
                    ["afplay", f"/System/Library/Sounds/{sound}.aiff"],
                    capture_output=True,
                )
                return True
            elif self.platform == "linux":
                subprocess.run(
                    [
                        "paplay",
                        "/usr/share/sounds/ubuntu/stereo/dialog-information.ogg",
                    ],
                    capture_output=True,
                )
                return True
        except Exception:
            pass
        return False

    def operation_complete(
        self,
        operation: str,
        files_processed: int,
        success: bool = True,
    ) -> None:
        """Send operation complete notification"""
        status = "✓" if success else "⚠️"
        self.notify(
            f"{status} {operation} Complete",
            f"Processed {files_processed} files",
            subtitle="Google Drive Organizer",
        )

    def error_occurred(self, error: str) -> None:
        """Send error notification"""
        self.notify(
            "⚠️ Operation Error",
            error,
            subtitle="Google Drive Organizer",
        )


def get_notifications(enabled: bool = False, sound: bool = True) -> NotificationManager:
    """Get notification manager instance"""
    return NotificationManager(enabled=enabled, sound=sound)
