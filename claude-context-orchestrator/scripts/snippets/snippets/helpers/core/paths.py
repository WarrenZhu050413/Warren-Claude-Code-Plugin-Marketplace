"""Path resolution and discovery utilities."""

import os
from pathlib import Path
from typing import Dict, List, Set, Tuple


def get_default_config_path() -> Path:
    """Get default configuration file path.

    Returns:
        Path to config.json in the snippets directory
    """
    script_dir = Path(__file__).parent.parent.parent  # Go up to snippets/
    warren_plugin_base = (
        Path.home()
        / ".claude"
        / "plugins"
        / "marketplaces"
        / "warren-claude-code-plugin-marketplace"
        / "claude-context-orchestrator"
    )

    # Check Warren's plugin location first
    if (warren_plugin_base / "scripts" / "snippets" / "config.json").exists():
        return warren_plugin_base / "scripts" / "snippets" / "config.json"

    # Fallback to script directory
    return script_dir / "config.json"


def get_default_snippets_dir() -> Path:
    """Get default snippets directory.

    Returns:
        Path to snippets/local directory
    """
    script_dir = Path(__file__).parent.parent.parent  # Go up to snippets/
    warren_plugin_base = (
        Path.home()
        / ".claude"
        / "plugins"
        / "marketplaces"
        / "warren-claude-code-plugin-marketplace"
        / "claude-context-orchestrator"
    )

    # Check Warren's plugin location first
    if (warren_plugin_base / "snippets" / "local").exists():
        return warren_plugin_base / "snippets" / "local"

    # Fallback to relative path from script directory
    return script_dir.parent.parent / "snippets" / "local"


def discover_categories(config: Dict) -> Dict[str, Dict]:
    """Dynamically discover snippet categories from configuration.

    Parses snippet file paths to extract categories and group them.

    Args:
        config: Configuration dictionary containing mappings

    Returns:
        Dictionary mapping category names to their metadata:
        {
            "category_name": {
                "paths": ["path1", "path2", ...],
                "count": 3
            }
        }
    """
    discovered_paths: Set[Tuple[str, str]] = set()

    for mapping in config.get("mappings", []):
        snippet_files = mapping.get("snippet", [])
        if isinstance(snippet_files, str):
            snippet_files = [snippet_files]

        for snippet_file in snippet_files:
            snippet_path = Path(snippet_file)
            parts = snippet_path.parts

            # Find base directory and category
            if "snippets" in parts and "local" in parts:
                # Format: snippets/local/category/name/SKILL.md
                try:
                    local_idx = parts.index("local")
                    if local_idx + 1 < len(parts):
                        category = parts[local_idx + 1]
                        full_path = str(snippet_path.parent)
                        discovered_paths.add((category, full_path))
                except (ValueError, IndexError):
                    pass
            elif "skills" in parts:
                # Format: ../skills/skill-name/SKILL.md
                try:
                    skills_idx = parts.index("skills")
                    if skills_idx + 1 < len(parts):
                        skill_name = parts[skills_idx + 1]
                        full_path = str(snippet_path.parent)
                        discovered_paths.add(("skills", full_path))
                except (ValueError, IndexError):
                    pass

    # Group by category and collect unique paths
    categories: Dict[str, Dict] = {}
    for category, path in sorted(discovered_paths):
        if category not in categories:
            categories[category] = {"paths": [], "count": 0}
        categories[category]["paths"].append(path)
        categories[category]["count"] += 1

    return categories


def resolve_snippet_path(snippet_file: str, base_dir: Path) -> Path:
    """Resolve a snippet file path relative to base directory.

    Args:
        snippet_file: Snippet file path (relative or absolute)
        base_dir: Base directory for resolution

    Returns:
        Resolved absolute path
    """
    snippet_path = Path(snippet_file)

    # If already absolute, return as-is
    if snippet_path.is_absolute():
        return snippet_path

    # Try relative to base_dir first
    resolved = base_dir / snippet_path
    if resolved.exists():
        return resolved.resolve()

    # Try relative to current working directory
    resolved = Path.cwd() / snippet_path
    if resolved.exists():
        return resolved.resolve()

    # Return as-is if nothing works (will fail later with clear error)
    return snippet_path


def get_plugin_root() -> Path:
    """Get the plugin root directory.

    Returns:
        Path to plugin root (claude-context-orchestrator/)
    """
    warren_plugin_base = (
        Path.home()
        / ".claude"
        / "plugins"
        / "marketplaces"
        / "warren-claude-code-plugin-marketplace"
        / "claude-context-orchestrator"
    )

    if warren_plugin_base.exists():
        return warren_plugin_base

    # Fallback to relative path from script directory
    script_dir = Path(__file__).parent.parent.parent  # Go up to snippets/
    return script_dir.parent.parent  # Go up to plugin root
