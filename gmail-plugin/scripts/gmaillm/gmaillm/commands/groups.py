"""Gmail distribution groups management commands."""

from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from gmaillm.helpers.core import get_groups_file_path, create_backup
from gmaillm.helpers.domain import load_email_groups, normalize_group_name, save_email_groups
from gmaillm.helpers.cli import (
    HelpfulGroup,
    OutputFormat,
    parse_output_format,
    load_and_validate_json,
    display_schema_and_exit,
    show_operation_preview,
    confirm_or_force,
    handle_command_error,
    ensure_item_exists,
    create_backup_with_message,
    print_success,
    output_json_or_rich
)
from gmaillm.validators.email import validate_email
from gmaillm.validators.email_operations import (
    get_group_json_schema_string,
    validate_group_json
)

# Initialize Typer app and console
app = typer.Typer(
    help="Manage email distribution groups",
    cls=HelpfulGroup,  # Show help on missing required args
    context_settings={"help_option_names": ["-h", "--help"]}
)
console = Console()


@app.command("examples")
def show_examples() -> None:
    """Show example usage and workflows for email groups."""
    console.print("\n[bold cyan]Email Groups - Example Usage[/bold cyan]\n")

    console.print("[bold]📋 LISTING GROUPS[/bold]")
    console.print("  [dim]$ gmail groups list[/dim]")
    console.print("  [dim]$ gmail groups list --output-format json[/dim]")
    console.print()

    console.print("[bold]👁️  VIEWING GROUP DETAILS[/bold]")
    console.print("  [dim]$ gmail groups show team[/dim]")
    console.print("  [dim]$ gmail groups show #team          # Also accepts # prefix[/dim]")
    console.print()

    console.print("[bold]➕ CREATING GROUPS[/bold]")
    console.print("  [dim]# Interactive mode[/dim]")
    console.print("  [dim]$ gmail groups create team --emails user1@example.com --emails user2@example.com[/dim]")
    console.print()
    console.print("  [dim]# Programmatic mode from JSON[/dim]")
    console.print("  [dim]$ gmail groups create --json-input-path team.json[/dim]")
    console.print("  [dim]$ gmail groups schema  # See JSON format[/dim]")
    console.print()

    console.print("[bold]👤 MANAGING MEMBERS[/bold]")
    console.print("  [dim]$ gmail groups add team user3@example.com[/dim]")
    console.print("  [dim]$ gmail groups add #team user4@example.com  # Also accepts # prefix[/dim]")
    console.print("  [dim]$ gmail groups remove team user1@example.com[/dim]")
    console.print()

    console.print("[bold]✓ VALIDATING GROUPS[/bold]")
    console.print("  [dim]$ gmail groups validate             # Validate all groups[/dim]")
    console.print("  [dim]$ gmail groups validate team        # Validate specific group[/dim]")
    console.print()

    console.print("[bold]🗑️  DELETING GROUPS[/bold]")
    console.print("  [dim]$ gmail groups delete team          # Prompts for confirmation[/dim]")
    console.print("  [dim]$ gmail groups delete team --force  # Skip confirmation[/dim]")
    console.print()

    console.print("[bold]📧 USING GROUPS IN EMAILS[/bold]")
    console.print("  [dim]$ gmail send --to #team --subject \"Meeting\" --body \"Let's meet tomorrow\"[/dim]")
    console.print("  [dim]$ gmail send --to user@example.com --cc #team --subject \"FYI\"[/dim]")
    console.print()

    console.print("[bold yellow]💡 WORKFLOWS[/bold yellow]")
    console.print("  [dim]1. Create a project team:[/dim]")
    console.print("     [dim]gmail groups create project-alpha --emails dev1@corp.com --emails dev2@corp.com[/dim]")
    console.print()
    console.print("  [dim]2. Add stakeholders:[/dim]")
    console.print("     [dim]gmail groups add project-alpha manager@corp.com[/dim]")
    console.print("     [dim]gmail groups add project-alpha designer@corp.com[/dim]")
    console.print()
    console.print("  [dim]3. Send updates:[/dim]")
    console.print("     [dim]gmail send --to #project-alpha --subject \"Weekly Update\" --body \"...\"[/dim]")
    console.print()


