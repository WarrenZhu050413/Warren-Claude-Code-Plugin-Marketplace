---
name: google-drive
description: Interact with Google Drive API using PyDrive2 for uploading, downloading, searching, and managing files. Use when working with Google Drive operations including file transfers, metadata queries, search operations, folder management, batch operations, and sharing. Authentication is pre-configured at ~/.gdrivelm/. Includes helper scripts for common operations and comprehensive API references. Helper script automatically detects markdown formatting and sets appropriate MIME types.
---

## Configuration

**Helper script path:**
```
/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts/gdrive_helper.py
```

**Authentication files** (use `~/.gdrivelm/` - expands to home directory):
- Credentials: `~/.gdrivelm/credentials.json`
- Settings: `~/.gdrivelm/settings.yaml`
- Token: `~/.gdrivelm/token.json` (auto-generated)

Load `references/auth_setup.md` for detailed authentication configuration.

## Helper Script Usage

Use `scripts/gdrive_helper.py` for common operations to avoid rewriting authentication and upload/download code.

### Import and Use Functions

```python
import sys
sys.path.insert(0, '/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts')
from gdrive_helper import authenticate, upload_file, download_file, search_files, get_metadata

# Authenticate once
drive = authenticate()

# Upload file
result = upload_file(drive, '/path/to/file.txt', title='My File')
print(f"Uploaded: {result['id']}")

# Search files
results = search_files(drive, "title contains 'report'")
for file in results:
    print(f"{file['title']} - {file['id']}")

# Download file
download_file(drive, 'FILE_ID', '/path/to/save.txt')

# Get metadata
metadata = get_metadata(drive, 'FILE_ID')
print(f"Size: {metadata['size']} bytes")
```

### Available Helper Functions

- `authenticate()` - Authenticate and return Drive instance
- `upload_file(drive, local_path, title=None, folder_id=None)` - Upload local file
- `upload_string(drive, content, title, folder_id=None, use_markdown=None)` - Upload string content with auto-markdown detection
- `download_file(drive, file_id, local_path)` - Download file
- `get_file_content(drive, file_id)` - Get file content as string
- `get_metadata(drive, file_id)` - Get file metadata
- `search_files(drive, query, max_results=None)` - Search for files
- `delete_file(drive, file_id, permanent=False)` - Delete or trash file
- `create_folder(drive, folder_name, parent_id=None)` - Create folder
- `list_files_in_folder(drive, folder_id)` - List files in folder

### CLI Usage

The helper script can also be used from command line:

```bash
# Activate environment first
cd ~/Desktop/zPersonalProjects/gdrivelm
source venv/bin/activate

# Run commands
python ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts/gdrive_helper.py upload /path/to/file.txt
python ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts/gdrive_helper.py search "title contains 'report'"
python ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts/gdrive_helper.py download FILE_ID /path/to/save.txt
```

## File Type Handling

Google Drive files require different retrieval methods depending on their type:

### Google Docs/Sheets/Slides (Native Google Formats)

Native Google formats require **export** with a specific MIME type, not direct download:

```python
import sys
sys.path.insert(0, '/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts')
from gdrive_helper import authenticate

drive = authenticate()

# Extract file ID from URL
file_id = '1rX7KHFnHyoAu3KrIvQgv0gJdTvMztWJT-Pkx5x954vc'

# Create file object and fetch metadata
file = drive.CreateFile({'id': file_id})
file.FetchMetadata()

# Export with appropriate MIME type
content = file.GetContentString(mimetype='text/plain')  # For Google Docs
# content = file.GetContentString(mimetype='text/csv')  # For Google Sheets
# content = file.GetContentString(mimetype='text/plain')  # For Google Slides

print(content)
```

### Regular Files (PDF, Images, Text, etc.)

Regular uploaded files can use direct download:

```python
from gdrive_helper import authenticate, get_file_content

drive = authenticate()
content = get_file_content(drive, 'FILE_ID')
```

### Usage Pattern: No Project Directory Required

**Important:** The helper scripts are globally available. You don't need to `cd` into a project directory:

