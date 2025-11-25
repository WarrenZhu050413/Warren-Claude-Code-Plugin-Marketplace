#!/usr/bin/env python3
"""
Clean up inbox by archiving processed emails.

This script provides automated inbox cleanup functionality,
archiving emails based on various criteria.

Usage:
    python scripts/inbox_cleanup.py [OPTIONS]

Example:
    python scripts/inbox_cleanup.py --archive-newsletters
    python scripts/inbox_cleanup.py --archive-older-than 30
    python scripts/inbox_cleanup.py --workflow gmaillm-inbox
"""

import sys
import json
import subprocess
import argparse
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


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
        return None


def archive_email(message_id: str, dry_run: bool = False) -> bool:
    """
    Archive an email by removing INBOX label.

    Args:
        message_id: Gmail message ID
        dry_run: If True, don't actually archive

    Returns:
        True if successful, False otherwise
    """
    if dry_run:
        print(f"[DRY RUN] Would archive: {message_id}")
        return True

    response = run_gmail_command(
        'labels', 'remove',
        message_id,
        'INBOX'
    )

    return response is not None


def archive_newsletters(dry_run: bool = False) -> int:
    """
    Archive emails from common newsletter senders.

    Args:
        dry_run: If True, don't actually archive

    Returns:
        Number of emails archived
    """
    # Common newsletter patterns
    newsletter_patterns = [
        'noreply@',
        'newsletter@',
        'no-reply@',
        'updates@',
        'notifications@',
    ]

    archived = 0

    for pattern in newsletter_patterns:
        print(f"Searching for: {pattern}")

        query = f"from:{pattern} in:inbox"
        response = run_gmail_command('search', query, '--max', '50')

        if not response:
            continue

        emails = response.get('emails', [])
        print(f"  Found {len(emails)} emails")

        for email in emails:
            message_id = email.get('id')
            from_addr = email.get('from', 'Unknown')

            print(f"  - {from_addr}")

            if archive_email(message_id, dry_run):
                archived += 1

    return archived


def archive_older_than(days: int, dry_run: bool = False) -> int:
    """
    Archive emails older than specified days.

    Args:
        days: Number of days
        dry_run: If True, don't actually archive

    Returns:
        Number of emails archived
    """
    # Calculate date
    cutoff_date = datetime.now() - timedelta(days=days)
    date_str = cutoff_date.strftime('%Y/%m/%d')

    print(f"Archiving emails before: {date_str}")

    query = f"in:inbox before:{date_str}"
    response = run_gmail_command('search', query, '--max', '100')

    if not response:
        return 0

    emails = response.get('emails', [])
    print(f"Found {len(emails)} emails")

    archived = 0
    for email in emails:
        message_id = email.get('id')
        subject = email.get('subject', 'No subject')
        date = email.get('date', 'Unknown')

        print(f"  - {subject} ({date})")

        if archive_email(message_id, dry_run):
            archived += 1

    return archived


def cleanup_with_workflow(workflow_name: str, dry_run: bool = False) -> None:
    """
    Use a workflow to clean up inbox.

    Args:
        workflow_name: Name of workflow to run
        dry_run: If True, don't actually execute actions
    """
    print(f"Starting workflow: {workflow_name}")

    # Start workflow
    response = run_gmail_command('workflows', 'start', workflow_name)
    if not response:
        print("Failed to start workflow")
        return

    token = response.get('token')
    if not token:
        print("No token in response")
        return

    archived = 0
    skipped = 0

    # Process each email
    while response and response.get('progress', {}).get('remaining', 0) > 0:
        email = response.get('email', {})
        progress = response.get('progress', {})

        print(f"\n[{progress.get('current', 0)}/{progress.get('total', 0)}]")
        print(f"From: {email.get('from', 'Unknown')}")
        print(f"Subject: {email.get('subject', 'No subject')}")

        if dry_run:
            response = run_gmail_command('workflows', 'continue', token, 'skip')
            skipped += 1
        else:
            # Default action: archive
            response = run_gmail_command('workflows', 'continue', token, 'archive')
            archived += 1

    print(f"\nArchived: {archived}, Skipped: {skipped}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Clean up inbox by archiving emails',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Archive newsletters
  %(prog)s --archive-newsletters

  # Archive emails older than 30 days
  %(prog)s --archive-older-than 30

  # Use workflow for cleanup
  %(prog)s --workflow gmaillm-inbox

  # Dry run (show what would be done)
  %(prog)s --archive-newsletters --dry-run
        """
    )

    parser.add_argument(
        '--archive-newsletters',
        action='store_true',
        help='Archive emails from common newsletter senders'
    )
    parser.add_argument(
        '--archive-older-than',
        type=int,
        metavar='DAYS',
        help='Archive emails older than specified days'
    )
    parser.add_argument(
        '--workflow',
        metavar='NAME',
        help='Use workflow for cleanup'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without executing'
    )

    args = parser.parse_args()

    # Check that at least one action is specified
    if not any([args.archive_newsletters, args.archive_older_than, args.workflow]):
        parser.error('Must specify at least one action: --archive-newsletters, --archive-older-than, or --workflow')

    if args.dry_run:
        print("DRY RUN MODE - No changes will be made\n")

    try:
        total_archived = 0

        if args.archive_newsletters:
            print("=" * 50)
            print("Archiving Newsletters")
            print("=" * 50)
            count = archive_newsletters(args.dry_run)
            total_archived += count
            print(f"\nArchived {count} newsletter emails\n")

        if args.archive_older_than:
            print("=" * 50)
            print(f"Archiving Emails Older Than {args.archive_older_than} Days")
            print("=" * 50)
            count = archive_older_than(args.archive_older_than, args.dry_run)
            total_archived += count
            print(f"\nArchived {count} old emails\n")

        if args.workflow:
            print("=" * 50)
            print("Using Workflow for Cleanup")
            print("=" * 50)
            cleanup_with_workflow(args.workflow, args.dry_run)

        if total_archived > 0:
            print("=" * 50)
            print(f"Total Archived: {total_archived}")
            print("=" * 50)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
