---
name: Reflecting on Learnings
description: Analyzes conversations to identify learnings, patterns, and techniques for capture in skills/snippets. Proposes updates or new skills, shows preview before changes. Use when user says "reflect", "what did we learn", or after complex tasks.
---

# REFLECT: Capture Learnings from Conversations

## Triggers

- User says "REFLECT" or "what did we learn?"
- End of complex task with new techniques
- After solving tricky problems with insights

## Core Principle

**Learn from doing.** Capture discoveries (techniques, approaches, patterns) into skills/snippets for future sessions.

## Workflow

### 1. Analyze Conversation

Identify:
- Tasks completed, problems solved, techniques used
- New approaches that worked, mistakes/lessons learned
- Patterns, effective tool combinations
- Knowledge gaps filled, misunderstandings corrected

### 2. Categorize Discoveries

For each discovery:

**Update existing?** → Which skill/snippet? Which section? Correction/addition/clarification?
**Create new?** → Distinct topic? Independent invocation? Fills gap?
**Skip?** → Too specific? Already covered? Adds noise?

### 3. Present Report

```
# Reflection Report: [Topic]

## Summary
[What was accomplished and key learnings]

## Discoveries

### [Discovery Name]
**Learned:** [Description]
**Matters:** [Value]
**Action:** Update `skills/[name]/SKILL.md` [section] OR Create `skills/[new]/SKILL.md`

## Proposed Changes

**Updates:**
`skills/existing/SKILL.md`
```diff
+ Add section on [technique]
+ Include example: [from conversation]
! Correct misconception
```

**New:**
`skills/new-skill/SKILL.md` - [Purpose], [Triggers], [Content]

**Summary:** [N] updates, [N] new, [Impact]

---
**Proceed? (yes/no)**
```

### 4. Get Confirmation

**CRITICAL:** No changes without explicit approval. Ask: "Review above. Proceed?"

### 5. Apply Changes (After Approval)

**Update existing:**
- Read file → Edit tool → Preserve structure → Add to appropriate sections

**Create new:**
- Use templates → YAML frontmatter → Clear description/triggers → Add examples

**Verify:**
- Confirm changes → Show summary → Provide paths

### 6. Report Completion

```
✅ Reflection complete!

Updated: skills/skill-1/SKILL.md (added X)
Created: skills/new-skill/SKILL.md

Learnings captured for future sessions.
```

## Analysis Strategies

**Look for:**
- Explicit learnings ("I discovered...", "key insight was...")
- Problem → Solution patterns (reusable workflows)
- Comparisons ("X didn't work, Y did")
- User corrections (misunderstandings to document)
- Repeated patterns (done multiple times = pattern)
- Tool/technique combinations

**Identify:**
- Before/After states, decision points
- Debugging journeys, integration patterns
- Error corrections → insights

**Prioritize (✅) vs Skip (❌):**
- ✅ High reusability, fills gaps, corrects misconceptions, simplifies complexity, from real problem-solving
- ❌ Edge cases, already documented, obvious, adds noise

## Best Practices

**Analyzing:** Be selective. Focus on "aha moments" not procedures. Prioritize future value. Patterns > single instances.

**Proposing:** Be specific (exact files/sections). Show value. Use examples. Clear preview.

**Updating:** Minimal edits. Preserve structure. Add, don't replace (unless correcting). Match existing style.

## Example

```
User: "REFLECT on embedding images"

# Reflection Report: Wikimedia Commons Images

## Summary
Learned proper workflow: WebSearch → WebFetch → verify → embed. Key: don't guess URL structures.

## Discoveries

### Proper Workflow
**Learned:** WebSearch for file page → WebFetch for URL → curl verify → use in HTML
**Matters:** Prevents broken links, ensures attribution
**Action:** Update `skills/building-artifacts/SKILL.md` "External Resources" section

### Common Mistake
**Learned:** Wikimedia uses hash directories (/commons/7/72/Image.jpg) - can't guess
**Matters:** Prevents 404 errors
**Action:** Create `snippets/workflows/fetching-images/SNIPPET.md`

## Proposed Changes

**Update:** `skills/building-artifacts/SKILL.md`
+ Add "Embedding Images" section with 4-step workflow
! Note pitfall: Don't guess URL structures

**New:** `snippets/workflows/fetching-images/SNIPPET.md`
Purpose: Image embedding reference
Triggers: "embed image", "wikimedia commons"
Content: WebSearch patterns, WebFetch prompts, verification, attribution

**Summary:** 1 update, 1 new. Impact: Prevents common embedding mistakes.

---
**Proceed? (yes/no)**

User: "yes"

✅ Reflection complete!
Updated: skills/building-artifacts/SKILL.md (image embedding)
Created: snippets/workflows/fetching-images/SNIPPET.md
```

## Decision Guide

**Add when:**
- ✅ Concrete workflows from practice, corrections, proven patterns, actual examples, common pitfalls

**Skip when:**
- ❌ Theoretical/untested, edge cases, already covered, generic advice, obscures content

**Update existing:** Fits scope, fills gap, corrects content, adds examples
**Create new skill:** Distinct topic, independent invocation, clear gap
**Create snippet:** Context-injected, quick reference, clear triggers, broadly applicable

## Meta

REFLECT improves over time: Track patterns, learn from feedback, adapt analysis, refine proposals.

Works with: managing-skills, creating-skills, updating-skills, EXPLAIN

**Goal:** Capture insights for better future work. Focus on: save time, avoid mistakes, reusable patterns, simplify complexity.
