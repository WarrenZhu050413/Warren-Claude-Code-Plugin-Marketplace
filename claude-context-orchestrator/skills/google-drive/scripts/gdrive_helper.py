#!/usr/bin/env python3
"""
Google Drive Helper Script
Provides reusable functions for common Google Drive operations.
"""

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
import sys


def authenticate():
    """
    Authenticate with Google Drive API.

    Returns:
        GoogleDrive: Authenticated Drive instance
    """
    settings_path = os.path.expanduser('~/.gdrivelm/settings.yaml')
    token_path = os.path.expanduser('~/.gdrivelm/token.json')

    gauth = GoogleAuth(settings_file=settings_path)
    gauth.LoadCredentialsFile(token_path)

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile(token_path)
    return GoogleDrive(gauth)


def upload_file(drive, local_path, title=None, folder_id=None):
    """
    Upload a file to Google Drive.

    Args:
        drive: Authenticated GoogleDrive instance
        local_path: Path to local file
        title: Optional custom title (defaults to filename)
        folder_id: Optional parent folder ID

    Returns:
        dict: File metadata including ID
    """
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"File not found: {local_path}")

    metadata = {'title': title or os.path.basename(local_path)}
    if folder_id:
        metadata['parents'] = [{'id': folder_id}]

    file = drive.CreateFile(metadata)
    file.SetContentFile(local_path)
    file.Upload()

    return {
        'id': file['id'],
        'title': file['title'],
        'link': file.get('alternateLink', 'N/A')
    }


def upload_string(drive, content, title, folder_id=None, use_markdown=None):
    """
    Upload string content as a file to Google Drive.

    Args:
        drive: Authenticated GoogleDrive instance
        content: String content to upload
        title: File title
        folder_id: Optional parent folder ID
        use_markdown: If True, upload as markdown. If None, auto-detect based on content/title.
                     If False, upload as plain text.

    Returns:
        dict: File metadata including ID
    """
    metadata = {'title': title}
    if folder_id:
        metadata['parents'] = [{'id': folder_id}]

    # Auto-detect markdown if not specified
    if use_markdown is None:
        # Check if title ends with .md or if content has markdown formatting
        is_md_file = title.lower().endswith('.md')
        has_md_formatting = any([
            content.startswith('#'),  # Headers
            '\n#' in content,         # Headers in content
            '**' in content,          # Bold
            '__' in content,          # Bold/italic
            '- ' in content,          # Lists
            '* ' in content,          # Lists
            '```' in content,         # Code blocks
            '[' in content and '](' in content,  # Links
        ])
        use_markdown = is_md_file or has_md_formatting

    # Set MIME type based on markdown detection
    if use_markdown:
        metadata['mimeType'] = 'text/markdown'
        # Ensure title has .md extension if it's markdown
        if not title.lower().endswith('.md'):
            metadata['title'] = title + '.md'

    file = drive.CreateFile(metadata)
    file.SetContentString(content)
    file.Upload()

    return {
        'id': file['id'],
        'title': file['title'],
        'link': file.get('alternateLink', 'N/A'),
        'mimeType': file.get('mimeType', 'text/plain')
    }


def download_file(drive, file_id, local_path):
    """
    Download a file from Google Drive.

    Args:
        drive: Authenticated GoogleDrive instance
        file_id: Google Drive file ID
        local_path: Path to save downloaded file

    Returns:
        dict: File metadata
    """
    file = drive.CreateFile({'id': file_id})
    file.FetchMetadata()
    file.GetContentFile(local_path)

    return {
        'id': file['id'],
        'title': file['title'],
        'size': file.get('fileSize', 'N/A'),
        'local_path': local_path
    }


def get_file_content(drive, file_id):
    """
    Get file content as string.

    Args:
        drive: Authenticated GoogleDrive instance
        file_id: Google Drive file ID

    Returns:
        str: File content
    """
    file = drive.CreateFile({'id': file_id})
    return file.GetContentString()


