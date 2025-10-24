#!/usr/bin/env python3
"""
Generate simplified HTML summary for Agent Skills.

Usage:
    python3 generate-skill-html.py <skill-directory> > skill-summary.html
    open skill-summary.html
"""

import os
import sys
import subprocess
from pathlib import Path
from html import escape
from datetime import datetime


def read_skill_md(skill_path: Path) -> str:
    """Read SKILL.md content from skill directory."""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_path}")

    with open(skill_md, 'r', encoding='utf-8') as f:
        return f.read()


def get_directory_tree(skill_path: Path) -> str:
    """Get directory structure as a tree."""
    try:
        # Try using tree command (if available)
        result = subprocess.run(
            ['tree', '-L', '3', '-a', str(skill_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: use ls with recursive listing
    try:
        result = subprocess.run(
            ['ls', '-lahR', str(skill_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"[Timeout listing directory {skill_path}]"


def generate_html(skill_path: Path) -> str:
    """Generate simplified HTML summary for a skill."""

    # Read SKILL.md
    skill_content = read_skill_md(skill_path)

    # Get directory structure
    dir_tree = get_directory_tree(skill_path)

    # Escape HTML
    skill_content_escaped = escape(skill_content)
    dir_tree_escaped = escape(dir_tree)

    # Get skill name
    skill_name = skill_path.name

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skill: {skill_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background: #0d1117;
            color: #c9d1d9;
            font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Consolas', monospace;
            font-size: 13px;
            line-height: 1.5;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            color: #58a6ff;
            font-size: 24px;
            margin-bottom: 15px;
            border-bottom: 2px solid #30363d;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #58a6ff;
            font-size: 16px;
            margin: 30px 0 15px 0;
            font-weight: 600;
        }}
        .meta {{
            color: #8b949e;
            font-size: 11px;
            margin-bottom: 20px;
        }}
        pre {{
            background: #161b22;
            border: 1px solid #30363d;
            padding: 15px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            border-radius: 6px;
            margin: 10px 0;
        }}
        button {{
            background: #238636;
            color: #fff;
            border: none;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            border-radius: 6px;
            margin: 20px 0;
            font-family: inherit;
            transition: background 0.2s;
        }}
        button:hover {{
            background: #2ea043;
        }}
        button:active {{
            background: #26a641;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        code {{
            background: #161b22;
            color: #e6edf3;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        #edit-prompt {{
            display: none;
            background: #161b22;
            border: 1px solid #30363d;
            padding: 20px;
            margin: 20px 0;
            border-radius: 6px;
        }}
        #edit-prompt.show {{
            display: block;
        }}
        textarea {{
            width: 100%;
            height: 100px;
            background: #0d1117;
            color: #c9d1d9;
            border: 1px solid #30363d;
            padding: 10px;
            font-family: inherit;
            font-size: 13px;
            border-radius: 6px;
        }}
        .btn-group {{
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }}
        .btn-secondary {{
            background: #21262d;
            color: #c9d1d9;
        }}
        .btn-secondary:hover {{
            background: #30363d;
        }}
    </style>
</head>
<body>
    <h1>✨ Skill: {skill_name}</h1>
    <div class="meta">
        Location: <code>{skill_path}</code><br>
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>

    <button onclick="showEditPrompt()">✏️ Edit Skill</button>

    <div id="edit-prompt">
        <h2 style="margin-top: 0;">What changes do you want to make?</h2>
        <textarea id="changes-input" placeholder="Example: Add a section about error handling&#10;Example: Fix typo in line 42&#10;Example: Add more examples for X"></textarea>
        <div class="btn-group">
            <button onclick="generateEditScript()">📝 Generate Edit Script</button>
            <button class="btn-secondary" onclick="hideEditPrompt()">Cancel</button>
        </div>
    </div>

    <div class="section">
        <h2>📄 SKILL.md</h2>
        <pre id="skill-content">{skill_content_escaped}</pre>
    </div>

    <div class="section">
        <h2>📁 Directory Structure</h2>
        <pre id="dir-structure">{dir_tree_escaped}</pre>
    </div>

    <script>
        const SKILL_PATH = "{skill_path}";
        const SKILL_NAME = "{skill_name}";
        const SCRIPT_PATH = "{Path(__file__).parent}";

        function showEditPrompt() {{
            document.getElementById('edit-prompt').classList.add('show');
            document.getElementById('changes-input').focus();
        }}

        function hideEditPrompt() {{
            document.getElementById('edit-prompt').classList.remove('show');
            document.getElementById('changes-input').value = '';
        }}

        function generateEditScript() {{
            const changes = document.getElementById('changes-input').value.trim();

            if (!changes) {{
                alert('Please enter the changes you want to make.');
                return;
            }}

            const script = `#!/bin/bash
# Edit Skill: ${{SKILL_NAME}}
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

set -e

SKILL_PATH="${{SKILL_PATH}}"
SKILL_NAME="${{SKILL_NAME}}"
SCRIPT_PATH="${{SCRIPT_PATH}}"

# Create temp file with edit request
TEMP_FILE="/tmp/skill-edit-${{SKILL_NAME}}-${{Date.now()}}.txt"

cat > "$TEMP_FILE" << 'EDIT_REQUEST_EOF'
MANAGESKILL

I want to modify the skill: ${{SKILL_NAME}}
Location: ${{SKILL_PATH}}

Requested changes:
${{changes}}

After making the changes:
1. Regenerate HTML summary:
   cd "$SCRIPT_PATH"
   python3 generate-skill-html.py "$SKILL_PATH" > /tmp/skill-summary-new.html

2. Open the new HTML:
   open /tmp/skill-summary-new.html

3. Delete this temp file:
   rm "$TEMP_FILE"
EDIT_REQUEST_EOF

echo "✓ Edit request saved to: $TEMP_FILE"
echo ""
echo "Opening Claude Code with MANAGESKILL context..."
echo ""

# Open Claude Code (adjust based on your setup)
# Option 1: If you have 'claude' CLI
if command -v claude &> /dev/null; then
    cat "$TEMP_FILE" | claude
# Option 2: Open in Claude Desktop
elif [ -d "/Applications/Claude.app" ]; then
    open -a "Claude" "$TEMP_FILE"
# Option 3: Copy to clipboard and notify user
else
    cat "$TEMP_FILE" | pbcopy
    echo "✓ Edit request copied to clipboard!"
    echo "  Paste it into Claude Code to apply changes."
fi

echo ""
echo "Note: After Claude completes the changes, the new HTML will open automatically."
`;

            // Download the script
            const blob = new Blob([script], {{ type: 'text/plain' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `edit-${{SKILL_NAME}}.sh`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            // Show success message
            alert(`✓ Script downloaded: edit-${{SKILL_NAME}}.sh\\n\\nTo apply changes:\\n1. Open Terminal\\n2. Run: bash ~/Downloads/edit-${{SKILL_NAME}}.sh\\n3. Claude Code will open with your changes`);

            hideEditPrompt();
        }}
    </script>
</body>
</html>
"""

    return html


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 generate-skill-html.py <skill-directory>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Example:", file=sys.stderr)
        print("  python3 generate-skill-html.py ~/.claude/skills/my-skill > summary.html", file=sys.stderr)
        sys.exit(1)

    skill_path = Path(sys.argv[1]).resolve()

    if not skill_path.exists():
        print(f"Error: Directory not found: {skill_path}", file=sys.stderr)
        sys.exit(1)

    if not skill_path.is_dir():
        print(f"Error: Not a directory: {skill_path}", file=sys.stderr)
        sys.exit(1)

    try:
        html = generate_html(skill_path)
        print(html)
    except Exception as e:
        print(f"Error generating HTML: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
