"""Email body parsing utilities for extracting new content and removing quotes.

This module provides functionality to parse email bodies and extract only the
new content, removing quoted replies and attribution lines.
"""

import re


class EmailBodyParser:
    """Parser for extracting new content from email bodies."""

    # Common attribution patterns (Gmail, Outlook, Apple Mail, etc.)
    ATTRIBUTION_PATTERNS = [
        r'^On .+? wrote:',                          # English Gmail, Apple Mail
        r'^El El .+? <.+?>$',                       # Spanish Gmail line 1 (El El [date] [name] <email>)
        r'^escribió:$',                             # Spanish Gmail line 2
        r'^El .+? escribió:',                       # Spanish Gmail (single line)
        r'^Am .+? schrieb .+?:',                    # German
        r'^Le .+? a écrit :',                       # French
        r'^From: .+?Sent: .+?To: .+?Subject:',      # Outlook
        r'^_{5,}.*?Original Message.*?_{5,}',       # Outlook delimiter
        r'^-+ Forwarded message -+',                # Forwarded emails
    ]

    def extract_new_content_plain(self, body: str) -> str:
        """Extract new content from plain text email, removing quotes.

        Args:
            body: Plain text email body

        Returns:
            New content only, with quotes and attribution removed

        """
        if not body:
            return ''

        lines = body.split('\n')
        new_content_lines = []

        for line in lines:
            # Strip line for checking (but preserve original for output)
            stripped = line.strip()

            # Check if this is a quoted line (starts with >)
            if stripped.startswith('>'):
                break

            # Check if this matches any attribution pattern
            if self._matches_attribution_pattern(stripped):
                break

            # This is new content, keep it
            new_content_lines.append(line)

        # Join lines and strip trailing whitespace
        result = '\n'.join(new_content_lines)
        return result.strip()

    def _matches_attribution_pattern(self, line: str) -> bool:
        """Check if line matches any known attribution pattern.

        Args:
            line: Line to check

        Returns:
            True if line is an attribution line

        """
        for pattern in self.ATTRIBUTION_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False
