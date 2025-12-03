#!/usr/bin/env python3
"""
Comprehensive CLI integration tests for snippets_cli.py

Tests the main() function including:
- Argument parsing
- Command routing
- Error handling at CLI level
- Output formatting
- Exit codes

These tests run the CLI as a subprocess to test the full integration.
"""

import json
import pytest
import subprocess
import sys
from pathlib import Path


class TestCLICreate:
    """Test CLI create command"""

    def test_create_with_inline_content(self, tmp_path):
        """Test create command with --content"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        # Initialize empty config
        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test snippet",
            "--content", "Test content"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["success"] is True
        assert output["operation"] == "create"
        assert output["data"]["name"] == "test1"

        # Verify file was created
        assert (snippets_dir / "test1.md").exists()

    def test_create_with_file(self, tmp_path):
        """Test create command with --file"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        source_file = tmp_path / "source.md"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        source_file.write_text("Source content")

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test snippet",
            "--file", str(source_file)
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["success"] is True

        # Verify content from file
        snippet_content = (snippets_dir / "test1.md").read_text()
        assert "Source content" in snippet_content

    def test_create_with_force_flag(self, tmp_path):
        """Test create command with --force to overwrite"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        # Create first snippet
        self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test",
            "--content", "Original"
        ])

        # Overwrite with --force
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "goodbye",
            "--description", "Test",
            "--content", "Updated",
            "--force"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["data"]["pattern"] == "goodbye"

    def test_create_without_content_fails(self, tmp_path):
        """Test create command fails without content/file"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test"
        ])

        assert result.returncode == 1
        output = json.loads(result.stderr)
        assert output["success"] is False
        assert output["error"]["code"] == "INVALID_INPUT"

    def test_create_duplicate_without_force_fails(self, tmp_path):
        """Test create fails for duplicate without --force"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        # Create first snippet
        self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test",
            "--content", "Content"
        ])

        # Try to create duplicate
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test",
            "--content", "Content"
        ])

        assert result.returncode == 1
        output = json.loads(result.stderr)
        assert output["error"]["code"] == "DUPLICATE_NAME"

    def test_create_with_invalid_regex(self, tmp_path):
        """Test create fails with invalid regex pattern"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "(unclosed",
            "--description", "Test",
            "--content", "Content"
        ])

        assert result.returncode == 1
        output = json.loads(result.stderr)
        assert output["error"]["code"] == "INVALID_REGEX"

    def test_create_with_use_base_config_flag(self, tmp_path):
        """Test create saves to base config with --use-base-config"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "--use-base-config",
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test",
            "--content", "Content"
        ])

        assert result.returncode == 0

        # Verify saved to base config, not local
        with open(config_path) as f:
            config = json.load(f)
        assert len(config["mappings"]) == 1
        assert config["mappings"][0]["name"] == "test1"

        # Local config should not exist
        local_config = tmp_path / "config.local.json"
        assert not local_config.exists()

    def _run_cli(self, args):
        """Helper to run CLI with arguments"""
        script_path = Path(__file__).parent / "snippets_cli.py"
        cmd = [sys.executable, str(script_path)] + args
        return subprocess.run(cmd, capture_output=True, text=True)


class TestCLIList:
    """Test CLI list command"""

    def test_list_empty(self, tmp_path):
        """Test list command with no snippets"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "list"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["success"] is True
        assert output["data"]["snippets"] == []

    def test_list_all_snippets(self, tmp_path):
        """Test list command shows all snippets"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True},
                {"name": "test2", "pattern": "world", "snippet": ["snippets/test2.md"], "enabled": False}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        (snippets_dir / "test1.md").write_text("Content 1")
        (snippets_dir / "test2.md").write_text("Content 2")

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "list"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert len(output["data"]["snippets"]) == 2

    def test_list_specific_snippet(self, tmp_path):
        """Test list command with specific name"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True},
                {"name": "test2", "pattern": "world", "snippet": ["snippets/test2.md"], "enabled": True}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        (snippets_dir / "test1.md").write_text("Content 1")
        (snippets_dir / "test2.md").write_text("Content 2")

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "list", "test1"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert len(output["data"]["snippets"]) == 1
        assert output["data"]["snippets"][0]["name"] == "test1"

    def test_list_with_stats(self, tmp_path):
        """Test list command with --show-stats"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True},
                {"name": "test2", "pattern": "world", "snippet": ["snippets/test2.md"], "enabled": False}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        (snippets_dir / "test1.md").write_text("Content 1")
        (snippets_dir / "test2.md").write_text("Content 2")

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "list", "--show-stats"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "total" in output["data"]
        assert output["data"]["total"] == 2
        assert output["data"]["enabled"] == 1
        assert output["data"]["disabled"] == 1

    def test_list_with_content(self, tmp_path):
        """Test list command with --show-content"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"], "enabled": True}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        (snippets_dir / "test1.md").write_text("Test content here")

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "list", "--show-content"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "content" in output["data"]["snippets"][0]
        assert "Test content here" in output["data"]["snippets"][0]["content"]

    def _run_cli(self, args):
        """Helper to run CLI with arguments"""
        script_path = Path(__file__).parent / "snippets_cli.py"
        cmd = [sys.executable, str(script_path)] + args
        return subprocess.run(cmd, capture_output=True, text=True)


