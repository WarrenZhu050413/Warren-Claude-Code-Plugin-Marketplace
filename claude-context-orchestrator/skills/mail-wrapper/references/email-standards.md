# Email Standards: A Developer's Guide

**Mental Model**: Email is a federated text-based protocol from the 1980s. Messages are plain text with headers (metadata) and body (content). SMTP sends, IMAP/POP3 receives. No central server - anyone can run a mail server.

---

## Table of Contents

1. [Core Protocols](#core-protocols)
2. [Message Format (RFC 5322)](#message-format-rfc-5322)
3. [Email Headers Explained](#email-headers-explained)
4. [Threading: How Conversations Work](#threading-how-conversations-work)
5. [SMTP: Sending Mail](#smtp-sending-mail)
6. [MIME: Attachments & HTML](#mime-attachments--html)
7. [Real Examples](#real-examples)
8. [Quick Reference](#quick-reference)

---

## Core Protocols

Email uses **three main protocols**:

| Protocol | Purpose | Port | Use Case |
|----------|---------|------|----------|
| **SMTP** | Send mail | 25, 587, 465 | Client → Server, Server → Server |
| **IMAP** | Read mail (stateful) | 143, 993 | Client syncs with server, keeps mail on server |
| **POP3** | Download mail (stateless) | 110, 995 | Client downloads and deletes from server |

**Real World**:
- Your email client (Mail.app, Thunderbird) uses **SMTP** to send
- Uses **IMAP** or **POP3** to receive
- Gmail, Outlook.com run mail servers that speak all three

---

## Message Format (RFC 5322)

Every email is a **plain text file** with two parts:

```
Headers
Headers
Headers
<blank line>
Body content
Body content
```

### Viewing Raw Email

**macOS Mail.app**:
```bash
# Select email → View → Message → Raw Source
# Or: Command+Shift+U
```

**Gmail**:
```
Click email → Three dots menu → "Show original"
```

**Example Raw Email**:
```
From: warren@example.com
To: friend@example.com
Subject: Lunch tomorrow?
Date: Mon, 26 Oct 2025 15:30:00 -0400
Message-ID: <abc123@example.com>
Content-Type: text/plain; charset=UTF-8

Hey, want to grab lunch tomorrow at 12?

Warren
```

**Key Insight**: Headers are `Name: Value` pairs. Body is everything after the blank line.

---

## Email Headers Explained

### Required Headers

**`From:`** - Sender's email address
```
From: Warren Zhu <warren@example.com>
```

**`To:`** - Recipient(s)
```
To: alice@example.com, bob@example.com
```

**`Subject:`** - Email subject
```
Subject: Meeting notes from today
```

**`Date:`** - When email was composed (RFC 5322 format)
```
Date: Mon, 26 Oct 2025 15:30:00 -0400
```

**`Message-ID:`** - Globally unique identifier
```
Message-ID: <20251026153000.abc123@mail.example.com>
```

### Optional Headers

**`Cc:`** - Carbon copy (visible to all)
```
Cc: manager@example.com
```

**`Bcc:`** - Blind carbon copy (hidden from other recipients)
```
Bcc: audit@example.com
```
*Note: Bcc header is removed before delivery*

**`Reply-To:`** - Where replies should go
```
Reply-To: support@example.com
```

**`In-Reply-To:`** - Message-ID of email being replied to
```
In-Reply-To: <xyz789@example.com>
```

**`References:`** - Thread history (all Message-IDs in conversation)
```
References: <msg1@example.com> <msg2@example.com> <msg3@example.com>
```

### Custom Headers

Any header starting with `X-` is custom:
```
X-Mailer: Claude Code Mail Wrapper 0.1
X-Priority: 1
X-Spam-Score: 0.5
```

---

## Threading: How Conversations Work

Email threading is built on **three headers**:

### 1. Message-ID (Every Email)

Unique identifier for this specific email:
```
Message-ID: <abc123@mail.example.com>
```

Format: `<unique-string@domain>`
- Must be globally unique
- Usually includes timestamp + random component + domain

### 2. In-Reply-To (Replies Only)

Points to the **direct parent** email:

```
Original Email:
  Message-ID: <original@example.com>

Reply:
  Message-ID: <reply1@example.com>
  In-Reply-To: <original@example.com>
```

### 3. References (Replies Only)

Contains **full thread history**:

```
Email 1:
  Message-ID: <msg1@example.com>

Email 2 (reply to 1):
  Message-ID: <msg2@example.com>
  In-Reply-To: <msg1@example.com>
  References: <msg1@example.com>

Email 3 (reply to 2):
  Message-ID: <msg3@example.com>
  In-Reply-To: <msg2@example.com>
  References: <msg1@example.com> <msg2@example.com>
```

### How Email Clients Thread

**Standard approach** (Thunderbird, Apple Mail):
1. Use `In-Reply-To` and `References` to link replies
2. Fallback to subject matching (strip "Re:", "Fwd:")
3. Consider time proximity

**Gmail's approach**:
- Same as above, PLUS
- Assigns internal `thread_id` to grouped messages
- More aggressive subject matching
- Considers participant overlap

### Threading Without Gmail

When connecting to IMAP servers (not Gmail):

**Option 1: IMAP THREAD extension (RFC 5256)**
```
C: A1 CAPABILITY
S: * CAPABILITY IMAP4rev1 THREAD=REFERENCES
C: A2 THREAD REFERENCES UTF-8 ALL
S: * THREAD (1 2 3)(4 5)(6)
```

**Option 2: Build it yourself**
```python
def build_threads(emails):
    threads = {}
    msg_to_thread = {}

    for email in emails:
        msg_id = email.headers['Message-ID']
        in_reply_to = email.headers.get('In-Reply-To')

        if in_reply_to and in_reply_to in msg_to_thread:
            # Add to existing thread
            thread_id = msg_to_thread[in_reply_to]
            threads[thread_id].append(email)
            msg_to_thread[msg_id] = thread_id
        else:
            # New thread
            thread_id = msg_id
            threads[thread_id] = [email]
            msg_to_thread[msg_id] = thread_id

    return threads
```

---

## SMTP: Sending Mail

SMTP (Simple Mail Transfer Protocol) is a **text-based conversation** between client and server.

### Basic SMTP Session

```
# Connect to SMTP server
telnet smtp.example.com 25

S: 220 smtp.example.com ESMTP
C: HELO client.example.com
S: 250 smtp.example.com

C: MAIL FROM:<sender@example.com>
S: 250 OK

C: RCPT TO:<recipient@example.com>
S: 250 OK

C: DATA
S: 354 Start mail input; end with <CRLF>.<CRLF>

C: From: sender@example.com
C: To: recipient@example.com
C: Subject: Test email
C:
C: This is the email body.
C: .
S: 250 OK: Message accepted

C: QUIT
S: 221 Bye
```

**Key Points**:
- Commands are plain text (HELO, MAIL FROM, RCPT TO, DATA)
- Server responds with numeric codes (250 = OK, 354 = ready for data)
- Email ends with a line containing only `.`
- Envelope (MAIL FROM/RCPT TO) is separate from headers

### SMTP with Authentication

Modern SMTP requires authentication:

```
C: EHLO client.example.com
S: 250-smtp.example.com
S: 250-AUTH PLAIN LOGIN
S: 250 STARTTLS

C: STARTTLS
S: 220 Ready to start TLS
[TLS handshake]

C: AUTH LOGIN
S: 334 VXNlcm5hbWU6
C: dXNlckBleGFtcGxlLmNvbQ==   [base64 encoded username]
S: 334 UGFzc3dvcmQ6
C: cGFzc3dvcmQ=                [base64 encoded password]
S: 235 Authentication successful
```

### Real Command: Send Email via SMTP

```bash
# Send email using curl
curl --url 'smtps://smtp.gmail.com:465' \
  --ssl-reqd \
  --mail-from 'sender@gmail.com' \
  --mail-rcpt 'recipient@example.com' \
  --user 'sender@gmail.com:app_password' \
  --upload-file email.txt

# email.txt contents:
# From: sender@gmail.com
# To: recipient@example.com
# Subject: Test from curl
#
# Hello from command line!
```

---

## MIME: Attachments & HTML

MIME (Multipurpose Internet Mail Extensions) extends email to support:
- Attachments
- HTML content
- Multiple parts (text + HTML versions)
- Non-ASCII characters

### MIME Headers

**`Content-Type:`** - What kind of content
```
Content-Type: text/plain; charset=UTF-8
Content-Type: text/html; charset=UTF-8
Content-Type: multipart/mixed; boundary="frontier"
```

**`Content-Transfer-Encoding:`** - How content is encoded
```
Content-Transfer-Encoding: 7bit
Content-Transfer-Encoding: quoted-printable
Content-Transfer-Encoding: base64
```

### Multipart Email Example

```
From: sender@example.com
To: recipient@example.com
Subject: Email with attachment
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset=UTF-8

This is the email body.

--boundary123
Content-Type: application/pdf; name="document.pdf"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="document.pdf"

JVBERi0xLjQKJeLjz9MKMyAwIG9iago8PC9UeXBlL1BhZ2UvUGFyZW50IDIgMCBS...
[base64 encoded PDF content]

--boundary123--
```

**Key Points**:
- `boundary` separates parts
- Each part has its own Content-Type
- Attachments are base64 encoded
- Final boundary has `--` suffix

### HTML Email with Plain Text Fallback

```
Content-Type: multipart/alternative; boundary="alt123"

--alt123
Content-Type: text/plain; charset=UTF-8

This is the plain text version.

--alt123
Content-Type: text/html; charset=UTF-8

<html>
<body>
<p>This is the <strong>HTML</strong> version.</p>
</body>
</html>

--alt123--
```

Email clients show HTML version if supported, plain text otherwise.

---

## Real Examples

### Example 1: View Gmail Email Headers

```bash
# Using Gmail API (if you have mail_wrapper)
python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/wz/Desktop/zPersonalProjects')
from mail_wrapper import GmailClient

client = GmailClient()
result = client.list_emails(folder='INBOX', max_results=1)
email = client.read_email(result.emails[0].message_id, format="full")

# Print all headers
for header in email.payload['headers']:
    print(f"{header['name']}: {header['value']}")
EOF
```

### Example 2: Send Email with Python (SMTP)

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create message
msg = MIMEMultipart()
msg['From'] = 'you@example.com'
msg['To'] = 'recipient@example.com'
msg['Subject'] = 'Test from Python'
msg['Message-ID'] = '<unique123@example.com>'

# Add body
body = MIMEText('Hello from Python!', 'plain')
msg.attach(body)

# Send via SMTP
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login('you@example.com', 'app_password')
    server.send_message(msg)
```

### Example 3: Parse Email Headers in Python

```python
import email
from email import policy

# Read raw email
with open('email.eml', 'rb') as f:
    msg = email.message_from_binary_file(f, policy=policy.default)

# Access headers
print(f"From: {msg['From']}")
print(f"To: {msg['To']}")
print(f"Subject: {msg['Subject']}")
print(f"Message-ID: {msg['Message-ID']}")
print(f"In-Reply-To: {msg.get('In-Reply-To', 'None')}")

# Get body
if msg.is_multipart():
    for part in msg.walk():
        if part.get_content_type() == 'text/plain':
            print(part.get_content())
else:
    print(msg.get_content())
```

### Example 4: Check if Email is a Reply

```python
def is_reply(email_headers):
    """Check if email is a reply based on headers"""
    has_in_reply_to = 'In-Reply-To' in email_headers
    has_references = 'References' in email_headers
    subject_is_reply = email_headers.get('Subject', '').startswith('Re:')

    return has_in_reply_to or has_references or subject_is_reply

# Usage
headers = {
    'Message-ID': '<new@example.com>',
    'In-Reply-To': '<original@example.com>',
    'Subject': 'Re: Your question'
}

print(is_reply(headers))  # True
```

---

## Quick Reference

### Common Headers

| Header | Purpose | Example |
|--------|---------|---------|
| `From` | Sender address | `From: alice@example.com` |
| `To` | Recipient(s) | `To: bob@example.com, charlie@example.com` |
| `Cc` | Carbon copy | `Cc: manager@example.com` |
| `Bcc` | Blind copy (hidden) | `Bcc: audit@example.com` |
| `Subject` | Email subject | `Subject: Meeting notes` |
| `Date` | Composition time | `Date: Mon, 26 Oct 2025 15:30:00 -0400` |
| `Message-ID` | Unique ID | `Message-ID: <abc@example.com>` |
| `In-Reply-To` | Parent message | `In-Reply-To: <xyz@example.com>` |
| `References` | Thread history | `References: <a@x.com> <b@x.com>` |
| `Reply-To` | Reply address | `Reply-To: support@example.com` |

### SMTP Response Codes

| Code | Meaning |
|------|---------|
| 220 | Service ready |
| 250 | Requested action okay, completed |
| 354 | Start mail input |
| 421 | Service not available |
| 450 | Mailbox unavailable (temporary) |
| 550 | Mailbox unavailable (permanent) |
| 554 | Transaction failed |

### MIME Content Types

| Type | Use Case |
|------|----------|
| `text/plain` | Plain text email |
| `text/html` | HTML email |
| `multipart/mixed` | Email with attachments |
| `multipart/alternative` | Text + HTML versions |
| `application/pdf` | PDF attachment |
| `image/jpeg` | Image attachment |

### RFCs to Read

- **RFC 5321**: SMTP (Simple Mail Transfer Protocol)
- **RFC 5322**: Internet Message Format (headers, structure)
- **RFC 2045-2049**: MIME (attachments, encoding)
- **RFC 5256**: IMAP THREAD extension
- **RFC 6854**: Update to From and Sender headers
- **RFC 3798**: Message Disposition Notifications (read receipts)

---

## Advanced Topics

### SPF, DKIM, DMARC (Anti-Spam)

**SPF** (Sender Policy Framework) - DNS record listing authorized mail servers
```
example.com.  TXT  "v=spf1 mx ip4:192.0.2.1 -all"
```

**DKIM** (DomainKeys Identified Mail) - Cryptographic signature in headers
```
DKIM-Signature: v=1; a=rsa-sha256; d=example.com; s=selector;
  h=from:to:subject; bh=base64hash; b=base64signature
```

**DMARC** - Policy for handling SPF/DKIM failures
```
_dmarc.example.com.  TXT  "v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com"
```

### Email Size Limits

- **SMTP standard**: 10 MB recommended limit
- **Gmail**: 25 MB (attachments + message)
- **Outlook.com**: 20 MB
- **Yahoo Mail**: 25 MB

Large files? Use links instead of attachments.

---

## Common Questions

**Q: Why does Message-ID include a domain?**
A: To ensure global uniqueness. Your domain guarantees no one else generates that ID.

**Q: Can I send email without a mail server?**
A: No. You always need an SMTP server (yours or a provider's like Gmail).

**Q: What's the difference between envelope and headers?**
A: Envelope is SMTP conversation (MAIL FROM/RCPT TO). Headers are in the message itself. They can differ (e.g., Bcc).

**Q: Why do email clients show different threading?**
A: Each implements threading differently. Some strict (headers only), some loose (subject + time + headers).

**Q: Can I forge From header?**
A: Yes, headers are just text. But SPF/DKIM/DMARC prevent your email from being delivered.

---

## See Also

- [mail_wrapper library](../SKILL.md) - Python wrapper for Gmail API
- [Gmail API tutorial](./gmail-api-tutorial.md) - Hands-on Gmail API guide
- [Gmail search syntax](./gmail_search_syntax.md) - Query syntax reference
- [Email usage examples](./usage_examples.md) - Common patterns with mail_wrapper

**External Resources**:
- [RFC 5322 Full Text](https://www.rfc-editor.org/rfc/rfc5322.html)
- [RFC 5321 Full Text](https://www.rfc-editor.org/rfc/rfc5321.html)
- [MIME RFCs](https://www.rfc-editor.org/rfc/rfc2045.html)
