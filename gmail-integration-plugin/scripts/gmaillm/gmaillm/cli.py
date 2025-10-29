#!/usr/bin/env python3
"""Command-line interface for gmaillm using Typer."""

import builtins
import json
import os
import re
import subprocess
import yaml
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import typer
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gmaillm import GmailClient, SendEmailRequest
from gmaillm.formatters import RichFormatter

# Initialize Typer app and console
app = typer.Typer(
    name="gmaillm",
    help="Gmail CLI with LLM-friendly operations and progressive disclosure patterns",
    add_completion=True,
    no_args_is_help=True,
)
console = Console()
formatter = RichFormatter(console)

# ============ CONSTANTS ============

# Output format enum
class OutputFormat(str, Enum):
    """Output format for CLI commands."""
    RICH = "rich"  # Rich terminal output (default)
    JSON = "json"  # Raw JSON output

# Preview lengths (kept for status command)
SNIPPET_PREVIEW_LENGTH = 80
MESSAGE_ID_DISPLAY_LENGTH = 8

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Label validation
MAX_LABEL_NAME_LENGTH = 225
INVALID_LABEL_CHARS = r'[<>&"\'`]'

# Style validation
STYLE_NAME_MIN_LENGTH = 3
STYLE_NAME_MAX_LENGTH = 50
STYLE_DESC_MIN_LENGTH = 30
STYLE_DESC_MAX_LENGTH = 200
INVALID_STYLE_CHARS = r'[/\\<>&"\'\`\s]'  # No slashes, spaces, or special chars
RESERVED_STYLE_NAMES = {'default', 'template', 'base', 'system'}
REQUIRED_STYLE_SECTIONS = ['examples', 'greeting', 'body', 'closing', 'do', 'dont']
STYLE_SECTION_ORDER = ['examples', 'greeting', 'body', 'closing', 'do', 'dont']
MIN_EXAMPLES = 1
MAX_EXAMPLES = 3
MIN_DO_ITEMS = 2
MIN_DONT_ITEMS = 2


# ============ CONFIG HELPERS ============


def get_plugin_config_dir() -> Path:
    """Get the plugin config directory path.

    Uses CLAUDE_PLUGIN_ROOT environment variable when available (set by Claude Code),
    otherwise falls back to relative path for development.
    """
    # Primary: Use CLAUDE_PLUGIN_ROOT environment variable (set by Claude Code)
    plugin_root = os.getenv("CLAUDE_PLUGIN_ROOT")
    if plugin_root:
        return Path(plugin_root) / "config"

    # Fallback: Use relative path (for development/testing)
    cli_dir = Path(__file__).parent.resolve()
    plugin_dir = cli_dir.parent.parent.parent
    return plugin_dir / "config"


