"""
Confidence-Based Executor with Rollback
"""

import os
import json
import shutil
from typing import Dict, List, Optional
from datetime import datetime


class ConfidenceExecutor:
    """
    Confidence-based executor with rollback capability

    Features:
    - Execute actions based on confidence
    - Automatic execution for high confidence
    - Manual review for medium confidence
    - Skip low confidence actions
    - Rollback executed actions
    - Batch execution
    - Execution history
    - Action validation
    - Statistics tracking
    """

    def __init__(self, thresholds: Optional[Dict] = None):
        """
        Initialize confidence executor

        Args:
            thresholds: Confidence thresholds (auto_execute, review, skip)
        """
        self.thresholds = thresholds or {
            "auto_execute": 0.9,
            "review": 0.5,
            "skip": 0.5,
        }
        self.execution_history = []
        self.stats = {
            "total_actions": 0,
            "executed_actions": 0,
            "skipped_actions": 0,
            "rollback_actions": 0,
        }

        # Create backup directory
        import os

        os.makedirs("data/rollbacks", exist_ok=True)
        self.execution_history = []
        self.stats = {
            "total_actions": 0,
            "executed_actions": 0,
            "skipped_actions": 0,
            "rollback_actions": 0,
        }

    def execute_action(self, action: Dict) -> Dict:
        """
        Execute a single action based on confidence

        Args:
            action: Action dict with type, file, confidence

        Returns:
            Result dict with executed status and method
        """
        self.stats["total_actions"] += 1

        confidence = action.get("confidence", 0.5)
        action_type = action.get("type")

        # Determine execution method
        if confidence >= self.thresholds["auto_execute"]:
            method = "automatic"
            executed = self._execute_automatic(action)
        elif confidence >= self.thresholds.get("review", 0.5):
            method = "manual_review"
            executed = False
        else:
            method = "skipped"
            executed = False

        result = {
            "id": len(self.execution_history),
            "action": action,
            "confidence": confidence,
            "method": method,
            "executed": executed,
            "executed_at": datetime.now().isoformat(),
        }

        self.execution_history.append(result)

        if executed:
            self.stats["executed_actions"] += 1
        else:
            self.stats["skipped_actions"] += 1

        return result

    def _execute_automatic(self, action: Dict) -> bool:
        """
        Execute action automatically

        Args:
            action: Action dict

        Returns:
            True if successful, False otherwise
        """
        action_type = action.get("type")
        file_path = action.get("file")

        if not file_path:
            return False

        try:
            if action_type == "DELETE":
                if os.path.exists(file_path):
                    # Backup file before deletion
                    action_id = len(self.execution_history)
                    self._backup_file(file_path, action_id)
                    os.remove(file_path)
                    return True

            elif action_type == "MOVE":
                target = action.get("target")
                if target:
                    shutil.move(file_path, target)
                    return True

            elif action_type == "COPY":
                target = action.get("target")
                if target:
                    shutil.copy2(file_path, target)
                    return True

            return False

        except Exception as e:
            print(f"⚠️  Error executing action: {e}")
            return False

        except Exception as e:
            print(f"⚠️  Error executing action: {e}")
            return False

    def _backup_file(self, file_path: str, action_id: int):
        """
        Backup file before execution

        Args:
            file_path: Path to file
            action_id: Action ID
        """
        backup_dir = "data/rollbacks"
        os.makedirs(backup_dir, exist_ok=True)

        backup_path = os.path.join(
            backup_dir, f"action_{action_id}_{os.path.basename(file_path)}"
        )

        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)

    def rollback_action(self, action_id: int) -> bool:
        """
        Rollback an executed action

        Args:
            action_id: Action ID to rollback

        Returns:
            True if successful, False otherwise
        """
        action = next((a for a in self.execution_history if a["id"] == action_id), None)

        if not action or not action["executed"]:
            return False

        action_data = action["action"]
        action_type = action_data.get("type")

        try:
            if action_type == "DELETE":
                # Restore from backup
                backup_dir = "data/rollbacks"
                backup_path = os.path.join(
                    backup_dir,
                    f"action_{action_id}_{os.path.basename(action_data['file'])}",
                )

                if os.path.exists(backup_path):
                    # Move back to original location
                    shutil.copy2(backup_path, action_data["file"])
                    return True

            return False

        except Exception as e:
            print(f"⚠️  Error rolling back action: {e}")
            return False

    def batch_execute(self, actions: List[Dict]) -> List[Dict]:
        """
        Execute multiple actions

        Args:
            actions: List of action dicts

        Returns:
            List of result dicts
        """
        results = []

        for action in actions:
            result = self.execute_action(action)
            results.append(result)

        return results

    def get_execution_history(self) -> List[Dict]:
        """Get execution history"""
        return self.execution_history.copy()

    def clear_history(self):
        """Clear execution history"""
        self.execution_history = []

    def validate_action(self, action: Dict) -> bool:
        """
        Validate action before execution

        Args:
            action: Action dict

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["type", "file", "confidence"]

        if not all(field in action for field in required_fields):
            return False

        if not isinstance(action.get("confidence"), (int, float)):
            return False

        if not 0 <= action.get("confidence", 0) <= 1:
            return False

        return True

    def get_statistics(self) -> Dict:
        """Get executor statistics"""
        return self.stats.copy()

    def export_history(self, export_path: str):
        """
        Export execution history to JSON

        Args:
            export_path: Path to export file
        """
        data = {
            "history": self.execution_history,
            "statistics": self.stats,
            "thresholds": self.thresholds,
            "exported_at": datetime.now().isoformat(),
        }

        os.makedirs(os.path.dirname(export_path), exist_ok=True)

        with open(export_path, "w") as f:
            json.dump(data, f, indent=2)
