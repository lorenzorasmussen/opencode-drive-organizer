"""
Content Indexer
"""

import os
import re
import json
from typing import Dict, List, Optional, Set
from collections import Counter
from datetime import datetime


class ContentIndexer:
    """
    Content indexer for searching file contents

    Features:
    - Index directory contents
    - Search indexed content
    - Update index with new files
    - Extract keywords
    - Export/import index
    - Remove files from index
    - Clear index
    - Find similar documents
    - Performance tracking
    """

    def __init__(self):
        """Initialize content indexer"""
        self.index = {}
        self.keywords = {}
        self.stats = {"total_files": 0, "total_keywords": 0, "indexed_at": None}

    def index_directory(self, directory: str) -> List[Dict]:
        """
        Index all files in a directory

        Args:
            directory: Directory to index

        Returns:
            List of indexed file dicts
        """
        if not os.path.isdir(directory):
            return []

        indexed = []

        for item in os.listdir(directory):
            file_path = os.path.join(directory, item)

            if not os.path.isfile(file_path):
                continue

            # Skip binary files
            if self._is_binary_file(file_path):
                continue

            # Extract content
            content = self._extract_text_content(file_path)

            if content is None:
                continue

            # Extract keywords
            keywords = self.extract_keywords(content)

            # Add to index
            self.index[file_path] = {
                "file": item,
                "path": file_path,
                "content": content,
                "keywords": keywords,
                "indexed_at": datetime.now().isoformat(),
            }

            # Update keyword index
            for keyword in keywords:
                if keyword not in self.keywords:
                    self.keywords[keyword] = []
                self.keywords[keyword].append(file_path)

            indexed.append(self.index[file_path])
            self.stats["total_files"] += 1
            self.stats["total_keywords"] += len(keywords)

        self.stats["indexed_at"] = datetime.now().isoformat()

        return indexed

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search indexed content

        Args:
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of matching file dicts
        """
        query_lower = query.lower()
        results = []

        for file_path, file_data in self.index.items():
            # Search in content
            if query_lower in file_data["content"].lower():
                results.append(file_data)
                continue

            # Search in keywords
            for keyword in file_data["keywords"]:
                if query_lower in keyword.lower():
                    results.append(file_data)
                    break

        return results[:limit]

    def update_index(self, directory: str) -> List[Dict]:
        """
        Update index with new/modified files

        Args:
            directory: Directory to update

        Returns:
            List of newly indexed files
        """
        new_files = []

        for item in os.listdir(directory):
            file_path = os.path.join(directory, item)

            if not os.path.isfile(file_path):
                continue

            # Skip if already indexed
            if file_path in self.index:
                continue

            # Index new file
            indexed = self.index_directory(directory)
            if file_path in [i["path"] for i in indexed]:
                new_files.extend([i for i in indexed if i["path"] == file_path])

        return new_files

    def extract_keywords(self, content: str) -> List[str]:
        """
        Extract keywords from content

        Args:
            content: Text content

        Returns:
            List of keywords
        """
        # Simple keyword extraction
        words = re.findall(r"\b[a-zA-Z]{4,}\b", content)

        # Filter common words
        common_words = {
            "this",
            "that",
            "with",
            "from",
            "have",
            "were",
            "been",
            "their",
            "there",
            "which",
            "would",
            "could",
            "should",
        }

        keywords = [word.lower() for word in words if word.lower() not in common_words]

        # Count frequency and return top keywords
        keyword_counts = Counter(keywords)
        top_keywords = [k for k, v in keyword_counts.most_common(10)]

        return top_keywords

    def get_index_stats(self) -> Dict:
        """Get index statistics"""
        return self.stats.copy()

    def export_index(self, export_path: str):
        """
        Export index to JSON file

        Args:
            export_path: Path to export file
        """
        data = {
            "index": self.index,
            "keywords": self.keywords,
            "stats": self.stats,
            "exported_at": datetime.now().isoformat(),
        }

        os.makedirs(os.path.dirname(export_path), exist_ok=True)

        with open(export_path, "w") as f:
            json.dump(data, f, indent=2)

    def import_index(self, import_path: str):
        """
        Import index from JSON file

        Args:
            import_path: Path to import file
        """
        with open(import_path, "r") as f:
            data = json.load(f)

        self.index = data.get("index", {})
        self.keywords = data.get("keywords", {})
        self.stats = data.get("stats", {"total_files": 0, "total_keywords": 0})

    def remove_from_index(self, file_path: str):
        """
        Remove a file from index

        Args:
            file_path: Path to file
        """
        if file_path not in self.index:
            return

        # Remove from index
        keywords = self.index[file_path].get("keywords", [])

        # Remove from keyword index
        for keyword in keywords:
            if keyword in self.keywords and file_path in self.keywords[keyword]:
                self.keywords[keyword].remove(file_path)

        # Remove from index
        del self.index[file_path]
        self.stats["total_files"] -= 1

    def clear_index(self):
        """Clear entire index"""
        self.index = {}
        self.keywords = {}
        self.stats = {"total_files": 0, "total_keywords": 0, "indexed_at": None}

    def find_similar(self, file_path: str, limit: int = 5) -> List[Dict]:
        """
        Find similar documents based on keywords

        Args:
            file_path: Path to file
            limit: Maximum results to return

        Returns:
            List of similar file dicts
        """
        if file_path not in self.index:
            return []

        # Get keywords for file
        keywords = set(self.index[file_path].get("keywords", []))

        # Find files with similar keywords
        similar_files = []

        for other_path, other_data in self.index.items():
            if other_path == file_path:
                continue

            other_keywords = set(other_data.get("keywords", []))

            # Calculate similarity
            intersection = len(keywords & other_keywords)
            union = len(keywords | other_keywords)

            if union > 0:
                similarity = intersection / union

                if similarity > 0.1:  # At least 10% keyword overlap
                    similar_files.append(
                        {
                            "file": other_data["file"],
                            "path": other_path,
                            "similarity": round(similarity, 2),
                        }
                    )

        # Sort by similarity and limit
        similar_files.sort(key=lambda x: x["similarity"], reverse=True)

        return similar_files[:limit]

    def _is_binary_file(self, file_path: str) -> bool:
        """
        Check if file is binary

        Args:
            file_path: Path to file

        Returns:
            True if binary, False otherwise
        """
        binary_extensions = {
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".bin",
            ".zip",
            ".tar",
            ".gz",
            ".jpg",
            ".jpeg",
            ".png",
            ".pdf",
            ".docx",
            ".xlsx",
        }

        _, ext = os.path.splitext(file_path)
        return ext.lower() in binary_extensions

    def _extract_text_content(self, file_path: str) -> Optional[str]:
        """
        Extract text content from file

        Args:
            file_path: Path to file

        Returns:
            Text content or None if binary/error
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except UnicodeDecodeError:
            return None
        except Exception:
            return None
