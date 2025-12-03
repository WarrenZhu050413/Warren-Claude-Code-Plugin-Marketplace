#!/usr/bin/env python3
"""
Process gmail workflow autonomously.

This script demonstrates how to use gmaillm workflows programmatically
to process emails in batches with autonomous decision-making.

Usage:
    python scripts/process_workflow.py <workflow_name> [--dry-run]

Example:
    python scripts/process_workflow.py gmaillm-inbox
    python scripts/process_workflow.py daily-clear --dry-run
"""

import sys
import json
import subprocess
import argparse
from typing import Optional, Dict, Any


def run_gmail_command(*args: str) -> Optional[Dict[str, Any]]:
    """
    Run gmail command and return JSON output.

    Args:
        *args: Command arguments to pass to gmail CLI

    Returns:
        Parsed JSON response or None on error
    """
    # Workflow commands return JSON by default, others need --output-format
    if args[0] == 'workflows' and args[1] in ('start', 'continue'):
        cmd = ['gmail'] + list(args)
    else:
        cmd = ['gmail'] + list(args) + ['--output-format', 'json']

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        print(f"Output: {result.stdout}", file=sys.stderr)
        return None


def determine_action(email: Dict[str, Any]) -> str:
    """
    Determine what action to take on an email.

    This is a simple example - replace with your own logic.

    Args:
        email: Email metadata from workflow

    Returns:
        Action to take: 'archive', 'skip', or 'reply'
    """
    from_addr = email.get('from', '').lower()
    subject = email.get('subject', '').lower()

    # Example rules - customize these for your needs
    if 'newsletter' in from_addr or 'noreply' in from_addr:
        return 'archive'

    if 'urgent' in subject or 'important' in subject:
        return 'skip'  # Review manually

    return 'skip'  # Default: don't take automatic action


def generate_reply(email: Dict[str, Any]) -> str:
    """
    Generate a reply body for an email.

    This is a placeholder - replace with your own logic.

    Args:
        email: Email metadata from workflow

    Returns:
        Reply body text
    """
    # Example: simple auto-reply
    return "Thank you for your email. I'll review this and get back to you soon."


def process_workflow(workflow_name: str, dry_run: bool = False) -> None:
    """
    Process a workflow autonomously.

    Args:
        workflow_name: Name of workflow to run
        dry_run: If True, show actions but don't execute them
    """
    print(f"Starting workflow: {workflow_name}")
    if dry_run:
        print("DRY RUN MODE - No actions will be executed\n")

    # Start workflow
    response = run_gmail_command('workflows', 'start', workflow_name)
    if not response:
        print("Failed to start workflow")
        sys.exit(1)

    token = response.get('token')
    if not token:
        print("No token in response")
        sys.exit(1)

    # Counters
    archived = 0
    replied = 0
    skipped = 0

    # Process each email
    while response and response.get('progress', {}).get('remaining', 0) > 0:
        email = response.get('email', {})
        progress = response.get('progress', {})

        # Show email info
        print(f"\n[{progress.get('current', 0)}/{progress.get('total', 0)}]")
        print(f"From: {email.get('from', 'Unknown')}")
        print(f"Subject: {email.get('subject', 'No subject')}")
        print(f"Date: {email.get('date', 'Unknown')}")

        # Determine action
        action = determine_action(email)
        print(f"Action: {action}")

        if dry_run:
            # In dry run, just skip to next
            response = run_gmail_command('workflows', 'continue', token, 'skip')
            skipped += 1
        else:
            # Execute action
            if action == 'archive':
                response = run_gmail_command('workflows', 'continue', token, 'archive')
                archived += 1
            elif action == 'reply':
                reply_body = generate_reply(email)
                response = run_gmail_command(
                    'workflows', 'continue', token, 'reply',
                    '-b', reply_body
                )
                replied += 1
            else:
                response = run_gmail_command('workflows', 'continue', token, 'skip')
                skipped += 1

    # Summary
    print("\n" + "=" * 50)
    print("Workflow Complete!")
    print(f"Archived: {archived}")
    print(f"Replied: {replied}")
    print(f"Skipped: {skipped}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Process gmail workflow autonomously',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s gmaillm-inbox
  %(prog)s daily-clear --dry-run
        """
    )
    parser.add_argument(
        'workflow_name',
        help='Name of workflow to process'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without executing actions'
    )

    args = parser.parse_args()

    try:
        process_workflow(args.workflow_name, args.dry_run)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
