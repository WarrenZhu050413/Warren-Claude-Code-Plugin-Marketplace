"""User interface helpers for CLI commands."""

from typing import Any, Callable, Dict, List, Optional

from rich.console import Console

from gmaillm.helpers.cli.typer_extras import OutputFormat

console = Console()


def show_operation_preview(
    title: str,
    details: Dict[str, Any],
    width: int = 60
) -> None:
    """Display a formatted preview box for operations.

    Args:
        title: Operation title (e.g., "Creating Email Group")
        details: Dictionary of field names to values to display
        width: Width of the separator line

    Example:
        show_operation_preview(
            "Creating Email Group",
            {
                "Name": "#team",
                "Members": 3,
                "Emails": ["user1@example.com", "user2@example.com"]
            }
        )
    """
    console.print("=" * width)
    console.print(title)
    console.print("=" * width)

    for key, value in details.items():
        if isinstance(value, list):
            console.print(f"{key}: {len(value)}")
            for item in value:
                console.print(f"  - {item}")
        else:
            console.print(f"{key}: {value}")

    console.print("=" * width)


def print_success(
    message: str,
    details: Optional[Dict[str, Any]] = None,
    next_steps: Optional[List[str]] = None
) -> None:
    """Display success message with optional details and next steps.

    Args:
        message: Main success message
        details: Optional dictionary of additional details to show
        next_steps: Optional list of suggested next steps

    Example:
        print_success(
            f"Group created: #{group_name}",
            {"Members": len(emails)},
            ["gmail send --to #{group_name} ..."]
        )
    """
    console.print(f"\n[green]✅ {message}[/green]")

    if details:
        for key, value in details.items():
            console.print(f"   {key}: {value}")

    if next_steps:
        console.print("\nNext steps:")
        for step in next_steps:
            console.print(f"  [cyan]{step}[/cyan]")


def output_json_or_rich(
    format_enum: OutputFormat,
    json_data: Any,
    rich_func: Callable[[], None]
) -> None:
    """Output data in JSON or Rich format based on the format enum.

    Args:
        format_enum: The output format (OutputFormat.JSON or OutputFormat.RICH)
        json_data: Data to output as JSON (will be passed to console.print_json)
        rich_func: Function to call for Rich output (should take no arguments)

    Example:
        output_json_or_rich(
            format_enum,
            json_data=[f.model_dump(mode='json') for f in folders],
            rich_func=lambda: formatter.print_folder_list(folders, "Gmail Labels")
        )
    """
    if format_enum == OutputFormat.JSON:
        console.print_json(data=json_data)
    else:
        rich_func()
