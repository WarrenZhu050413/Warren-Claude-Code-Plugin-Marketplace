"""Core snippets management client.

This module provides the SnippetsClient class which handles all business logic
for managing Claude Code snippets. It is CLI-agnostic and can be used programmatically.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .helpers.core import (
    discover_categories,
    get_default_config_path,
    get_default_snippets_dir,
    save_config_file,
)
from .models import (
    CategoryInfo,
    ConfigFileInfo,
    PathsResponse,
    SearchResult,
    SnippetInfo,
    ValidationResult,
)
from .validators import validate_full_config, validate_regex_pattern


class SnippetError(Exception):
    """Base exception for snippet operations."""

    def __init__(self, code: str, message: str, details: Dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class SnippetsClient:
    """Core snippets management client.

    Handles all CRUD operations for snippets configuration and files.
    Supports multi-config system with base, local, and named configs.
    """

    # Default priorities for standard config files
    DEFAULT_PRIORITIES = {
        "config.json": 0,
        "config.local.json": 100,
    }

    def __init__(
        self,
        config_path: Optional[Path] = None,
        snippets_dir: Optional[Path] = None,
        use_base_config: bool = False,
        config_name: Optional[str] = None,
    ):
        """Initialize snippets client.

        Args:
            config_path: Path to base config file (default: auto-detect)
            snippets_dir: Path to snippets directory (default: auto-detect)
            use_base_config: If True, modify base config instead of local
            config_name: Named config to target (e.g., 'work' for config.work.json)
        """
        self.config_path = config_path or get_default_config_path()
        self.snippets_dir = snippets_dir or get_default_snippets_dir()
        self.use_base_config = use_base_config
        self.config_name = config_name
        self.local_config_path = self.config_path.parent / "config.local.json"

        # Load all configs with priority information
        self.all_configs = self._load_all_configs()
        self.config = self._get_merged_config()

        # Determine target config for modifications
        if config_name:
            # Target specific named config
            target_filename = f"config.{config_name}.json"
            self.target_config_path = self.config_path.parent / target_filename
            self.target_config = self._load_single_config(self.target_config_path, config_name)
        elif use_base_config:
            # Target base config
            self.target_config_path = self.config_path
            self.target_config = self._load_single_config(self.config_path, "base")
        else:
            # Target local config (default)
            self.target_config_path = self.local_config_path
            self.target_config = self._load_single_config(self.local_config_path, "local")

    def _load_single_config(self, path: Path, name: str) -> Dict:
        """Load a single config file.

        Args:
            path: Path to config file
            name: Config name for error messages

        Returns:
            Configuration dictionary

        Raises:
            SnippetError: If config file is invalid JSON
        """
        config = {"mappings": []}
        if path.exists():
            try:
                with open(path, encoding='utf-8') as f:
                    config = json.load(f)
                    if "mappings" not in config:
                        config["mappings"] = []
            except json.JSONDecodeError as e:
                raise SnippetError(
                    "CONFIG_ERROR",
                    f"Invalid JSON in {name} config file: {e}",
                    {"path": str(path)},
                )
        return config

    def _load_all_configs(self) -> List[Dict]:
        """Load all config*.json files with priority information.

        Returns:
            List of config dictionaries with metadata

        Raises:
            SnippetError: If base config file is malformed
        """
        config_files = []
        config_dir = self.config_path.parent

        # Find all config*.json files
        for config_path in sorted(config_dir.glob("config*.json")):
            try:
                with open(config_path, encoding='utf-8') as f:
                    config_data = json.load(f)

                # Determine priority
                filename = config_path.name
                if filename in self.DEFAULT_PRIORITIES:
                    # Use default priority, but allow override from file
                    priority = config_data.get("priority", self.DEFAULT_PRIORITIES[filename])
                else:
                    # Custom config files default to 50
                    priority = config_data.get("priority", 50)

                config_files.append({
                    "path": config_path,
                    "filename": filename,
                    "priority": priority,
                    "data": config_data,
                })
            except (json.JSONDecodeError, KeyError) as e:
                # Raise error for base config, skip others
                if config_path == self.config_path:
                    raise SnippetError(
                        "CONFIG_ERROR",
                        f"Invalid JSON in base config file: {e}",
                        {"path": str(config_path)},
                    )
                # Skip other malformed config files
                continue

        # Sort by priority (ascending)
        config_files.sort(key=lambda x: x["priority"])
        return config_files

    def _get_merged_config(self) -> Dict:
        """Get merged config from all configs by priority.

        Returns:
            Merged configuration dictionary
        """
        merged_mappings = {}

        # Merge all configs by snippet name (higher priority comes later and overwrites)
        for config_file in self.all_configs:
            for mapping in config_file["data"].get("mappings", []):
                name = mapping.get("name", "")
                if name:
                    # Store mapping with source info
                    mapping_copy = mapping.copy()
                    mapping_copy["_source_config"] = config_file["filename"]
                    mapping_copy["_source_priority"] = config_file["priority"]
                    merged_mappings[name] = mapping_copy

        return {"mappings": list(merged_mappings.values())}

    def _save_config(self):
        """Save config changes to target config file."""
        target_path = self.target_config_path

        # Create backup if file exists
        if target_path.exists():
            backup_path = target_path.with_suffix('.json.bak')
            shutil.copy2(target_path, backup_path)

        # Save config
        save_config_file(target_path, self.target_config)

        # Reload merged config to reflect changes
        self._reload_configs()

    def _reload_configs(self):
        """Reload and merge all config files."""
        self.all_configs = self._load_all_configs()
        self.config = self._get_merged_config()

    def _find_snippet(self, name: str) -> Optional[Dict]:
        """Find snippet in merged config by name.

        Args:
            name: Snippet name

        Returns:
            Snippet mapping dictionary or None
        """
        for mapping in self.config["mappings"]:
            if mapping.get("name") == name:
                return mapping
        return None

    def _find_in_target_config(self, name: str) -> Optional[Dict]:
        """Find snippet in target config by name.

        Args:
            name: Snippet name

        Returns:
            Snippet mapping dictionary or None
        """
        for mapping in self.target_config["mappings"]:
            if mapping.get("name") == name:
                return mapping
        return None

    def _get_snippet_path(self, name: str) -> Path:
        """Get file path for snippet.

        Args:
            name: Snippet name

        Returns:
            Path to snippet file
        """
        return self.snippets_dir / f"{name}.md"

    # ============ PUBLIC API ============

    def create(
        self,
        name: str,
        pattern: str,
        description: str,
        content: Optional[str] = None,
        priority: int = 0,
    ) -> SnippetInfo:
        """Create a new snippet.

        Args:
            name: Snippet name (identifier)
            pattern: Regex pattern to trigger snippet
            description: Brief description of snippet purpose
            content: Snippet content (optional, default template used)
            priority: Priority for pattern matching (default: 0)

        Returns:
            SnippetInfo for created snippet

        Raises:
            SnippetError: If snippet already exists or validation fails
        """
        # Validate pattern
        is_valid, error_msg = validate_regex_pattern(pattern)
        if not is_valid:
            raise SnippetError("INVALID_PATTERN", error_msg)

        # Check if snippet already exists in merged config OR target config
        if self._find_snippet(name) or self._find_in_target_config(name):
            raise SnippetError(
                "SNIPPET_EXISTS",
                f"Snippet '{name}' already exists",
                {"name": name},
            )

        # Create snippet file
        snippet_path = self._get_snippet_path(name)
        snippet_path.parent.mkdir(parents=True, exist_ok=True)

        if content is None:
            # Use default template
            content = f"""---
