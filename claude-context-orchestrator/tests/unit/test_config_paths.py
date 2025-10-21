#!/usr/bin/env python3
"""
Test that all paths in config.json and config.local.json point to existing files.
"""

import json
import sys
from pathlib import Path

def test_config_paths(config_name):
    """Test paths in a config file"""
    plugin_root = Path(__file__).parent.parent
    config_path = plugin_root / "scripts" / config_name

    print(f"\nTesting {config_name}")
    print("=" * 60)

    with open(config_path) as f:
        config = json.load(f)

    failed = 0
    passed = 0

    for mapping in config["mappings"]:
        name = mapping["name"]
        snippets = mapping.get("snippet", [])

        for snippet_path in snippets:
            # Convert relative path to absolute
            # snippet_path is relative to scripts/ directory
            full_path = (plugin_root / "scripts" / snippet_path).resolve()

            if full_path.exists():
                print(f"✓ {name}: {snippet_path}")
                passed += 1
            else:
                print(f"✗ {name}: {snippet_path} NOT FOUND")
                print(f"  Expected: {full_path}")
                failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    success = True

    # Test both config files
    success &= test_config_paths("config.json")
    success &= test_config_paths("config.local.json")

    sys.exit(0 if success else 1)
