"""Input validation helpers for CLI commands."""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List

import typer
from rich.console import Console

console = Console()


def load_and_validate_json(
    json_path_str: str,
    validator_func: Callable[[Dict[str, Any]], List[str]],
    schema_help_command: str
) -> Dict[str, Any]:
    """Load JSON from file and validate it.

    Args:
        json_path_str: Path to JSON file as string
        validator_func: Function to validate JSON data, returns list of error messages
        schema_help_command: Command to show schema (e.g., "gmail send --schema")

    Returns:
        Validated JSON data as dictionary

    Raises:
        typer.Exit: If file not found, invalid JSON, or validation fails
    """
    # Load JSON from file
    json_path = Path(json_path_str)

    if not json_path.exists():
        console.print(f"[red]✗ File not found: {json_path}[/red]")
        raise typer.Exit(code=1)

    if not json_path.is_file():
        console.print(f"[red]✗ Not a file: {json_path}[/red]")
        raise typer.Exit(code=1)

    try:
        console.print(f"Reading JSON from: {json_path}")
        with open(json_path) as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ Invalid JSON in {json_path}: {e}[/red]")
        console.print(f"\nView schema: [cyan]{schema_help_command}[/cyan]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error reading file: {e}[/red]")
        raise typer.Exit(code=1)

    # Validate JSON against schema
    validation_errors = validator_func(json_data)
    if validation_errors:
        console.print(f"[red]✗ Invalid JSON data:[/red]")
        for err in validation_errors:
            console.print(f"  - {err}")
        console.print(f"\nView schema: [cyan]{schema_help_command}[/cyan]")
        raise typer.Exit(code=1)

    return json_data


def display_schema_and_exit(
    schema_getter: Callable[[], str],
    title: str,
    description: str,
    usage_example: str,
) -> None:
    """Display JSON schema and exit.

    Args:
        schema_getter: Function that returns formatted JSON schema string
        title: Title to display (e.g., "Send Email JSON Schema")
        description: Brief description of the schema
        usage_example: Example command showing how to use the schema
    """
    schema_str = schema_getter(indent=2)
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print(f"[dim]{description}[/dim]\n")
    console.print_json(schema_str)
    console.print("\n[bold]Usage Example:[/bold]")
    console.print(f"  [cyan]{usage_example}[/cyan]")
