# Gmail API Quirks and Gotchas

**Last Updated**: October 28, 2025
**Purpose**: Document surprising Gmail API behavior to prevent future bugs

---

## 🔴 Critical Quirks (Will Cause Bugs)

### 1. `labels.list()` Does NOT Return Message Counts

**What You'd Expect** (based on API docs):
```python
labels = service.users().labels().list(userId='me').execute()
for label in labels['labels']:
    print(label['messagesTotal'])      # ❌ KeyError!
    print(label['messagesUnread'])     # ❌ KeyError!
```

**What Actually Happens**:
- `labels.list()` returns ONLY: `id`, `name`, `type`, `labelListVisibility`, `messageListVisibility`
- Message counts (`messagesTotal`, `messagesUnread`) are **NOT included**
- API documentation shows these fields but they're only available via `labels.get()`

**Correct Implementation**:
```python
# Step 1: Get list of labels
labels_list = service.users().labels().list(userId='me').execute()

# Step 2: Fetch EACH label individually for counts
for label_data in labels_list['labels']:
    label_details = service.users().labels().get(
        userId='me',
        id=label_data['id']
    ).execute()

    # NOW you have messagesTotal and messagesUnread
    total = label_details.get('messagesTotal', 0)
    unread = label_details.get('messagesUnread', 0)
```

**Performance Impact**: O(n) API calls where n = number of labels (typically 20-50)

**Why This Matters**:
- Bug fixed in commit `d05c6a3`
- Status command showed 0 unread messages despite having unread emails
- Took hours to debug because docs were misleading

**Reference**:
- Bug report: TEST_FINDINGS.md #3
- Code: `gmail_client.py:get_folders()`

---

### 2. Message Body Encoding is Inconsistent

**The Problem**:
Gmail returns message bodies in different formats depending on MIME structure:
- Plain text: `body.data` (base64 encoded)
- HTML: `body.data` (base64 encoded)
- Multipart: Nested in `parts[]` array with varying depth

**Correct Parsing Logic**:
```python
def _get_body(payload: dict) -> tuple[str, str]:
    """Extract body from Gmail message payload.

    Returns: (plain_text, html_text)
    """
    plain = ""
    html = ""

    # Case 1: Direct body data (simple messages)
    if 'body' in payload and 'data' in payload['body']:
        data = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        mime_type = payload.get('mimeType', '')

        if 'html' in mime_type:
            html = data
        else:
            plain = data

    # Case 2: Multipart messages (nested parts)
    if 'parts' in payload:
        for part in payload['parts']:
            mime_type = part.get('mimeType', '')

            # Recursive for nested multipart
            if mime_type.startswith('multipart/'):
                p, h = _get_body(part)
                plain = plain or p
                html = html or h

            # Extract text parts
            elif 'body' in part and 'data' in part['body']:
                data = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

                if mime_type == 'text/plain':
                    plain = data
                elif mime_type == 'text/html':
                    html = data

    return plain, html
```

**Why This Matters**:
- Different email clients format messages differently
- Recursive parsing required for complex MIME structures
- Must handle both simple and multipart messages

**Reference**: `gmail_client.py:read_email()`

---

### 3. Thread IDs vs Message IDs

**Confusion Point**:
- Every message has BOTH a `threadId` and `id` (message ID)
- Single-message threads: `threadId == messageId`
- Multi-message threads: All messages share same `threadId`, different `messageId`

**Correct Usage**:
```python
# Get all messages in a thread
thread = service.users().threads().get(
    userId='me',
    id=thread_id,  # ✅ Use threadId
    format='full'
).execute()

messages = thread.get('messages', [])

# Get single message
message = service.users().messages().get(
    userId='me',
    id=message_id,  # ✅ Use messageId (not threadId!)
    format='full'
).execute()
```

**Why This Matters**:
- Using wrong ID causes "Not Found" errors
- Thread view requires `threadId`, message view requires `messageId`
- Tests must verify correct ID type is used

**Reference**: `gmail_client.py:get_thread()`

---

## ⚠️ Warning: Unexpected Behavior

### 4. `modify()` Doesn't Validate Label IDs

**The Issue**:
```python
# This SUCCEEDS even with invalid label!
service.users().messages().modify(
    userId='me',
    id=message_id,
    body={
        'addLabelIds': ['INVALID_LABEL_ID_12345'],
        'removeLabelIds': ['INBOX']
    }
).execute()

# No error raised, but label not actually added
# You must check response to verify
```

