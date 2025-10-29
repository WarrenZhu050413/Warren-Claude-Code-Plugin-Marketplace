---
name: "Outputting Text"
description: "Write content to structured .txt files using markdown and XML formatting."
---

# Outputting Text

## Required Actions
1. Write to `.txt` file (descriptive filename)
2. **Open immediately:**
   - macOS: `open filename.txt`
   - Linux: `xdg-open filename.txt`
   - Windows: `start filename.txt`

## Formatting

**Markdown for structure:**
```markdown
# Main Topic
## Subsection
- Bullet points
- **Bold** for emphasis
- `code` for technical terms
```

**XML for semantic sections:**
```xml
<summary>Brief overview</summary>
<context>Background information</context>
<details>Key points</details>
<next-steps>What to do next</next-steps>
```

## Template

```
# [Title]

<summary>
One paragraph: what this is about and why it matters.
</summary>

<context>
## Background
Essential context. What led to this?

## Key Concepts
- Concept 1: Brief explanation
- Concept 2: Brief explanation
</context>

<details>
## Main Content

### Subsection 1
Content...

### Subsection 2
Content...
</details>

<next-steps>
## What to Do Next
1. First action
2. Second action

## Questions to Consider
- Question 1
- Question 2
</next-steps>
```

## Example Flow

```bash
# Write TXT file
cat > clear_filename.txt << 'EOF'
[content]
EOF

# Open immediately
open clear_filename.txt

# Confirm
echo "✅ Written to clear_filename.txt and opened for review"
```

## Combination
Use with CLEAR snippet for concise style: `TXT CLEAR`
