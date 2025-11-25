"""Core infrastructure for gmaillm helpers."""

from gmaillm.helpers.core.io import create_backup, load_json_config, save_json_config
from gmaillm.helpers.core.paths import (
    get_groups_dir,
    get_groups_file_path,
    get_plugin_config_dir,
    get_style_file_path,
    get_styles_dir,
)

__all__ = [
    # I/O operations
    "load_json_config",
    "save_json_config",
    "create_backup",
    # Path management
    "get_plugin_config_dir",
    "get_groups_dir",
    "get_groups_file_path",
    "get_styles_dir",
    "get_style_file_path",
]
