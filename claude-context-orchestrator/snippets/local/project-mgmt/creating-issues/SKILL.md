---
description: Comprehensive guidance for creating GitHub issues by learning from existing formats
SNIPPET_NAME: creating-issues
ANNOUNCE_USAGE: false
---

# GitHub Issue Creation Guide

## Overview

This snippet provides comprehensive guidance for creating GitHub issues (feature requests OR bug reports) by learning from existing issue formats in the repository.

## Core Workflow

### Phase 1: Understand Intent & Search for Duplicates

1. **Determine issue type:**
   - Feature request: New functionality, enhancement, improvement
   - Bug report: Something broken, not working as expected, error

2. **Search for existing issues:**
   ```bash
   # Search issues in the repository
   gh search issues --repo anthropics/claude-code "{key terms}" --limit 15

   # Try multiple search strategies:
   # - Core keywords from user's description
   # - Alternative phrasings
   # - Related technical terms
   ```

3. **Check for duplicates:**
   - Show user similar issues with titles and URLs
   - For each potential duplicate:
     ```bash
     gh issue view --repo anthropics/claude-code [issue-number] --comments
     ```
   - Check if user has already engaged (commented, reacted)
   - Ask: "Do any of these match what you're reporting?"

4. **If duplicate found:**
   - If not engaged: Offer to add +1 reaction/comment
     ```bash
     gh issue comment --repo anthropics/claude-code [issue-number] --body "+1"
     ```
   - If already engaged: Note they've already participated
   - End workflow

### Phase 2: Learn from Existing Issue Formats

**CRITICAL**: Don't impose a fixed template. Learn from what the repo uses.

1. **Fetch recent similar issues:**
   ```bash
   # For feature requests, search for feature requests
   gh search issues --repo anthropics/claude-code "is:issue label:enhancement" --limit 5

   # For bug reports, search for bug reports
   gh search issues --repo anthropics/claude-code "is:issue label:bug" --limit 5
   ```

2. **Analyze issue structure:**
   ```bash
   # Get full content of 2-3 recent issues
   gh issue view --repo anthropics/claude-code [issue-number]
   ```

3. **Identify common patterns:**
   - What sections do they use? (e.g., "Problem", "Proposed Solution", "Steps to Reproduce")
   - How detailed are descriptions? (brief vs comprehensive)
   - Do they use checklists, code blocks, examples?
   - What tone/style? (formal vs casual)
   - Do they tag components/areas?

4. **Extract format template:**
   - Note which sections appear consistently
   - Identify optional vs required sections
   - Observe markdown formatting patterns

### Phase 3: Draft Issue Using Learned Format

