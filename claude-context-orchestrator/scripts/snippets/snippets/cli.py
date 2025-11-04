#!/usr/bin/env python3
"""Command-line interface for snippets CLI using Typer."""

from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from snippets.client import SnippetsClient, SnippetError
from snippets.helpers.cli import HelpfulGroup, confirm_or_force
from snippets.helpers.cli.colors import Colors


# Output format enum
class OutputFormat(str, Enum):
    """Output format for CLI commands."""

    RICH = "rich"  # Rich terminal output (default)
    JSON = "json"  # Raw JSON output


# Initialize Typer app and console
app = typer.Typer(
    name="snippets",
    help="Snippets CLI for managing Claude Code context snippets",
    add_completion=True,
    no_args_is_help=True,
    cls=HelpfulGroup,
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_markup_mode="rich",
)
console = Console()


# ============ HELPER FUNCTIONS ============

def _get_client(
    config_path: Optional[Path] = None,
    snippets_dir: Optional[Path] = None,
    use_base_config: bool = False,
    config_name: Optional[str] = None,
) -> SnippetsClient:
    """Create and return a SnippetsClient instance.

    Args:
        config_path: Path to config file
        snippets_dir: Path to snippets directory
        use_base_config: Whether to use base config
        config_name: Named config to use

    Returns:
        Initialized SnippetsClient

    Raises:
        typer.Exit: If client initialization fails
    """
    try:
        return SnippetsClient(
            config_path=config_path,
            snippets_dir=snippets_dir,
            use_base_config=use_base_config,
            config_name=config_name,
        )
    except SnippetError as e:
        console.print(Colors.error(f"Error initializing client: {e.message}"))
        raise typer.Exit(code=1)


def _display_snippet_table(snippets, show_content: bool = False, show_numbers: bool = False):
    """Display snippets in a rich table.

    Args:
        snippets: List of SnippetInfo objects
        show_content: Whether to show snippet content
        show_numbers: Whether to show selection numbers (for interactive mode)
    """
    if not snippets:
        console.print(Colors.warning("No snippets found."))
        return

    table = Table(title=f"{len(snippets)} Snippet(s)")

    if show_numbers:
        table.add_column("#", style="dim", justify="right", width=3)

    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Pattern", style="yellow")
    table.add_column("Priority", justify="right", style="magenta")

    if show_content:
        table.add_column("Path", style="blue")

    for i, snippet in enumerate(snippets, 1):
        row = []

        if show_numbers:
            row.append(str(i))

        row.extend([
            snippet.name,
            snippet.pattern or "—",
            str(snippet.priority),
        ])

        if show_content:
            row.append(snippet.path)

        table.add_row(*row)

    console.print(table)


# ============ MAIN COMMANDS ============

@app.command()
def list(
    name: Optional[str] = typer.Argument(None, help="Specific snippet name to list"),
    show_content: bool = typer.Option(False, "--content", "-c", help="Show snippet file paths"),
    show_stats: bool = typer.Option(False, "--stats", "-s", help="Show statistics"),
    output_format: OutputFormat = typer.Option(OutputFormat.RICH, "--output-format", help="Output format"),
    config_path: Optional[Path] = typer.Option(None, "--config", help="Path to config file"),
    snippets_dir: Optional[Path] = typer.Option(None, "--snippets-dir", help="Path to snippets directory"),
    use_base_config: bool = typer.Option(False, "--use-base-config", help="Use base config instead of local"),
    config_name: Optional[str] = typer.Option(None, "--config-name", help="Named config to use"),
) -> None:
    """List all snippets or a specific snippet.

    [bold cyan]EXAMPLES[/bold cyan]:
      [dim]$[/dim] snippets list
      [dim]$[/dim] snippets list my-snippet
      [dim]$[/dim] snippets list --content
      [dim]$[/dim] snippets list --stats
    """
    try:
        client = _get_client(config_path, snippets_dir, use_base_config, config_name)
        result = client.list_snippets(name=name, show_content=show_content)

        if output_format == OutputFormat.JSON:
            import json
            console.print_json(data=[s.model_dump() for s in result])
        else:  # RICH
            _display_snippet_table(result, show_content=show_content)

            if show_stats:
                total = len(result)
                console.print(f"\n{Colors.info('Statistics:')}")
                console.print(f"  Total snippets: {Colors.highlight(str(total))}")

    except SnippetError as e:
        console.print(Colors.error(f"Error: {e.message}"))
        raise typer.Exit(code=1)


