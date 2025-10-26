#!/usr/bin/env python3
"""
Claude Code Snippets CLI

A rigid, testable CLI for CRUD operations on snippet configurations.
Designed to be wrapped by LLM-enabled commands for intelligent UX.
"""

import argparse
import json
import re
import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import shutil


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output"""
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    DIM = '\033[2m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @staticmethod
    def enabled():
        """Check if colors should be enabled (TTY and not piped)"""
        return sys.stdout.isatty()

    @classmethod
    def cyan(cls, text):
        return f"{cls.CYAN}{text}{cls.RESET}" if cls.enabled() else text

    @classmethod
    def yellow(cls, text):
        return f"{cls.YELLOW}{text}{cls.RESET}" if cls.enabled() else text

    @classmethod
    def green(cls, text):
        return f"{cls.GREEN}{text}{cls.RESET}" if cls.enabled() else text

    @classmethod
    def red(cls, text):
        return f"{cls.RED}{text}{cls.RESET}" if cls.enabled() else text

    @classmethod
    def dim(cls, text):
        return f"{cls.DIM}{text}{cls.RESET}" if cls.enabled() else text

    @classmethod
    def bold(cls, text):
        return f"{cls.BOLD}{text}{cls.RESET}" if cls.enabled() else text


# Template for Agent Skills format
ANNOUNCEMENT_TEMPLATE = """---
name: {name}
description: {description}
---

