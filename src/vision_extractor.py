"""
Vision Model Integration for Image Categorization

Uses Ollama with Moondream vision model (or similar) to analyze images
and generate descriptions, tags, and categorization.

Based on LlamaFS methodology:
- Uses Moondream via Ollama for image analysis
- Converts images to ImageDocument objects
- Generates textual descriptions for semantic organization
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class VisionExtractor:
    """
    Vision-based image analyzer using Ollama Moondream model

    Features:
    - Detect and categorize images
    - Generate descriptions via LLM vision
    - Extract image metadata (dimensions, format, etc.)
    - Categorize by content type (people, nature, documents, etc.)
    """

    SUPPORTED_IMAGE_FORMATS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".tiff",
        ".tif",
        ".svg",
    }

    CATEGORY_KEYWORDS = {
        "people": ["person", "people", "portrait", "selfie", "group", "face", "crowd"],
        "nature": [
            "landscape",
            "nature",
            "mountain",
            "beach",
            "forest",
            "sunset",
            "ocean",
            "sky",
        ],
        "documents": [
            "document",
            "text",
            "receipt",
            "invoice",
            "certificate",
            "id",
            "passport",
        ],
        "food": ["food", "meal", "dish", "restaurant", "cooking", "ingredients"],
        "work": [
            "office",
            "meeting",
            "presentation",
            "work",
            "business",
            "computer",
            "laptop",
        ],
        "travel": ["travel", "vacation", "trip", "hotel", "airport", "tourist"],
        "events": [
            "party",
            "wedding",
            "birthday",
            "celebration",
            "concert",
            "festival",
        ],
        "art": ["art", "painting", "sculpture", "design", "creative", "architecture"],
    }

    def __init__(
        self, ollama_url: str = "http://localhost:11434", model: str = "moondream"
    ):
        """
        Initialize vision extractor

        Args:
            ollama_url: Ollama server URL
            model: Vision model name (moondream, llava, etc.)
        """
        self.ollama_url = ollama_url
        self.model = model
        self._model_available = None

    def find_images(self, directory: str, recursive: bool = True) -> List[str]:
        """
        Find all image files in directory

        Args:
            directory: Path to scan
            recursive: Scan subdirectories

        Returns:
            List of image file paths
        """
        images = []
        dir_path = Path(directory)

        if not dir_path.exists():
            return images

        pattern = "**/*" if recursive else "*"

        for file_path in dir_path.glob(pattern):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.SUPPORTED_IMAGE_FORMATS
            ):
                images.append(str(file_path))

        return images

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze image and generate description using vision model

        Args:
            image_path: Path to image file

        Returns:
            Dict with description, tags, and analysis
        """
        if not os.path.exists(image_path):
            return {"error": "Image not found"}

        # Try Ollama vision model
        try:
            import requests

            # Read image as base64
            import base64

            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            # Use Moondream/LLaVA for vision analysis
            prompt = """Describe this image in detail. Include:
1. What is shown in the image
2. The setting/environment
3. Any people, objects, or activities
4. Mood or atmosphere
5. Key visual elements

Format as JSON:
{
  "description": "2-3 sentence description",
  "tags": ["tag1", "tag2", "tag3"],
  "category": "primary category"
}"""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "images": [image_data],
                    "stream": False,
                    "format": "json",
                },
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                analysis = json.loads(result.get("response", "{}"))
                return {
                    "description": analysis.get("description", ""),
                    "tags": analysis.get("tags", []),
                    "category": analysis.get("category", "uncategorized"),
                    "confidence": 0.8,
                    "source": "ollama_vision",
                }

        except Exception:
            pass

        # Fallback: Use basic metadata and heuristics
        return self._basic_image_analysis(image_path)

    def _basic_image_analysis(self, image_path: str) -> Dict[str, Any]:
        """Basic analysis without vision model"""
        file_path = Path(image_path)

        # Get file metadata
        stat = file_path.stat()

        # Extract tags from filename
        filename = file_path.stem
        tags = [
            t.strip().lower()
            for t in filename.replace("-", " ").replace("_", " ").split()
        ]

        # Determine category from filename
        category = "uncategorized"
        filename_lower = filename.lower()
        for cat, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in filename_lower for kw in keywords):
                category = cat
                break

        return {
            "description": f"Image file: {file_path.name}",
            "tags": tags[:5],  # Limit tags
            "category": category,
            "confidence": 0.3,  # Low confidence without vision model
            "source": "filename_heuristic",
        }

    def categorize_images(
        self, directory: str, recursive: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Categorize all images in directory

        Args:
            directory: Path to scan
            recursive: Scan subdirectories

        Returns:
            List of image categorizations with path, category, and confidence
        """
        images = self.find_images(directory, recursive)
        results = []

        for image_path in images:
            analysis = self.analyze_image(image_path)
            results.append(
                {
                    "path": image_path,
                    "file_name": Path(image_path).name,
                    "category": analysis.get("category", "unknown"),
                    "description": analysis.get("description", ""),
                    "tags": analysis.get("tags", []),
                    "confidence": analysis.get("confidence", 0),
                    "source": analysis.get("source", "unknown"),
                }
            )

        return results

    def extract_image_metadata(self, image_path: str) -> Dict[str, Any]:
        """
        Extract technical metadata from image

        Args:
            image_path: Path to image file

        Returns:
            Dict with dimensions, format, size, etc.
        """
        file_path = Path(image_path)

        if not file_path.exists():
            return {"error": "Image not found"}

        stat = file_path.stat()

        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": stat.st_size,
            "format": file_path.suffix.lower(),
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

        # Try to get image dimensions using Pillow
        try:
            from PIL import Image

            with Image.open(image_path) as img:
                metadata["width"] = img.width
                metadata["height"] = img.height
                metadata["mode"] = img.mode
                if hasattr(img, "info"):
                    metadata["exif"] = img.info

        except Exception:
            # Pillow not available or can't read image
            metadata["width"] = None
            metadata["height"] = None

        return metadata

    def organize_images_by_category(
        self, directory: str, output_base: Optional[str] = None, recursive: bool = True
    ) -> Dict[str, List[str]]:
        """
        Organize images into category folders

        Args:
            directory: Source directory
            output_base: Base directory for organized output (None = same as source)
            recursive: Scan subdirectories

        Returns:
            Dict mapping categories to list of file paths
        """
        if output_base is None:
            output_base = directory

        categories = self.categorize_images(directory, recursive)
        organized = {}

        for item in categories:
            src_path = item["path"]
            category = item["category"]

            if category not in organized:
                organized[category] = []

            organized[category].append(src_path)

        return organized


def get_vision_summary(directory: str) -> Dict[str, Any]:
    """
    Get comprehensive vision analysis summary for directory

    Args:
        directory: Path to analyze

    Returns:
        Summary dict with image counts, categories, and samples
    """
    extractor = VisionExtractor()

    # Find all images
    images = extractor.find_images(directory)

    # Categorize
    categories = extractor.categorize_images(directory)

    # Aggregate by category
    category_counts = {}
    for cat in categories:
        cat_name = cat["category"]
        category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

    return {
        "total_images": len(images),
        "category_distribution": category_counts,
        "analyzed_images": len(categories),
        "categories": categories[:10],  # Sample for display
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        summary = get_vision_summary(sys.argv[1])
        print(f"Images found: {summary['total_images']}")
        print(f"Categories: {summary['category_distribution']}")
    else:
        print("Usage: python vision_extractor.py <directory>")
