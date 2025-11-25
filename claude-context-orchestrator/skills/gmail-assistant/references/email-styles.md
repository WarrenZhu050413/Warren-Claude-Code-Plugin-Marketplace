# Email Styles Guide

Complete guide for creating and managing email styles in gmaillm.

## Overview

Email styles define different writing patterns for various contexts. Each style includes:
- **Metadata** - Name and usage guidance
- **Examples** - Real email templates
- **Guidelines** - Structured writing rules
- **Best practices** - Do's and don'ts

## Quick Start

### List Available Styles

```bash
gmail styles list
```

Shows all styles with "when to use" descriptions.

### View a Style

```bash
gmail styles show professional-formal
```

Displays the complete style template.

### Create a New Style

```bash
gmail styles create my-style
```

Creates from template and opens in your editor.

### Edit Existing Style

```bash
gmail styles edit casual-friend
```

### Validate Styles

```bash
# Validate single style
gmail styles validate my-style

# Auto-fix formatting issues
gmail styles validate my-style --fix

# Validate all styles
gmail styles validate-all --fix
```

## Style File Format

### Complete Structure

Each style file MUST follow this exact structure:

```markdown
---
name: "Style Name"
description: "When to use: Context description (30-200 chars)."
---

<examples>
Example email 1
---
Example email 2
</examples>

<greeting>
- Greeting option 1
- Greeting option 2
</greeting>

<body>
- Body guideline 1
- Body guideline 2
</body>

<closing>
- Closing option 1
- Closing option 2
</closing>

<do>
- Best practice 1
- Best practice 2
</do>

<dont>
- Avoid this 1
- Avoid this 2
</dont>
```

### Required Components

#### 1. YAML Frontmatter

**Required fields:**
- `name` - Style display name (3-50 characters)
- `description` - Usage context (30-200 characters, must start with "When to use:")

**Rules:**
- No extra fields allowed
- Must be at top of file
- Enclosed in `---` markers

**Example:**
```yaml
---
name: "Professional Formal"
description: "When to use: Executives, senior leadership, clients, legal/HR contacts, or first-time professional outreach."
---
```

#### 2. XML Sections

**Required sections (in strict order):**

1. `<examples>` - Example emails showing style in action
2. `<greeting>` - Greeting patterns and guidelines
3. `<body>` - Body content guidelines
4. `<closing>` - Closing patterns
5. `<do>` - Best practices
6. `<dont>` - Things to avoid

**Rules:**
- Must appear in exactly this order
- Each section must have opening and closing tags
- Sections must contain actual content
- Use bullet lists (`- ` followed by space) for guidelines

## Section Details

### Examples Section

**Purpose**: Show complete email examples demonstrating the style.

**Format**:
```markdown
<examples>
Subject: Meeting Follow-up

Hi [Name],

Thanks for meeting today. I'll send the proposal by Friday.

Best,
[Your Name]
---
Subject: Quick Question

Hi [Name],

Do you have 5 minutes to discuss the project timeline?

Thanks,
[Your Name]
</examples>
```

**Requirements:**
- 1-3 complete email examples
- Separate multiple examples with `---`
- Include realistic greetings, body, and closings

### Greeting Section

**Purpose**: Define greeting patterns.

**Format**:
```markdown
<greeting>
- "Dear [Title] [Last Name],"
- Use full name and title for first contact
- Avoid first names unless invited
</greeting>
```

### Body Section

**Purpose**: Define body content guidelines.

**Format**:
```markdown
<body>
- Write concise sentences
- One main point per paragraph
- Use bullet points for lists
- Professional tone throughout
</body>
```

### Closing Section

**Purpose**: Define closing patterns.

**Format**:
```markdown
<closing>
- "Best regards,"
- "Sincerely,"
- Sign with full name and title
</closing>
```

### Do Section

**Purpose**: Best practices to follow.

