---
name: Searching Deeply
description: Advanced search strategies combining WebSearch, Exa, and Codex for comprehensive information discovery. Use when researching topics, finding code examples, gathering technical documentation, or performing complex multi-source searches. Keywords - search, research, web search, exa, code examples, documentation, technical research, information gathering.
---

# Deeply Searching

## Core Philosophy

**Always start with WebSearch.** It's free and fast (2-4s). Supplement with other tools only when WebSearch results are insufficient.

## Tool Selection

| Tool | Best For | Cost | Speed | Primary Use Case |
|------|----------|------|-------|------------------|
| **WebSearch** | Breaking news, general knowledge, consumer products, local info | Free | 2-4s | Primary - start here always |
| **Exa** | Code examples, technical docs, API/library usage, academic papers | $0.01/query | 5-6s | Technical depth supplement |
| **Codex** | Complex analysis, multi-step research, synthesis across sources | API usage | 10-30s | Autonomous research with reasoning |

### WebSearch: Use For
- Breaking news & current events (95% confidence)
- General knowledge and overviews
- Consumer products - reviews, comparisons (90% confidence)
- Local information - restaurants, services (85% confidence)
- Regulatory/legal information (90% confidence)
- Trend analysis

### Exa: Supplement Only When
- **Code examples** (100% confidence) - Production code from real repositories with exceptional depth
- **Technical documentation** (95% confidence) - Deep context with multiple implementation patterns
- **API/library usage** (100% confidence) - Real-world GitHub examples
- **Academic papers** (85% confidence) - Direct links to ArXiv, Nature, IEEE with full-text access
- **Performance optimization** (95% confidence) - Advanced patterns with production examples

**Key differences:**
- Exa returns full article text, WebSearch returns summaries
- Exa code quality is exceptional (10+ real examples), WebSearch is basic
- Exa fails badly on consumer/shopping queries - it's technical/research optimized

**Available Exa Tools:**
- `mcp__exa__web_search_exa` - General web search (5 results default)
- `mcp__exa__get_code_context_exa` - **Best for code** - Returns production code with "dynamic" token allocation

### Codex: Use When Task Requires
- Autonomous multi-step research with reasoning
- Heavy analytical tasks requiring synthesis
- Complex queries needing deep investigation
- WebSearch provides results but deeper analysis needed
- Cross-source validation and comparison

## Decision Tree

```
1. Run WebSearch first
   ↓
2. Analyze results
   ↓
3. Are results sufficient?
   ├─ YES → Done
   │
   └─ NO → What's missing?
      ├─ Deep analysis/multi-step research? → Use Codex
      ├─ Code examples/technical depth? → Add Exa
      └─ Multiple gaps? → Combine tools
```

## WebSearch Optimization

### Query Decomposition
Break complex queries into focused sub-queries:

**❌ Too Complex:** "Analyze AI trends and compare frameworks and recommend best practices"

**✅ Decomposed:**
```typescript
Promise.all([
  WebSearch({ query: "AI framework trends 2024 2025" }),
  WebSearch({ query: "LLM framework comparison benchmarks" }),
  WebSearch({ query: "AI development best practices production" })
])
```

### Query Expansion
- **Add Context:** "authentication error" → "JWT token authentication error Node.js Express"
- **Use Synonyms:** "machine learning" → "ML artificial intelligence deep learning"
- **Include Years:** Current date context is October 2025 - use "2024 2025" for recent developments

### Query Specificity Levels
| Level | Example | Result Quality |
|-------|---------|----------------|
| Vague | "AI stuff" | Poor - Too broad |
| General | "machine learning" | Moderate - Still broad |
| Specific | "transformer architecture in LLMs" | Good - Focused |
| Highly Specific | "BERT vs GPT transformer differences" | Excellent - Precise |

### Domain Filtering
```typescript
// Only trusted sources
WebSearch({
  query: "React best practices",
  allowed_domains: ["reactjs.org", "github.com", "dev.to"]
})

// Exclude low-quality sites
WebSearch({
  query: "JavaScript tutorials",
  blocked_domains: ["spam.com", "low-quality-content.net"]
})
```

