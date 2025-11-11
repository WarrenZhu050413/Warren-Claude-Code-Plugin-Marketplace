"""Tests for search integration in update command - Unit tests."""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from snippets.client import SnippetsClient
from snippets.models import SearchResult, SnippetInfo


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

    # Create empty local config
    local_config_path = config_dir / "config.local.json"
    with open(local_config_path, 'w') as f:
        json.dump({"mappings": []}, f)

    return {
        "config_dir": config_dir,
        "config_path": config_path,
        "snippets_dir": snippets_dir,
    }


@pytest.fixture
def client(temp_config_dir):
    """Create a SnippetsClient instance for testing."""
    return SnippetsClient(
        config_path=temp_config_dir["config_path"],
        snippets_dir=temp_config_dir["snippets_dir"]
    )


# =============================================================================
# TESTS FOR SEARCH INTEGRATION
# =============================================================================

def test_find_exact_match_returns_snippet(client):
    """Test: Exact match should return the snippet directly."""
    from snippets.cli import _find_or_search_snippet

    snippet = _find_or_search_snippet(client, "mail")

    assert snippet is not None
    assert snippet.name == "mail"
    assert "MAIL" in snippet.pattern


def test_find_single_fuzzy_match_returns_snippet(client):
    """Test: Single fuzzy match should return automatically."""
    from snippets.cli import _find_or_search_snippet

    # 'gma' should match only 'gmail'
    snippet = _find_or_search_snippet(client, "gma")

    assert snippet is not None
    assert snippet.name == "gmail"


def test_find_multiple_fuzzy_matches_prompts_user(client):
    """Test: Multiple fuzzy matches should prompt for selection."""
    import typer

    from snippets.cli import _find_or_search_snippet

    # 'ma' should match both 'mail' and 'gmail'
    # Mock the prompt to return first choice
    with patch('typer.prompt', return_value='1') as mock_prompt:
        snippet = _find_or_search_snippet(client, "ma")

        # Should have prompted for selection
        assert mock_prompt.called
        assert snippet is not None
        # Should select one of the matches
        assert snippet.name in ["mail", "gmail"]


def test_find_no_matches_raises_exit(client):
    """Test: No matches should raise typer.Exit."""
    import typer

    from snippets.cli import _find_or_search_snippet

    with pytest.raises(typer.Exit) as exc_info:
        _find_or_search_snippet(client, "nonexistent")

    # Should exit with error code
    assert exc_info.value.exit_code == 1


def test_exact_match_takes_priority(client):
    """Test: Exact match should take priority over fuzzy search."""
    from snippets.cli import _find_or_search_snippet

    # 'mail' is both an exact match and could fuzzy match 'gmail'
    snippet = _find_or_search_snippet(client, "mail")

    # Should return exact match 'mail', not prompt for selection
    assert snippet.name == "mail"
    assert "MAIL" in snippet.pattern


def test_find_with_quit_selection_raises_exit(client):
    """Test: User selecting 'q' should raise typer.Exit with code 0."""
    import typer

    from snippets.cli import _find_or_search_snippet

    # Mock prompt to return 'q'
    with patch('typer.prompt', return_value='q') as mock_prompt, \
         pytest.raises(typer.Exit) as exc_info:
        _find_or_search_snippet(client, "ma")  # Matches both 'mail' and 'gmail'

    # Should exit cleanly (code 0)
    assert exc_info.value.exit_code == 0


def test_find_with_invalid_selection_raises_exit(client):
    """Test: Invalid selection should raise typer.Exit with code 1."""
    import typer

    from snippets.cli import _find_or_search_snippet

    # Mock prompt to return invalid choice
    with patch('typer.prompt', return_value='999') as mock_prompt, \
         pytest.raises(typer.Exit) as exc_info:
        _find_or_search_snippet(client, "ma")  # Matches both 'mail' and 'gmail'

    # Should exit with error code
    assert exc_info.value.exit_code == 1
