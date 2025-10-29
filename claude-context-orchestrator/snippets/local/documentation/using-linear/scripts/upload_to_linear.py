#!/usr/bin/env python3
"""
Upload files to Linear issues with proper header handling for Google Cloud Storage.

This script demonstrates the complete workflow for:
1. Searching for Linear issues by identifier
2. Uploading files to Linear's Google Cloud Storage backend
3. Adding comments with embedded images

Key discovery: Google Cloud Storage signed URLs require exact headers
that match the cryptographic signature. Linear provides these headers
in the fileUpload mutation response.
"""

import json
import urllib.request
import os
import sys

def graphql_request(api_key, query, variables=None):
    """
    Make a GraphQL request to Linear API.

    Args:
        api_key: Linear API key (format: lin_api_...)
        query: GraphQL query string
        variables: Optional variables dict for the query

    Returns:
        Parsed JSON response
    """
    url = "https://api.linear.app/graphql"

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(f"Response: {e.read().decode('utf-8')}")
        raise

def search_issue_by_identifier(api_key, identifier):
    """
    Search for a Linear issue by identifier (e.g., "UNIFIED-26").

    Args:
        api_key: Linear API key
        identifier: Issue identifier (e.g., "UNIFIED-26")

    Returns:
        Issue dict with id, identifier, and title, or None if not found
    """
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

    # Extract number from identifier (e.g., 26 from "UNIFIED-26")
    number = int(identifier.split("-")[1])

    variables = {
        "filter": {
            "number": {"eq": number}
        }
    }

    result = graphql_request(api_key, query, variables)
    issues = result.get("data", {}).get("issues", {}).get("nodes", [])

    # Find exact match (handles multiple teams with same number)
    for issue in issues:
        if issue["identifier"] == identifier:
            return issue

    return None

def upload_file_to_linear(api_key, file_path):
    """
    Upload a file to Linear and return the asset URL.

    This implements the two-step upload process:
    1. Request upload URL from Linear GraphQL API
    2. Upload file to Google Cloud Storage with required headers

    Args:
        api_key: Linear API key
        file_path: Path to file to upload

    Returns:
        Asset URL (Linear CDN URL) if successful, None otherwise
    """
    # Step 1: Request upload URL from Linear
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

    file_size = os.path.getsize(file_path)
    filename = os.path.basename(file_path)

    # Determine content type (extend as needed)
    content_type = "image/png"
    if filename.endswith(".jpg") or filename.endswith(".jpeg"):
        content_type = "image/jpeg"
    elif filename.endswith(".pdf"):
        content_type = "application/pdf"

    variables = {
        "size": file_size,
        "filename": filename,
        "contentType": content_type
    }

    result = graphql_request(api_key, query, variables)

    if not result.get("data", {}).get("fileUpload", {}).get("success"):
        print(f"Failed to get upload URL from Linear")
        return None

    upload_data = result["data"]["fileUpload"]["uploadFile"]
    upload_url = upload_data["uploadUrl"]
    asset_url = upload_data["assetUrl"]

    # Step 2: Upload file to Google Cloud Storage
    # CRITICAL: Include ALL headers provided by Linear
    upload_headers = {"Content-Type": content_type}
    for header in upload_data.get("headers", []):
        upload_headers[header["key"]] = header["value"]

    with open(file_path, 'rb') as f:
        file_data = f.read()

    req = urllib.request.Request(
        upload_url,
        data=file_data,
        headers=upload_headers,
        method='PUT'
    )

    try:
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 201]:
                print(f"✅ Uploaded: {filename}")
                return asset_url
            else:
                print(f"❌ Upload failed: HTTP {response.status}")
                return None
    except urllib.error.HTTPError as e:
        print(f"❌ Upload error: {e.code}")
        print(f"Response: {e.read().decode('utf-8')}")
        return None

def add_comment_with_image(api_key, issue_id, comment_text, image_url):
    """
    Add a comment with an embedded image to a Linear issue.

    Args:
        api_key: Linear API key
        issue_id: Linear issue ID
        comment_text: Comment text (supports Markdown)
        image_url: URL of uploaded image (from upload_file_to_linear)

    Returns:
        True if successful, False otherwise
    """
    # Markdown format for embedded image
    body = f"""{comment_text}

![Screenshot]({image_url})"""

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
            "body": body
        }
    }

    result = graphql_request(api_key, mutation, variables)

    if result.get("data", {}).get("commentCreate", {}).get("success"):
        print(f"✅ Comment added to issue")
        return True
    else:
        print(f"❌ Failed to add comment")
        return False

def main():
    """
    Example usage: Upload screenshot to Linear issue.
    """
    if len(sys.argv) < 4:
        print("Usage: python upload_to_linear.py <api_key> <issue_identifier> <file_path> [comment]")
        print("Example: python upload_to_linear.py lin_api_... UNIFIED-26 screenshot.png 'Test results'")
        sys.exit(1)

    api_key = sys.argv[1]
    issue_identifier = sys.argv[2]
    file_path = sys.argv[3]
    comment_text = sys.argv[4] if len(sys.argv) > 4 else "Screenshot uploaded"

    print(f"Processing {issue_identifier}...")

    # Step 1: Find the issue
    issue = search_issue_by_identifier(api_key, issue_identifier)
    if not issue:
        print(f"❌ Issue {issue_identifier} not found")
        sys.exit(1)

    print(f"Found: {issue['title']}")

    # Step 2: Upload the file
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    image_url = upload_file_to_linear(api_key, file_path)
    if not image_url:
        print(f"❌ Failed to upload file")
        sys.exit(1)

    # Step 3: Add comment with image
    success = add_comment_with_image(api_key, issue['id'], comment_text, image_url)

    if success:
        print(f"\n✅ Complete! View at: https://linear.app")
        print(f"Asset URL: {image_url}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
