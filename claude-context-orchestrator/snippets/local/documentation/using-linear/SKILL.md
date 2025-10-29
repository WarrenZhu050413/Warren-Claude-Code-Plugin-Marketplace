---
name: Using Linear
description: Guide for working with Linear project management via GraphQL API. Use when creating/updating Linear issues, changing status, adding comments, or uploading files/screenshots. Covers raw GraphQL, Python SDK (linear-py), issue search, mutations, and file upload workflows with Google Cloud Storage signed URLs. Tested October 2025.
---

# Using Linear

Comprehensive guide for working with Linear project management system via GraphQL API and Python SDK.

**Last tested**: October 26, 2025
**Test workspace**: cs1060f25
**Recommended approach**: Raw GraphQL with urllib

## When to Use This Skill

Use this skill when:
- Creating or updating Linear issues programmatically
- Searching for issues by identifier or filter
- Changing issue status (e.g., marking as "Done")
- Adding comments to issues
- Uploading files or screenshots to Linear issues
- Automating Linear workflows with Python scripts

## API Approaches

### Raw GraphQL (Recommended) ⭐

**Pros**: Full feature support, file uploads, variables, no dependencies
**Cons**: More verbose
**Use when**: Need file uploads, complex queries, or full API access

```python
import json
import urllib.request

def graphql_request(query, variables=None):
    url = "https://api.linear.app/graphql"
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": "lin_api_...",
            "Content-Type": "application/json"
        }
    )

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))
```

### Python SDK (linear-py)

**Pros**: Simpler API for basic operations
**Cons**: No file uploads, no variables in queries, limited field support (no `estimate`!)
**Use when**: Only need simple reads

```python
from linear import Linear

client = Linear("lin_api_...")
teams = client.teams()  # Returns list of dicts
```

**SDK Limitations**:
- Uses snake_case (`team_id`) not camelCase (`teamId`)
- Cannot pass variables to GraphQL queries
- No file upload support
- `estimate` parameter doesn't work in create_issue

**Recommendation**: Use raw GraphQL for any real work. SDK only for quick prototypes.

### Comprehensive Guide

See `references/linear-api-comprehensive-guide.md` for:
- Detailed SDK comparison with tested examples
- Advanced GraphQL patterns (pagination, filtering, bulk operations)
- File upload workflow variations
- Common gotchas and solutions
- Testing results from cs1060f25 workspace

## API Authentication

Linear uses API tokens for authentication. Include the token in request headers:

```python
headers = {
    "Authorization": "lin_api_...",
    "Content-Type": "application/json"
}
```

**API Endpoint**: `https://api.linear.app/graphql`

## Common Operations

### 1. Search for Issue by Identifier

To find an issue like "UNIFIED-26":

```python
query = """
query SearchIssues($filter: IssueFilter!) {
  issues(filter: $filter) {
    nodes {
      id
      identifier
      title
    }
  }
}
"""

variables = {
    "filter": {
        "number": {"eq": 26}  # Extract number from "UNIFIED-26"
    }
}

result = graphql_request(query, variables)

# Find exact match
for issue in result["data"]["issues"]["nodes"]:
    if issue["identifier"] == "UNIFIED-26":
        return issue
```

**Important**: Filter by number first, then match exact identifier to handle multiple teams.

### 2. Update Issue Status

To mark an issue as "Done":

```python
mutation = """
mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
  issueUpdate(id: $id, input: $input) {
    success
    issue {
      id
      state {
        name
      }
    }
  }
}
"""

variables = {
    "id": issue_id,
    "input": {
        "stateId": "done_state_id"  # Get from team workflow states
    }
}
```

### 3. Add Comment to Issue

To add a text comment (supports Markdown):

```python
mutation = """
mutation CreateComment($input: CommentCreateInput!) {
  commentCreate(input: $input) {
    success
    comment {
      id
      body
    }
  }
}
"""

variables = {
    "input": {
        "issueId": issue_id,
        "body": "Comment text with **Markdown** support"
    }
}
```

## File Upload Workflow

Uploading files to Linear requires a two-step process with Google Cloud Storage signed URLs.

### Overview

1. Request upload URL from Linear GraphQL API
2. Upload file to Google Cloud Storage with required headers
3. Use returned asset URL in comments or issue descriptions

### Critical Discovery: Required Headers

