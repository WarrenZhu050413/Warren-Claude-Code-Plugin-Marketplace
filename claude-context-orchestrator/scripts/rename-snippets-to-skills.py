#!/usr/bin/env python3
"""
Rename all SNIPPET.md files to SKILL.md for interoperability with Claude Code skills system.
Updates all configuration file references automatically.
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime


def find_snippet_files():
    """Find all SNIPPET.md files in the repository."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    snippet_files = []
    for snippet_file in repo_root.rglob("SNIPPET.md"):
        snippet_files.append(snippet_file)

    return sorted(snippet_files)


def rename_snippet_files(dry_run=True):
    """Rename all SNIPPET.md files to SKILL.md."""
    snippet_files = find_snippet_files()
    changes = []

    for snippet_file in snippet_files:
        skill_file = snippet_file.parent / "SKILL.md"

        if skill_file.exists():
            print(f"⚠️  SKIP (SKILL.md exists): {snippet_file.relative_to(snippet_file.parents[4])}")
            continue

        if dry_run:
            print(f"→ Would rename: {snippet_file.relative_to(snippet_file.parents[4])}")
        else:
            snippet_file.rename(skill_file)
            print(f"✓ Renamed: {snippet_file.relative_to(snippet_file.parents[4])}")

        changes.append({
            "type": "rename",
            "from": str(snippet_file),
            "to": str(skill_file)
        })

    return changes


def update_config_file(config_path, dry_run=True):
    """Update snippet references in config file."""
    if not config_path.exists():
        return []

    # Read config
    with open(config_path, 'r') as f:
        config = json.load(f)

    changes = []

    # Update all snippet references
    if "mappings" in config:
        for mapping in config["mappings"]:
            if "snippet" in mapping and isinstance(mapping["snippet"], list):
                for i, snippet_path in enumerate(mapping["snippet"]):
                    if "SNIPPET.md" in snippet_path:
                        old_path = snippet_path
                        new_path = snippet_path.replace("SNIPPET.md", "SKILL.md")
                        mapping["snippet"][i] = new_path
                        changes.append({
                            "type": "config_update",
                            "mapping": mapping["name"],
                            "from": old_path,
                            "to": new_path,
                            "config_file": str(config_path)
                        })
                        print(f"→ Update in {config_path.name}: {mapping['name']}")
                        print(f"  {old_path} → {new_path}")

    if not dry_run and changes:
        # Create backup
        backup_path = config_path.parent / f"{config_path.name}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(config_path, backup_path)
        print(f"✓ Backup created: {backup_path.name}")

        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✓ Updated: {config_path.name}")

    return changes


def main():
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    print("=" * 70)
    print("SNIPPET.md → SKILL.md Standardization")
    print("=" * 70)
    print()

    # Parse command-line arguments
    import sys
    dry_run = "--force" not in sys.argv

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print("   Run with --force to apply changes\n")
    else:
        print("⚡ FORCE MODE - Changes will be applied\n")

    # Step 1: Find and rename SNIPPET.md files
    print("Step 1: Renaming SNIPPET.md → SKILL.md files")
    print("-" * 70)
    file_changes = rename_snippet_files(dry_run=dry_run)
    print(f"Total files: {len(file_changes)}\n")

    # Step 2: Update config.json
    print("Step 2: Updating config.json")
    print("-" * 70)
    config_json_path = script_dir / "config.json"
    config_changes = update_config_file(config_json_path, dry_run=dry_run)
    if not config_changes:
        print("No changes needed in config.json\n")
    else:
        print(f"Total updates: {len(config_changes)}\n")

    # Step 3: Update config.local.json
    print("Step 3: Updating config.local.json")
    print("-" * 70)
    config_local_path = script_dir / "config.local.json"
    if config_local_path.exists():
        local_changes = update_config_file(config_local_path, dry_run=dry_run)
        print(f"Total updates: {len(local_changes)}\n")
    else:
        print("config.local.json not found (skipped)\n")
        local_changes = []

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    total_file_changes = len(file_changes)
    total_config_changes = len(config_changes) + len(local_changes)

    print(f"Files to rename: {total_file_changes}")
    print(f"Config entries to update: {total_config_changes}")
    print()

    if dry_run:
        print("✓ Dry run complete. Run with --force to apply changes:")
        print(f"  python3 {Path(__file__).name} --force")
    else:
        print("✓ All changes applied successfully!")
        print()
        print("Next steps:")
        print("1. Review the changes:")
        print("   git diff scripts/config*.json")
        print("2. Verify SKILL.md files exist:")
        print("   find . -name SKILL.md | grep snippets/local | head -5")
        print("3. Restart Claude Code to reload snippets")
        print("4. Test snippet injection by typing trigger keywords")


if __name__ == "__main__":
    main()
