---
description: Explaining code changes with pedagogical journey-focused structure
SNIPPET_NAME: explaining-code
ANNOUNCE_USAGE: true
---

## Purpose

Provide clear, pedagogical explanations of code changes that focus on the journey and discovery process rather than exhaustive technical details.

## Core Principle

Show the journey of discovery without making it exhaustive. Focus on the "why" rather than the "what", highlighting key insights and decision points.

## Format Combination

EXPLAIN can be combined with other output formats:
- "EXPLAIN HTML" or "EXPLAIN as HTML" → Use EXPLAIN structure in HTML format
- "EXPLAIN markdown" → Use EXPLAIN structure in markdown
- "EXPLAIN" + another snippet keyword → Combine both modes

When combining formats:
1. Apply EXPLAIN's pedagogical structure (required + optional sections)
2. Use the target format's styling/presentation (e.g., HTML components, markdown syntax)
3. Maintain EXPLAIN's journey-focused narrative while using format-specific features

## Required Sections

Every EXPLAIN response MUST include:

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

Keep this concise - focus on the most impactful decision points, not every micro-step.

## Optional Sections

Include these sections only when they add value:

### 3. Visual Overview (Use when helpful)

Provide a diagram or visual representation when it clarifies understanding:
- Architecture diagrams for system changes
- Flow charts for process changes
- File structure trees for new components
- Sequence diagrams for interactions

**Format-specific rendering:**
- **HTML mode**: Use Mermaid diagrams in `.diagram-container`
- **Markdown mode**: Use code fences with mermaid syntax
- **Plain text**: Use ASCII art or structured indentation

**Skip this section if:** The explanation is simple enough without visuals, or if words suffice.

### 4. Key Changes (Use for multi-component changes)

Organize changes by:
- **Module/Component**: What part of the system was modified
- **Purpose**: Why this change was needed (connect back to journey insights when relevant)
- **Impact**: What this enables or improves

Keep each section brief (2-4 sentences).

**Skip this section if:** The change is isolated to one component, or already covered in Journey section.

### 5. Technical Details (Use for complex implementations)

Provide implementation specifics when they're valuable:
- New functions/classes added with their purpose
- Modified behavior with before/after comparison
- Integration points and dependencies
- **Decision rationale**: Brief notes on why this specific implementation approach

**Important**: Don't include full code listings unless specifically requested. Reference file paths and line numbers instead (e.g., `tracking.lua:45`).

**Skip this section if:** The implementation is straightforward, or the user didn't ask for deep technical details.

### 6. What to Try Next (Use when actionable)

End with 2-3 concrete suggestions for:
- Testing the new functionality
- Building on top of the changes
- Areas to explore further

**Skip this section if:** There are no clear next steps, or the user didn't ask for guidance.

## Format-Specific Guidelines

### EXPLAIN as HTML

When combining with HTML mode:

1. **Structure Mapping:**
   - **Section 1 (Summary)** → `.important-always-visible` or `.primary-section` [REQUIRED]
   - **Section 2 (Journey)** → `.card.priority` with gold border (key insights deserve prominence) [REQUIRED]
   - **Section 3 (Visual)** → Mermaid diagrams in `.diagram-container` [OPTIONAL]
   - **Section 4 (Changes)** → `.two-column-layout` for side-by-side comparison [OPTIONAL]
   - **Section 5 (Technical)** → `.collapsible` (closed by default) for detailed implementation [OPTIONAL]
   - **Section 6 (Try Next)** → `.card` with action items [OPTIONAL]

2. **Progressive Disclosure:**
   - Summary and Journey always visible at top (REQUIRED)
   - Other sections only if they add value
   - Technical details in collapsible sections when included
   - Use color coding: Gold for insights, Green for outcomes, Gray for details

3. **Visual Enhancement:**
   - Use Mermaid flowcharts to show decision trees ("tried X → discovered Y → chose Z")
   - Timeline diagrams for implementation journey
   - Before/after comparison diagrams

