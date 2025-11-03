"""Hashing utilities for snippet verification."""

import hashlib
import re
from typing import Optional


def compute_verification_hash(content: str) -> str:
    """Compute verification hash for snippet content.

    Creates a stable hash by:
    1. Removing existing verification hash lines
    2. Normalizing whitespace
    3. Computing MD5 hash of first 8 characters

    Args:
        content: Snippet file content

    Returns:
        8-character hexadecimal hash string
    """
    # Remove existing verification hash line (allow any characters in hash value)
    content_to_hash = re.sub(
        r'\*\*VERIFICATION_HASH:\*\*\s*`[^`]+`\s*\n?',
        '',
        content,
        flags=re.IGNORECASE
    )

    # Normalize whitespace
    content_to_hash = content_to_hash.strip()

    # Compute MD5 hash
    hash_obj = hashlib.md5(content_to_hash.encode('utf-8'))
    return hash_obj.hexdigest()[:8]


def extract_verification_hash(content: str) -> Optional[str]:
    """Extract verification hash from snippet content.

    Args:
        content: Snippet file content

    Returns:
        Hash string if found, None otherwise
    """
    match = re.search(
        r'\*\*VERIFICATION_HASH:\*\*\s*`([a-f0-9]+)`',
        content,
        flags=re.IGNORECASE
    )
    return match.group(1) if match else None


def update_verification_hash(content: str, new_hash: str) -> str:
    """Update or add verification hash in content.

    Args:
        content: Original snippet content
        new_hash: New hash to insert

    Returns:
        Updated content with hash
    """
    hash_line = f"**VERIFICATION_HASH:** `{new_hash}`"

    # Check if hash already exists (allow any characters in hash value)
    if re.search(r'\*\*VERIFICATION_HASH:\*\*', content, flags=re.IGNORECASE):
        # Replace existing hash
        return re.sub(
            r'\*\*VERIFICATION_HASH:\*\*\s*`[^`]+`',
            hash_line,
            content,
            flags=re.IGNORECASE
        )
    else:
        # Add hash after frontmatter if it exists
        if content.strip().startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                # Has frontmatter
                return f"---{parts[1]}---\n\n{hash_line}\n\n{parts[2].lstrip()}"

        # No frontmatter, add at the beginning
        return f"{hash_line}\n\n{content.lstrip()}"


def verify_hash(content: str) -> bool:
    """Verify that content hash matches embedded hash.

    Args:
        content: Snippet content with embedded hash

    Returns:
        True if hash matches, False otherwise
    """
    embedded_hash = extract_verification_hash(content)
    if not embedded_hash:
        return False

    computed_hash = compute_verification_hash(content)
    return embedded_hash == computed_hash
