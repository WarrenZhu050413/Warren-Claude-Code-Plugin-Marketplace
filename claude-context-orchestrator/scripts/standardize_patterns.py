#!/usr/bin/env python3
"""
Standardize all regex patterns in config files to: \\b(PATTERN)[.,;:]?\\b
"""

import json
import re
from pathlib import Path


def standardize_pattern(pattern: str, name: str) -> str:
    """
    Standardize a pattern to the format: \\b(PATTERN)[.,;:]?\\b

    Special cases:
    - Complex patterns (with |, .*,  etc. beyond simple alternation) are kept as-is
    - Simple patterns are wrapped in \\b(...)[ .,;:]?\\b
    """

    # Special cases to keep as-is (complex patterns)
    if re.search(r'\.\*|\.+[^,;:]', pattern):
        print(f"  SKIP (complex): {name}: {pattern}")
        return pattern

    # Extract the core pattern
    # Remove existing word boundaries
    core = pattern.replace('\\\\b', '').replace('\\b', '')

    # Remove existing optional punctuation patterns
    core = re.sub(r'\[.,;:\]\?', '', core)
    core = re.sub(r'\[/:\\.\]\?', '', core)
    core = re.sub(r'\[/:\\.\]\\\\s\*', '', core)
    core = re.sub(r'\\\\s\*', '', core)

    # Remove existing parentheses if they're the outermost
    if core.startswith('(') and core.endswith(')'):
        core = core[1:-1]

    # Remove trailing 's?' for plurals
    core = re.sub(r's\?$', '', core)

    # Ensure core uses only valid separators for multi-word
    # Allow: A-Z, 0-9, |, _, -
    if not re.match(r'^[A-Z0-9_|\-]+$', core):
        print(f"  WARN: {name}: Invalid characters in core pattern: {core}")
        return pattern  # Keep original if invalid

    # Build standardized pattern
    standardized = f"\\\\b({core})[.,;:]?\\\\b"

    if standardized != pattern:
        print(f"  FIX: {name}")
        print(f"    OLD: {pattern}")
        print(f"    NEW: {standardized}")

    return standardized


def standardize_config(config_path: Path):
    """Standardize patterns in a config file"""
    print(f"\nProcessing: {config_path.name}")
    print("=" * 60)

    with open(config_path) as f:
        config = json.load(f)

    for mapping in config.get("mappings", []):
        original_pattern = mapping["pattern"]
        standardized_pattern = standardize_pattern(original_pattern, mapping["name"])
        mapping["pattern"] = standardized_pattern

    # Write back with pretty formatting
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print("\n✅ Config updated successfully")


if __name__ == "__main__":
    script_dir = Path(__file__).parent

    # Standardize config.local.json
    config_local = script_dir / "config.local.json"
    if config_local.exists():
        standardize_config(config_local)

    print("\n" + "=" * 60)
    print("✅ All patterns standardized")
    print("=" * 60)
