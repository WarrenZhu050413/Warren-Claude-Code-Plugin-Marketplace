#!/usr/bin/env python3
"""Command-line interface for mail_wrapper"""

import argparse
import sys

from mail_wrapper import GmailClient, SendEmailRequest


def cmd_verify(args):
    """Verify authentication and setup"""
    try:
        client = GmailClient()
        result = client.verify_setup()

        print("=" * 60)
        print("Mail Wrapper Setup Verification")
        print("=" * 60)

        if result['auth']:
            print("✓ Authentication: Working")
        else:
            print("✗ Authentication: Failed")

        print(f"✓ Folders accessible: {result['folders']}")

        if result['inbox_accessible']:
            print("✓ Inbox: Accessible")
        else:
            print("✗ Inbox: Not accessible")

        if result['errors']:
            print("\nErrors:")
            for error in result['errors']:
                print(f"  - {error}")
        else:
            print("\n✅ All checks passed!")

    except Exception as e:
        print(f"✗ Setup verification failed: {e}")
        sys.exit(1)


def cmd_list(args):
    """List emails from a folder"""
    try:
        client = GmailClient()
        result = client.list_emails(
            folder=args.folder,
            max_results=args.max,
            query=args.query
        )
        print(result.to_markdown())
    except Exception as e:
        print(f"Error listing emails: {e}")
        sys.exit(1)


def cmd_read(args):
    """Read a specific email"""
    try:
        client = GmailClient()
        format_type = "full" if args.full else "summary"
        email = client.read_email(args.message_id, format=format_type)
        print(email.to_markdown())
    except Exception as e:
        print(f"Error reading email: {e}")
        sys.exit(1)


def cmd_thread(args):
    """Show entire email thread"""
    try:
        client = GmailClient()
        thread = client.get_thread(args.message_id)

        print("=" * 60)
        print(f"Thread: {len(thread)} message(s)")
        print("=" * 60)

        for i, email in enumerate(thread, 1):
            print(f"\n[{i}] {email.from_.email} → ", end="")
            if email.to:
                print(email.to[0].email if email.to else "unknown")
            else:
                print("unknown")
            print(f"Date: {email.date.strftime('%Y-%m-%d %H:%M')}")
            print(f"Subject: {email.subject}")
            print(f"Snippet: {email.snippet[:100]}...")
            if i < len(thread):
                print("-" * 60)

    except Exception as e:
        print(f"Error getting thread: {e}")
        sys.exit(1)


def cmd_search(args):
    """Search emails"""
    try:
        client = GmailClient()
        result = client.search_emails(
            query=args.query,
            folder=args.folder,
            max_results=args.max
        )
        print(result.to_markdown())
    except Exception as e:
        print(f"Error searching emails: {e}")
        sys.exit(1)


def cmd_reply(args):
    """Reply to an email"""
    try:
        client = GmailClient()

        # Get original email for context
        original = client.read_email(args.message_id, format="summary")

        # Show preview
        print("=" * 60)
        print("Reply Preview")
        print("=" * 60)
        print(f"To: {original.from_.email}")
        print(f"Subject: Re: {original.subject}")
        print(f"\n{args.body}")
        print("=" * 60)

        # Confirm
        response = input("\nSend this reply? (y/n/yolo): ").lower()
        if response not in ['y', 'yes', 'yolo']:
            print("Cancelled.")
            return

        # Send reply
        result = client.reply_email(
            message_id=args.message_id,
            body=args.body,
            reply_all=args.reply_all
        )

        print(f"\n✅ Reply sent! Message ID: {result.message_id}")

    except Exception as e:
        print(f"Error sending reply: {e}")
        sys.exit(1)


