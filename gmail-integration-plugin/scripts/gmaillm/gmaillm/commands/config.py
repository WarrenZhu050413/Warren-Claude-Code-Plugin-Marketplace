"""Gmail configuration management commands."""

import os

import typer
from rich.console import Console

from gmaillm.helpers.config import (
    get_plugin_config_dir,
    get_styles_dir,
    get_groups_file_path
)
from gmaillm.helpers.typer_utils import HelpOnMissingArgsGroup

# Initialize Typer app and console
app = typer.Typer(
    help="Manage Gmail integration configuration",
    cls=HelpOnMissingArgsGroup  # Show help on missing required args
)
console = Console()


@app.command("show")
def show_config() -> None:
    """Show configuration file locations and commands."""
    config_dir = get_plugin_config_dir()
    styles_dir = get_styles_dir()
    groups_file = get_groups_file_path()
    learned_dir = config_dir / "learned-patterns"

    editor = os.environ.get("EDITOR", "vim")

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
    console.print("  [cyan]gmail styles validate-all[/cyan]    # Validate all styles")
    console.print("\nGroup Commands:")
    console.print("  [cyan]gmail groups list[/cyan]            # List all groups")
    console.print("  [cyan]gmail groups create <name>[/cyan]   # Create new group")
    console.print("  [cyan]gmail groups add <group> <email>[/cyan]  # Add member")
    console.print("  [cyan]gmail groups validate[/cyan]        # Validate all groups")
    console.print("\nOther:")
    console.print("  [cyan]gmail config show[/cyan]            # Show this information")