def get_metadata(drive, file_id):
    """
    Get file metadata.

    Args:
        drive: Authenticated GoogleDrive instance
        file_id: Google Drive file ID

    Returns:
        dict: File metadata
    """
    file = drive.CreateFile({'id': file_id})
    file.FetchMetadata()

    return {
        'id': file['id'],
        'title': file['title'],
        'mimeType': file['mimeType'],
        'size': file.get('fileSize', 'N/A'),
        'created': file['createdDate'],
        'modified': file['modifiedDate'],
        'link': file.get('alternateLink', 'N/A'),
        'trashed': file.get('trashed', False)
    }


def search_files(drive, query, max_results=None):
    """
    Search for files in Google Drive.

    Args:
        drive: Authenticated GoogleDrive instance
        query: Search query string
        max_results: Optional limit on results

    Returns:
        list: List of file metadata dicts
    """
    params = {'q': query}
    if max_results:
        params['maxResults'] = max_results

    file_list = drive.ListFile(params).GetList()

    results = []
    for file in file_list:
        results.append({
            'id': file['id'],
            'title': file['title'],
            'mimeType': file.get('mimeType', 'N/A'),
            'modified': file.get('modifiedDate', 'N/A')
        })

    return results


def delete_file(drive, file_id, permanent=False):
    """
    Delete a file from Google Drive.

    Args:
        drive: Authenticated GoogleDrive instance
        file_id: Google Drive file ID
        permanent: If True, permanently delete; if False, move to trash

    Returns:
        bool: Success status
    """
    file = drive.CreateFile({'id': file_id})

    if permanent:
        file.Delete()
    else:
        file.Trash()

    return True


def create_folder(drive, folder_name, parent_id=None):
    """
    Create a folder in Google Drive.

    Args:
        drive: Authenticated GoogleDrive instance
        folder_name: Name for the new folder
        parent_id: Optional parent folder ID

    Returns:
        dict: Folder metadata including ID
    """
    metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    if parent_id:
        metadata['parents'] = [{'id': parent_id}]

    folder = drive.CreateFile(metadata)
    folder.Upload()

    return {
        'id': folder['id'],
        'title': folder['title'],
        'link': folder.get('alternateLink', 'N/A')
    }


def list_files_in_folder(drive, folder_id):
    """
    List all files in a specific folder.

    Args:
        drive: Authenticated GoogleDrive instance
        folder_id: Google Drive folder ID

    Returns:
        list: List of file metadata dicts
    """
    query = f"'{folder_id}' in parents and trashed = false"
    return search_files(drive, query)


def main():
    """CLI interface for testing"""
    if len(sys.argv) < 2:
        print("Usage: gdrive_helper.py <command> [args...]")
        print("\nCommands:")
        print("  upload <local_path> [title]")
        print("  download <file_id> <local_path>")
        print("  search <query>")
        print("  metadata <file_id>")
        print("  delete <file_id>")
        print("  create-folder <name>")
        sys.exit(1)

    command = sys.argv[1]
    drive = authenticate()

    if command == 'upload':
        local_path = sys.argv[2]
        title = sys.argv[3] if len(sys.argv) > 3 else None
        result = upload_file(drive, local_path, title)
        print(f"Uploaded: {result['title']}")
        print(f"ID: {result['id']}")
        print(f"Link: {result['link']}")

    elif command == 'download':
        file_id = sys.argv[2]
        local_path = sys.argv[3]
        result = download_file(drive, file_id, local_path)
        print(f"Downloaded: {result['title']}")
        print(f"Saved to: {result['local_path']}")

    elif command == 'search':
        query = sys.argv[2]
        results = search_files(drive, query)
        print(f"Found {len(results)} results:")
        for r in results:
            print(f"  [{r['id']}] {r['title']}")

    elif command == 'metadata':
        file_id = sys.argv[2]
        metadata = get_metadata(drive, file_id)
        for key, value in metadata.items():
            print(f"{key}: {value}")

    elif command == 'delete':
        file_id = sys.argv[2]
        delete_file(drive, file_id)
        print(f"Deleted file: {file_id}")

    elif command == 'create-folder':
        name = sys.argv[2]
        result = create_folder(drive, name)
        print(f"Created folder: {result['title']}")
        print(f"ID: {result['id']}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
