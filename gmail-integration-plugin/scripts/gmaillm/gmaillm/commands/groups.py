"""Gmail distribution groups management commands."""

import os
import subprocess
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from gmaillm.helpers.config import (
    get_groups_file_path,
    load_email_groups,
    save_email_groups,
    create_backup
)
from gmaillm.helpers.typer_utils import HelpfulGroup
from gmaillm.helpers.json_input import load_and_validate_json, display_schema_and_exit
from gmaillm.helpers.cli_utils import (
    show_operation_preview,
    confirm_or_force,
    handle_command_error,
    ensure_item_exists,
    create_backup_with_message,
    print_success
)
from gmaillm.validators.email import validate_email, validate_editor
from gmaillm.validators.email_operations import (
    get_group_json_schema_string,
    validate_group_json
)

# Initialize Typer app and console
app = typer.Typer(
    help="Manage email distribution groups",
    cls=HelpfulGroup  # Show help on missing required args
)
console = Console()


@app.command("schema")
def show_schema() -> None:
    """Display JSON schema for programmatic group creation.

    This schema defines the structure required for creating groups
    via the --json-input flag in the 'create' command.
    """
    display_schema_and_exit(
        schema_getter=get_group_json_schema_string,
        title="Email Group JSON Schema",
        description="Use this schema for programmatic group creation with --json-input",
        usage_example="gmail groups create --json-input group.json --force"
    )