**Format**:
```markdown
<do>
- Proofread before sending
- Keep paragraphs short
- Use active voice
- Include clear call to action
</do>
```

**Requirements:**
- Minimum 2 items
- Actionable advice
- Clear and specific

### Dont Section

**Purpose**: Things to avoid.

**Format**:
```markdown
<dont>
- Use slang or casual language
- Write overly long paragraphs
- Forget to proofread
- Use all caps for emphasis
</dont>
```

**Requirements:**
- Minimum 2 items
- Clear antipatterns
- Specific examples

## Validation Rules

The `StyleLinter` enforces these rules:

### YAML Frontmatter
- ✓ Required fields: `name`, `description`
- ✓ Name length: 3-50 characters
- ✓ Description: 30-200 characters
- ✓ Description must start with "When to use:"
- ✓ No extra fields

### XML Sections
- ✓ All 6 sections present
- ✓ Correct order: examples → greeting → body → closing → do → dont
- ✓ Proper opening/closing tags
- ✓ Non-empty content

### Formatting
- ✓ No trailing whitespace
- ✓ List items: `- ` (dash + space)
- ✓ Minimum items: examples (1), do (2), dont (2)

### Auto-Fix Capabilities

The `--fix` flag can automatically correct:
- Trailing whitespace
- List item spacing (`-item` → `- item`)
- Extra blank lines

**Cannot auto-fix:**
- Missing sections
- Wrong section order
- Invalid frontmatter
- Empty sections

## Creating a New Style

### Step 1: Create Template

```bash
gmail styles create my-custom-style
```

This creates `~/.gmaillm/email-styles/my-custom-style.md` with template structure.

### Step 2: Edit in Your Editor

The command automatically opens the file in your default editor (determined by `$EDITOR` environment variable).

### Step 3: Fill In Content

Replace template placeholders with your content:

1. **Update frontmatter** - Set name and description
2. **Add examples** - Write 1-3 complete email examples
3. **Define greeting patterns** - Specify greeting guidelines
4. **Define body guidelines** - Specify writing rules
5. **Define closing patterns** - Specify closing guidelines
6. **List do's** - Best practices (minimum 2)
7. **List dont's** - Things to avoid (minimum 2)

### Step 4: Validate

```bash
gmail styles validate my-custom-style
```

Fix any errors shown.

### Step 5: Use

```bash
gmail styles show my-custom-style
```

## Common Validation Errors

### "Description must start with 'When to use:'"

**Problem**: Description doesn't have required prefix.

**Fix**:
```yaml
# Wrong
description: "For casual emails to friends"

# Correct
description: "When to use: Casual emails to friends and close colleagues."
```

### "Sections must appear in strict order"

**Problem**: Sections are out of order.

**Fix**: Reorder sections to match: examples → greeting → body → closing → do → dont

### "Missing required section"

**Problem**: One or more sections are missing.

**Fix**: Add all 6 required sections with proper tags.

### "List items must start with '- '"

**Problem**: List items have incorrect formatting.

**Fix**:
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

## Tips for Good Styles

1. **Be specific** - "Use first name only" not "Be casual"
2. **Show examples** - Real email examples are most helpful
3. **Keep it concise** - Shorter guidelines are easier to follow
4. **Test it** - Use the style for real emails and refine
5. **Version control** - Styles are just text files, commit them to git

## File Location

All styles are stored in:
```
~/.gmaillm/email-styles/
├── professional-formal.md
├── professional-friendly.md
├── academic.md
├── casual-friend.md
├── brief-update.md
└── my-custom-style.md
```

## Built-in Styles

gmaillm includes 5 professional styles:

1. **professional-formal** - Executives, legal, formal outreach
2. **professional-friendly** - Colleagues, known contacts
3. **academic** - Faculty, academic collaborators
4. **casual-friend** - Friends, informal communication
5. **brief-update** - Quick status updates

View any style: `gmail styles show <name>`
