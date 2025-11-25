"""Email validation utilities for gmaillm."""

import re
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

console = Console()

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


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


def validate_label_name(name: str, max_length: int = 225) -> None:
    """Validate label name according to Gmail constraints.

    Args:
        name: Label name to validate
        max_length: Maximum allowed length

    Raises:
        typer.Exit: If label name is invalid
    """
    invalid_chars = r'[<>&"\'`]'

    if len(name) == 0:
        console.print("[red]Error: Label name cannot be empty[/red]")
        raise typer.Exit(code=1)

    if len(name) > max_length:
        console.print(
            f"[red]Error: Label name too long (max {max_length} characters)[/red]"
        )
        raise typer.Exit(code=1)

    if re.search(invalid_chars, name):
        console.print(f"[red]Error: Label name contains invalid characters: {invalid_chars}[/red]")
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
