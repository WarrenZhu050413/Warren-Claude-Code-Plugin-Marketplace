# PyDrive2 API Quick Reference

## Core Methods

### Create File Object

```python
# New file
file = drive.CreateFile({'title': 'filename.txt'})

# Existing file by ID
file = drive.CreateFile({'id': 'FILE_ID_HERE'})

# File in specific folder
file = drive.CreateFile({
    'title': 'filename.txt',
    'parents': [{'id': 'FOLDER_ID'}]
})
```

### Upload Operations

```python
# Upload from local file
file.SetContentFile('/path/to/local/file.txt')
file.Upload()

# Upload from string
file.SetContentString('Hello, World!')
file.Upload()

# Upload from string with markdown MIME type
file = drive.CreateFile({
    'title': 'document.md',
    'mimeType': 'text/markdown'
})
file.SetContentString('# My Document\n\nMarkdown content here')
file.Upload()

# Upload with metadata update
file['title'] = 'New Title'
file.Upload()
```

### Download Operations

```python
# Download to local file
file.GetContentFile('/path/to/download/location.txt')

# Get content as string
content = file.GetContentString()

# Get content as file object
file_obj = file.GetContentFile()  # Returns file object
```

### Metadata Operations

```python
# Fetch metadata
file.FetchMetadata()

# Access metadata fields
title = file['title']
mime_type = file['mimeType']
file_size = file['fileSize']
created = file['createdDate']
modified = file['modifiedDate']
web_link = file['alternateLink']

# Update metadata
file['title'] = 'New Title'
file['description'] = 'Updated description'
file.Upload()  # Save changes
```

### List/Search Operations

```python
# List all files
file_list = drive.ListFile().GetList()

# List with query
file_list = drive.ListFile({'q': "title contains 'report'"}).GetList()

# List with pagination
file_list = drive.ListFile({
    'q': "trashed = false",
    'maxResults': 10
}).GetList()

# Iterate through results
for file in file_list:
    print(f"{file['title']} - {file['id']}")
```

### Delete Operations

```python
# Move to trash
file.Trash()

# Permanently delete
file.Delete()

# Restore from trash
file.UnTrash()
```

### Permission Operations

```python
# Get permissions
permissions = file.GetPermissions()

# Share with specific user
permission = file.InsertPermission({
    'type': 'user',
    'value': 'user@example.com',
    'role': 'reader'
})

# Share with anyone (public)
permission = file.InsertPermission({
    'type': 'anyone',
    'role': 'reader'
})

# Remove permission
file.DeletePermission(permission_id)
```

## Metadata Fields Reference

### Common File Fields

```python
file['id']                  # File ID
file['title']               # File name
file['mimeType']           # MIME type
file['description']        # Description
file['createdDate']        # Creation timestamp
file['modifiedDate']       # Last modified timestamp
file['fileSize']           # Size in bytes
file['parents']            # Parent folder IDs
file['owners']             # Owner information
file['alternateLink']      # Web view link
file['downloadUrl']        # Direct download URL
file['thumbnailLink']      # Thumbnail URL
file['shared']             # Shared status (boolean)
file['trashed']            # Trash status (boolean)
```

## Export Google Docs

```python
# Export Google Doc as PDF
file = drive.CreateFile({'id': 'DOC_ID'})
file.GetContentFile('output.pdf', mimetype='application/pdf')

# Export Google Sheet as Excel
file.GetContentFile('output.xlsx',
    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# Export Google Slides as PowerPoint
file.GetContentFile('output.pptx',
    mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')
```

## Folder Operations

```python
# Create folder
folder = drive.CreateFile({
    'title': 'My Folder',
    'mimeType': 'application/vnd.google-apps.folder'
})
folder.Upload()

# List files in folder
file_list = drive.ListFile({
    'q': f"'{folder['id']}' in parents and trashed = false"
}).GetList()

# Upload file to folder
file = drive.CreateFile({
    'title': 'file.txt',
    'parents': [{'id': folder['id']}]
})
file.SetContentString('Content')
file.Upload()
```

## Error Handling

```python
from pydrive2.files import ApiRequestError

try:
    file = drive.CreateFile({'id': 'FILE_ID'})
    file.FetchMetadata()
except ApiRequestError as e:
    if e.error['code'] == 404:
        print("File not found")
    else:
        print(f"Error: {e}")
```

## Batch Operations

```python
# Upload multiple files
files_to_upload = [
    ('file1.txt', '/path/to/file1.txt'),
    ('file2.txt', '/path/to/file2.txt'),
]

for title, path in files_to_upload:
    file = drive.CreateFile({'title': title})
    file.SetContentFile(path)
    file.Upload()
    print(f"Uploaded {title}: {file['id']}")
```

## Advanced Features

### Resumable Upload (for large files)

```python
# PyDrive2 handles resumable uploads automatically
# Just use normal upload for large files
file = drive.CreateFile({'title': 'large_file.zip'})
file.SetContentFile('/path/to/large_file.zip')
file.Upload()  # Automatically uses resumable upload
```

### File Revisions

```python
# List revisions
revisions = file.GetRevisions()

for rev in revisions:
    print(f"Revision ID: {rev['id']}")
    print(f"Modified: {rev['modifiedDate']}")
```

### Copy File

```python
# Copy file
original = drive.CreateFile({'id': 'ORIGINAL_FILE_ID'})
copied = original.Copy()
copied['title'] = 'Copy of ' + original['title']
copied.Upload()
```

## Performance Tips

1. **Fetch only needed fields**: Use `fields` parameter
2. **Batch operations**: Group multiple API calls when possible
3. **Cache metadata**: Store frequently accessed metadata locally
4. **Use file IDs**: Faster than searching by title