**Google Cloud Storage signed URLs require EXACT headers** that match the cryptographic signature. Linear's API provides these headers - they MUST be included in the upload request.

### Step 1: Request Upload URL

Query Linear's `fileUpload` mutation with file metadata:

```python
query = """
mutation FileUpload($size: Int!, $filename: String!, $contentType: String!) {
  fileUpload(size: $size, filename: $filename, contentType: $contentType) {
    success
    uploadFile {
      uploadUrl
      assetUrl
      headers {
        key
        value
      }
    }
  }
}
"""

variables = {
    "size": os.path.getsize(file_path),
    "filename": os.path.basename(file_path),
    "contentType": "image/png"  # or appropriate MIME type
}

result = graphql_request(query, variables)
upload_data = result["data"]["fileUpload"]["uploadFile"]
```

**Response includes**:
- `uploadUrl`: Google Cloud Storage signed URL (valid for 60 seconds)
- `assetUrl`: Final Linear CDN URL for the uploaded file
- `headers`: Array of required headers for upload

### Step 2: Upload File with Required Headers

**Critical**: Include ALL headers returned by Linear API:

```bash
curl -X PUT \
  -H "Content-Type: image/png" \
  -H "x-goog-content-length-range: [exact_size],[exact_size]" \
  -H 'Content-Disposition: attachment; filename="..."' \
  -T /path/to/file \
  "[uploadUrl]"
```

**Headers breakdown**:
1. `Content-Type`: Must match `contentType` from mutation (part of signature)
2. `x-goog-content-length-range`: Exact file size range (provided by Linear)
3. `Content-Disposition`: Filename for download (provided by Linear)

**Python example using urllib**:

```python
import urllib.request

# Build headers from Linear's response
upload_headers = {"Content-Type": "image/png"}
for header in upload_data["headers"]:
    upload_headers[header["key"]] = header["value"]

# Read file
with open(file_path, 'rb') as f:
    file_data = f.read()

# Upload with PUT request
req = urllib.request.Request(
    upload_data["uploadUrl"],
    data=file_data,
    headers=upload_headers,
    method='PUT'
)

with urllib.request.urlopen(req) as response:
    if response.status in [200, 201]:
        print(f"✅ Upload successful")
        asset_url = upload_data["assetUrl"]
```

### Step 3: Use Asset URL in Comments

Embed the uploaded image in a comment using Markdown:

```python
comment_body = f"""✅ Screenshot uploaded

![Description]({asset_url})"""

# Add comment with embedded image
mutation = """
mutation CreateComment($input: CommentCreateInput!) {
  commentCreate(input: $input) {
    success
  }
}
"""

variables = {
    "input": {
        "issueId": issue_id,
        "body": comment_body
    }
}
```

## Common Errors and Solutions

### HTTP 400: Bad Request (File Upload)

**Cause**: Missing required headers or header mismatch

**Solution**:
1. Check that `headers` field is included in `fileUpload` mutation query
2. Add ALL headers from Linear's response to upload request
3. Ensure `Content-Type` matches exactly

### HTTP 403: Signature Does Not Match

**Cause**: Headers don't match signed URL signature

**Solution**:
- Ensure headers are added in exact order
- Don't modify header values
- Upload file within 60-second window (signed URLs expire)

### Upload Succeeds but Returns Empty Response

**Expected behavior**: Google Cloud Storage returns empty 200 response on success. Use the `assetUrl` from Step 1, not the upload response.

## Python Template

Complete working example in `scripts/upload_to_linear.py` demonstrates:
- GraphQL request wrapper
- Issue search by identifier
- File upload with proper headers
- Comment creation with embedded image

Use this template as a reference for Linear automation workflows.

## Tips and Best Practices

1. **Signed URL expiration**: Upload URLs expire in 60 seconds. Get fresh URL for each upload.

2. **File size**: Include exact file size in mutation. Linear uses this for `x-goog-content-length-range` header.

3. **Error handling**: Linear API returns detailed error messages in GraphQL response `errors` field.

4. **Rate limiting**: Linear has API rate limits. Add delays between bulk operations.

5. **Testing**: Use Linear's GraphQL explorer at https://linear.app/your-workspace/settings/api for query testing.

6. **Asset URLs**: Linear asset URLs are permanent CDN links. Safe to store in documentation or external systems.

## Reference Script

See `scripts/upload_to_linear.py` for complete implementation with error handling and retry logic.
