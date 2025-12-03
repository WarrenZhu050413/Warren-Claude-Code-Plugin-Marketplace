# Linear API Comprehensive Guide

**Tested**: October 26, 2025
**Workspace**: cs1060f25
**API Version**: GraphQL v1

---

## Table of Contents

1. [API Approaches Compared](#api-approaches-compared)
2. [Raw GraphQL (Recommended)](#raw-graphql-recommended)
3. [Python SDK (linear-py)](#python-sdk-linear-py)
4. [Advanced GraphQL Patterns](#advanced-graphql-patterns)
5. [File Upload Workflow](#file-upload-workflow)
6. [Best Practices](#best-practices)
7. [Common Gotchas](#common-gotchas)

---

## API Approaches Compared

### 1. Raw GraphQL with urllib (Python) ⭐ RECOMMENDED

**Pros:**
- Full control over all GraphQL features
- No external dependencies
- Supports file uploads, variables, custom queries
- Works with all Linear API features

**Cons:**
- More verbose code
- Manual error handling

**Use when:** Need file uploads, complex queries, or full API access

### 2. Python SDK (linear-py)

**Pros:**
- Simpler API for basic operations
- Type hints (if present)
- Less boilerplate for common tasks

**Cons:**
- Limited functionality (no file uploads, no variables in GraphQL)
- Uses snake_case (team_id) instead of GraphQL's camelCase (teamId)
- Not all issue fields supported (e.g., `estimate` parameter doesn't work)
- Last updated: Unknown (check PyPI)

**Use when:** Only need basic issue/team/project queries

### 3. TypeScript/JavaScript SDK (Official)

**Pros:**
- Officially maintained by Linear
- Full feature support
- Strong typing
- Best documentation

**Cons:**
- Requires Node.js environment
- Not useful for Python workflows

**Use when:** Building web apps or Node.js integrations

---

## Raw GraphQL (Recommended)

### Basic Setup

```python
import json
import urllib.request

LINEAR_API_KEY = "lin_api_..."

def graphql_request(query, variables=None):
    """Make a GraphQL request to Linear API"""
    url = "https://api.linear.app/graphql"

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    headers = {
        "Authorization": LINEAR_API_KEY,
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers
    )

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))
```

### Common Queries

#### Get Current User

```python
query = "{ viewer { id name email } }"
result = graphql_request(query)
user = result['data']['viewer']
```

#### Search Issue by Identifier

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
        "number": {"eq": 26}  # For UNIFIED-26
    }
}

result = graphql_request(query, variables)
issues = result['data']['issues']['nodes']

# Find exact match (handles multiple teams)
for issue in issues:
    if issue['identifier'] == "UNIFIED-26":
        found_issue = issue
        break
```

#### Create Issue

```python
mutation = """
mutation CreateIssue($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue {
      id
      identifier
      title
      url
    }
  }
}
"""

variables = {
    "input": {
        "title": "Fix authentication bug",
        "teamId": "team-id-here",
        "estimate": 3,
        "priority": 2,
        "description": "User sessions expire too quickly"
    }
}

result = graphql_request(mutation, variables)
new_issue = result['data']['issueCreate']['issue']
```

---

## Python SDK (linear-py)

### Installation

```bash
pip install linear-py
```

### Basic Usage

```python
from linear import Linear

client = Linear("lin_api_...")

# Get teams
teams = client.teams()  # Returns list of dicts
for team in teams:
    print(team['name'], team['key'])

# Get projects
projects = client.projects()

# Create issue (LIMITED - estimate parameter doesn't work!)
issue = client.create_issue(
    title="New feature",
    team_id="team-id",  # Note: snake_case, not camelCase!
    description="Description here"
)

# Raw GraphQL (but no variables support!)
result = client.query_grapql("{ viewer { name } }")
```

### SDK Limitations

**Does NOT support:**
- File uploads
- Variables in GraphQL queries (must use string interpolation - unsafe!)
- `estimate` field in create_issue
- Many advanced GraphQL features

**Conclusion:** Use SDK only for simple read operations. Use raw GraphQL for everything else.

---

## Advanced GraphQL Patterns

### 1. Pagination

```python
query = """
query GetIssuesPaginated($first: Int!, $after: String) {
  issues(first: $first, after: $after) {
    nodes {
      id
      identifier
      title
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""

# First page
result = graphql_request(query, {"first": 10})
issues = result['data']['issues']

# Next page
if issues['pageInfo']['hasNextPage']:
    result = graphql_request(query, {
        "first": 10,
        "after": issues['pageInfo']['endCursor']
    })
```

### 2. Complex Filtering

```python
query = """
query FilterIssues($filter: IssueFilter!) {
  issues(filter: $filter) {
    nodes {
      identifier
      title
      state { name }
    }
  }
}
"""

# Multiple filter conditions
variables = {
    "filter": {
        "state": {"type": {"eq": "unstarted"}},
        "team": {"key": {"eq": "UNIFIED"}},
        "estimate": {"gte": 3, "lte": 7}
    }
}
```

### 3. Nested Data with Aliases

```python
query = """
{
  teams {
    nodes {
      name
      todoIssues: issues(filter: { state: { type: { eq: "unstarted" }}}) {
        nodes {
          identifier
          title
        }
      }
      activeIssues: issues(filter: { state: { type: { eq: "started" }}}) {
        nodes {
          identifier
          title
        }
      }
    }
  }
}
"""

result = graphql_request(query)
team = result['data']['teams']['nodes'][0]
print(f"Todo: {len(team['todoIssues']['nodes'])}")
print(f"Active: {len(team['activeIssues']['nodes'])}")
```

### 4. Bulk Operations in One Request

```python
mutation = """
mutation BulkCreate($title1: String!, $title2: String!, $teamId: String!) {
  issue1: issueCreate(input: { title: $title1, teamId: $teamId }) {
    success
    issue { identifier }
  }
  issue2: issueCreate(input: { title: $title2, teamId: $teamId }) {
    success
    issue { identifier }
  }
}
"""

variables = {
    "title1": "First task",
    "title2": "Second task",
    "teamId": "team-id"
}

# Creates both issues in one API call
result = graphql_request(mutation, variables)
```

---

## File Upload Workflow

### Critical Discovery

**Google Cloud Storage signed URLs require EXACT headers** matching the cryptographic signature. Linear's API provides these headers - they MUST be included.

### Two-Step Process

#### Step 1: Get Upload URL from Linear

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

import os

file_path = "/path/to/screenshot.png"
variables = {
    "size": os.path.getsize(file_path),
    "filename": os.path.basename(file_path),
    "contentType": "image/png"
}

result = graphql_request(query, variables)
upload_data = result['data']['fileUpload']['uploadFile']
```

#### Step 2: Upload to Google Cloud Storage

**CRITICAL: Include ALL headers from Linear's response**

```python
import subprocess

# Build headers
upload_headers = {"Content-Type": "image/png"}
for header in upload_data["headers"]:
    upload_headers[header["key"]] = header["value"]

# Upload with curl (handles signed URLs correctly)
curl_cmd = [
    'curl', '-X', 'PUT',
    '-H', 'Content-Type: image/png',
    '-H', f'x-goog-content-length-range: {file_size},{file_size}',
    '-H', f'Content-Disposition: attachment; filename="{filename}"',
    '-T', file_path,
    upload_data['uploadUrl']
]

subprocess.run(curl_cmd, check=True)

# upload_data['assetUrl'] is now the permanent Linear CDN URL
```

#### Step 3: Use Asset URL in Comment

```python
mutation = """
mutation CreateComment($input: CommentCreateInput!) {
  commentCreate(input: $input) {
    success
    comment { id }
  }
}
"""

variables = {
    "input": {
        "issueId": issue_id,
        "body": f"Screenshot attached:\n\n![Screenshot]({upload_data['assetUrl']})"
    }
}

graphql_request(mutation, variables)
```

### Common Upload Errors

| Error | Cause | Solution |
|-------|-------|----------|
| HTTP 400: Bad Request | Missing required headers | Include ALL headers from Linear's API response |
| HTTP 403: Signature Does Not Match | Headers don't match signature | Don't modify header values; use exact values from API |
| Empty 200 response | Normal behavior! | This is expected. Use `assetUrl` from Step 1, not upload response |
| Expired URL | Took too long (>60s) | Get fresh upload URL before each upload |

---

## Best Practices

### 1. Error Handling

```python
def graphql_request_safe(query, variables=None):
    try:
        result = graphql_request(query, variables)

        # Check for GraphQL errors
        if 'errors' in result:
            for error in result['errors']:
                print(f"GraphQL Error: {error['message']}")
            return None

        return result

    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### 2. Rate Limiting

Linear has API rate limits. Add delays for bulk operations:

```python
import time

for item in large_list:
    result = graphql_request(mutation, {"input": item})
    time.sleep(0.5)  # 500ms delay
```

### 3. Reusable Queries with Variables

```python
# Good: Reusable with variables
query = "query GetIssue($id: String!) { issue(id: $id) { title } }"
result = graphql_request(query, {"id": issue_id})

# Bad: String interpolation (unsafe, not reusable)
query = f"{{ issue(id: \"{issue_id}\") {{ title }} }}"
result = graphql_request(query)
```

### 4. Selective Field Fetching

```python
# Good: Request only what you need
query = "{ issues(first: 10) { nodes { id title } } }"

# Bad: Over-fetching
query = "{ issues(first: 10) { nodes { id title description state { ... } team { ... } assignee { ... } } } }"
```

---

## Common Gotchas

### 1. Issue Search by Number

**Problem:** Multiple teams can have the same issue number.

**Solution:** Filter by number, then match exact identifier:

```python
# Filter returns all #26 issues across all teams
variables = {"filter": {"number": {"eq": 26}}}
result = graphql_request(query, variables)

# Find the one you want
for issue in result['data']['issues']['nodes']:
    if issue['identifier'] == "UNIFIED-26":
        found = issue
```

### 2. SDK Parameter Naming

**Problem:** linear-py uses snake_case, GraphQL uses camelCase.

```python
# SDK (snake_case)
client.create_issue(team_id="abc")

# GraphQL (camelCase)
variables = {"input": {"teamId": "abc"}}
```

### 3. File Upload Headers

**Problem:** Missing or incorrect headers cause 400/403 errors.

**Solution:** Always include x-goog-content-length-range and Content-Disposition from Linear's response.

### 4. Pagination Cursor Encoding

**Problem:** Cursor values contain special characters.

**Solution:** Don't manually construct cursors. Use `endCursor` from API response.

### 5. Mutation Success Field

**Problem:** Mutation might return `success: true` but still have errors.

**Solution:** Check both `success` field AND `errors` array:

```python
result = graphql_request(mutation, variables)
if result.get('data', {}).get('issueCreate', {}).get('success'):
    if 'errors' not in result:
        print("✅ Success")
```

---

## Testing Checklist

When working with Linear API:

- [ ] Test with real issue IDs from your workspace
- [ ] Verify team IDs match your workspace
- [ ] Check state IDs exist in your workflow
- [ ] Test file uploads with small files first (<1MB)
- [ ] Verify signed URLs expire after 60 seconds
- [ ] Handle pagination for lists >50 items
- [ ] Add error handling for all API calls
- [ ] Test rate limiting with delays

---

## Resources

- **GraphQL Docs**: https://graphql.org/learn/
- **Linear API Docs**: https://linear.app/developers
- **Schema Explorer**: https://studio.apollographql.com/public/Linear-API/variant/current/home
- **linear-py PyPI**: https://pypi.org/project/linear-py/
- **Linear JS SDK**: https://github.com/linear/linear

---

## Summary

**For Production Use:**
1. Use raw GraphQL with urllib for full control
2. Handle errors gracefully
3. Use variables for all dynamic values
4. Follow file upload headers exactly
5. Test thoroughly in your workspace

**Quick Prototyping:**
- Use linear-py SDK for simple reads
- Switch to raw GraphQL when you hit limitations

**File Uploads:**
- ALWAYS use raw GraphQL
- Include ALL headers from Linear API
- Use curl for reliable signed URL uploads
