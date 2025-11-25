"""Gmail configuration management commands."""

import os

import typer
from rich.console import Console

from gmaillm.helpers.core import (
    get_plugin_config_dir,
    get_styles_dir,
    get_groups_file_path
)
from gmaillm.helpers.cli import HelpfulGroup, OutputFormat, parse_output_format, output_json_or_rich

# Initialize Typer app and console
app = typer.Typer(
    help="Manage Gmail integration configuration",
    cls=HelpfulGroup,  # Show help on missing required args
    context_settings={"help_option_names": ["-h", "--help"]}
)
console = Console()


@app.command("examples")
def show_examples() -> None:
    """Show example usage for configuration management."""
    console.print("\n[bold cyan]Configuration - Example Usage[/bold cyan]\n")

    console.print("[bold]👁️  VIEWING CONFIGURATION[/bold]")
    console.print("  [dim]$ gmail config show[/dim]")
    console.print("  [dim]$ gmail config show --output-format json[/dim]")
    console.print()

    console.print("[bold yellow]💡 COMMON TASKS[/bold yellow]")
    console.print("  [dim]1. Find where styles are stored:[/dim]")
    console.print("     [dim]gmail config show[/dim]")
    console.print("     [dim]# Look for \"Email Styles\" path[/dim]")
    console.print()
    console.print("  [dim]2. Check current editor:[/dim]")
    console.print("     [dim]gmail config show | grep Editor[/dim]")
    console.print()
    console.print("  [dim]3. Get all config as JSON for automation:[/dim]")
    console.print("     [dim]gmail config show --output-format json[/dim]")
    console.print()


@app.command("show")
def show_config(
    output_format: str = typer.Option("rich", "--output-format", help="Output format (rich|json)"),
) -> None:
    """Show configuration file locations and commands."""
    config_dir = get_plugin_config_dir()
    styles_dir = get_styles_dir()
    groups_file = get_groups_file_path()
    learned_dir = config_dir / "learned-patterns"

    editor = os.environ.get("EDITOR", "vi")

    # Parse output format
    format_enum = parse_output_format(output_format, console)

    # Prepare JSON data
    config_data = {
        "config_dir": str(config_dir),
        "email_styles": str(styles_dir),
        "email_groups": str(groups_file),
        "learned_patterns": str(learned_dir),
        "editor": editor
    }

    # Define rich output function
    def print_rich():
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

    # Output in appropriate format
    output_json_or_rich(format_enum, config_data, print_rich)
