# Search Strategy Guide

**VERIFICATION_HASH:** `7f22b25e35f3c1f8`

## Overview
**IMPORTANT: Start with WebSearch, then supplement with Codex/Exa/Anna's Archive ONLY if needed.**

WebSearch is free and fast (2-4s). Use it as your primary search tool. Only add supplementary tools when WebSearch results are insufficient or require deeper analysis.

## Primary Strategy: WebSearch First

### Default Workflow
```
1. Start with WebSearch (free, fast, broad coverage)
2. Analyze results for gaps or complexity
3. If gaps exist or task is complex:
   - Need deep analysis or multi-step research? → Use Codex
   - Need code examples? → Add Exa
   - Need academic papers? → Add Anna's Archive
4. If no gaps, you're done!
```

## Tool-Specific References

### 🌐 WebSearch (START HERE - Always Use First)
**→ See "WebSearch Optimization Tactics" section below for:**
- Query decomposition and expansion
- Multi-strategy parallel search patterns
- Iterative refinement with gap analysis
- Date-aware searching techniques
**Cost:** Free | **Speed:** 2-4s

### 🤖 Codex (For Complex Analysis & Multi-Step Research)
**→ Read the `codex` snippet for:**
- Autonomous multi-step research with reasoning
- Heavy analytical tasks requiring synthesis
- Complex queries needing deep investigation
- When WebSearch provides results but deeper analysis is needed
**Cost:** API usage (OpenAI/Anthropic) | **Speed:** 10-30s depending on complexity
**Use when:** Task requires autonomous research, multi-source synthesis, or complex reasoning beyond simple search results

### 🔍 Exa (Supplement Only When Needed)
**→ Read the `exa` snippet for:**
- Deep code examples and production patterns
- Technical documentation with context
- When WebSearch lacks technical depth
**Cost:** $0.01/query | **Speed:** 5-6s
**Use when:** WebSearch doesn't provide sufficient code examples or technical detail

### 📚 Anna's Archive (Supplement Only When Needed)
**→ Read the `annas-archive` snippet for:**
- Academic papers and research
- Technical books and textbooks
- When WebSearch lacks scholarly sources
**Use when:** Need academic foundation or comprehensive book content

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
      │  └─ Use Codex (read codex snippet)
      │     → Codex can autonomously search + reason + synthesize
      │
      ├─ Code examples/technical depth?
      │  └─ Supplement with Exa (read exa snippet)
      │
      ├─ Academic papers/books?
      │  └─ Supplement with Anna's Archive (read annas-archive snippet)
      │
      └─ Multiple gaps?
         └─ Combine tools: Codex + Exa + Anna's Archive
            → Use Codex for complex research orchestration
```

---

# WebSearch Optimization Tactics

## When to Use WebSearch

Use the `WebSearch` tool for:
- **Breaking news & current events** - Real-time information
- **General knowledge** - Broad overviews and summaries
- **Consumer products** - Reviews, comparisons, shopping
- **Local information** - Restaurants, services, businesses
- **Regulatory/legal info** - Multi-jurisdictional coverage
- **Trend analysis** - What's happening now

**Cost:** Free (no API charges)
**Speed:** 2-4 seconds typical

## Query Optimization Strategies

### 1. Query Decomposition

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

### 2. Query Expansion & Reformulation

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

### 3. Multi-Strategy Parallel Search

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

### 4. Iterative Search with Gap Analysis

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

## Date-Aware Searching

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

## Domain Filtering

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

## Query Clarity Guidelines

### Specificity Levels

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

## Common Pitfalls & Solutions

### Pitfall 1: Too Broad
```
❌ "AI information"
✅ "GPT-4 API rate limits and pricing October 2025"
```

### Pitfall 2: Single Source
```
❌ Relying on first search result
✅ Cross-reference 3+ sources, validate claims
```

### Pitfall 3: Static Queries
```
❌ Repeating same query when results are poor
✅ Reformulate, expand, try different angles
```

### Pitfall 4: Ignoring Recency
```
❌ "React best practices" (could be outdated)
✅ "React 19 best practices 2025"
```

### Pitfall 5: No Gap Analysis
```
❌ Stopping after first search
✅ Identify missing info, iterate with targeted searches
```

## Advanced Techniques

### Multi-Source Validation

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

## Success Metrics

Evaluate search effectiveness:

- **Coverage**: Found all relevant information?
- **Accuracy**: Sources authoritative and cross-validated?
- **Efficiency**: Optimal queries for information density?
- **Freshness**: Information recency appropriate?
- **Relevance**: Results directly address query intent?

---

## Recommended Search Pattern

### Step 1: Always Start with WebSearch
```typescript
// ALWAYS start here (free, fast)
const webResults = await WebSearch({ query: userQuery });
```

### Step 2: Analyze WebSearch Results & Task Complexity
```typescript
// Check if results are sufficient and assess task needs
const analysis = {
  needsDeepAnalysis: requiresMultiStepReasoning(query),
  needsComplexSynthesis: requiresCrossSynthesis(webResults),
  hasCodeExamples: checkForCode(webResults),
  hasAcademicDepth: checkForScholarship(webResults),
  hasSufficientDetail: checkQuality(webResults)
};
```

### Step 3: Supplement ONLY if Needed
```typescript
// For complex analytical tasks, delegate to Codex
if (analysis.needsDeepAnalysis || analysis.needsComplexSynthesis) {
  // Codex autonomously handles web search + reasoning + synthesis
  return codexResearch(query); // Read 'codex' snippet for details
}