class TestCLIUpdate:
    """Test CLI update command"""

    def test_update_pattern(self, tmp_path):
        """Test update command changing pattern"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        # Create initial snippet
        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test",
            "--content", "Content"
        ])

        # Update pattern
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "update", "test1",
            "--pattern", "goodbye"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "pattern" in output["data"]["changes"]
        assert output["data"]["changes"]["pattern"]["new"] == "goodbye"

    def test_update_content(self, tmp_path):
        """Test update command changing content"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test",
            "--content", "Original"
        ])

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "update", "test1",
            "--content", "Updated"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "content" in output["data"]["changes"]

    def test_update_rename(self, tmp_path):
        """Test update command renaming snippet"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test",
            "--content", "Content"
        ])

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "update", "test1",
            "--rename", "test2"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["data"]["name"] == "test2"
        assert "name" in output["data"]["changes"]

    def test_update_nonexistent_fails(self, tmp_path):
        """Test update fails for nonexistent snippet"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "update", "nonexistent",
            "--pattern", "test"
        ])

        assert result.returncode == 1
        output = json.loads(result.stderr)
        assert output["error"]["code"] == "NOT_FOUND"

    def _run_cli(self, args):
        """Helper to run CLI with arguments"""
        script_path = Path(__file__).parent / "snippets_cli.py"
        cmd = [sys.executable, str(script_path)] + args
        return subprocess.run(cmd, capture_output=True, text=True)


class TestCLIDelete:
    """Test CLI delete command"""

    def test_delete_snippet(self, tmp_path):
        """Test delete command"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        # Create snippet
        self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test",
            "--content", "Content"
        ])

        # Delete it
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "delete", "test1",
            "--force"  # Skip confirmation
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["success"] is True
        assert output["data"]["config_updated"] is True

    def test_delete_nonexistent_fails(self, tmp_path):
        """Test delete fails for nonexistent snippet"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "delete", "nonexistent",
            "--force"
        ])

        assert result.returncode == 1
        output = json.loads(result.stderr)
        assert output["error"]["code"] == "NOT_FOUND"

    def _run_cli(self, args):
        """Helper to run CLI with arguments"""
        script_path = Path(__file__).parent / "snippets_cli.py"
        cmd = [sys.executable, str(script_path)] + args
        return subprocess.run(cmd, capture_output=True, text=True)


