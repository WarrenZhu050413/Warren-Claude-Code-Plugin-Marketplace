---
name: Pedagogical Journey
description: Explain solutions through the lens of discovery and conversation journey, emphasizing how insights emerged rather than exhaustive technical details. Use when explaining code changes, decision-making processes, problem-solving approaches, or any narrative that benefits from showing the "why" before the "what". Trigger with JOURNEY keyword.
---

# Pedagogical Journey

Explain solutions through discovery—showing **how insights emerged** rather than exhaustive technical details.

## Core Principle

Show the journey of discovery without exhaustion. Focus on the "why" rather than the "what", highlighting key insights and decision points.

## Required Sections

Every explanation MUST include:

### 1. High-Level Summary (2-3 sentences)

Start with a concise overview of what was accomplished. Focus on the "what" and "why" before the "how".

### 2. The Journey & Discovery Process (2-4 sentences)

Brief context on how the solution emerged:
- What led to the approach taken
- Key insights or turning points during implementation
- Alternative approaches considered (if relevant)
- How testing or debugging shaped the final solution

**Examples:**
- "Initially I tried X, but discovered Y limitation which led to the current Z approach"
- "The key insight came from noticing [pattern/behavior], which informed..."
- "During testing, I found [issue], which revealed the need for..."

Keep this concise—focus on the most impactful decision points.

## Optional Sections

Include when they add value:

### 3. Visual Overview
Diagrams clarifying understanding: architecture diagrams, flow charts, file structure trees, sequence diagrams.

**Skip if:** Explanation is simple enough without visuals or words suffice.

### 4. Key Changes
Organize changes by module/component, purpose, and impact.

**Skip if:** Change is isolated to one component or already covered in Journey section.

### 5. Technical Details
Implementation specifics: new functions/classes, modified behavior (before/after), integration points.

**Important**: Don't include full code listings—reference file paths and line numbers instead (e.g., `tracking.lua:45`).

**Skip if:** Implementation is straightforward or user didn't ask for deep technical details.

### 6. What to Try Next
2-3 concrete suggestions for testing, building, or exploring further.

**Skip if:** No clear next steps or user didn't ask for guidance.

## Format-Specific Guidelines

### As HTML
1. Summary + Journey at top (required, always visible)
2. Other sections only if they add value
3. Use Mermaid flowcharts for decision trees
4. Collapsible sections for technical details
5. Color coding: Gold for insights, Green for outcomes, Gray for details

### As Markdown
1. Use standard headers (`##`, `###`)
2. Use `> **Journey Insight:**` blockquotes for key discoveries
3. Use mermaid code fences for diagrams
4. Use tables for before/after comparisons
5. Only include optional sections when valuable

## Section Selection Logic

**Always include:**
- ✅ High-Level Summary
- ✅ The Journey & Discovery Process

**Consider including when:**
- 📊 Visual Overview: Complex architecture, multiple components, or process flows
- 🔧 Key Changes: Multiple modules modified or changes span different layers
- ⚙️ Technical Details: Non-trivial implementation or user specifically asked
- 🚀 What to Try Next: Clear actionable next steps or areas to explore

**Skip optional sections when:**
- ❌ Information already covered in required sections
- ❌ Change is simple and self-explanatory
- ❌ Would add noise without adding clarity
- ❌ User didn't express interest in that level of detail

## General Guidelines

- **Be intentionally concise**: Aim for clarity over completeness
- **Show the journey, don't narrate every step**: Highlight key discoveries and decision points
- **Connect decisions to outcomes**: Help users understand why choices were made
- **Use formatting liberally**: Headers, bullets, bold text for scanning
- **Avoid walls of text**: Break up long sections with whitespace
- **Adapt to format**: Use format-specific features to enhance clarity

## Minimal Example

```
I've fixed the popup issue where they were closing immediately after opening.

**How we got here:**
Initially I suspected the popup code itself, but debugging revealed the CursorMoved autocommand was closing popups globally. The fix adds a buffer name check to only close popups when cursor moves in source files, not within the popup itself.
```

## Format Combinations

You can combine this with other output formats:
- "EXPLAIN HTML" → Use this structure in HTML format
- "EXPLAIN markdown" → Use this structure in markdown
- "EXPLAIN + [another format]" → Apply both modes together

For detailed examples and advanced patterns, see [reference.md](reference.md).
