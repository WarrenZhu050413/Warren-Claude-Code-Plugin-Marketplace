---
name: Making Files Clearer
description: Simplify and clarify files by removing redundancy, organizing content logically, and keeping only essential information. Use when asked to make something clearer, remove fluff, simplify, declutter, make more concise, or improve readability. Keywords - clarity, simplify, concise, declutter, remove redundancy, essential only, no fluff.
---

# Making Files Clearer

A systematic approach to transforming verbose, redundant, or disorganized files into clear, concise, essential-only content.

## Core Principles

### 1. Ruthless Elimination
- **Remove redundancy**: Delete duplicate information, repeated explanations, and overlapping content
- **Cut fluff**: Eliminate unnecessary adjectives, hedging language, and verbose phrasing
- **Strip decorative elements**: Remove ASCII art, excessive formatting, and visual noise unless they serve a functional purpose

### 2. Essential Information Only
- **Keep what matters**: Retain only information that directly serves the file's purpose
- **Question every line**: Ask "Does removing this change understanding?" If no, remove it
- **Preserve accuracy**: Never sacrifice correctness for brevity

### 3. Strategic Examples
- **Examples add clarity when**:
  - Concept is abstract or counterintuitive
  - Multiple valid interpretations exist
  - Common mistakes need illustration
- **Examples are unnecessary when**:
  - Concept is self-evident
  - They merely repeat what's already clear
  - They're "nice to have" but not essential

### 4. Logical Organization
- **Group related content**: Cluster similar topics together
- **Progressive structure**: Simple concepts before complex ones
- **Clear hierarchy**: Use headings to show relationships
- **Scannable format**: Readers should find information quickly

## Workflow

### Step 1: Create Backup
```bash
cp original.md original.md.backup
```

### Step 2: Analyze Current State
1. Read the entire file
2. Identify the file's core purpose
3. List essential information categories
4. Note redundant sections, fluff, and organizational issues

### Step 3: Create Clarity Plan
Before editing, outline:
- What to keep (essential information)
- What to remove (redundancy, fluff)
- How to reorganize (new structure)
- Where examples add value

### Step 4: Execute Transformation
Apply changes systematically:
1. **Remove**: Delete redundant and unnecessary content
2. **Reorganize**: Restructure for logical flow
3. **Clarify**: Rewrite unclear sections concisely
4. **Validate**: Ensure no essential information lost

### Step 5: Present Changes for Review
Show the user:
- Summary of what changed
- Before/after comparison
- Ask for confirmation

### Step 6: Finalize
After user confirms:
```bash
rm original.md.backup
```

If user rejects changes:
```bash
mv original.md.backup original.md
```

## Common Clarity Anti-Patterns

### Redundancy
❌ **Bad**: Explaining the same concept multiple times in different words
✅ **Good**: One clear explanation, possibly with a targeted example

### Unnecessary Examples
❌ **Bad**: "For instance, if you have a variable `x = 5`, that's an example of setting a variable"
✅ **Good**: "Variables store values: `x = 5`"

### Verbose Phrasing
❌ **Bad**: "It is important to note that you should always make sure to..."
✅ **Good**: "Always..."

### Over-Documentation
❌ **Bad**: Documenting every obvious step
✅ **Good**: Documenting non-obvious behavior and gotchas

### Poor Organization
❌ **Bad**: Random topic ordering, nested sections with unclear purpose
✅ **Good**: Logical grouping, clear hierarchy, scannable headings

## Output Format

When making a file clearer:

1. **Show before/after comparison** (if file is small enough):
   ```
   Original: 250 lines, 15 sections, 30% redundancy
   Revised: 120 lines, 8 sections, focused content
   ```

2. **Summarize changes**:
   - What was removed and why
   - How content was reorganized
   - Where examples were added/removed

3. **Present the clarified content**: Use Edit tool to update the file

4. **Validate**: Confirm all essential information preserved

## Edge Cases

- **Technical documentation**: Preserve all technical accuracy; brevity should never compromise correctness
- **Legal/compliance files**: Consult before removing anything that might be required
- **Tutorials**: Examples are often essential; keep those that teach, remove those that just show off
- **Configuration files**: Comments may seem verbose but often prevent errors; keep contextual comments

## Success Criteria

A file is clearer when:
- A first-time reader understands it faster
- Information is findable without scrolling/searching extensively
- No questions arise from ambiguity or missing context
- The file can be maintained more easily
- Essential information density is maximized