1. **Apply learned structure:**
   - Use sections that match repository patterns
   - Match the level of detail (don't over-specify or under-specify)
   - Use similar markdown formatting
   - Adopt appropriate tone

2. **Feature Request Example Structure** (adapt based on what you learned):
   ```markdown
   ## Problem / Use Case
   [Brief description of what you're trying to do or what's missing]

   ## Proposed Solution
   [What you'd like to see added or changed]

   ## Example Usage
   [Concrete example of how you'd use this]

   ## Additional Context
   [Optional: screenshots, related issues, alternatives considered]
   ```

3. **Bug Report Example Structure** (adapt based on what you learned):
   ```markdown
   ## Description
   [What's happening vs what should happen]

   ## Steps to Reproduce
   1. [First step]
   2. [Second step]
   3. [Third step]

   ## Expected Behavior
   [What should happen]

   ## Actual Behavior
   [What actually happens]

   ## Environment
   - Claude Code version: [version]
   - OS: [operating system]
   - [Other relevant details]

   ## Additional Context
   [Optional: error messages, screenshots, logs]
   ```

4. **Gather information from user:**
   - Ask clarifying questions based on learned format
   - Request specific details that appear in similar issues
   - Keep it conversational - don't interrogate

### Phase 4: Preview & Refine

1. **Show complete draft:**
   ```
   ═══════════════════════════════════════════════════════════
   📋 DRAFT ISSUE: [Type: Feature Request / Bug Report]
   ═══════════════════════════════════════════════════════════

   🏷️  TITLE: [Clear, searchable title]

   📝 BODY:
   ─────────────────────────────────────────────────────────
   [Full issue content following learned format]
   ─────────────────────────────────────────────────────────

   📊 METADATA:
   - Type: [Feature Request / Bug Report]
   - Labels: [Suggested labels based on similar issues]
   - Similar to: [Issue numbers of related issues]

   ═══════════════════════════════════════════════════════════
   ```

2. **Get feedback:**
   - "Does this capture what you want to report?"
   - "Should I submit, or would you like to adjust anything?"
   - "Do you want to add any additional context?"

3. **Iterate if needed:**
   - Make requested changes
   - Show updated version
   - Re-confirm

### Phase 5: Submit Issue

1. **Only submit with explicit approval:**
   - User must say "yes", "submit", "go ahead", or similar
   - Never submit without confirmation

2. **Create issue:**
   ```bash
   gh issue create \
     --repo anthropics/claude-code \
     --title "[Clear title here]" \
     --body "$(cat <<'EOF'
   [Full issue content]
   EOF
   )"
   ```

3. **Confirm submission:**
   ```
   ✅ Issue created successfully!

   🔗 Issue #[number]: [title]
   🔗 URL: [full GitHub URL]

   💡 You can:
   - View: gh issue view --repo anthropics/claude-code [number]
   - Edit: gh issue edit --repo anthropics/claude-code [number]
   - Comment: gh issue comment --repo anthropics/claude-code [number]
   ```

## Advanced Features

### Learning from Specific Issues

If user references a specific issue format they like:

```bash
# Get that issue's format
gh issue view --repo anthropics/claude-code [reference-issue-number]

# Use it as the template
```

### Multi-Repository Support

While default is `anthropics/claude-code`, support other repos:

```bash
# User specifies different repo
gh search issues --repo [owner/repo] "{terms}"
gh issue create --repo [owner/repo] ...
```

### Label Suggestions

Based on issue content, suggest appropriate labels:

```bash
# View available labels
gh label list --repo anthropics/claude-code

# Suggest based on content analysis
# - "bug" for bug reports
# - "enhancement" for features
# - "documentation" if docs-related
# - Component labels (e.g., "plugin", "mcp", "hooks")
```

## Best Practices

### For Feature Requests

1. **Start with "why"** - explain the problem or use case
2. **Provide concrete examples** - show how you'd use it
3. **Be open to alternatives** - there may be existing solutions
4. **Check related issues** - link to similar requests
5. **Consider scope** - is this a small tweak or major feature?

### For Bug Reports

1. **Be specific** - exact steps to reproduce
2. **Include context** - version, OS, environment
3. **Show actual vs expected** - what happens vs what should happen
4. **Provide evidence** - error messages, screenshots, logs
5. **Isolate the issue** - minimal reproduction case

### General Guidelines

1. **Clear titles** - descriptive, searchable, specific
2. **One issue per report** - don't combine multiple requests
3. **Search first** - avoid duplicates
4. **Be respectful** - maintainers are volunteers
5. **Follow up** - respond to questions, provide updates

## Common Patterns

### Title Formats

**Feature Requests:**
- "Add support for [feature]"
- "Allow [action] when [condition]"
- "Improve [component] to [benefit]"

**Bug Reports:**
- "[Component] fails when [condition]"
- "Error: [brief error] in [component]"
- "[Action] produces unexpected [result]"

### Markdown Elements

**Code Blocks:**
```bash
# Command examples
claude --debug -p "test"
```

```json
// Configuration examples
{
  "setting": "value"
}
```

**Checklists:**
- [ ] Task one
- [ ] Task two
- [x] Completed task

**Quotes:**
> This is a quote from error message or documentation

**Links:**
- Related issue: #123
- Documentation: [Link text](URL)
- Duplicate of: #456

## Error Handling

### Common Issues

**GitHub CLI not authenticated:**
```bash
# Check auth status
gh auth status

# If not authenticated
gh auth login
```

**Repository not found:**
- Verify repo owner/name spelling
- Check you have access to private repos

**Issue creation failed:**
- Check required fields are present
- Verify markdown formatting is valid
- Ensure no special characters break the command

**Duplicate detection missed:**
- Try broader search terms
- Search without quotes for partial matches
- Check closed issues too

## Quick Reference

```bash
# Search issues
gh search issues --repo anthropics/claude-code "{terms}" --limit 15

# View issue with comments
gh issue view --repo anthropics/claude-code [number] --comments

# Create issue
gh issue create --repo anthropics/claude-code --title "Title" --body "Body"

# Add comment
gh issue comment --repo anthropics/claude-code [number] --body "Comment"

# List labels
gh label list --repo anthropics/claude-code

# Check recent feature requests
gh search issues --repo anthropics/claude-code "is:issue label:enhancement" --limit 5

# Check recent bugs
gh search issues --repo anthropics/claude-code "is:issue label:bug" --limit 5
```
