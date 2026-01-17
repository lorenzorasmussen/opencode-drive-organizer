"""
Learning System for Manual Corrections
"""

import os
import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from difflib import SequenceMatcher


class LearningSystem:
    """
    Learning system for recording and learning from manual corrections

    Features:
    - Record manual corrections
    - Learn patterns from corrections
    - Pattern similarity matching
    - Confidence scoring based on correction frequency
    - Pattern decay for old data
    - Export/import learning data
    - Batch learning
    - Statistics generation
    """

    def __init__(self, decay_rate: float = 0.1):
        """
        Initialize learning system

        Args:
            decay_rate: Rate at which old patterns decay (0.0-1.0)
        """
        self.corrections = []
        self.patterns = {}
        self.decay_rate = decay_rate

    def record_correction(
        self, file_path: str, original_action: str, corrected_action: str, reason: str
    ):
        """
        Record a manual correction

        Args:
            file_path: Path to file that was corrected
            original_action: Original action predicted
            corrected_action: Correct action chosen by human
            reason: Reason for correction
        """
        correction = {
            "file_path": file_path,
            "original_action": original_action,
            "corrected_action": corrected_action,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }

        self.corrections.append(correction)
        self._learn_from_correction(correction)

    def _learn_from_correction(self, correction: Dict):
        """Learn pattern from a single correction"""
        file_name = os.path.basename(correction["file_path"])
        name, ext = os.path.splitext(file_name)
        ext = ext.lower()

        key = f"{ext}:{name[:10]}"  # Use extension and name prefix

        if key not in self.patterns:
            self.patterns[key] = {
                "recommended_action": correction["corrected_action"],
                "correction_count": 0,
                "confidence": 0.0,
                "last_updated": datetime.now(),
            }

        self.patterns[key]["correction_count"] += 1
        self.patterns[key]["confidence"] = min(
            0.99, 0.5 + (self.patterns[key]["correction_count"] * 0.1)
        )
        self.patterns[key]["last_updated"] = datetime.now()

    def get_corrections(self) -> List[Dict]:
        """Get all recorded corrections"""
        return self.corrections

    def get_learned_pattern(self, file_path: str) -> Optional[Dict]:
        """
        Get learned pattern for a file

        Args:
            file_path: Path to file

        Returns:
            Pattern dict or None if no pattern found
        """
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)
        ext = ext.lower()

        # Try exact match first
        key = f"{ext}:{name[:10]}"
        if key in self.patterns:
            pattern = self._apply_decay(key)
            return pattern

        # Try similarity match
        for pattern_key, pattern in self.patterns.items():
            if self._calculate_similarity(file_name, pattern_key) > 0.7:
                return self._apply_decay(pattern_key)

        return None

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, str1, str2).ratio()

    def _apply_decay(self, key: str) -> Dict:
        """Apply decay to pattern based on age"""
        pattern = self.patterns[key].copy()

        time_since_update = datetime.now() - pattern["last_updated"]
        days_old = time_since_update.days

        if days_old > 30:
            decay_factor = self.decay_rate ** (days_old / 30)
            pattern["confidence"] *= decay_factor

        return pattern

    def get_pattern_similarity(self, file_path: str) -> float:
        """
        Get similarity score for a file path

        Args:
            file_path: Path to file

        Returns:
            Similarity score (0.0-1.0)
        """
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)
        ext = ext.lower()

        max_similarity = 0.0

        for pattern_key in self.patterns:
            similarity = self._calculate_similarity(file_name, pattern_key)
            max_similarity = max(max_similarity, similarity)

        return max_similarity

    def recommend_action(self, file_path: str) -> Dict:
        """
        Get recommended action based on learned patterns

        Args:
            file_path: Path to file

        Returns:
            Dict with 'action' and 'confidence' keys
        """
        pattern = self.get_learned_pattern(file_path)

        if pattern:
            return {
                "action": pattern["recommended_action"],
                "confidence": pattern["confidence"],
                "based_on": f"{pattern['correction_count']} corrections",
            }
        else:
            return {
                "action": "REVIEW_MANUAL",
                "confidence": 0.0,
                "based_on": "No pattern found",
            }

    def batch_learn(self, corrections: List[Dict]):
        """
        Learn from multiple corrections at once

        Args:
            corrections: List of correction dicts
        """
        for correction in corrections:
            self.record_correction(
                file_path=correction["file_path"],
                original_action=correction["original_action"],
                corrected_action=correction["corrected_action"],
                reason=correction["reason"],
            )

    def export_learning_data(self, export_path: str):
        """
        Export learning data to JSON file

        Args:
            export_path: Path to export file
        """
        data = {
            "corrections": self.corrections,
            "patterns": {
                k: {
                    "recommended_action": v["recommended_action"],
                    "correction_count": v["correction_count"],
                    "confidence": v["confidence"],
                    "last_updated": v["last_updated"].isoformat(),
                }
                for k, v in self.patterns.items()
            },
            "exported_at": datetime.now().isoformat(),
        }

        os.makedirs(os.path.dirname(export_path), exist_ok=True)

        with open(export_path, "w") as f:
            json.dump(data, f, indent=2)

    def import_learning_data(self, import_path: str):
        """
        Import learning data from JSON file

        Args:
            import_path: Path to import file
        """
        with open(import_path, "r") as f:
            data = json.load(f)

        self.corrections = data.get("corrections", [])

        for key, pattern_data in data.get("patterns", {}).items():
            self.patterns[key] = {
                "recommended_action": pattern_data["recommended_action"],
                "correction_count": pattern_data["correction_count"],
                "confidence": pattern_data["confidence"],
                "last_updated": datetime.fromisoformat(pattern_data["last_updated"]),
            }

    def get_statistics(self) -> Dict:
        """Generate statistics about the learning system"""
        if not self.corrections:
            return {
                "total_corrections": 0,
                "most_common_correction": None,
                "average_confidence": 0.0,
                "pattern_count": len(self.patterns),
            }

        # Find most common correction
        correction_counts = {}
        for c in self.corrections:
            action = c["corrected_action"]
            correction_counts[action] = correction_counts.get(action, 0) + 1

        most_common = max(correction_counts.items(), key=lambda x: x[1])

        # Calculate average confidence
        avg_confidence = (
            sum(p["confidence"] for p in self.patterns.values()) / len(self.patterns)
            if self.patterns
            else 0
        )

        return {
            "total_corrections": len(self.corrections),
            "most_common_correction": most_common[0],
            "most_common_count": most_common[1],
            "average_confidence": avg_confidence,
            "pattern_count": len(self.patterns),
            "corrections_by_type": correction_counts,
        }