@app.command("list")
def list_groups() -> None:
    """List all email distribution groups with member counts."""
    try:
        groups = load_email_groups()

        if not groups:
            console.print("[yellow]No groups found[/yellow]")
            console.print(f"\nCreate a group: [cyan]gmail groups create <name> --emails email@example.com[/cyan]")
            return

        # Create table
        table = Table(title="Email Distribution Groups")
        table.add_column("Group", style="cyan")
        table.add_column("Members", justify="right", style="green")
        table.add_column("Emails", style="dim")

        for name, emails in sorted(groups.items()):
            # Show first 2 emails, then "..."
            if len(emails) <= 2:
                email_preview = ", ".join(emails)
            else:
                email_preview = f"{emails[0]}, {emails[1]}, ... ({len(emails) - 2} more)"

            table.add_row(f"#{name}", str(len(emails)), email_preview)

        console.print(table)
        console.print(f"\n[dim]Total: {len(groups)} group(s)[/dim]")
        console.print(f"\nUsage: [cyan]gmail send --to #groupname --subject \"...\" --body \"...\"[/cyan]")

    except Exception as e:
        console.print(f"[red]✗ Error listing groups: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("show")
def show_group(
    name: str = typer.Argument(..., help="Name of the group to show"),
) -> None:
    """Show detailed information about a specific group."""
    try:
        groups = load_email_groups()

        if name not in groups:
            console.print(f"[red]✗ Group '{name}' not found[/red]")
            console.print(f"\nAvailable groups: [cyan]gmail groups list[/cyan]")
            raise typer.Exit(code=1)

        emails = groups[name]

        console.print("=" * 60)
        console.print(f"Group: #{name}")
        console.print("=" * 60)
        console.print(f"Members: {len(emails)}")
        console.print()

        for i, email in enumerate(emails, 1):
            console.print(f"  {i}. {email}")

        console.print()
        console.print(f"Usage: [cyan]gmail send --to #{name} ...[/cyan]")

    except Exception as e:
        console.print(f"[red]✗ Error showing group: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("create")
def create_group(
    name: Optional[str] = typer.Argument(None, help="Name of the group to create (required unless using --json-input)"),
    emails: Optional[List[str]] = typer.Option(None, "--emails", "-e", help="Email addresses to add"),
    json_input: Optional[str] = typer.Option(
        None,
        "--json-input",
        "-j",
        help="Path to JSON file for programmatic creation"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Create a new email distribution group from CLI args or JSON file.

    \b
    MODES:
      1. Interactive (default): Provide name and emails via CLI
      2. Programmatic (--json-input): Create from JSON file

    \b
    EXAMPLES:
      Interactive creation:
        $ gmail groups create team --emails user1@example.com --emails user2@example.com

      From JSON file:
        $ gmail groups create --json-input group.json --force

      View schema:
        $ gmail groups schema
    """
    try:
        groups = load_email_groups()

        # PROGRAMMATIC MODE: JSON input
        if json_input:
            console.print("[cyan]Creating group from JSON file...[/cyan]")

            # Load and validate JSON
            json_data = load_and_validate_json(
                json_path_str=json_input,
                validator_func=validate_group_json,
                schema_help_command="gmail groups schema"
            )

            # Extract from JSON
            group_name = json_data["name"]
            member_emails = json_data["members"]

        # INTERACTIVE MODE: CLI arguments
        else:
            if name is None:
                console.print("[red]✗ Group name is required (or use --json-input)[/red]")
                console.print("\nUsage: [cyan]gmail groups create <name> --emails <email> ...[/cyan]")
                console.print("   Or: [cyan]gmail groups create --json-input group.json[/cyan]")
                raise typer.Exit(code=1)

            if emails is None or len(emails) == 0:
                console.print("[red]✗ At least one email is required (or use --json-input)[/red]")
                console.print("\nUsage: [cyan]gmail groups create {name} --emails <email> ...[/cyan]")
                raise typer.Exit(code=1)

            group_name = name
            member_emails = emails

        # Check if group already exists
        if group_name in groups:
            console.print(f"[red]✗ Group '{group_name}' already exists[/red]")
            if not force:
                console.print(f"\nUse: [cyan]gmail groups add {group_name} <email>[/cyan]")
                console.print(f"Or: [cyan]gmail groups create ... --force[/cyan] to overwrite")
                raise typer.Exit(code=1)
            else:
                console.print("[yellow]--force: Overwriting existing group[/yellow]")

        # Validate email addresses
        for email in member_emails:
            if not validate_email(email):
                console.print(f"[red]✗ Invalid email address: {email}[/red]")
                raise typer.Exit(code=1)

        # Show preview
        console.print("=" * 60)
        console.print("Creating Email Group")
        console.print("=" * 60)
        console.print(f"Name: #{group_name}")
        console.print(f"Members: {len(member_emails)}")
        for email in member_emails:
            console.print(f"  - {email}")
        console.print("=" * 60)

        # Confirm unless --force
        if not force:
            response = typer.confirm("\nCreate this group?")
            if not response:
                console.print("Cancelled.")
                return
        else:
            console.print("\n[yellow]--force: Creating without confirmation[/yellow]")

        # Create group
        groups[group_name] = member_emails
        save_email_groups(groups)

        console.print(f"\n[green]✅ Group created: #{group_name}[/green]")
        console.print(f"   Members: {len(member_emails)}")
        console.print(f"\nUsage: [cyan]gmail send --to #{group_name} ...[/cyan]")

    except Exception as e:
        console.print(f"[red]✗ Error creating group: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("add")
def add_member(
    group: str = typer.Argument(..., help="Group name"),
    email: str = typer.Argument(..., help="Email address to add"),
) -> None:
    """Add a member to an existing group."""
    try:
        groups = load_email_groups()

        # Check if group exists
        if group not in groups:
            console.print(f"[red]✗ Group '{group}' not found[/red]")
            console.print(f"\nCreate it first: [cyan]gmail groups create {group} --emails {email}[/cyan]")
            raise typer.Exit(code=1)

        # Validate email
        if not validate_email(email):
            console.print(f"[red]✗ Invalid email address: {email}[/red]")
            raise typer.Exit(code=1)

        # Check if already a member
        if email in groups[group]:
            console.print(f"[yellow]⚠️  {email} is already in group #{group}[/yellow]")
            return

        # Add member
        groups[group].append(email)
        save_email_groups(groups)

        console.print(f"[green]✅ Added {email} to #{group}[/green]")
        console.print(f"   Total members: {len(groups[group])}")

    except Exception as e:
        console.print(f"[red]✗ Error adding member: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("remove")
def remove_member(
    group: str = typer.Argument(..., help="Group name"),
    email: str = typer.Argument(..., help="Email address to remove"),
) -> None:
    """Remove a member from a group."""
    try:
        groups = load_email_groups()

        # Check if group exists
        if group not in groups:
            console.print(f"[red]✗ Group '{group}' not found[/red]")
            raise typer.Exit(code=1)

        # Check if member exists
        if email not in groups[group]:
            console.print(f"[yellow]⚠️  {email} is not in group #{group}[/yellow]")
            return

        # Remove member
        groups[group].remove(email)

        # If group is now empty, ask if they want to delete it
        if len(groups[group]) == 0:
            console.print(f"[yellow]⚠️  Group #{group} is now empty[/yellow]")
            response = typer.confirm("Delete the empty group?")
            if response:
                del groups[group]
                save_email_groups(groups)
                console.print(f"[green]✅ Removed {email} and deleted empty group #{group}[/green]")
                return

        save_email_groups(groups)
        console.print(f"[green]✅ Removed {email} from #{group}[/green]")
        console.print(f"   Remaining members: {len(groups[group])}")

    except Exception as e:
        console.print(f"[red]✗ Error removing member: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("delete")
def delete_group(
    name: str = typer.Argument(..., help="Name of the group to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete an email distribution group."""
    try:
        groups = load_email_groups()

        # Check if exists
        ensure_item_exists(name, groups, "Group", "gmail groups list")

        # Show what will be deleted
        show_operation_preview(
            "Deleting Email Group",
            {
                "Name": f"#{name}",
                "Members": len(groups[name]),
                "Emails": groups[name]
            }
        )

        # Confirm unless --force
        if not confirm_or_force("\n⚠️  Delete this group? This cannot be undone.", force, "Deleting without confirmation"):
            console.print("Cancelled.")
            return

        # Create backup before deletion
        groups_file = get_groups_file_path()
        create_backup_with_message(groups_file, create_backup)

        # Delete
        del groups[name]
        save_email_groups(groups)

        print_success(f"Group deleted: #{name}")

    except Exception as e:
        handle_command_error("deleting group", e)


@app.command("edit")
def edit_groups() -> None:
    """Open email groups file in editor (deprecated - use create/add/remove instead)."""
    # Deprecation warning
    console.print("[yellow]⚠️  Deprecation Warning:[/yellow]")
    console.print("[yellow]   'gmail groups edit' is deprecated.[/yellow]")
    console.print("[yellow]   Use these commands instead:[/yellow]")
    console.print("[yellow]     - Create group: [cyan]gmail groups create <name> --emails email@example.com[/cyan][/yellow]")
    console.print("[yellow]     - Add member:   [cyan]gmail groups add <group> <email>[/cyan][/yellow]")
    console.print("[yellow]     - Remove member: [cyan]gmail groups remove <group> <email>[/cyan][/yellow]")
    console.print()

    groups_file = get_groups_file_path()

    try:
        # Check if file exists
        with open(groups_file):
            pass
    except FileNotFoundError:
        console.print(f"[red]Error: {groups_file} does not exist[/red]")
        raise typer.Exit(code=1)

    editor = os.environ.get("EDITOR", "vim")
    validate_editor(editor)
    console.print(f"Opening {groups_file} in {editor}...")
    subprocess.run([editor, str(groups_file)], shell=False)


@app.command("validate")
def validate_group(
    name: Optional[str] = typer.Argument(None, help="Group name to validate (validates all if not specified)"),
) -> None:
    """Validate group(s) for email format, duplicates."""
    try:
        groups = load_email_groups()

        if name:
            # Validate single group
            if name not in groups:
                console.print(f"[red]✗ Group '{name}' not found[/red]")
                raise typer.Exit(code=1)

            groups_to_validate = {name: groups[name]}
        else:
            # Validate all groups
            groups_to_validate = groups

        errors_found = False

        for group_name, emails in groups_to_validate.items():
            group_errors = []

            # Check for invalid emails
            for email in emails:
                if not validate_email(email):
                    group_errors.append(f"Invalid email: {email}")

            # Check for duplicates
            seen = set()
            for email in emails:
                if email in seen:
                    group_errors.append(f"Duplicate email: {email}")
                seen.add(email)

            # Report
            if group_errors:
                console.print(f"[red]✗ #{group_name}:[/red]")
                for error in group_errors:
                    console.print(f"  - {error}")
                errors_found = True
            else:
                console.print(f"[green]✅ #{group_name}[/green]")

        if errors_found:
            console.print(f"\n[red]Validation failed[/red]")
            console.print(f"Fix manually: [cyan]gmail groups edit[/cyan]")
            raise typer.Exit(code=1)
        else:
            if name:
                console.print(f"\n[green]✅ Group #{name} is valid[/green]")
            else:
                console.print(f"\n[green]✅ All groups are valid[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error validating groups: {e}[/red]")
        raise typer.Exit(code=1)
