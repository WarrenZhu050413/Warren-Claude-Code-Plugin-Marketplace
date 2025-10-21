---
name: Searching Deeply
description: Advanced search strategies combining WebSearch, Exa, and Codex for comprehensive information discovery. Use when researching topics, finding code examples, gathering technical documentation, or performing complex multi-source searches. Keywords - search, research, web search, exa, code examples, documentation, technical research, information gathering.
---

# Deeply Searching

## Purpose

This skill provides comprehensive search strategies that combine multiple tools (WebSearch, Exa, Codex) to achieve optimal information discovery across different content types. It teaches you how to select the right tool for each task and orchestrate them effectively.

## When to Use This Skill

Use this skill when the user needs to:
- Research a topic thoroughly with multiple sources
- Find code examples and technical documentation
- Compare information across different sources
- Validate claims or gather evidence
- Perform complex queries requiring multi-tool orchestration
- Balance search breadth (WebSearch) with depth (Exa/Codex)

## Core Search Philosophy

**Always start with WebSearch first.** It's free and fast (2-4s). Use it as your primary search tool, then supplement with other tools only when WebSearch results are insufficient or require deeper analysis.

## Search Tool Selection Guide

### Tool Comparison Matrix

| Tool | Best For | Cost | Speed | Use Case |
|------|----------|------|-------|----------|
| **WebSearch** | Breaking news, general knowledge, consumer products, local info | Free | 2-4s | Primary search tool - always start here |
| **Exa** | Code examples, technical docs, API/library usage, framework patterns | $0.01/query | 5-6s | Supplement when code depth needed |
| **Codex** | Complex analysis, multi-step research, synthesis across sources | API usage | 10-30s | Autonomous research requiring reasoning |

### When to Use WebSearch (START HERE)

Use WebSearch for:
- **Breaking news & current events** (95% confidence) - Better synthesis and comprehensive coverage
- **General knowledge** - Broad overviews and summaries
- **Consumer products** (90% confidence) - Reviews, comparisons, shopping
- **Local information** (85% confidence) - Restaurants, services, businesses
- **Regulatory/legal information** (90% confidence) - Systematic multi-jurisdictional coverage
- **Trend analysis** - What's happening now

### When to Use Exa (SUPPLEMENT ONLY)

Use Exa when WebSearch lacks technical depth:
- **Code examples & snippets** (100% confidence) - Returns production-ready code from real repositories with exceptional depth
- **Technical documentation** (95% confidence) - Deep context with multiple implementation patterns
- **API/library usage** (100% confidence) - Real-world examples from GitHub, unmatched quality
- **Framework/library patterns** (100% confidence) - Production code from real projects
- **Academic research papers** (85% confidence) - Direct links to papers (Nature, ArXiv), full-text access
- **Performance optimization** (95% confidence) - Advanced patterns with production examples

**Key Differences:**
- Exa returns full article text, WebSearch returns summaries
- Exa code quality is exceptional (10+ real examples), WebSearch is basic
- Exa **fails badly** on consumer/shopping queries - it's optimized for technical/research content

**Available Exa Tools:**
- `mcp__exa__web_search_exa` - General web search (5 results default)
- `mcp__exa__get_code_context_exa` - **BEST for code** - Returns production code with "dynamic" token allocation

### When to Use Codex

Use Codex when the task requires:
- Autonomous multi-step research with reasoning
- Heavy analytical tasks requiring synthesis
- Complex queries needing deep investigation
- WebSearch provides results but deeper analysis is needed
- Cross-source validation and comparison

## Decision Tree

```
Always start here ↓

1. Run WebSearch first
   ↓
2. Analyze results and task complexity
   ↓
3. Are results sufficient?
   ├─ YES → Done! Use WebSearch results
   │
   └─ NO → What's missing or needed?
      ├─ Need deep analysis/multi-step research?
      │  └─ Use Codex
      │     → Codex autonomously searches + reasons + synthesizes
      │
      ├─ Code examples/technical depth?
      │  └─ Supplement with Exa
      │     → Use get_code_context_exa for best results
      │
      └─ Multiple gaps?
         └─ Combine tools: Codex + Exa
            → Codex orchestrates, Exa provides code
```

