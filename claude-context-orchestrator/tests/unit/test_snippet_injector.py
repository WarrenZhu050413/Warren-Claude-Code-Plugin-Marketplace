#!/usr/bin/env python3
"""
Comprehensive tests for snippet_injector.py

Tests cover:
- Config loading and merging (base + local)
- Pattern matching (regex)
- Snippet injection
- Multi-file snippets with separators
- Error handling and edge cases

Uses subprocess to test the script since it runs on import.
"""

import json
import pytest
import subprocess
import sys
from pathlib import Path


class TestConfigLoading:
    """Test configuration loading and merging"""

    def test_load_base_config_only(self, tmp_path):
        """Test loading when only base config exists"""
        # Create base config
        base_config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        config_path = tmp_path / "config.json"
        with open(config_path, 'w') as f:
            json.dump(base_config, f)

        # Create snippet file
        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "test1.md").write_text("Hello content")

        # Prepare input
        input_data = {"prompt": "hello world"}

        # Run the script
        result = self._run_injector(tmp_path, input_data)

        assert result is not None
        assert "hookSpecificOutput" in result
        assert "Hello content" in result["hookSpecificOutput"]["additionalContext"][0]

    def test_load_local_override(self, tmp_path):
        """Test local config overrides base config"""
        # Create base config
        base_config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        config_path = tmp_path / "config.json"
        with open(config_path, 'w') as f:
            json.dump(base_config, f)

        # Create local config that overrides test1
        local_config = {
            "mappings": [
                {"name": "test1", "pattern": "hi", "snippet": ["snippets/override.md"], "enabled": True}
            ]
        }
        local_path = tmp_path / "config.local.json"
        with open(local_path, 'w') as f:
            json.dump(local_config, f)

        # Create snippet files
        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "test1.md").write_text("Original")
        (snippet_dir / "override.md").write_text("Override content")

        # Test with "hi" (should match override pattern)
        input_data = {"prompt": "hi there"}
        result = self._run_injector(tmp_path, input_data)

        assert result is not None
        assert "Override content" in result["hookSpecificOutput"]["additionalContext"][0]

    def test_load_local_adds_new(self, tmp_path):
        """Test local config can add new snippets"""
        base_config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        config_path = tmp_path / "config.json"
        with open(config_path, 'w') as f:
            json.dump(base_config, f)

        local_config = {
            "mappings": [
                {"name": "test2", "pattern": "goodbye", "snippet": ["snippets/test2.md"], "enabled": True}
            ]
        }
        local_path = tmp_path / "config.local.json"
        with open(local_path, 'w') as f:
            json.dump(local_config, f)

        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "test1.md").write_text("Hello")
        (snippet_dir / "test2.md").write_text("Goodbye")

        # Test that both patterns work
        result1 = self._run_injector(tmp_path, {"prompt": "hello"})
        assert result1 is not None
        assert "Hello" in result1["hookSpecificOutput"]["additionalContext"][0]

        result2 = self._run_injector(tmp_path, {"prompt": "goodbye"})
        assert result2 is not None
        assert "Goodbye" in result2["hookSpecificOutput"]["additionalContext"][0]

    def test_empty_configs(self, tmp_path):
        """Test behavior with empty or missing configs"""
        input_data = {"prompt": "test"}
        result = self._run_injector(tmp_path, input_data)

        # No configs, no output
        assert result is None or result == {}

    def _run_injector(self, plugin_root, input_data):
        """Helper to run snippet_injector.py with given input"""
        script_path = Path(__file__).parent / "snippet_injector.py"

        # Set environment to use test directory as PLUGIN_ROOT
        # We do this by creating a modified version of the script
        test_script = plugin_root / "test_injector.py"

        with open(script_path) as f:
            original_code = f.read()

        # Replace PLUGIN_ROOT calculation
        modified_code = original_code.replace(
            "PLUGIN_ROOT = Path(__file__).parent",
            f"PLUGIN_ROOT = Path('{plugin_root}')"
        )

        with open(test_script, 'w') as f:
            f.write(modified_code)

        # Run the script
        proc = subprocess.run(
            [sys.executable, str(test_script)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True
        )

        # Parse output
        if proc.stdout.strip():
            try:
                return json.loads(proc.stdout)
            except json.JSONDecodeError:
                return None
        return None


class TestPatternMatching:
    """Test regex pattern matching"""

    def test_simple_pattern_match(self, tmp_path):
        """Test simple regex pattern matching"""
        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        self._setup_config(tmp_path, config)

        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "test1.md").write_text("Hello content")

        input_data = {"prompt": "hello world"}
        result = self._run_injector(tmp_path, input_data)

        assert result is not None
        assert "Hello content" in result["hookSpecificOutput"]["additionalContext"][0]

    def test_case_sensitive_matching(self, tmp_path):
        """Test that pattern matching is case-sensitive"""
        config = {
            "mappings": [
                {"name": "test1", "pattern": "Hello", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        self._setup_config(tmp_path, config)

        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "test1.md").write_text("Content")

        # Should NOT match - case differs
        input_data = {"prompt": "hello world"}
        result = self._run_injector(tmp_path, input_data)

        assert result is None or "additionalContext" not in result.get("hookSpecificOutput", {})

    def test_complex_regex_pattern(self, tmp_path):
        """Test complex regex patterns"""
        config = {
            "mappings": [
                {
                    "name": "test1",
                    "pattern": r"(email|mail|send message)",
                    "snippet": ["snippets/test1.md"],
                    "enabled": True
                }
            ]
        }
        self._setup_config(tmp_path, config)

        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "test1.md").write_text("Email snippet")

        # Test multiple triggers
        for prompt in ["send email", "check mail", "send message"]:
            result = self._run_injector(tmp_path, {"prompt": prompt})
            assert result is not None
            assert "Email snippet" in result["hookSpecificOutput"]["additionalContext"][0]

    def test_disabled_snippet_not_matched(self, tmp_path):
        """Test that disabled snippets are not injected"""
        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": False}
            ]
        }
        self._setup_config(tmp_path, config)

        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "test1.md").write_text("Content")

        input_data = {"prompt": "hello world"}
        result = self._run_injector(tmp_path, input_data)

        assert result is None or "additionalContext" not in result.get("hookSpecificOutput", {})

    def _setup_config(self, tmp_path, config):
        """Helper to set up config file"""
        config_path = tmp_path / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f)

    def _run_injector(self, plugin_root, input_data):
        """Helper to run snippet_injector.py with given input"""
        script_path = Path(__file__).parent / "snippet_injector.py"
        test_script = plugin_root / "test_injector.py"

        with open(script_path) as f:
            original_code = f.read()

        modified_code = original_code.replace(
            "PLUGIN_ROOT = Path(__file__).parent",
            f"PLUGIN_ROOT = Path('{plugin_root}')"
        )

        with open(test_script, 'w') as f:
            f.write(modified_code)

        proc = subprocess.run(
            [sys.executable, str(test_script)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True
        )

        if proc.stdout.strip():
            try:
                return json.loads(proc.stdout)
            except json.JSONDecodeError:
                return None
        return None


class TestMultiFileSnippets:
    """Test multi-file snippet handling"""

    def test_multi_file_with_default_separator(self, tmp_path):
        """Test loading multiple files with default newline separator"""
        config = {
            "mappings": [
                {
                    "name": "test1",
                    "pattern": "multi",
                    "snippet": ["snippets/part1.md", "snippets/part2.md"],
                    "enabled": True
                }
            ]
        }
        self._setup_config(tmp_path, config)

        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "part1.md").write_text("Part 1")
        (snippet_dir / "part2.md").write_text("Part 2")

        input_data = {"prompt": "multi file test"}
        result = self._run_injector(tmp_path, input_data)

        assert result is not None
        content = result["hookSpecificOutput"]["additionalContext"][0]
        assert content == "Part 1\nPart 2"

    def test_multi_file_with_custom_separator(self, tmp_path):
        """Test loading multiple files with custom separator"""
        config = {
            "mappings": [
                {
                    "name": "test1",
                    "pattern": "multi",
                    "snippet": ["snippets/part1.md", "snippets/part2.md"],
                    "separator": "\n---\n",
                    "enabled": True
                }
            ]
        }
        self._setup_config(tmp_path, config)

        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "part1.md").write_text("Part 1")
        (snippet_dir / "part2.md").write_text("Part 2")

        input_data = {"prompt": "multi file test"}
        result = self._run_injector(tmp_path, input_data)

        assert result is not None
        content = result["hookSpecificOutput"]["additionalContext"][0]
        assert content == "Part 1\n---\nPart 2"

    def test_missing_file_skipped(self, tmp_path):
        """Test that missing files are skipped gracefully"""
        config = {
            "mappings": [
                {
                    "name": "test1",
                    "pattern": "multi",
                    "snippet": ["snippets/exists.md", "snippets/missing.md"],
                    "enabled": True
                }
            ]
        }
        self._setup_config(tmp_path, config)

        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "exists.md").write_text("Exists")

        input_data = {"prompt": "multi file test"}
        result = self._run_injector(tmp_path, input_data)

        assert result is not None
        content = result["hookSpecificOutput"]["additionalContext"][0]
        assert content == "Exists"

    def _setup_config(self, tmp_path, config):
        """Helper to set up config file"""
        config_path = tmp_path / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f)

    def _run_injector(self, plugin_root, input_data):
        """Helper to run snippet_injector.py with given input"""
        script_path = Path(__file__).parent / "snippet_injector.py"
        test_script = plugin_root / "test_injector.py"

        with open(script_path) as f:
            original_code = f.read()

        modified_code = original_code.replace(
            "PLUGIN_ROOT = Path(__file__).parent",
            f"PLUGIN_ROOT = Path('{plugin_root}')"
        )

        with open(test_script, 'w') as f:
            f.write(modified_code)

        proc = subprocess.run(
            [sys.executable, str(test_script)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True
        )

        if proc.stdout.strip():
            try:
                return json.loads(proc.stdout)
            except json.JSONDecodeError:
                return None
        return None


class TestMultipleMatches:
    """Test handling of multiple pattern matches"""

    def test_multiple_snippets_matched(self, tmp_path):
        """Test when multiple patterns match the prompt"""
        config = {
            "mappings": [
                {"name": "test1", "pattern": "email", "snippet": ["snippets/email.md"], "enabled": True},
                {"name": "test2", "pattern": "urgent", "snippet": ["snippets/urgent.md"], "enabled": True}
            ]
        }
        self._setup_config(tmp_path, config)

        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "email.md").write_text("Email snippet")
        (snippet_dir / "urgent.md").write_text("Urgent snippet")

        input_data = {"prompt": "send urgent email"}
        result = self._run_injector(tmp_path, input_data)

        assert result is not None
        contexts = result["hookSpecificOutput"]["additionalContext"]
        assert len(contexts) == 2

    def test_duplicate_matches_removed(self, tmp_path):
        """Test that duplicate matches are removed"""
        config = {
            "mappings": [
                {"name": "test1", "pattern": "email", "snippet": ["snippets/email.md"], "enabled": True},
                {"name": "test2", "pattern": "email", "snippet": ["snippets/email.md"], "enabled": True}
            ]
        }
        self._setup_config(tmp_path, config)

        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "email.md").write_text("Email snippet")

        input_data = {"prompt": "send email"}
        result = self._run_injector(tmp_path, input_data)

        assert result is not None
        contexts = result["hookSpecificOutput"]["additionalContext"]
        # Duplicates should be removed
        assert len(contexts) == 1

    def _setup_config(self, tmp_path, config):
        """Helper to set up config file"""
        config_path = tmp_path / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f)

    def _run_injector(self, plugin_root, input_data):
        """Helper to run snippet_injector.py with given input"""
        script_path = Path(__file__).parent / "snippet_injector.py"
        test_script = plugin_root / "test_injector.py"

        with open(script_path) as f:
            original_code = f.read()

        modified_code = original_code.replace(
            "PLUGIN_ROOT = Path(__file__).parent",
            f"PLUGIN_ROOT = Path('{plugin_root}')"
        )

        with open(test_script, 'w') as f:
            f.write(modified_code)

        proc = subprocess.run(
            [sys.executable, str(test_script)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True
        )

        if proc.stdout.strip():
            try:
                return json.loads(proc.stdout)
            except json.JSONDecodeError:
                return None
        return None


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_malformed_json_input(self, tmp_path):
        """Test handling of malformed JSON input"""
        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        self._setup_config(tmp_path, config)

        # Run with invalid JSON
        script_path = Path(__file__).parent / "snippet_injector.py"
        test_script = tmp_path / "test_injector.py"

        with open(script_path) as f:
            original_code = f.read()

        modified_code = original_code.replace(
            "PLUGIN_ROOT = Path(__file__).parent",
            f"PLUGIN_ROOT = Path('{tmp_path}')"
        )

        with open(test_script, 'w') as f:
            f.write(modified_code)

        proc = subprocess.run(
            [sys.executable, str(test_script)],
            input="not valid json",
            capture_output=True,
            text=True
        )

        # Should exit with code 0 (graceful exit)
        assert proc.returncode == 0
        assert proc.stdout.strip() == ""

    def test_missing_prompt_field(self, tmp_path):
        """Test when prompt field is missing from input"""
        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        self._setup_config(tmp_path, config)

        input_data = {"other_field": "value"}
        result = self._run_injector(tmp_path, input_data)

        # Missing prompt should be handled gracefully (no matches)
        assert result is None or "additionalContext" not in result.get("hookSpecificOutput", {})

    def test_empty_prompt(self, tmp_path):
        """Test with empty prompt"""
        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        self._setup_config(tmp_path, config)

        input_data = {"prompt": ""}
        result = self._run_injector(tmp_path, input_data)

        # Empty prompt shouldn't match anything
        assert result is None or "additionalContext" not in result.get("hookSpecificOutput", {})

    def test_no_matches(self, tmp_path):
        """Test when no patterns match"""
        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        self._setup_config(tmp_path, config)

        input_data = {"prompt": "goodbye world"}
        result = self._run_injector(tmp_path, input_data)

        # No matches, no output
        assert result is None or "additionalContext" not in result.get("hookSpecificOutput", {})

    def _setup_config(self, tmp_path, config):
        """Helper to set up config file"""
        config_path = tmp_path / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f)

    def _run_injector(self, plugin_root, input_data):
        """Helper to run snippet_injector.py with given input"""
        script_path = Path(__file__).parent / "snippet_injector.py"
        test_script = plugin_root / "test_injector.py"

        with open(script_path) as f:
            original_code = f.read()

        modified_code = original_code.replace(
            "PLUGIN_ROOT = Path(__file__).parent",
            f"PLUGIN_ROOT = Path('{plugin_root}')"
        )

        with open(test_script, 'w') as f:
            f.write(modified_code)

        proc = subprocess.run(
            [sys.executable, str(test_script)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True
        )

        if proc.stdout.strip():
            try:
                return json.loads(proc.stdout)
            except json.JSONDecodeError:
                return None
        return None


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_config(self, tmp_path):
        """Test with completely empty config"""
        config = {"mappings": []}
        self._setup_config(tmp_path, config)

        input_data = {"prompt": "anything"}
        result = self._run_injector(tmp_path, input_data)

        # No mappings, no output
        assert result is None or "additionalContext" not in result.get("hookSpecificOutput", {})

    def test_pattern_with_special_regex_chars(self, tmp_path):
        """Test patterns with special regex characters"""
        config = {
            "mappings": [
                {"name": "test1", "pattern": r"\btest\b", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        self._setup_config(tmp_path, config)

        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "test1.md").write_text("Test content")

        # Should match whole word "test"
        result = self._run_injector(tmp_path, {"prompt": "run test now"})
        assert result is not None
        assert "Test content" in result["hookSpecificOutput"]["additionalContext"][0]

        # Should NOT match partial word
        result2 = self._run_injector(tmp_path, {"prompt": "testing now"})
        assert result2 is None or "additionalContext" not in result2.get("hookSpecificOutput", {})

    def test_unicode_content(self, tmp_path):
        """Test handling of Unicode content in snippets"""
        config = {
            "mappings": [
                {"name": "test1", "pattern": "emoji", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        self._setup_config(tmp_path, config)

        snippet_dir = tmp_path / "snippets"
        snippet_dir.mkdir()
        (snippet_dir / "test1.md").write_text("Hello 👋 世界 🌍")

        input_data = {"prompt": "emoji test"}
        result = self._run_injector(tmp_path, input_data)

        assert result is not None
        content = result["hookSpecificOutput"]["additionalContext"][0]
        assert "👋" in content
        assert "世界" in content
        assert "🌍" in content

    def _setup_config(self, tmp_path, config):
        """Helper to set up config file"""
        config_path = tmp_path / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f)

    def _run_injector(self, plugin_root, input_data):
        """Helper to run snippet_injector.py with given input"""
        script_path = Path(__file__).parent / "snippet_injector.py"
        test_script = plugin_root / "test_injector.py"

        with open(script_path) as f:
            original_code = f.read()

        modified_code = original_code.replace(
            "PLUGIN_ROOT = Path(__file__).parent",
            f"PLUGIN_ROOT = Path('{plugin_root}')"
        )

        with open(test_script, 'w') as f:
            f.write(modified_code)

        proc = subprocess.run(
            [sys.executable, str(test_script)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True
        )

        if proc.stdout.strip():
            try:
                return json.loads(proc.stdout)
            except json.JSONDecodeError:
                return None
        return None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