// For specific gaps, use targeted supplements
const supplements = [];

if (!analysis.hasCodeExamples) {
  // WebSearch lacks code depth → Add Exa
  supplements.push(exaSearch(query));
}

if (!analysis.hasAcademicDepth) {
  // WebSearch lacks academic sources → Add Anna's Archive
  supplements.push(annasArchive(query));
}

// Run supplements in parallel if needed
if (supplements.length > 0) {
  const supplementResults = await Promise.all(supplements);
  return synthesize([webResults, ...supplementResults]);
}

return webResults; // WebSearch was sufficient!
```

## Common Search Patterns

### Pattern 1: WebSearch Only (Most Common)
```
1. WebSearch provides sufficient results
2. Done! No need for other tools
```

### Pattern 2: WebSearch → Delegate to Codex (For Complex Research)
```
1. WebSearch gives initial overview
2. Task requires deep analysis, multi-step reasoning, or synthesis
3. Delegate to Codex for autonomous research (read codex snippet)
   → Codex handles its own web searching + reasoning + synthesis
```

### Pattern 3: WebSearch → Supplement with Exa
```
1. WebSearch gives overview
2. Lacks code examples or technical depth
3. Add Exa for production code (read exa snippet)
```

### Pattern 4: WebSearch → Supplement with Anna's Archive
```
1. WebSearch gives overview
2. Lacks academic foundation
3. Add Anna's Archive for papers/books (read annas-archive snippet)
```

### Pattern 5: WebSearch → Supplement with Multiple Tools
```
1. WebSearch gives overview
2. Multiple gaps identified
3. Combine tools strategically:
   - Codex for orchestration + synthesis
   - Exa for code examples
   - Anna's Archive for academic papers
```

## Quality Checklist

### Before Searching
- [ ] Identified information type (academic/code/web/all)
- [ ] Selected appropriate tool(s)
- [ ] Read relevant tool snippets for best practices

### During Search
- [ ] Using parallel execution where appropriate
- [ ] Following tool-specific optimization (see snippets)
- [ ] Cross-validating critical claims

### After Search
- [ ] Synthesized across source types
- [ ] Validated consistency
- [ ] Identified and addressed gaps
- [ ] Documented sources

## Key Principles

1. **WebSearch first, always** - It's free and fast, start here
2. **Consider complexity** - For multi-step research or deep analysis, use Codex
3. **Supplement strategically** - Only add supplementary tools if WebSearch has clear gaps
4. **Read the snippets** - Each tool has detailed guidance (`codex`, `exa`, `annas-archive`)
5. **Cost-conscious** - Consider API costs (Codex uses OpenAI/Anthropic, Exa costs $0.01/query)
6. **Gap-driven supplements** - Don't use all tools by default, use them to fill specific gaps

## Quick Reference

**For detailed implementation, always read:**
- See "WebSearch Optimization Tactics" section above for query optimization and current information
- `codex` snippet - Autonomous research, multi-step analysis, synthesis
- `exa` snippet - Code examples, APIs, technical docs
- `annas-archive` snippet - Academic papers, books, research