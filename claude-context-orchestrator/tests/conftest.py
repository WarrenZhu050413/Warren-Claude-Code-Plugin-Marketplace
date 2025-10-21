"""
Pytest configuration and shared fixtures for all tests
"""

import sys
from pathlib import Path

# Add scripts directory to Python path so tests can import snippet_injector and snippets_cli
PLUGIN_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import pytest


@pytest.fixture
def plugin_root():
    """Return the plugin root directory"""
    return PLUGIN_ROOT


@pytest.fixture
def scripts_dir():
    """Return the scripts directory"""
    return SCRIPTS_DIR


@pytest.fixture
def config_path():
    """Return the default config path"""
    return SCRIPTS_DIR / "config.json"


@pytest.fixture
def snippets_dir():
    """Return the snippets directory"""
    return PLUGIN_ROOT / "snippets"


@pytest.fixture
def skills_dir():
    """Return the skills directory"""
    return PLUGIN_ROOT / "skills"