## WebSearch Optimization Strategies

### Query Decomposition

Break complex queries into focused sub-queries:

**❌ Too Complex:**
```
"Analyze AI trends and compare frameworks and recommend best practices"
```

**✅ Decomposed:**
```typescript
Promise.all([
  WebSearch({ query: "AI framework trends 2024 2025" }),
  WebSearch({ query: "LLM framework comparison benchmarks" }),
  WebSearch({ query: "AI development best practices production" })
])
```

**Examples:**

| Complex Query | Decomposed Sub-Queries |
|--------------|------------------------|
| "How do I fix authentication in my app?" | 1. "JWT authentication troubleshooting"<br>2. "Node.js authentication best practices"<br>3. "Common auth error solutions" |
| "Best database for my project" | 1. "SQL vs NoSQL comparison 2025"<br>2. "PostgreSQL performance benchmarks"<br>3. "Database scaling strategies" |

### Query Expansion & Reformulation

**Add Context:**
```
Vague: "authentication error"
Better: "JWT token authentication error Node.js Express"
```

**Use Synonyms:**
```
machine learning → ML artificial intelligence deep learning
database optimization → query performance tuning indexing
responsive design → mobile-first adaptive layout
```

**Reformulation Pattern:**
```typescript
// Original vague query
const original = "How do I fix this?";

// Reformulated with context
const reformulated = "How to debug authentication errors in Node.js JWT tokens";

// With technical details
const specific = "JWT token expired error 401 Express.js middleware solution";
```

### Multi-Strategy Parallel Search

Execute different query variations simultaneously:

```typescript
// Strategy A: Core + Expanded + Alternative
Promise.all([
  WebSearch({ query: "React Server Components performance" }),
  WebSearch({ query: "RSC server-side rendering optimization" }),
  WebSearch({ query: "Next.js App Router streaming speed" })
])

// Strategy B: Breadth-First Discovery
Promise.all([
  WebSearch({ query: "LLM frameworks", numResults: 3 }),
  WebSearch({ query: "language model APIs", numResults: 3 }),
  WebSearch({ query: "AI agent libraries", numResults: 3 })
])
```

### Iterative Search with Gap Analysis

```typescript
async function iterativeWebSearch(query: string) {
  let round = 1;
  let allResults = [];
  let gaps = [];

  while (round <= 3) {
    // Refine query based on gaps
    const refinedQuery = round === 1
      ? query
      : refineBasedOnGaps(query, gaps);

    const results = await WebSearch({ query: refinedQuery });
    allResults.push(...results);

    // Analyze what's missing
    gaps = analyzeGaps(query, allResults);

    if (gaps.length === 0) break;
    round++;
  }

  return synthesize(allResults);
}
```

### Date-Aware Searching

Always include temporal context for time-sensitive queries:

```typescript
// ✅ Good - Includes year
"LLM frameworks 2024 2025"
"React 19 features release"
"TypeScript 5 new capabilities"

// ✅ Good - Temporal keywords
"latest Next.js updates"
"recent AI developments"
"current best practices"
"upcoming JavaScript features"

// ❌ Bad - No temporal context
"AI frameworks"
"React features"
"TypeScript capabilities"
```

**Current Date Context:** October 2025
- Use "2024 2025" for recent developments
- Use "2025" for cutting-edge information
- Avoid older years unless historical context needed

### Domain Filtering

Control which domains to include/exclude:

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

// Academic research only
WebSearch({
  query: "machine learning research",
  allowed_domains: ["arxiv.org", "scholar.google.com", "*.edu"]
})
```

### Query Specificity Levels

| Level | Example | Result Quality |
|-------|---------|----------------|
| **Vague** | "AI stuff" | Poor - Too broad |
| **General** | "machine learning" | Moderate - Still broad |
| **Specific** | "transformer architecture in LLMs" | Good - Focused |
| **Highly Specific** | "BERT vs GPT transformer differences" | Excellent - Precise |

### Adding Technical Context

```typescript
// Base query
const base = "authentication error";

// + Technology
const withTech = "JWT authentication error Node.js";

// + Framework
const withFramework = "JWT authentication error Express.js middleware";

