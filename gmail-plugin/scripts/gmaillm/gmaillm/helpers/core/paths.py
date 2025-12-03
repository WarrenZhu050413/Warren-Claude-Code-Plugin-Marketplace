"""Path and directory management for gmaillm configuration."""

from pathlib import Path


def get_plugin_config_dir() -> Path:
    """Get the plugin config directory path.

    Always uses ~/.gmaillm/ for consistency with credentials storage.

    Returns:
        Path to config directory (~/.gmaillm/)
    """
    config_dir = Path.home() / ".gmaillm"
    config_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
    return config_dir


def get_groups_dir() -> Path:
    """Get the email groups directory path.

    Returns:
        Path to email groups directory
    """
    config_dir = get_plugin_config_dir()
    groups_dir = config_dir / "email-groups"
    groups_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
    return groups_dir


def get_groups_file_path() -> Path:
    """Get path to email groups file.

    Returns:
        Path to groups.json
    """
    groups_dir = get_groups_dir()
    return groups_dir / "groups.json"


def get_styles_dir() -> Path:
    """Get the email styles directory path.

    Returns:
        Path to email styles directory
    """
    config_dir = get_plugin_config_dir()
    styles_dir = config_dir / "email-styles"
    styles_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
    return styles_dir


def get_style_file_path(name: str) -> Path:
    """Get path to a specific style file.

    Args:
        name: Style name

    Returns:
        Path to style file
    """
    styles_dir = get_styles_dir()
    return styles_dir / f"{name}.md"
