---
name: "Condensing Content"
description: "Use when asked to condense, simplify, or reduce verbosity in documentation, workflows, or explanations. Focuses on essential information and general principles over extensive examples."
---

# Condensing Content

Apply these principles when asked to CONDENSE information.

## Core Condensing Principles

1. **Many examples  Fewer representative examples**
   - Keep 1-2 illustrative examples instead of 5-10
   - Choose examples that demonstrate key concepts
   - Remove redundant or similar examples

2. **Elaborate workflows  General principles**
   - Extract the underlying principles from step-by-step instructions
   - Keep detailed workflows only when steps are absolutely necessary
   - Convert "how to do X" into "key things to know about X"

3. **Remove redundancy**
   - Eliminate repetitive explanations
   - Merge similar sections
   - Say things once, clearly

4. **Focus on essential information**
   - Preserve critical details and requirements
   - Remove verbose explanations and qualifiers
   - Keep the "what" and "why", reduce the "how" (unless necessary)

5. **Command reference over tutorials**
   - List commands with brief inline comments
   - Group related commands together
   - Remove lengthy setup/context sections

## When to Condense

Apply condensing to:
- Long documentation with many examples
- Verbose workflow specifications
- Skills/snippets with excessive detail
- Tutorial-style content that should be reference-style
- Repeated explanations across sections

## What to Preserve

**DO NOT condense:**
- Critical warnings or safety information
- Unique examples that demonstrate different concepts
- Essential steps in sequential workflows
- Configuration requirements or syntax rules
- Error messages and troubleshooting info

## Before/After Example

**Before (verbose):**
```markdown
### Step 1: Search for Past Emails

Before drafting ANY email, search past correspondence:

```bash
# Search emails to a specific person
gmail search "to:recipient@example.com" --max 10

# Search emails from a specific person
gmail search "from:recipient@example.com" --max 10

# Search recent thread about a topic
gmail search "subject:project-name after:2024/10/01"
```

**When to use each search:**
- **Before replying**: Use `gmail search "from:sender@example.com"` to understand their style
- **Before composing**: Use `gmail search "to:recipient@example.com"` to match Warren's past style with them
- **For context**: Use `gmail search "subject:keyword"` to find related emails
```

**After (condensed):**
```markdown
### Search Commands
```bash
gmail search "to:person@example.com" --max 10      # Emails to someone
gmail search "from:person@example.com" --max 10    # Emails from someone
gmail search "subject:keyword after:2024/10/01"    # By subject + date
```

**Before composing:** Search past emails to extract patterns (greeting, tone, sign-off)
```

## Quick Checklist

When condensing, ask:
- [ ] Can multiple examples be reduced to one representative example?
- [ ] Can step-by-step workflows become general principles?
- [ ] Are there repeated explanations that can be merged?
- [ ] Can commands be listed with inline comments instead of lengthy descriptions?
- [ ] Are there sections that explain "how" when only "what" is needed?
- [ ] Have I preserved all critical warnings and requirements?

## Output Format

After condensing:
- Commands grouped by category with inline comments
- Principles stated clearly and concisely
- 1-2 examples maximum (only if needed for clarity)
- "Key things to know" section instead of extensive workflows
- References to detailed docs when available
