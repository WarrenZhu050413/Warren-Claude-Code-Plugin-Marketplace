---
description: "Iterative parallel search strategy using WebSearch and Exa - keep searching until you find answers"
SNIPPET_NAME: DEEPSEARCH
ANNOUNCE_USAGE: true
---

# Deep Search Strategy

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: DEEPSEARCH

If multiple snippets are detected, combine them:

📎 **Active Contexts**: DEEPSEARCH, snippet2, snippet3

---

**VERIFICATION_HASH:** `deepsearch_v1_20251109`

## Trigger Keywords

This snippet should be active when:
- User mentions: "deep search", "research", "can't find", "need more information"
- User asks for comprehensive research on a topic
- User needs to find multiple sources or examples
- User says "DEEPSEARCH" (all caps) to explicitly trigger
- When initial searches fail or return insufficient results

## Auto-Invoke Skill

When deep search is needed, **ALWAYS invoke the searching-deeply skill first**:

```
Use the Skill tool with skill="searching-deeply"
```

This loads the complete iterative search methodology and best practices.

## Quick Reference (When Skill Not Needed)

For simple deep searches or when skill already loaded:

### Core Strategy

**Search in parallel. Learn from failures. Keep iterating.**

Never stop after one search round - launch new searches based on what worked and what didn't.

### Available Tools

- **WebSearch** - General info, news, tutorials (free, fast)
- **mcp__exa__get_code_context_exa** - Code examples ($0.01/query)
- **mcp__exa__web_search_exa** - Academic papers, technical docs ($0.01/query)

### Iterative Workflow

**Round 1: Launch 3-5 parallel searches from different angles**
```
- WebSearch with query variations
- Different phrasings, synonyms, related terms
- Add context: "2024 2025", tech stack, keywords
```

**Round 2: Analyze & iterate**
```
What did you learn?
- New terminology discovered?
- Specific sources mentioned?
- Related topics to explore?

What's missing?
- Gaps in understanding
- Unanswered questions
- Need more examples

→ Launch 3-5 new parallel searches targeting gaps
```

**Round 3+: Keep going until complete**
```
Don't stop until:
- Question fully answered
- Multiple sources confirm findings
- Examples found and verified
- All gaps filled
```

### Query Optimization

**Make queries specific:**
- ❌ "authentication"
- ✅ "JWT authentication Express.js tutorial 2025"

**Add context:**
- Technology: "Node.js", "Python", "React"
- Timeframe: "2024 2025" for recent info
- Type: "tutorial", "example", "production", "best practices"

**Use domain filtering:**
```javascript
// Academic sources
allowed_domains: ["*.edu", "arxiv.org", "scholar.google.com"]

// Developer sources
allowed_domains: ["github.com", "dev.to", "stackoverflow.com"]
```

### When Stuck

**If results are poor:**
1. Try different keywords/synonyms
2. Broaden or narrow scope
3. Split into smaller questions
4. Switch tools (WebSearch ↔ Exa)
5. Search related topics first

**Never give up after one failed search.**

### Common Research Patterns

**Quick Answer:**
Single focused WebSearch with specific query

**General Research:**
3-5 parallel WebSearch with different angles, iterate based on results

**Code Research:**
- WebSearch for overview
- mcp__exa__get_code_context_exa for examples
- Iterate for edge cases, error handling

**Academic Research:**
- WebSearch for overview
- mcp__exa__web_search_exa for papers
- Use google-scholar skill for citations
- Use search-cli to download PDFs
- Use document-skills:pdf to extract content

### Example: Iterative Search Flow

```
Round 1:
WebSearch: "Python async programming"
→ Learned: asyncio is the main library

Round 2 (3 parallel searches):
WebSearch: "Python asyncio tutorial 2025"
WebSearch: "asyncio vs threading when to use"
mcp__exa__get_code_context_exa: "Python asyncio examples"
→ Learned: Good basics, but need error handling

Round 3 (3 parallel searches):
WebSearch: "asyncio error handling best practices"
WebSearch: "asyncio common mistakes"
mcp__exa__get_code_context_exa: "asyncio exception handling"
→ Complete understanding achieved
```

## Validation

Cross-reference findings:
- ✓ Check multiple sources
- ✓ Verify recent dates (2024-2025)
- ✓ Look for authoritative sources
- ✓ Test code examples
- ✓ Confirm consistency across sources

## Related Resources

- **google-scholar** skill - Academic paper research with citation tracking
- **search-cli** skill - Download PDFs from Anna's Archive
- **document-skills:pdf** - Extract text from downloaded papers
- **SEARCHCLI** snippet - Quick reference for search-cli tool

## Persistence Rules

**NEVER GIVE UP AFTER ONE FAILED SEARCH**

Keep iterating until you find complete, validated answers.

**Remember:** The key to deep search is persistence - each round builds on the last, filling gaps and refining understanding.