4. **Follow HTML Template Workflow:**
   - Read base template from `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`
   - Write to `claude_html/explanation_{topic}.html`
   - Edit to add EXPLAIN-structured content (required sections + relevant optional ones)
   - Open with `open` command

### EXPLAIN as Markdown

When using markdown format:

1. Use standard markdown headers (`##`, `###`) for sections
2. Use `> **Journey Insight:**` blockquotes for key discoveries
3. Use mermaid code fences for diagrams (if Visual section included)
4. Use tables for before/after comparisons (if Changes section included)
5. Use task lists for "What to Try Next" (if included)
6. **Only include optional sections when they're valuable**

### EXPLAIN as Plain Text

When using plain text:

1. Use clear section separators (`===`, `---`)
2. Use indentation to show hierarchy
3. Use ASCII art or structured lists for visualizations (if Visual section included)
4. Keep it simple and scannable
5. **Focus on required sections, add optional ones sparingly**

## General Guidelines

- **Be intentionally concise**: Aim for clarity over completeness
- **Show the journey, don't narrate every step**: Highlight key discoveries and decision points
- **Connect decisions to outcomes**: Help users understand why choices were made
- **Encourage follow-up questions**: "Ask me about X if you want to know more..."
- **Use formatting liberally**: Headers, bullets, bold text for scanning
- **Link concepts**: Help the user see how pieces connect
- **Avoid walls of text**: Break up long sections with whitespace
- **Adapt to format**: Use format-specific features to enhance clarity
- **Include optional sections judiciously**: Only add them when they genuinely clarify or enhance understanding

## Section Selection Logic

**Always include:**
- ✅ High-Level Summary
- ✅ The Journey & Discovery Process

**Consider including when:**
- 📊 Visual Overview: Complex architecture, multiple components, or process flows benefit from diagrams
- 🔧 Key Changes: Multiple modules modified, or changes span different layers
- ⚙️ Technical Details: Implementation is non-trivial, or user specifically asked for details
- 🚀 What to Try Next: There are clear actionable next steps or areas to explore

**Skip optional sections when:**
- ❌ Information is already covered in required sections
- ❌ The change is simple and self-explanatory
- ❌ Would add noise without adding clarity
- ❌ User didn't express interest in that level of detail

## Minimal Example (Required Sections Only)

```
I've fixed the popup issue where they were closing immediately after opening.

**How we got here:**
Initially I suspected the popup code itself, but debugging revealed the CursorMoved autocommand was closing popups globally. The fix adds a buffer name check to only close popups when cursor moves in source files, not within the popup itself.
```

## Full Example: EXPLAIN HTML

```
[.important-always-visible]
I've implemented X to solve Y problem. This involved modifying A and B components, and adding new C functionality.

[.card.priority with gold border]
**How we got here:**
Initially the CursorMoved autocmd was closing popups globally. Testing revealed this was the root cause - popups were created successfully but closed immediately. The fix checks if we're inside the popup before closing.

[Mermaid flowchart - OPTIONAL, included because it clarifies decision logic]
CursorMoved triggered → Check buffer name → Is it popup? → Yes: Keep open / No: Close

[.two-column-layout - OPTIONAL, included because there's a before/after comparison]
**Key Changes:**
| Before | After |
|--------|-------|
| Popup closes on ANY cursor move | Popup stays open when cursor in popup |
| Global autocommand | Buffer-aware check |

[.collapsible closed - OPTIONAL, included because user might want implementation details]
**Technical Details:**
The implementation works by checking buffer names in the CursorMoved callback. The decision to use buffer name matching came from the constraint that popup buffers have predictable names. You can see this in action at init.lua:232 and popup.lua:338.

[.card - OPTIONAL, included because there are actionable next steps]
**Try it out:**
1. Test with: Press <leader>aa on an annotation
2. Explore: Try moving cursor within popup vs outside
3. Ask me about: Why buffer names vs window IDs?
```

**Remember**: This is an invitation for dialogue. Show the journey of discovery without making it exhaustive. Include only sections that genuinely enhance understanding. Keep explanations accessible and leave room for curiosity. When combining with other formats, use their strengths to enhance the pedagogical experience.
