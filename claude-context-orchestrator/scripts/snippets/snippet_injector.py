#!/usr/bin/env python3
"""
Claude Code Snippets Hook - Injects snippets into prompts via regex matching

This hook listens to UserPromptSubmit events and injects matched snippet content
anywhere in the user's message based on regex patterns.

Supports multi-config system with priority-based merging:
- config.json: Base configuration (priority: 0)
- config.local.json: Local overrides (priority: 100)
- config.{name}.json: Named configs (priority: 50 or specified)

Higher priority configs override lower priority ones when snippet names conflict.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

# Debug logging to file
DEBUG_LOG = Path("/tmp/snippet_hook_debug.log")

def debug_log(msg):
    with open(DEBUG_LOG, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

# Get plugin root directory
# snippet_injector.py is in scripts/snippets/
# Config files are in scripts/snippets/
# Snippet files referenced in config are relative to config file directory (scripts/snippets/)
# e.g., ../../snippets/local/... resolves from scripts/snippets/ to claude-context-orchestrator/snippets/local/
SCRIPT_DIR = Path(__file__).parent  # scripts/snippets/
CONFIG_ROOT = SCRIPT_DIR  # Config files are in scripts/snippets/
SNIPPET_BASE = SCRIPT_DIR  # Base path for resolving snippet file paths (same as config location)

# Default priorities for standard config files
DEFAULT_PRIORITIES = {
    "config.json": 0,
    "config.local.json": 100,
}


def load_merged_config():
    """Load and merge all config*.json files by priority.

    Returns:
        dict: Merged configuration with all mappings
    """
    config_files = []

    # Find all config*.json files
    for config_path in sorted(CONFIG_ROOT.glob("config*.json")):
        try:
            with open(config_path) as f:
                config_data = json.load(f)

            # Determine priority
            filename = config_path.name
            if filename in DEFAULT_PRIORITIES:
                # Use default priority, but allow override from file
                priority = config_data.get("priority", DEFAULT_PRIORITIES[filename])
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

    # Sort by priority (ascending, so higher priority comes later and overwrites)
    config_files.sort(key=lambda x: x["priority"])

    # Merge all configs by snippet name
    merged_mappings = {}
    for config_file in config_files:
        for mapping in config_file["data"].get("mappings", []):
            name = mapping.get("name", "")
            if name:
                # Higher priority configs come later, so they overwrite
                merged_mappings[name] = mapping

    return {"mappings": list(merged_mappings.values())}


try:
    # Read the hook input
    input_data = json.load(sys.stdin)
    prompt = input_data.get("prompt", "")

    # Load merged config (base + local)
    debug_log(f"Starting hook, prompt: {prompt[:100]}...")
    config = load_merged_config()
    debug_log(f"Loaded config with {len(config.get('mappings', []))} mappings")

    # Check for matches (all patterns are regex)
    matched_snippets = []
    for mapping in config.get("mappings", []):
        # Skip disabled snippets
        if not mapping.get("enabled", True):
            continue

        pattern = mapping["pattern"]

        # All patterns are treated as regex with case-sensitive matching
        if re.search(pattern, prompt):
            debug_log(f"MATCH: {mapping.get('name')} with pattern {pattern}")
            # Store snippet files array and separator
            snippet_files = mapping["snippet"]  # Now always an array
            separator = mapping.get("separator", "\n")
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
                snippet_path = (SNIPPET_BASE / snippet_file).resolve()
                if snippet_path.exists():
                    with open(snippet_path) as f:
                        content = f.read()
                        file_contents.append(content)

            # Join files with separator and add to context
            if file_contents:
                combined_content = separator.join(file_contents)
                additional_context.append(combined_content)

        if additional_context:
            # Output plain text - Claude Code adds any stdout as context
            # This is simpler and more reliable than JSON format
            output = "\n\n".join(additional_context)
            debug_log(f"OUTPUT: {len(output)} chars")
            print(output)
        else:
            debug_log("No context to output")
    else:
        debug_log("No matches found")

except Exception as e:
    # Log error to stderr for debugging
    debug_log(f"ERROR: {e}")
    print(f"Snippet injection hook error: {e}", file=sys.stderr)
    # Exit gracefully - don't block the prompt
    pass

debug_log("Hook complete")
sys.exit(0)
