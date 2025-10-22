#!/usr/bin/env python3
"""
Disable snippet announcements across all snippets.

This script:
1. Sets ANNOUNCE_USAGE: false for all snippets
2. Removes announcement instruction blocks
"""

import re
from pathlib import Path

# Plugin root
PLUGIN_ROOT = Path(__file__).parent.parent

# Find all snippet files
snippet_files = list(PLUGIN_ROOT.glob("snippets/**/*.md")) + list(PLUGIN_ROOT.glob("skills/**/*.md"))

print(f"Found {len(snippet_files)} snippet/skill files\n")

for snippet_file in snippet_files:
    try:
        content = snippet_file.read_text()
        original_content = content

        # 1. Change ANNOUNCE_USAGE: true to false
        content = re.sub(
            r'^ANNOUNCE_USAGE:\s*true\s*$',
            'ANNOUNCE_USAGE: false',
            content,
            flags=re.MULTILINE
        )

        # 2. Remove announcement instruction blocks
        # Pattern: **INSTRUCTION TO CLAUDE**: ... up to the next --- or ##
        content = re.sub(
            r'\*\*INSTRUCTION TO CLAUDE\*\*:.*?At the very beginning of your response.*?(?=^---$|^##|\*\*VERIFICATION_HASH\*\*)',
            '',
            content,
            flags=re.MULTILINE | re.DOTALL
        )

        # Clean up extra blank lines (more than 2 consecutive)
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Save if changed
        if content != original_content:
            snippet_file.write_text(content)
            print(f"✅ Updated: {snippet_file.relative_to(PLUGIN_ROOT)}")

    except Exception as e:
        print(f"❌ Error processing {snippet_file.name}: {e}")

print("\n✅ Done!")
