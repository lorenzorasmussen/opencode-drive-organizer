"""
Smart Folder Naming - LLM-powered folder name suggestions

Features:
- Analyze file content to suggest folder names
- Context-aware naming
- Multi-language support
- Custom naming conventions
"""

from typing import Dict, List, Optional


class SmartFolderNamer:
    """LLM-powered folder naming assistant"""

    def __init__(self, ollama_model: str = "llama2"):
        """
        Initialize folder namer

        Args:
            ollama_model: Ollama model to use
        """
        self.model = ollama_model
        self.naming_patterns = {
            "date_based": ["YYYY", "YYYY-MM", "YYYY-MM-DD", "MMM YYYY"],
            "type_based": ["Documents", "Images", "Videos", "Archives"],
            "project_based": ["Project-Name", "ProjectName_v1", "Project_Name_Final"],
            "context_based": ["Inbox", "Processed", "Pending", "Archive"],
        }

    def suggest_folder_name(
        self,
        files: List[str],
        context: Optional[str] = None,
        style: str = "auto",
    ) -> Dict:
        """
        Suggest folder name based on file analysis

        Args:
            files: List of file paths
            context: Optional context description
            style: Naming style (auto, date, type, project, context)

        Returns:
            Dict with suggested name and alternatives
        """
        from ollama_integration import OllamaIntegration

        ollama = OllamaIntegration()

        if not ollama.check_connection():
            return self._fallback_suggestion(files, style)

        # Build prompt
        file_names = [f.split("/")[-1] for f in files[:10]]
        file_types = [f.split(".")[-1] if "." in f else "unknown" for f in files[:10]]

        prompt = f"""Analyze these files and suggest a concise folder name:

Files: {file_names}
Types: {file_types}
Context: {context or "General"}
Style: {style}

Return ONLY the best folder name (1-3 words, camelCase or snake_case)."""

        try:
            response = ollama.generate(
                prompt,
                model=self.model,
                max_tokens=20,
                temperature=0.3,
            )

            if response:
                suggested = response.strip().replace(" ", "").replace("-", "_")
                return {
                    "suggested": suggested,
                    "style": style,
                    "confidence": "high",
                    "alternatives": self._generate_alternatives(files, style),
                }

        except Exception as e:
            print(f"⚠️  LLM naming error: {e}")

        return self._fallback_suggestion(files, style)

    def _fallback_suggestion(self, files: List[str], style: str) -> Dict:
        """Fallback suggestion without LLM"""
        file_names = [f.split("/")[-1] for f in files[:5]]
        extensions = set(f.split(".")[-1].lower() for f in files if "." in f)

        # Detect primary type
        type_map = {
            "pdf": "Documents",
            "doc": "Documents",
            "docx": "Documents",
            "jpg": "Images",
            "png": "Images",
            "gif": "Images",
            "mp4": "Videos",
            "mov": "Videos",
            "zip": "Archives",
            "txt": "Text",
            "md": "Notes",
        }

        primary_type = "Mixed"
        for ext in extensions:
            if ext in type_map:
                primary_type = type_map[ext]
                break

        suggested = primary_type
        if style == "date":
            from datetime import datetime

            suggested = datetime.now().strftime("%Y-%m")

        return {
            "suggested": suggested,
            "style": style,
            "confidence": "low",
            "alternatives": self._generate_alternatives(files, style),
        }

    def _generate_alternatives(self, files: List[str], style: str) -> List[str]:
        """Generate alternative folder names"""
        alternatives = []
        file_names = [f.split("/")[-1] for f in files[:3]]

        # Type-based alternatives
        type_alts = ["by_type", "categorized", "sorted", "organized"]
        alternatives.extend(type_alts[:2])

        # Date-based alternatives
        from datetime import datetime

        date_alts = [datetime.now().strftime("%Y"), datetime.now().strftime("%B")]
        alternatives.extend(date_alts[:1])

        # Context-based
        context_alts = ["input", "processing", "output"]
        alternatives.extend(context_alts[:1])

        return alternatives[:3]

    def suggest_structure(
        self,
        files: List[str],
        max_folders: int = 5,
    ) -> List[Dict]:
        """
        Suggest folder structure for organizing files

        Args:
            files: List of file paths
            max_folders: Maximum number of folders

        Returns:
            List of folder suggestions with files
        """
        from ollama_integration import OllamaIntegration

        ollama = OllamaIntegration()

        if not ollama.check_connection():
            return self._fallback_structure(files, max_folders)

        file_names = [f.split("/")[-1] for f in files[:15]]

        prompt = f"""Group these files into up to {max_folders} folders and suggest folder names:

Files: {file_names}

Return JSON array of {{folder_name, files}} structure."""

        try:
            response = ollama.generate(
                prompt,
                model=self.model,
                max_tokens=200,
                temperature=0.4,
            )

            if response:
                import json

                try:
                    structure = json.loads(response)
                    return structure
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            print(f"⚠️  LLM structure error: {e}")

        return self._fallback_structure(files, max_folders)

    def _fallback_structure(self, files: List[str], max_folders: int) -> List[Dict]:
        """Fallback structure without LLM"""
        from collections import defaultdict

        extensions = defaultdict(list)
        for f in files:
            ext = f.split(".")[-1].lower() if "." in f else "other"
            extensions[ext].append(f)

        type_map = {
            "pdf": "Documents",
            "doc": "Documents",
            "docx": "Documents",
            "jpg": "Images",
            "png": "Images",
            "gif": "Images",
            "mp4": "Videos",
            "mov": "Videos",
            "zip": "Archives",
            "txt": "Text",
            "md": "Notes",
        }

        structure = []
        for ext, files_list in list(extensions.items())[:max_folders]:
            folder_name = type_map.get(ext, ext.upper())
            structure.append(
                {
                    "folder_name": folder_name,
                    "files": [f.split("/")[-1] for f in files_list],
                }
            )

        return structure


def get_folder_namer(model: str = "llama2") -> SmartFolderNamer:
    """Get folder namer instance"""
    return SmartFolderNamer(ollama_model=model)