@app.command("schema")
def show_schema() -> None:
    """Display JSON schema for programmatic group creation."""
    display_schema_and_exit(
        schema_getter=get_group_json_schema_string,
        title="Email Group JSON Schema",
        description="Use this schema for programmatic group creation with --json-input-path",
        usage_example="gmail groups create --json-input-path group.json --force"
    )


@app.command("list")
def list_groups(
    output_format: str = typer.Option("rich", "--output-format", help="Output format (rich|json)"),
) -> None:
    """List all email distribution groups.

    \b
    EXAMPLES:
      $ gmail groups list
      $ gmail groups list --output-format json
    """
    try:
        groups = load_email_groups()

        # Parse output format
        format_enum = parse_output_format(output_format, console)

        # Prepare JSON data
        groups_list = [
            {"name": name, "members": emails, "member_count": len(emails)}
            for name, emails in sorted(groups.items())
        ]

        # Define rich output function
        def print_rich():
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

        # Output in appropriate format
        output_json_or_rich(format_enum, groups_list, print_rich)

    except Exception as e:
        console.print(f"[red]✗ Error listing groups: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("show")
def show_group(
    name: str = typer.Argument(..., help="Name of the group to show (with or without # prefix)"),
    output_format: str = typer.Option("rich", "--output-format", help="Output format (rich|json)"),
) -> None:
    """Show detailed information about a group.

    \b
    EXAMPLES:
      $ gmail groups show team
      $ gmail groups show #team
      $ gmail groups show team --output-format json
    """
    try:
        # Normalize group name (accept # prefix)
        name = normalize_group_name(name)

        groups = load_email_groups()
        ensure_item_exists(name, groups, "Group", "gmail groups list")

        emails = groups[name]

        # Parse output format
        format_enum = parse_output_format(output_format, console)

        # Prepare JSON data
        group_data = {
            "name": name,
            "members": emails,
            "member_count": len(emails)
        }

        # Define rich output function
        def print_rich():
            console.print("=" * 60)
            console.print(f"Group: #{name}")
            console.print("=" * 60)
            console.print(f"Members: {len(emails)}")
            console.print()

            for i, email in enumerate(emails, 1):
                console.print(f"  {i}. {email}")

            console.print()
            console.print(f"Usage: [cyan]gmail send --to #{name} ...[/cyan]")

        # Output in appropriate format
        output_json_or_rich(format_enum, group_data, print_rich)

    except Exception as e:
        handle_command_error("showing group", e)


@app.command("create")
def create_group(
    name: Optional[str] = typer.Argument(None, help="Name of the group to create (required unless using --json-input-path)"),
    emails: Optional[List[str]] = typer.Option(None, "--emails", "-e", help="Email addresses to add"),
    json_input_path: Optional[str] = typer.Option(
        None,
        "--json-input-path",
        "-j",
        help="Path to JSON file for programmatic creation"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Create a new email distribution group from CLI args or JSON file.

    \b
    MODES:
      1. Interactive: Provide name and emails via CLI
      2. Programmatic: Create from JSON file (--json-input-path)

    \b
    EXAMPLES:
      $ gmail groups create team --emails user1@example.com --emails user2@example.com
      $ gmail groups create --json-input-path group.json --force
      $ gmail groups schema
    """
    try:
        groups = load_email_groups()

        # PROGRAMMATIC MODE: JSON input
        if json_input_path:
            console.print("[cyan]Creating group from JSON file...[/cyan]")

            # Load and validate JSON
            json_data = load_and_validate_json(
                json_path_str=json_input_path,
                validator_func=validate_group_json,
                schema_help_command="gmail groups schema"
            )

            # Extract from JSON
            group_name = json_data["name"]
            member_emails = json_data["members"]

        # INTERACTIVE MODE: CLI arguments
        else:
            if name is None:
                console.print("[red]✗ Group name is required (or use --json-input-path)[/red]")
                console.print("\nUsage: [cyan]gmail groups create <name> --emails <email> ...[/cyan]")
                console.print("   Or: [cyan]gmail groups create --json-input-path group.json[/cyan]")
                raise typer.Exit(code=1)

            if emails is None or len(emails) == 0:
                console.print("[red]✗ At least one email is required (or use --json-input-path)[/red]")
                console.print("\nUsage: [cyan]gmail groups create {name} --emails <email> ...[/cyan]")
                raise typer.Exit(code=1)

            group_name = normalize_group_name(name)
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
        show_operation_preview(
            "Creating Email Group",
            {
                "Name": f"#{group_name}",
                "Members": len(member_emails),
                "Emails": member_emails
            }
        )

        # Confirm unless --force
        if not confirm_or_force("\nCreate this group?", force, "Creating without confirmation"):
            console.print("Cancelled.")
            return

        # Create group
        groups[group_name] = member_emails
        save_email_groups(groups)

        print_success(
            f"Group created: #{group_name}",
            {"Members": len(member_emails)},
            [f"gmail send --to #{group_name} ..."]
        )

    except Exception as e:
        handle_command_error("creating group", e)


@app.command("add")
def add_member(
    group: str = typer.Argument(..., help="Group name (with or without # prefix)"),
    email: str = typer.Argument(..., help="Email address to add"),
) -> None:
    """Add a member to an existing group."""
    try:
        # Normalize group name (accept # prefix)
        group = normalize_group_name(group)

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
    group: str = typer.Argument(..., help="Group name (with or without # prefix)"),
    email: str = typer.Argument(..., help="Email address to remove"),
) -> None:
    """Remove a member from a group."""
    try:
        # Normalize group name (accept # prefix)
        group = normalize_group_name(group)

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
    name: str = typer.Argument(..., help="Name of the group to delete (with or without # prefix)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete an email distribution group."""
    try:
        # Normalize group name (accept # prefix)
        name = normalize_group_name(name)

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


@app.command("validate")
def validate_group(
    name: Optional[str] = typer.Argument(None, help="Group name to validate (with or without # prefix, validates all if not specified)"),
    output_format: str = typer.Option("rich", "--output-format", help="Output format (rich|json)"),
) -> None:
    """Validate group(s) for email format and duplicates.

    \b
    EXAMPLES:
      $ gmail groups validate
      $ gmail groups validate team
      $ gmail groups validate #team
    """
    try:
        # Normalize group name if provided (accept # prefix)
        if name:
            name = normalize_group_name(name)

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

        # Parse output format
        format_enum = parse_output_format(output_format, console)

        errors_found = False
        validation_results = []

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

            # Store result
            validation_results.append({
                "group": group_name,
                "valid": len(group_errors) == 0,
                "errors": group_errors
            })

            # Report (rich format)
            if format_enum == OutputFormat.RICH:
                if group_errors:
                    console.print(f"[red]✗ #{group_name}:[/red]")
                    for error in group_errors:
                        console.print(f"  - {error}")
                    errors_found = True
                else:
                    console.print(f"[green]✅ #{group_name}[/green]")

        if format_enum == OutputFormat.JSON:
            console.print_json(data=validation_results)
            # Set errors_found based on validation results
            errors_found = any(not r["valid"] for r in validation_results)
        else:  # RICH
            if errors_found:
                console.print(f"\n[red]Validation failed[/red]")
                console.print(f"Fix manually: [cyan]gmail groups edit[/cyan]")
            else:
                if name:
                    console.print(f"\n[green]✅ Group #{name} is valid[/green]")
                else:
                    console.print(f"\n[green]✅ All groups are valid[/green]")

        if errors_found:
            raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]✗ Error validating groups: {e}[/red]")
        raise typer.Exit(code=1)