```python
# ✅ CORRECT: Import from global skill path directly
import sys
sys.path.insert(0, '/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts')
from gdrive_helper import authenticate

drive = authenticate()
# Continue with operations...

# ❌ INCORRECT: Don't try to cd into project directory
# cd ~/Desktop/zPersonalProjects/gdrivelm  # This may not exist
```

## Common Operations

### Upload File from Local Path

```python
from gdrive_helper import authenticate, upload_file

drive = authenticate()
result = upload_file(drive, '/path/to/document.pdf', title='Important Document')
print(f"File ID: {result['id']}")
print(f"Link: {result['link']}")
```

### Upload String Content

The `upload_string` function automatically detects markdown formatting and sets the appropriate MIME type:

```python
from gdrive_helper import authenticate, upload_string

drive = authenticate()

# Auto-detects markdown based on content
markdown_content = """# My Document

This is a **markdown** formatted document with:
- Lists
- **Bold** text
- [Links](https://example.com)
"""

result = upload_string(drive, markdown_content, 'My Document')
print(f"Created: {result['title']}")  # Will be 'My Document.md'
print(f"MIME Type: {result['mimeType']}")  # Will be 'text/markdown'

# Force plain text (disable auto-detection)
plain_content = "This is plain text content"
result = upload_string(drive, plain_content, 'note.txt', use_markdown=False)

# Force markdown
result = upload_string(drive, "Simple text", 'doc', use_markdown=True)  # Will be 'doc.md'
```

### Search Files

```python
from gdrive_helper import authenticate, search_files

drive = authenticate()

# Search by title
results = search_files(drive, "title contains 'invoice'")

# Search by type
results = search_files(drive, "mimeType = 'application/pdf'")

# Complex search
query = "title contains 'report' and mimeType = 'application/pdf' and trashed = false"
results = search_files(drive, query)

for file in results:
    print(f"{file['title']} ({file['id']})")
```

For comprehensive search query syntax and examples, load `references/search_queries.md`.

### Download File

```python
from gdrive_helper import authenticate, download_file

drive = authenticate()
result = download_file(drive, 'FILE_ID_HERE', '/path/to/save/file.txt')
print(f"Downloaded {result['title']} to {result['local_path']}")
```

### Get File Metadata

```python
from gdrive_helper import authenticate, get_metadata

drive = authenticate()
metadata = get_metadata(drive, 'FILE_ID_HERE')

print(f"Title: {metadata['title']}")
print(f"Size: {metadata['size']} bytes")
print(f"Modified: {metadata['modified']}")
print(f"Link: {metadata['link']}")
```

### Create Folder and Upload to It

```python
from gdrive_helper import authenticate, create_folder, upload_file

drive = authenticate()

# Create folder
folder = create_folder(drive, 'My Documents')
print(f"Folder ID: {folder['id']}")

# Upload file to folder
result = upload_file(drive, '/path/to/file.txt', folder_id=folder['id'])
print(f"Uploaded to folder: {result['title']}")
```

## Advanced Usage

For direct PyDrive2 API usage and advanced features, load `references/api_reference.md`.

### Manual Authentication Pattern

If not using the helper script:

```python
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

gauth = GoogleAuth(settings_file='/Users/wz/.gdrivelm/settings.yaml')
gauth.LoadCredentialsFile('/Users/wz/.gdrivelm/token.json')

if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

gauth.SaveCredentialsFile('/Users/wz/.gdrivelm/token.json')
drive = GoogleDrive(gauth)
```

### Batch Operations

```python
from gdrive_helper import authenticate, upload_file

drive = authenticate()

files = [
    '/path/to/file1.txt',
    '/path/to/file2.pdf',
    '/path/to/file3.docx'
]

for file_path in files:
    result = upload_file(drive, file_path)
    print(f"Uploaded: {result['title']} ({result['id']})")
```

## Search Query Patterns

Common search patterns (load `references/search_queries.md` for complete syntax):

- `title contains 'text'` - Files with title containing text
- `mimeType = 'application/pdf'` - PDF files only
- `'root' in parents` - Files in root directory
- `trashed = false` - Not in trash
- `'me' in owners` - Files you own
- `modifiedDate > '2024-01-01'` - Modified after date
- `fullText contains 'keyword'` - Search file content

