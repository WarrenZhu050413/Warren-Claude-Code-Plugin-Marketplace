---
name: "Formatting Files"
description: "Fix structure only: line breaks, indentation, ordering. Preserves all content word-for-word."
---

# FORMAT

Fix ONLY physical structure. Preserve all words.

## DO
- Remove random/excessive line breaks
- Fix indentation (consistent tabs/spaces)
- Reorder sections logically (headers before content, imports at top)
- Standardize whitespace

## DON'T
- Change any words or phrases
- Remove content (even if redundant)
- Apply STYLE rules
- Rewrite sentences

## Example
**Before:** `# Header\n\n\nText.\n  Indented wrong.`
**After:** `# Header\n\nText.\n\nIndented wrong.`

**Before:** `def foo():\nreturn 1\n  def bar():`
**After:** `def foo():\n    return 1\n\ndef bar():`

## Test
- Changed words? (NO)
- Fixed structure? (YES)
- Removed content? (NO)
