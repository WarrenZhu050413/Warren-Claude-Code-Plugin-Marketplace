"""Gmail email styles management commands."""

import builtins
import os
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from gmaillm.helpers.core import get_styles_dir, get_style_file_path, create_backup
from gmaillm.helpers.domain import load_all_styles, create_style_from_template
from gmaillm.helpers.cli import (
    HelpfulGroup,
    OutputFormat,
    parse_output_format,
    output_json_or_rich,
    load_and_validate_json,
    display_schema_and_exit,
    show_operation_preview,
    confirm_or_force,
    create_backup_with_message,
    handle_command_error
)
from gmaillm.validators.email import validate_editor
from gmaillm.validators.styles import (
    validate_style_name,
    StyleLinter,
    get_style_json_schema_string,
    create_style_from_json,
    validate_json_against_schema
)

# Initialize Typer app and console
app = typer.Typer(
    help="Manage email style templates",
    cls=HelpfulGroup,  # Show help on missing required args
    context_settings={"help_option_names": ["-h", "--help"]}
)
console = Console()


@app.command("schema")
def show_schema() -> None:
    """Display JSON schema for programmatic style creation.

    This schema defines the structure required for creating styles
    via the --json-input-path flag in the 'create' and 'edit' commands.
    """
    display_schema_and_exit(
        schema_getter=get_style_json_schema_string,
        title="Email Style JSON Schema",
        description="Use this schema for programmatic style creation with --json-input-path",
        usage_example="gmail styles create my-style --json-input-path style.json --force"
    )


