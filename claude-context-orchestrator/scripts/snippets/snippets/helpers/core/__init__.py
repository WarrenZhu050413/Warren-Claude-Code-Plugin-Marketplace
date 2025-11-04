"""Core utilities for snippets management."""

from .config import (
    add_mapping,
    find_mapping_by_pattern,
    load_config_file,
    load_merged_config,
    merge_configs,
    remove_mapping,
    save_config_file,
    update_mapping,
)
from .paths import (
    discover_categories,
    get_default_config_path,
    get_default_snippets_dir,
    get_plugin_root,
    resolve_snippet_path,
)

__all__ = [
    # Config
    "add_mapping",
    "find_mapping_by_pattern",
    "load_config_file",
    "load_merged_config",
    "merge_configs",
    "remove_mapping",
    "save_config_file",
    "update_mapping",
    # Paths
    "discover_categories",
    "get_default_config_path",
    "get_default_snippets_dir",
    "get_plugin_root",
    "resolve_snippet_path",
]
