"""Email style business logic for gmaillm."""

import yaml
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console

from gmaillm.helpers.core.paths import get_styles_dir

console = Console()


def load_all_styles(styles_dir: Path) -> List[Dict[str, Any]]:
    """Load all style files and extract metadata.

    Args:
        styles_dir: Directory containing style files

    Returns:
        List of style metadata dictionaries (excludes backup files)
    """
    styles = []
    for style_file in styles_dir.glob("*.md"):
        # Skip backup files (*.backup.*.md)
        if ".backup." in style_file.name:
            continue

        try:
            metadata = extract_style_metadata(style_file)
            styles.append({
                'name': style_file.stem,
                'description': metadata.get('description', 'No description'),
                'path': style_file,
            })
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load {style_file}: {e}[/yellow]")
    return sorted(styles, key=lambda x: x['name'])


def extract_style_metadata(style_file: Path) -> Dict[str, str]:
    """Extract YAML frontmatter metadata from style file.

    Args:
        style_file: Path to style file

    Returns:
        Dictionary of metadata fields
    """
    content = style_file.read_text()

    # Check for YAML frontmatter
    if content.startswith('---'):
        try:
            end_idx = content.index('\n---\n', 3)
            frontmatter = content[3:end_idx]
            return yaml.safe_load(frontmatter)
        except Exception:
            pass

    # Fallback: minimal metadata
    return {'name': style_file.stem, 'description': 'No description'}


def create_style_from_template(name: str, output_path: Path) -> None:
    """Create new style file from default template.

    Args:
        name: Name of the style
        output_path: Path where style file should be created
    """
    template = """---
name: "{name}"
description: "When to use: [Describe the context and recipients for this style]. [Characteristics of this style]."
---

<examples>
Hi [Name],

[Example email body goes here]

Best,
Warren
---
[Optional second example]
</examples>

<greeting>
- "Hi [Name],"
- "Hello [Name],"
</greeting>

<body>
- Keep sentences clear and concise
- Use active voice
- Organize with paragraphs or bullet points
</body>

<closing>
- "Best,"
- "Thank you,"
</closing>

<do>
- Be direct about requests
- Use appropriate formality for recipient
- Proofread before sending
</do>

<dont>
- Use overly casual language inappropriately
- Write excessively long paragraphs
- Forget to include next steps or action items
</dont>
"""
    output_path.write_text(template.format(name=name))
