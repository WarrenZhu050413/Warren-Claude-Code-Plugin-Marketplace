# Gmail Assistant Skill

A comprehensive skill for managing email workflows using the gmaillm CLI tool.

## Skill Structure

```
gmail-assistant/
├── SKILL.md                          # Main skill instructions
├── references/
│   └── quick-reference.md           # Concrete syntax examples and common patterns
└── assets/
    └── style-template.md            # Template for creating new email styles
```

## What This Skill Provides

### Core Workflows

1. **Email Composition** - Draft emails with context from past messages
2. **Search & Discovery** - Find similar emails, threads, and patterns
3. **Contact Finding** - Search web for email addresses before sending
4. **Group Management** - Create and manage distribution lists
5. **Style Management** - Work with email style templates
6. **Workflow Automation** - Set up and run email processing workflows

### Progressive Disclosure Design

The skill follows gmaillm's progressive disclosure pattern:
- **SKILL.md** provides high-level workflows and discovery patterns
- **quick-reference.md** loaded when concrete syntax examples needed
- **style-template.md** used when creating new email styles

### Safety First

The skill emphasizes **always testing first** to fuchengwarrenzhu@gmail.com before sending real emails.

## Usage Examples

### Compose Email with Context

Claude will:
1. Search for similar past emails
2. Review relevant threads
3. Check available styles
4. Draft based on context
5. TEST to fuchengwarrenzhu@gmail.com
6. Send after user confirms

### Find Contact and Send

Claude will:
1. Search web for contact information
2. Extract email address
3. Draft appropriate message
4. TEST first
5. Send after confirmation

### Manage Distribution Groups

Claude can:
- List existing groups
- Create new groups
- Add/remove members
- Send to groups
- Validate group emails

## Key Features

### Runtime Discovery

Instead of loading all documentation upfront, Claude uses discovery commands:

```bash
uv run gmail styles list        # See what's available
uv run gmail styles show posts  # Get specific details
uv run gmail styles examples    # Learn patterns
```

### Context-Aware Email Drafting

Claude searches past emails to:
- Match tone with previous interactions
- Reference relevant context
- Follow established patterns
- Maintain consistency

### Multi-Channel Search

- Search email history (gmaillm)
- Search web for contacts (WebSearch/WebFetch)
- Combine information for informed communication

## Testing

A test email was sent during skill creation to verify the workflow:

```
To: fuchengwarrenzhu@gmail.com
Subject: [TEST] Gmail Assistant Skill - Testing Email Workflow
Status: ✅ Delivered (Message ID: 19a5a8dd9f5e3a21)
```

## Integration with gmaillm

This skill works with gmaillm CLI commands:
- `gmail send` - Send emails (with TEST-first workflow)
- `gmail search` - Find past emails
- `gmail read` - Read messages and threads
- `gmail groups` - Manage distribution lists
- `gmail styles` - Work with email templates
- `gmail workflows` - Automate email processing

All commands support `--output-format json` for programmatic parsing.

## Skill Metadata

- **Name**: gmail-assistant
- **Description**: Email workflow management using gmaillm CLI
- **Location**: `~/.claude/plugins/.../skills/gmail-assistant/`
- **Created**: 2025-11-06
- **Test Status**: ✅ Verified working

## Related Files

- **SKILL.md** - Main instructions (always loaded when skill triggers)
- **quick-reference.md** - Syntax examples (loaded on demand)
- **style-template.md** - Template for new styles (used when creating styles)