Combine with `and`/`or`:
```python
query = "title contains 'report' and mimeType = 'application/pdf' and trashed = false"
```

## Bundled Resources

### Scripts
- `scripts/gdrive_helper.py` - Reusable Python functions for all common operations

### References
- `references/auth_setup.md` - Complete authentication configuration guide
- `references/search_queries.md` - Comprehensive search query syntax and examples
- `references/api_reference.md` - PyDrive2 API method reference with examples

### Assets
- `assets/settings_template.yaml` - Template PyDrive2 settings file

## Workflow Guidelines

1. **Always activate the virtual environment first** before running any Google Drive code
2. **Use the helper script** for common operations to avoid rewriting code
3. **Load reference files as needed** for detailed syntax and advanced features
4. **Test with small operations first** before batch processing
5. **Check file IDs** when downloading or modifying files

## Error Handling

```python
from pydrive2.files import ApiRequestError
from gdrive_helper import authenticate, get_metadata

drive = authenticate()

try:
    metadata = get_metadata(drive, 'FILE_ID')
    print(metadata['title'])
except ApiRequestError as e:
    if e.error['code'] == 404:
        print("File not found")
    elif e.error['code'] == 403:
        print("Permission denied")
    else:
        print(f"API Error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

## Common Pitfalls

### Pitfall 1: FileNotDownloadableError with Google Docs

**Error Message:**
```
pydrive2.files.FileNotDownloadableError: No downloadLink/exportLinks for mimetype found in metadata
```

**Cause:** Using `get_file_content()` or direct download methods on native Google formats (Docs, Sheets, Slides).

**Solution:** Use `GetContentString(mimetype='...')` to export the file:

```python
# ❌ WRONG: This fails for Google Docs
from gdrive_helper import get_file_content
content = get_file_content(drive, 'GOOGLE_DOC_ID')

# ✅ CORRECT: Export with MIME type
file = drive.CreateFile({'id': 'GOOGLE_DOC_ID'})
file.FetchMetadata()
content = file.GetContentString(mimetype='text/plain')
```

### Pitfall 2: Hardcoded Project Paths

**Error Message:**
```
cd: no such file or directory: /Users/wz/Desktop/zPersonalProjects/gdrivelm
```

**Cause:** Assuming the gdrivelm project directory exists in a specific location.

**Solution:** Import from the global skill path directly (no `cd` required):

```python
# ✅ CORRECT: Works from any directory
import sys
sys.path.insert(0, '/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/google-drive/scripts')
from gdrive_helper import authenticate

# ❌ WRONG: Don't rely on project directory
# cd ~/Desktop/zPersonalProjects/gdrivelm && source venv/bin/activate
```

### Pitfall 3: Extracting File IDs from URLs

**Common patterns:**

```python
# From full URL
url = "https://docs.google.com/document/d/1rX7KHFnHyoAu3KrIvQgv0gJdTvMztWJT-Pkx5x954vc/edit"
file_id = url.split('/d/')[1].split('/')[0]  # '1rX7KHFnHyoAu3KrIvQgv0gJdTvMztWJT-Pkx5x954vc'

# From sharing URL
url = "https://drive.google.com/file/d/1ABC123xyz/view"
file_id = url.split('/d/')[1].split('/')[0]  # '1ABC123xyz'
```

## Performance Tips

1. Use helper script functions to minimize authentication overhead
2. Authenticate once and reuse the `drive` instance
3. Use specific search queries instead of listing all files
4. Batch operations when uploading/downloading multiple files
5. Cache file IDs for frequently accessed files

## Additional Documentation

For complete setup guide and test results, see:
- Project location: `~/Desktop/zPersonalProjects/gdrivelm/`
- README: `~/Desktop/zPersonalProjects/gdrivelm/README.md`
- Test script: `~/Desktop/zPersonalProjects/gdrivelm/test_gdrive.py`
- HTML documentation: `~/Desktop/zPersonalProjects/gdrivelm/claude_html/google_drive_api_setup.html`
