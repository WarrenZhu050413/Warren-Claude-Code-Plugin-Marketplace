#!/usr/bin/env python3
"""Command-line interface for gmaillm"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from gmaillm import GmailClient, SendEmailRequest


def get_plugin_config_dir():
    """Get the plugin config directory path"""
    # When installed, find the actual plugin directory
    # Look for gmail-integration-plugin in the user's home
    home = Path.home()
    plugin_path = home / ".claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/gmail-integration-plugin/config"

    if plugin_path.exists():
        return plugin_path

    # Fallback: try relative path (for development)
    cli_dir = Path(__file__).parent.resolve()
    plugin_dir = cli_dir.parent.parent.parent
    return plugin_dir / "config"


def load_email_groups():
    """Load email distribution groups from config"""
    config_dir = get_plugin_config_dir()
    groups_file = config_dir / "email-groups.json"

    if not groups_file.exists():
        return {}

    try:
        with open(groups_file, 'r') as f:
            groups = json.load(f)
        # Filter out metadata/comment keys
        return {k: v for k, v in groups.items() if not k.startswith("_")}
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load email groups: {e}", file=sys.stderr)
        return {}


def expand_email_groups(recipients):
    """Expand #groupname references to actual email addresses

    Args:
        recipients: List of email addresses or #groupname references

    Returns:
        List of expanded email addresses
    """
    groups = load_email_groups()
    expanded = []

    for recipient in recipients:
        if recipient.startswith("#"):
            # This is a group reference
            group_name = recipient[1:]  # Remove # prefix
            if group_name in groups:
                expanded.extend(groups[group_name])
            else:
                print(f"Warning: Unknown group '#{group_name}', available groups: {', '.join('#' + k for k in groups.keys())}", file=sys.stderr)
                expanded.append(recipient)  # Keep as-is if group not found
        else:
            expanded.append(recipient)

    return expanded


def cmd_verify(args):
    """Verify authentication and setup"""
    try:
        client = GmailClient()
        result = client.verify_setup()

        print("=" * 60)
        print("gmaillm Setup Verification")
        print("=" * 60)

        if result['auth']:
            print("✓ Authentication: Working")
            if result['email_address']:
                print(f"✓ Authenticated as: {result['email_address']}")
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


def cmd_status(args):
    """Show current Gmail account status"""
    try:
        client = GmailClient()
        result = client.verify_setup()

        print("=" * 60)
        print("gmaillm Account Status")
        print("=" * 60)

        if result['auth'] and result['email_address']:
            print(f"\n✓ Authenticated as: {result['email_address']}")
        else:
            print("\n✗ Not authenticated")
            if result['errors']:
                print("\nErrors:")
                for error in result['errors']:
                    print(f"  - {error}")
            sys.exit(1)

        # Get inbox status
        try:
            inbox_list = client.list_emails(folder='INBOX', max_results=1)
            print(f"✓ Total folders/labels: {result['folders']}")
            print(f"✓ Inbox status: Accessible")
        except Exception as e:
            print(f"✗ Inbox status: Error - {e}")

        # Get unread count
        try:
            folders = client.get_folders()
            inbox_folder = next((f for f in folders if f.name == 'INBOX'), None)
            if inbox_folder and inbox_folder.unread_count is not None:
                print(f"✓ Unread messages: {inbox_folder.unread_count}")
        except Exception:
            pass  # Don't fail if we can't get unread count

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"✗ Failed to get status: {e}")
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

        # Expand email groups (@groupname -> actual emails)
        to_list = expand_email_groups(to_list)
        if cc_list:
            cc_list = expand_email_groups(cc_list)

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


def cmd_label_create(args):
    """Create a new label/folder"""
    try:
        client = GmailClient()

        # Show preview
        print("=" * 60)
        print("Creating Label")
        print("=" * 60)
        print(f"Name: {args.name}")
        print("=" * 60)

        # Confirm
        response = input("\nCreate this label? (y/n): ").lower()
        if response not in ['y', 'yes']:
            print("Cancelled.")
            return

        # Create label
        label = client.create_label(args.name)

        print(f"\n✅ Label created: {label.name}")
        print(f"   ID: {label.id}")

    except Exception as e:
        print(f"✗ Error creating label: {e}")
        sys.exit(1)


def cmd_label_list(args):
    """List all labels/folders"""
    try:
        client = GmailClient()
        folders = client.get_folders()

        # Separate system and user labels
        system_labels = [f for f in folders if f.type == 'system']
        user_labels = [f for f in folders if f.type == 'user']

        print("=" * 60)
        print(f"Gmail Labels")
        print("=" * 60)

        if system_labels:
            print("\n📋 System Labels:")
            for label in system_labels:
                print(f"  {label.to_markdown()}")

        if user_labels:
            print("\n🏷️  Custom Labels:")
            for label in user_labels:
                print(f"  {label.to_markdown()}")

        print(f"\nTotal: {len(system_labels)} system, {len(user_labels)} custom")

    except Exception as e:
        print(f"✗ Error listing labels: {e}")
        sys.exit(1)


def cmd_config_edit_style(args):
    """Edit email style configuration"""
    config_dir = get_plugin_config_dir()
    style_file = config_dir / "email-style.md"

    if not style_file.exists():
        print(f"Error: {style_file} does not exist")
        sys.exit(1)

    editor = os.environ.get("EDITOR", "vim")
    print(f"Opening {style_file} in {editor}...")
    subprocess.run([editor, str(style_file)])


def cmd_config_edit_groups(args):
    """Edit email distribution groups"""
    config_dir = get_plugin_config_dir()
    groups_file = config_dir / "email-groups.json"

    if not groups_file.exists():
        print(f"Error: {groups_file} does not exist")
        sys.exit(1)

    editor = os.environ.get("EDITOR", "vim")
    print(f"Opening {groups_file} in {editor}...")
    subprocess.run([editor, str(groups_file)])


def cmd_config_list_groups(args):
    """List all configured email distribution groups"""
    config_dir = get_plugin_config_dir()
    groups_file = config_dir / "email-groups.json"

    if not groups_file.exists():
        print(f"Error: {groups_file} does not exist")
        sys.exit(1)

    try:
        with open(groups_file, 'r') as f:
            groups = json.load(f)

        print("=" * 60)
        print("Email Distribution Groups")
        print("=" * 60)

        for group_name, emails in groups.items():
            if group_name.startswith("_"):
                continue  # Skip comments/metadata
            print(f"\n#{group_name}:")
            for email in emails:
                print(f"  - {email}")

        total = len([k for k in groups.keys() if not k.startswith("_")])
        print(f"\nTotal groups: {total}")
        print("\nUsage: gmail send --to #groupname --subject \"...\" --body \"...\"")

    except json.JSONDecodeError as e:
        print(f"Error parsing {groups_file}: {e}")
        sys.exit(1)


def cmd_config_show(args):
    """Show configuration file locations"""
    config_dir = get_plugin_config_dir()
    style_file = config_dir / "email-style.md"
    groups_file = config_dir / "email-groups.json"
    learned_dir = config_dir / "learned-patterns"

    editor = os.environ.get("EDITOR", "vim")

    print("=" * 60)
    print("Gmail Integration Configuration")
    print("=" * 60)
    print(f"\nEmail Style:      {style_file}")
    print(f"Email Groups:     {groups_file}")
    print(f"Learned Patterns: {learned_dir}")
    print(f"\nEditor: {editor} (set via $EDITOR)")
    print("\nCommands:")
    print("  gmail config edit-style    # Edit email style preferences")
    print("  gmail config edit-groups   # Edit distribution groups")
    print("  gmail config list-groups   # List all groups")
    print("  gmail config show          # Show this information")


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

    # status command
    status_parser = subparsers.add_parser('status', help='Show current Gmail account status')
    status_parser.set_defaults(func=cmd_status)

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

    # label command with subcommands
    label_parser = subparsers.add_parser('label', help='Manage Gmail labels')
    label_subparsers = label_parser.add_subparsers(dest='label_command', help='Label commands')
    label_subparsers.required = True

    # label create
    label_create_parser = label_subparsers.add_parser('create', help='Create a new label')
    label_create_parser.add_argument('name', help='Name of the label to create')
    label_create_parser.set_defaults(func=cmd_label_create)

    # label list
    label_list_parser = label_subparsers.add_parser('list', help='List all labels (system and custom)')
    label_list_parser.set_defaults(func=cmd_label_list)

    # config command with subcommands
    config_parser = subparsers.add_parser('config', help='Manage Gmail integration configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_command', help='Configuration commands')
    config_subparsers.required = True

    # config edit-style
    config_edit_style_parser = config_subparsers.add_parser('edit-style', help='Edit email style preferences')
    config_edit_style_parser.set_defaults(func=cmd_config_edit_style)

    # config edit-groups
    config_edit_groups_parser = config_subparsers.add_parser('edit-groups', help='Edit email distribution groups')
    config_edit_groups_parser.set_defaults(func=cmd_config_edit_groups)

    # config list-groups
    config_list_groups_parser = config_subparsers.add_parser('list-groups', help='List all configured groups')
    config_list_groups_parser.set_defaults(func=cmd_config_list_groups)

    # config show
    config_show_parser = config_subparsers.add_parser('show', help='Show configuration information')
    config_show_parser.set_defaults(func=cmd_config_show)

    # Parse and execute
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