def load_json_config(file_path: Path) -> Dict[str, Any]:
    """Load JSON config file with error handling.

    Args:
        file_path: Path to JSON config file

    Returns:
        Dictionary containing config data, or empty dict on error
    """
    try:
        with open(file_path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except (OSError, json.JSONDecodeError) as e:
        console.print(f"[yellow]Warning: Could not load {file_path}: {e}[/yellow]")
        return {}


def load_email_groups(groups_file: Optional[Path] = None) -> Dict[str, List[str]]:
    """Load email distribution groups from config.

    Args:
        groups_file: Optional path to groups file (for testing)

    Returns:
        Dictionary mapping group names to email lists
    """
    if groups_file is None:
        config_dir = get_plugin_config_dir()
        groups_file = config_dir / "email-groups.json"

    groups = load_json_config(groups_file)
    # Filter out metadata/comment keys
    return {k: v for k, v in groups.items() if not k.startswith("_")}


def expand_email_groups(recipients: List[str], groups: Optional[Dict[str, List[str]]] = None) -> List[str]:
    """Expand #groupname references to actual email addresses.

    Args:
        recipients: List of email addresses or #group references
        groups: Optional groups dict (for testing), loads from config if None

    Returns:
        Expanded list with all #group references resolved (duplicates removed)
    """
    if groups is None:
        groups = load_email_groups()

    expanded = []
    seen = set()

    for recipient in recipients:
        if recipient.startswith("#"):
            # This is a group reference
            group_name = recipient[1:]  # Remove # prefix
            if group_name in groups:
                for email in groups[group_name]:
                    if email not in seen:
                        expanded.append(email)
                        seen.add(email)
            else:
                available = ", ".join("#" + k for k in groups.keys())
                console.print(
                    f"[yellow]Warning: Unknown group '#{group_name}', available: {available}[/yellow]"
                )
                if recipient not in seen:
                    expanded.append(recipient)  # Keep as-is if group not found
                    seen.add(recipient)
        else:
            if recipient not in seen:
                expanded.append(recipient)
                seen.add(recipient)

    return expanded


def get_styles_dir() -> Path:
    """Get the email styles directory path.

    Returns:
        Path to email styles directory
    """
    config_dir = get_plugin_config_dir()
    styles_dir = config_dir / "email-styles"
    styles_dir.mkdir(exist_ok=True, mode=0o755)
    return styles_dir


def get_style_file_path(name: str) -> Path:
    """Get path to a specific style file.

    Args:
        name: Style name

    Returns:
        Path to style file
    """
    styles_dir = get_styles_dir()
    return styles_dir / f"{name}.md"


def load_all_styles(styles_dir: Path) -> List[Dict[str, Any]]:
    """Load all style files and extract metadata.

    Args:
        styles_dir: Directory containing style files

    Returns:
        List of style metadata dictionaries
    """
    styles = []
    for style_file in styles_dir.glob("*.md"):
        try:
            metadata = extract_style_metadata(style_file)
            styles.append({
                'name': style_file.stem,
                'description': metadata.get('description', 'No description'),
                'path': style_file,
            })
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load {style_file}: {e}[/yellow]")
    return sorted(styles, key=lambda x: x['name'])


def extract_style_metadata(style_file: Path) -> Dict[str, str]:
    """Extract YAML frontmatter metadata from style file.

    Args:
        style_file: Path to style file

    Returns:
        Dictionary of metadata fields
    """
    content = style_file.read_text()

    # Check for YAML frontmatter
    if content.startswith('---'):
        try:
            end_idx = content.index('\n---\n', 3)
            frontmatter = content[3:end_idx]
            return yaml.safe_load(frontmatter)
        except Exception:
            pass

    # Fallback: minimal metadata
    return {'name': style_file.stem, 'description': 'No description'}


def create_backup(file_path: Path) -> Path:
    """Create timestamped backup of file.

    Args:
        file_path: Path to file to backup

    Returns:
        Path to backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.parent / f"{file_path.stem}.backup.{timestamp}{file_path.suffix}"
    backup_path.write_text(file_path.read_text())
    return backup_path


def create_style_from_template(name: str, output_path: Path) -> None:
    """Create new style file from default template.

    Args:
        name: Name of the style
        output_path: Path where style file should be created
    """
    template = """---
name: "{name}"
description: "When to use: [Describe the context and recipients for this style]. [Characteristics of this style]."
---

<examples>
Hi [Name],

[Example email body goes here]

Best,
Warren
---
[Optional second example]
</examples>

<greeting>
- "Hi [Name],"
- "Hello [Name],"
</greeting>

<body>
- Keep sentences clear and concise
- Use active voice
- Organize with paragraphs or bullet points
</body>

<closing>
- "Best,"
- "Thank you,"
</closing>

<do>
- Be direct about requests
- Use appropriate formality for recipient
- Proofread before sending
</do>

<dont>
- Use overly casual language inappropriately
- Write excessively long paragraphs
- Forget to include next steps or action items
</dont>
"""
    output_path.write_text(template.format(name=name))


# ============ VALIDATION HELPERS ============


def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    return bool(EMAIL_REGEX.match(email))


def validate_email_list(emails: List[str], field_name: str = "email") -> None:
    """Validate list of email addresses.

    Args:
        emails: List of email addresses to validate
        field_name: Name of field for error messages

    Raises:
        typer.Exit: If any email is invalid
    """
    for email in emails:
        if not email.startswith("#") and not validate_email(email):
            console.print(f"[red]Error: Invalid {field_name} address: {email}[/red]")
            raise typer.Exit(code=1)


def validate_attachment_paths(attachments: Optional[List[str]]) -> Optional[List[str]]:
    """Validate and resolve attachment file paths.

    Args:
        attachments: List of file paths to validate

    Returns:
        List of validated absolute paths, or None if no attachments

    Raises:
        typer.Exit: If any path is invalid
    """
    if not attachments:
        return None

    validated = []
    for path in attachments:
        file_path = Path(path).resolve()
        if not file_path.exists():
            console.print(f"[red]Attachment not found: {path}[/red]")
            raise typer.Exit(code=1)
        if not file_path.is_file():
            console.print(f"[red]Not a file: {path}[/red]")
            raise typer.Exit(code=1)
        validated.append(str(file_path))
    return validated


def validate_label_name(name: str) -> None:
    """Validate label name according to Gmail constraints.

    Args:
        name: Label name to validate

    Raises:
        typer.Exit: If label name is invalid
    """
    if len(name) == 0:
        console.print("[red]Error: Label name cannot be empty[/red]")
        raise typer.Exit(code=1)

    if len(name) > MAX_LABEL_NAME_LENGTH:
        console.print(
            f"[red]Error: Label name too long (max {MAX_LABEL_NAME_LENGTH} characters)[/red]"
        )
        raise typer.Exit(code=1)

    if re.search(INVALID_LABEL_CHARS, name):
        console.print(f"[red]Error: Label name contains invalid characters: {INVALID_LABEL_CHARS}[/red]")
        raise typer.Exit(code=1)


def validate_editor(editor: str) -> None:
    """Validate editor command for security.

    Args:
        editor: Editor command to validate

    Raises:
        typer.Exit: If editor contains dangerous characters
    """
    if any(c in editor for c in [" ", ";", "|", "&", "$", "`"]):
        console.print("[red]Error: EDITOR contains invalid characters[/red]")
        raise typer.Exit(code=1)


def validate_style_name(name: str) -> None:
    """Validate style name for file system safety.

    Args:
        name: Style name to validate

    Raises:
        typer.Exit: If style name is invalid
    """
    if len(name) == 0:
        console.print("[red]Error: Style name cannot be empty[/red]")
        raise typer.Exit(code=1)

    if len(name) < STYLE_NAME_MIN_LENGTH:
        console.print(f"[red]Error: Style name too short (min {STYLE_NAME_MIN_LENGTH} characters)[/red]")
        raise typer.Exit(code=1)

    if len(name) > STYLE_NAME_MAX_LENGTH:
        console.print(f"[red]Error: Style name too long (max {STYLE_NAME_MAX_LENGTH} characters)[/red]")
        raise typer.Exit(code=1)

    if re.search(INVALID_STYLE_CHARS, name):
        console.print("[red]Error: Style name contains invalid characters (no spaces or special chars)[/red]")
        raise typer.Exit(code=1)

    if name.lower() in RESERVED_STYLE_NAMES:
        console.print(f"[red]Error: '{name}' is a reserved name[/red]")
        raise typer.Exit(code=1)


@dataclass
class StyleLintError:
    """Represents a style validation error."""
    section: str
    message: str
    line: Optional[int] = None

    def __str__(self) -> str:
        """Format error message."""
        if self.line:
            return f"[{self.section}] Line {self.line}: {self.message}"
        return f"[{self.section}] {self.message}"


class StyleLinter:
    """Linter for email style files with strict XML format validation."""

    def lint(self, content: str) -> List[StyleLintError]:
        """Run all linting checks on style content.

        Args:
            content: Style file content to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # 1. Check YAML frontmatter
        errors.extend(self._lint_frontmatter(content))

        # 2. Check XML sections exist
        errors.extend(self._lint_sections_exist(content))

        # 3. Check XML sections order
        errors.extend(self._lint_sections_order(content))

        # 4. Check section content
        errors.extend(self._lint_section_content(content))

        # 5. Check formatting
        errors.extend(self._lint_formatting(content))

        return errors

    def lint_and_fix(self, content: str) -> Tuple[str, List[StyleLintError]]:
        """Run linting and auto-fix formatting issues.

        Args:
            content: Style file content to validate and fix

        Returns:
            Tuple of (fixed_content, remaining_errors)
        """
        fixed_content = content

        # Auto-fix trailing whitespace
        lines = fixed_content.split('\n')
        fixed_lines = [line.rstrip() for line in lines]
        fixed_content = '\n'.join(fixed_lines)

        # Auto-fix list item spacing
        fixed_content = re.sub(r'^-([^ ])', r'- \1', fixed_content, flags=re.MULTILINE)

        # Run lint on fixed content
        errors = self.lint(fixed_content)

        # Filter out errors that were fixed
        remaining_errors = [
            err for err in errors
            if 'trailing whitespace' not in err.message.lower()
            and 'list syntax' not in err.message.lower()
        ]

        return fixed_content, remaining_errors

    def _lint_frontmatter(self, content: str) -> List[StyleLintError]:
        """Validate YAML frontmatter."""
        errors = []

        if not content.startswith('---'):
            errors.append(StyleLintError('frontmatter', 'Missing YAML frontmatter'))
            return errors

        try:
            end_idx = content.index('\n---\n', 3)
            frontmatter_text = content[3:end_idx]

            metadata = yaml.safe_load(frontmatter_text)

            # Check required fields
            if 'name' not in metadata:
                errors.append(StyleLintError('frontmatter', 'Missing "name" field'))
            else:
                name = metadata['name']
                if len(name) < STYLE_NAME_MIN_LENGTH:
                    errors.append(StyleLintError('frontmatter', f'Name too short (min {STYLE_NAME_MIN_LENGTH} chars)'))
                if len(name) > STYLE_NAME_MAX_LENGTH:
                    errors.append(StyleLintError('frontmatter', f'Name too long (max {STYLE_NAME_MAX_LENGTH} chars)'))

            if 'description' not in metadata:
                errors.append(StyleLintError('frontmatter', 'Missing "description" field'))
            else:
                desc = metadata['description']
                if not desc.startswith('When to use:'):
                    errors.append(StyleLintError('frontmatter', 'Description must start with "When to use:"'))
                if len(desc) < STYLE_DESC_MIN_LENGTH:
                    errors.append(StyleLintError('frontmatter', f'Description too short (min {STYLE_DESC_MIN_LENGTH} chars)'))
                if len(desc) > STYLE_DESC_MAX_LENGTH:
                    errors.append(StyleLintError('frontmatter', f'Description too long (max {STYLE_DESC_MAX_LENGTH} chars)'))

            # Check for extra fields
            allowed_fields = {'name', 'description'}
            extra_fields = set(metadata.keys()) - allowed_fields
            if extra_fields:
                errors.append(StyleLintError('frontmatter', f'Unexpected fields: {", ".join(extra_fields)}'))

        except ValueError:
            errors.append(StyleLintError('frontmatter', 'Invalid YAML frontmatter (missing closing ---)'))
        except yaml.YAMLError as e:
            errors.append(StyleLintError('frontmatter', f'Invalid YAML syntax: {e}'))

        return errors

    def _lint_sections_exist(self, content: str) -> List[StyleLintError]:
        """Check that all required sections exist."""
        errors = []

        for section in REQUIRED_STYLE_SECTIONS:
            if f'<{section}>' not in content:
                errors.append(StyleLintError(section, f'Missing required section: <{section}>'))
            elif f'</{section}>' not in content:
                errors.append(StyleLintError(section, f'Section not properly closed: <{section}>'))

        return errors

    def _lint_sections_order(self, content: str) -> List[StyleLintError]:
        """Check that sections appear in correct order (STRICT)."""
        errors = []

        section_positions = {}
        for section in REQUIRED_STYLE_SECTIONS:
            match = re.search(f'<{section}>', content)
            if match:
                section_positions[section] = match.start()

        # Check STRICT order
        prev_pos = -1
        for section in STYLE_SECTION_ORDER:
            if section in section_positions:
                pos = section_positions[section]
                if pos < prev_pos:
                    errors.append(StyleLintError(section, f'Section <{section}> out of order (must follow {STYLE_SECTION_ORDER})'))
                prev_pos = pos

        return errors

    def _lint_section_content(self, content: str) -> List[StyleLintError]:
        """Validate content within each section."""
        errors = []

        for section in REQUIRED_STYLE_SECTIONS:
            section_content = self._extract_section_content(content, section)
            if section_content is None:
                continue  # Already caught by _lint_sections_exist

            if not section_content.strip():
                errors.append(StyleLintError(section, f'Section <{section}> is empty'))
                continue

            # Section-specific validation
            if section == 'examples':
                examples = [ex.strip() for ex in section_content.split('---') if ex.strip()]
                if len(examples) < MIN_EXAMPLES:
                    errors.append(StyleLintError(section, f'Must have at least {MIN_EXAMPLES} example(s)'))
                if len(examples) > MAX_EXAMPLES:
                    errors.append(StyleLintError(section, f'Too many examples (max {MAX_EXAMPLES})'))

            elif section in ['greeting', 'body', 'closing', 'do', 'dont']:
                lines = [line for line in section_content.split('\n') if line.strip()]
                list_items = [line for line in lines if line.strip().startswith('-')]

                if len(list_items) == 0:
                    errors.append(StyleLintError(section, f'Section <{section}> must contain list items'))

                if section in ['do', 'dont'] and len(list_items) < 2:
                    min_items = MIN_DO_ITEMS if section == 'do' else MIN_DONT_ITEMS
                    errors.append(StyleLintError(section, f'Section <{section}> must have at least {min_items} items'))

                # Check list formatting
                for i, line in enumerate(lines):
                    if line.strip().startswith('-'):
                        if not line.startswith('- '):
                            errors.append(StyleLintError(section, f'Invalid list syntax (use "- " with space)', line=i+1))

        return errors

    def _extract_section_content(self, content: str, section: str) -> Optional[str]:
        """Extract content between <section> and </section>."""
        match = re.search(f'<{section}>(.*?)</{section}>', content, re.DOTALL)
        if match:
            return match.group(1)
        return None

    def _lint_formatting(self, content: str) -> List[StyleLintError]:
        """Check general formatting issues."""
        errors = []

        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Check trailing whitespace
            if line != line.rstrip():
                errors.append(StyleLintError('formatting', f'Trailing whitespace', line=i+1))

        return errors


# ============ HELPER FUNCTIONS ============


def _get_folder_by_name(folders: List[Any], folder_name: str) -> Optional[Any]:
    """Get folder by name from list.

    Args:
        folders: List of folder objects
        folder_name: Name to search for

    Returns:
        Folder object or None if not found
    """
    return next((f for f in folders if f.name == folder_name), None)


# ============ MAIN COMMANDS ============


@app.command()
def verify() -> None:
    """Verify authentication and setup."""
    try:
        client = GmailClient()
        result = client.verify_setup()

        console.print("=" * 60)
        console.print("gmaillm Setup Verification")
        console.print("=" * 60)

        if result["auth"]:
            console.print("[green]✓[/green] Authentication: Working")
            if result["email_address"]:
                console.print(f"[green]✓[/green] Authenticated as: {result['email_address']}")
        else:
            console.print("[red]✗[/red] Authentication: Failed")

        console.print(f"[green]✓[/green] Folders accessible: {result['folders']}")

        if result["inbox_accessible"]:
            console.print("[green]✓[/green] Inbox: Accessible")
        else:
            console.print("[red]✗[/red] Inbox: Not accessible")

        if result["errors"]:
            console.print("\n[red]Errors:[/red]")
            for error in result["errors"]:
                console.print(f"  - {error}")
        else:
            console.print("\n[green]✅ All checks passed![/green]")

    except Exception as e:
        console.print(f"[red]✗ Setup verification failed: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def setup_auth(
    oauth_keys: Optional[str] = typer.Option(
        None, "--oauth-keys", help="Path to OAuth2 client secrets (gcp-oauth.keys.json)"
    ),
    credentials: Optional[str] = typer.Option(
        None,
        "--credentials",
        help="Path to save credentials (default: ~/.gmail-mcp/credentials.json)",
    ),
    port: int = typer.Option(8080, "--port", help="Local server port for OAuth callback"),
) -> None:
    """Set up Gmail API authentication via OAuth2."""
    try:
        from gmaillm.setup_auth import setup_authentication

        console.print("=" * 70)
        console.print("  Gmail API Authentication Setup")
        console.print("=" * 70)
        console.print()

        result = setup_authentication(
            oauth_keys_file=oauth_keys,
            credentials_file=credentials,
            port=port,
        )

        if result is None:
            console.print(
                "\n[yellow]⚠️  Setup incomplete. Please address the issues above.[/yellow]"
            )
            raise typer.Exit(code=1)
        else:
            console.print("\n[green]✅ Setup complete![/green]")
            console.print("\nYou can now use the Gmail CLI and Python library.")
            console.print("\nVerify with: [cyan]gmail verify[/cyan]")

            console.print("\n" + "=" * 70)
            console.print("📊 Next Steps (Optional)")
            console.print("=" * 70)
            console.print("\n💡 Install shell completions for faster typing:")
            console.print("   [cyan]$ gmail --install-completion[/cyan]")
            console.print("\nThen restart your shell to enable tab-completion:")
            console.print("   [cyan]$ exec $SHELL[/cyan]\n")

    except Exception as e:
        console.print(f"\n[red]✗ Authentication failed: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def status() -> None:
    """Show current Gmail account status with beautiful formatting."""
    try:
        client = GmailClient()

        # Verify authentication
        result = client.verify_setup()

        if not result["auth"] or not result["email_address"]:
            console.print(
                Panel(
                    "[red]✗ Not authenticated[/red]\n\n"
                    + "\n".join(f"  - {error}" for error in result["errors"]),
                    title="Authentication Failed",
                    border_style="red",
                )
            )
            raise typer.Exit(code=1)

        # Account header
        console.print(
            Panel(
                f"[bold cyan]{result['email_address']}[/bold cyan]",
                title="📧 Gmail Account",
                border_style="cyan",
            )
        )

        # Get folder statistics and display
        folders = client.get_folders()
        stats_table = formatter.build_folder_stats_table(folders)
        console.print(Panel(stats_table, title="📊 Folder Statistics", border_style="blue"))

        # Get most recent email (the "current" email)
        try:
            recent_emails = client.list_emails(folder="INBOX", max_results=1)
            if recent_emails.emails:
                recent = recent_emails.emails[0]

                # Format recent email display
                from_display = f"{recent.from_.name or recent.from_.email}"
                date_display = recent.date.strftime("%Y-%m-%d %H:%M")

                recent_info = f"""[bold]From:[/bold] {from_display}
[bold]Subject:[/bold] {recent.subject}
[bold]Date:[/bold] {date_display}
[bold]Preview:[/bold] {recent.snippet[:SNIPPET_PREVIEW_LENGTH]}..."""

                if recent.is_unread:
                    recent_info = "🔵 [bold yellow]UNREAD[/bold yellow]\n\n" + recent_info

                console.print(
                    Panel(
                        recent_info,
                        title=f"📬 Most Recent Email (ID: {recent.message_id[:MESSAGE_ID_DISPLAY_LENGTH]}...)",
                        border_style="green",
                    )
                )
        except Exception as e:
            console.print(f"[dim]Could not fetch recent email: {e}[/dim]")

        # Quick stats summary
        total_labels = len(folders)
        user_labels = len([f for f in folders if f.type == "user"])
        system_labels = len([f for f in folders if f.type == "system"])

        summary_items = [
            f"[cyan]Total Labels:[/cyan] {total_labels}",
            f"[blue]Custom:[/blue] {user_labels}",
            f"[magenta]System:[/magenta] {system_labels}",
        ]

        console.print("\n" + " | ".join(summary_items))

        # Unread indicator
        inbox_folder = _get_folder_by_name(folders, "INBOX")
        if inbox_folder and inbox_folder.unread_count and inbox_folder.unread_count > 0:
            console.print(
                f"\n[bold yellow]⚠️  You have {inbox_folder.unread_count} unread message(s)[/bold yellow]"
            )
        else:
            console.print("\n[green]✓ All caught up![/green]")

    except Exception as e:
        console.print(f"[red]✗ Failed to get status: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def list(
    folder: str = typer.Option("INBOX", "--folder", help="Folder to list from"),
    max: int = typer.Option(10, "--max", "-n", help="Maximum results"),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Optional search query"),
    format: OutputFormat = typer.Option(OutputFormat.RICH, "--format", help="Output format"),
) -> None:
    """List emails from a folder."""
    try:
        client = GmailClient()
        result = client.list_emails(folder=folder, max_results=max, query=query)

        if format == OutputFormat.JSON:
            console.print_json(data=result.model_dump(mode='json'))
        else:  # RICH
            formatter.print_email_list(result.emails, folder)
    except Exception as e:
        console.print(f"[red]Error listing emails: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def read(
    message_id: str = typer.Argument(..., help="Message ID to read"),
    full: bool = typer.Option(False, "--full", help="Show full email body"),
    format: OutputFormat = typer.Option(OutputFormat.RICH, "--format", help="Output format"),
) -> None:
    """Read a specific email."""
    try:
        client = GmailClient()
        format_type = "full" if full else "summary"
        email = client.read_email(message_id, format=format_type)

        if format == OutputFormat.JSON:
            console.print_json(data=email.model_dump(mode='json'))
        else:  # RICH
            formatter.print_email_full(email)
    except Exception as e:
        console.print(f"[red]Error reading email: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def thread(
    message_id: str = typer.Argument(..., help="Message ID in the thread"),
) -> None:
    """Show entire email thread."""
    try:
        client = GmailClient()
        thread = client.get_thread(message_id)
        formatter.print_thread(thread, message_id)

    except Exception as e:
        console.print(f"[red]Error getting thread: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Gmail search query"),
    folder: str = typer.Option("INBOX", "--folder", help="Folder to search in"),
    max: int = typer.Option(10, "--max", "-n", help="Maximum results"),
    format: OutputFormat = typer.Option(OutputFormat.RICH, "--format", help="Output format"),
) -> None:
    """Search emails."""
    try:
        client = GmailClient()
        result = client.search_emails(query=query, folder=folder, max_results=max)

        if format == OutputFormat.JSON:
            console.print_json(data=result.model_dump(mode='json'))
        else:  # RICH
            formatter.print_search_results(result)
    except Exception as e:
        console.print(f"[red]Error searching emails: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def reply(
    message_id: str = typer.Argument(..., help="Message ID to reply to"),
    body: str = typer.Option(..., "--body", help="Reply body text"),
    reply_all: bool = typer.Option(False, "--reply-all", help="Reply to all recipients"),
) -> None:
    """Reply to an email."""
    try:
        client = GmailClient()

        # Get original email for context
        original = client.read_email(message_id, format="summary")

        # Show preview
        console.print("=" * 60)
        console.print("Reply Preview")
        console.print("=" * 60)
        console.print(f"To: {original.from_.email}")
        console.print(f"Subject: Re: {original.subject}")
        console.print(f"\n{body}")
        console.print("=" * 60)

        # Confirm
        response = typer.confirm("\nSend this reply?")
        if not response:
            console.print("Cancelled.")
            return

        # Send reply
        result = client.reply_email(message_id=message_id, body=body, reply_all=reply_all)

        console.print(f"\n[green]✅ Reply sent! Message ID: {result.message_id}[/green]")

    except Exception as e:
        console.print(f"[red]Error sending reply: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def send(
    to: List[str] = typer.Option(..., "--to", "-t", help="Recipient email(s)"),
    subject: str = typer.Option(..., "--subject", "-s", help="Email subject"),
    body: str = typer.Option(..., "--body", "-b", help="Email body"),
    cc: Optional[List[str]] = typer.Option(None, "--cc", help="CC recipient(s)"),
    attachments: Optional[List[str]] = typer.Option(
        None, "--attachment", "-a", help="Attachment file path(s)"
    ),
    yolo: bool = typer.Option(False, "--yolo", help="Send without confirmation"),
) -> None:
    """Send a new email."""
    try:
        client = GmailClient()

        # Validate email addresses
        validate_email_list(to, "recipient")
        if cc:
            validate_email_list(cc, "CC")

        # Validate attachments
        validated_attachments = validate_attachment_paths(attachments)

        # Expand email groups (@groupname -> actual emails)
        to_list = expand_email_groups(to)
        cc_list = expand_email_groups(cc) if cc else None

        # Show preview
        console.print("=" * 60)
        console.print("Email Preview")
        console.print("=" * 60)
        console.print(f"To: {', '.join(to_list)}")
        if cc_list:
            console.print(f"Cc: {', '.join(cc_list)}")
        console.print(f"Subject: {subject}")
        console.print(f"\n{body}")
        if validated_attachments:
            console.print(f"\nAttachments: {len(validated_attachments)} file(s)")
            for att in validated_attachments:
                console.print(f"  - {att}")
        console.print("=" * 60)

        # Confirm unless yolo
        if not yolo:
            response = typer.confirm("\nSend this email?")
            if not response:
                console.print("Cancelled.")
                return
        else:
            console.print("\n[yellow]YOLO mode: Sending without confirmation...[/yellow]")

        # Send email
        request = SendEmailRequest(
            to=to_list, subject=subject, body=body, cc=cc_list, attachments=validated_attachments
        )
        result = client.send_email(request)

        console.print(f"\n[green]✅ Email sent! Message ID: {result.message_id}[/green]")

    except Exception as e:
        console.print(f"[red]Error sending email: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def folders() -> None:
    """List available folders/labels."""
    try:
        client = GmailClient()
        folders = client.get_folders()
        formatter.print_folder_list(folders, "Available Folders")

    except Exception as e:
        console.print(f"[red]Error listing folders: {e}[/red]")
        raise typer.Exit(code=1)


# ============ LABEL SUBCOMMANDS ============

label_app = typer.Typer(help="Manage Gmail labels")
app.add_typer(label_app, name="label")


@label_app.command("create")
def label_create(
    name: str = typer.Argument(..., help="Name of the label to create"),
) -> None:
    """Create a new label/folder."""
    try:
        # Validate label name
        validate_label_name(name)

        client = GmailClient()

        # Show preview
        console.print("=" * 60)
        console.print("Creating Label")
        console.print("=" * 60)
        console.print(f"Name: {name}")
        console.print("=" * 60)

        # Confirm
        response = typer.confirm("\nCreate this label?")
        if not response:
            console.print("Cancelled.")
            return

        # Create label
        label = client.create_label(name)

        console.print(f"\n[green]✅ Label created: {label.name}[/green]")
        console.print(f"   ID: {label.id}")

    except Exception as e:
        console.print(f"[red]✗ Error creating label: {e}[/red]")
        raise typer.Exit(code=1)


@label_app.command("list")
def label_list() -> None:
    """List all labels (system and custom)."""
    try:
        client = GmailClient()
        folders = client.get_folders()
        formatter.print_folder_list(folders, "Gmail Labels")

    except Exception as e:
        console.print(f"[red]✗ Error listing labels: {e}[/red]")
        raise typer.Exit(code=1)


# ============ CONFIG SUBCOMMANDS ============

config_app = typer.Typer(help="Manage Gmail integration configuration")
app.add_typer(config_app, name="config")


@config_app.command("edit-style")
def config_edit_style() -> None:
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


@config_app.command("edit-groups")
def config_edit_groups() -> None:
    """Edit email distribution groups."""
    config_dir = get_plugin_config_dir()
    groups_file = config_dir / "email-groups.json"

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


@config_app.command("list-groups")
def config_list_groups() -> None:
    """List all configured email distribution groups."""
    config_dir = get_plugin_config_dir()
    groups_file = config_dir / "email-groups.json"

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


@config_app.command("show")
def config_show() -> None:
    """Show configuration file locations."""
    config_dir = get_plugin_config_dir()
    styles_dir = get_styles_dir()
    groups_file = config_dir / "email-groups.json"
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
    console.print("  [cyan]gmail config edit-groups[/cyan]     # Edit distribution groups")
    console.print("  [cyan]gmail config list-groups[/cyan]     # List all groups")
    console.print("\nOther:")
    console.print("  [cyan]gmail config show[/cyan]            # Show this information")


# ============ STYLES SUBCOMMANDS ============

styles_app = typer.Typer(help="Manage email style templates")
app.add_typer(styles_app, name="styles")


@styles_app.command("list")
def styles_list() -> None:
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


@styles_app.command("show")
def styles_show(
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


@styles_app.command("create")
def styles_create(
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


@styles_app.command("edit")
def styles_edit(
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


@styles_app.command("delete")
def styles_delete(
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


@styles_app.command("validate")
def styles_validate(
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


@styles_app.command("validate-all")
def styles_validate_all(
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


def main() -> None:
    """Run the main CLI application."""
    app()


if __name__ == "__main__":
    main()
