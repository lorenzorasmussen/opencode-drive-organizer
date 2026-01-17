"""
Pattern Sharing - Export and import learning patterns

Features:
- Export patterns to JSON/YAML
- Import patterns from files
- Share patterns between users
- Pattern versioning
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


class PatternSharer:
    """Export and import learning patterns"""

    def __init__(self, patterns_dir: str = "data/patterns"):
        """
        Initialize pattern sharer

        Args:
            patterns_dir: Directory for pattern exports
        """
        self.patterns_dir = patterns_dir
        os.makedirs(patterns_dir, exist_ok=True)

    def export_patterns(
        self,
        patterns: List[Dict],
        name: str,
        format: str = "json",
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Export patterns to file

        Args:
            patterns: List of pattern dictionaries
            name: Export name
            format: Export format (json, yaml)
            metadata: Optional metadata

        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.{format}"
        filepath = os.path.join(self.patterns_dir, filename)

        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "name": name,
            "pattern_count": len(patterns),
            "metadata": metadata or {},
            "patterns": patterns,
        }

        try:
            if format == "json":
                with open(filepath, "w") as f:
                    json.dump(export_data, f, indent=2)
            elif format == "yaml":
                import yaml

                with open(filepath, "w") as f:
                    yaml.dump(export_data, f, default_flow_style=False, indent=2)

            print(f"✓ Exported {len(patterns)} patterns to {filepath}")
            return filepath

        except Exception as e:
            print(f"⚠️  Export error: {e}")
            return ""

    def import_patterns(
        self,
        filepath: str,
        merge_strategy: str = "append",
    ) -> List[Dict]:
        """
        Import patterns from file

        Args:
            filepath: Path to import file
            merge_strategy: How to handle duplicates (append, replace, skip)

        Returns:
            List of imported patterns
        """
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filepath}")
            return []

        try:
            if filepath.endswith(".json"):
                with open(filepath, "r") as f:
                    data = json.load(f)
            elif filepath.endswith(".yaml") or filepath.endswith(".yml"):
                import yaml

                with open(filepath, "r") as f:
                    data = yaml.safe_load(f)
            else:
                print(f"⚠️  Unsupported format: {filepath}")
                return []

            patterns = data.get("patterns", [])
            print(f"✓ Imported {len(patterns)} patterns from {filepath}")
            return patterns

        except Exception as e:
            print(f"⚠️  Import error: {e}")
            return []

    def export_to_clipboard(self, patterns: List[Dict]) -> str:
        """Export patterns to clipboard (JSON string)"""
        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "pattern_count": len(patterns),
            "patterns": patterns,
        }
        return json.dumps(export_data, indent=2)

    def import_from_clipboard(self, clipboard_data: str) -> List[Dict]:
        """Import patterns from clipboard"""
        try:
            data = json.loads(clipboard_data)
            patterns = data.get("patterns", [])
            print(f"✓ Imported {len(patterns)} patterns from clipboard")
            return patterns
        except Exception as e:
            print(f"⚠️  Clipboard import error: {e}")
            return []

    def list_exports(self) -> List[Dict]:
        """List all pattern exports"""
        exports = []
        if os.path.exists(self.patterns_dir):
            for f in os.listdir(self.patterns_dir):
                if f.endswith((".json", ".yaml", ".yml")):
                    filepath = os.path.join(self.patterns_dir, f)
                    stat = os.stat(filepath)
                    exports.append(
                        {
                            "filename": f,
                            "path": filepath,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime
                            ).isoformat(),
                        }
                    )
        return sorted(exports, key=lambda x: x["modified"], reverse=True)

    def delete_export(self, filename: str) -> bool:
        """Delete an export file"""
        filepath = os.path.join(self.patterns_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"✓ Deleted {filename}")
            return True
        return False

    def create_template(self, name: str, category: str) -> str:
        """Create a pattern template file"""
        template = {
            "version": "1.0",
            "name": name,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "patterns": [
                {
                    "src_pattern": "/downloads/",
                    "src_filename": "*.pdf",
                    "dst_pattern": "/documents/pdfs/",
                    "operation": "move",
                    "count": 1,
                }
            ],
        }

        filepath = os.path.join(self.patterns_dir, f"template_{name}.json")
        with open(filepath, "w") as f:
            json.dump(template, f, indent=2)

        print(f"✓ Created template: {filepath}")
        return filepath


def get_pattern_sharer(patterns_dir: str = "data/patterns") -> PatternSharer:
    """Get pattern sharer instance"""
    return PatternSharer(patterns_dir)
