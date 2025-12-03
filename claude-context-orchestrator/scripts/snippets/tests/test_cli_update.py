"""Tests for snippets update command with search integration."""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from typer.testing import CliRunner

from snippets.cli import app
from snippets.client import SnippetsClient

runner = CliRunner()


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory with test configs."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Create snippets directory
    snippets_dir = tmp_path / "snippets" / "local"
    snippets_dir.mkdir(parents=True)

    # Create test snippets
    test_snippets = [
        {"name": "mail", "pattern": r"\b(MAIL|EMAIL)\b[.,;:!?]?"},
        {"name": "gmail", "pattern": r"\b(GMAIL)\b[.,;:!?]?"},
        {"name": "calendar", "pattern": r"\b(GCAL|CALENDAR)\b[.,;:!?]?"},
    ]

    mappings = []
    for snippet in test_snippets:
        # Create snippet file
        snippet_path = snippets_dir / f"{snippet['name']}.md"
        snippet_path.write_text(f"# {snippet['name']}\nTest content")

        mappings.append({
            "name": snippet["name"],
            "pattern": snippet["pattern"],
            "snippet": [str(snippet_path)],
            "priority": 0
        })

    # Create base config
    base_config = {"mappings": mappings}
    config_path = config_dir / "config.json"
    with open(config_path, 'w') as f:
        json.dump(base_config, f)

    # Create empty local config to avoid issues
    local_config_path = config_dir / "config.local.json"
    with open(local_config_path, 'w') as f:
        json.dump({"mappings": []}, f)

    return {
        "config_dir": config_dir,
        "config_path": config_path,
        "snippets_dir": snippets_dir,
    }


# =============================================================================
# RED PHASE - TESTS THAT SHOULD FAIL INITIALLY
# =============================================================================

def test_update_exact_match_proceeds_directly(temp_config_dir):
    """Test: Exact match name should proceed directly to update without search.

    Given: A snippet named 'mail' exists
    When: User runs 'snippets update mail -p'
    Then: The command should find the exact match and proceed to update
    """
    # This test should FAIL initially because we haven't implemented search yet
    with patch('subprocess.run') as mock_subprocess, \
         patch('tempfile.NamedTemporaryFile') as mock_tempfile, \
         patch('builtins.open', create=True) as mock_open:

        # Setup mocks
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test.txt'
        mock_tempfile.return_value.__enter__.return_value = mock_temp

        # Mock file read to return modified pattern
        mock_file = MagicMock()
        mock_file.read.return_value = r'\b(MAIL|EMAIL|NEWKEYWORD)\b[.,;:!?]?'
        mock_open.return_value.__enter__.return_value = mock_file

        result = runner.invoke(app, [
            'update', 'mail',
            '-p',
            '--force',
            '--config', str(temp_config_dir['config_path']),
            '--snippets-dir', str(temp_config_dir['snippets_dir'])
        ])

        # Should succeed without showing search results
        if result.exit_code != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
        assert result.exit_code == 0
        assert 'Updated snippet: mail' in result.stdout


def test_update_single_fuzzy_match_auto_proceeds(temp_config_dir):
    """Test: Single fuzzy match should auto-select and proceed to update.

    Given: A snippet named 'gmail' exists and 'mail' exists
    When: User runs 'snippets update gma -p' (partial match to 'gmail' only)
    Then: Should automatically use 'gmail' without prompting
    """
    # This test should FAIL initially
    with patch('subprocess.run') as mock_subprocess, \
         patch('tempfile.NamedTemporaryFile') as mock_tempfile, \
         patch('builtins.open', create=True) as mock_open:

        # Setup mocks
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test.txt'
        mock_tempfile.return_value.__enter__.return_value = mock_temp

        mock_file = MagicMock()
        mock_file.read.return_value = r'\b(GMAIL|NEWPATTERN)\b[.,;:!?]?'
        mock_open.return_value.__enter__.return_value = mock_file

        result = runner.invoke(app, [
            'update', 'gma',  # Partial match
            '-p',
            '--force',
            '--config', str(temp_config_dir['config_path']),
            '--snippets-dir', str(temp_config_dir['snippets_dir'])
        ])

        # Should succeed and auto-select 'gmail'
        assert result.exit_code == 0
        assert 'gmail' in result.stdout.lower()


def test_update_multiple_fuzzy_matches_show_selection(temp_config_dir):
    """Test: Multiple fuzzy matches should show interactive selection.

    Given: Snippets 'mail' and 'gmail' exist
    When: User runs 'snippets update mail -p' (matches both)
    Then: Should show numbered list and prompt for selection
    """
    # This test should FAIL initially
    with patch('subprocess.run') as mock_subprocess, \
         patch('tempfile.NamedTemporaryFile') as mock_tempfile, \
         patch('builtins.open', create=True) as mock_open, \
         patch('typer.prompt', return_value='1'):

        # Setup mocks
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test.txt'
        mock_tempfile.return_value.__enter__.return_value = mock_temp

        mock_file = MagicMock()
        mock_file.read.return_value = r'\b(MAIL|EMAIL|NEW)\b[.,;:!?]?'
        mock_open.return_value.__enter__.return_value = mock_file

        result = runner.invoke(app, [
            'update', 'mail',  # Matches both 'mail' and 'gmail'
            '-p',
            '--force',
            '--config', str(temp_config_dir['config_path']),
            '--snippets-dir', str(temp_config_dir['snippets_dir'])
        ])

        # Should show multiple results and prompt for selection
        assert result.exit_code == 0
        # Should show table with numbers
        assert '#' in result.stdout or 'Select' in result.stdout


def test_update_no_matches_shows_error(temp_config_dir):
    """Test: No matches should show helpful error message.

    Given: No snippet matches the keyword
    When: User runs 'snippets update nonexistent -p'
    Then: Should show error with suggestion to create snippet
    """
    # This test should FAIL initially
    result = runner.invoke(app, [
        'update', 'nonexistent',
        '-p',
        '--config', str(temp_config_dir['config_path']),
        '--snippets-dir', str(temp_config_dir['snippets_dir'])
    ])

    # Should fail with helpful message
    assert result.exit_code != 0
    assert 'not found' in result.stdout.lower() or 'no match' in result.stdout.lower()


def test_update_search_respects_exact_match_priority(temp_config_dir):
    """Test: Exact name match should take priority over fuzzy search.

    Given: Snippets 'mail' and 'gmail' exist
    When: User runs 'snippets update mail -p'
    Then: Should use exact match 'mail', not search for both
    """
    # This test should FAIL initially
    with patch('subprocess.run') as mock_subprocess, \
         patch('tempfile.NamedTemporaryFile') as mock_tempfile, \
         patch('builtins.open', create=True) as mock_open:

        # Setup mocks
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test.txt'
        mock_tempfile.return_value.__enter__.return_value = mock_temp

        mock_file = MagicMock()
        mock_file.read.return_value = r'\b(MAIL|EMAIL)\b[.,;:!?]?'
        mock_open.return_value.__enter__.return_value = mock_file

        result = runner.invoke(app, [
            'update', 'mail',
            '-p',
            '--force',
            '--config', str(temp_config_dir['config_path']),
            '--snippets-dir', str(temp_config_dir['snippets_dir'])
        ])

        # Should succeed with exact match, no search UI shown
        assert result.exit_code == 0
        assert 'Updated snippet: mail' in result.stdout
        # Should NOT show search results table
        assert 'Search results' not in result.stdout