### Parallel Multi-Strategy Search
```typescript
// Execute variations simultaneously
Promise.all([
  WebSearch({ query: "React Server Components performance" }),
  WebSearch({ query: "RSC server-side rendering optimization" }),
  WebSearch({ query: "Next.js App Router streaming speed" })
])
```

## Common Workflows

### Pattern 1: WebSearch Only (Most Common)
```typescript
// WebSearch provides sufficient results → Done
const results = await WebSearch({ query: "React 19 features release 2025" });
```

### Pattern 2: WebSearch → Delegate to Codex
```typescript
// Initial overview
const overview = await WebSearch({ query: "JWT vs session authentication security 2025" });
// Task requires deep analysis → Delegate to Codex for autonomous multi-step research
```

### Pattern 3: WebSearch → Supplement with Exa
```typescript
// Step 1: Overview
const overview = await WebSearch({ query: "OAuth2 Express.js implementation guide 2025" });

// Step 2: Add production code examples
const codeExamples = await mcp__exa__get_code_context_exa({
  query: "Express.js OAuth2 implementation examples",
  tokensNum: "dynamic"
});
```

### Pattern 4: WebSearch → Multiple Tools
```typescript
// Step 1: Initial overview
const overview = await WebSearch({ query: "LLM application best practices production 2025" });

// Step 2: Multiple gaps - use Codex for orchestration + Exa for code
const codeExamples = await mcp__exa__get_code_context_exa({
  query: "production LLM application error handling security",
  tokensNum: "dynamic"
});
```

## Adaptive Search Depth

```typescript
// Quick Answer (30 seconds)
const quick = await WebSearch({ query: specificQuery });

// Moderate Depth (2-3 minutes)
const moderate = await Promise.all([
  WebSearch({ query: coreQuery }),
  WebSearch({ query: expandedQuery }),
  WebSearch({ query: alternativeQuery })
]);

// Deep Research (10+ minutes) - see Deep Research Mode section
```

## Multi-Source Validation

```typescript
async function validateClaim(claim: string) {
  const [general, academic, news] = await Promise.all([
    WebSearch({ query: claim }),
    WebSearch({ query: claim, allowed_domains: ["*.edu", "scholar.google.com"] }),
    WebSearch({ query: `${claim} news 2025`, allowed_domains: ["nytimes.com", "reuters.com"] })
  ]);

  return {
    claim,
    generalSupport: analyze(general),
    academicSupport: analyze(academic),
    newsSupport: analyze(news),
    confidence: calculateConsistency([general, academic, news])
  };
}
```

## Deep Research Mode

### When to Use
Activate when:
- User explicitly requests "deep research", "comprehensive analysis", or "thorough investigation"
- Topic requires multi-step reasoning
- Need to synthesize dozens of sources
- Validating claims across multiple perspectives

### Best Practices (2025)

**1. Start with Clear, Detailed Queries**
```
❌ Vague: "AI trends"
✅ Specific: "What are the latest transformer architecture innovations in large language models as of October 2025, with focus on efficiency improvements?"
```

Key principles:
- Be specific, avoid pronouns and vague terms
- Specify exact timeframes (not "recently")
- State goal and constraints upfront

**2. Draft a Structured Research Plan**
```markdown
Research Plan:
1. Identify key aspects to investigate
2. Prioritize source types (academic papers > industry blogs > news)
3. Define success criteria
4. Plan validation strategy
```

**3. Source Citation & Verification**
Always:
- Request citations/links for all claims
- Cross-reference 3+ independent sources
- Triangulate across source types
- Document confidence levels
- Verify recency (check publication dates)

**4. Multi-Source Triangulation**
Validate across:
- Academic sources (papers, research institutions)
- Industry sources (documentation, official blogs)
- News sources (journalism, analysis)
- Community sources (GitHub, forums)

**5. Progressive Disclosure Strategy**
```
Round 1: Broad overview (5-10 sources)
  ↓ Analyze gaps
Round 2: Targeted deep-dives (10-20 sources per gap)
  ↓ Analyze remaining unknowns
Round 3: Expert-level details (specialized sources)
```

**6. Diverse Perspectives**
Actively seek:
- Different viewpoints on controversial topics
- Alternative implementations/approaches
- Critiques and limitations
- Edge cases and exceptions

