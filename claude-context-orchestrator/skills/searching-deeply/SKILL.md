---
name: Searching Deeply
description: Iterative parallel search strategy using WebSearch and Exa. Launch multiple searches simultaneously, learn from failures, and keep iterating until finding answers. Use for research, code examples, documentation, and technical information gathering.
---

# Searching Deeply

## Core Strategy

**Search in parallel. Learn from failures. Keep iterating.**

Never give up after one search round. Launch new searches based on what worked and what didn't.

## Available Tools

- **WebSearch** - General info, news, tutorials, overviews (free, fast)
- **mcp__exa__get_code_context_exa** - Code examples, implementations ($0.01/query)
- **mcp__exa__web_search_exa** - Academic papers, technical docs ($0.01/query)

## Related Skills & Snippets

- **google-scholar** skill - For academic paper research with citation tracking
- **DOWNLOAD** snippet - For downloading PDFs from Anna's Archive
- **document-skills:pdf** - For extracting text from downloaded papers

## Iterative Workflow

### Round 1: Launch Parallel Searches

Start with 3-5 searches from different angles:

**General topics:**
- WebSearch with variations of query
- Different phrasings, synonyms, related terms
- Add context: year "2024 2025", tech stack, keywords

**Code/implementation:**
- WebSearch for overview/tutorial
- mcp__exa__get_code_context_exa for real examples

**Academic/research:**
- WebSearch for overview
- mcp__exa__web_search_exa for papers
- Use google-scholar skill for deeper research

### Round 2: Analyze & Iterate

**What did you learn?**
- New terminology discovered?
- Specific authors/sources mentioned?
- Related topics to explore?

**What's missing?**
- Gaps in understanding
- Unanswered questions
- Need more examples/evidence

**Launch next round:**
- Reformulate queries with new terms
- Search for specific gaps
- Try broader or narrower scope
- 3-5 new parallel searches

### Round 3+: Keep Going

**Don't stop until:**
- Question fully answered
- Multiple sources confirm findings
- Examples found and verified
- All gaps identified and filled

**If stuck:**
- Try different keywords/synonyms
- Split complex query into parts
- Search related topics first
- Switch tools (WebSearch ↔ Exa)
- Check alternative sources

## Query Optimization

**Make queries specific:**
- ❌ "authentication"
- ✅ "JWT authentication Express.js tutorial 2025"

**Add context:**
- Technology: "Node.js", "Python", "React"
- Timeframe: "2024 2025" for recent
- Type: "tutorial", "example", "production", "best practices"

**Use domain filtering:**
- Academic: `allowed_domains: ["*.edu", "arxiv.org"]`
- Developer: `allowed_domains: ["github.com", "dev.to"]`

## Persistence Rules

**Never give up after one failed search.**

If results are poor:
1. Try different keywords
2. Broaden or narrow scope
3. Split into smaller questions
4. Switch tools
5. Search related topics first

**Keep iterating until satisfied.**

## Common Research Patterns

### Quick Answer
Single focused WebSearch with specific query

### General Research
- 3-5 parallel WebSearch with different angles
- Iterate based on results

### Code Research
- WebSearch for overview
- mcp__exa__get_code_context_exa for examples
- Iterate for edge cases, error handling

### Academic Research
- WebSearch for overview
- mcp__exa__web_search_exa for papers
- Use **google-scholar** skill for citations
- Use **DOWNLOAD** snippet for PDFs
- Use **document-skills:pdf** to extract content

## Example: Iterative Search

**Round 1:**
```
WebSearch: "Python async programming"
→ Learned: asyncio is the main library
```

**Round 2:**
```
WebSearch: "Python asyncio tutorial 2025"
WebSearch: "asyncio vs threading when to use"
mcp__exa__get_code_context_exa: "Python asyncio examples"
→ Learned: Good basics, but need error handling
```

**Round 3:**
```
WebSearch: "asyncio error handling best practices"
WebSearch: "asyncio common mistakes"
mcp__exa__get_code_context_exa: "asyncio exception handling"
→ Complete understanding achieved
```

## Validation

Cross-reference findings:
- Check multiple sources
- Verify recent dates (2024-2025)
- Look for authoritative sources
- Test code examples
- Confirm consistency

## Quick Reference

**Default:** 3-5 parallel WebSearch with different angles

**For code:** Add mcp__exa__get_code_context_exa

**For papers:** Add mcp__exa__web_search_exa or use google-scholar skill

**For PDFs:** Use DOWNLOAD snippet

**When stuck:** Reformulate, try new terms, iterate

**Remember:** Keep going until you find complete answers
