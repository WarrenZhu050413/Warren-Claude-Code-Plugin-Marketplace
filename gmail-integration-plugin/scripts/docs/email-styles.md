# Email Styles Guide

Email styles define writing patterns for different contexts.

## Quick Commands

```bash
gmail styles list              # List all styles
gmail styles show formal       # View specific style
gmail styles create my-style   # Create new style
gmail styles edit my-style     # Edit existing style
gmail styles validate my-style # Check format
gmail styles validate --fix    # Auto-fix issues
```

## File Format

Each style file needs:
1. YAML frontmatter (metadata)
2. Six XML sections (in strict order)

### Structure

```markdown
---
name: "Style Name"
description: "When to use: Context (30-200 chars)."
---

<examples>
Example email 1
---
Example email 2
</examples>

<greeting>
- Greeting option 1
</greeting>

<body>
- Writing guideline 1
</body>

<closing>
- Closing option 1
</closing>

<do>
- Best practice 1
</do>

<dont>
- Avoid this 1
</dont>
```

### Section Order (Required)

Sections must appear in this order:
1. `examples` - Sample emails
2. `greeting` - Greeting patterns
3. `body` - Writing guidelines
4. `closing` - Closing patterns
5. `do` - Best practices
6. `dont` - Antipatterns

## YAML Frontmatter

**Required fields:**
- `name` - 3-50 characters
- `description` - 30-200 characters, must start with "When to use:"

**Example:**
```yaml
---
name: "Professional Formal"
description: "When to use: Executives, legal contacts, formal outreach."
---
```

## XML Sections

### Examples

Show 1-3 complete emails demonstrating the style. Separate multiple examples with `---`.

```markdown
<examples>
Subject: Meeting Follow-up

Hi John,

Thanks for meeting. I'll send the proposal Friday.

Best,
Alice
---
Subject: Quick Question

Hi John,

Do you have 5 minutes for a call?

Thanks,
Alice
</examples>
```

### Greeting

Define greeting patterns.

```markdown
<greeting>
- "Dear [Title] [Last Name],"
- Use full name for first contact
- Avoid first names unless invited
</greeting>
```

### Body

Define writing guidelines.

```markdown
<body>
- Write concise sentences
- One point per paragraph
- Professional tone throughout
</body>
```

### Closing

Define closing patterns.

```markdown
<closing>
- "Best regards,"
- "Sincerely,"
- Sign with full name
</closing>
```

### Do

List best practices (minimum 2).

```markdown
<do>
- Proofread before sending
- Keep paragraphs short
- Use active voice
</do>
```

### Dont

List antipatterns (minimum 2).

```markdown
<dont>
- Use slang
- Write long paragraphs
- Forget to proofread
</dont>
```

## Validation Rules

The validator checks:

**YAML:**
- Required fields present
- Name length 3-50 characters
- Description 30-200 characters
- Description starts with "When to use:"

**XML:**
- All 6 sections present
- Correct order
- Proper tags
- Non-empty content
- Minimum items (examples: 1, do: 2, dont: 2)

**Format:**
- No trailing whitespace
- List items: `- ` (dash + space)

## Auto-Fix

The `--fix` flag can correct:
- Trailing whitespace
- List spacing (`-item` → `- item`)

Cannot fix:
- Missing sections
- Wrong order
- Invalid frontmatter
- Empty sections

## Creating a Style

**Step 1: Create**
```bash
gmail styles create my-style
```

This creates `~/.gmaillm/email-styles/my-style.md` and opens your editor.

**Step 2: Edit**

Fill in the template:
1. Set name and description
2. Add 1-3 example emails
3. Define greeting patterns
4. Define body guidelines
5. Define closing patterns
6. List do's (minimum 2)
7. List dont's (minimum 2)

**Step 3: Validate**
```bash
gmail styles validate my-style
```

Fix any errors shown.

**Step 4: Use**
```bash
gmail styles show my-style
```

## Common Errors

### "Description must start with 'When to use:'"

```yaml
# Wrong
description: "For casual emails"

# Correct
description: "When to use: Casual emails to friends."
```

### "Sections must appear in strict order"

Reorder to: examples → greeting → body → closing → do → dont

### "Missing required section"

Add all 6 sections with proper tags.

### "List items must start with '- '"

```markdown
# Wrong
<do>
-Item 1
* Item 2
</do>

# Correct
<do>
- Item 1
- Item 2
</do>
```

## Tips

1. **Be specific** - "Use first name only" not "Be casual"
2. **Show examples** - Real emails help most
3. **Keep concise** - Shorter guidelines work better
4. **Test it** - Use the style and refine

## Built-in Styles

gmaillm includes 5 styles:

1. **professional-formal** - Executives, legal, formal outreach
2. **professional-friendly** - Colleagues, known contacts
3. **academic** - Faculty, academic collaborators
4. **casual-friend** - Friends, informal communication
5. **brief-update** - Quick status updates

View any: `gmail styles show <name>`

## File Location

```
~/.gmaillm/email-styles/
├── professional-formal.md
├── professional-friendly.md
├── academic.md
├── casual-friend.md
├── brief-update.md
└── my-custom-style.md
```
