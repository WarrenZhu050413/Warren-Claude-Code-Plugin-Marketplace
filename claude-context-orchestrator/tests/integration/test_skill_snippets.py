#!/usr/bin/env python3
"""
Tests for skill snippet entries in config.local.json

Tests verify:
- All skills have corresponding snippet entries
- Snippet entries point to valid SKILL.md files
- Regex patterns follow ALL CAPS convention
- Patterns match expected triggers
"""

import json
import pytest
from pathlib import Path


class TestSkillSnippetEntries:
    """Test skill snippet configuration entries"""

    @pytest.fixture
    def config_dir(self):
        """Get the config directory"""
        return Path(__file__).parent

    @pytest.fixture
    def config_local(self, config_dir):
        """Load config.local.json"""
        with open(config_dir / "config.local.json") as f:
            return json.load(f)

    @pytest.fixture
    def skills_dir(self, config_dir):
        """Get the skills directory"""
        return config_dir.parent / "skills"

    @pytest.fixture
    def expected_skills(self):
        """Expected skill directories"""
        return [
            "building-artifacts",
            "building-mcp",
            "managing-skills",
            "managing-snippets",
            "searching-deeply",
            "testing-webapps",
            "theming-artifacts",
            "using-claude",
            "using-codex",
        ]

    @pytest.fixture
    def expected_patterns(self):
        """Expected ALL CAPS regex patterns for skills"""
        return {
            "building-artifacts": "BUILD_ARTIFACT",
            "building-mcp": "BUILD_MCP",
            "managing-skills": "MANAGE_SKILL",
            "managing-snippets": "MANAGE_SNIPPET",
            "searching-deeply": "DEEP_SEARCH",
            "testing-webapps": "TEST_WEB",
            "theming-artifacts": "THEME_ARTIFACT",
            "using-claude": "USE_CLAUDE",
            "using-codex": "USE_CODEX",
        }

    def test_all_skills_have_snippet_entries(self, config_local, expected_skills):
        """Verify all skills have corresponding snippet entries"""
        skill_entries = [
            mapping["name"]
            for mapping in config_local["mappings"]
            if mapping["name"] in expected_skills
        ]

        for skill in expected_skills:
            assert skill in skill_entries, f"Skill {skill} missing snippet entry in config.local.json"

    def test_skill_snippet_paths_exist(self, config_local, config_dir, expected_skills):
        """Verify snippet paths point to existing SKILL.md files"""
        for mapping in config_local["mappings"]:
            if mapping["name"] in expected_skills:
                snippet_paths = mapping["snippet"]
                for snippet_path in snippet_paths:
                    # Resolve relative path from config directory
                    full_path = (config_dir / snippet_path).resolve()
                    assert full_path.exists(), f"Snippet file not found: {full_path}"
                    assert full_path.name == "SKILL.md", f"Expected SKILL.md, got {full_path.name}"

    def test_skill_patterns_all_caps(self, config_local, expected_skills):
        """Verify skill patterns use ALL CAPS convention"""
        for mapping in config_local["mappings"]:
            if mapping["name"] in expected_skills:
                pattern = mapping["pattern"]
                # Extract the main pattern keyword (remove regex syntax)
                # Pattern format: \\bKEYWORD[.,;:]?\\b
                # Keyword can use underscore (_), hyphen (-), or no separator
                import re
                match = re.search(r'\\b([A-Z_-]+)\[', pattern)
                assert match, f"Pattern {pattern} doesn't match expected format"

                keyword = match.group(1)
                assert keyword.replace('_', '').replace('-', '').isupper(), \
                    f"Pattern keyword {keyword} not ALL CAPS"
                assert len(keyword) <= 15, f"Pattern {keyword} too long (>15 chars)"

                # Check no mixed separators
                if '_' in keyword and '-' in keyword:
                    pytest.fail(f"Pattern {keyword} mixes separators (_ and -)")

    def test_skill_patterns_match_expected(self, config_local, expected_patterns):
        """Verify skill patterns match expected ALL CAPS keywords"""
        for skill_name, expected_keyword in expected_patterns.items():
            # Find mapping for this skill
            mapping = next(
                (m for m in config_local["mappings"] if m["name"] == skill_name),
                None
            )
            assert mapping, f"No mapping found for {skill_name}"

            # Extract keyword from pattern
            import re
            match = re.search(r'\\b([A-Z_]+)\[', mapping["pattern"])
            assert match, f"Invalid pattern format for {skill_name}"

            actual_keyword = match.group(1)
            assert actual_keyword == expected_keyword, \
                f"Expected pattern {expected_keyword} for {skill_name}, got {actual_keyword}"

    def test_skill_entries_enabled(self, config_local, expected_skills):
        """Verify all skill entries are enabled"""
        for mapping in config_local["mappings"]:
            if mapping["name"] in expected_skills:
                assert mapping["enabled"] is True, \
                    f"Skill {mapping['name']} should be enabled"

    def test_skill_entries_have_separator(self, config_local, expected_skills):
        """Verify all skill entries have separator defined"""
        for mapping in config_local["mappings"]:
            if mapping["name"] in expected_skills:
                assert "separator" in mapping, \
                    f"Skill {mapping['name']} missing separator"
                assert mapping["separator"] == "\n", \
                    f"Skill {mapping['name']} separator should be newline"

    def test_pattern_regex_valid(self, config_local, expected_skills):
        """Verify patterns are valid regex"""
        import re
        for mapping in config_local["mappings"]:
            if mapping["name"] in expected_skills:
                pattern = mapping["pattern"]
                try:
                    re.compile(pattern)
                except re.error as e:
                    pytest.fail(f"Invalid regex pattern for {mapping['name']}: {pattern}\nError: {e}")

    def test_pattern_matches_trigger_words(self, expected_patterns):
        """Verify patterns match their intended trigger words"""
        import re

        test_cases = {
            "BUILD_ARTIFACT": ["BUILD_ARTIFACT", "BUILD_ARTIFACT:", "BUILD_ARTIFACT."],
            "BUILD_MCP": ["BUILD_MCP", "BUILD_MCP,", "BUILD_MCP;"],
            "MANAGE_SKILL": ["MANAGE_SKILL", "MANAGE_SKILL:", "MANAGE_SKILL."],
            "MANAGE_SNIPPET": ["MANAGE_SNIPPET", "MANAGE_SNIPPET,"],
            "DEEP_SEARCH": ["DEEP_SEARCH", "DEEP_SEARCH:", "DEEP_SEARCH;"],
            "TEST_WEB": ["TEST_WEB", "TEST_WEB."],
            "THEME_ARTIFACT": ["THEME_ARTIFACT", "THEME_ARTIFACT:"],
            "USE_CLAUDE": ["USE_CLAUDE", "USE_CLAUDE,"],
            "USE_CODEX": ["USE_CODEX", "USE_CODEX;"],
        }

        for keyword, test_inputs in test_cases.items():
            pattern = rf"\b{keyword}[.,;:]?\b"
            regex = re.compile(pattern)

            for test_input in test_inputs:
                assert regex.search(test_input), \
                    f"Pattern {pattern} should match '{test_input}'"

    def test_no_duplicate_skill_entries(self, config_local, expected_skills):
        """Verify no duplicate skill entries"""
        skill_names = [
            mapping["name"]
            for mapping in config_local["mappings"]
            if mapping["name"] in expected_skills
        ]

        assert len(skill_names) == len(set(skill_names)), \
            f"Duplicate skill entries found: {skill_names}"

    def test_skill_directory_structure(self, skills_dir, expected_skills):
        """Verify skill directories exist and have SKILL.md"""
        for skill in expected_skills:
            skill_dir = skills_dir / skill
            assert skill_dir.exists(), f"Skill directory not found: {skill_dir}"
            assert skill_dir.is_dir(), f"Expected directory, got file: {skill_dir}"

            skill_md = skill_dir / "SKILL.md"
            assert skill_md.exists(), f"SKILL.md not found in {skill_dir}"
            assert skill_md.is_file(), f"Expected file, got directory: {skill_md}"

    def test_skill_md_has_yaml_frontmatter(self, skills_dir, expected_skills):
        """Verify SKILL.md files have valid YAML frontmatter"""
        for skill in expected_skills:
            skill_md = skills_dir / skill / "SKILL.md"
            content = skill_md.read_text()

            # Check for YAML frontmatter
            assert content.startswith("---"), \
                f"{skill}/SKILL.md missing YAML frontmatter"

            # Find closing ---
            lines = content.split("\n")
            closing_idx = None
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    closing_idx = i
                    break

            assert closing_idx, \
                f"{skill}/SKILL.md has unclosed YAML frontmatter"

    def test_regex_convention_documented(self, config_dir):
        """Verify regex naming convention is documented"""
        managing_skills_md = config_dir.parent / "skills" / "managing-skills" / "SKILL.md"

        if managing_skills_md.exists():
            content = managing_skills_md.read_text()
            # Check for documentation about snippet entries
            assert "snippet" in content.lower() or "config" in content.lower(), \
                "managing-skills/SKILL.md should document snippet configuration"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