def cmd_send(args):
    """Send a new email"""
    try:
        client = GmailClient()

        # Parse recipients
        to_list = args.to if isinstance(args.to, list) else [args.to]
        cc_list = args.cc if args.cc else None

        # Show preview
        print("=" * 60)
        print("Email Preview")
        print("=" * 60)
        print(f"To: {', '.join(to_list)}")
        if cc_list:
            print(f"Cc: {', '.join(cc_list)}")
        print(f"Subject: {args.subject}")
        print(f"\n{args.body}")
        if args.attachments:
            print(f"\nAttachments: {len(args.attachments)} file(s)")
            for att in args.attachments:
                print(f"  - {att}")
        print("=" * 60)

        # Confirm unless yolo
        if not args.yolo:
            response = input("\nSend this email? (y/n/yolo): ").lower()
            if response not in ['y', 'yes', 'yolo']:
                print("Cancelled.")
                return
        else:
            print("\nYOLO mode: Sending without confirmation...")

        # Send email
        request = SendEmailRequest(
            to=to_list,
            subject=args.subject,
            body=args.body,
            cc=cc_list,
            attachments=args.attachments
        )
        result = client.send_email(request)

        print(f"\n✅ Email sent! Message ID: {result.message_id}")

    except Exception as e:
        print(f"Error sending email: {e}")
        sys.exit(1)


def cmd_folders(args):
    """List available folders/labels"""
    try:
        client = GmailClient()
        folders = client.get_folders()

        print("=" * 60)
        print(f"Available Folders ({len(folders)})")
        print("=" * 60)

        for folder in folders:
            print(folder.to_markdown())

    except Exception as e:
        print(f"Error listing folders: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Gmail CLI wrapper with LLM-friendly operations',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    subparsers.required = True

    # verify command
    verify_parser = subparsers.add_parser('verify', help='Verify authentication and setup')
    verify_parser.set_defaults(func=cmd_verify)

    # list command
    list_parser = subparsers.add_parser('list', help='List emails')
    list_parser.add_argument('--folder', default='INBOX', help='Folder to list from (default: INBOX)')
    list_parser.add_argument('--max', type=int, default=10, help='Maximum results (default: 10)')
    list_parser.add_argument('--query', help='Optional search query')
    list_parser.set_defaults(func=cmd_list)

    # read command
    read_parser = subparsers.add_parser('read', help='Read a specific email')
    read_parser.add_argument('message_id', help='Message ID to read')
    read_parser.add_argument('--full', action='store_true', help='Show full email body')
    read_parser.set_defaults(func=cmd_read)

    # thread command
    thread_parser = subparsers.add_parser('thread', help='Show entire email thread')
    thread_parser.add_argument('message_id', help='Message ID in the thread')
    thread_parser.set_defaults(func=cmd_thread)

    # search command
    search_parser = subparsers.add_parser('search', help='Search emails')
    search_parser.add_argument('query', help='Gmail search query')
    search_parser.add_argument('--folder', default='INBOX', help='Folder to search in (default: INBOX)')
    search_parser.add_argument('--max', type=int, default=10, help='Maximum results (default: 10)')
    search_parser.set_defaults(func=cmd_search)

    # reply command
    reply_parser = subparsers.add_parser('reply', help='Reply to an email')
    reply_parser.add_argument('message_id', help='Message ID to reply to')
    reply_parser.add_argument('--body', required=True, help='Reply body text')
    reply_parser.add_argument('--reply-all', action='store_true', help='Reply to all recipients')
    reply_parser.set_defaults(func=cmd_reply)

    # send command
    send_parser = subparsers.add_parser('send', help='Send a new email')
    send_parser.add_argument('--to', nargs='+', required=True, help='Recipient email(s)')
    send_parser.add_argument('--subject', required=True, help='Email subject')
    send_parser.add_argument('--body', required=True, help='Email body')
    send_parser.add_argument('--cc', nargs='+', help='CC recipient(s)')
    send_parser.add_argument('--attachments', nargs='+', help='Attachment file path(s)')
    send_parser.add_argument('--yolo', action='store_true', help='Send without confirmation')
    send_parser.set_defaults(func=cmd_send)

    # folders command
    folders_parser = subparsers.add_parser('folders', help='List available folders/labels')
    folders_parser.set_defaults(func=cmd_folders)

    # Parse and execute
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
