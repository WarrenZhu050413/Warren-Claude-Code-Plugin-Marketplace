#!/usr/bin/env python3
"""
Claude Code Snippets CLI

A rigid, testable CLI for CRUD operations on snippet configurations.
Designed to be wrapped by LLM-enabled commands for intelligent UX.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


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

    def _diagnose_pattern_issue(self, pattern: str) -> str:
        """Diagnose specific issue with pattern format"""
        # Check for missing opening \b
        if not pattern.startswith('\\b'):
            return "Missing opening word boundary \\b at start"

        # Check for missing opening parenthesis
        if not re.match(r'^\\b\(', pattern):
            return "Missing opening parenthesis after \\b (should be \\b(PATTERN))"

        # Check if has parentheses but \b in wrong place (after punctuation)
        if re.search(r'\)\[\.,;:!\?\]\?\\b', pattern):
            return "Word boundary \\b is after punctuation; move it: (PATTERN)\\b[.,;:!?]?"

        # Check for missing \b after closing paren
        if re.search(r'\)[^\\\[]', pattern):
            return "Missing word boundary \\b after closing parenthesis"

        # Check for wrong punctuation class
        if '[' in pattern:
            if '[.,;:]?' in pattern or '[.,;:?]?' in pattern:
                return "Incomplete punctuation class; use [.,;:!?]? (missing !)"
            if not re.search(r'\[\.,;:!\?\]\?', pattern):
                return "Incorrect punctuation format; use [.,;:!?]?"

        # Check for missing punctuation class
        if '[' not in pattern:
            return "Missing optional punctuation [.,;:!?]? at end"

        # Check for lowercase in pattern
        paren_match = re.search(r'\(([^)]+)\)', pattern)
        if paren_match:
            content = paren_match.group(1)
            if re.search(r'[a-z]', content):
                return "Pattern content must be ALL CAPS (found lowercase letters)"

        return "Pattern doesn't match required format \\b(PATTERN)\\b[.,;:!?]?"

    def _validate_pattern(self, pattern: str) -> bool:
        """
        Validate regex pattern follows standard format: \\b(PATTERN)\\b[.,;:!?]?

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

        # Check for standard format: \b(PATTERN)\b[.,;:!?]?
        # Allow for complex patterns as exceptions
        standard_pattern = r'^\\b\([A-Z0-9_|]+\)\\b\[\.,;:!\?\]\?$'

        if not re.match(standard_pattern, pattern):
            # Check if it's a complex pattern (contains .* or other advanced regex)
            if re.search(r'\.\*|\.+[^,;:]|\[\^', pattern):
                # Complex pattern - allow it but warn
                # (Could add warning in the future)
                return True

            # Diagnose specific issue for better error message
            issue_detail = self._diagnose_pattern_issue(pattern)

            # Not standard format and not complex - reject
            raise SnippetError(
                "INVALID_PATTERN_FORMAT",
                f"Pattern must follow standard format: \\b(PATTERN)\\b[.,;:!?]?\n"
                f"  Issue: {issue_detail}\n"
                f"  Your pattern: {pattern}\n"
                f"  Example: \\b(BUILD_ARTIFACT)\\b[.,;:!?]?",
                {"pattern": pattern, "issue": issue_detail}
            )

        # Validate the pattern content (between parentheses)
        match = re.match(r'^\\b\(([^)]+)\)\\b\[\.,;:!\?\]\?$', pattern)
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
                "Pattern conflicts with existing snippet(s)",
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
             show_stats: bool = False, show_source: bool = True, search_term: str = None) -> Dict:
        """List snippets with optional search across name/pattern/description"""
        snippets = []

        for mapping in self.config["mappings"]:
            # snippet is now always an array
            snippet_files = mapping["snippet"]

            # Use explicit name field if present, otherwise extract from first file
            if "name" in mapping:
                snippet_name = mapping["name"]
            else:
                snippet_name = Path(snippet_files[0]).stem

            # Filter by name if specified (exact match for backwards compat)
            if name and snippet_name != name:
                continue

            # Enhanced search across name, pattern, description
            match_type = None
            match_priority = 999

            if search_term:
                search_lower = search_term.lower()

                # Check exact name match (highest priority)
                if snippet_name.lower() == search_lower:
                    match_type = "exact"
                    match_priority = 1
                # Check name contains
                elif search_lower in snippet_name.lower():
                    match_type = "name"
                    match_priority = 2
                else:
                    # Check pattern match
                    pattern = mapping["pattern"]
                    pattern_match_obj = re.search(r'\(([^)]+)\)', pattern)
                    if pattern_match_obj:
                        pattern_content = pattern_match_obj.group(1)
                        if any(search_lower in alt.lower() for alt in pattern_content.split('|')):
                            match_type = "pattern"
                            match_priority = 3

                    # If still no match, check description (read from file)
                    if not match_type:
                        for snippet_file in snippet_files:
                            snippet_path = self.snippets_dir.parent / snippet_file
                            if snippet_path.exists():
                                try:
                                    file_content = snippet_path.read_text()
                                    if file_content.startswith("---"):
                                        parts = file_content.split("---", 2)
                                        if len(parts) >= 3:
                                            import yaml
                                            frontmatter = yaml.safe_load(parts[1])
                                            if frontmatter:
                                                desc = frontmatter.get("description", "")
                                                if search_lower in desc.lower():
                                                    match_type = "description"
                                                    match_priority = 4
                                                    break
                                except Exception:
                                    # Ignore errors reading/parsing frontmatter
                                    pass

                # Skip if no matches
                if not match_type:
                    continue

            snippet_info = {
                "name": snippet_name,
                "pattern": mapping["pattern"],
                "files": snippet_files,  # Show all files
                "file_count": len(snippet_files),
                "separator": mapping.get("separator", "\n"),
                "enabled": mapping.get("enabled", True),
                "alternatives": self._count_alternatives(mapping["pattern"]),
                "match_priority": match_priority,
            }

            if match_type:
                snippet_info["match_type"] = match_type

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

        # Sort by match priority (lower = better)
        snippets.sort(key=lambda x: x.get("match_priority", 999))

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
                    "Pattern conflicts with existing snippet(s)",
                    {"pattern": pattern, "conflicts_with": conflicts}
                )
            changes["pattern"] = {"old": existing["pattern"], "new": pattern}
            existing["pattern"] = pattern

            # Also update in target config
            target_existing = self._find_in_target_config(name)
            if target_existing:
                target_existing["pattern"] = pattern

        # Update content
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

    def show_paths(self, filter_term: str = None) -> Dict:
        """Show available snippet locations and categories"""
        categories = {
            "communication": "Email, reports, writing templates",
            "documentation": "Guides, references, how-tos",
            "development": "Code patterns, debugging workflows",
            "productivity": "Workflow automation, task management",
            "output-formats": "Formatting styles, templates"
        }

        if filter_term:
            categories = {
                k: v for k, v in categories.items()
                if filter_term.lower() in k.lower() or filter_term.lower() in v.lower()
            }

        return {
            "base_dir": str(self.snippets_dir),
            "categories": [
                {
                    "name": name,
                    "description": desc,
                    "path": f"snippets/local/{name}/"
                }
                for name, desc in categories.items()
            ]
        }

    def create_from_file(self, source_file: str, destination_path: str,
                         pattern_override: str = None, force: bool = False) -> Dict:
        """
        Create snippet from source file to destination path.

        Validates frontmatter, pattern, and destination before creating.
        """
        import yaml

        # 1. Validate source file
        source_path = Path(source_file).expanduser().resolve()
        if not source_path.exists():
            raise SnippetError("FILE_ERROR", f"Source file not found: {source_file}")

        # 2. Read and validate YAML frontmatter
        content = source_path.read_text()
        if not content.startswith("---"):
            raise SnippetError(
                "MISSING_FRONTMATTER",
                "Source file must start with YAML frontmatter:\n"
                "---\n"
                "name: \"Snippet Name\"\n"
                "description: \"Description\"\n"
                "pattern: \"\\\\b(PATTERN)\\\\b[.,;:!?]?\"\n"
                "---"
            )

        # Extract frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            raise SnippetError("INVALID_FRONTMATTER", "Malformed YAML frontmatter")

        try:
            frontmatter = yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            raise SnippetError("INVALID_YAML", f"Invalid YAML in frontmatter: {e}")

        if not frontmatter:
            raise SnippetError("EMPTY_FRONTMATTER", "YAML frontmatter is empty")

        # Extract required fields
        name = frontmatter.get("name", "")
        description = frontmatter.get("description", "")
        pattern = pattern_override or frontmatter.get("pattern", "")

        if not name:
            raise SnippetError("MISSING_NAME", "Frontmatter must include 'name' field")
        if not description:
            raise SnippetError("MISSING_DESCRIPTION", "Frontmatter must include 'description' field")
        if not pattern:
            raise SnippetError("MISSING_PATTERN", "Frontmatter must include 'pattern' field or use --pattern flag")

        # 3. Validate pattern
        self._validate_pattern(pattern)

        # 4. Validate destination path
        dest_path = Path(destination_path)

        # Check it's within snippets directory
        try:
            rel_dest = dest_path if not dest_path.is_absolute() else dest_path.relative_to(self.config_path.parent)
            if not str(rel_dest).startswith("snippets/local/"):
                raise ValueError("Not in snippets/local/")
        except (ValueError, OSError):
            raise SnippetError(
                "INVALID_DESTINATION",
                f"Destination must be within snippets/local/ directory\n"
                f"Expected format: snippets/local/<category>/<name>/SKILL.md\n"
                f"Got: {destination_path}\n\n"
                f"Run 'snippets paths' to see available categories."
            )

        # 5. Extract snippet name from path
        path_parts = dest_path.parts
        if len(path_parts) < 4:
            raise SnippetError(
                "INVALID_DESTINATION_STRUCTURE",
                f"Destination must follow: snippets/local/<category>/<name>/SKILL.md\n"
                f"Got: {destination_path}"
            )

        snippet_name = path_parts[-2]  # Parent directory name

        # 6. Check destination doesn't exist
        full_dest_path = self.snippets_dir.parent / dest_path
        if full_dest_path.exists() and not force:
            raise SnippetError(
                "DESTINATION_EXISTS",
                f"Destination already exists: {destination_path}\n\n"
                f"Use --force to overwrite"
            )

        # 7. Create destination directory
        full_dest_path.parent.mkdir(parents=True, exist_ok=True)

        # 8. Copy file to destination
        shutil.copy2(source_path, full_dest_path)

        # 9. Register in config.local.json
        target_config = self._get_target_config()

        # Remove existing entry if force
        if force:
            target_config["mappings"] = [
                m for m in target_config["mappings"]
                if m.get("name") != snippet_name
            ]

        # Add new entry
        target_config["mappings"].append({
            "name": snippet_name,
            "pattern": pattern,
            "snippet": [str(dest_path)],
            "separator": "\n",
            "enabled": True
        })

        self._save_config()

        return {
            "name": snippet_name,
            "pattern": pattern,
            "destination": str(destination_path),
            "source": str(source_file),
            "registered": True
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
        if not success:
            error_msg = error.message if error else message or "Unknown error"
            return f"✗ {error_msg}"

        # Special formatting for validate command
        if operation == "validate" and data:
            lines = []

            config_valid = data.get("config_valid", False)
            files_checked = data.get("files_checked", 0)
            issues = data.get("issues", [])

            # Header
            if config_valid:
                lines.append(Colors.green(f"✓ All snippets valid ({files_checked} checked)"))
            else:
                lines.append(Colors.yellow(f"⚠ Validation issues found ({len(issues)} issues, {files_checked} snippets checked)"))
                lines.append("")

            # Group issues by type
            if issues:
                invalid_patterns = [i for i in issues if i["type"] == "invalid_pattern"]
                missing_files = [i for i in issues if i["type"] == "missing_file"]
                duplicate_patterns = [i for i in issues if i["type"] == "duplicate_pattern"]

                # Invalid patterns
                if invalid_patterns:
                    lines.append(Colors.bold("Invalid Patterns:"))
                    for issue in invalid_patterns:
                        snippet_files = issue["snippet"]
                        snippet_path = snippet_files[0] if isinstance(snippet_files, list) else snippet_files

                        # Show parent directory + filename for better context
                        path_parts = Path(snippet_path).parts
                        if len(path_parts) >= 2:
                            display_name = f"{path_parts[-2]}/{Path(snippet_path).name}"
                        else:
                            display_name = Path(snippet_path).name

                        pattern = issue["details"]["pattern"]
                        specific_issue = issue["details"].get("issue", "Pattern format is incorrect")

                        expected_pattern = '\\b(PATTERN)\\b[.,;:!?]?'
                        lines.append(f"  {Colors.red('✗')} {Colors.cyan(display_name)}")
                        lines.append(f"    Current:  {Colors.yellow(pattern)}")
                        lines.append(f"    Issue:    {Colors.red(specific_issue)}")
                        lines.append(f"    Expected: {Colors.dim(expected_pattern)}")
                        lines.append("")

                # Missing files
                if missing_files:
                    lines.append(Colors.bold("Missing Files:"))
                    for issue in missing_files:
                        snippet_file = issue["snippet"]
                        lines.append(f"  {Colors.red('✗')} {Colors.dim(snippet_file)}")
                        lines.append("")

                # Duplicate patterns
                if duplicate_patterns:
                    lines.append(Colors.bold("Duplicate Patterns:"))
                    for issue in duplicate_patterns:
                        pattern = issue["pattern"]
                        snippets = issue["snippets"]
                        snippet_names = [Path(s[0]).stem if isinstance(s, list) else Path(s).stem for s in snippets]

                        lines.append(f"  {Colors.red('✗')} Pattern: {Colors.yellow(pattern)}")
                        lines.append(f"    Found in: {', '.join(Colors.cyan(name) for name in snippet_names)}")
                        lines.append("")

            return "\n".join(lines)

        # Default formatting for other commands
        lines = [f"✓ {message or 'Success'}"]
        if data:
            for key, value in data.items():
                if key not in ["config_valid", "files_checked", "issues"]:  # Skip validation-specific keys
                    lines.append(f"  {key}: {value}")
        return "\n".join(lines)

    return ""


def preprocess_args(args):
    """
    Pre-process arguments to treat first positional arg as search term for list.
    Also ensures global flags come before subcommands.

    Examples:
      snippets docker        → snippets list docker
      snippets paths --output json → snippets --output json paths
      snippets create foo    → snippets create foo (unchanged)
    """
    subcommands = {'create', 'paths', 'list', 'validate'}

    # Separate global flags, subcommand, and subcommand args
    global_flags = []
    subcommand = None
    subcommand_args = []
    i = 0

    while i < len(args):
        arg = args[i]

        # Global flags (need to come before subcommand)
        if arg in ['--config', '--snippets-dir', '--output']:
            if i + 1 < len(args):
                global_flags.extend([arg, args[i+1]])
                i += 2
            else:
                i += 1
            continue

        # Found subcommand
        if arg in subcommands:
            subcommand = arg
            # Continue parsing remaining args
            i += 1
            # Everything after subcommand is subcommand args
            while i < len(args):
                arg = args[i]
                # Check if this is a global flag that should come before subcommand
                if arg in ['--config', '--snippets-dir', '--output']:
                    if i + 1 < len(args):
                        global_flags.extend([arg, args[i+1]])
                        i += 2
                    else:
                        i += 1
                    continue
                else:
                    # Regular subcommand arg
                    subcommand_args.append(arg)
                    i += 1
            break

        # Positional arg before subcommand - treat as search term for list
        if not arg.startswith('-'):
            subcommand = 'list'
            subcommand_args = [arg]
            i += 1
            # Get remaining args
            while i < len(args):
                arg = args[i]
                if arg in ['--config', '--snippets-dir', '--output']:
                    if i + 1 < len(args):
                        global_flags.extend([arg, args[i+1]])
                        i += 2
                    else:
                        i += 1
                else:
                    subcommand_args.append(arg)
                    i += 1
            break

        i += 1

    # No subcommand found - default to list
    if not subcommand:
        subcommand = 'list'

    # Reconstruct: global_flags + subcommand + subcommand_args
    return global_flags + [subcommand] + subcommand_args


def main():
    parser = argparse.ArgumentParser(
        description="Snippets CLI v2.0 - Search, Create, Validate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show available snippet locations
  snippets paths
  snippets paths dev

  # Create snippet from file
  snippets create ~/my-snippet.md snippets/local/development/my-snippet/SKILL.md

  # Search snippets
  snippets docker
  snippets "email handling"

  # List all snippets
  snippets list

  # Validate configuration
  snippets validate
        """
    )

    # Global options (minimal)
    parser.add_argument("--config", type=Path,
                       help="Config file path (default: ./config.json)")
    parser.add_argument("--snippets-dir", type=Path,
                       help="Snippets directory (default: ./snippets/local)")
    parser.add_argument("--output", choices=["json", "text"], default="text",
                       help="Output format (default: text)")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", required=False)

    # paths
    paths_parser = subparsers.add_parser("paths", help="Show available snippet locations")
    paths_parser.add_argument("filter", nargs="?", help="Filter categories by keyword")

    # create
    create_parser = subparsers.add_parser("create", help="Create new snippet from file")
    create_parser.add_argument("source_file", help="Source SKILL.md file")
    create_parser.add_argument("destination_path", help="Destination path (snippets/local/<category>/<name>/SKILL.md)")
    create_parser.add_argument("--pattern", help="Override pattern from frontmatter")
    create_parser.add_argument("--force", action="store_true", help="Overwrite if exists")

    # list
    list_parser = subparsers.add_parser("list", help="List and search snippets")
    list_parser.add_argument("name", nargs="?", help="Search term")

    # validate
    subparsers.add_parser("validate",
                                           help="Validate config and files")

    # Pre-process arguments to treat first positional as search term
    processed_args = preprocess_args(sys.argv[1:])
    args = parser.parse_args(processed_args)

    # Default to list command if no command specified
    if args.command is None:
        args.command = "list"
        args.name = None

    # Set defaults for paths
    script_dir = Path(__file__).parent
    config_path = args.config or script_dir / "config.json"
    snippets_dir = args.snippets_dir or script_dir.parent / "snippets" / "local"

    try:
        manager = SnippetManager(config_path, snippets_dir, use_base_config=False, config_name=None)

        # Run automatic validation on every invocation (except for validate command itself)
        # Only output if there are issues
        if args.command != "validate" and args.output != "json":
            validation_result = manager.validate()
            if not validation_result["config_valid"]:
                issues = validation_result["issues"]
                issue_count = len(issues)
                print(Colors.yellow(f"⚠ {issue_count} validation issue{'s' if issue_count != 1 else ''} detected:"), file=sys.stderr)

                for issue in issues:
                    if issue["type"] == "invalid_pattern":
                        snippet_files = issue["snippet"]
                        snippet_path = snippet_files[0] if isinstance(snippet_files, list) else snippet_files

                        # Show parent directory + filename for better context
                        path_parts = Path(snippet_path).parts
                        if len(path_parts) >= 2:
                            display_name = f"{path_parts[-2]}/{Path(snippet_path).name}"
                        else:
                            display_name = Path(snippet_path).name

                        pattern = issue["details"]["pattern"]
                        specific_issue = issue["details"].get("issue", "")

                        # Show specific issue in dim text
                        if specific_issue:
                            print(f"  {Colors.red('✗')} {Colors.cyan(display_name)}: {Colors.dim(specific_issue)}", file=sys.stderr)
                        else:
                            print(f"  {Colors.red('✗')} {Colors.cyan(display_name)}: {Colors.dim(pattern)}", file=sys.stderr)

                    elif issue["type"] == "missing_file":
                        print(f"  {Colors.red('✗')} Missing: {Colors.dim(issue['snippet'])}", file=sys.stderr)

                    elif issue["type"] == "duplicate_pattern":
                        snippet_names = [Path(s[0]).stem if isinstance(s, list) else Path(s).stem for s in issue["snippets"]]
                        print(f"  {Colors.red('✗')} Duplicate {Colors.yellow(issue['pattern'])} in: {', '.join(Colors.cyan(n) for n in snippet_names)}", file=sys.stderr)

                print(Colors.dim("\nRun 'snippets_cli.py validate' for full details\n"), file=sys.stderr)

        if args.command == "paths":
            filter_term = getattr(args, 'filter', None)
            data = manager.show_paths(filter_term)

            if args.output == "json":
                print(json.dumps(data, indent=2))
            else:
                print("\nAvailable snippet locations:\n")
                print(f"Base directory: {data['base_dir']}\n")
                print("Categories:")
                for cat in data["categories"]:
                    print(f"  {cat['name']}/")
                    print(f"    {cat['description']}")
                    print(f"    Path: {cat['path']}\n")

        elif args.command == "create":
            data = manager.create_from_file(
                args.source_file,
                args.destination_path,
                getattr(args, 'pattern', None),
                getattr(args, 'force', False)
            )

            if args.output == "json":
                print(json.dumps({"success": True, "data": data}, indent=2))
            else:
                print("\n✓ Snippet created successfully!")
                print(f"  Name: {data['name']}")
                print(f"  Pattern: {data['pattern']}")
                print(f"  Destination: {data['destination']}")
                print("\nTest it: Type trigger keyword in a new prompt")

        elif args.command == "list":
            search_term = args.name if hasattr(args, 'name') else None
            data = manager.list(search_term=search_term)

            # Auto-detect TTY mode
            is_tty = sys.stdout.isatty()

            if args.output == "json" or not is_tty:
                # Non-interactive mode
                print(json.dumps(data, indent=2))
            else:
                # Interactive mode
                snippets = data.get("snippets", [])
                if not snippets:
                    print("No snippets found.")
                else:
                    selected_idx = interactive_select(snippets, operation="edit", base_dir=snippets_dir.parent)
                    if selected_idx is not None:
                        snippet = snippets[selected_idx]
                        file_path = Path(snippet['files'][0])
                        if not file_path.is_absolute():
                            file_path = snippets_dir.parent / file_path

                        print(f"\nOpening {file_path} in $EDITOR...")
                        if open_in_editor(file_path):
                            print("Saved.")
                        else:
                            print("Editor closed without saving or error occurred.")

        elif args.command == "validate":
            data = manager.validate()
            message = "All snippets valid" if data["config_valid"] else "Validation issues found"
            print(format_output(True, "validate", data, message,
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
