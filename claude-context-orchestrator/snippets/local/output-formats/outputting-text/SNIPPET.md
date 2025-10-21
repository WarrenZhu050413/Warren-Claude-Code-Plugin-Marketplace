---
description: Writing structured text files with markdown and XML formatting
SNIPPET_NAME: outputting-text
ANNOUNCE_USAGE: true
---

## Purpose

Write content to structured `.txt` files using markdown and XML for clarity.

## Required Actions

1. Write content to a `.txt` file (use descriptive filename)
2. **Open the file immediately** after writing using:
   - macOS: `open filename.txt`
   - Linux: `xdg-open filename.txt`
   - Windows: `start filename.txt`

## Formatting Guidelines

Use **Markdown** for structure:
```markdown
# Main Topic
## Subsection
- Bullet points for lists
- **Bold** for emphasis
- `code` for technical terms
```

Use **XML** for semantic sections:
```xml
<summary>
Brief overview of what this document explains
</summary>

<context>
Essential background information
</context>

<details>
Key points, organized clearly
</details>

<next-steps>
What to do with this information
</next-steps>
```

## Content Structure Template

```
# [Clear, Descriptive Title]

<summary>
One paragraph explaining what this is about and why it matters.
</summary>

<context>
## Background
Essential context the reader needs. What led to this? What's the situation?

## Key Concepts
- Concept 1: Brief explanation
- Concept 2: Brief explanation
</context>

<details>
## Main Content

Organized sections with clear headings. Each section should:
- Start with a clear statement
- Provide necessary details (but not excessive)
- Use examples when helpful
- Connect to the overall narrative

### Subsection 1
Content here...

### Subsection 2
Content here...
</details>

<next-steps>
## What to Do Next
1. First action
2. Second action
3. Follow-up items

## Questions to Consider
- Question 1
- Question 2
</next-steps>
```

## Example Output Flow

```bash
# 1. Write the TXT file
cat > clear_filename.txt << 'EOF'
[well-structured markdown + XML content]
EOF

# 2. Open it immediately
open clear_filename.txt

# 3. Confirm to user
echo "✅ Written to clear_filename.txt and opened for review"
```

## Combination with CLEAR

For writing style guidance (concise, direct communication), combine with CLEAR snippet: `TXT CLEAR`
