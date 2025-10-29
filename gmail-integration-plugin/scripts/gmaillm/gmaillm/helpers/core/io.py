"""Generic file I/O operations for gmaillm."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from rich.console import Console

console = Console()


def load_json_config(file_path: Path) -> Dict[str, Any]:
    """Load JSON config file with error handling.

    Args:
        file_path: Path to JSON config file

    Returns:
        Dictionary containing config data, or empty dict on error
    """
    try:
        with open(file_path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError) as e:
        console.print(f"[yellow]Warning: Could not load {file_path}: {e}[/yellow]")
        return {}


def save_json_config(file_path: Path, data: Dict[str, Any]) -> None:
    """Save data to JSON config file.

    Args:
        file_path: Path to JSON config file
        data: Dictionary to save

    Raises:
        OSError: If file cannot be written
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')  # Ensure trailing newline


def create_backup(file_path: Path) -> Path:
    """Create timestamped backup of file.

    Args:
        file_path: Path to file to backup

    Returns:
        Path to backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.parent / f"{file_path.stem}.backup.{timestamp}{file_path.suffix}"
    backup_path.write_text(file_path.read_text())
    return backup_path
