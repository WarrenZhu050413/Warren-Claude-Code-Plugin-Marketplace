"""Configuration loading and management utilities."""

import json
from pathlib import Path
from typing import Dict, List, Optional


def load_config_file(config_path: Path) -> Dict:
    """Load a single configuration file.

    Args:
        config_path: Path to config JSON file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, encoding='utf-8') as f:
        return json.load(f)


def save_config_file(config_path: Path, config: Dict) -> None:
    """Save configuration to file.

    Args:
        config_path: Path to config JSON file
        config: Configuration dictionary to save
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Add trailing newline


def merge_configs(base_config: Dict, local_config: Optional[Dict]) -> Dict:
    """Merge base and local configurations.

    Local config mappings are added after base config mappings,
    so they have effective higher priority in pattern matching.

    Args:
        base_config: Base configuration
        local_config: Local configuration override (optional)

    Returns:
        Merged configuration dictionary
    """
    if not local_config:
        return base_config.copy()

    merged = base_config.copy()

    # Merge mappings: base first, then local
    base_mappings = base_config.get("mappings", [])
    local_mappings = local_config.get("mappings", [])
    merged["mappings"] = base_mappings + local_mappings

    # Merge other top-level keys (prefer local)
    for key, value in local_config.items():
        if key != "mappings":
            merged[key] = value

    return merged


def load_merged_config(config_path: Path, local_config_path: Optional[Path] = None) -> Dict:
    """Load and merge base and local configurations.

    Args:
        config_path: Path to base config file
        local_config_path: Path to local config file (optional)

    Returns:
        Merged configuration dictionary
    """
    base_config = load_config_file(config_path)

    local_config = None
    if local_config_path and local_config_path.exists():
        try:
            local_config = load_config_file(local_config_path)
        except (FileNotFoundError, json.JSONDecodeError):
            # Local config is optional, ignore errors
            pass

    return merge_configs(base_config, local_config)


def find_mapping_by_pattern(config: Dict, pattern: str) -> Optional[Dict]:
    """Find a mapping entry by pattern.

    Args:
        config: Configuration dictionary
        pattern: Pattern to search for

    Returns:
        Mapping dictionary if found, None otherwise
    """
    for mapping in config.get("mappings", []):
        if mapping.get("pattern") == pattern:
            return mapping
    return None


def add_mapping(config: Dict, pattern: str, snippet: List[str], priority: int = 0) -> Dict:
    """Add a new mapping to configuration.

    Args:
        config: Configuration dictionary
        pattern: Regex pattern
        snippet: List of snippet file paths
        priority: Priority value (default: 0)

    Returns:
        Updated configuration dictionary
    """
    new_mapping = {
        "pattern": pattern,
        "snippet": snippet,
        "priority": priority
    }

    if "mappings" not in config:
        config["mappings"] = []

    config["mappings"].append(new_mapping)
    return config


def remove_mapping(config: Dict, pattern: str) -> Dict:
    """Remove a mapping from configuration.

    Args:
        config: Configuration dictionary
        pattern: Pattern to remove

    Returns:
        Updated configuration dictionary
    """
    if "mappings" in config:
        config["mappings"] = [
            m for m in config["mappings"]
            if m.get("pattern") != pattern
        ]
    return config


def update_mapping(config: Dict, pattern: str, updates: Dict) -> Dict:
    """Update an existing mapping.

    Args:
        config: Configuration dictionary
        pattern: Pattern to update
        updates: Dictionary of fields to update

    Returns:
        Updated configuration dictionary
    """
    for mapping in config.get("mappings", []):
        if mapping.get("pattern") == pattern:
            mapping.update(updates)
            break
    return config
