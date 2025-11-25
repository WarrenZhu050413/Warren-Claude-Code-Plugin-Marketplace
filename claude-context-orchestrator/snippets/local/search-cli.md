---
name: "Search CLI"
description: "Use when user needs to search for books, papers, PDFs, or files. MD5-based workflow: search shows MD5 hashes, use 'search get <MD5>' to download. Supports Archive downloads (books/papers), Google Drive search, and local file search."
---

## Installation

Install globally via uv tool:

```bash
uv tool install --editable /Users/wz/Desktop/zPersonalProjects/search
```

Or:

```bash
cd /Users/wz/Desktop/zPersonalProjects/search
make install
```

## Basic Commands

### Search Archive (Books/Papers)

**MD5-based workflow** (recommended):

```bash
# Step 1: Search and get MD5 hashes
search download "godot gdscript" --max-results 10

# Output shows table with MD5 column
# Copy the MD5 hash from the table

# Step 2: Download by MD5
search get e2fb948b8fef8e99ab22124d21600711
```

**Interactive mode** (classic workflow):

```bash
search download "practical vim" --interactive
# Shows numbered list, prompts for selection, downloads immediately
```

### Search Google Drive

Search files in Drive:

```bash
search drive "meeting notes"
search drive "mimeType='application/pdf'"
search drive "project" --table
```

### Search Local Files

Find files by name or content:

```bash
search local "*.py"
search local "*.md" --grep "TODO"
search local "*.txt" --max-results 20
```

## How It Works

Search results are cached for 7 days. The `search get` command looks up the MD5 in your recent searches to download the file.

## Configuration

### First-Time Setup

```bash
search setup
```

Prompts for:
- Archive API key (default provided)
- Download directory (default: `~/Desktop/Archive`)
- Google Drive credentials (optional)

### View Current Config

```bash
search config show
```

### Set Config Values

```bash
search config set archive_api_key YOUR_KEY
search config set archive_download_dir ~/Downloads/Books
search config set default_backend drive
search config set max_results 25
```

Configuration file: `~/.search/config.json`

## Output Formats

**Default: Table format with session token**

```bash
search download "vim"
```

Shows:
- Rich-formatted table with results
- Session token for later downloads
- Usage hint

**Interactive mode:**

```bash
search download "vim" --interactive
```

Shows numbered list, prompts for selection, downloads immediately.

**JSON output:**

```bash
search download "vim" --json
```

Machine-readable format for scripting.

## Common Workflows

### Download Book (Recommended Workflow)

```bash
# 1. Search
search download "godot"

# 2. Copy MD5 from table output

# 3. Download by MD5
search get e2fb948b8fef8e99ab22124d21600711
```

### Quick Interactive Download

```bash
# Search and select interactively (classic workflow)
search download "practical vim" --interactive
```

### Find Google Drive PDFs

```bash
search drive "mimeType='application/pdf' and title contains 'report'"
```

### Search Project for TODOs

```bash
cd /path/to/project
search local "*.py" --grep "TODO"
```

### Get JSON for Scripting

```bash
search download "machine learning" --json | jq '.[0].url'
```

## Configuration Keys

Full config structure:

```json
{
  "default_backend": "archive",
  "default_output_format": "table",
  "max_results": 10,
  "archive_api_key": "YOUR_KEY",
  "archive_download_dir": "~/Desktop/Archive",
  "archive_check_duplicates": true,
  "drive_credentials_path": "~/.search/drive_credentials.json",
  "local_base_dir": "."
}
```

## Backends

### Archive

- Searches books/papers by title, author, subject
- Downloads to configured directory (default: ~/Desktop/Archive)
- Checks for duplicates before downloading
- Has daily download quota (account-dependent)

### Google Drive

- OAuth 2.0 authentication (browser opens first time)
- Supports Drive query syntax
- Shows file metadata (size, owner, dates)
- Can open files in browser

### Local Files

- Uses `find` for name patterns
- Uses `grep` for content search
- Shows match counts and line numbers
- Configurable base directory

## Troubleshooting

### "search command not found"

Reinstall:

```bash
cd /Users/wz/Desktop/zPersonalProjects/search
make install
# OR
uv tool install --force --editable .
```

### Download fails with "Invalid domain_index or path_index"

This occurs when:
- Account has no fast downloads remaining
- File not available for fast download

**Note**: The API requires valid path_index and domain_index values that vary per file. The current implementation tries multiple combinations but may fail if the account doesn't have active fast download quota.

### "API key not configured"

Set key:

```bash
search config set archive_api_key YOUR_KEY
```

### Google Drive authentication

1. Download OAuth credentials from Google Cloud Console
2. Save to `~/.search/drive_credentials.json`
3. Run any Drive search - browser opens for auth
4. Token cached in `~/.search/token.json`

### No results found

- Verify search query is correct
- Try different keywords
- Check backend is configured (run `search config show`)
- For Archive backend, verify API key is set

## Manual

View concise manual:

```bash
search manual
```

## Development

Repository location: `/Users/wz/Desktop/zPersonalProjects/search`

Local development:

```bash
cd /Users/wz/Desktop/zPersonalProjects/search
make install  # Install/reinstall
make test     # Run tests (if tests exist)
```

## Key Changes from Previous Version

1. **MD5-based workflow**: Use MD5 hashes to download (no tokens/session numbers)
2. **Archive terminology**: All user-facing text uses "Archive" instead of specific service names
3. **Download directory**: Changed from `AArchive` to `Archive`
4. **New `get` command**: `search get <MD5>` to download by hash
5. **Table format default**: Shows MD5 column for easy copy-paste

To use classic interactive workflow: Use `--interactive` flag