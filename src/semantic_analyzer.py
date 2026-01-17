"""
10-Dimensional Semantic Analysis Engine for risk-aware file categorization
"""

import os
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


class SemanticAnalyzer:
    """
    10-dimensional semantic analysis for risk-aware file categorization

    Dimensions:
    1. Type (15%): File type significance
    2. Location (15%): Folder context
    3. Age (20%): File age
    4. Size (15%): File size impact
    5. Git Activity (10%): Repository activity
    6. Reversibility (10%): Can changes be undone?
    7. Personal Data (25%): Contains personal info?
    8. Context (8%): Surrounding files
    9. Predictive Factors (7%): Future need prediction
    10. Overall Confidence: Weighted combination

    Risk Levels: CRITICAL, HIGH, MEDIUM, LOW

    Actions: DELETE_IMMEDIATE, REVIEW_MANUAL, KEEP_ACTIVE, MOVE_CORRECT, BACKUP_CLOUD, COMPRESS
    """

    # Dimension weights (must sum to 100)
    DIMENSION_WEIGHTS = {
        "type_score": 15,
        "location_score": 15,
        "age_score": 20,
        "size_score": 15,
        "git_activity_score": 10,
        "reversibility_score": 10,
        "personal_data_score": 25,
        "context_score": 8,
        "predictive_score": 7,
        "overall_confidence": 0,
    }

    # Risk level thresholds
    RISK_THRESHOLDS = {"CRITICAL": 0.5, "HIGH": 0.7, "MEDIUM": 0.85, "LOW": 1.0}

    # Action mappings
    ACTION_MAPPINGS = {
        "DELETE_IMMEDIATE": ["CRITICAL"],
        "REVIEW_MANUAL": ["HIGH"],
        "KEEP_ACTIVE": ["LOW", "MEDIUM"],
        "MOVE_CORRECT": ["MEDIUM"],
        "BACKUP_CLOUD": ["HIGH"],
        "COMPRESS": ["MEDIUM"],
    }

    # File type risk scores (0-1, higher = more deletable)
    FILE_TYPE_SCORES = {
        # High-risk (executables, scripts)
        ".exe": 0.9,
        ".sh": 0.85,
        ".bat": 0.85,
        ".cmd": 0.85,
        ".ps1": 0.85,
        # Medium-risk (documents, archives)
        ".pdf": 0.6,
        ".docx": 0.55,
        ".doc": 0.55,
        ".pptx": 0.55,
        ".xlsx": 0.55,
        ".xls": 0.55,
        ".zip": 0.6,
        ".tar": 0.6,
        ".gz": 0.6,
        ".rar": 0.6,
        # Low-risk (text, data, images)
        ".txt": 0.3,
        ".md": 0.3,
        ".csv": 0.4,
        ".json": 0.4,
        ".xml": 0.4,
        ".yml": 0.35,
        ".yaml": 0.35,
        ".png": 0.35,
        ".jpg": 0.35,
        ".jpeg": 0.35,
        ".gif": 0.35,
        ".svg": 0.35,
    }

    # Location risk scores (0-1, higher = more deletable)
    LOCATION_SCORES = {
        # High-risk locations
        "downloads": 0.8,
        "desktop": 0.75,
        "temp": 0.85,
        "tmp": 0.85,
        "root": 0.7,
        "/": 0.7,
        # Medium-risk locations
        "documents": 0.5,
        "home": 0.5,
        "user": 0.5,
        # Low-risk locations
        "archived": 0.2,
        "backup": 0.2,
        "organized": 0.3,
    }

    def __init__(self):
        self.learned_patterns = {}
        self.analysis_stats = {
            "total_files_analyzed": 0,
            "total_confidence": 0,
            "risk_distribution": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
            "action_distribution": {
                "DELETE_IMMEDIATE": 0,
                "REVIEW_MANUAL": 0,
                "KEEP_ACTIVE": 0,
                "MOVE_CORRECT": 0,
                "BACKUP_CLOUD": 0,
                "COMPRESS": 0,
            },
        }

    def calculate_type_score(self, file_path: str) -> float:
        """Calculate type score based on file extension"""
        _, ext = os.path.splitext(file_path.lower())

        if ext in self.FILE_TYPE_SCORES:
            return self.FILE_TYPE_SCORES[ext]

        # Default medium score for unknown types
        return 0.5

    def calculate_location_score(self, file_path: str) -> float:
        """Calculate location score based on folder context"""
        path_lower = file_path.lower()

        # Check for low-risk locations first (more specific)
        for keyword, score in sorted(
            self.LOCATION_SCORES.items(), key=lambda x: -len(x[0])
        ):
            if keyword in path_lower:
                return score

        # Default medium score
        return 0.5

    def calculate_age_score(self, file_path: str) -> float:
        """Calculate age score based on file modification time"""
        try:
            mtime = os.path.getmtime(file_path)
            file_age_days = (time.time() - mtime) / (24 * 60 * 60)

            # Older files have higher deletion confidence
            if file_age_days > 365:
                return 0.9
            elif file_age_days > 90:
                return 0.7
            elif file_age_days > 30:
                return 0.5
            elif file_age_days > 7:
                return 0.3
            else:
                return 0.1
        except Exception:
            return 0.5

    def calculate_size_score(self, file_size_bytes: int) -> float:
        """Calculate size score based on file size"""
        size_mb = file_size_bytes / (1024 * 1024)

        # Larger files have higher deletion confidence
        if size_mb > 100:
            return 0.8
        elif size_mb > 50:
            return 0.7
        elif size_mb > 10:
            return 0.5
        elif size_mb > 1:
            return 0.3
        else:
            return 0.2

    def classify_risk(self, confidence: float) -> str:
        """Classify risk level based on confidence score"""
        if confidence < self.RISK_THRESHOLDS["CRITICAL"]:
            return "CRITICAL"
        elif confidence < self.RISK_THRESHOLDS["HIGH"]:
            return "HIGH"
        elif confidence < self.RISK_THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        else:
            return "LOW"

    def classify_action(self, risk: str, confidence: float) -> str:
        """Classify action based on risk and confidence"""
        # Critical + low confidence → DELETE_IMMEDIATE
        if risk == "CRITICAL" and confidence < 0.5:
            return "DELETE_IMMEDIATE"

        # High risk + medium confidence → REVIEW_MANUAL
        if risk == "HIGH" and confidence < 0.7:
            return "REVIEW_MANUAL"

        # Low risk + high confidence → KEEP_ACTIVE
        if risk == "LOW" and confidence > 0.85:
            return "KEEP_ACTIVE"

        # Default mappings
        for action, risks in self.ACTION_MAPPINGS.items():
            if risk in risks:
                return action

        return "REVIEW_MANUAL"

    def calculate_overall_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate overall confidence from weighted dimensions"""
        total_weight = 0
        weighted_sum = 0

        for dimension, weight in self.DIMENSION_WEIGHTS.items():
            if dimension == "overall_confidence":
                continue

            if dimension in scores:
                weighted_sum += scores[dimension] * weight
                total_weight += weight

        if total_weight == 0:
            return 0.5

        return weighted_sum / total_weight

    def learn_from_correction(self, file_type: str, location: str, confidence: float):
        """Learn from manual corrections to improve predictions"""
        key = f"{file_type}:{location}"

        if key not in self.learned_patterns:
            self.learned_patterns[key] = []

        self.learned_patterns[key].append(
            {"confidence": confidence, "timestamp": datetime.now().isoformat()}
        )

        # Keep only last 100 corrections per pattern
        if len(self.learned_patterns[key]) > 100:
            self.learned_patterns[key] = self.learned_patterns[key][-100:]

    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a single file and return risk assessment"""
        try:
            # Calculate dimension scores
            scores = {
                "type_score": self.calculate_type_score(file_path),
                "location_score": self.calculate_location_score(file_path),
                "age_score": self.calculate_age_score(file_path),
            }

            # Get file size
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                scores["size_score"] = self.calculate_size_score(file_size)
            else:
                scores["size_score"] = 0.5

            # Default scores for other dimensions (to be implemented)
            scores["git_activity_score"] = 0.5
            scores["reversibility_score"] = 0.5
            scores["personal_data_score"] = 0.5
            scores["context_score"] = 0.5
            scores["predictive_score"] = 0.5

            # Calculate overall confidence
            confidence = self.calculate_overall_confidence(scores)

            # Classify risk and action
            risk = self.classify_risk(confidence)
            action = self.classify_action(risk, confidence)

            # Update statistics
            self.analysis_stats["total_files_analyzed"] += 1
            self.analysis_stats["total_confidence"] += confidence
            self.analysis_stats["risk_distribution"][risk] += 1
            self.analysis_stats["action_distribution"][action] += 1

            return {
                "file_path": file_path,
                "confidence": confidence,
                "risk": risk,
                "action": action,
                "scores": scores,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
            return {
                "file_path": file_path,
                "confidence": 0.5,
                "risk": "MEDIUM",
                "action": "REVIEW_MANUAL",
                "error": str(e),
            }

    def batch_analyze_files(self, file_paths: List[str]) -> List[Dict]:
        """Analyze multiple files efficiently"""
        print(f"🔍 Analyzing {len(file_paths)} files...")

        results = []
        for i, file_path in enumerate(file_paths):
            if i % 100 == 0:
                print(f"  Progress: {i}/{len(file_paths)}")

            result = self.analyze_file(file_path)
            results.append(result)

        print(f"✓ Analyzed {len(results)} files")
        return results

    def generate_statistics(self) -> Dict:
        """Generate statistics for analysis run"""
        total = self.analysis_stats["total_files_analyzed"]
        avg_confidence = (
            self.analysis_stats["total_confidence"] / total if total > 0 else 0
        )

        return {
            "total_files_analyzed": total,
            "average_confidence": avg_confidence,
            "risk_distribution": self.analysis_stats["risk_distribution"],
            "action_distribution": self.analysis_stats["action_distribution"],
            "learned_patterns_count": len(self.learned_patterns),
            "timestamp": datetime.now().isoformat(),
        }
