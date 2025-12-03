---
name: "Writing Papers"
description: "Create interactive HTML artifacts for academic papers using parallel subagent processing. Includes comprehensive pre-submission review checklist for paper quality assurance."
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

---

## Pre-Submission Paper Review Checklist

Use this checklist when reviewing academic papers before submission. Prioritize citation accuracy and template compliance as they can cause desk rejection.

### 1. Style & Formatting Consistency
- [ ] **Template compliance**: Verify required conference/journal template is used correctly
- [ ] **Consistent terminology**: Key terms used consistently throughout
- [ ] **Voice consistency**: Academic tone maintained; no unintended informal language
- [ ] **Section structure**: Logical flow verified (Introduction → Related Work → Method → Results → Discussion → Conclusion)

### 2. Citation Accuracy & Appropriateness
**Priority: CRITICAL** - Most important for scholarly integrity
- [ ] **Quote verification**: Every direct quote matches exact source wording
- [ ] **Source claims**: Each citation says what the paper claims it says
- [ ] **Better citations**: Search for more recent/authoritative sources where appropriate
- [ ] **Citation format**: All in-text citations match bibliography entries

### 3. Figure & Table Completeness
- [ ] **All figures referenced**: Verify all figures exist as files and are cited in text
- [ ] **Table accuracy**: Data matches actual study/analysis
- [ ] **Alt text**: Meaningful accessibility descriptions provided
- [ ] **Figure quality**: High-resolution images, anonymized if needed

### 4. Method & Results Integrity
- [ ] **Participant count consistency**: Numbers consistent throughout paper
- [ ] **Quotes attribution**: All participant quotes traceable to transcripts
- [ ] **Method details complete**: IRB approval mentioned if required
- [ ] **Results support claims**: Each claim backed by specific evidence

### 5. Contribution Clarity
- [ ] **Abstract-body alignment**: Abstract claims match what paper delivers
- [ ] **Research questions addressed**: Each stated question/obstacle gets explicit solution
- [ ] **Novel contribution**: Introduction distinguishes work from related work

### 6. Anonymization (if blind review)
**Priority: CRITICAL** - Can cause desk rejection
- [ ] **Author information removed**: No self-identifying details (institutions, grants, locations)
- [ ] **Study location anonymized**: Geographic references removed
- [ ] **Supplementary materials**: External links to code/data are anonymized

### 7. Reference Completeness
- [ ] **All citations in bibliography**: Every in-text citation has corresponding entry
- [ ] **Bibliography formatting**: Required format followed (APA, ACM, IEEE, etc.)
- [ ] **DOIs included**: Add DOI links where available for verification

### 8. Logical Coherence
- [ ] **Theory-to-design mapping**: Theoretical foundation informs design decisions
- [ ] **Evaluation validates claims**: Study findings support design implications
- [ ] **No contradictions**: Introduction promises match Discussion delivery

### 9. Writing Quality
- [ ] **Proofread for typos**: Spell-checker used; common errors reviewed
- [ ] **Sentence clarity**: Overly long sentences (>40 words) broken up
- [ ] **Jargon defined**: Technical terms defined on first use

### 10. Ethical & Inclusivity Check
- [ ] **Participant consent**: IRB approval and informed consent obtained
- [ ] **Inclusive language**: Gender-neutral pronouns; no assumptions about populations
- [ ] **Limitations acknowledged**: Honest assessment of scope limits included
- [ ] **Data availability**: Statement about repository access if applicable

### Recommended Review Order

1. **Citation accuracy (Item 2)** — Critical for scholarly integrity
2. **Anonymization (Item 6)** — Can cause desk rejection
3. **Method integrity (Item 4)** — Ensures reproducibility
4. **Figure/Table completeness (Item 3)** — Avoids broken references
5. **All others** — For polish and clarity

### Citation Verification Process

For each citation:
1. **Locate source**: Find original paper/book/website
2. **Verify quote accuracy**: If quoting, check exact wording matches
3. **Verify claim accuracy**: Confirm source says what you claim it says
4. **Check context**: Ensure quote/claim not taken out of context
5. **Find better sources**: Search for more recent or authoritative alternatives
6. **Document verification**: Note which citations verified and when
