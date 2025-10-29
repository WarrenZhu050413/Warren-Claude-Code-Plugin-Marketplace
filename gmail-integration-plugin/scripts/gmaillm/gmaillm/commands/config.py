"""Gmail configuration management commands."""

import os

import typer
from rich.console import Console

from gmaillm.helpers.core import (
    get_plugin_config_dir,
    get_styles_dir,
    get_groups_file_path
)
from gmaillm.helpers.cli import HelpfulGroup

# Initialize Typer app and console
app = typer.Typer(
    help="Manage Gmail integration configuration",
    cls=HelpfulGroup,  # Show help on missing required args
    context_settings={"help_option_names": ["-h", "--help"]}
)
console = Console()


@app.command("show")
def show_config(
    output_format: str = typer.Option("rich", "--output-format", help="Output format (rich|json)"),
) -> None:
    """Show configuration file locations and commands."""
    from enum import Enum

    # Define OutputFormat enum locally to avoid circular import
    class OutputFormat(str, Enum):
        RICH = "rich"
        JSON = "json"

    config_dir = get_plugin_config_dir()
    styles_dir = get_styles_dir()
    groups_file = get_groups_file_path()
    learned_dir = config_dir / "learned-patterns"

    editor = os.environ.get("EDITOR", "vi")

    # Parse output format
    try:
        format_enum = OutputFormat(output_format.lower())
    except ValueError:
        console.print(f"[red]✗ Invalid output format: {output_format}. Use 'rich' or 'json'[/red]")
        raise typer.Exit(code=1)

    if format_enum == OutputFormat.JSON:
        config_data = {
            "config_dir": str(config_dir),
            "email_styles": str(styles_dir),
            "email_groups": str(groups_file),
            "learned_patterns": str(learned_dir),
            "editor": editor
        }
        console.print_json(data=config_data)
        return

    console.print("=" * 60)
    console.print("Gmail Integration Configuration")
    console.print("=" * 60)
    console.print(f"\nEmail Styles:     {styles_dir}")
    console.print(f"Email Groups:     {groups_file}")
    console.print(f"Learned Patterns: {learned_dir}")
    console.print(f"\nEditor: {editor} (set via $EDITOR)")
    console.print("\nStyle Commands:")
    console.print("  [cyan]gmail styles list[/cyan]            # List all email styles")
    console.print("  [cyan]gmail styles create <name>[/cyan]   # Create new style")
    console.print("  [cyan]gmail styles edit <name>[/cyan]     # Edit style")
    console.print("  [cyan]gmail styles validate [name][/cyan] # Validate style(s)")
    console.print("\nGroup Commands:")
    console.print("  [cyan]gmail groups list[/cyan]            # List all groups")
    console.print("  [cyan]gmail groups create <name>[/cyan]   # Create new group")
    console.print("  [cyan]gmail groups add <group> <email>[/cyan]  # Add member")
    console.print("  [cyan]gmail groups validate[/cyan]        # Validate all groups")
    console.print("\nOther:")
    console.print("  [cyan]gmail config show[/cyan]            # Show this information")
