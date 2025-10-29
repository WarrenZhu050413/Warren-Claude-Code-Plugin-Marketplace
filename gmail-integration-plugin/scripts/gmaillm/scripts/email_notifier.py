#!/usr/bin/env python3
"""
Check for new important emails and send notifications.

This script checks for new emails matching specific criteria and
sends desktop notifications or logs them for monitoring.

Usage:
    python scripts/email_notifier.py [--query QUERY] [--max-results N]

Example:
    python scripts/email_notifier.py --query "is:unread is:important"
    python scripts/email_notifier.py --query "from:boss@example.com"
"""

import sys
import json
import subprocess
import argparse
from typing import Optional, Dict, Any, List
from datetime import datetime


def run_gmail_command(*args: str) -> Optional[Dict[str, Any]]:
    """
    Run gmail command and return JSON output.

    Args:
        *args: Command arguments to pass to gmail CLI

    Returns:
        Parsed JSON response or None on error
    """
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


def send_notification(title: str, message: str) -> None:
    """
    Send desktop notification.

    Args:
        title: Notification title
        message: Notification message
    """
    try:
        # macOS notification using osascript
        subprocess.run([
            'osascript', '-e',
            f'display notification "{message}" with title "{title}"'
        ], check=False)
    except Exception as e:
        print(f"Failed to send notification: {e}", file=sys.stderr)


def check_emails(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Check for emails matching query.

    Args:
        query: Gmail search query
        max_results: Maximum number of results to return

    Returns:
        List of email metadata dictionaries
    """
    response = run_gmail_command(
        'search',
        query,
        '--max', str(max_results)
    )

    if not response:
        return []

    # Parse emails from response
    emails = response.get('emails', [])
    return emails


def format_email_summary(email: Dict[str, Any]) -> str:
    """
    Format email as summary string.

    Args:
        email: Email metadata dictionary

    Returns:
        Formatted summary string
    """
    from_addr = email.get('from', 'Unknown')
    subject = email.get('subject', 'No subject')
    date = email.get('date', 'Unknown')

    return f"{from_addr}: {subject} ({date})"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Check for new important emails and notify',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check for unread important emails
  %(prog)s --query "is:unread is:important"

  # Check for emails from specific sender
  %(prog)s --query "from:boss@example.com is:unread"

  # Check for emails with attachments
  %(prog)s --query "has:attachment is:unread"

Common Gmail Search Queries:
  is:unread              - Unread emails
  is:important           - Important emails
  from:user@example.com  - From specific sender
  to:user@example.com    - To specific recipient
  has:attachment         - Has attachments
  in:inbox               - In inbox
  label:MyLabel          - Has specific label
  after:2024/10/01       - After specific date
        """
    )
    parser.add_argument(
        '--query',
        default='is:unread is:important',
        help='Gmail search query (default: "is:unread is:important")'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=10,
        help='Maximum number of emails to check (default: 10)'
    )
    parser.add_argument(
        '--notify',
        action='store_true',
        help='Send desktop notifications (macOS only)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Only output email count, not details'
    )

    args = parser.parse_args()

    try:
        # Check for emails
        emails = check_emails(args.query, args.max_results)

        if not emails:
            if not args.quiet:
                print("No matching emails found")
            return

        # Output results
        count = len(emails)
        if args.quiet:
            print(count)
        else:
            print(f"Found {count} matching email(s):\n")
            for i, email in enumerate(emails, 1):
                summary = format_email_summary(email)
                print(f"{i}. {summary}")

        # Send notification if requested
        if args.notify and count > 0:
            if count == 1:
                title = "New Email"
                message = format_email_summary(emails[0])
            else:
                title = f"{count} New Emails"
                message = format_email_summary(emails[0]) + f" (and {count-1} more)"

            send_notification(title, message)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
