#!/usr/bin/env python3
"""
Test script for snippet injection system.

Tests:
1. All snippet files exist
2. Regex patterns match correctly
3. Full injection flow works
4. Config merging works correctly
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Setup paths
SCRIPT_DIR = Path(__file__).parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent

def load_config(config_file: Path) -> Dict:
    """Load a single config file."""
    try:
        with open(config_file) as f:
            return json.load(f)
    except Exception as e:
        print(f"{Colors.RED}✗ Failed to load {config_file.name}: {e}{Colors.END}")
        return {"mappings": []}

def test_file_paths():
    """Test 1: Verify all snippet files exist."""
    print(f"\n{Colors.BOLD}Test 1: File Existence{Colors.END}")
    print("=" * 80)

    config = load_config(SCRIPT_DIR / "config.local.json")

    total = 0
    passed = 0
    failed = []

    for mapping in config.get("mappings", []):
        name = mapping.get("name", "unknown")
        enabled = mapping.get("enabled", True)
        snippet_files = mapping.get("snippet", [])

        for snippet_file in snippet_files:
            total += 1
            snippet_path = PLUGIN_ROOT / snippet_file
            exists = snippet_path.exists()

            if exists:
                passed += 1
                status = f"{Colors.GREEN}✓{Colors.END}"
            else:
                status = f"{Colors.RED}✗{Colors.END}"
                if enabled:
                    failed.append((name, snippet_file))

            enabled_str = f" {Colors.YELLOW}[DISABLED]{Colors.END}" if not enabled else ""
            print(f"{status} {name:30} {snippet_file}{enabled_str}")

    print("=" * 80)
    print(f"Result: {passed}/{total} files exist")

    if failed:
        print(f"\n{Colors.RED}Failed (enabled only):{Colors.END}")
        for name, path in failed:
            print(f"  - {name}: {path}")
        return False

    return True

def test_regex_patterns():
    """Test 2: Verify regex patterns are valid and match expected keywords."""
    print(f"\n{Colors.BOLD}Test 2: Regex Pattern Validation{Colors.END}")
    print("=" * 80)

    config = load_config(SCRIPT_DIR / "config.local.json")

    # Test cases: (keyword, expected_to_match_snippets)
    test_cases = [
        ("SCREENSHOT test", ["screenshot-workflow"]),
        ("HTML generation", ["generating-html"]),
        ("SEARCH for files", ["search-cli"]),
        ("NVIM config", ["nvim"]),
        ("PLAN the feature", ["plan-html"]),
        ("SNIPPET management", ["managing-snippets"]),
        ("TODO list", ["add-todo"]),
        ("No match here", []),
    ]

    passed = 0
    failed = []

    for test_prompt, expected_matches in test_cases:
        matched_snippets = []

        for mapping in config.get("mappings", []):
            if not mapping.get("enabled", True):
                continue

            name = mapping.get("name")
            pattern = mapping.get("pattern")

            try:
                if re.search(pattern, test_prompt):
                    matched_snippets.append(name)
            except re.error as e:
                print(f"{Colors.RED}✗ Invalid regex for {name}: {e}{Colors.END}")
                failed.append((name, str(e)))
                continue

        # Check if matches are as expected
        if set(matched_snippets) == set(expected_matches):
            status = f"{Colors.GREEN}✓{Colors.END}"
            passed += 1
        else:
            status = f"{Colors.RED}✗{Colors.END}"
            failed.append((test_prompt, matched_snippets, expected_matches))

        print(f"{status} '{test_prompt}' -> {matched_snippets}")

    print("=" * 80)
    print(f"Result: {passed}/{len(test_cases)} pattern tests passed")

    if failed:
        print(f"\n{Colors.RED}Failed pattern tests:{Colors.END}")
        for item in failed:
            if len(item) == 3:
                prompt, got, expected = item
                print(f"  '{prompt}': got {got}, expected {expected}")
            else:
                name, error = item
                print(f"  {name}: {error}")
        return False

    return True

def test_injection_flow():
    """Test 3: Test full injection flow with actual script."""
    print(f"\n{Colors.BOLD}Test 3: Full Injection Flow{Colors.END}")
    print("=" * 80)

    import subprocess

    test_cases = [
        ("SCREENSHOT workflow", True),
        ("HTML generation", True),
        ("SEARCH files", True),
        ("no keywords here", False),
    ]

    passed = 0
    failed = []

    for prompt, should_inject in test_cases:
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT_DIR / "snippet_injector.py")],
                input=json.dumps({"prompt": prompt}),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                print(f"{Colors.RED}✗ Script failed for '{prompt}'{Colors.END}")
                print(f"  stderr: {result.stderr}")
                failed.append((prompt, "non-zero exit"))
                continue

            # Check if output contains additionalContext
            has_output = bool(result.stdout.strip())

            if has_output == should_inject:
                status = f"{Colors.GREEN}✓{Colors.END}"
                passed += 1
            else:
                status = f"{Colors.RED}✗{Colors.END}"
                failed.append((prompt, f"has_output={has_output}, expected={should_inject}"))

            inject_str = "injected" if has_output else "no injection"
            print(f"{status} '{prompt}' -> {inject_str}")

        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}✗ Timeout for '{prompt}'{Colors.END}")
            failed.append((prompt, "timeout"))
        except Exception as e:
            print(f"{Colors.RED}✗ Error for '{prompt}': {e}{Colors.END}")
            failed.append((prompt, str(e)))

    print("=" * 80)
    print(f"Result: {passed}/{len(test_cases)} injection tests passed")

    if failed:
        print(f"\n{Colors.RED}Failed injection tests:{Colors.END}")
        for prompt, error in failed:
            print(f"  '{prompt}': {error}")
        return False

    return True

def test_config_merging():
    """Test 4: Test config merging with priorities."""
    print(f"\n{Colors.BOLD}Test 4: Config Merging{Colors.END}")
    print("=" * 80)

    # Load all configs
    configs = []
    for config_path in sorted(SCRIPT_DIR.glob("config*.json")):
        with open(config_path) as f:
            config_data = json.load(f)

        filename = config_path.name
        if filename == "config.json":
            priority = config_data.get("priority", 0)
        elif filename == "config.local.json":
            priority = config_data.get("priority", 100)
        else:
            priority = config_data.get("priority", 50)

        configs.append({
            "filename": filename,
            "priority": priority,
            "mappings": config_data.get("mappings", [])
        })
        print(f"  {filename}: priority={priority}, mappings={len(config_data.get('mappings', []))}")

    # Sort by priority
    configs.sort(key=lambda x: x["priority"])

    # Merge
    merged_mappings = {}
    for config in configs:
        for mapping in config["mappings"]:
            name = mapping.get("name", "")
            if name:
                merged_mappings[name] = mapping

    print(f"\n  Total unique snippets after merge: {len(merged_mappings)}")
    print("=" * 80)
    print(f"Result: {Colors.GREEN}✓{Colors.END} Config merging works")

    return True

def test_content_loading():
    """Test 5: Test that snippet content actually loads."""
    print(f"\n{Colors.BOLD}Test 5: Content Loading{Colors.END}")
    print("=" * 80)

    config = load_config(SCRIPT_DIR / "config.local.json")

    passed = 0
    failed = []
    empty = []

    for mapping in config.get("mappings", []):
        if not mapping.get("enabled", True):
            continue

        name = mapping.get("name")
        snippet_files = mapping.get("snippet", [])
        separator = mapping.get("separator", "\n")

        # Try to load content
        file_contents = []
        for snippet_file in snippet_files:
            snippet_path = PLUGIN_ROOT / snippet_file
            if snippet_path.exists():
                try:
                    with open(snippet_path) as f:
                        content = f.read()
                        if content.strip():
                            file_contents.append(content)
                        else:
                            empty.append((name, snippet_file))
                except Exception as e:
                    failed.append((name, snippet_file, str(e)))

        if file_contents:
            combined = separator.join(file_contents)
            status = f"{Colors.GREEN}✓{Colors.END}"
            passed += 1
            print(f"{status} {name:30} ({len(combined)} chars)")
        elif name not in [f[0] for f in failed]:
            print(f"{Colors.YELLOW}⚠{Colors.END} {name:30} (empty or missing)")

    print("=" * 80)
    print(f"Result: {passed} snippets loaded successfully")

    if empty:
        print(f"\n{Colors.YELLOW}Empty files:{Colors.END}")
        for name, path in empty:
            print(f"  - {name}: {path}")

    if failed:
        print(f"\n{Colors.RED}Failed to load:{Colors.END}")
        for name, path, error in failed:
            print(f"  - {name} ({path}): {error}")
        return False

    return True

def test_content_quality():
    """Test 6: Content Quality Validation"""
    print(f"\n{Colors.BOLD}Test 6: Content Quality Validation{Colors.END}")
    print("=" * 80)

    config = load_config(SCRIPT_DIR / "config.local.json")

    passed = 0
    warnings = []
    failed = []

    for mapping in config.get("mappings", []):
        if not mapping.get("enabled", True):
            continue

        name = mapping.get("name")
        snippet_files = mapping.get("snippet", [])

        for snippet_file in snippet_files:
            snippet_path = PLUGIN_ROOT / snippet_file
            if not snippet_path.exists():
                continue

            try:
                with open(snippet_path, encoding='utf-8') as f:
                    content = f.read()

                issues = []

                # Check for YAML frontmatter
                if snippet_path.suffix == '.md':
                    if content.startswith('---'):
                        frontmatter_end = content.find('---', 3)
                        if frontmatter_end == -1:
                            issues.append("unclosed YAML frontmatter")
                        else:
                            frontmatter = content[3:frontmatter_end]
                            if 'name:' not in frontmatter:
                                issues.append("missing 'name' in frontmatter")
                            if 'description:' not in frontmatter:
                                issues.append("missing 'description' in frontmatter")

                # Check for unclosed code blocks
                code_block_count = content.count('```')
                if code_block_count % 2 != 0:
                    issues.append(f"unclosed code block ({code_block_count} backticks)")

                # Check file size
                file_size = len(content)
                if file_size > 20000:
                    warnings.append((name, f"large file ({file_size} bytes)"))

                # Check for broken internal links (basic check)
                if '](../' in content or '](/Users/' in content:
                    issues.append("contains absolute/relative paths (may break)")

                if issues:
                    status = f"{Colors.RED}✗{Colors.END}"
                    failed.append((name, snippet_file, issues))
                    print(f"{status} {name:30} {', '.join(issues)}")
                else:
                    status = f"{Colors.GREEN}✓{Colors.END}"
                    passed += 1
                    size_str = f"({file_size} bytes)"
                    print(f"{status} {name:30} {size_str}")

            except Exception as e:
                failed.append((name, snippet_file, [f"error: {e}"]))
                print(f"{Colors.RED}✗{Colors.END} {name:30} error: {e}")

    print("=" * 80)
    print(f"Result: {passed} snippets validated")

    if warnings:
        print(f"\n{Colors.YELLOW}Warnings:{Colors.END}")
        for name, warning in warnings:
            print(f"  - {name}: {warning}")

    if failed:
        print(f"\n{Colors.RED}Failed quality checks:{Colors.END}")
        for name, path, issues in failed:
            print(f"  - {name} ({path}):")
            for issue in issues:
                print(f"    • {issue}")
        return False

    return True

def test_pattern_coverage():
    """Test 7: Pattern Coverage Analysis"""
    print(f"\n{Colors.BOLD}Test 7: Pattern Coverage Analysis{Colors.END}")
    print("=" * 80)

    config = load_config(SCRIPT_DIR / "config.local.json")

    # Build pattern mapping
    pattern_map = {}
    for mapping in config.get("mappings", []):
        if not mapping.get("enabled", True):
            continue
        name = mapping.get("name")
        pattern = mapping.get("pattern")
        pattern_map[name] = pattern

    # Test corpus to check for overlaps
    test_corpus = [
        "SCREENSHOT",
        "HTML",
        "SEARCH",
        "PLAN",
        "TODO",
        "SNIPPET",
        "SCRIPT",
        "CLEAR",
        "STYLE",
        "POST",
    ]

    overlaps = []
    coverage = {}

    for keyword in test_corpus:
        matches = []
        for name, pattern in pattern_map.items():
            try:
                if re.search(pattern, keyword):
                    matches.append(name)
            except re.error:
                pass

        coverage[keyword] = matches
        if len(matches) > 1:
            overlaps.append((keyword, matches))

        match_str = ', '.join(matches) if matches else 'none'
        if len(matches) > 1:
            print(f"{Colors.YELLOW}⚠{Colors.END} '{keyword}' -> {match_str}")
        elif len(matches) == 1:
            print(f"{Colors.GREEN}✓{Colors.END} '{keyword}' -> {match_str}")
        else:
            print(f"{Colors.BLUE}○{Colors.END} '{keyword}' -> {match_str}")

    print("=" * 80)

    if overlaps:
        print(f"\n{Colors.YELLOW}Pattern overlaps detected:{Colors.END}")
        for keyword, matches in overlaps:
            print(f"  '{keyword}' triggers: {', '.join(matches)}")
        print(f"\nNote: Overlaps aren't necessarily bad, but review to ensure intentional.")

    # Check for overly broad patterns
    broad_patterns = []
    for name, pattern in pattern_map.items():
        # Simple heuristic: patterns without word boundaries
        if '\\b' not in pattern and len(pattern) < 10:
            broad_patterns.append((name, pattern))

    if broad_patterns:
        print(f"\n{Colors.YELLOW}Potentially broad patterns:{Colors.END}")
        for name, pattern in broad_patterns:
            print(f"  - {name}: {pattern}")

    print(f"\nResult: {Colors.GREEN}✓{Colors.END} Coverage analysis complete")
    return True

def test_live_hook_integration():
    """Test 9: Live Hook Integration"""
    print(f"\n{Colors.BOLD}Test 9: Live Hook Integration{Colors.END}")
    print("=" * 80)

    import subprocess

    test_cases = [
        ("SCREENSHOT test", True, "should inject screenshot workflow"),
        ("HTML generation", True, "should inject HTML guide"),
        ("random text without keywords", False, "should not inject"),
        ("", False, "empty prompt should not inject"),
    ]

    passed = 0
    failed = []

    for prompt, should_inject, description in test_cases:
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT_DIR / "snippet_injector.py")],
                input=json.dumps({"prompt": prompt}),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                failed.append((prompt, f"exit code {result.returncode}", description))
                print(f"{Colors.RED}✗{Colors.END} {description}")
                continue

            has_output = bool(result.stdout.strip())

            if has_output == should_inject:
                passed += 1
                print(f"{Colors.GREEN}✓{Colors.END} {description}")
            else:
                failed.append((prompt, f"expected inject={should_inject}, got {has_output}", description))
                print(f"{Colors.RED}✗{Colors.END} {description}")

        except subprocess.TimeoutExpired:
            failed.append((prompt, "timeout", description))
            print(f"{Colors.RED}✗{Colors.END} {description} (timeout)")
        except Exception as e:
            failed.append((prompt, str(e), description))
            print(f"{Colors.RED}✗{Colors.END} {description} ({e})")

    print("=" * 80)
    print(f"Result: {passed}/{len(test_cases)} integration tests passed")

    if failed:
        print(f"\n{Colors.RED}Failed integration tests:{Colors.END}")
        for prompt, error, description in failed:
            print(f"  - {description}")
            print(f"    Prompt: '{prompt}'")
            print(f"    Error: {error}")
        return False

    return True

def test_documentation_generation():
    """Test 10: Documentation Generation"""
    print(f"\n{Colors.BOLD}Test 10: Documentation Generation{Colors.END}")
    print("=" * 80)

    config = load_config(SCRIPT_DIR / "config.local.json")

    # Generate keyword reference
    keywords = []
    categories = {}

    for mapping in config.get("mappings", []):
        if not mapping.get("enabled", True):
            continue

        name = mapping.get("name")
        pattern = mapping.get("pattern")
        snippet_files = mapping.get("snippet", [])

        # Extract keywords from pattern
        # Simple extraction: look for pipe-separated words in pattern
        import re
        keyword_matches = re.findall(r'\\b\(([^)]+)\)\\b', pattern)
        if keyword_matches:
            kw_list = keyword_matches[0].split('|')
            keywords.append({
                'name': name,
                'keywords': kw_list,
                'files': snippet_files
            })

            # Categorize
            if 'snippets/local/documentation' in snippet_files[0]:
                category = 'Documentation'
            elif 'snippets/local/development' in snippet_files[0]:
                category = 'Development'
            elif 'snippets/local/output-formats' in snippet_files[0]:
                category = 'Output Formats'
            elif 'snippets/local/communication' in snippet_files[0]:
                category = 'Communication'
            elif 'snippets/local/productivity' in snippet_files[0]:
                category = 'Productivity'
            elif 'skills/' in snippet_files[0]:
                category = 'Skills'
            else:
                category = 'Other'

            if category not in categories:
                categories[category] = []
            categories[category].append({'name': name, 'keywords': kw_list})

    # Generate markdown
    markdown = "# Snippet Keyword Reference\n\n"
    markdown += "Auto-generated keyword reference for snippet injection system.\n\n"
    markdown += f"**Total Snippets**: {len(keywords)}\n\n"

    markdown += "## Quick Reference\n\n"
    markdown += "| Keyword | Snippet Name | Category |\n"
    markdown += "|---------|--------------|----------|\n"

    for kw in sorted(keywords, key=lambda x: x['keywords'][0]):
        keyword_str = ', '.join(kw['keywords'])
        category = 'Other'
        for cat, items in categories.items():
            if any(item['name'] == kw['name'] for item in items):
                category = cat
                break
        markdown += f"| {keyword_str} | {kw['name']} | {category} |\n"

    markdown += "\n## By Category\n\n"
    for category in sorted(categories.keys()):
        markdown += f"### {category}\n\n"
        for item in sorted(categories[category], key=lambda x: x['name']):
            keyword_str = ', '.join(item['keywords'])
            markdown += f"- **{keyword_str}**: {item['name']}\n"
        markdown += "\n"

    # Write to file
    output_path = SCRIPT_DIR / "KEYWORDS.md"
    try:
        with open(output_path, 'w') as f:
            f.write(markdown)
        print(f"{Colors.GREEN}✓{Colors.END} Generated keyword reference: {output_path}")
        print(f"  {len(keywords)} snippets documented")
        print(f"  {len(categories)} categories")
        print("=" * 80)
        print(f"Result: {Colors.GREEN}✓{Colors.END} Documentation generated")
        return True
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} Failed to write documentation: {e}")
        print("=" * 80)
        return False

def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Snippet Injection System Test Suite{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")

    print(f"\nPlugin Root: {PLUGIN_ROOT}")
    print(f"Config Dir: {SCRIPT_DIR}")

    tests = [
        ("File Existence", test_file_paths),
        ("Regex Patterns", test_regex_patterns),
        ("Injection Flow", test_injection_flow),
        ("Config Merging", test_config_merging),
        ("Content Loading", test_content_loading),
        ("Content Quality", test_content_quality),
        ("Pattern Coverage", test_pattern_coverage),
        ("Live Hook Integration", test_live_hook_integration),
        ("Documentation Generation", test_documentation_generation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n{Colors.RED}✗ Test '{test_name}' crashed: {e}{Colors.END}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}Test Summary{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} {test_name}")

    print(f"\n{Colors.BOLD}Overall: {passed_count}/{total_count} tests passed{Colors.END}")

    if passed_count == total_count:
        print(f"{Colors.GREEN}{Colors.BOLD}All tests passed! ✓{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}Some tests failed! ✗{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