### Deep Research Workflow

**Step 1: Planning (2-3 minutes)**
```markdown
Task: [User's research question]

Research Plan:
- Key aspects: [3-5 main areas to investigate]
- Source priorities: [Academic/Industry/Community/News]
- Success criteria: [What defines complete answer?]
- Validation strategy: [How to verify claims?]
```

**Step 2: Broad Discovery (5-10 minutes)**
```typescript
const broadResults = await Promise.all([
  WebSearch({ query: "core topic 2025" }),
  WebSearch({ query: "core topic latest developments" }),
  WebSearch({ query: "core topic best practices" })
]);
```

**Step 3: Gap Analysis**
Identify:
- Unanswered questions
- Aspects needing deeper investigation
- Conflicting claims to resolve

**Step 4: Targeted Deep-Dives**

**Code/Technical:**
```typescript
const codeContext = await mcp__exa__get_code_context_exa({
  query: "specific technical implementation",
  tokensNum: "dynamic"
});
```

**Academic Papers:**
```typescript
// Find papers
const papers = await mcp__exa__web_search_exa({
  query: "research topic arxiv nature",
  numResults: 10
});
// Extract PDFs using document-skills:pdf skill
```

**General/Recent:**
```typescript
const recent = await WebSearch({ query: "topic 2025 latest developments" });
```

**Autonomous Investigation:**
Use Codex for multi-step reasoning and synthesis

**Step 5: Cross-Validation**
Verify critical claims across multiple source types

**Step 6: Synthesis & Documentation**
Create structured output with:
- Executive summary
- Detailed findings per aspect
- Source citations
- Confidence levels (High/Medium/Low)
- Acknowledged gaps/limitations

### Deep Research with Codex

**When to use:**
- Topic requires 20+ sources
- Multi-step reasoning needed
- Complex synthesis required
- Time budget is 15+ minutes
- Need autonomous orchestration

**Codex capabilities:**
- Independent search strategy planning
- Multi-tool orchestration (WebSearch, Exa, etc.)
- Cross-source validation
- Claim verification
- Structured synthesis

### Exa Integration for Deep Research

**When to use Exa:**
- Academic papers (85% confidence) - Direct ArXiv, Nature, IEEE links with full-text access
- Code examples (100% confidence) - Production code, 10+ examples
- Technical documentation (95% confidence) - API docs, framework guides with deep context
- Research-heavy topics - Scientific, technical, scholarly content

**Workflow:**
```typescript
// Recent papers
const academicSources = await mcp__exa__web_search_exa({
  query: "machine learning optimization arxiv 2024 2025",
  numResults: 10
});

// Technical implementation
const technicalContext = await mcp__exa__get_code_context_exa({
  query: "transformer architecture PyTorch implementation",
  tokensNum: "dynamic"
});

// Domain-specific research
const domainResearch = await mcp__exa__web_search_exa({
  query: "quantum computing error correction nature science",
  numResults: 15
});
```

**Exa advantages:**
- Returns full article text (not just summaries)
- Direct academic paper access
- Exceptional code quality with real production examples
- Deep context with multiple implementation patterns

**Cost consideration:**
- $0.01/query
- At $100/hr developer rate: breaks even if saves >36 seconds
- Typical savings for academic/technical research: 10-30 minutes
- **ROI is excellent for deep technical research**

### PDF Extraction Workflow

**When to extract PDFs:**
- Found relevant academic papers via Exa/WebSearch
- Need detailed methodology analysis
- Extracting data tables or figures
- Building comprehensive literature review
- Validating citations and claims

**Pattern:**
```typescript
// Step 1: Find papers
const papers = await mcp__exa__web_search_exa({
  query: "neural architecture search arxiv 2024",
  numResults: 10
});

// Step 2: Download PDFs
// curl -o paper.pdf [URL]

// Step 3: Extract using document-skills:pdf
// - Extract text for content analysis
// - Extract tables for data
// - Parse citations and references
```

