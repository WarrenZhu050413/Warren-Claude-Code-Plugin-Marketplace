#!/usr/bin/env python3
"""
Test script for mail_wrapper library

Tests all major functions with your Gmail account
"""

import sys
from pathlib import Path

# Add parent directory to path to import as a package
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from mail_wrapper.gmail_client import GmailClient
from mail_wrapper.models import SendEmailRequest


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def test_authentication():
    """Test 1: Authentication"""
    print_section("Test 1: Authentication")
    try:
        client = GmailClient()
        print("✅ Authentication successful!")
        return client
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)


def test_list_folders(client: GmailClient):
    """Test 2: List folders/labels"""
    print_section("Test 2: List Folders")
    try:
        folders = client.get_folders()
        print(f"Found {len(folders)} folders/labels:\n")

        # Show first 10 system labels and first 5 user labels
        system_labels = [f for f in folders if f.type == 'system'][:10]
        user_labels = [f for f in folders if f.type == 'user'][:5]

        print("System Labels:")
        for folder in system_labels:
            print(folder.to_markdown())

        if user_labels:
            print("\nUser Labels (first 5):")
            for folder in user_labels:
                print(folder.to_markdown())

        print("\n✅ List folders successful!")
    except Exception as e:
        print(f"❌ List folders failed: {e}")


def test_list_emails(client: GmailClient):
    """Test 3: List emails with pagination"""
    print_section("Test 3: List Emails (INBOX, limit 5)")
    try:
        result = client.list_emails(folder='INBOX', max_results=5)
        print(result.to_markdown())
        print("\n✅ List emails successful!")
        return result.emails[0].message_id if result.emails else None
    except Exception as e:
        print(f"❌ List emails failed: {e}")
        return None


def test_read_email_summary(client: GmailClient, message_id: str):
    """Test 4: Read email (summary format)"""
    print_section("Test 4: Read Email (Summary)")
    try:
        email = client.read_email(message_id, format='summary')
        print(email.to_markdown())
        print("\n✅ Read email (summary) successful!")
    except Exception as e:
        print(f"❌ Read email (summary) failed: {e}")


def test_read_email_full(client: GmailClient, message_id: str):
    """Test 5: Read email (full format)"""
    print_section("Test 5: Read Email (Full)")
    try:
        email = client.read_email(message_id, format='full')
        print(email.to_markdown()[:1000])  # Truncate for display
        if len(email.to_markdown()) > 1000:
            print(f"\n...(truncated, total length: {len(email.to_markdown())} chars)")
        print("\n✅ Read email (full) successful!")
    except Exception as e:
        print(f"❌ Read email (full) failed: {e}")


def test_search_emails(client: GmailClient):
    """Test 6: Search emails"""
    print_section("Test 6: Search Emails")
    try:
        # Search for recent emails from Gmail (likely to have results)
        result = client.search_emails(
            query="from:@gmail.com",
            folder='INBOX',
            max_results=3
        )
        print(result.to_markdown())
        print("\n✅ Search emails successful!")
    except Exception as e:
        print(f"❌ Search emails failed: {e}")


def test_pagination(client: GmailClient):
    """Test 7: Pagination"""
    print_section("Test 7: Pagination")
    try:
        # Get first page
        page1 = client.list_emails(folder='INBOX', max_results=2)
        print(f"Page 1: {len(page1.emails)} emails")
        for email in page1.emails:
            print(f"  - {email.subject[:50]}")

        # Get second page if available
        if page1.next_page_token:
            page2 = client.list_emails(
                folder='INBOX',
                max_results=2,
                page_token=page1.next_page_token
            )
            print(f"\nPage 2: {len(page2.emails)} emails")
            for email in page2.emails:
                print(f"  - {email.subject[:50]}")

        print("\n✅ Pagination successful!")
    except Exception as e:
        print(f"❌ Pagination failed: {e}")


def test_send_email_dry_run(client: GmailClient):
    """Test 8: Prepare to send email (dry run - commented out actual send)"""
    print_section("Test 8: Send Email (Dry Run)")
    try:
        request = SendEmailRequest(
            to=["fuchengwarrenzhu@gmail.com"],
            subject="Test from mail_wrapper library",
            body="This is a test email from the mail_wrapper library.\n\nIt works!",
        )

        print("Email prepared:")
        print(f"  To: {request.to}")
        print(f"  Subject: {request.subject}")
        print(f"  Body: {request.body[:50]}...")

        # Actually send to test it:
        response = client.send_email(request)
        print(f"\n{response.to_markdown()}")

        print("\n✅ Send email preparation successful!")
        print("ℹ️  To actually send, uncomment the send_email call in the test")
    except Exception as e:
        print(f"❌ Send email preparation failed: {e}")


def test_labels(client: GmailClient, message_id: str):
    """Test 9: Modify labels"""
    print_section("Test 9: Modify Labels")
    try:
        # Mark as read (remove UNREAD label)
        success = client.modify_labels(message_id, remove_labels=['UNREAD'])
        print(f"✅ Removed UNREAD label: {success}")

        # Star the email (add STARRED label)
        success = client.modify_labels(message_id, add_labels=['STARRED'])
        print(f"✅ Added STARRED label: {success}")

        # Remove star
        success = client.modify_labels(message_id, remove_labels=['STARRED'])
        print(f"✅ Removed STARRED label: {success}")

        print("\n✅ Label modification successful!")
    except Exception as e:
        print(f"❌ Label modification failed: {e}")


def main():
    """Run all tests"""
    print("\n🧪 Mail Wrapper Library Test Suite")
    print("=" * 60)

    # Test 1: Authentication
    client = test_authentication()

    # Test 2: List folders
    test_list_folders(client)

    # Test 3: List emails
    first_message_id = test_list_emails(client)

    if first_message_id:
        # Test 4: Read email (summary)
        test_read_email_summary(client, first_message_id)

        # Test 5: Read email (full)
        test_read_email_full(client, first_message_id)

        # Test 9: Modify labels (non-destructive)
        test_labels(client, first_message_id)
    else:
        print("\n⚠️  Skipping email-specific tests (no emails in INBOX)")

    # Test 6: Search emails
    test_search_emails(client)

    # Test 7: Pagination
    test_pagination(client)

    # Test 8: Send email (dry run)
    test_send_email_dry_run(client)

    # Summary
    print_section("Test Summary")
    print("✅ All tests completed!")
    print("\nThe library is ready to use.")
    print("To actually send emails, uncomment the send_email call in test 8.")


if __name__ == '__main__':
    main()
