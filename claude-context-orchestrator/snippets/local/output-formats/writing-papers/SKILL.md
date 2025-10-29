---
name: "Writing Papers"
description: "Create interactive HTML artifacts for academic papers using parallel subagent processing."
---

# Writing Papers

## Sources
Use parallel subagents to fetch:
- **ArXiv**: Open-access papers (most common)
- **Anna's Archive**: Download if not freely available
- **Exa Search** (`mcp__exa__web_search_exa`): Fallback
- **Web search**: General fallback

## Subagent Processing
- Launch one subagent per paper (or per major section for long papers)
- Each agent extracts:
  - Title, authors, publication info
  - Abstract and key findings
  - Methodology overview
  - Important figures/tables
  - Citations and references

## Artifact Creation
**Compose with artifacts-builder skill** - don't duplicate instructions.

Include:
- Paper summary (title, authors, abstract)
- Key visualizations (figures, concept maps)
- Navigation (collapsible sections, TOC)
- Searchable content (full-text search)
- Citations (properly formatted)
- Responsive design (mobile/desktop)

## Batch Organization
When handling multiple papers:
- Group by week, topic, or theme
- Create dashboard with links between papers
- Highlight connections and cross-references
- Show thematic patterns

**Output**: Single HTML artifact per paper, or combined dashboard for batches.
