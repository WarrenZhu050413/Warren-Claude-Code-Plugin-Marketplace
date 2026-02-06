---
name: "Creating Issues"
description: "Create GitHub issues (feature requests or bug reports) by learning from existing issue formats in the repository."
---

# Creating Issues

## Phase 1: Search Duplicates (MANDATORY)

**CRITICAL**: Always search exhaustively BEFORE creating a new issue. Many issues have already been reported. Adding a +1 to an existing issue is MORE valuable than creating a duplicate.

**1. Determine type:**
- Feature request: New functionality, enhancement
- Bug report: Broken, not working, error

**2. Search with MULTIPLE keyword variations:**
```bash
# Search at least 3-5 different keyword combinations
gh search issues --repo anthropics/claude-code "input buffer" --limit 15
gh search issues --repo anthropics/claude-code "text disappear" --limit 15
gh search issues --repo anthropics/claude-code "prompt lost" --limit 15
gh search issues --repo anthropics/claude-code "race condition" --limit 15
```

**Keyword strategy:**
- Use synonyms (input/prompt/text, lost/disappear/cleared)
- Try both technical terms ("race condition", "buffer") and user descriptions ("disappears", "gone")
- Search for the symptom AND the cause

**3. Check duplicates thoroughly:**
- Show similar issues (titles, URLs)
- View potential duplicates: `gh issue view --repo anthropics/claude-code [number] --comments`
- Follow duplicate chains (issues often reference canonical issues)
- Check if user already engaged (commented, reacted)
- Ask: "Do any match what you're reporting?"

**4. If duplicate found:**
- Not engaged: Add detailed +1 comment with your specific scenario
  ```bash
  gh issue comment --repo anthropics/claude-code [number] --body "+1 Still experiencing this in v2.x. [Add your specific details]"
  ```
- Already engaged: Note participation, end workflow

**5. Only proceed to Phase 2 if NO duplicates found after thorough search.**

## Phase 2: Learn Format

**CRITICAL:** Don't impose fixed template. Learn from repo.

**1. Fetch similar issues:**
```bash
# Feature requests
gh search issues --repo anthropics/claude-code "is:issue label:enhancement" --limit 5

# Bug reports
gh search issues --repo anthropics/claude-code "is:issue label:bug" --limit 5
```

**2. Analyze structure:**
```bash
gh issue view --repo anthropics/claude-code [number]
```

**3. Identify patterns:**
- Sections used (Problem, Solution, Steps to Reproduce)
- Detail level (brief vs comprehensive)
- Checklists, code blocks, examples
- Tone (formal vs casual)
- Component tags

**4. Extract template:**
- Consistent sections
- Optional vs required
- Markdown patterns

## Phase 3: Draft Issue

**1. Apply learned structure:**
- Match repository patterns
- Match detail level
- Use similar formatting
- Adopt appropriate tone

**2. Feature Request Structure** (adapt):
```markdown
## Problem / Use Case
[What trying to do or what's missing]

## Proposed Solution
[What to add or change]

## Example Usage
[Concrete example]

## Additional Context
[Optional: screenshots, related issues]
```

**3. Bug Report Structure** (adapt):
```markdown
## Description
[What's happening vs should happen]

## Steps to Reproduce
1. [First]
2. [Second]
3. [Third]

## Expected / Actual Behavior
Expected: [what should happen]
Actual: [what happens]

## Environment
- Claude Code version: [version]
- OS: [OS]

## Additional Context
[Optional: errors, screenshots, logs]
```

**4. Gather information:**
- Ask clarifying questions based on learned format
- Request details from similar issues
- Keep conversational

## Phase 4: Preview & Refine

**1. Show draft:**
```
════════════════════════════════════════
📋 DRAFT ISSUE: [Type]
════════════════════════════════════════
🏷️  TITLE: [Clear, searchable title]

📝 BODY:
[Full content]

📊 METADATA:
- Type: [Feature/Bug]
- Labels: [Suggested]
- Similar: [Related issue numbers]
════════════════════════════════════════
```

**2. Get feedback:**
- "Does this capture what you want?"
- "Submit or adjust?"

**3. Iterate if needed**

## Phase 5: Submit

**1. Only with explicit approval** ("yes", "submit", "go ahead")

**2. Create:**
```bash
gh issue create \
  --repo anthropics/claude-code \
  --title "[title]" \
  --body "$(cat <<'EOF'
[content]
EOF
)"
```

**3. Confirm:**
```
✅ Issue #[number]: [title]
🔗 URL: [URL]

View: gh issue view --repo anthropics/claude-code [number]
```

## Advanced

**Specific issue format:**
```bash
gh issue view --repo anthropics/claude-code [reference-number]
```

**Other repos:**
```bash
gh search issues --repo [owner/repo] "{terms}"
```

**Label suggestions:**
```bash
gh label list --repo anthropics/claude-code
# Suggest: bug, enhancement, documentation, plugin, mcp, hooks
```

## Best Practices

**Feature Requests:**
- Start with "why"
- Concrete examples
- Open to alternatives
- Link related issues
- Consider scope

**Bug Reports:**
- Exact steps
- Include context (version, OS)
- Actual vs expected
- Evidence (errors, screenshots)
- Minimal reproduction

**General:**
- Clear, searchable titles
- One issue per report
- Search first
- Be respectful
- Follow up

## Quick Reference

```bash
# Search (use MULTIPLE variations)
gh search issues --repo anthropics/claude-code "{terms}" --limit 15
gh search issues --repo anthropics/claude-code "{synonym1}" --limit 15
gh search issues --repo anthropics/claude-code "{synonym2}" --limit 15

# View with comments (to check for user engagement)
gh issue view --repo anthropics/claude-code [number] --comments

# +1 existing issue (PREFERRED over creating duplicate)
gh issue comment --repo anthropics/claude-code [number] --body "+1 Still experiencing this. [specific details]"

# Create (only after exhaustive search)
gh issue create --repo anthropics/claude-code --title "Title" --body "Body"

# Labels
gh label list --repo anthropics/claude-code
```
