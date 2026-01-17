"""
Configuration management for Google Drive Organizer
"""

import os
import json
import yaml
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Configuration management with YAML/JSON support

    Features:
    - Load/save settings from YAML
    - Get configuration values
    - Set configuration values
    - Environment variable overrides
    - Configuration validation
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config manager

        Args:
            config_path: Path to config file (default: config/settings.yaml)
        """
        self.config_path = config_path or "config/settings.yaml"
        self.config = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"⚠️  Error loading config: {e}")
                self.config = {}
        else:
            self.config = self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "confidence_thresholds": {"auto_execute": 0.9, "review": 0.5, "skip": 0.5},
            "performance": {
                "enable_xxhash": True,
                "disk_monitor_enable": True,
                "disk_threshold_percent": 90,
            },
            "tools": {
                "fd_enabled": True,
                "fzf_enabled": True,
                "ripgrep_enabled": True,
                "nnn_enabled": True,
            },
            "ollama": {
                "enabled": True,
                "model": "llama2",
                "temperature": 0.3,
                "api_url": "http://localhost:11434",
            },
            "learning": {
                "enabled": True,
                "learning_file_path": "data/learning-data.json",
            },
            "google_drive": {
                "credentials_path": "config/credentials.json",
                "batch_size": 100,
            },
            "automation": {
                "schedule_scan": "weekly",
                "schedule_organization": "weekly",
                "schedule_archiving": "monthly",
                "auto_cleanup_days": 7,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key (supports dot notation, e.g., 'ollama.model')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        if keys:
            config[keys[-1]] = value

    def save(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        with open(self.config_path, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

        print(f"✓ Configuration saved to {self.config_path}")

    def validate(self) -> Dict:
        """
        Validate configuration

        Returns:
            Dict with 'valid' bool and 'errors' list
        """
        errors = []

        # Validate confidence thresholds
        thresholds = self.get("confidence_thresholds", {})
        if thresholds:
            if not (0 <= thresholds.get("auto_execute", 0.9) <= 1.0):
                errors.append("auto_execute must be between 0 and 1")
            if not (0 <= thresholds.get("review", 0.5) <= 1.0):
                errors.append("review must be between 0 and 1")
            if not (0 <= thresholds.get("skip", 0.5) <= 1.0):
                errors.append("skip must be between 0 and 1")

        # Validate batch size
        batch_size = self.get("google_drive.batch_size", 100)
        if batch_size < 1 or batch_size > 1000:
            errors.append("batch_size must be between 1 and 1000")

        return {"valid": len(errors) == 0, "errors": errors}

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self._get_default_config()
        self.save()
