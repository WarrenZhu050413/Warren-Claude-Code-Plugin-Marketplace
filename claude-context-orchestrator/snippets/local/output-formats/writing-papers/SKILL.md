---
description: Creating interactive paper visualizations with parallel processing
SNIPPET_NAME: writing-papers
ANNOUNCE_USAGE: false
---

## Purpose

Create interactive HTML artifacts for academic papers using parallel subagent processing and the artifacts-builder skill.

## Source Acquisition Strategy

Use parallel subagents to fetch papers from multiple sources:
- **ArXiv**: Direct fetch for open-access papers (most common)
- **Anna's Archive**: DOWNLOAD if paper not freely available
- **Exa Search** (`mcp__exa__web_search_exa`): Fallback for hard-to-find sources
- **Web search**: General web search if needed

## Parallel Processing with Subagents

- Launch **one subagent per paper** (or per major section for very long papers)
- Each agent extracts:
  - Title, authors, publication info
  - Abstract and key findings
  - Methodology overview
  - Important figures/tables
  - Citations and references

## Interactive Artifact Creation

**Compose with artifacts-builder skill** - don't duplicate those instructions.

Create interactive HTML artifacts that include:
- **Paper summary**: Title, authors, abstract
- **Key visualizations**: Extracted figures, concept maps
- **Navigation**: Collapsible sections, table of contents
- **Searchable content**: Full-text search within artifact
- **Citations**: Properly formatted references
- **Responsive design**: Works on mobile/desktop

## Weekly/Batch Organization

When handling multiple papers:
- Group by week, topic, or theme
- Create dashboard/index with links between papers
- Highlight connections and cross-references
- Show thematic patterns across papers

**Output Format**: Single interactive HTML artifact per paper, or combined dashboard for weekly batches.