**Safe Implementation**:
```python
result = service.users().messages().modify(
    userId='me',
    id=message_id,
    body={'addLabelIds': [label_id]}
).execute()

# Verify label was actually added
if label_id not in result.get('labelIds', []):
    raise ValueError(f"Failed to add label {label_id}")
```

**Why This Matters**:
- Silent failures are worse than exceptions
- Must validate label IDs before modify call
- Need to check response, not assume success

---

### 5. Search Queries Have Undocumented Limits

**Query Length Limit**: ~500 characters
```python
# This works
result = service.users().messages().list(
    userId='me',
    q='is:unread in:inbox'
).execute()

# This FAILS silently (returns empty results)
result = service.users().messages().list(
    userId='me',
    q='from:' + 'x' * 600  # Query too long!
).execute()
```

**Complex Query Gotcha**:
```python
# Doesn't work as expected - AND is implicit
q = 'from:alice@example.com OR from:bob@example.com is:unread'
# Interpreted as: (from:alice OR from:bob) AND is:unread

# Use parentheses for explicit OR
q = '(from:alice@example.com OR from:bob@example.com) is:unread'
```

**Why This Matters**:
- Long queries fail silently (no error, just empty results)
- Operator precedence is different from SQL
- Must validate query length before API call

**Reference**: `gmail_client.py:search_emails()`

---

## 📊 Performance Quirks

### 6. Batch Requests Save API Quota But Are Complex

**Problem**: Each API call consumes quota, fetching 100 labels = 100 calls

**Solution**: Batch API requests
```python
from googleapiclient.http import BatchHttpRequest

def list_emails_batch(service, message_ids):
    """Fetch multiple messages in one API call."""

    def callback(request_id, response, exception):
        if exception:
            print(f"Error for {request_id}: {exception}")
        else:
            results[request_id] = response

    results = {}
    batch = service.new_batch_http_request(callback=callback)

    for msg_id in message_ids:
        batch.add(service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ))

    batch.execute()
    return results
```

**Why This Matters**:
- Reduces API calls from O(n) to O(1)
- Saves quota (10,000 calls/day limit for free tier)
- Much faster for bulk operations

**Implementation Status**: ✅ Added in commit `233f299`

**Reference**: `gmail_client.py:list_emails()`, `gmail_client.py:get_folders()`

---

### 7. Rate Limiting is Per-User, Not Per-Token

**The Surprise**:
```python
# You have multiple OAuth tokens for same user
token1 = "user_token_from_device_A"
token2 = "user_token_from_device_B"

# Rate limit is SHARED across both tokens!
# Making 100 calls with token1 + 100 with token2 = 200 total
# Quota consumed: 200 (not 100 per token)
```

**Implications**:
- Can't bypass rate limits with multiple tokens
- Implement client-side rate limiting/caching
- Consider batch requests for bulk operations

**Why This Matters**:
- Users running CLI on multiple devices share quota
- Need to implement exponential backoff for retries
- Cache frequently accessed data (labels, etc.)

---

## 🐛 Bug Potential Areas

### 8. Attachment Handling Edge Cases

**Problematic Cases**:
```python
# Case 1: Inline images (not "attachments")
# MIME type: image/png
# Content-Disposition: inline
# filename: "image001.png"
# attachmentId: present but not in parts[].body.attachmentId

# Case 2: Embedded calendar invites
# MIME type: text/calendar
# Not treated as attachment by Gmail API

# Case 3: Zero-byte attachments
# filename present, size = 0, no attachmentId
```

**Robust Attachment Detection**:
```python
def _extract_attachments(parts: list) -> list:
    """Extract actual downloadable attachments."""
    attachments = []

    for part in parts:
        filename = part.get('filename', '')
        mime_type = part.get('mimeType', '')

        # Skip inline images and calendars
        if not filename:
            continue
        if mime_type.startswith('image/') and 'inline' in part.get('headers', {}):
            continue
        if mime_type == 'text/calendar':
            continue

        # Must have attachment ID to download
        body = part.get('body', {})
        if 'attachmentId' not in body:
            continue

        # Valid attachment
        attachments.append({
            'filename': filename,
            'mimeType': mime_type,
            'size': body.get('size', 0),
            'attachmentId': body['attachmentId']
        })

    return attachments
```