@app.command()
def create(
    name: str = typer.Argument(..., help="Snippet name"),
    pattern: str = typer.Option(..., "--pattern", "-p", help="Regex pattern to trigger snippet"),
    description: str = typer.Option(..., "--description", "-d", help="Brief description"),
    content: Optional[str] = typer.Option(None, "--content", "-c", help="Snippet content (default template used if omitted)"),
    priority: int = typer.Option(0, "--priority", help="Priority for pattern matching"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    output_format: OutputFormat = typer.Option(OutputFormat.RICH, "--output-format", help="Output format"),
    config_path: Optional[Path] = typer.Option(None, "--config", help="Path to config file"),
    snippets_dir: Optional[Path] = typer.Option(None, "--snippets-dir", help="Path to snippets directory"),
    use_base_config: bool = typer.Option(False, "--use-base-config", help="Use base config instead of local"),
    config_name: Optional[str] = typer.Option(None, "--config-name", help="Named config to use"),
) -> None:
    """Create a new snippet.

    [bold cyan]EXAMPLES[/bold cyan]:
      [dim]$[/dim] snippets create my-snippet --pattern "my.*pattern" --description "My snippet"
      [dim]$[/dim] snippets create my-snippet -p "pattern" -d "Description" --content "# Content"
      [dim]$[/dim] snippets create my-snippet -p "pattern" -d "Desc" --priority 50
    """
    try:
        client = _get_client(config_path, snippets_dir, use_base_config, config_name)

        # Show preview
        if not force:
            console.print(Panel(
                f"[cyan]Name:[/cyan] {name}\n"
                f"[cyan]Pattern:[/cyan] {pattern}\n"
                f"[cyan]Description:[/cyan] {description}\n"
                f"[cyan]Priority:[/cyan] {priority}\n"
                f"[cyan]Content:[/cyan] {'Default template' if content is None else 'Custom'}",
                title="Creating Snippet",
                border_style="cyan"
            ))

            if not confirm_or_force(force, "Create this snippet?"):
                console.print(Colors.warning("Cancelled."))
                raise typer.Exit(code=0)

        result = client.create(
            name=name,
            pattern=pattern,
            description=description,
            content=content,
            priority=priority,
        )

        if output_format == OutputFormat.JSON:
            console.print_json(data=result.model_dump())
        else:  # RICH
            console.print(Colors.success(f"✓ Created snippet: {result.name}"))
            console.print(f"  Path: {Colors.highlight(result.path)}")
            console.print(f"\n{Colors.info('Next steps:')}")
            console.print("  1. Restart Claude Code to load the new snippet")
            console.print(f"  2. Test with a prompt matching pattern: {Colors.highlight(pattern)}")

    except SnippetError as e:
        console.print(Colors.error(f"Error: {e.message}"))
        raise typer.Exit(code=1)


@app.command()
def update(
    name: str = typer.Argument(..., help="Snippet name to update"),
    pattern: Optional[str] = typer.Option(None, "--pattern", "-p", help="New regex pattern"),
    content: Optional[str] = typer.Option(None, "--content", "-c", help="New snippet content"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    output_format: OutputFormat = typer.Option(OutputFormat.RICH, "--output-format", help="Output format"),
    config_path: Optional[Path] = typer.Option(None, "--config", help="Path to config file"),
    snippets_dir: Optional[Path] = typer.Option(None, "--snippets-dir", help="Path to snippets directory"),
    use_base_config: bool = typer.Option(False, "--use-base-config", help="Use base config instead of local"),
    config_name: Optional[str] = typer.Option(None, "--config-name", help="Named config to use"),
) -> None:
    """Update an existing snippet.

    [bold cyan]EXAMPLES[/bold cyan]:
      [dim]$[/dim] snippets update my-snippet --pattern "new.*pattern"
      [dim]$[/dim] snippets update my-snippet --content "# New content"
      [dim]$[/dim] snippets update my-snippet -p "pattern" -c "content"
    """
    if pattern is None and content is None:
        console.print(Colors.error("Error: Must specify either --pattern or --content"))
        raise typer.Exit(code=1)

    try:
        client = _get_client(config_path, snippets_dir, use_base_config, config_name)

        # Show preview
        if not force:
            updates = []
            if pattern:
                updates.append(f"[cyan]Pattern:[/cyan] {pattern}")
            if content:
                updates.append(f"[cyan]Content:[/cyan] {'<updated>' if content else 'N/A'}")

            console.print(Panel(
                f"[cyan]Snippet:[/cyan] {name}\n" + "\n".join(updates),
                title="Updating Snippet",
                border_style="yellow"
            ))

            if not confirm_or_force(force, "Update this snippet?"):
                console.print(Colors.warning("Cancelled."))
                raise typer.Exit(code=0)

        result = client.update(name=name, pattern=pattern, content=content)

        if output_format == OutputFormat.JSON:
            console.print_json(data=result.model_dump())
        else:  # RICH
            console.print(Colors.success(f"✓ Updated snippet: {result.name}"))
            console.print(f"  Path: {Colors.highlight(result.path)}")

    except SnippetError as e:
        console.print(Colors.error(f"Error: {e.message}"))
        raise typer.Exit(code=1)


@app.command()
def delete(
    name: str = typer.Argument(..., help="Snippet name to delete"),
    backup: bool = typer.Option(True, "--backup/--no-backup", help="Create backup before deleting"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    output_format: OutputFormat = typer.Option(OutputFormat.RICH, "--output-format", help="Output format"),
    config_path: Optional[Path] = typer.Option(None, "--config", help="Path to config file"),
    snippets_dir: Optional[Path] = typer.Option(None, "--snippets-dir", help="Path to snippets directory"),
    use_base_config: bool = typer.Option(False, "--use-base-config", help="Use base config instead of local"),
    config_name: Optional[str] = typer.Option(None, "--config-name", help="Named config to use"),
) -> None:
    """Delete a snippet.

    [bold cyan]EXAMPLES[/bold cyan]:
      [dim]$[/dim] snippets delete my-snippet
      [dim]$[/dim] snippets delete my-snippet --no-backup
      [dim]$[/dim] snippets delete my-snippet --force
    """
    try:
        client = _get_client(config_path, snippets_dir, use_base_config, config_name)

        # Show warning
        if not force:
            console.print(Panel(
                f"[red]⚠ Warning:[/red] This will delete the snippet: [cyan]{name}[/cyan]\n"
                f"Backup: {'Yes' if backup else 'No'}",
                title="Delete Snippet",
                border_style="red"
            ))

            if not confirm_or_force(force, "Delete this snippet?"):
                console.print(Colors.warning("Cancelled."))
                raise typer.Exit(code=0)

        result = client.delete(name=name, force=True, backup=backup)

        if output_format == OutputFormat.JSON:
            import json
            console.print_json(data=result)
        else:  # RICH
            console.print(Colors.success(f"✓ Deleted snippet: {result['name']}"))
            console.print(f"  Deleted {len(result['deleted_files'])} file(s)")

            if result.get('backup_paths'):
                console.print(f"\n{Colors.info('Backups created:')}")
                for backup_path in result['backup_paths']:
                    console.print(f"  {Colors.highlight(backup_path)}")

    except SnippetError as e:
        console.print(Colors.error(f"Error: {e.message}"))
        raise typer.Exit(code=1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactively select and edit snippet"),
    output_format: OutputFormat = typer.Option(OutputFormat.RICH, "--output-format", help="Output format"),
    config_path: Optional[Path] = typer.Option(None, "--config", help="Path to config file"),
    snippets_dir: Optional[Path] = typer.Option(None, "--snippets-dir", help="Path to snippets directory"),
    use_base_config: bool = typer.Option(False, "--use-base-config", help="Use base config instead of local"),
    config_name: Optional[str] = typer.Option(None, "--config-name", help="Named config to use"),
) -> None:
    """Search snippets by keyword.

    [bold cyan]EXAMPLES[/bold cyan]:
      [dim]$[/dim] snippets search mail
      [dim]$[/dim] snippets search "error handling"
      [dim]$[/dim] snippets search mail -i  [dim]# Interactive mode[/dim]
    """
    try:
        client = _get_client(config_path, snippets_dir, use_base_config, config_name)
        result = client.search(query)

        if output_format == OutputFormat.JSON:
            import json
            data = {
                "query": result.query,
                "total_searched": result.total_searched,
                "matches": [s.model_dump() for s in result.matches]
            }
            console.print_json(data=data)
        else:  # RICH
            console.print(f"\n{Colors.info(f'Search results for:')} {Colors.highlight(query)}")
            console.print(f"Searched {result.total_searched} snippet(s)\n")

            if not result.matches:
                console.print(Colors.warning("No snippets found."))
                return

            _display_snippet_table(result.matches, show_numbers=interactive)

            # Interactive mode: prompt user to select and edit
            if interactive:
                console.print()
                choice = typer.prompt(
                    f"{Colors.info('Select snippet to edit')} (1-{len(result.matches)}, or 'q' to quit)",
                    default="q"
                )

                if choice.lower() == 'q':
                    return

                try:
                    index = int(choice) - 1
                    if 0 <= index < len(result.matches):
                        snippet = result.matches[index]
                        import subprocess
                        import os

                        editor = os.environ.get("EDITOR", "vim")
                        console.print(f"\n{Colors.info('Opening')} {Colors.highlight(snippet.path)} {Colors.info('in')} {Colors.highlight(editor)}...")
                        subprocess.run([editor, snippet.path])
                    else:
                        console.print(Colors.error(f"Invalid choice: {choice}"))
                        raise typer.Exit(code=1)
                except ValueError:
                    console.print(Colors.error(f"Invalid choice: {choice}"))
                    raise typer.Exit(code=1)

    except SnippetError as e:
        console.print(Colors.error(f"Error: {e.message}"))
        raise typer.Exit(code=1)


@app.command()
def validate(
    output_format: OutputFormat = typer.Option(OutputFormat.RICH, "--output-format", help="Output format"),
    config_path: Optional[Path] = typer.Option(None, "--config", help="Path to config file"),
    snippets_dir: Optional[Path] = typer.Option(None, "--snippets-dir", help="Path to snippets directory"),
    use_base_config: bool = typer.Option(False, "--use-base-config", help="Use base config instead of local"),
    config_name: Optional[str] = typer.Option(None, "--config-name", help="Named config to use"),
) -> None:
    """Validate snippet configuration.

    [bold cyan]EXAMPLES[/bold cyan]:
      [dim]$[/dim] snippets validate
    """
    try:
        client = _get_client(config_path, snippets_dir, use_base_config, config_name)
        result = client.validate()

        if output_format == OutputFormat.JSON:
            import json
            data = {
                "valid": result.valid,
                "total_mappings": result.total_mappings,
                "errors": [{"type": e.error_type, "message": e.message} for e in result.errors],
                "warnings": [{"type": w.error_type, "message": w.message} for w in result.warnings]
            }
            console.print_json(data=data)
        else:  # RICH
            if result.valid:
                console.print(Colors.success(f"✓ Configuration is valid"))
            else:
                console.print(Colors.error(f"✗ Configuration has errors"))

            console.print(f"  Total mappings: {result.total_mappings}")

            if result.errors:
                console.print(f"\n{Colors.error('Errors:')}")
                for err in result.errors:
                    console.print(f"  [{err.error_type}] {err.message}")

            if result.warnings:
                console.print(f"\n{Colors.warning('Warnings:')}")
                for warn in result.warnings:
                    console.print(f"  [{warn.error_type}] {warn.message}")

            if not result.valid:
                raise typer.Exit(code=1)

    except SnippetError as e:
        console.print(Colors.error(f"Error: {e.message}"))
        raise typer.Exit(code=1)


@app.command(name="show-paths")
def show_paths(
    filter_term: Optional[str] = typer.Argument(None, help="Filter categories by keyword"),
    output_format: OutputFormat = typer.Option(OutputFormat.RICH, "--output-format", help="Output format"),
    config_path: Optional[Path] = typer.Option(None, "--config", help="Path to config file"),
    snippets_dir: Optional[Path] = typer.Option(None, "--snippets-dir", help="Path to snippets directory"),
    use_base_config: bool = typer.Option(False, "--use-base-config", help="Use base config instead of local"),
    config_name: Optional[str] = typer.Option(None, "--config-name", help="Named config to use"),
) -> None:
    """Show available snippet locations and configuration structure.

    [bold cyan]EXAMPLES[/bold cyan]:
      [dim]$[/dim] snippets show-paths
      [dim]$[/dim] snippets show-paths dev
    """
    try:
        client = _get_client(config_path, snippets_dir, use_base_config, config_name)
        result = client.show_paths(filter_term=filter_term)

        if output_format == OutputFormat.JSON:
            import json
            data = {
                "base_dir": result.base_dir,
                "config_files": [
                    {"path": cf.path, "type": cf.type, "priority": cf.priority}
                    for cf in result.config_files
                ],
                "categories": [
                    {"name": cat.name, "path": cat.path, "count": cat.snippet_count}
                    for cat in result.categories
                ]
            }
            console.print_json(data=data)
        else:  # RICH
            console.print(f"\n{Colors.info('Base directory:')} {Colors.highlight(result.base_dir)}\n")

            # Config files table
            config_table = Table(title="Configuration Files")
            config_table.add_column("Type", style="cyan")
            config_table.add_column("Path", style="yellow")
            config_table.add_column("Priority", justify="right", style="magenta")

            for cf in result.config_files:
                config_table.add_row(cf.type, cf.path, str(cf.priority))

            console.print(config_table)
            console.print()

            # Categories table
            if result.categories:
                cat_table = Table(title="Snippet Categories")
                cat_table.add_column("Category", style="cyan")
                cat_table.add_column("Path", style="yellow")
                cat_table.add_column("Count", justify="right", style="magenta")

                for cat in result.categories:
                    cat_table.add_row(cat.name, cat.path, str(cat.snippet_count))

                console.print(cat_table)
            else:
                console.print(Colors.warning("No snippet categories found."))

    except SnippetError as e:
        console.print(Colors.error(f"Error: {e.message}"))
        raise typer.Exit(code=1)


def main() -> None:
    """Main entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
