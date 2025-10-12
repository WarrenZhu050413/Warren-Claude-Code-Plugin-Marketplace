#!/usr/bin/env python3
"""
Claude Code Snippets Hook - Injects snippets into prompts via regex matching

This hook listens to UserPromptSubmit events and injects matched snippet content
anywhere in the user's message based on regex patterns.

Supports layered configuration:
- config.json: Base configuration (committed to git)
- config.local.json: User-specific overrides (gitignored)

Local config takes precedence over base config.
"""
import json
import sys
import re
from pathlib import Path

# Get plugin root directory
PLUGIN_ROOT = Path(__file__).parent
CONFIG_PATH = PLUGIN_ROOT / 'config.json'
CONFIG_LOCAL_PATH = PLUGIN_ROOT / 'config.local.json'

def load_merged_config():
    """Load and merge base config with local config."""
    # Load base config
    base_config = {'mappings': []}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            base_config = json.load(f)

    # Load local config if it exists
    local_config = {'mappings': []}
    if CONFIG_LOCAL_PATH.exists():
        with open(CONFIG_LOCAL_PATH) as f:
            local_config = json.load(f)

    # Merge configs: local overrides base by name
    # Create a dict of base mappings by name
    merged_mappings = {}
    for mapping in base_config.get('mappings', []):
        name = mapping.get('name', '')
        if name:
            merged_mappings[name] = mapping

    # Override/add from local config
    for mapping in local_config.get('mappings', []):
        name = mapping.get('name', '')
        if name:
            merged_mappings[name] = mapping

    # Return merged config
    return {'mappings': list(merged_mappings.values())}

try:
    # Read the hook input
    input_data = json.load(sys.stdin)
    prompt = input_data.get('prompt', '')

    # Load merged config (base + local)
    config = load_merged_config()

    # Check for matches (all patterns are regex)
    matched_snippets = []
    for mapping in config.get('mappings', []):
        # Skip disabled snippets
        if not mapping.get('enabled', True):
            continue

        pattern = mapping['pattern']

        # All patterns are treated as regex with case-insensitive matching
        if re.search(pattern, prompt, re.IGNORECASE):
            # Store snippet files array and separator
            snippet_files = mapping['snippet']  # Now always an array
            separator = mapping.get('separator', '\n')
            matched_snippets.append((snippet_files, separator))

    # Remove duplicates while preserving order
    seen = set()
    unique_snippets = []
    for snippet_tuple in matched_snippets:
        key = (tuple(snippet_tuple[0]), snippet_tuple[1])
        if key not in seen:
            seen.add(key)
            unique_snippets.append(snippet_tuple)
    matched_snippets = unique_snippets

    # Load and append snippets
    if matched_snippets:
        additional_context = []
        for snippet_files, separator in matched_snippets:
            # Load all files for this snippet and join with separator
            file_contents = []
            for snippet_file in snippet_files:
                snippet_path = PLUGIN_ROOT / snippet_file
                if snippet_path.exists():
                    with open(snippet_path) as f:
                        content = f.read()
                        file_contents.append(content)

            # Join files with separator and add to context
            if file_contents:
                combined_content = separator.join(file_contents)
                additional_context.append(combined_content)

        if additional_context:
            # Add global announcement instruction before all snippets
            meta_instruction = """
**CRITICAL INSTRUCTION - READ THIS FIRST**:

Before responding to the user, you MUST:
1. Scan the ENTIRE context below for ALL snippets that have `ANNOUNCE_USAGE: true` in their YAML frontmatter
2. Extract ALL `SNIPPET_NAME` values from those snippets
3. Announce them at the VERY BEGINNING of your response using this exact format:
   - If ONE snippet is active: 📎 **Active Context**: snippet_name
   - If MULTIPLE snippets are active: 📎 **Active Contexts**: snippet1, snippet2, snippet3

This announcement MUST be the first thing in your response, before any other content.

---

"""
            # Prepend meta-instruction to the combined context
            full_context = meta_instruction + "\n".join(additional_context)

            # Return JSON with additional context
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": full_context
                }
            }
            print(json.dumps(output))

except Exception as e:
    # Log error to stderr for debugging
    print(f"Snippet injection hook error: {e}", file=sys.stderr)
    # Exit gracefully - don't block the prompt
    pass

sys.exit(0)
