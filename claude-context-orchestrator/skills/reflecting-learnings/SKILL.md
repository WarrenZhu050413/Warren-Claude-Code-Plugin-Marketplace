---
name: Reflecting on Learnings
description: Analyzes conversations to identify learnings, patterns, and techniques for capture in skills/snippets. Proposes updates or new skills, shows preview before changes. Use when user says "reflect", "what did we learn", or after complex tasks.
---

# REFLECT: Capture Learnings from Conversations

## Triggers

- User says "REFLECT" or "what did we learn?"
- End of complex task with new techniques
- After solving tricky problems with insights
- After using multiple skills in a session

## Core Principle

**Learn from doing.** Capture discoveries (techniques, approaches, patterns) into skills/snippets for future sessions.

## Workflow

### 1. Track Skills Used

Before analyzing, document all skills invoked during the session:
- Which skills were executed (e.g., "using-github-cli", "building-artifacts")
- When they were invoked (early, middle, late in session)
- How effective they were for the task
- Any patterns in skill usage
- Skills that worked well together vs. conflicts

Create or update eval file in `evals/` with this metadata.

### 2. Analyze Conversation

Identify:
- Tasks completed, problems solved, techniques used
- New approaches that worked, mistakes/lessons learned
- Patterns, effective tool combinations
- Knowledge gaps filled, misunderstandings corrected
- How invoked skills contributed to the solutions

### 3. Categorize Discoveries

For each discovery:

**Update existing?** → Which skill/snippet? Which section? Correction/addition/clarification?
**Create new?** → Distinct topic? Independent invocation? Fills gap?
**Skip?** → Too specific? Already covered? Adds noise?

### 4. Store Evaluation Data

Save findings to `~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/evals/`:

**File format:** `evals/{date}_{session_name}_{context}.md`
Example: `evals/2025-10-22_main_database-optimization.md`

**Evaluation file structure:**
```json
{
  "date": "YYYY-MM-DD",
  "session_name": "[name]",
  "context": "[brief_description]",
  "reproducible_prompt": "[original user prompt]",
  "skills_invoked": [
    "skill-name-1",
    "skill-name-2"
  ]
}
```

### 5. Present Report

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

### 6. Get Confirmation

**CRITICAL:** No changes without explicit approval. Ask: "Review above. Proceed?"

### 7. Apply Changes (After Approval)

**Update existing:**
- Read file → Edit tool → Preserve structure → Add to appropriate sections

**Create new:**
- Use templates → YAML frontmatter → Clear description/triggers → Add examples

**Verify:**
- Confirm changes → Show summary → Provide paths

### 8. Report Completion

```
✅ Reflection complete!

Eval stored: evals/2025-10-22_main_database-optimization.md
Updated: skills/skill-1/SKILL.md (added X)
Created: skills/new-skill/SKILL.md

Skills tracked: [skill-1, skill-2, skill-3]
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

## File Locations

**Skills directory:**
```
/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/{skill-name}/SKILL.md
```

**Snippets directory:**
```
/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/snippets/local/{category}/{snippet-name}/SKILL.md
```

**Evals directory:**
```
/Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/evals/{date}_{session}_{context}.md
```

**Finding files:**
```bash
# Find a skill
find /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills -name "*keyword*"

# Find a snippet
find /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/snippets -name "*keyword*"

# Search for content
grep -r "search term" /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator --include="*.md"
```

**Common snippet categories:**
- `documentation/` - Guides, references, how-tos
- `development/` - Code patterns, debugging
- `communication/` - Email, writing templates
- `productivity/` - Workflow, automation
- `utilities/` - Tools, scripts

## Example

```
User: "REFLECT on embedding images"

Session eval created:
```json
{
  "date": "2025-10-22",
  "session_name": "main",
  "context": "Learned proper workflow for embedding Wikimedia Commons images",
  "reproducible_prompt": "Help me create an artifact with images from Wikimedia Commons",
  "skills_invoked": [
    "fetching-images",
    "building-artifacts",
    "making-clearer"
  ]
}
```

# Reflection Report: Wikimedia Commons Images

## Summary
Learned proper workflow: WebSearch → WebFetch → verify → embed. Key: don't guess URL structures.
Skills combination (fetching + building) was highly effective.

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

Eval stored: evals/2025-10-22_main_image-embedding.md
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

**Skill Tracking for Continuous Improvement:**
- Evaluation files in `evals/` create a history of skill effectiveness
- Review evals periodically to identify:
  - Which skills are most valuable in different contexts
  - Skill combinations that work well together
  - Skills that might need enhancement
  - Gaps in available skills
- Use this data to improve existing skills and identify new ones to create

Works with: managing-skills, creating-skills, updating-skills, EXPLAIN

**Goal:** Capture insights for better future work. Focus on: save time, avoid mistakes, reusable patterns, simplify complexity. Build data on skill effectiveness over time.