**Complete Academic Research Workflow:**
```markdown
1. Discovery: Use Exa to find papers
2. Download: Collect PDFs from URLs
3. Extraction: Use document-skills:pdf
   - Extract full text
   - Extract tables for quantitative data
   - Parse citations
4. Analysis: Compare methodologies, validate claims
5. Synthesis: Integrate findings, document confidence, cite sources
```

**Best practices:**
- Cite page numbers when extracting claims
- Verify extracted tables for accuracy
- Cross-reference citations across papers
- Document PDF metadata (authors, date, journal)

### Deep Research Quality Checklist

Before concluding:
- [ ] Consulted 15+ diverse sources
- [ ] Cross-validated all critical claims (3+ sources)
- [ ] Included academic/authoritative sources
- [ ] Verified source publication dates
- [ ] Documented citations for all claims
- [ ] Identified and acknowledged limitations
- [ ] Synthesized information coherently
- [ ] Provided confidence levels
- [ ] Addressed multiple perspectives
- [ ] Validated conflicting information

**For academic/technical:**
- [ ] Used Exa for academic papers and code
- [ ] Extracted and analyzed PDFs (if applicable)
- [ ] Cited papers with page numbers
- [ ] Verified data from tables
- [ ] Cross-referenced claims across papers
- [ ] Documented PDF metadata

### Output Structure

```markdown
# Deep Research: [Topic]

## Executive Summary
[2-3 sentence overview]

## Research Methodology
- Sources: [Number and types]
  - WebSearch: X queries
  - Exa: Y searches (academic, code)
  - PDFs: Z analyzed
- Time period: [Date range]
- Validation: [How claims verified]

## Key Findings

### 1. [Finding]
- **Finding**: [Statement]
- **Evidence**: [Data]
- **Sources**: [Citations]
  - Academic: Smith et al. (2024). p.15-17. [Link]
  - Code: [GitHub repo/file]
  - Industry: [Blog/docs with dates]
- **Confidence**: [High/Medium/Low]

## Synthesis
[Integration of findings, patterns, insights]

## Limitations
[Gaps, uncertainties]

## Recommendations
[Actionable next steps]

## Appendix: Source Details
### Academic Papers
1. [Author et al., Year] - [Key on p.X]

### Code Examples
1. [Repository] - [Specific approach]
```

## Common Pitfalls & Solutions

| Pitfall | Solution |
|---------|----------|
| Too broad query | ❌ "AI information" → ✅ "GPT-4 API rate limits pricing October 2025" |
| Single source | ❌ First result only → ✅ Cross-reference 3+ sources |
| Static queries | ❌ Same query when poor → ✅ Reformulate, expand, different angles |
| Ignoring recency | ❌ "React best practices" → ✅ "React 19 best practices 2025" |
| No gap analysis | ❌ Stop after first search → ✅ Identify missing info, iterate |
| Wrong tool | ❌ Exa for "restaurants NYC" → ✅ WebSearch for consumer/local |

## Best Practices

1. **WebSearch first, always** - Free and fast, start here
2. **Consider complexity** - Multi-step research or deep analysis → use Codex
3. **Supplement strategically** - Only add tools if WebSearch has clear gaps
4. **Cost-conscious** - Codex uses API, Exa costs $0.01/query
5. **Gap-driven supplements** - Don't use all tools by default, fill specific gaps
6. **Parallel execution** - Run independent queries simultaneously
7. **Cross-validate** - Verify critical claims across multiple sources

## Quick Reference

### Tool Selection Cheat Sheet

| Query Type | Primary Tool | Supplement With |
|------------|-------------|-----------------|
| Breaking news | WebSearch | None |
| Code examples | Exa | None |
| Complex research | Codex | Exa for code |
| General knowledge | WebSearch | None |
| Academic papers | Exa | WebSearch for context |
| Consumer products | WebSearch | None (Exa fails) |
| API documentation | Exa | WebSearch for overview |
| Multi-step analysis | Codex | Exa/WebSearch as needed |

### Workflow Summary

```
1. Start with WebSearch (always)
2. Analyze results:
   - Sufficient? → Done
   - Needs deep analysis? → Use Codex
   - Lacks code examples? → Add Exa
   - Multiple gaps? → Combine tools
3. Synthesize and validate
4. Iterate if gaps remain
```
