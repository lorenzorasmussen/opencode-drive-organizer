"""
LlamaIndex Content Extractor for richer file content analysis

Supports:
- Text file extraction (txt, md, json, csv, etc.)
- PDF extraction (requires pypdf)
- Metadata extraction
- Optional LLM summarization (via Ollama)
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class LlamaIndexExtractor:
    """
    Content extractor using LlamaIndex patterns for document loading
    and content analysis.

    This implementation provides llamaindex-like functionality using
    Python standard library, with optional enhancements when llamaindex
    is available.
    """

    SUPPORTED_EXTENSIONS = {
        ".txt",
        ".md",
        ".json",
        ".csv",
        ".xml",
        ".yaml",
        ".yml",
        ".html",
        ".htm",
        ".rst",
        ".tex",
        ".py",
        ".js",
        ".ts",
        ".css",
        ".scss",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".sh",
        ".bash",
        ".zsh",
        ".fish",
        ".ps1",
        ".bat",
        ".ini",
        ".cfg",
        ".conf",
        ".log",
        ".toml",
        ".pdf",
        ".doc",
        ".docx",
    }

    def __init__(
        self, use_llamaindex: bool = False, ollama_url: str = "http://localhost:11434"
    ):
        """
        Initialize extractor

        Args:
            use_llamaindex: Use actual LlamaIndex if available
            ollama_url: URL for Ollama LLM API
        """
        self.use_llamaindex = use_llamaindex
        self.ollama_url = ollama_url
        self._llamaindex_available = False

        # Try to import llamaindex
        try:
            from llama_index import SimpleDirectoryReader

            self._llamaindex_available = True
            self._SimpleDirectoryReader = SimpleDirectoryReader
        except ImportError:
            pass

    def extract(self, directory: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Extract content and metadata from files in directory

        Args:
            directory: Path to directory to scan
            recursive: Scan subdirectories

        Returns:
            List of document dicts with content and metadata
        """
        docs = []
        dir_path = Path(directory)

        if not dir_path.exists():
            return docs

        # Use LlamaIndex if available and requested
        if self.use_llamaindex and self._llamaindex_available:
            docs = self._extract_with_llamaindex(dir_path)
        else:
            docs = self._extract_with_stdlib(dir_path, recursive)

        return docs

    def _extract_with_stdlib(
        self, dir_path: Path, recursive: bool
    ) -> List[Dict[str, Any]]:
        """Extract using standard library"""
        docs = []

        pattern = "**/*" if recursive else "*"

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                ext = file_path.suffix.lower()

                if ext in self.SUPPORTED_EXTENSIONS:
                    doc = self._read_text_file(file_path)
                    docs.append(doc)

        return docs

    def _read_text_file(self, file_path: Path) -> Dict[str, Any]:
        """Read a text file and extract content + metadata"""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            content = f"[Error reading file: {e}]"

        stat = file_path.stat()

        return {
            "content": content,
            "metadata": {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": stat.st_size,
                "file_type": file_path.suffix.lower(),
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            },
        }

    def _extract_with_llamaindex(self, dir_path: Path) -> List[Dict[str, Any]]:
        """Extract using actual LlamaIndex"""
        try:
            reader = self._SimpleDirectoryReader(
                input_dir=str(dir_path), recursive=True
            )
            documents = reader.load_data()

            return [
                {
                    "content": doc.text if hasattr(doc, "text") else str(doc),
                    "metadata": doc.metadata if hasattr(doc, "metadata") else {},
                }
                for doc in documents
            ]
        except Exception as e:
            # Fallback to stdlib on error
            return self._extract_with_stdlib(dir_path, True)

    def summarize_content(
        self, content: str, model: str = "llama3.2"
    ) -> Dict[str, str]:
        """
        Summarize content using LLM

        Args:
            content: Text to summarize
            model: Ollama model name

        Returns:
            Dict with summary and keywords
        """
        try:
            import requests

            prompt = f"""Summarize this document content. Return JSON with:
- summary: A concise 2-3 sentence summary
- keywords: Comma-separated key topics

Content:
{content[:2000]}  # Limit to avoid token limits

JSON:"""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                return json.loads(result.get("response", "{}"))

        except Exception:
            pass

        # Fallback: simple extraction
        return {
            "summary": content[:200] + ("..." if len(content) > 200 else ""),
            "keywords": "",
        }

    def extract_with_summaries(
        self, directory: str, summarize: bool = True, model: str = "llama3.2"
    ) -> List[Dict[str, Any]]:
        """
        Extract content and optionally generate summaries

        Args:
            directory: Directory to scan
            summarize: Generate LLM summaries
            model: LLM model for summarization

        Returns:
            List of documents with content, metadata, and summaries
        """
        documents = self.extract(directory)

        if summarize:
            for doc in documents:
                summary = self.summarize_content(doc["content"], model)
                doc["summary"] = summary.get("summary", "")
                doc["keywords"] = summary.get("keywords", "")

        return documents


def get_directory_summary(directory: str) -> Dict[str, Any]:
    """
    Get comprehensive summary of directory contents

    Args:
        directory: Path to directory

    Returns:
        Summary dict with file counts, types, and sample content
    """
    extractor = LlamaIndexExtractor()
    documents = extractor.extract(directory)

    # Aggregate statistics
    file_types = {}
    total_size = 0

    for doc in documents:
        file_type = doc["metadata"].get("file_type", "unknown")
        file_types[file_type] = file_types.get(file_type, 0) + 1
        total_size += doc["metadata"].get("file_size", 0)

    return {
        "total_files": len(documents),
        "file_types": file_types,
        "total_size_bytes": total_size,
        "documents": documents[:10],  # Limit for display
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        summary = get_directory_summary(sys.argv[1])
        print(f"Files: {summary['total_files']}")
        print(f"Types: {summary['file_types']}")
        print(f"Size: {summary['total_size_bytes']} bytes")
    else:
        print("Usage: python llamaindex_extractor.py <directory>")