name: {name}
description: {description}
---

# {name}

{description}

[Add snippet content here]
"""

        # Write file
        with open(snippet_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Add to config
        self.target_config["mappings"].append({
            "name": name,
            "pattern": pattern,
            "snippet": [str(snippet_path)],
            "priority": priority,
        })
        self._save_config()

        return SnippetInfo(
            name=name,
            path=str(snippet_path),
            pattern=pattern,
            priority=priority,
        )

    def list_snippets(
        self,
        name: Optional[str] = None,
        show_content: bool = False,
    ) -> List[SnippetInfo]:
        """List all snippets or get details for specific snippet.

        Args:
            name: Optional snippet name to filter
            show_content: Whether to include content in results

        Returns:
            List of SnippetInfo objects
        """
        results = []

        for mapping in self.config["mappings"]:
            snippet_name = mapping.get("name", "")
            if name and snippet_name != name:
                continue

            snippet_files = mapping.get("snippet", [])
            if isinstance(snippet_files, str):
                snippet_files = [snippet_files]

            for snippet_file in snippet_files:
                snippet_path = Path(snippet_file)

                # Resolve path: check if absolute first, then try relative paths
                if not snippet_path.is_absolute():
                    # Try multiple resolution strategies
                    candidates = [
                        (self.config_path.parent / snippet_file).resolve(),  # Relative to config file
                        (self.snippets_dir.parent.parent / snippet_file).resolve(),  # Relative to plugin root
                        (self.snippets_dir / snippet_file).resolve(),  # Relative to snippets_dir
                        (Path.cwd() / snippet_file).resolve(),  # Relative to current directory
                    ]

                    # Smart fallback: if path contains 'snippets/', try from plugin root
                    import re
                    if match := re.search(r'\.\.?/?(snippets/.+)$', snippet_file):
                        candidates.append((self.snippets_dir.parent.parent / match.group(1)).resolve())

                    for candidate in candidates:
                        if candidate.exists():
                            snippet_path = candidate
                            break

                results.append(SnippetInfo(
                    name=snippet_name,
                    path=str(snippet_path.resolve()),
                    pattern=mapping.get("pattern"),
                    priority=mapping.get("priority", 0),
                ))

        return results

    def search(self, query: str) -> SearchResult:
        """Search snippets by keyword.

        Args:
            query: Search keyword

        Returns:
            SearchResult with matching snippets
        """
        query_lower = query.lower()
        matches = []

        for mapping in self.config["mappings"]:
            name = mapping.get("name", "")
            pattern = mapping.get("pattern", "")

            # Read snippet file content to search description
            snippet_files = mapping.get("snippet", [])
            if isinstance(snippet_files, str):
                snippet_files = [snippet_files]

            # Check name and pattern first
            if query_lower in name.lower() or query_lower in pattern.lower():
                for snippet_file in snippet_files:
                    snippet_path = Path(snippet_file)
                    if not snippet_path.is_absolute():
                        # Try multiple resolution strategies
                        candidates = [
                            (self.config_path.parent / snippet_file).resolve(),  # Relative to config file
                            (self.snippets_dir.parent.parent / snippet_file).resolve(),  # Relative to plugin root
                            (self.snippets_dir / snippet_file).resolve(),  # Relative to snippets_dir
                            (Path.cwd() / snippet_file).resolve(),  # Relative to current directory
                        ]

                        # Smart fallback: if path contains 'snippets/', try from plugin root
                        import re
                        if match := re.search(r'\.\.?/?(snippets/.+)$', snippet_file):
                            candidates.append((self.snippets_dir.parent.parent / match.group(1)).resolve())

                        for candidate in candidates:
                            if candidate.exists():
                                snippet_path = candidate
                                break

                    matches.append(SnippetInfo(
                        name=name,
                        path=str(snippet_path.resolve()),
                        pattern=pattern,
                        priority=mapping.get("priority", 0),
                    ))

        return SearchResult(
            query=query,
            matches=matches,
            total_searched=len(self.config["mappings"]),
        )

    def update(
        self,
        name: str,
        pattern: Optional[str] = None,
        content: Optional[str] = None,
    ) -> SnippetInfo:
        """Update an existing snippet.

        Args:
            name: Snippet name
            pattern: New pattern (optional)
            content: New content (optional)

        Returns:
            Updated SnippetInfo

        Raises:
            SnippetError: If snippet not found or validation fails
        """
        # Find snippet
        mapping = self._find_in_target_config(name)
        if not mapping:
            raise SnippetError(
                "SNIPPET_NOT_FOUND",
                f"Snippet '{name}' not found",
                {"name": name},
            )

        # Update pattern if provided
        if pattern is not None:
            is_valid, error_msg = validate_regex_pattern(pattern)
            if not is_valid:
                raise SnippetError("INVALID_PATTERN", error_msg)
            mapping["pattern"] = pattern

        # Update content if provided
        if content is not None:
            snippet_files = mapping.get("snippet", [])
            if isinstance(snippet_files, str):
                snippet_files = [snippet_files]

            for snippet_file in snippet_files:
                snippet_path = Path(snippet_file)
                if not snippet_path.is_absolute():
                    snippet_path = self.snippets_dir / snippet_file

                with open(snippet_path, 'w', encoding='utf-8') as f:
                    f.write(content)

        self._save_config()

        snippet_path = self._get_snippet_path(name)
        return SnippetInfo(
            name=name,
            path=str(snippet_path),
            pattern=mapping.get("pattern"),
            priority=mapping.get("priority", 0),
        )

    def delete(
        self,
        name: str,
        force: bool = False,
        backup: bool = True,
    ) -> Dict:
        """Delete a snippet.

        Args:
            name: Snippet name
            force: Skip confirmation
            backup: Create backup before deletion

        Returns:
            Dictionary with deletion details

        Raises:
            SnippetError: If snippet not found
        """
        # Find snippet
        mapping = self._find_in_target_config(name)
        if not mapping:
            raise SnippetError(
                "SNIPPET_NOT_FOUND",
                f"Snippet '{name}' not found",
                {"name": name},
            )

        snippet_files = mapping.get("snippet", [])
        if isinstance(snippet_files, str):
            snippet_files = [snippet_files]

        # Backup files if requested
        backup_paths = []
        if backup:
            for snippet_file in snippet_files:
                snippet_path = Path(snippet_file)
                if not snippet_path.is_absolute():
                    snippet_path = self.snippets_dir / snippet_file

                if snippet_path.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = snippet_path.with_suffix(f'.md.backup.{timestamp}')
                    shutil.copy2(snippet_path, backup_path)
                    backup_paths.append(str(backup_path))

        # Remove from config
        self.target_config["mappings"] = [
            m for m in self.target_config["mappings"]
            if m.get("name") != name
        ]
        self._save_config()

        # Delete files
        deleted_files = []
        for snippet_file in snippet_files:
            snippet_path = Path(snippet_file)
            if not snippet_path.is_absolute():
                snippet_path = self.snippets_dir / snippet_file

            if snippet_path.exists():
                snippet_path.unlink()
                deleted_files.append(str(snippet_path))

        return {
            "name": name,
            "deleted_files": deleted_files,
            "backup_paths": backup_paths,
        }

    def validate(self) -> ValidationResult:
        """Validate configuration.

        Returns:
            ValidationResult with any errors found
        """
        # Use config file's parent directory (scripts/) as base_dir for path resolution
        # This matches snippet_injector.py's PLUGIN_ROOT behavior
        config_base_dir = self.config_path.parent.parent  # scripts/snippets -> scripts
        errors = validate_full_config(self.config, config_base_dir)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            total_mappings=len(self.config["mappings"]),
        )

    def show_paths(self, filter_term: Optional[str] = None) -> PathsResponse:
        """Show available snippet locations and categories.

        Args:
            filter_term: Optional filter for categories

        Returns:
            PathsResponse with configuration structure
        """
        # Discover categories from config
        categories_dict = discover_categories(self.config)

        # Filter if requested
        if filter_term:
            categories_dict = {
                k: v
                for k, v in categories_dict.items()
                if filter_term.lower() in k.lower()
            }

        # Build config files list
        config_files = [
            ConfigFileInfo(
                path=str(self.config_path),
                priority=0,
                type="base",
            )
        ]

        if self.local_config_path.exists():
            config_files.append(
                ConfigFileInfo(
                    path=str(self.local_config_path),
                    priority=100,
                    type="local",
                )
            )

        # Build categories list
        categories = [
            CategoryInfo(
                name=name,
                snippet_count=info["count"],
                sample_paths=info["paths"][:3],  # Show up to 3 samples
            )
            for name, info in sorted(categories_dict.items())
        ]

        # Use scripts/ as base_dir to match snippet_injector.py's PLUGIN_ROOT
        config_base_dir = self.config_path.parent.parent  # scripts/snippets -> scripts

        return PathsResponse(
            config_files=config_files,
            base_dir=str(config_base_dir),
            categories=categories,
        )
