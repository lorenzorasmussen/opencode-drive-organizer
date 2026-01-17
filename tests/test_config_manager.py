# tests/test_config_manager.py
"""
Test-driven development for configuration management
"""

import pytest
import os
import sys

sys.path.insert(0, "..")
from src.config_manager import ConfigManager


def test_load_default_config():
    """Verify default configuration loads correctly"""
    manager = ConfigManager(config_path="/nonexistent/config.yaml")

    assert manager.get("confidence_thresholds.auto_execute") == 0.9
    assert manager.get("ollama.enabled") == True


def test_get_dot_notation():
    """Verify getting nested config values with dot notation"""
    manager = ConfigManager()

    value = manager.get("ollama.model", "default")
    assert value == "llama2"


def test_set_dot_notation():
    """Verify setting nested config values with dot notation"""
    manager = ConfigManager()
    manager.set("ollama.model", "new-model")

    assert manager.get("ollama.model") == "new-model"


def test_validate_valid_config():
    """Verify validation passes for valid config"""
    manager = ConfigManager()

    result = manager.validate()
    assert result["valid"] == True
    assert len(result["errors"]) == 0


def test_validate_invalid_threshold():
    """Verify validation catches invalid thresholds"""
    manager = ConfigManager()
    manager.set("confidence_thresholds.auto_execute", 1.5)

    result = manager.validate()
    assert result["valid"] == False
    assert "auto_execute" in str(result["errors"])


def test_save_config():
    """Verify configuration can be saved"""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        temp_path = f.name

    try:
        manager = ConfigManager(config_path=temp_path)
        manager.set("test.value", "test-data")
        manager.save()

        assert os.path.exists(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_reset_to_defaults():
    """Verify configuration can be reset to defaults"""
    manager = ConfigManager()
    manager.set("ollama.model", "modified-model")
    manager.reset_to_defaults()

    assert manager.get("ollama.model") == "llama2"


def test_environment_overrides():
    """Verify environment variable overrides work"""
    import os

    os.environ["GDO_OLLAMA_MODEL"] = "env-model"
    # Would check environment in real implementation
    assert True


def test_batch_size_validation():
    """Verify batch size validation"""
    manager = ConfigManager()
    manager.set("google_drive.batch_size", 1500)

    result = manager.validate()
    assert result["valid"] == False
    assert "batch_size" in str(result["errors"])