**Why This Matters**:
- Inline images shouldn't show as "attachments"
- Calendar invites need special handling
- Zero-byte files cause download errors

---

## 📝 Best Practices Learned

### 9. Always Use `format='metadata'` for Lists

**Inefficient** (fetches full message):
```python
messages = service.users().messages().list(
    userId='me',
    q='is:unread'
).execute()

for msg_id in messages.get('messages', []):
    # Full fetch for every message!
    msg = service.users().messages().get(
        userId='me',
        id=msg_id['id'],
        format='full'  # ❌ Wasteful if you just need summary
    ).execute()
```

**Efficient** (use format parameter):
```python
messages = service.users().messages().list(
    userId='me',
    q='is:unread',
    maxResults=100  # Always set limit
).execute()

for msg_data in messages.get('messages', []):
    # Get minimal data first
    msg = service.users().messages().get(
        userId='me',
        id=msg_data['id'],
        format='metadata',  # ✅ Just headers, much faster
        metadataHeaders=['From', 'Subject', 'Date']
    ).execute()
```

**Performance Impact**:
- `format='full'`: ~2-5 KB per message
- `format='metadata'`: ~500 bytes per message
- 10x less bandwidth, 5x faster response

---

### 10. Pagination is Mandatory for Production

**The Bug**:
```python
# Only returns first 100 results by default!
messages = service.users().messages().list(
    userId='me',
    q='label:inbox'
).execute()

# If user has 500 inbox messages, 400 are missed!
```

**Correct Pagination**:
```python
def list_all_messages(service, query):
    """Get ALL messages, not just first page."""
    all_messages = []
    page_token = None

    while True:
        result = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=500,  # Max allowed per page
            pageToken=page_token
        ).execute()

        all_messages.extend(result.get('messages', []))

        page_token = result.get('nextPageToken')
        if not page_token:
            break  # No more pages

    return all_messages
```

**Why This Matters**:
- Default limit is 100 messages
- Large mailboxes require pagination
- `nextPageToken` is how you get next page

**Reference**: `gmail_client.py:search_emails()`

---

## 🎯 Testing Recommendations

### What to Test:

1. **API Response Validation**
   ```python
   def test_labels_get_returns_message_counts():
       """Verify labels.get() has messagesTotal field."""
       label = service.users().labels().get(
           userId='me',
           id='INBOX'
       ).execute()

       assert 'messagesTotal' in label
       assert 'messagesUnread' in label
       assert isinstance(label['messagesTotal'], int)
   ```

2. **Edge Case Messages**
   - Empty body
   - Only HTML (no plain text)
   - Multipart with 3+ levels
   - Inline images
   - Zero-byte attachments

3. **Pagination**
   - Verify `nextPageToken` handled
   - Test with >100 results
   - Verify all pages fetched

4. **Rate Limiting**
   - Exponential backoff on 429 errors
   - Respect Retry-After header
   - Cache frequently accessed data

---

## 📚 Official Documentation (With Caveats)

**Official Docs**: https://developers.google.com/gmail/api/reference/rest

**Known Issues with Docs**:
- ❌ Claims `labels.list()` returns message counts (IT DOESN'T)
- ❌ Doesn't mention 500-character query limit
- ❌ Sparse on MIME multipart handling details
- ❌ No examples of batch requests
- ❌ Rate limiting details are vague

**Better Resources**:
- Stack Overflow: Search for specific error messages
- This file: Real-world gotchas from production use
- API Explorer: Test actual responses

---

## 🔧 Quick Reference

| Operation | Correct Method | Common Mistake |
|-----------|---------------|----------------|
| Get message counts | `labels.get(id)` | `labels.list()` ❌ |
| Get single message | `messages.get(id, format='full')` | Using threadId ❌ |
| Search with pagination | Loop with `pageToken` | Only first page ❌ |
| Batch operations | `new_batch_http_request()` | Individual calls ❌ |
| Attachment detection | Check `attachmentId` + filename | Just check filename ❌ |
| Body extraction | Recursive multipart parsing | Assume simple structure ❌ |

---

**Last Updated**: October 28, 2025
**Maintainer**: Add your discoveries here!
**Status**: Living document - update as you find more quirks
