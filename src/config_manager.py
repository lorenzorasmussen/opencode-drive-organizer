"""
Configuration Management for Google Drive Organizer

Supports:
- YAML config file with user preferences
- Environment variable overrides
- Command-line defaults
"""

import os
import yaml
import copy
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """Configuration manager with YAML file, env vars, and CLI overrides"""

    DEFAULT_CONFIG = {
        "organize": {
            "auto_threshold": 0.9,
            "dry_run_default": True,
            "disk_safety_gb": 1.0,
            "auto_execute": False,
        },
        "confidence_thresholds": {
            "auto_execute": 0.9,
        },
        "scan": {
            "fast_mode": False,
            "default_recursive": True,
            "max_files": 10000,
        },
        "cloud": {
            "enabled": False,
            "sync_on_scan": False,
            "fetch_metadata": True,
        },
        "ai": {
            "use_ollama": True,
            "use_orchestrator": False,
            "model": "llama2",
            "temperature": 0.7,
        },
        "ollama": {
            "enabled": True,
            "model": "llama2",
        },
        "learning": {
            "enabled": True,
            "data_file": "data/learning-data.json",
            "min_confidence": 0.5,
        },
        "notifications": {
            "enabled": False,
            "desktop": False,
            "sound": True,
        },
        "parallel": {
            "enabled": False,
            "max_workers": 4,
        },
        "paths": {
            "config_dir": "~/.config/gdo",
            "data_dir": "data",
            "logs_dir": "logs",
            "cache_dir": "cache",
        },
        "ui": {
            "progress_bars": True,
            "interactive_mode": False,
            "color_output": True,
        },
        "google_drive": {
            "batch_size": 100,
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager

        Args:
            config_path: Path to config file (default: ~/.config/gdo/config.yaml)
        """
        self.config_path = config_path or os.path.join(
            os.path.expanduser("~"), ".config", "gdo", "config.yaml"
        )
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        self._load_config()
        self._apply_env_overrides()

    def _load_config(self) -> None:
        """Load configuration from YAML file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, "r") as f:
                    user_config = yaml.safe_load(f) or {}
                self._deep_merge(self.config, user_config)
                print(f"✓ Loaded config from {self.config_path}")
            else:
                print(f"⚠️  Config file not found, using defaults: {self.config_path}")
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")

    def _deep_merge(self, base: Dict, user: Dict) -> None:
        """Deep merge user config into base config"""
        for key, value in user.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides"""
        env_mappings = {
            "GDO_AUTO_THRESHOLD": ("organize", "auto_threshold", float),
            "GDO_DRY_RUN": (
                "organize",
                "dry_run_default",
                lambda x: x.lower() == "true",
            ),
            "GDO_FAST_MODE": ("scan", "fast_mode", lambda x: x.lower() == "true"),
            "GDO_DISK_SAFETY_GB": ("organize", "disk_safety_gb", float),
            "GDO_AUTO_EXECUTE": (
                "organize",
                "auto_execute",
                lambda x: x.lower() == "true",
            ),
            "GDO_OLLAMA_MODEL": ("ai", "model", str),
            "GDO_MAX_WORKERS": ("parallel", "max_workers", int),
            "GDO_PROGRESS_BARS": ("ui", "progress_bars", lambda x: x.lower() == "true"),
        }

        for env_key, (section, key, converter) in env_mappings.items():
            env_value = os.environ.get(env_key)
            if env_value:
                try:
                    if section not in self.config:
                        self.config[section] = {}
                    self.config[section][key] = converter(env_value)
                except Exception as e:
                    print(f"⚠️  Invalid env var {env_key}: {e}")

    def get(self, *keys: str, default: Any = None) -> Any:
        """Get config value by key path

        Supports both:
        - get("section.key") - dot notation
        - get("section.key", default) - dot notation with default
        - get("section", "key") - variadic args
        - get("section", "key", default) - variadic args with default
        """
        if len(keys) == 0:
            return default

        if len(keys) == 1:
            if "." in keys[0]:
                keys = tuple(keys[0].split("."))
            else:
                return self.config.get(keys[0], default)

        if len(keys) == 2:
            if "." in keys[0]:
                keys = tuple(keys[0].split("."))
                return self._get_nested(*keys, default=keys[1])
            return self._get_nested(keys[0], keys[1], default=default)

        if len(keys) == 3:
            if "." in keys[0]:
                keys = tuple(keys[0].split(".")) + (keys[1],)
                return self._get_nested(*keys, default=keys[2])
            return self._get_nested(keys[0], keys[1], default=keys[2])

        return self._get_nested(*keys, default=default)

    def _get_nested(self, *keys: str, default: Any = None) -> Any:
        """Internal method to get nested value"""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, *keys: str, value: Any = None) -> None:
        """Set config value by key path

        Supports both:
        - set("section.key", value) - dot notation with positional value
        - set("section", "key", value) - variadic args
        - set("section.key", value=value) - keyword arg
        """
        if value is None:
            if len(keys) == 2 and "." in keys[0]:
                parts = keys[0].split(".")
                value = keys[1]
                keys = tuple(parts)
            elif len(keys) == 3:
                value = keys[2]
                keys = keys[:2]
            else:
                raise ValueError("Value must be provided")

        if len(keys) == 1 and "." in keys[0]:
            keys = tuple(keys[0].split("."))

        current = self.config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def save(self, path: Optional[str] = None) -> None:
        """Save current config to file"""
        save_path = path or self.config_path
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            print(f"✓ Config saved to {save_path}")
        except Exception as e:
            print(f"⚠️  Error saving config: {e}")

    def reset(self) -> None:
        """Reset to default configuration"""
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        self._apply_env_overrides()

    def reset_to_defaults(self) -> None:
        """Reset to default configuration (alias for reset())"""
        self.reset()

    def validate(self) -> Dict[str, Any]:
        """Validate configuration and return results"""
        errors = []

        auto_threshold = self.get("organize", "auto_threshold")
        if auto_threshold is not None and not (0 <= auto_threshold <= 1):
            errors.append(
                f"auto_threshold must be between 0 and 1, got {auto_threshold}"
            )

        confidence_auto_execute = self.get("confidence_thresholds", "auto_execute")
        if confidence_auto_execute is not None and not (
            0 <= confidence_auto_execute <= 1
        ):
            errors.append(
                f"confidence_thresholds.auto_execute must be between 0 and 1, got {confidence_auto_execute}"
            )

        batch_size = self.get("google_drive", "batch_size")
        if batch_size is not None and not (1 <= batch_size <= 1000):
            errors.append(f"batch_size must be between 1 and 1000, got {batch_size}")

        return {"valid": len(errors) == 0, "errors": errors}

    def show(self) -> Dict:
        """Return current configuration"""
        return self.config.copy()

    def create_sample_config(self, path: Optional[str] = None) -> str:
        """Create sample config file and return path"""
        sample_path = path or os.path.join(
            os.path.dirname(self.config_path), "config.example.yaml"
        )
        try:
            with open(sample_path, "w") as f:
                yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False, indent=2)
            return sample_path
        except Exception as e:
            return f"Error: {e}"


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """Get configuration manager instance"""
    return ConfigManager(config_path)