// + Error details
const withDetails = "JWT token expired 401 unauthorized Express.js middleware";
```

## Exa for Code & Technical Content

### Exa Decision Rule

**If query contains code/API/library/framework names → Use Exa**
**If query is about news/shopping/local/general info → Use WebSearch**
**If complex technical topic → Use both in parallel**

### Hybrid Strategy for Best Results

For complex technical queries requiring both breadth and depth:
1. Use **WebSearch** for conceptual overview and current landscape
2. Use **Exa** for deep code examples and implementation details
3. **ROI:** At $100/hr developer rate, Exa breaks even if it saves >36 seconds. Typical savings: 10-30 minutes for code queries

### Exa Best Practices

- Use `get_code_context_exa` with "dynamic" token allocation for code queries
- Excellent for production-ready code from real repositories
- Returns 10+ real examples vs WebSearch's basic snippets
- Full article text extraction included
- Optimized for technical/research content, not consumer information

## Codex for Complex Research

### When to Delegate to Codex

Use Codex when:
- Task requires autonomous research with multi-step reasoning
- Need to synthesize information across multiple sources
- Complex analytical tasks beyond simple search results
- WebSearch provides initial results but deeper investigation needed

### Codex Capabilities

- Autonomous multi-step research orchestration
- Built-in reasoning and synthesis
- Can perform its own web searching
- Handles complex queries requiring deep analysis

## Search Patterns & Workflows

### Pattern 1: WebSearch Only (Most Common)

```
1. WebSearch provides sufficient results
2. Done! No need for other tools
```

**Example:**
```typescript
// User asks: "What are the latest React 19 features?"
const results = await WebSearch({
  query: "React 19 features release 2025"
});
// Results are comprehensive - done!
```

### Pattern 2: WebSearch → Delegate to Codex

```
1. WebSearch gives initial overview
2. Task requires deep analysis, multi-step reasoning, or synthesis
3. Delegate to Codex for autonomous research
```

**Example:**
```typescript
// User asks: "Compare the security models of JWT vs Session auth
// and recommend which to use for different scenarios"

// Step 1: Initial WebSearch
const overview = await WebSearch({
  query: "JWT vs session authentication security 2025"
});

// Step 2: Task requires deep analysis and synthesis
// Delegate to Codex for autonomous multi-step research
```

### Pattern 3: WebSearch → Supplement with Exa

```
1. WebSearch gives overview
2. Lacks code examples or technical depth
3. Add Exa for production code
```

**Example:**
```typescript
// User asks: "How do I implement OAuth2 in Express?"

// Step 1: WebSearch for overview
const overview = await WebSearch({
  query: "OAuth2 Express.js implementation guide 2025"
});

// Step 2: Lacks production code examples
const codeExamples = await mcp__exa__get_code_context_exa({
  query: "Express.js OAuth2 implementation examples",
  tokensNum: "dynamic"
});
```

### Pattern 4: WebSearch → Supplement with Multiple Tools

```
1. WebSearch gives overview
2. Multiple gaps identified
3. Combine tools strategically
```

**Example:**
```typescript
// User asks: "Research the best practices for building production-ready
// LLM applications, including security, cost optimization, and error handling"

// Step 1: Initial WebSearch
const overview = await WebSearch({
  query: "LLM application best practices production 2025"
});

// Step 2: Multiple gaps - needs code + deep analysis
// Use Codex for orchestration + synthesis
// Use Exa for production code examples
const codeExamples = await mcp__exa__get_code_context_exa({
  query: "production LLM application error handling security",
  tokensNum: "dynamic"
});
```

## Adaptive Search Depth

Match search depth to information needs:

```typescript
// Quick Answer (30 seconds)
const quick = await WebSearch({
  query: specificQuery,
  // Default 5 results, single query
});

// Moderate Depth (2-3 minutes)
const moderate = await Promise.all([
  WebSearch({ query: coreQuery }),
  WebSearch({ query: expandedQuery }),
  WebSearch({ query: alternativeQuery })
]);

