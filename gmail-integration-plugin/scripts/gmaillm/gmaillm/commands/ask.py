"""Ask command - Natural language email querying.

This command allows users to ask questions about their email history
and get synthesized answers powered by Claude.

Example:
    $ gmail ask "What did Angela say about the meeting?"
    $ gmail ask "Summarize emails from Matt this month"
    $ gmail ask "When is the next deadline?"
"""

from typing import Optional
from enum import Enum

import typer
from rich.console import Console
from rich.panel import Panel

from gmaillm import GmailClient
from gmaillm.agent import ClaudeEmailAgent
from gmaillm.helpers.cli import HelpfulGroup

console = Console()


class OutputFormat(str, Enum):
    """Output format for ask command."""
    RICH = "rich"  # Rich terminal output (default)
    JSON = "json"  # Raw JSON output


app = typer.Typer(
    name="ask",
    help="Ask natural language questions about your email history",
    cls=HelpfulGroup,
    rich_markup_mode="rich",
)


def generate_search_query(question: str, agent: Optional[ClaudeEmailAgent] = None) -> str:
    """Generate Gmail search query from natural language question.

    This is a simple approach that can be enhanced with Claude to generate
    more sophisticated queries.

    Args:
        question: Natural language question
        agent: Optional agent for query generation

    Returns:
        Gmail search query string
    """
    # For now, return a simple search query
    # In future, could use Claude to generate more sophisticated queries
    # that understand intent (who, what, when, where)

    # Simple heuristics:
    question_lower = question.lower()

    # Extract person names (simple pattern)
    if "from" in question_lower or "said" in question_lower:
        # Try to find names - for now just search for content
        words = question.split()
        # Look for potential names (capitalized words)
        names = [w for w in words if w and w[0].isupper()]
        if names:
            return f"from:{names[0].lower()}"

    # Extract time references
    if "last week" in question_lower:
        return "after:2025-10-23"
    if "this month" in question_lower:
        return "after:2025-10-01"
    if "today" in question_lower:
        return "after:2025-10-30"

    # Extract topic keywords
    if "deadline" in question_lower:
        return "deadline"
    if "meeting" in question_lower:
        return "meeting"
    if "project" in question_lower:
        return "project"

    # Default: search in unread or recent
    return "is:unread OR newer_than:1w"


@app.command()
def ask_command(
    question: str = typer.Argument(
        ...,
        help="Your question about email history"
    ),
    folder: str = typer.Option(
        "INBOX",
        "--folder",
        help="Folder to search in"
    ),
    max_results: int = typer.Option(
        10,
        "--max",
        "-n",
        help="Maximum emails to analyze"
    ),
    context: bool = typer.Option(
        False,
        "--context",
        help="Show email context in response"
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.RICH,
        "--output-format",
        help="Output format"
    ),
) -> None:
    """Ask a natural language question about your email history.

    [bold cyan]EXAMPLES[/bold cyan]:
      [dim]$[/dim] gmail ask "What did Angela say about the meeting?"
      [dim]$[/dim] gmail ask "Summarize emails from Matt this month"
      [dim]$[/dim] gmail ask "When is the next deadline?"
      [dim]$[/dim] gmail ask "What's the project status?" --context

    The ask command:
    1. Takes your natural language question
    2. Searches your email history for relevant messages
    3. Uses Claude to synthesize an answer
    4. Shows you the sources and reasoning
    """
    try:
        # Show what we're doing
        console.print(f"\n[cyan]📧 Searching email history...{' (with context)' if context else ''}[/cyan]")

        # Initialize clients
        gmail_client = GmailClient()
        agent = ClaudeEmailAgent(model="sonnet")

        # Generate search query from question
        search_query = generate_search_query(question, agent)

        # Search emails
        console.print(f"[dim]Query: {search_query}[/dim]")
        search_results = gmail_client.search_emails(
            query=search_query,
            folder=folder,
            max_results=max_results
        )

        if not search_results.emails:
            console.print("\n[yellow]No matching emails found.[/yellow]")
            console.print("\nTry:")
            console.print("  - Using different keywords")
            console.print("  - Checking a different folder")
            console.print("  - Being more specific about time period")
            raise typer.Exit(code=0)

        # Show summary of search
        email_count = len(search_results.emails)
        console.print(f"[dim]Found {email_count} email(s) to analyze[/dim]\n")

        # Convert to dict format for agent
        emails_for_agent = [
            {
                "from": e.from_.email,
                "subject": e.subject,
                "body": e.body_plain or e.body_html or ""
            }
            for e in search_results.emails
        ]

        # Have Claude synthesize answer
        with console.status("[bold green]🤖 Synthesizing answer with Claude...", spinner="dots"):
            answer = agent.query(question, emails_for_agent)

        # Display answer
        if output_format == OutputFormat.JSON:
            console.print_json(data={
                "question": question,
                "answer": answer,
                "sources": email_count,
                "folder": folder
            })
        else:  # RICH
            # Show sources
            source_info = f"[dim]Based on {email_count} email(s) from {folder}[/dim]"
            console.print(source_info)

            # Show answer in panel
            console.print(
                Panel(
                    answer,
                    title="📝 Answer",
                    border_style="green"
                )
            )

            # Show email context if requested
            if context:
                console.print("\n[bold cyan]📧 Email Context[/bold cyan]")
                for i, email in enumerate(search_results.emails, 1):
                    console.print(f"\n[dim]Email {i}:[/dim]")
                    console.print(f"[bold]From:[/bold] {email.from_.email}")
                    console.print(f"[bold]Subject:[/bold] {email.subject}")
                    if email.body_plain:
                        snippet = email.body_plain[:200]
                        if len(email.body_plain) > 200:
                            snippet += "..."
                        console.print(f"[dim]{snippet}[/dim]")

            console.print()

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


# Register as subcommand
if __name__ == "__main__":
    app()
