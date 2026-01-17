"""
GDrive Executor - Extends ConfidenceExecutor for Google Drive operations

Features:
- Path router to detect gdrive: paths
- GDrive-specific execution (move, delete)
- Folder ID resolution from local paths
- Rollback support for GDrive operations
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime


class GDriveExecutor:
    """
    Executor for Google Drive file operations

    Features:
    - Execute actions on GDrive files
    - Resolve local paths to GDrive folder IDs
    - Rollback GDrive operations
    - Track GDrive execution history
    """

    def __init__(self, local_executor=None):
        """
        Initialize GDrive executor

        Args:
            local_executor: Optional ConfidenceExecutor for local operations
        """
        self.local_executor = local_executor
        self.gd_api = None
        self.gdrive_history = []
        self.folder_cache = {}  # folder_name -> folder_id
        self.stats = {
            "gdrive_actions": 0,
            "gdrive_executed": 0,
            "gdrive_failed": 0,
        }

        # Initialize GDrive API
        self._init_gdrive()

    def _init_gdrive(self):
        """Initialize Google Drive API connection"""
        try:
            from google_drive_api import GoogleDriveAPI

            self.gd_api = GoogleDriveAPI()
            if self.gd_api.authenticated:
                print("✓ GDrive Executor initialized")
                # Pre-load folder cache
                self._build_folder_cache()
            else:
                print("⚠️  GDrive API not authenticated, cloud operations disabled")
        except Exception as e:
            print(f"⚠️  Failed to initialize GDrive API: {e}")
            self.gd_api = None

    def _build_folder_cache(self):
        """Build cache of GDrive folder names to IDs"""
        if not self.gd_api:
            return

        try:
            folders = self.gd_api.list_files(
                query="mimeType='application/vnd.google-apps.folder'"
            )
            if folders:
                for f in folders:
                    self.folder_cache[f["name"]] = f["id"]
                print(f"  ✓ Cached {len(folders)} folders")
        except Exception as e:
            print(f"  ⚠️  Failed to build folder cache: {e}")

    def is_gdrive_path(self, path: str) -> bool:
        """Check if path is a GDrive path"""
        return path.startswith("gdrive:")

    def extract_file_id(self, gdrive_path: str) -> Optional[str]:
        """Extract file ID from gdrive: path"""
        if self.is_gdrive_path(gdrive_path):
            return gdrive_path.replace("gdrive:", "")
        return None

    def resolve_folder_id(self, folder_path: str) -> Optional[str]:
        """
        Resolve local folder path to GDrive folder ID

        Args:
            folder_path: Local-style path (e.g., "work/reports")

        Returns:
            GDrive folder ID or None
        """
        if not self.gd_api:
            return None

        # Extract folder name from path
        folder_name = os.path.basename(folder_path) or folder_path

        # Check cache first
        if folder_name in self.folder_cache:
            return self.folder_cache[folder_name]

        # Search in GDrive
        try:
            results = self.gd_api.search_files(
                query=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            )
            if results:
                folder_id = results[0]["id"]
                self.folder_cache[folder_name] = folder_id
                return folder_id
        except Exception as e:
            print(f"  ⚠️  Error resolving folder '{folder_name}': {e}")

        return None

    def create_folder(self, folder_path: str) -> Optional[str]:
        """
        Create folder in GDrive and return ID

        Args:
            folder_path: Local-style path (e.g., "work/reports/2024")

        Returns:
            GDrive folder ID or None
        """
        if not self.gd_api:
            return None

        try:
            # Create folder structure
            parts = folder_path.strip("/").split("/")
            parent_id = None

            for part in parts:
                # Check if folder exists
                if part in self.folder_cache:
                    parent_id = self.folder_cache[part]
                    continue

                # Create folder
                folder_id = self.gd_api.create_folder(part, parent_id)
                if folder_id:
                    self.folder_cache[part] = folder_id
                    parent_id = folder_id
                else:
                    return None

            return parent_id
        except Exception as e:
            print(f"  ⚠️  Error creating folder '{folder_path}': {e}")
            return None

    def execute_action(self, action: Dict) -> Dict:
        """
        Execute action - routes to local or GDrive executor

        Args:
            action: Action dict with type, file, confidence, target

        Returns:
            Result dict with executed status
        """
        file_path = action.get("file", "")

        if not file_path:
            return {"executed": False, "error": "No file path"}

        self.stats["gdrive_actions"] += 1

        if self.is_gdrive_path(file_path):
            return self._execute_gdrive_action(action)
        elif self.local_executor:
            return self.local_executor.execute_action(action)
        else:
            return {"executed": False, "error": "No executor for local path"}

    def _execute_gdrive_action(self, action: Dict) -> Dict:
        """Execute action on GDrive file"""
        file_id = self.extract_file_id(action.get("file", ""))
        action_type = action.get("type", "MOVE")
        target = action.get("target", "")

        if not file_id:
            return {"executed": False, "error": "Invalid GDrive path"}

        try:
            if action_type == "MOVE":
                # Resolve target folder
                folder_id = self.resolve_folder_id(target)
                if not folder_id:
                    # Try to create folder
                    folder_id = self.create_folder(target)

                if not folder_id:
                    return {
                        "executed": False,
                        "error": f"Could not resolve target: {target}",
                    }

                success = self.gd_api.move_file(file_id, folder_id)

            elif action_type == "DELETE":
                success = self.gd_api.delete_file(file_id)

            else:
                return {
                    "executed": False,
                    "error": f"Unsupported action type: {action_type}",
                }

            if success:
                self.stats["gdrive_executed"] += 1
                result = {
                    "executed": True,
                    "file_id": file_id,
                    "action": action_type,
                    "target": target,
                    "target_id": folder_id if action_type == "MOVE" else None,
                    "executed_at": datetime.now().isoformat(),
                }
                self.gdrive_history.append(result)
                return result
            else:
                self.stats["gdrive_failed"] += 1
                return {"executed": False, "error": "API call failed"}

        except Exception as e:
            self.stats["gdrive_failed"] += 1
            return {"executed": False, "error": str(e)}

    def rollback_action(self, action_id: int) -> bool:
        """
        Rollback a GDrive action

        Args:
            action_id: Action ID to rollback

        Returns:
            True if successful
        """
        action = next(
            (a for a in self.gdrive_history if a.get("id") == action_id), None
        )

        if not action:
            return False

        try:
            file_id = action.get("file_id")
            original_parent = action.get("original_parent")

            if action.get("action") == "MOVE" and file_id and original_parent:
                # Move back to original folder
                success = self.gd_api.move_file(file_id, original_parent)
                if success:
                    self.stats["gdrive_actions"] += 1
                    return True

            elif action.get("action") == "DELETE":
                # Cannot easily undo delete without backup
                print("  ⚠️  Cannot rollback delete operation")
                return False

        except Exception as e:
            print(f"  ⚠️  Error rolling back action {action_id}: {e}")
            return False

        return False

    def batch_execute(self, actions: List[Dict]) -> List[Dict]:
        """Execute multiple actions"""
        results = []
        for action in actions:
            result = self.execute_action(action)
            results.append(result)
        return results

    def get_statistics(self) -> Dict:
        """Get executor statistics"""
        stats = self.stats.copy()
        if self.local_executor:
            local_stats = self.local_executor.get_statistics()
            stats.update(
                {
                    "local_total": local_stats.get("total_actions", 0),
                    "local_executed": local_stats.get("executed_actions", 0),
                }
            )
        return stats

    def get_history(self) -> List[Dict]:
        """Get GDrive execution history"""
        return self.gdrive_history.copy()


def create_unified_executor() -> GDriveExecutor:
    """
    Create unified executor with local and GDrive support

    Returns:
        GDriveExecutor with local confidence_executor
    """
    from confidence_executor import ConfidenceExecutor

    local = ConfidenceExecutor()
    return GDriveExecutor(local_executor=local)
