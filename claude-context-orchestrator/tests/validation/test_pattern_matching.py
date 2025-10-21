#!/usr/bin/env python3
"""
Test pattern matching for all snippets and skills.
Validates that regex patterns correctly match expected trigger words.
"""

import json
import re
import sys
from pathlib import Path

# Test cases: (snippet_name, test_inputs, should_match)
TEST_CASES = [
    # HTML
    ("HTML", ["HTML", "html", "write HTML", "generate html page"], True),
    ("HTML", ["htm", "hypertext", "markup"], False),

    # TDD
    ("tdd", ["TDD", "TDD:", "test-driven development"], True),
    ("tdd", ["test", "testing", "td"], False),

    # Mail
    ("mail", ["email", "mail", "e-mail", "message", "inbox", "send to", "send message"], True),
    ("mail", ["mai", "emai", "mailbox"], False),

    # GCal
    ("gcal", ["gcal", "g-cal", "google calendar", "calendar", "event", "schedule", "appointment"], True),
    ("gcal", ["cal", "gc", "scheduling"], False),

    # Style
    ("style", ["STYLE", "STYLE:", "apply STYLE"], True),
    ("style", ["style", "styling", "css"], False),

    # Subagent
    ("subagent-viz", ["subagent", "sub-agent", "sub agent", "subagents"], True),
    ("subagent-viz", ["agent", "sub", "visualization"], False),

    # PLANHTML
    ("PLANHTML", ["PLANHTML", "PLANHTMl", "PLANHTml", "html_plan", "html-plan"], True),
    ("PLANHTML", ["plan", "html", "planning"], False),

    # Download PDF
    ("download-pdf", ["DOWNLOAD", "DLD", "DOWNLOAD:"], True),
    ("download-pdf", ["download", "dld", "pdf"], False),

    # POST
    ("post", ["POST", "post", "shitPOST", "shitpost"], True),
    ("post", ["posting", "pos", "posts"], False),

    # NOTIFY
    ("NOTIFY", ["NOTIFY", "NOTIFY:"], True),
    ("NOTIFY", ["notify", "notification", "notif"], False),

    # TXT
    ("txt", ["TXT:", "TXT/", "TXT.", "TXT "], True),
    ("txt", ["TXT", "txt", "text"], False),

    # CLEAR
    ("clear", ["CLEAR:", "CLEAR/", "CLEAR.", "CLEAR "], True),
    ("clear", ["CLEAR", "clear", "clearing"], False),

    # TODO
    ("add-todo", ["TODO", "add-todo", "TODO:", "add-todo."], True),
    ("add-todo", ["todo", "todos", "to-do"], False),

    # LINEAR
    ("LINEAR", ["linear", "linearapp", "linearapi", "linear-app", "linear_api"], True),
    ("LINEAR", ["line", "linear-", "linea"], False),

    # Screenshot
    ("screenshot-workflow", ["screenshot", "screenshots", "screenshot:"], True),
    ("screenshot-workflow", ["screen", "shot", "capture"], False),

    # EXPLAIN
    ("explain", ["EXPLAIN", "EXPLAIN:"], True),
    ("explain", ["explain", "explaining", "explanation"], False),

    # LUA
    ("lua", ["LUA", "LUA:"], True),
    ("lua", ["lua", "Lua", "luau"], False),

    # ITER
    ("iter", ["ITER", "ITER:"], True),
    ("iter", ["iter", "iterate", "iteration"], False),

    # PAPER
    ("PAPER", ["PAPER", "PAPER:"], True),
    ("PAPER", ["paper", "Paper", "papers"], False),

    # ISSUE
    ("create-issue", ["ISSUE", "ISSUE:"], True),
    ("create-issue", ["issue", "issues", "problem"], False),

    # Nvim
    ("nvim", ["nvim", "neovim", "nvim:", "neovim."], True),
    ("nvim", ["vim", "nvi", "neo"], False),
]

def load_config():
    """Load config.json"""
    # Navigate from tests/validation/ to plugin root, then to scripts/
    config_path = Path(__file__).parent.parent.parent / "scripts" / "config.json"
    with open(config_path) as f:
        return json.load(f)

def test_patterns():
    """Test all pattern matches"""
    config = load_config()
    mappings = {m["name"]: m["pattern"] for m in config["mappings"]}

    total = 0
    passed = 0
    failed = 0

    print("Testing Pattern Matching")
    print("=" * 60)

    for snippet_name, test_inputs, should_match in TEST_CASES:
        if snippet_name not in mappings:
            print(f"⚠️  WARNING: {snippet_name} not found in config")
            continue

        pattern = mappings[snippet_name]
        regex = re.compile(pattern, re.IGNORECASE if snippet_name in ["HTML", "LINEAR", "screenshot-workflow", "mail", "gcal"] else 0)

        for test_input in test_inputs:
            total += 1
            match = bool(regex.search(test_input))

            if match == should_match:
                passed += 1
                status = "✓"
            else:
                failed += 1
                status = "✗"
                print(f"{status} {snippet_name}: '{test_input}' (expected {should_match}, got {match})")

    print()
    print(f"Results: {passed}/{total} passed, {failed} failed")
    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    success = test_patterns()
    sys.exit(0 if success else 1)
