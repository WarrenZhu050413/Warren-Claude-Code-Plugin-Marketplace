"""Gmail email styles management commands."""

import builtins
import os
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from gmaillm.helpers.config import (
    get_styles_dir,
    get_style_file_path,
    load_all_styles,
    create_backup,
    create_style_from_template
)
from gmaillm.validators.email import validate_editor
from gmaillm.validators.styles import (
    validate_style_name,
    StyleLinter
)

# Initialize Typer app and console
app = typer.Typer(help="Manage email style templates")
console = Console()


@app.command("list")
def list_styles() -> None:
    """List all email styles with name/description."""
    try:
        styles_dir = get_styles_dir()
        styles = load_all_styles(styles_dir)

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

        console.print(f"\n[dim]Total: {len(styles)} style(s)[/dim]")
        console.print(f"\nUsage: [cyan]gmail styles show <name>[/cyan]")

    except Exception as e:
        console.print(f"[red]✗ Error listing styles: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("show")
def show_style(
    name: str = typer.Argument(..., help="Name of the style to show"),
) -> None:
    """Show full style content."""
    try:
        style_file = get_style_file_path(name)

        if not style_file.exists():
            console.print(f"[red]✗ Style '{name}' not found[/red]")
            console.print(f"\nAvailable styles: [cyan]gmail styles list[/cyan]")
            raise typer.Exit(code=1)

        content = style_file.read_text()
        console.print(content)

    except Exception as e:
        console.print(f"[red]✗ Error showing style: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("create")
def create_style(
    name: str = typer.Argument(..., help="Name of the style to create"),
    skip_validation: bool = typer.Option(False, "--skip-validation", help="Skip validation"),
) -> None:
    """Create a new email style from template."""
    try:
        # Validate name
        validate_style_name(name)

        # Check if already exists
        style_file = get_style_file_path(name)
        if style_file.exists():
            console.print(f"[red]✗ Style '{name}' already exists[/red]")
            console.print(f"\nUse: [cyan]gmail styles edit {name}[/cyan]")
            raise typer.Exit(code=1)

        # Show preview
        console.print("=" * 60)
        console.print("Creating Email Style")
        console.print("=" * 60)
        console.print(f"Name: {name}")
        console.print(f"Location: {style_file}")
        console.print("=" * 60)

        # Confirm
        response = typer.confirm("\nCreate this style?")
        if not response:
            console.print("Cancelled.")
            return

        # Create from template
        create_style_from_template(name, style_file)

        # Validate (unless skipped)
        if not skip_validation:
            content = style_file.read_text()
            linter = StyleLinter()
            errors = linter.lint(content)
            if errors:
                console.print("\n[yellow]⚠️  Template created but has validation errors:[/yellow]")
                for error in errors:
                    console.print(f"   {error}")
                console.print(f"\nEdit to fix: [cyan]gmail styles edit {name}[/cyan]")

        # Success feedback
        console.print(f"\n[green]✅ Style created: {name}[/green]")
        console.print(f"   Location: {style_file}")
        console.print(f"\nNext steps:")
        console.print(f"  1. Edit: [cyan]gmail styles edit {name}[/cyan]")
        console.print(f"  2. Validate: [cyan]gmail styles validate {name}[/cyan]")

    except Exception as e:
        console.print(f"[red]✗ Error creating style: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("edit")
def edit_style(
    name: str = typer.Argument(..., help="Name of the style to edit"),
    skip_validation: bool = typer.Option(False, "--skip-validation", help="Skip post-edit validation"),
) -> None:
    """Edit an existing email style."""
    try:
        style_file = get_style_file_path(name)

        # Check if exists
        try:
            with open(style_file):
                pass
        except FileNotFoundError:
            console.print(f"[red]✗ Style '{name}' not found[/red]")
            console.print(f"\nCreate it first: [cyan]gmail styles create {name}[/cyan]")
            raise typer.Exit(code=1)

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
                for error in errors:
                    console.print(f"   {error}")
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
        console.print("=" * 60)
        console.print("Deleting Email Style")
        console.print("=" * 60)
        console.print(f"Name: {name}")
        console.print(f"Location: {style_file}")
        console.print("=" * 60)

        # Confirm unless --force
        if not force:
            response = typer.confirm("\n⚠️  Delete this style? This cannot be undone.")
            if not response:
                console.print("Cancelled.")
                return
        else:
            console.print("\n[yellow]--force: Deleting without confirmation[/yellow]")

        # Create backup before deletion
        backup_path = create_backup(style_file)
        console.print(f"Backup created: {backup_path}")

        # Delete
        style_file.unlink()

        console.print(f"\n[green]✅ Style deleted: {name}[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error deleting style: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("validate")
def validate_style(
    name: str = typer.Argument(..., help="Name of the style to validate"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix formatting issues"),
) -> None:
    """Validate a specific style format."""
    try:
        style_file = get_style_file_path(name)

        if not style_file.exists():
            console.print(f"[red]✗ Style '{name}' not found[/red]")
            raise typer.Exit(code=1)

        content = style_file.read_text()
        linter = StyleLinter()

        if fix:
            # Auto-fix and re-validate
            console.print(f"Fixing {name}...")
            fixed_content, errors = linter.lint_and_fix(content)

            # Save fixed content
            style_file.write_text(fixed_content)
            console.print("[green]✅ Auto-fixed formatting issues[/green]")

            if errors:
                console.print(f"\n[yellow]⚠️  Remaining validation errors:[/yellow]")
                for error in errors:
                    console.print(f"   {error}")
                raise typer.Exit(code=1)
            else:
                console.print(f"\n[green]✅ Style '{name}' is now valid[/green]")
        else:
            # Just validate
            errors = linter.lint(content)

            if errors:
                console.print(f"[red]✗ Style '{name}' has validation errors:[/red]")
                for error in errors:
                    console.print(f"   {error}")
                console.print(f"\nAuto-fix: [cyan]gmail styles validate {name} --fix[/cyan]")
                raise typer.Exit(code=1)
            else:
                console.print(f"[green]✅ Style '{name}' is valid[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error validating style: {e}[/red]")
        raise typer.Exit(code=1)


@app.command("validate-all")
def validate_all_styles(
    fix: bool = typer.Option(False, "--fix", help="Auto-fix formatting issues in all styles"),
) -> None:
    """Validate all style formats."""
    try:
        styles_dir = get_styles_dir()
        styles = builtins.list(styles_dir.glob("*.md"))

        if not styles:
            console.print("[yellow]No styles found[/yellow]")
            return

        console.print(f"Validating {len(styles)} style(s)...\n")

        valid_count = 0
        invalid_count = 0
        linter = StyleLinter()

        for style_file in styles:
            name = style_file.stem
            content = style_file.read_text()

            if fix:
                fixed_content, errors = linter.lint_and_fix(content)
                style_file.write_text(fixed_content)

                if errors:
                    console.print(f"[red]✗ {name}: {len(errors)} error(s) remaining[/red]")
                    for error in errors[:3]:  # Show first 3 errors
                        console.print(f"     {error}")
                    invalid_count += 1
                else:
                    console.print(f"[green]✅ {name} (fixed)[/green]")
                    valid_count += 1
            else:
                errors = linter.lint(content)

                if errors:
                    console.print(f"[red]✗ {name}: {len(errors)} error(s)[/red]")
                    for error in errors[:3]:  # Show first 3 errors
                        console.print(f"     {error}")
                    invalid_count += 1
                else:
                    console.print(f"[green]✅ {name}[/green]")
                    valid_count += 1

        console.print(f"\nResults: [green]{valid_count} valid[/green], [red]{invalid_count} invalid[/red]")

        if invalid_count > 0:
            if not fix:
                console.print(f"\nAuto-fix all: [cyan]gmail styles validate-all --fix[/cyan]")
            raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]✗ Error validating styles: {e}[/red]")
        raise typer.Exit(code=1)
