---
description: Make files clearer by removing redundancy and organizing content
SNIPPET_NAME: making-clearer
ANNOUNCE_USAGE: false
---

# Making Files Clearer

---

**VERIFICATION_HASH:** `7c3a9f5e2d8b4160`

## Primary Purpose

Transform verbose, redundant, or disorganized files into clear, concise, essential-only content.

## Core Principles

### 1. Ruthless Elimination
- Remove redundancy: Delete duplicate information, repeated explanations, overlapping content
- Cut fluff: Eliminate unnecessary adjectives, hedging language, verbose phrasing
- Strip decorative elements: Remove ASCII art, excessive formatting, visual noise (unless functional)

### 2. Essential Information Only
- Keep what matters: Retain only information that directly serves the file's purpose
- Question every line: "Does removing this change understanding?" If no, remove it
- Preserve accuracy: Never sacrifice correctness for brevity

### 3. Strategic Examples
**Add examples when they**:
- Clarify abstract or counterintuitive concepts
- Distinguish between multiple valid interpretations
- Illustrate common mistakes

**Remove examples when they**:
- State the self-evident
- Merely repeat what's already clear
- Are "nice to have" but not essential

### 4. Logical Organization
- Group related content together
- Simple concepts before complex ones
- Clear hierarchy with headings
- Scannable format for quick navigation

## Workflow

**Step 1: Analyze**
1. Read entire file
2. Identify core purpose
3. List essential information categories
4. Note redundancy, fluff, organizational issues

**Step 2: Plan**
Outline:
- What to keep (essential)
- What to remove (redundant, fluff)
- How to reorganize (structure)
- Where examples add value

**Step 3: Execute**
1. Remove: Delete redundant and unnecessary content
2. Reorganize: Restructure for logical flow
3. Clarify: Rewrite unclear sections concisely
4. Validate: Ensure no essential information lost

**Step 4: Verify**
- [ ] File serves its purpose clearly
- [ ] No redundancy remains
- [ ] Organization is logical and scannable
- [ ] Examples enhance understanding
- [ ] No essential information lost

## Common Anti-Patterns

**Redundancy**: Explaining same concept multiple times
**Unnecessary Examples**: "For instance, `x = 5` is an example of setting a variable"
**Verbose Phrasing**: "It is important to note that you should always..."
**Over-Documentation**: Documenting every obvious step
**Poor Organization**: Random topic ordering, unclear hierarchy

## Output Format

1. **Before/After Summary**:
   - Original: X lines, Y sections
   - Revised: X lines, Y sections

2. **Change Summary**:
   - What was removed and why
   - How content was reorganized
   - Where examples were added/removed

3. **Present clarified content** using Edit tool

4. **Validate** all essential information preserved

## Edge Cases

- **Technical docs**: Preserve all technical accuracy; brevity never compromises correctness
- **Legal/compliance**: Consult before removing potentially required content
- **Tutorials**: Keep examples that teach, remove those that just demonstrate
- **Config files**: Keep contextual comments that prevent errors

## Success Criteria

File is clearer when:
- First-time readers understand faster
- Information is findable without extensive scrolling
- No ambiguity or missing context
- Easier to maintain
- Maximum essential information density
