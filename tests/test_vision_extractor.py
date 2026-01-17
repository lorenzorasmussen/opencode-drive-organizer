"""
Test-driven development for Feature 2: Vision Model Image Categorization
"""

import pytest
import os
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_vision_extractor_initialization():
    """Verify vision extractor can be initialized"""
    from src.vision_extractor import VisionExtractor

    extractor = VisionExtractor()
    assert extractor is not None


def test_vision_detects_images():
    """Verify extractor identifies image files"""
    from src.vision_extractor import VisionExtractor

    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "photo.jpg").write_bytes(b"fake jpg content")
        (Path(tmpdir) / "image.png").write_bytes(b"fake png content")
        (Path(tmpdir) / "document.txt").write_text("not an image")

        extractor = VisionExtractor()
        images = extractor.find_images(tmpdir)

        assert len(images) == 2
        assert any("photo.jpg" in img for img in images)
        assert any("image.png" in img for img in images)


def test_vision_basic_analysis():
    """Verify extractor does basic analysis without vision model"""
    from src.vision_extractor import VisionExtractor

    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "trip_to_paris.jpg").write_bytes(b"fake jpg content")

        extractor = VisionExtractor()
        # Don't use actual Ollama - just test basic analysis
        analysis = extractor._basic_image_analysis(
            str(Path(tmpdir) / "trip_to_paris.jpg")
        )

        assert "description" in analysis
        assert "tags" in analysis
        assert "category" in analysis
        # Filename contains "trip" which should trigger travel category
        assert analysis["category"] == "travel"


def test_vision_categorizes_images():
    """Verify extractor categorizes images by content"""
    from src.vision_extractor import VisionExtractor

    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "vacation.jpg").write_bytes(b"fake jpg")
        (Path(tmpdir) / "work_presentation.jpg").write_bytes(b"fake jpg")

        extractor = VisionExtractor()

        # Test basic analysis for each
        results = []
        for img in [
            (Path(tmpdir) / "vacation.jpg"),
            (Path(tmpdir) / "work_presentation.jpg"),
        ]:
            analysis = extractor._basic_image_analysis(str(img))
            results.append(
                {
                    "path": str(img),
                    "category": analysis.get("category"),
                    "confidence": analysis.get("confidence"),
                }
            )

        assert len(results) == 2
        # vacation.jpg should be categorized as travel
        assert any(r["category"] == "travel" for r in results)
        # work_presentation.jpg should be categorized as work
        assert any(r["category"] == "work" for r in results)


def test_vision_extracts_image_metadata():
    """Verify extractor extracts image metadata"""
    from src.vision_extractor import VisionExtractor

    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "photo.jpg").write_bytes(b"fake jpg content")

        extractor = VisionExtractor()
        metadata = extractor.extract_image_metadata(str(Path(tmpdir) / "photo.jpg"))

        assert "file_path" in metadata
        assert "file_name" in metadata
        assert "file_size" in metadata
        assert "format" in metadata
        # Without Pillow, dimensions will be None
        assert "width" in metadata
        assert "height" in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