@app.command("list")
def list_styles(
    show_paths: bool = typer.Option(
        True,
        "--paths/--no-paths",
        help="Show file paths for each style (default: True)"
    ),
    output_format: str = typer.Option("rich", "--output-format", help="Output format (rich|json)"),
) -> None:
    """List all email styles with name/description."""
    try:
        styles_dir = get_styles_dir()
        styles = load_all_styles(styles_dir)

        # Parse output format
        format_enum = parse_output_format(output_format, console)

        # Prepare JSON data
        styles_json = []
        for style in styles:
            style_data = {
                "name": style['name'],
                "description": style['description']
            }
            if show_paths:
                style_data["path"] = str(get_style_file_path(style['name']))
            styles_json.append(style_data)

        # Define rich output function
        def print_rich():
            console.print("=" * 60)
            console.print(f"Email Styles ({len(styles)})")
            console.print("=" * 60)

            if not styles:
                console.print("\n[yellow]No styles found[/yellow]")
                console.print(f"\nCreate a new style with: [cyan]gmail styles create <name>[/cyan]")
                return

            for style in styles:
                console.print(f"\n📝 [bold]{style['name']}[/bold]")
                console.print(f"   {style['description']}")

                if show_paths:
                    style_path = get_style_file_path(style['name'])
                    console.print(f"   [dim]Path: {style_path}[/dim]")

            console.print(f"\n[dim]Total: {len(styles)} style(s)[/dim]")
            console.print(f"\nUsage: [cyan]gmail styles show <name>[/cyan]")

        # Output in appropriate format
        output_json_or_rich(format_enum, styles_json, print_rich)

    except Exception as e:
        console.print(f"[red]✗ Error listing styles: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("show")
def show_style(
    name: str = typer.Argument(..., help="Name of the style to show"),
    output_format: str = typer.Option("rich", "--output-format", help="Output format (rich|json)"),
) -> None:
    """Show full style content."""
    try:
        style_file = get_style_file_path(name)

        if not style_file.exists():
            console.print(f"[red]✗ Style '{name}' not found[/red]")
            console.print(f"\nAvailable styles: [cyan]gmail styles list[/cyan]")
            raise typer.Exit(code=1)

        content = style_file.read_text()

        # Parse output format
        format_enum = parse_output_format(output_format, console)

        # Prepare JSON data
        style_data = {
            "name": name,
            "path": str(style_file),
            "content": content
        }

        # Output in appropriate format
        output_json_or_rich(format_enum, style_data, lambda: console.print(content))

    except Exception as e:
        console.print(f"[red]✗ Error showing style: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("create")
def create_style(
    name: str = typer.Argument(..., help="Name of the style to create"),
    json_input_path: Optional[str] = typer.Option(
        None,
        "--json-input-path",
        "-j",
        help="Path to JSON file for programmatic creation"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompts and overwrite if exists"
    ),
    skip_validation: bool = typer.Option(False, "--skip-validation", help="Skip validation"),
) -> None:
    """Create a new email style from template or JSON file.

    \b
    MODES:
      1. Interactive (default): Create from template with editor
      2. Programmatic (--json-input-path): Create from JSON file

    \b
    EXAMPLES:
      Interactive creation:
        $ gmail styles create professional-casual

      From JSON file:
        $ gmail styles create my-style --json-input-path style.json --force
        $ gmail styles create my-style -j /path/to/style.json -f

      View schema:
        $ gmail styles schema
    """
    try:
        # Validate name
        validate_style_name(name)

        # Check if already exists
        style_file = get_style_file_path(name)
        if style_file.exists() and not force:
            console.print(f"[red]✗ Style '{name}' already exists[/red]")
            console.print(f"\nUse: [cyan]gmail styles edit {name}[/cyan]")
            console.print(f"Or: [cyan]gmail styles create {name} --force[/cyan] to overwrite")
            raise typer.Exit(code=1)

        # PROGRAMMATIC MODE: JSON input
        if json_input_path:
            console.print("[cyan]Creating style from JSON file...[/cyan]")

            # Load and validate JSON
            json_data = load_and_validate_json(
                json_path_str=json_input_path,
                validator_func=validate_json_against_schema,
                schema_help_command="gmail styles schema"
            )

            # Create backup if overwriting
            if style_file.exists():
                backup_path = create_backup(style_file)
                console.print(f"[yellow]Backup created: {backup_path}[/yellow]")

            # Create from JSON
            try:
                create_style_from_json(json_data, style_file)
            except ValueError as e:
                console.print(f"[red]✗ {e}[/red]")
                console.print("\nView schema: [cyan]gmail styles schema[/cyan]")
                raise typer.Exit(code=1)

            console.print(f"[green]✅ Style created: {name}[/green]")
            console.print(f"   Location: {style_file}")

        # INTERACTIVE MODE: Template-based
        else:
            # Show preview
            show_operation_preview(
                "Creating Email Style",
                {
                    "Name": name,
                    "Location": str(style_file)
                }
            )

            # Confirm (unless --force)
            if not confirm_or_force("\nCreate this style?", force, "Creating without confirmation"):
                console.print("Cancelled.")
                return

            # Create backup if overwriting
            create_backup_with_message(style_file, create_backup)

            # Create from template
            create_style_from_template(name, style_file)

            console.print(f"\n[green]✅ Style created: {name}[/green]")
            console.print(f"   Location: {style_file}")

        # Validate (unless skipped)
        if not skip_validation:
            content = style_file.read_text()
            linter = StyleLinter()
            errors = linter.lint(content)
            if errors:
                console.print("\n[yellow]⚠️  Validation errors found:[/yellow]")
                for error in errors[:5]:  # Show first 5
                    console.print(f"   {error}")
                if len(errors) > 5:
                    console.print(f"   ... and {len(errors) - 5} more")
                console.print(f"\nEdit to fix: [cyan]gmail styles edit {name}[/cyan]")
                console.print(f"Or auto-fix: [cyan]gmail styles validate {name} --fix[/cyan]")
            else:
                console.print(f"[green]✅ Style validated successfully[/green]")

        # Next steps (interactive mode only)
        if not json_input_path:
            console.print(f"\nNext steps:")
            console.print(f"  1. Edit: [cyan]gmail styles edit {name}[/cyan]")
            console.print(f"  2. Validate: [cyan]gmail styles validate {name}[/cyan]")

    except Exception as e:
        console.print(f"[red]✗ Error creating style: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("edit")
def edit_style(
    name: str = typer.Argument(..., help="Name of the style to edit"),
    json_input_path: Optional[str] = typer.Option(
        None,
        "--json-input-path",
        "-j",
        help="Path to JSON file for programmatic editing"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompts (for programmatic use)"
    ),
    skip_validation: bool = typer.Option(False, "--skip-validation", help="Skip post-edit validation"),
) -> None:
    """Edit an existing email style interactively or programmatically.

    \b
    MODES:
      1. Interactive (default): Open style in $EDITOR
      2. Programmatic (--json-input-path): Replace content from JSON file

    \b
    EXAMPLES:
      Interactive editing:
        $ gmail styles edit professional-casual

      Replace from JSON file:
        $ gmail styles edit my-style --json-input-path updated.json --force
        $ gmail styles edit my-style -j /path/to/updated.json -f
    """
    try:
        style_file = get_style_file_path(name)

        # Check if exists
        if not style_file.exists():
            console.print(f"[red]✗ Style '{name}' not found[/red]")
            console.print(f"\nCreate it first: [cyan]gmail styles create {name}[/cyan]")
            raise typer.Exit(code=1)

        # PROGRAMMATIC MODE: JSON input
        if json_input_path:
            console.print("[cyan]Updating style from JSON file...[/cyan]")

            # Create backup
            backup_path = create_backup(style_file)
            console.print(f"Backup created: {backup_path}")

            # Load and validate JSON
            json_data = load_and_validate_json(
                json_path_str=json_input_path,
                validator_func=validate_json_against_schema,
                schema_help_command="gmail styles schema"
            )

            # Replace content
            try:
                create_style_from_json(json_data, style_file)
            except ValueError as e:
                console.print(f"[red]✗ {e}[/red]")
                console.print(f"Restoring from backup: {backup_path}")
                style_file.write_text(backup_path.read_text())
                raise typer.Exit(code=1)

            console.print(f"[green]✅ Style updated: {name}[/green]")

        # INTERACTIVE MODE: Editor
        else:
            # Get editor
            editor = os.environ.get("EDITOR", "vim")
            validate_editor(editor)

            console.print(f"Opening {style_file} in {editor}...")
            subprocess.run([editor, str(style_file)], shell=False)

        # Validate after edit (unless skipped)
        if not skip_validation:
            content = style_file.read_text()
            linter = StyleLinter()
            errors = linter.lint(content)

            if errors:
                console.print("\n[yellow]⚠️  Validation errors found:[/yellow]")
                for error in errors[:5]:
                    console.print(f"   {error}")
                if len(errors) > 5:
                    console.print(f"   ... and {len(errors) - 5} more")
                console.print(f"\nFix errors: [cyan]gmail styles edit {name}[/cyan]")
                console.print(f"Or auto-fix: [cyan]gmail styles validate {name} --fix[/cyan]")
            else:
                console.print(f"\n[green]✅ Style validated successfully[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error editing style: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("delete")
def delete_style(
    name: str = typer.Argument(..., help="Name of the style to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete an email style."""
    try:
        style_file = get_style_file_path(name)

        # Check if exists
        if not style_file.exists():
            console.print(f"[red]✗ Style '{name}' not found[/red]")
            raise typer.Exit(code=1)

        # Show what will be deleted
        show_operation_preview(
            "Deleting Email Style",
            {
                "Name": name,
                "Location": str(style_file)
            }
        )

        # Confirm unless --force
        if not confirm_or_force("\n⚠️  Delete this style? This cannot be undone.", force, "Deleting without confirmation"):
            console.print("Cancelled.")
            return

        # Create backup before deletion
        create_backup_with_message(style_file, create_backup)

        # Delete
        style_file.unlink()

        console.print(f"\n[green]✅ Style deleted: {name}[/green]")

    except Exception as e:
        handle_command_error("deleting style", e)


def _validate_single_style(name: str, style_file: Path, fix: bool, linter: StyleLinter) -> dict:
    """Validate a single style and return result.

    Returns dict with keys: name, valid, errors, fixed (if fix=True)
    """
    content = style_file.read_text()

    if fix:
        fixed_content, errors = linter.lint_and_fix(content)
        style_file.write_text(fixed_content)
        return {
            "name": name,
            "fixed": True,
            "valid": len(errors) == 0,
            "errors": errors
        }
    else:
        errors = linter.lint(content)
        return {
            "name": name,
            "valid": len(errors) == 0,
            "errors": errors
        }


@app.command("validate")
def validate_style(
    name: Optional[str] = typer.Argument(None, help="Name of the style to validate (validates all if not specified)"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix formatting issues"),
    output_format: str = typer.Option("rich", "--output-format", help="Output format (rich|json)"),
) -> None:
    """Validate style format(s).

    If a name is provided, validates that specific style.
    If no name is provided, validates all styles.

    \b
    EXAMPLES:
      $ gmail styles validate professional-casual
      $ gmail styles validate professional-casual --fix
      $ gmail styles validate  # Validates all styles
      $ gmail styles validate --fix  # Auto-fix all styles
    """
    try:
        # Parse output format
        format_enum = parse_output_format(output_format, console)

        linter = StyleLinter()

        # Determine which styles to validate
        if name is None:
            # Validate all styles
            styles_dir = get_styles_dir()
            style_files = builtins.list(styles_dir.glob("*.md"))

            if not style_files:
                console.print("[yellow]No styles found[/yellow]")
                return

            if format_enum == OutputFormat.RICH:
                console.print(f"Validating {len(style_files)} style(s)...\n")

            styles_to_validate = [(f.stem, f) for f in style_files]
        else:
            # Validate specific style
            style_file = get_style_file_path(name)

            if not style_file.exists():
                console.print(f"[red]✗ Style '{name}' not found[/red]")
                raise typer.Exit(code=1)

            styles_to_validate = [(name, style_file)]

        # Validate all selected styles
        results = []
        for style_name, style_path in styles_to_validate:
            result = _validate_single_style(style_name, style_path, fix, linter)
            results.append(result)

        # Output results
        if format_enum == OutputFormat.JSON:
            if len(results) == 1:
                # Single style: output just the result
                console.print_json(data=results[0])
            else:
                # Multiple styles: output summary
                valid_count = sum(1 for r in results if r["valid"])
                invalid_count = len(results) - valid_count
                summary = {
                    "total": len(results),
                    "valid": valid_count,
                    "invalid": invalid_count,
                    "results": results
                }
                console.print_json(data=summary)
        else:  # RICH
            if len(results) == 1:
                # Single style: detailed output
                result = results[0]
                style_name = result["name"]
                errors = result["errors"]

                if fix:
                    console.print(f"Fixing {style_name}...")
                    console.print("[green]✅ Auto-fixed formatting issues[/green]")
                    if errors:
                        console.print(f"\n[yellow]⚠️  Remaining validation errors:[/yellow]")
                        for error in errors:
                            console.print(f"   {error}")
                    else:
                        console.print(f"\n[green]✅ Style '{style_name}' is now valid[/green]")
                else:
                    if errors:
                        console.print(f"[red]✗ Style '{style_name}' has validation errors:[/red]")
                        for error in errors:
                            console.print(f"   {error}")
                        console.print(f"\nAuto-fix: [cyan]gmail styles validate {style_name} --fix[/cyan]")
                    else:
                        console.print(f"[green]✅ Style '{style_name}' is valid[/green]")
            else:
                # Multiple styles: summary output
                for result in results:
                    style_name = result["name"]
                    errors = result["errors"]

                    if errors:
                        error_count = len(errors)
                        status = f"[red]✗ {style_name}: {error_count} error(s)"
                        if fix:
                            status += " remaining"
                        status += "[/red]"
                        console.print(status)
                        for error in errors[:3]:  # Show first 3 errors
                            console.print(f"     {error}")
                    else:
                        status = f"[green]✅ {style_name}"
                        if fix:
                            status += " (fixed)"
                        status += "[/green]"
                        console.print(status)

                # Summary
                valid_count = sum(1 for r in results if r["valid"])
                invalid_count = len(results) - valid_count
                console.print(f"\nResults: [green]{valid_count} valid[/green], [red]{invalid_count} invalid[/red]")

                if invalid_count > 0 and not fix:
                    console.print(f"\nAuto-fix all: [cyan]gmail styles validate --fix[/cyan]")

        # Exit with error if any validation failed
        if any(not r["valid"] for r in results):
            raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]✗ Error validating style: {e}[/red]")
        raise typer.Exit(code=1)