class TestCLIValidate:
    """Test CLI validate command"""

    def test_validate_valid_config(self, tmp_path):
        """Test validate with valid configuration"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"]}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        (snippets_dir / "test1.md").write_text("Content")

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "validate"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["data"]["config_valid"] is True
        assert len(output["data"]["issues"]) == 0

    def test_validate_missing_file(self, tmp_path):
        """Test validate detects missing files"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"]}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        # Don't create the file

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "validate"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["data"]["config_valid"] is False
        assert len(output["data"]["issues"]) > 0

    def test_validate_invalid_regex(self, tmp_path):
        """Test validate detects invalid regex"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        config = {
            "mappings": [
                {"name": "test1", "pattern": "(unclosed", "snippet": ["snippets/test1.md"]}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        (snippets_dir / "test1.md").write_text("Content")

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "validate"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["data"]["config_valid"] is False

    def _run_cli(self, args):
        """Helper to run CLI with arguments"""
        script_path = Path(__file__).parent / "snippets_cli.py"
        cmd = [sys.executable, str(script_path)] + args
        return subprocess.run(cmd, capture_output=True, text=True)


class TestCLITest:
    """Test CLI test command for pattern matching"""

    def test_pattern_match(self, tmp_path):
        """Test test command with matching pattern"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        # Create snippet
        self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test",
            "--content", "Content"
        ])

        # Test matching text
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "test", "test1", "hello world"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["data"]["matched"] is True
        assert output["data"]["match_count"] > 0

    def test_pattern_no_match(self, tmp_path):
        """Test test command with non-matching text"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test",
            "--content", "Content"
        ])

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "test", "test1", "goodbye world"
        ])

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["data"]["matched"] is False
        assert output["data"]["match_count"] == 0

    def _run_cli(self, args):
        """Helper to run CLI with arguments"""
        script_path = Path(__file__).parent / "snippets_cli.py"
        cmd = [sys.executable, str(script_path)] + args
        return subprocess.run(cmd, capture_output=True, text=True)


class TestCLIOutputFormats:
    """Test CLI output formatting"""

    def test_json_format(self, tmp_path):
        """Test --format json"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "--format", "json",
            "list"
        ])

        assert result.returncode == 0
        # Should be valid JSON
        output = json.loads(result.stdout)
        assert "success" in output

    def test_text_format(self, tmp_path):
        """Test --format text"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "--format", "text",
            "list"
        ])

        assert result.returncode == 0
        # Should contain success marker
        assert "✓" in result.stdout

    def _run_cli(self, args):
        """Helper to run CLI with arguments"""
        script_path = Path(__file__).parent / "snippets_cli.py"
        cmd = [sys.executable, str(script_path)] + args
        return subprocess.run(cmd, capture_output=True, text=True)


class TestCLIErrorHandling:
    """Test CLI error handling"""

    def test_missing_required_argument(self, tmp_path):
        """Test CLI fails with missing required argument"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        # Create without --pattern (required)
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--description", "Test",
            "--content", "Content"
        ])

        # Should fail due to missing --pattern
        assert result.returncode != 0

    def test_malformed_config_file(self, tmp_path):
        """Test CLI handles malformed config gracefully"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        # Write invalid JSON
        with open(config_path, 'w') as f:
            f.write("not valid json")

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "list"
        ])

        assert result.returncode == 1
        # Should have error in stderr
        output = json.loads(result.stderr)
        assert output["error"]["code"] == "CONFIG_ERROR"

    def test_unknown_command(self, tmp_path):
        """Test CLI rejects unknown commands"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "unknown_command"
        ])

        # Should fail - argparse will exit with code 2
        assert result.returncode == 2

    def _run_cli(self, args):
        """Helper to run CLI with arguments"""
        script_path = Path(__file__).parent / "snippets_cli.py"
        cmd = [sys.executable, str(script_path)] + args
        return subprocess.run(cmd, capture_output=True, text=True)


class TestCLIWorkflows:
    """Test complete CLI workflows"""

    def test_full_crud_workflow(self, tmp_path):
        """Test complete create → list → update → delete workflow"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"

        with open(config_path, 'w') as f:
            json.dump({"mappings": []}, f)

        # Create
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "create", "test1",
            "--pattern", "hello",
            "--description", "Test",
            "--content", "Original"
        ])
        assert result.returncode == 0

        # List
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "list"
        ])
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert len(output["data"]["snippets"]) == 1

        # Update
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "update", "test1",
            "--content", "Updated"
        ])
        assert result.returncode == 0

        # Delete
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "delete", "test1",
            "--force"
        ])
        assert result.returncode == 0

        # Verify deleted
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "list"
        ])
        output = json.loads(result.stdout)
        assert len(output["data"]["snippets"]) == 0

    def test_validate_then_fix_workflow(self, tmp_path):
        """Test validate → fix → validate workflow"""
        config_path = tmp_path / "config.json"
        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()

        # Create config with missing file
        config = {
            "mappings": [
                {"name": "test1", "pattern": "hello", "snippet": ["snippets/test1.md"]}
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

        # Validate - should fail
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "validate"
        ])
        output = json.loads(result.stdout)
        assert output["data"]["config_valid"] is False

        # Fix by creating file
        (snippets_dir / "test1.md").write_text("Content")

        # Validate again - should pass
        result = self._run_cli([
            "--config", str(config_path),
            "--snippets-dir", str(snippets_dir),
            "validate"
        ])
        output = json.loads(result.stdout)
        assert output["data"]["config_valid"] is True

    def _run_cli(self, args):
        """Helper to run CLI with arguments"""
        script_path = Path(__file__).parent / "snippets_cli.py"
        cmd = [sys.executable, str(script_path)] + args
        return subprocess.run(cmd, capture_output=True, text=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