// Deep Research (10+ minutes)
async function deepResearch(query: string) {
  // Round 1: Broad search
  const round1 = await multiQuerySearch(query);

  // Round 2: Gap-targeted
  const gaps = analyzeGaps(round1);
  const round2 = await Promise.all(
    gaps.map(gap => WebSearch({ query: gap }))
  );

  // Round 3: Deep dive on key findings
  const keyTopics = extractKeyTopics([...round1, ...round2]);
  const round3 = await Promise.all(
    keyTopics.map(topic => WebSearch({ query: topic }))
  );

  return synthesize([round1, round2, round3]);
}
```

## Multi-Source Validation

Validate claims across different source types:

```typescript
async function validateClaim(claim: string) {
  // Search across different source types
  const [general, academic, news] = await Promise.all([
    WebSearch({ query: claim }),
    WebSearch({
      query: claim,
      allowed_domains: ["*.edu", "scholar.google.com"]
    }),
    WebSearch({
      query: `${claim} news 2025`,
      allowed_domains: ["nytimes.com", "reuters.com", "bbc.com"]
    })
  ]);

  // Analyze consistency
  return {
    claim,
    generalSupport: analyze(general),
    academicSupport: analyze(academic),
    newsSupport: analyze(news),
    confidence: calculateConsistency([general, academic, news])
  };
}
```

## Best Practices

### General Principles

1. **WebSearch first, always** - It's free and fast, start here
2. **Consider complexity** - For multi-step research or deep analysis, use Codex
3. **Supplement strategically** - Only add tools if WebSearch has clear gaps
4. **Cost-conscious** - Codex uses OpenAI/Anthropic API, Exa costs $0.01/query
5. **Gap-driven supplements** - Don't use all tools by default, fill specific gaps
6. **Parallel execution** - Run independent queries simultaneously
7. **Cross-validate** - Verify critical claims across multiple sources

### Common Pitfalls & Solutions

**Pitfall 1: Too Broad**
```
❌ "AI information"
✅ "GPT-4 API rate limits and pricing October 2025"
```

**Pitfall 2: Single Source**
```
❌ Relying on first search result
✅ Cross-reference 3+ sources, validate claims
```

**Pitfall 3: Static Queries**
```
❌ Repeating same query when results are poor
✅ Reformulate, expand, try different angles
```

**Pitfall 4: Ignoring Recency**
```
❌ "React best practices" (could be outdated)
✅ "React 19 best practices 2025"
```

**Pitfall 5: No Gap Analysis**
```
❌ Stopping after first search
✅ Identify missing info, iterate with targeted searches
```

**Pitfall 6: Wrong Tool for Task**
```
❌ Using Exa for "best restaurants in NYC"
✅ Using WebSearch for consumer/local queries
```

## Quality Checklist

### Before Searching
- [ ] Identified information type (general/code/academic/all)
- [ ] Selected appropriate starting tool (usually WebSearch)
- [ ] Formulated specific query with context

### During Search
- [ ] Using parallel execution where appropriate
- [ ] Following tool-specific optimization strategies
- [ ] Cross-validating critical claims across sources
- [ ] Analyzing gaps after each search round

### After Search
- [ ] Synthesized information across sources
- [ ] Validated consistency of claims
- [ ] Identified and addressed any remaining gaps
- [ ] Documented sources and confidence levels

## Deep Research Mode

When the user explicitly requests deep research or when a topic requires comprehensive multi-step investigation, use this native deep research workflow.

### When to Use Deep Research

Activate deep research mode when:
- User explicitly asks for "deep research", "comprehensive analysis", or "thorough investigation"
- Topic is complex and requires multi-step reasoning
- Need to synthesize information from dozens of sources
- Requires structured research plan with progressive exploration
- Task involves validating claims across multiple perspectives

### Deep Research Best Practices (2025)

Based on current industry best practices from ChatGPT Deep Research, Google Gemini, and Perplexity AI:

**1. Start with Clear, Detailed Queries**
```
❌ Vague: "AI trends"
✅ Specific: "What are the latest transformer architecture innovations in large language models as of October 2025, with focus on efficiency improvements?"
```

**Key principles:**
- Be specific while avoiding pronouns ("they", "that information")
- Avoid vague terms like "recently" - specify exact timeframes
- Provide explicit context about what you're looking for
- State your goal and constraints upfront

**2. Draft a Structured Research Plan**

Before executing deep research:
```markdown
Research Plan:
1. Identify key aspects to investigate
2. Prioritize source types (academic papers > industry blogs > news)
3. Define success criteria
4. Plan validation strategy
```

**3. Source Citation & Verification**

Always:
- Request citations or links for all claims
- Cross-reference 3+ independent sources
- Triangulate information across source types
- Document confidence levels per finding
- Verify recency of sources (check publication dates)

**4. Multi-Source Triangulation**

For critical claims, validate across:
- Academic sources (papers, research institutions)
- Industry sources (documentation, official blogs)
- News sources (journalism, analysis)
- Community sources (GitHub, forums, discussions)

Agreement across diverse sources = higher confidence.

**5. Progressive Disclosure Strategy**

Use iterative exploration:
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

**7. Automation & Efficiency**

For large-scale research:
- Use parallel queries to maximize throughput
- Leverage Python/APIs for data collection at scale
- Apply filters to reduce noise early
- Use AI/ML to prioritize high-value sources

### Deep Research Workflow

**Step 1: Planning (2-3 minutes)**
```markdown
Task: [User's research question]

Research Plan:
- Key aspects: [List 3-5 main areas to investigate]
- Source priorities: [Academic/Industry/Community/News]
- Success criteria: [What defines complete answer?]
- Validation strategy: [How to verify claims?]
```

**Step 2: Broad Discovery (5-10 minutes)**

Use WebSearch with parallel queries for landscape overview:
```typescript
const broadResults = await Promise.all([
  WebSearch({ query: "core topic 2025" }),
  WebSearch({ query: "core topic latest developments" }),
  WebSearch({ query: "core topic best practices" })
]);
```

**Step 3: Gap Analysis**

Identify missing information:
- What questions remain unanswered?
- Which aspects need deeper investigation?
- Are there conflicting claims to resolve?

**Step 4: Targeted Deep-Dives**

For each gap, execute focused research based on content type:

**Code/Technical Content:**
```typescript
const codeContext = await mcp__exa__get_code_context_exa({
  query: "specific technical implementation",
  tokensNum: "dynamic"  // Returns 100-1000+ most useful tokens
});
```

**Academic Papers:**
```typescript
// 1. Find papers with Exa (excellent for academic content)
const papers = await mcp__exa__web_search_exa({
  query: "research topic arxiv nature",
  numResults: 10
});

// 2. Extract full text from PDFs using pdf skill
// See "PDF Extraction Workflow" section below
```

**General/Recent Developments:**
```typescript
const recent = await WebSearch({
  query: "topic 2025 latest developments"
});
```

**Autonomous Investigation:**
- Use Codex for multi-step reasoning and synthesis

**Step 5: Cross-Validation**

Verify critical claims:
```typescript
async function validateClaim(claim: string) {
  const sources = await Promise.all([
    WebSearch({ query: `${claim} academic research` }),
    WebSearch({ query: `${claim} industry analysis` }),
    WebSearch({ query: `${claim} 2025` })
  ]);
  return analyzeConsistency(sources);
}
```

**Step 6: Synthesis & Documentation**

Create structured output with:
- Executive summary (key findings)
- Detailed findings per research aspect
- Source citations for all claims
- Confidence levels (High/Medium/Low)
- Gaps or limitations acknowledged

### Deep Research with Codex

For autonomous deep research, delegate to Codex:

```typescript
// User asks for comprehensive research
// Codex autonomously:
// 1. Plans research strategy
// 2. Executes searches across tools
// 3. Analyzes and synthesizes results
// 4. Validates claims
// 5. Produces comprehensive report
```

**When to use Codex for deep research:**
- Topic requires 20+ sources
- Multi-step reasoning needed
- Complex synthesis required
- Time budget is 15+ minutes
- Need autonomous orchestration

**Codex deep research capabilities:**
- Independent search strategy planning
- Multi-tool orchestration (WebSearch, Exa, etc.)
- Cross-source validation
- Claim verification
- Structured synthesis

### Exa Integration for Deep Research

Exa excels at finding high-quality technical and academic content. Integrate it strategically in deep research:

**When to use Exa in deep research:**
- **Academic papers** (85% confidence) - Direct links to ArXiv, Nature, IEEE papers with full-text access
- **Code examples** (100% confidence) - Production code from real repositories, 10+ examples
- **Technical documentation** (95% confidence) - API docs, framework guides with deep context
- **Research-heavy topics** - Scientific, technical, or scholarly content

**Exa workflow for academic research:**

```typescript
// Pattern 1: Find recent papers
const academicSources = await mcp__exa__web_search_exa({
  query: "machine learning optimization arxiv 2024 2025",
  numResults: 10  // Get top 10 papers
});

// Pattern 2: Get technical implementation details
const technicalContext = await mcp__exa__get_code_context_exa({
  query: "transformer architecture PyTorch implementation",
  tokensNum: "dynamic"  // Optimal token efficiency
});

// Pattern 3: Domain-specific research
const domainResearch = await mcp__exa__web_search_exa({
  query: "quantum computing error correction nature science",
  numResults: 15  // Comprehensive coverage
});
```

**Exa advantages for deep research:**
- Returns **full article text**, not just summaries (unlike WebSearch)
- Direct access to academic papers (ArXiv, Nature, IEEE, etc.)
- Exceptional code quality with real production examples
- Deep context with multiple implementation patterns
- Better for synthesis across technical sources

**Cost consideration:**
- Exa: $0.01/query
- At $100/hr developer rate: breaks even if saves >36 seconds
- Typical time savings for academic/technical research: 10-30 minutes per query
- **ROI is excellent for deep research on technical topics**

### PDF Extraction Workflow

Academic deep research often requires analyzing research papers in PDF format. Integrate PDF extraction for comprehensive analysis:

**When to extract PDFs:**
- Found relevant academic papers via Exa or WebSearch
- Need to analyze research methodology in detail
- Extracting data tables or figures from papers
- Building comprehensive literature review
- Validating citations and claims in papers

**PDF Extraction Pattern:**

```typescript
// Step 1: Find papers with Exa
const papers = await mcp__exa__web_search_exa({
  query: "neural architecture search arxiv 2024",
  numResults: 10
});

// Step 2: Download PDFs (if URLs provided)
// Use bash: curl -o paper.pdf [URL]

// Step 3: Extract text and tables using pdf skill
// Invoke skill: document-skills:pdf
// Then use PDF extraction tools to:
// - Extract all text for full content analysis
// - Extract tables for data analysis
// - Extract metadata (authors, citations, dates)
```

**Academic research workflow with PDFs:**

1. **Discovery Phase**: Use Exa to find relevant papers
   ```typescript
   const papers = await mcp__exa__web_search_exa({
     query: "research topic arxiv scholar",
     numResults: 15
   });
   ```

2. **Download Phase**: Collect PDFs from paper URLs
   ```bash
   # Download papers
   curl -o paper1.pdf [URL]
   curl -o paper2.pdf [URL]
   ```

3. **Extraction Phase**: Use `document-skills:pdf` skill
   - Extract full text for content analysis
   - Extract tables for quantitative data
   - Parse citations and references

4. **Analysis Phase**:
   - Compare methodologies across papers
   - Validate claims with original sources
   - Build synthesis across multiple papers
   - Extract key findings and evidence

5. **Synthesis Phase**:
   - Integrate findings from all papers
   - Document confidence levels per claim
   - Cite specific papers and page numbers

**PDF extraction best practices:**
- Always cite page numbers when extracting claims
- Verify extracted tables for accuracy
- Cross-reference citations in multiple papers
- Document PDF metadata (authors, publication date, journal)

**Tools available:**
- `document-skills:pdf` - Comprehensive PDF manipulation (text extraction, tables, forms, merging)
- Exa `web_search_exa` - Finding academic papers with direct links
- Bash `curl` - Downloading PDF files

**Example: Complete academic research workflow**

```markdown
Research Question: "What are the latest techniques for neural architecture search?"

Step 1: Find papers with Exa
→ 15 papers from ArXiv, NeurIPS, ICML

Step 2: Download top 5 most relevant PDFs
→ paper1.pdf through paper5.pdf

Step 3: Extract content using pdf skill
→ Full text, tables, methodology sections

Step 4: Analyze and synthesize
→ Compare techniques across papers
→ Validate performance claims with extracted tables
→ Document citations with page numbers

Step 5: Output structured findings
→ Executive summary
→ Key techniques with paper citations (Author et al., 2024, p.15)
→ Comparative analysis table
→ Recommendations based on evidence
```

### OSINT Techniques for Advanced Research

For investigative research:

**Data Mining:**
- Use advanced algorithms to uncover patterns
- Analyze large datasets for trends
- Filter noise and prioritize signal

**Cross-Referencing:**
- Verify through multiple independent sources
- Compare data across different platforms
- Identify discrepancies and investigate

**Automation:**
- Python scripts for batch data collection
- API integration for programmatic access (including Exa API)
- Scheduled monitoring for updates

**Deep Web Sources:**
- Academic databases not indexed by search engines
- Specialized repositories (ArXiv, PubMed, IEEE Xplore)
- Industry-specific archives
- Use Exa to access papers from these sources efficiently

### Deep Research Quality Checklist

Before concluding:
- [ ] Consulted 15+ diverse sources
- [ ] Cross-validated all critical claims (3+ sources)
- [ ] Included academic/authoritative sources
- [ ] Verified source publication dates (recency)
- [ ] Documented citations for all claims
- [ ] Identified and acknowledged limitations
- [ ] Synthesized information coherently
- [ ] Provided confidence levels for findings
- [ ] Addressed multiple perspectives
- [ ] Validated conflicting information

**For academic/technical deep research:**
- [ ] Used Exa for high-quality academic papers and code examples
- [ ] Extracted and analyzed relevant PDFs (if applicable)
- [ ] Cited specific papers with page numbers
- [ ] Verified data from extracted tables
- [ ] Cross-referenced claims across multiple papers
- [ ] Documented PDF metadata (authors, dates, journals)

### Example: Deep Research Output Structure

```markdown
# Deep Research: [Topic]

## Executive Summary
[2-3 sentence overview of key findings]

## Research Methodology
- Sources consulted: [Number and types]
  - WebSearch queries: X
  - Exa searches: Y (academic papers, code examples)
  - PDFs analyzed: Z
- Time period: [Date range]
- Validation strategy: [How claims were verified]

## Key Findings

### 1. [First Major Finding]
- **Finding**: [Clear statement]
- **Evidence**: [Supporting data]
- **Sources**: [Citations with links]
  - Academic: Smith et al. (2024). "Paper Title." Journal. p.15-17. [Link]
  - Code: [GitHub repo/file with specific implementation]
  - Industry: [Blog/documentation with dates]
- **Confidence**: [High/Medium/Low]

### 2. [Second Major Finding]
[Same structure...]

## Synthesis
[Integration of findings, patterns, insights]

## Limitations
[What couldn't be found, gaps, uncertainties]

## Recommendations
[Actionable next steps or conclusions]

## Appendix: Source Details
### Academic Papers Analyzed
1. [Author et al., Year] - [PDF extracted, key methodology on p.X]
2. [Author et al., Year] - [PDF extracted, results table on p.Y]

### Code Examples Reviewed
1. [Repository/implementation] - [Exa code context, specific approach]
2. [Repository/implementation] - [Alternative pattern]
```

## Success Metrics

Evaluate search effectiveness:

- **Coverage**: Found all relevant information?
- **Accuracy**: Sources authoritative and cross-validated?
- **Efficiency**: Optimal queries for information density?
- **Freshness**: Information recency appropriate for context?
- **Relevance**: Results directly address query intent?
- **Cost-effectiveness**: Appropriate tool selection for task?

**Deep Research specific metrics:**
- **Source diversity**: Multiple source types consulted?
- **Validation depth**: Critical claims verified across 3+ sources?
- **Citation quality**: All claims properly attributed?
- **Synthesis quality**: Information integrated coherently?
- **Perspective breadth**: Multiple viewpoints considered?

## Quick Reference

### Tool Selection Cheat Sheet

| Query Type | Primary Tool | Supplement With |
|------------|-------------|-----------------|
| Breaking news | WebSearch | None |
| Code examples | Exa | None |
| Complex research | Codex | Exa for code |
| General knowledge | WebSearch | None |
| Academic papers | Exa | WebSearch for context |
| Consumer products | WebSearch | None (Exa fails here) |
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
