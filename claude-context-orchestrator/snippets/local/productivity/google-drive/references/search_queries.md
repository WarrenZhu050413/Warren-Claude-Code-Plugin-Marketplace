# Google Drive Search Query Syntax

## Query Operators

| Query | Description |
|-------|-------------|
| `title contains 'text'` | Files with title containing text |
| `fullText contains 'text'` | Search file content |
| `mimeType = 'type'` | Files of specific MIME type |
| `'parent_id' in parents` | Files in specific folder |
| `'root' in parents` | Files in root directory |
| `trashed = false` | Not in trash |
| `trashed = true` | In trash |
| `'me' in owners` | Files you own |
| `starred = true` | Starred files |
| `modifiedDate > 'date'` | Modified after date |
| `modifiedDate < 'date'` | Modified before date |
| `createdDate > 'date'` | Created after date |

## Common MIME Types

| Type | MIME Type |
|------|-----------|
| PDF | `application/pdf` |
| Text | `text/plain` |
| Word | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| Excel | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| PowerPoint | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |
| Google Doc | `application/vnd.google-apps.document` |
| Google Sheet | `application/vnd.google-apps.spreadsheet` |
| Google Slides | `application/vnd.google-apps.presentation` |
| Folder | `application/vnd.google-apps.folder` |
| Image | `image/jpeg`, `image/png`, `image/gif` |

## Search Examples

### Basic Searches

```python
# Files containing "report" in title
file_list = drive.ListFile({'q': "title contains 'report'"}).GetList()

# PDF files only
file_list = drive.ListFile({'q': "mimeType = 'application/pdf'"}).GetList()

# Files in root, not trashed
file_list = drive.ListFile({'q': "'root' in parents and trashed = false"}).GetList()
```

### Complex Queries

```python
# Multiple conditions with AND
query = (
    "title contains 'invoice' and "
    "mimeType = 'application/pdf' and "
    "trashed = false"
)
file_list = drive.ListFile({'q': query}).GetList()

# Files you own
file_list = drive.ListFile({'q': "'me' in owners"}).GetList()

# Modified after specific date
file_list = drive.ListFile({'q': "modifiedDate > '2024-01-01'"}).GetList()

# Folders only
file_list = drive.ListFile({'q': "mimeType = 'application/vnd.google-apps.folder'"}).GetList()

# Starred PDFs
query = "starred = true and mimeType = 'application/pdf'"
file_list = drive.ListFile({'q': query}).GetList()
```

### Content Search

```python
# Search file content (not just title)
file_list = drive.ListFile({'q': "fullText contains 'keyword'"}).GetList()
```

## Date Format

Use ISO 8601 format: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`

Examples:
- `'2024-01-01'`
- `'2024-12-31T23:59:59'`

## Combining Conditions

Use `and` and `or` operators:

```python
# Either condition
query = "title contains 'report' or title contains 'summary'"

# Both conditions
query = "title contains 'report' and mimeType = 'application/pdf'"

# Complex combination
query = (
    "(title contains 'invoice' or title contains 'receipt') and "
    "mimeType = 'application/pdf' and "
    "modifiedDate > '2024-01-01'"
)
```

## Special Characters

Escape single quotes in search terms:

```python
# Searching for "O'Brien"
query = "title contains 'O\\'Brien'"
```

## Performance Tips

1. **Be specific**: More specific queries return faster
2. **Limit fields**: Use `fields` parameter to request only needed data
3. **Use pagination**: For large result sets, use `pageToken`
4. **Avoid fullText searches**: They are slower than title searches

## Iterating Results

```python
# Process all results
file_list = drive.ListFile({'q': "title contains 'report'"}).GetList()

for file in file_list:
    print(f"{file['title']} (ID: {file['id']})")
    print(f"  Modified: {file['modifiedDate']}")
    print(f"  Size: {file.get('fileSize', 'N/A')} bytes")
```
