"""Gmail configuration management commands."""

import os
import subprocess

import typer
from rich.console import Console

from gmaillm.helpers.config import (
    get_plugin_config_dir,
    get_styles_dir,
    get_groups_file_path,
    load_json_config
)
from gmaillm.validators.email import validate_editor

# Initialize Typer app and console
app = typer.Typer(help="Manage Gmail integration configuration")
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


@app.command("edit-style")
def edit_style() -> None:
    """Edit email style preferences (deprecated)."""
    # Deprecation warning
    console.print("[yellow]⚠️  Deprecation Warning:[/yellow]")
    console.print("[yellow]   'gmail config edit-style' is deprecated.[/yellow]")
    console.print("[yellow]   Use the new styles system instead:[/yellow]")
    console.print("[yellow]     - List styles: [cyan]gmail styles list[/cyan][/yellow]")
    console.print("[yellow]     - Edit style:  [cyan]gmail styles edit <name>[/cyan][/yellow]")
    console.print()

    config_dir = get_plugin_config_dir()
    style_file = config_dir / "email-style.md"

    try:
        # Check if file exists using try/except (avoids TOCTOU)
        with open(style_file):
            pass
    except FileNotFoundError:
        console.print(f"[red]Error: {style_file} does not exist[/red]")
        console.print(f"\nThe old style file has been replaced by the new styles system.")
        console.print(f"Use: [cyan]gmail styles list[/cyan]")
        raise typer.Exit(code=1)

    editor = os.environ.get("EDITOR", "vim")
    validate_editor(editor)
    console.print(f"Opening {style_file} in {editor}...")
    subprocess.run([editor, str(style_file)], shell=False)


@app.command("edit-groups")
def edit_groups() -> None:
    """Edit email distribution groups (deprecated)."""
    # Deprecation warning
    console.print("[yellow]⚠️  Deprecation Warning:[/yellow]")
    console.print("[yellow]   'gmail config edit-groups' is deprecated.[/yellow]")
    console.print("[yellow]   Use the new groups system instead:[/yellow]")
    console.print("[yellow]     - Create group: [cyan]gmail groups create <name> --emails email@example.com[/cyan][/yellow]")
    console.print("[yellow]     - Add member:   [cyan]gmail groups add <group> <email>[/cyan][/yellow]")
    console.print("[yellow]     - Remove member: [cyan]gmail groups remove <group> <email>[/cyan][/yellow]")
    console.print()

    groups_file = get_groups_file_path()

    try:
        # Check if file exists using try/except (avoids TOCTOU)
        with open(groups_file):
            pass
    except FileNotFoundError:
        console.print(f"[red]Error: {groups_file} does not exist[/red]")
        raise typer.Exit(code=1)

    editor = os.environ.get("EDITOR", "vim")
    validate_editor(editor)
    console.print(f"Opening {groups_file} in {editor}...")
    subprocess.run([editor, str(groups_file)], shell=False)


@app.command("list-groups")
def list_groups() -> None:
    """List all configured email distribution groups (deprecated)."""
    # Deprecation warning
    console.print("[yellow]⚠️  Deprecation Warning:[/yellow]")
    console.print("[yellow]   'gmail config list-groups' is deprecated.[/yellow]")
    console.print("[yellow]   Use: [cyan]gmail groups list[/cyan][/yellow]")
    console.print()

    groups_file = get_groups_file_path()
    groups = load_json_config(groups_file)

    if not groups:
        console.print(f"[red]Error: Could not load {groups_file}[/red]")
        raise typer.Exit(code=1)

    console.print("=" * 60)
    console.print("Email Distribution Groups")
    console.print("=" * 60)

    for group_name, emails in groups.items():
        if group_name.startswith("_"):
            continue  # Skip comments/metadata
        console.print(f"\n#{group_name}:")
        for email in emails:
            console.print(f"  - {email}")

    total = len([k for k in groups.keys() if not k.startswith("_")])
    console.print(f"\nTotal groups: {total}")
    console.print(
        '\nUsage: [cyan]gmail send --to #groupname --subject "..." --body "..."[/cyan]'
    )
