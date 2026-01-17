"""
Undo Manager - Enhanced rollback with selective undo

Features:
- Selective undo by action ID
- Batch undo
- Preview undo operations
- Undo history browser
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class UndoManager:
    """Enhanced undo manager with selective rollback"""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize undo manager

        Args:
            data_dir: Directory for undo data
        """
        self.data_dir = data_dir
        self.history_file = os.path.join(data_dir, "undo_history.json")
        self.history: List[Dict] = []
        self._load_history()

    def _load_history(self) -> None:
        """Load undo history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    data = json.load(f)
                    self.history = data.get("actions", [])
            except Exception:
                self.history = []

    def _save_history(self) -> None:
        """Save undo history to file"""
        os.makedirs(self.data_dir, exist_ok=True)
        data = {
            "actions": self.history,
            "saved_at": datetime.now().isoformat(),
        }
        with open(self.history_file, "w") as f:
            json.dump(data, f, indent=2)

    def record_action(
        self,
        action_type: str,
        source: str,
        destination: str,
        metadata: Optional[Dict] = None,
    ) -> int:
        """
        Record an action for potential undo

        Args:
            action_type: Type of action (move, delete, etc.)
            source: Source path
            destination: Destination path
            metadata: Additional metadata

        Returns:
            Action ID
        """
        action_id = len(self.history)
        action = {
            "id": action_id,
            "type": action_type,
            "source": source,
            "destination": destination,
            "timestamp": datetime.now().isoformat(),
            "status": "executed",
            "metadata": metadata or {},
        }
        self.history.append(action)
        self._save_history()
        return action_id

    def undo(
        self,
        action_id: Optional[int] = None,
        batch: Optional[List[int]] = None,
        preview: bool = False,
    ) -> Dict:
        """
        Undo actions

        Args:
            action_id: Specific action to undo
            batch: List of action IDs to undo
            preview: Just show what would be undone

        Returns:
            Result dict with undone actions
        """
        if batch:
            action_ids = batch
        elif action_id is not None:
            action_ids = [action_id]
        else:
            return {"success": False, "error": "No action specified"}

        undone = []
        failed = []

        for aid in action_ids:
            action = next((a for a in self.history if a["id"] == aid), None)
            if not action:
                failed.append({"id": aid, "error": "Not found"})
                continue

            if action.get("status") != "executed":
                failed.append({"id": aid, "error": "Already undone"})
                continue

            if preview:
                undone.append(
                    {
                        "id": aid,
                        "action": action["type"],
                        "source": action["source"],
                        "destination": action["destination"],
                        "preview": True,
                    }
                )
            else:
                success = self._execute_undo(action)
                if success:
                    action["status"] = "undone"
                    action["undone_at"] = datetime.now().isoformat()
                    undone.append(
                        {
                            "id": aid,
                            "action": action["type"],
                            "source": action["source"],
                            "destination": action["destination"],
                        }
                    )
                else:
                    failed.append({"id": aid, "error": "Undo failed"})

        if not preview:
            self._save_history()

        return {
            "success": True if len(failed) == 0 else partial,
            "undone_count": len(undone),
            "failed_count": len(failed),
            "undone": undone,
            "failed": failed,
        }

    def _execute_undo(self, action: Dict) -> bool:
        """Execute undo for a single action"""
        try:
            import shutil

            if action["type"] == "move":
                # Move back to source
                if os.path.exists(action["destination"]):
                    if os.path.exists(action["source"]):
                        # Source exists, create backup
                        backup = action["source"] + ".backup"
                        shutil.move(action["source"], backup)
                    shutil.move(action["destination"], action["source"])
                    return True

            elif action["type"] == "copy":
                # Remove copied file
                if os.path.exists(action["destination"]):
                    if os.path.isdir(action["destination"]):
                        shutil.rmtree(action["destination"])
                    else:
                        os.remove(action["destination"])
                    return True

            elif action["type"] == "delete":
                # Restore from backup
                backup_dir = os.path.join(self.data_dir, "backups")
                backup_file = os.path.join(
                    backup_dir, f'action_{action["id"]}_{os.path.basename(action["source"]}'
                )
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, action["source"])
                    return True

        except Exception as e:
            print(f"⚠️  Undo error: {e}")

        return False

    def preview_undo(self, action_id: int) -> Dict:
        """Preview what undo would do"""
        return self.undo(action_id=action_id, preview=True)

    def get_history(
        self,
        action_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict]:
        """Get undo history with filtering"""
        filtered = self.history
        if action_type:
            filtered = [a for a in filtered if a.get("type") == action_type]
        return filtered[offset : offset + limit]

    def get_action(self, action_id: int) -> Optional[Dict]:
        """Get a specific action"""
        return next((a for a in self.history if a["id"] == action_id), None)

    def clear_history(self, before: Optional[datetime] = None) -> int:
        """Clear history, optionally before a date"""
        if before:
            original_count = len(self.history)
            self.history = [a for a in self.history if datetime.fromisoformat(a["timestamp"]) >= before]
            cleared = original_count - len(self.history)
        else:
            cleared = len(self.history)
            self.history = []

        self._save_history()
        return cleared

    def get_statistics(self) -> Dict:
        """Get undo statistics"""
        by_type = {}
        for action in self.history:
            t = action.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1

        return {
            "total_actions": len(self.history),
            "by_type": by_type,
            "undone_count": sum(1 for a in self.history if a.get("status") == "undone"),
            "executed_count": sum(1 for a in self.history if a.get("status") == "executed"),
        }

    def browse_history(self) -> str:
        """Generate readable history summary"""
        lines = ["=== Undo History ===", ""]
        for action in reversed(self.history[-20:]):
            status = "✓" if action.get("status") == "executed" else "↩️"
            timestamp = action.get("timestamp", "")[:19].replace("T", " ")
            lines.append(
                f"{status} [{action['id']:3d}] {timestamp} {action['type']:6s} {action['source'][-40:]} -> {action['destination'][-40:]}"
            )
        return "\n".join(lines)


def get_undo_manager(data_dir: str = "data") -> UndoManager:
    """Get undo manager instance"""
    return UndoManager(data_dir)
