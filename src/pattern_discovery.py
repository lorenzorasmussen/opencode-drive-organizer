"""
Pattern Discovery Engine
"""

import os
import re
from typing import Dict, List
from datetime import datetime, timedelta
from collections import Counter


class PatternDiscovery:
    """
    Pattern discovery engine for analyzing file organization

    Features:
    - Discover naming patterns
    - Discover organization patterns
    - Discover duplicate patterns
    - Discover size patterns
    - Discover temporary files
    - Discover type distribution
    - Discover age patterns
    - Generate recommendations
    - Pattern confidence scoring
    - Full pattern analysis
    """

    def __init__(self):
        """Initialize pattern discovery engine"""
        self.discovered_patterns = {}

    def discover_naming_patterns(self, directory: str) -> List[Dict]:
        """
        Discover file naming patterns

        Args:
            directory: Directory to analyze

        Returns:
            List of pattern dicts with name, count, confidence
        """
        if not os.path.isdir(directory):
            return []

        filenames = [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]

        patterns = []

        # Extract patterns using regex
        date_pattern = re.compile(r".*?(\d{4}[_-]\d{2}[_-]\d{2}).*?")
        numbered_pattern = re.compile(r".*?(\d{3,}).*?")

        for filename in filenames:
            name, ext = os.path.splitext(filename)

            # Date patterns (e.g., report_2024_01_01)
            match = date_pattern.match(filename)
            if match:
                base_name = filename.replace(match.group(1), "YYYY_MM_DD")
                patterns.append(
                    {
                        "pattern": base_name,
                        "type": "date",
                        "confidence": 0.7,
                        "examples": [filename],
                    }
                )
                continue

            # Numbered patterns (e.g., invoice_001)
            match = numbered_pattern.match(filename)
            if match:
                base_name = filename.replace(match.group(1), "###")
                patterns.append(
                    {
                        "pattern": base_name,
                        "type": "numbered",
                        "confidence": 0.6,
                        "examples": [filename],
                    }
                )
                continue

        # Aggregate similar patterns
        aggregated = {}
        for pattern in patterns:
            key = pattern["pattern"]
            if key not in aggregated:
                aggregated[key] = pattern
                aggregated[key]["count"] = 0
            aggregated[key]["count"] += 1

        # Update confidence based on count
        for pattern in aggregated.values():
            pattern["confidence"] = min(
                0.99, pattern["confidence"] * (1 + pattern["count"] * 0.1)
            )

        return list(aggregated.values())

    def discover_organization_patterns(self, directory: str) -> Dict:
        """
        Discover organization patterns

        Args:
            directory: Directory to analyze

        Returns:
            Dict with folder_structure and organization_score
        """
        if not os.path.isdir(directory):
            return {"folder_structure": [], "organization_score": 0}

        folder_structure = []

        for item in os.listdir(directory):
            path = os.path.join(directory, item)

            if os.path.isdir(path):
                folder_structure.append(
                    {
                        "name": item,
                        "type": "folder",
                        "file_count": len(
                            [
                                f
                                for f in os.listdir(path)
                                if os.path.isfile(os.path.join(path, f))
                            ]
                        ),
                    }
                )

        # Calculate organization score
        total_items = len(folder_structure)
        if total_items == 0:
            org_score = 0
        else:
            org_score = min(1.0, total_items / 10)

        return {
            "folder_structure": folder_structure,
            "organization_score": round(org_score, 2),
        }

    def discover_duplicate_patterns(self, directory: str) -> Dict:
        """
        Discover potential duplicate patterns

        Args:
            directory: Directory to analyze

        Returns:
            Dict with potential_duplicates and patterns
        """
        if not os.path.isdir(directory):
            return {"potential_duplicates": [], "patterns": []}

        files = [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]

        # Look for duplicate indicators
        duplicate_indicators = ["copy", "duplicate", "backup", "bak", "(1)", "(2)"]

        potential_duplicates = []
        for filename in files:
            name_lower = filename.lower()

            for indicator in duplicate_indicators:
                if indicator in name_lower:
                    potential_duplicates.append(
                        {"filename": filename, "indicator": indicator}
                    )
                    break

        return {
            "potential_duplicates": potential_duplicates,
            "count": len(potential_duplicates),
        }

    def discover_size_patterns(self, directory: str) -> Dict:
        """
        Discover file size patterns

        Args:
            directory: Directory to analyze

        Returns:
            Dict with size_distribution and statistics
        """
        if not os.path.isdir(directory):
            return {"size_distribution": []}

        files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]

        sizes = []
        size_distribution = []

        for file_path in files:
            try:
                size = os.path.getsize(file_path)
                sizes.append(size)
                size_kb = size / 1024

                # Categorize size
                if size_kb < 1:
                    category = "tiny (< 1KB)"
                elif size_kb < 100:
                    category = "small (1-100KB)"
                elif size_kb < 1024:
                    category = "medium (100KB-1MB)"
                elif size_kb < 10240:
                    category = "large (1-10MB)"
                else:
                    category = "very large (> 10MB)"

                size_distribution.append(
                    {
                        "file": os.path.basename(file_path),
                        "size_bytes": size,
                        "size_kb": round(size_kb, 2),
                        "category": category,
                    }
                )
            except OSError:
                continue

        # Calculate statistics
        if sizes:
            stats = {
                "min_size": min(sizes),
                "max_size": max(sizes),
                "avg_size": sum(sizes) / len(sizes),
                "total_size": sum(sizes),
            }
        else:
            stats = {}

        return {"size_distribution": size_distribution, "statistics": stats}

    def discover_temp_files(self, directory: str) -> Dict:
        """
        Discover temporary or backup files

        Args:
            directory: Directory to analyze

        Returns:
            Dict with temp_files list
        """
        if not os.path.isdir(directory):
            return {"temp_files": []}

        temp_extensions = [".tmp", ".temp", ".bak", ".old", ".swp", "~"]
        temp_files = []

        for item in os.listdir(directory):
            # Check for temp extensions
            name, ext = os.path.splitext(item)

            if ext.lower() in temp_extensions:
                temp_files.append(
                    {"filename": item, "type": "backup_temp", "indicator": ext}
                )
                continue

            # Check for leading dot (hidden)
            if item.startswith("."):
                temp_files.append(
                    {"filename": item, "type": "hidden", "indicator": "leading_dot"}
                )
                continue

            # Check for trailing tilde
            if item.endswith("~"):
                temp_files.append(
                    {
                        "filename": item,
                        "type": "backup_temp",
                        "indicator": "trailing_tilde",
                    }
                )

        return {"temp_files": temp_files, "count": len(temp_files)}

    def discover_type_distribution(self, directory: str) -> Dict:
        """
        Discover file type distribution

        Args:
            directory: Directory to analyze

        Returns:
            Dict with type_counts and most_common_type
        """
        if not os.path.isdir(directory):
            return {"type_counts": {}}

        files = [
            f
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        ]

        type_counts = Counter()

        for filename in files:
            _, ext = os.path.splitext(filename)
            ext_lower = ext.lower()
            type_counts[ext_lower] += 1

        most_common = type_counts.most_common(1)

        return {
            "type_counts": dict(type_counts),
            "most_common_type": most_common[0][0] if most_common else None,
            "most_common_count": most_common[0][1] if most_common else 0,
            "total_files": len(files),
        }

    def discover_age_patterns(self, directory: str) -> Dict:
        """
        Discover file age patterns

        Args:
            directory: Directory to analyze

        Returns:
            Dict with age_distribution and statistics
        """
        if not os.path.isdir(directory):
            return {"age_distribution": []}

        now = datetime.now()
        age_distribution = []

        for item in os.listdir(directory):
            path = os.path.join(directory, item)

            try:
                mtime = os.path.getmtime(path)
                file_date = datetime.fromtimestamp(mtime)
                age_days = (now - file_date).days

                # Categorize age
                if age_days < 7:
                    category = "recent (< 7 days)"
                elif age_days < 30:
                    category = "week (7-30 days)"
                elif age_days < 90:
                    category = "month (30-90 days)"
                elif age_days < 365:
                    category = "quarter (90-365 days)"
                else:
                    category = "old (> 365 days)"

                age_distribution.append(
                    {
                        "filename": item,
                        "age_days": age_days,
                        "category": category,
                        "modified_date": file_date.isoformat(),
                    }
                )
            except OSError:
                continue

        return {"age_distribution": age_distribution, "count": len(age_distribution)}

    def generate_recommendations(self, directory: str) -> List[Dict]:
        """
        Generate recommendations based on discovered patterns

        Args:
            directory: Directory to analyze

        Returns:
            List of recommendation dicts with action and priority
        """
        recommendations = []

        # Check for temp files
        temp_files = self.discover_temp_files(directory).get("temp_files", [])
        if len(temp_files) > 5:
            recommendations.append(
                {
                    "action": "Clean up temporary files",
                    "priority": "HIGH",
                    "reason": f"Found {len(temp_files)} temporary/backup files",
                    "count": len(temp_files),
                }
            )

        # Check for duplicate patterns
        dup_patterns = self.discover_duplicate_patterns(directory)
        if dup_patterns["count"] > 3:
            recommendations.append(
                {
                    "action": "Review potential duplicates",
                    "priority": "MEDIUM",
                    "reason": f"Found {dup_patterns['count']} potential duplicates",
                    "count": dup_patterns["count"],
                }
            )

        # Check for disorganization
        org_patterns = self.discover_organization_patterns(directory)
        if org_patterns["organization_score"] < 0.3:
            recommendations.append(
                {
                    "action": "Improve folder organization",
                    "priority": "MEDIUM",
                    "reason": "Low organization score detected",
                    "score": org_patterns["organization_score"],
                }
            )

        return recommendations

    def discover_all(self, directory: str) -> Dict:
        """
        Discover all patterns at once

        Args:
            directory: Directory to analyze

        Returns:
            Dict with all pattern discoveries
        """
        return {
            "naming_patterns": self.discover_naming_patterns(directory),
            "organization_patterns": self.discover_organization_patterns(directory),
            "duplicate_patterns": self.discover_duplicate_patterns(directory),
            "size_patterns": self.discover_size_patterns(directory),
            "temp_files": self.discover_temp_files(directory),
            "type_distribution": self.discover_type_distribution(directory),
            "age_patterns": self.discover_age_patterns(directory),
            "recommendations": self.generate_recommendations(directory),
            "analyzed_at": datetime.now().isoformat(),
        }
