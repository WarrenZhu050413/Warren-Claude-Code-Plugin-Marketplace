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
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import shutil
import hashlib


class SnippetError(Exception):
    """Base exception for snippet operations"""
    def __init__(self, code: str, message: str, details: Dict[str, Any] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class SnippetManager:
    """Core snippet management functionality"""

    def __init__(self, config_path: Path, snippets_dir: Path):
        self.config_path = config_path
        self.snippets_dir = snippets_dir
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load and validate config file"""
        if not self.config_path.exists():
            return {"mappings": []}

        try:
            with open(self.config_path) as f:
                config = json.load(f)
                if "mappings" not in config:
                    config["mappings"] = []
                return config
        except json.JSONDecodeError as e:
            raise SnippetError(
                "CONFIG_ERROR",
                f"Invalid JSON in config file: {e}",
                {"path": str(self.config_path)}
            )

    def _save_config(self):
        """Save config file with backup"""
        # Create backup
        if self.config_path.exists():
            backup_path = self.config_path.with_suffix('.json.bak')
            shutil.copy2(self.config_path, backup_path)

        # Save new config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            f.write('\n')

    def _validate_pattern(self, pattern: str) -> bool:
        """Validate regex pattern"""
        try:
            re.compile(pattern)
            return True
        except re.error as e:
            raise SnippetError(
                "INVALID_REGEX",
                f"Invalid regex pattern: {e}",
                {"pattern": pattern}
            )

    def _find_snippet(self, name: str) -> Optional[Dict]:
        """Find snippet by name"""
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

    def _generate_verification_hash(self, name: str) -> str:
        """Generate a unique verification hash for a snippet"""
        # Use snippet name + timestamp for uniqueness
        data = f"{name}-{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _add_verification_hash(self, file_path: Path, hash_value: str) -> None:
        """Add or update verification hash in snippet file"""
        if not file_path.exists():
            return

        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Check if hash already exists
        hash_line_idx = None
        for i, line in enumerate(lines):
            if 'VERIFICATION_HASH' in line:
                hash_line_idx = i
                break

        hash_text = f"\n**VERIFICATION_HASH:** `{hash_value}`\n\n"

        if hash_line_idx is not None:
            # Replace existing hash (and maintain blank lines)
            lines[hash_line_idx] = hash_text.strip() + '\n'
        else:
            # Add hash after first heading
            # Find first heading line
            heading_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('#'):
                    heading_idx = i
                    break

            # Insert after heading
            lines.insert(heading_idx + 1, hash_text)

        # Write back
        with open(file_path, 'w') as f:
            f.writelines(lines)

    def _extract_verification_hash(self, file_path: Path) -> Optional[str]:
        """Extract verification hash from snippet file"""
        if not file_path.exists():
            return None

        with open(file_path, 'r') as f:
            content = f.read()

        # Find hash in format: **VERIFICATION_HASH:** `hash` or VERIFICATION_HASH: `hash`
        match = re.search(r'\*\*VERIFICATION_HASH:\*\*\s*`([^`]+)`', content)
        if not match:
            match = re.search(r'VERIFICATION_HASH:\s*`([^`]+)`', content)
        return match.group(1) if match else None

    def create(self, name: str, pattern: str, content: str = None,
               file_path: str = None, file_paths: List[str] = None,
               separator: str = '\n', enabled: bool = True, force: bool = False) -> Dict:
        """Create a new snippet"""
        # Validate inputs
        if not name:
            raise SnippetError("INVALID_INPUT", "Snippet name is required")

        self._validate_pattern(pattern)

        snippet_file = f"snippets/{name}.md"
        snippet_path = self._get_snippet_path(name)

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

            # Write snippet file
            with open(snippet_path, 'w') as f:
                f.write(content)

            # Add verification hash
            verification_hash = self._generate_verification_hash(name)
            self._add_verification_hash(snippet_path, verification_hash)

            snippet_files = [snippet_file]
            total_size = snippet_path.stat().st_size

        # Update or add config mapping (always use array format)
        existing = self._find_snippet(name)
        if existing:
            existing["pattern"] = pattern
            existing["enabled"] = enabled
            existing["snippet"] = snippet_files  # Always array
            existing["separator"] = separator
            existing["name"] = name  # Add explicit name field
        else:
            self.config["mappings"].append({
                "name": name,  # Add explicit name field
                "pattern": pattern,
                "snippet": snippet_files,  # Always array
                "separator": separator,
                "enabled": enabled
            })

        self._save_config()

        return {
            "name": name,
            "pattern": pattern,
            "files": snippet_files,
            "file_count": len(snippet_files),
            "separator": separator,
            "enabled": enabled,
            "alternatives": self._count_alternatives(pattern),
            "size_bytes": total_size,
            "verification_hash": verification_hash if not file_paths else None
        }

    def list(self, name: str = None, show_content: bool = False,
             show_stats: bool = False) -> Dict:
        """List snippets"""
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

            snippet_info = {
                "name": snippet_name,
                "pattern": mapping["pattern"],
                "files": snippet_files,  # Show all files
                "file_count": len(snippet_files),
                "separator": mapping.get("separator", "\n"),
                "enabled": mapping.get("enabled", True),
                "alternatives": self._count_alternatives(mapping["pattern"])
            }

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

        # Rename
        if rename:
            new_snippet_file = f"snippets/{rename}.md"
            new_snippet_path = self._get_snippet_path(rename)

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

            # Update config (always use array format)
            existing["snippet"] = [new_snippet_file]
            changes["name"] = {"old": name, "new": rename}
            name = rename

        # Update verification hash if content or pattern changed
        verification_hash = None
        if content_updated or pattern is not None:
            verification_hash = self._generate_verification_hash(name)
            self._add_verification_hash(snippet_path if not rename else new_snippet_path, verification_hash)

        self._save_config()

        result = {
            "name": name,
            "changes": changes
        }
        if verification_hash:
            result["verification_hash"] = verification_hash

        return result

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

        # Remove from config
        self.config["mappings"] = [
            m for m in self.config["mappings"]
            if m["snippet"] != existing["snippet"]
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

            # Check file exists
            snippet_path = self.snippets_dir.parent / mapping["snippet"]
            if not snippet_path.exists():
                issues.append({
                    "type": "missing_file",
                    "snippet": mapping["snippet"],
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
        """Test if pattern matches text"""
        existing = self._find_snippet(name)
        if not existing:
            raise SnippetError(
                "NOT_FOUND",
                f"Snippet '{name}' not found",
                {"name": name}
            )

        pattern = existing["pattern"]
        matches = re.findall(pattern, text, re.IGNORECASE)

        return {
            "name": name,
            "pattern": pattern,
            "text": text,
            "matches": matches,
            "match_count": len(matches),
            "matched": len(matches) > 0
        }


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


def main():
    parser = argparse.ArgumentParser(
        description="Claude Code Snippets CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Global options
    parser.add_argument("--config", type=Path,
                       help="Config file path (default: ./config.json)")
    parser.add_argument("--snippets-dir", type=Path,
                       help="Snippets directory (default: ./snippets)")
    parser.add_argument("--format", choices=["json", "text"], default="json",
                       help="Output format (default: json)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    create_parser = subparsers.add_parser("create", help="Create new snippet")
    create_parser.add_argument("name", help="Snippet name")
    create_parser.add_argument("--pattern", required=True, help="Regex pattern")
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

    args = parser.parse_args()

    # Set defaults for paths
    script_dir = Path(__file__).parent
    config_path = args.config or script_dir / "config.json"
    snippets_dir = args.snippets_dir or script_dir / "snippets"

    try:
        manager = SnippetManager(config_path, snippets_dir)

        if args.command == "create":
            data = manager.create(
                args.name, args.pattern, args.content, args.file,
                getattr(args, 'files', None), args.separator,
                args.enabled, args.force
            )
            print(format_output(True, "create", data,
                              f"Snippet '{args.name}' created successfully",
                              format_type=args.format))

        elif args.command == "list":
            data = manager.list(args.name, args.show_content, args.show_stats)
            print(format_output(True, "list", data, format_type=args.format))

        elif args.command == "update":
            data = manager.update(
                args.name, args.pattern, args.content, args.file,
                args.enabled, args.rename
            )
            print(format_output(True, "update", data,
                              f"Snippet '{args.name}' updated successfully",
                              format_type=args.format))

        elif args.command == "delete":
            data = manager.delete(args.name, args.force, args.backup,
                                 args.backup_dir)
            print(format_output(True, "delete", data,
                              f"Snippet '{args.name}' deleted successfully",
                              format_type=args.format))

        elif args.command == "validate":
            data = manager.validate()
            message = "All snippets valid" if data["config_valid"] else "Validation issues found"
            print(format_output(True, "validate", data, message,
                              format_type=args.format))

        elif args.command == "test":
            data = manager.test(args.name, args.text)
            message = f"Pattern {'matched' if data['matched'] else 'did not match'}"
            print(format_output(True, "test", data, message,
                              format_type=args.format))

        sys.exit(0)

    except SnippetError as e:
        print(format_output(False, args.command, error=e, format_type=args.format),
              file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        error = SnippetError("UNKNOWN_ERROR", str(e))
        print(format_output(False, args.command, error=error, format_type=args.format),
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()