"""


class SnippetError(Exception):
    """Base exception for snippet operations"""
    def __init__(self, code: str, message: str, details: Dict[str, Any] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class SnippetManager:
    """Core snippet management functionality with multi-config support"""

    # Default priorities for standard config files
    DEFAULT_PRIORITIES = {
        "config.json": 0,
        "config.local.json": 100,
    }

    def __init__(self, config_path: Path, snippets_dir: Path, use_base_config: bool = False,
                 config_name: str = None):
        self.config_path = config_path
        self.snippets_dir = snippets_dir
        self.use_base_config = use_base_config
        self.config_name = config_name  # Named config to target (e.g., 'work' for config.work.json)
        self.local_config_path = config_path.parent / "config.local.json"

        # Load all configs with priority information
        self.all_configs = self._load_all_configs()
        self.config = self._get_merged_config()

        # Determine target config for modifications
        if config_name:
            # Target specific named config
            target_filename = f"config.{config_name}.json"
            self.target_config_path = config_path.parent / target_filename
            self.target_config = self._load_single_config(self.target_config_path, config_name)
        elif use_base_config:
            # Target base config
            self.target_config_path = config_path
            self.target_config = self._load_single_config(config_path, "base")
        else:
            # Target local config (default)
            self.target_config_path = self.local_config_path
            self.target_config = self._load_single_config(self.local_config_path, "local")

    def _load_single_config(self, path: Path, name: str) -> Dict:
        """Load a single config file"""
        config = {"mappings": []}
        if path.exists():
            try:
                with open(path) as f:
                    config = json.load(f)
                    if "mappings" not in config:
                        config["mappings"] = []
            except json.JSONDecodeError as e:
                raise SnippetError(
                    "CONFIG_ERROR",
                    f"Invalid JSON in {name} config file: {e}",
                    {"path": str(path)}
                )
        return config

    def _load_all_configs(self) -> List[Dict]:
        """Load all config*.json files with priority information"""
        config_files = []
        config_dir = self.config_path.parent

        # Find all config*.json files
        for config_path in sorted(config_dir.glob("config*.json")):
            try:
                with open(config_path) as f:
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
                    "data": config_data
                })
            except (json.JSONDecodeError, KeyError) as e:
                # Skip malformed config files
                print(f"Warning: Skipping {config_path.name}: {e}", file=sys.stderr)
                continue

        # Sort by priority (ascending)
        config_files.sort(key=lambda x: x["priority"])
        return config_files

    def _get_merged_config(self) -> Dict:
        """Get merged config from all configs by priority"""
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

    def _get_target_config(self) -> Dict:
        """Get the target config to modify"""
        return self.target_config

    def _save_config(self):
        """Save config changes to target config file"""
        target_path = self.target_config_path

        # Create backup if file exists
        if target_path.exists():
            backup_path = target_path.with_suffix('.json.bak')
            shutil.copy2(target_path, backup_path)

        # Ensure directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Save target config
        with open(target_path, 'w') as f:
            json.dump(self.target_config, f, indent=2)
            f.write('\n')

    def _validate_pattern(self, pattern: str) -> bool:
        """
        Validate regex pattern follows standard format: \\b(PATTERN)[.,;:!?]?\\b

        Standard format requirements:
        - Must use word boundaries: \\b
        - Pattern must be wrapped in parentheses: (PATTERN)
        - Must allow optional trailing punctuation: [.,;:!?]?
        - Pattern content must be ALL CAPS
        - Multi-word patterns use _, -, or no separator
        - Can use | for alternation (e.g., NVIM|NEOVIM)

        Exceptions:
        - Complex patterns with .* or other advanced regex are allowed
          but should be used sparingly
        """
        # First check if it's valid regex
        try:
            re.compile(pattern)
        except re.error as e:
            raise SnippetError(
                "INVALID_REGEX",
                f"Invalid regex pattern: {e}",
                {"pattern": pattern}
            )

        # Check for standard format: \b(PATTERN)[.,;:!?]?\b
        # Allow for complex patterns as exceptions
        standard_pattern = r'^\\b\([A-Z0-9_|]+\)\[\.,;:!\?\]\?\\b$'

        if not re.match(standard_pattern, pattern):
            # Check if it's a complex pattern (contains .* or other advanced regex)
            if re.search(r'\.\*|\.+[^,;:]|\[\^', pattern):
                # Complex pattern - allow it but warn
                # (Could add warning in the future)
                return True

            # Not standard format and not complex - reject
            raise SnippetError(
                "INVALID_PATTERN_FORMAT",
                f"Pattern must follow standard format: \\b(PATTERN)[.,;:!?]?\\b\n"
                f"  - Pattern must be ALL CAPS (A-Z, 0-9)\n"
                f"  - Multi-word patterns use _, -, or no separator\n"
                f"  - Use | for alternation (e.g., NVIM|NEOVIM)\n"
                f"  - Must have word boundaries \\b and optional punctuation [.,;:!?]?\n"
                f"  Your pattern: {pattern}\n"
                f"  Example: \\b(BUILD_ARTIFACT)[.,;:!?]?\\b",
                {"pattern": pattern}
            )

        # Validate the pattern content (between parentheses)
        match = re.match(r'^\\b\(([^)]+)\)\[\.,;:!\?\]\?\\b$', pattern)
        if match:
            pattern_content = match.group(1)

            # Check for spaces
            if ' ' in pattern_content:
                raise SnippetError(
                    "INVALID_PATTERN_FORMAT",
                    "Pattern cannot contain spaces. Use _, -, or no separator for multi-word patterns.",
                    {"pattern": pattern, "content": pattern_content}
                )

            # Check for lowercase
            if re.search(r'[a-z]', pattern_content):
                raise SnippetError(
                    "INVALID_PATTERN_FORMAT",
                    "Pattern must be ALL CAPS (A-Z). Found lowercase characters.",
                    {"pattern": pattern, "content": pattern_content}
                )

            # Check for mixed separators
            if '_' in pattern_content and '-' in pattern_content:
                raise SnippetError(
                    "INVALID_PATTERN_FORMAT",
                    "Pattern cannot mix separators (_ and -). Choose one style.",
                    {"pattern": pattern, "content": pattern_content}
                )

        return True

    def _find_snippet(self, name: str) -> Optional[Dict]:
        """Find snippet by name in merged config"""
        for mapping in self.config["mappings"]:
            # First check explicit name field if present
            if "name" in mapping and mapping["name"] == name:
                return mapping

            # Fallback: check if name.md file is in the snippet array
            snippet_file = f"snippets/{name}.md"
            snippet_array = mapping["snippet"]
            if snippet_file in snippet_array:
                return mapping
        return None

    def _find_in_target_config(self, name: str) -> Optional[Dict]:
        """Find snippet by name in target config"""
        target_config = self._get_target_config()
        for mapping in target_config["mappings"]:
            if "name" in mapping and mapping["name"] == name:
                return mapping
            snippet_file = f"commands/{name}.md"
            snippet_array = mapping.get("snippet", [])
            if snippet_file in snippet_array:
                return mapping
        return None

    def _check_pattern_conflicts(self, pattern: str, exclude_name: str = None) -> List[str]:
        """Check if pattern conflicts with existing patterns"""
        conflicts = []
        exclude_file = f"snippets/{exclude_name}.md" if exclude_name else None

        for mapping in self.config["mappings"]:
            if mapping["snippet"] == exclude_file:
                continue
            if mapping["pattern"] == pattern:
                conflicts.append(mapping["snippet"])

        return conflicts

    def _count_alternatives(self, pattern: str) -> int:
        """Count pattern alternatives (segments separated by |)"""
        # Remove word boundaries and grouping parens for counting
        cleaned = pattern.replace('\\b', '').strip('()')
        if not cleaned:
            return 0
        return len([p for p in cleaned.split('|') if p.strip()])

    def _get_snippet_path(self, name: str) -> Path:
        """Get full path for snippet file"""
        return self.snippets_dir / f"{name}.md"

    def create(self, name: str, pattern: str, description: str, content: str = None,
               file_path: str = None, file_paths: List[str] = None,
               separator: str = '\n', enabled: bool = True, force: bool = False,
               announce: bool = True) -> Dict:
        """Create a new snippet"""
        # Validate inputs
        if not name:
            raise SnippetError("INVALID_INPUT", "Snippet name is required")

        self._validate_pattern(pattern)

        # Get relative path from config directory to snippet file
        snippet_path = self._get_snippet_path(name)
        # Use relative path from config directory (where config.json lives)
        # os.path.relpath handles cases where paths are in different directory trees
        snippet_file = os.path.relpath(str(snippet_path), str(self.config_path.parent))

        # Check if snippet already exists
        if self._find_snippet(name) and not force:
            raise SnippetError(
                "DUPLICATE_NAME",
                f"Snippet '{name}' already exists",
                {"name": name, "suggestion": "Use --force to overwrite"}
            )

        # Check pattern conflicts
        conflicts = self._check_pattern_conflicts(pattern, exclude_name=name if force else None)
        if conflicts and not force:
            raise SnippetError(
                "DUPLICATE_PATTERN",
                f"Pattern conflicts with existing snippet(s)",
                {"pattern": pattern, "conflicts_with": conflicts}
            )

        # Determine snippet files to use
        snippet_files = []
        total_size = 0

        if file_paths:
            # Multi-file mode: reference existing files in snippets/ directory
            for fp in file_paths:
                # Ensure path is relative to snippets/
                if not fp.startswith("snippets/"):
                    fp = f"snippets/{Path(fp).name}"

                full_path = self.snippets_dir.parent / fp
                if not full_path.exists():
                    raise SnippetError(
                        "FILE_ERROR",
                        f"Source file not found: {fp}",
                        {"path": str(full_path)}
                    )
                snippet_files.append(fp)
                total_size += full_path.stat().st_size

        else:
            # Single-file mode: create new snippet file
            if file_path:
                source_path = Path(file_path).expanduser().resolve()
                if not source_path.exists():
                    raise SnippetError(
                        "FILE_ERROR",
                        f"Source file not found: {file_path}",
                        {"path": str(source_path)}
                    )
                with open(source_path) as f:
                    content = f.read()
            elif content is None:
                raise SnippetError("INVALID_INPUT", "Either --content, --file, or --files is required")

            # Create snippets directory if needed
            self.snippets_dir.mkdir(parents=True, exist_ok=True)

            # Prepend YAML frontmatter if requested
            if announce:
                announcement = ANNOUNCEMENT_TEMPLATE.format(
                    name=name,
                    description=description
                )
                content = announcement + content

            # Write snippet file
            with open(snippet_path, 'w') as f:
                f.write(content)

            snippet_files = [snippet_file]
            total_size = snippet_path.stat().st_size

        # Update or add to target config (base or local based on flag)
        target_config = self._get_target_config()
        target_existing = None
        for mapping in target_config["mappings"]:
            if mapping.get("name") == name:
                target_existing = mapping
                break

        if target_existing:
            # Update existing entry
            target_existing["pattern"] = pattern
            target_existing["enabled"] = enabled
            target_existing["snippet"] = snippet_files
            target_existing["separator"] = separator
            target_existing["name"] = name
        else:
            # Add new entry to target config
            target_config["mappings"].append({
                "name": name,
                "pattern": pattern,
                "snippet": snippet_files,
                "separator": separator,
                "enabled": enabled
            })

        self._save_config()

        # Also update merged config for this session
        existing = self._find_snippet(name)
        if existing:
            existing["pattern"] = pattern
            existing["enabled"] = enabled
            existing["snippet"] = snippet_files
            existing["separator"] = separator
            existing["name"] = name
        else:
            self.config["mappings"].append({
                "name": name,
                "pattern": pattern,
                "snippet": snippet_files,
                "separator": separator,
                "enabled": enabled
            })

        return {
            "name": name,
            "pattern": pattern,
            "files": snippet_files,
            "file_count": len(snippet_files),
            "separator": separator,
            "enabled": enabled,
            "alternatives": self._count_alternatives(pattern),
            "size_bytes": total_size
        }

    def list(self, name: str = None, show_content: bool = False,
             show_stats: bool = False, show_source: bool = True, keyword: str = None) -> Dict:
        """List snippets with source config and priority information"""
        snippets = []

        for mapping in self.config["mappings"]:
            # snippet is now always an array
            snippet_files = mapping["snippet"]

            # Use explicit name field if present, otherwise extract from first file
            if "name" in mapping:
                snippet_name = mapping["name"]
            else:
                snippet_name = Path(snippet_files[0]).stem

            # Filter by name if specified
            if name and snippet_name != name:
                continue

            # Filter by keyword in pattern
            if keyword:
                pattern = mapping["pattern"]
                # Extract pattern content between parentheses
                pattern_match = re.search(r'\(([^)]+)\)', pattern)
                if pattern_match:
                    pattern_content = pattern_match.group(1)
                    # Check if keyword matches any alternative in the pattern
                    if not any(keyword.upper() in alt.upper() for alt in pattern_content.split('|')):
                        continue
                else:
                    continue

            snippet_info = {
                "name": snippet_name,
                "pattern": mapping["pattern"],
                "files": snippet_files,  # Show all files
                "file_count": len(snippet_files),
                "separator": mapping.get("separator", "\n"),
                "enabled": mapping.get("enabled", True),
                "alternatives": self._count_alternatives(mapping["pattern"])
            }

            # Add source config info if available and requested
            if show_source:
                if "_source_config" in mapping:
                    snippet_info["source_config"] = mapping["_source_config"]
                if "_source_priority" in mapping:
                    snippet_info["priority"] = mapping["_source_priority"]

            # Collect info from all files
            total_size = 0
            all_content = []
            missing_files = []

            for snippet_file in snippet_files:
                snippet_path = self.snippets_dir.parent / snippet_file
                if snippet_path.exists():
                    total_size += snippet_path.stat().st_size
                    if show_content:
                        with open(snippet_path) as f:
                            all_content.append(f.read())
                else:
                    missing_files.append(snippet_file)

            snippet_info["size_bytes"] = total_size
            if show_content and all_content:
                # Join content with separator
                separator = mapping.get("separator", "\n")
                snippet_info["content"] = separator.join(all_content)

            if missing_files:
                snippet_info["missing"] = True
                snippet_info["missing_files"] = missing_files

            snippets.append(snippet_info)

        result = {"snippets": snippets}

        if show_stats:
            result["total"] = len(snippets)
            result["enabled"] = sum(1 for s in snippets if s.get("enabled", True))
            result["disabled"] = result["total"] - result["enabled"]
            result["missing_files"] = sum(1 for s in snippets if s.get("missing", False))

            # Add config-level stats
            result["config_count"] = len(self.all_configs)
            result["configs"] = [
                {
                    "filename": cfg["filename"],
                    "priority": cfg["priority"],
                    "snippet_count": len(cfg["data"].get("mappings", []))
                }
                for cfg in self.all_configs
            ]

        return result

    def update(self, name: str, pattern: str = None, content: str = None,
               file_path: str = None, enabled: bool = None, rename: str = None) -> Dict:
        """Update existing snippet"""
        # Find snippet
        existing = self._find_snippet(name)
        if not existing:
            raise SnippetError(
                "NOT_FOUND",
                f"Snippet '{name}' not found",
                {"name": name}
            )

        snippet_path = self._get_snippet_path(name)
        changes = {}

        # Update pattern
        if pattern is not None:
            self._validate_pattern(pattern)
            conflicts = self._check_pattern_conflicts(pattern, exclude_name=name)
            if conflicts:
                raise SnippetError(
                    "DUPLICATE_PATTERN",
                    f"Pattern conflicts with existing snippet(s)",
                    {"pattern": pattern, "conflicts_with": conflicts}
                )
            changes["pattern"] = {"old": existing["pattern"], "new": pattern}
            existing["pattern"] = pattern

            # Also update in target config
            target_existing = self._find_in_target_config(name)
            if target_existing:
                target_existing["pattern"] = pattern

        # Update content
        content_updated = False
        if content is not None or file_path is not None:
            if file_path:
                source_path = Path(file_path).expanduser().resolve()
                if not source_path.exists():
                    raise SnippetError(
                        "FILE_ERROR",
                        f"Source file not found: {file_path}",
                        {"path": str(source_path)}
                    )
                with open(source_path) as f:
                    content = f.read()

            old_size = snippet_path.stat().st_size if snippet_path.exists() else 0
            with open(snippet_path, 'w') as f:
                f.write(content)
            new_size = snippet_path.stat().st_size
            changes["content"] = {"old_size": old_size, "new_size": new_size}
            content_updated = True

        # Update enabled status
        if enabled is not None:
            old_enabled = existing.get("enabled", True)
            if old_enabled != enabled:
                changes["enabled"] = {"old": old_enabled, "new": enabled}
                existing["enabled"] = enabled

                # Also update in target config
                target_existing = self._find_in_target_config(name)
                if target_existing:
                    target_existing["enabled"] = enabled

        # Rename
        if rename:
            new_snippet_path = self._get_snippet_path(rename)
            new_snippet_file = str(new_snippet_path.relative_to(self.config_path.parent))

            # Check new name doesn't exist
            if self._find_snippet(rename):
                raise SnippetError(
                    "DUPLICATE_NAME",
                    f"Snippet '{rename}' already exists",
                    {"name": rename}
                )

            # Rename file
            if snippet_path.exists():
                snippet_path.rename(new_snippet_path)

            # Update merged config
            existing["snippet"] = [new_snippet_file]
            changes["name"] = {"old": name, "new": rename}

            # Also update in target config
            target_existing = self._find_in_target_config(name)
            if target_existing:
                target_existing["snippet"] = [new_snippet_file]
                target_existing["name"] = rename

            name = rename

        self._save_config()

        return {
            "name": name,
            "changes": changes
        }

    def delete(self, name: str, force: bool = False, backup: bool = True,
               backup_dir: str = None) -> Dict:
        """Delete snippet"""
        # Find snippet
        existing = self._find_snippet(name)
        if not existing:
            raise SnippetError(
                "NOT_FOUND",
                f"Snippet '{name}' not found",
                {"name": name}
            )

        snippet_path = self._get_snippet_path(name)
        deleted_files = []
        backup_location = None

        # Create backup if requested
        if backup and snippet_path.exists():
            if backup_dir:
                backup_base = Path(backup_dir)
            else:
                backup_base = self.snippets_dir.parent / "backups"

            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            backup_location = backup_base / f"{timestamp}_{name}"
            backup_location.mkdir(parents=True, exist_ok=True)

            shutil.copy2(snippet_path, backup_location / f"{name}.md")

        # Delete snippet file
        if snippet_path.exists():
            snippet_path.unlink()
            deleted_files.append(str(snippet_path))

        # Remove from merged config
        self.config["mappings"] = [
            m for m in self.config["mappings"]
            if m.get("name") != name
        ]

        # Remove from target config
        target_config = self._get_target_config()
        target_config["mappings"] = [
            m for m in target_config["mappings"]
            if m.get("name") != name
        ]

        self._save_config()

        return {
            "deleted": deleted_files,
            "backup_location": str(backup_location) if backup_location else None,
            "config_updated": True
        }

    def validate(self) -> Dict:
        """Validate configuration and files"""
        issues = []

        # Validate each mapping
        for mapping in self.config["mappings"]:
            # Check pattern
            try:
                self._validate_pattern(mapping["pattern"])
            except SnippetError as e:
                issues.append({
                    "type": "invalid_pattern",
                    "snippet": mapping["snippet"],
                    "details": e.details
                })

            # Check files exist (snippet is always an array)
            snippet_files = mapping["snippet"]
            for snippet_file in snippet_files:
                snippet_path = self.snippets_dir.parent / snippet_file
                if not snippet_path.exists():
                    issues.append({
                        "type": "missing_file",
                        "snippet": snippet_file,
                        "path": str(snippet_path)
                    })

        # Check for duplicate patterns
        patterns_seen = {}
        for mapping in self.config["mappings"]:
            pattern = mapping["pattern"]
            if pattern in patterns_seen:
                issues.append({
                    "type": "duplicate_pattern",
                    "pattern": pattern,
                    "snippets": [patterns_seen[pattern], mapping["snippet"]]
                })
            else:
                patterns_seen[pattern] = mapping["snippet"]

        return {
            "config_valid": len(issues) == 0,
            "files_checked": len(self.config["mappings"]),
            "issues": issues
        }

    def test(self, name: str, text: str) -> Dict:
        """Test if pattern matches text (case-sensitive)"""
        existing = self._find_snippet(name)
        if not existing:
            raise SnippetError(
                "NOT_FOUND",
                f"Snippet '{name}' not found",
                {"name": name}
            )

        pattern = existing["pattern"]
        matches = re.findall(pattern, text)

        return {
            "name": name,
            "pattern": pattern,
            "text": text,
            "matches": matches,
            "match_count": len(matches),
            "matched": len(matches) > 0
        }

    def set_priority(self, priority: int) -> Dict:
        """Set priority for the target config file"""
        # Update target config with new priority
        self.target_config["priority"] = priority

        # Save the updated config
        self._save_config()

        return {
            "config_file": str(self.target_config_path.name),
            "priority": priority,
            "message": f"Priority set to {priority} for {self.target_config_path.name}"
        }


def open_in_editor(file_path: Path) -> bool:
    """Open file in user's preferred editor"""
    # Get editor from environment
    editor = os.environ.get('EDITOR', os.environ.get('VISUAL', 'vim'))

    try:
        subprocess.run([editor, str(file_path)], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error opening editor: {e}", file=sys.stderr)
        return False


def interactive_select(snippets: List[Dict], operation: str = "edit", base_dir: Path = None) -> Optional[int]:
    """Prompt user to select a snippet from a numbered list"""
    if not snippets:
        print("No snippets found.")
        return None

    # Display numbered list
    print(f"\nFound {len(snippets)} snippet{'s' if len(snippets) != 1 else ''}:\n")
    for i, snippet in enumerate(snippets, 1):
        # Snippet name in cyan
        print(f"[{i}] {Colors.cyan(snippet['name'])}")

        # Pattern in yellow
        print(f"    Pattern: {Colors.yellow(snippet['pattern'])}")

        # Show absolute path in dim
        file_path = Path(snippet['files'][0])
        if not file_path.is_absolute() and base_dir:
            file_path = (base_dir / file_path).resolve()

        print(f"    File: {Colors.dim(str(file_path))}")
        print()

    # Prompt for selection
    try:
        if len(snippets) == 1:
            # Single match: allow Enter to select
            choice = input(f"Press Enter to {operation}, or q to quit: ").strip()
            if choice.lower() == 'q':
                return None
            if choice == '':
                return 0  # Select the only snippet
            # If they typed something else, try to parse as number
            try:
                index = int(choice) - 1
                if index == 0:
                    return 0
            except ValueError:
                pass
            print("Invalid input.")
            return None
        else:
            # Multiple matches: require number
            choice = input(f"Select snippet to {operation} [1-{len(snippets)}, q to quit]: ").strip()
            if choice.lower() == 'q':
                return None

            index = int(choice) - 1
            if 0 <= index < len(snippets):
                return index
            else:
                print(f"Invalid selection. Please enter 1-{len(snippets)}")
                return None
    except (ValueError, KeyboardInterrupt):
        print("\nCancelled.")
        return None


def format_output(success: bool, operation: str, data: Dict = None,
                  message: str = None, error: SnippetError = None,
                  format_type: str = "json") -> str:
    """Format command output"""
    if format_type == "json":
        output = {
            "success": success,
            "operation": operation
        }

        if success:
            output["data"] = data or {}
            if message:
                output["message"] = message
        else:
            output["error"] = {
                "code": error.code if error else "UNKNOWN_ERROR",
                "message": error.message if error else message or "Unknown error",
                "details": error.details if error else {}
            }

        return json.dumps(output, indent=2)

    elif format_type == "text":
        if success:
            lines = [f"✓ {message or 'Success'}"]
            if data:
                for key, value in data.items():
                    lines.append(f"  {key}: {value}")
            return "\n".join(lines)
        else:
            error_msg = error.message if error else message or "Unknown error"
            return f"✗ {error_msg}"

    return ""


def preprocess_args(args):
    """
    Pre-process arguments to treat first positional arg as keyword if it's not a subcommand.

    Examples:
      snippets DOCKER        → snippets -k DOCKER list
      snippets create foo    → snippets create foo (unchanged)
      snippets -k DOCKER     → snippets -k DOCKER list (unchanged)
    """
    subcommands = {'create', 'list', 'update', 'delete', 'validate', 'test', 'set-priority'}

    # Skip global flags to find first positional arg
    i = 0
    while i < len(args):
        arg = args[i]

        # Skip flag and its value
        if arg in ['--config', '--config-name', '--snippets-dir', '--output', '-k', '--keyword']:
            i += 2  # Skip flag and value
            continue
        if arg in ['--use-base-config', '-v', '--verbose']:
            i += 1  # Skip boolean flag
            continue
        if arg.startswith('-'):
            # Unknown flag, skip
            i += 1
            continue

        # Found first positional argument
        if arg not in subcommands:
            # Treat as keyword
            return args[:i] + ['-k', arg] + args[i+1:]
        else:
            # It's a subcommand, leave as is
            return args

        i += 1

    return args


def main():
    parser = argparse.ArgumentParser(
        description="Claude Code Snippets CLI with Multi-Config Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all snippets with source config info
  snippets_cli.py list --show-stats

  # Create snippet in named config (e.g., config.work.json)
  snippets_cli.py --config-name work create my-snippet --pattern "pattern" --description "desc"

  # Create snippet in local config (default: config.local.json)
  snippets_cli.py create my-snippet --pattern "pattern" --description "desc"

  # Create snippet in base config (config.json)
  snippets_cli.py --use-base-config create my-snippet --pattern "pattern" --description "desc"

Config Priority System:
  - config.json: priority 0 (base)
  - config.local.json: priority 100 (local overrides)
  - config.{name}.json: priority 50 (or specified in file)
  - Higher priority configs override lower priority when snippet names conflict
        """
    )

    # Global options
    parser.add_argument("--config", type=Path,
                       help="Base config file path (default: ./config.json)")
    parser.add_argument("--config-name", type=str,
                       help="Named config to target (e.g., 'work' for config.work.json)")
    parser.add_argument("--snippets-dir", type=Path,
                       help="Snippets directory (default: ./commands/local)")
    parser.add_argument("--use-base-config", action="store_true",
                       help="Save to config.json instead of config.local.json")
    parser.add_argument("--output", choices=["json", "text"], default="text",
                       help="Output format (default: text, use 'json' for raw JSON)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    parser.add_argument("-k", "--keyword", type=str,
                       help="Filter by keyword (searches in pattern)")

    # Subcommands (default to list if not specified)
    subparsers = parser.add_subparsers(dest="command", required=False)

    # create
    create_parser = subparsers.add_parser("create", help="Create new snippet")
    create_parser.add_argument("name", help="Snippet name")
    create_parser.add_argument("--pattern", required=True, help="Regex pattern")
    create_parser.add_argument("--description", required=True, help="Skill description (when to use)")
    create_parser.add_argument("--content", help="Snippet content (inline)")
    create_parser.add_argument("--file", help="Read content from file")
    create_parser.add_argument("--files", nargs="+", help="Multiple source files to combine")
    create_parser.add_argument("--separator", default="\n",
                              help="Separator between files (default: newline)")
    create_parser.add_argument("--enabled", type=bool, default=True,
                              help="Enable snippet (default: true)")
    create_parser.add_argument("--force", action="store_true",
                              help="Overwrite if exists")

    # list
    list_parser = subparsers.add_parser("list", help="List snippets")
    list_parser.add_argument("name", nargs="?", help="Specific snippet name")
    list_parser.add_argument("--show-content", action="store_true",
                            help="Include content in output")
    list_parser.add_argument("--show-stats", action="store_true",
                            help="Include statistics")

    # update
    update_parser = subparsers.add_parser("update", help="Update snippet")
    update_parser.add_argument("name", help="Snippet name")
    update_parser.add_argument("--pattern", help="New regex pattern")
    update_parser.add_argument("--content", help="New content (inline)")
    update_parser.add_argument("--file", help="Read new content from file")
    update_parser.add_argument("--enabled", type=bool, help="Enable/disable")
    update_parser.add_argument("--rename", help="Rename snippet")

    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete snippet")
    delete_parser.add_argument("name", help="Snippet name")
    delete_parser.add_argument("--force", action="store_true",
                              help="Skip confirmation")
    delete_parser.add_argument("--backup", action="store_true", default=True,
                              help="Create backup (default: true)")
    delete_parser.add_argument("--backup-dir", help="Backup directory")

    # validate
    validate_parser = subparsers.add_parser("validate",
                                           help="Validate config and files")

    # test
    test_parser = subparsers.add_parser("test", help="Test pattern matching")
    test_parser.add_argument("name", help="Snippet name")
    test_parser.add_argument("text", help="Text to test against")

    # set-priority (new command for managing config priorities)
    priority_parser = subparsers.add_parser("set-priority",
                                            help="Set priority for current target config")
    priority_parser.add_argument("priority", type=int,
                                help="Priority value (higher = takes precedence)")

    # Pre-process arguments to treat first positional as keyword
    processed_args = preprocess_args(sys.argv[1:])
    args = parser.parse_args(processed_args)

    # Default to list command if no command specified
    if args.command is None:
        args.command = "list"
        # Set default list args
        args.name = None
        args.show_content = False
        args.show_stats = False

    # Set defaults for paths
    script_dir = Path(__file__).parent
    config_path = args.config or script_dir / "config.json"
    snippets_dir = args.snippets_dir or script_dir.parent / "commands" / "local"

    # Validate config_name and use_base_config are mutually exclusive
    if args.config_name and args.use_base_config:
        print("Error: --config-name and --use-base-config cannot be used together",
              file=sys.stderr)
        sys.exit(1)

    try:
        manager = SnippetManager(config_path, snippets_dir, args.use_base_config, args.config_name)

        if args.command == "create":
            data = manager.create(
                args.name, args.pattern, args.description,
                args.content, args.file,
                getattr(args, 'files', None), args.separator,
                args.enabled, args.force,
                announce=True
            )
            print(format_output(True, "create", data,
                              f"Snippet '{args.name}' created successfully",
                              format_type=args.output))

        elif args.command == "list":
            # Use keyword from global args if provided
            keyword = args.keyword if hasattr(args, 'keyword') else None
            data = manager.list(args.name, args.show_content, args.show_stats, keyword=keyword)

            # If output is JSON, just print it
            if args.output == "json":
                print(json.dumps(data, indent=2))
            else:
                # Interactive mode: show list and prompt for selection
                snippets = data.get("snippets", [])
                if not snippets:
                    print("No snippets found.")
                else:
                    # Show list
                    selected_idx = interactive_select(snippets, operation="edit", base_dir=snippets_dir.parent)
                    if selected_idx is not None:
                        # Open selected snippet in editor
                        snippet = snippets[selected_idx]
                        file_path = Path(snippet['files'][0])
                        if not file_path.is_absolute():
                            file_path = snippets_dir.parent / file_path

                        print(f"\nOpening {file_path} in $EDITOR...")
                        if open_in_editor(file_path):
                            print("Saved.")
                        else:
                            print("Editor closed without saving or error occurred.")

        elif args.command == "update":
            data = manager.update(
                args.name, args.pattern, args.content, args.file,
                args.enabled, args.rename
            )
            print(format_output(True, "update", data,
                              f"Snippet '{args.name}' updated successfully",
                              format_type=args.output))

        elif args.command == "delete":
            data = manager.delete(args.name, args.force, args.backup,
                                 args.backup_dir)
            print(format_output(True, "delete", data,
                              f"Snippet '{args.name}' deleted successfully",
                              format_type=args.output))

        elif args.command == "validate":
            data = manager.validate()
            message = "All snippets valid" if data["config_valid"] else "Validation issues found"
            print(format_output(True, "validate", data, message,
                              format_type=args.output))

        elif args.command == "test":
            data = manager.test(args.name, args.text)
            message = f"Pattern {'matched' if data['matched'] else 'did not match'}"
            print(format_output(True, "test", data, message,
                              format_type=args.output))

        elif args.command == "set-priority":
            data = manager.set_priority(args.priority)
            print(format_output(True, "set-priority", data, data["message"],
                              format_type=args.output))

        sys.exit(0)

    except SnippetError as e:
        print(format_output(False, args.command, error=e, format_type=args.output),
              file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        error = SnippetError("UNKNOWN_ERROR", str(e))
        print(format_output(False, args.command, error=error, format_type=args.output),
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()