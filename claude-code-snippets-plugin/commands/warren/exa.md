<exa>
## When to Use Exa vs WebSearch

**VERIFICATION_HASH:** `4d3588183474c059`


### Use EXA for:
- **Code Examples & Snippets** (100% confidence) - Exa returns production-ready code from real repositories with exceptional depth
- **Technical Documentation** (95% confidence) - Deep context with multiple implementation patterns
- **API/Library Usage** (100% confidence) - Real-world examples from GitHub, unmatched quality
- **Academic Research Papers** (85% confidence) - Direct links to papers (Nature, ArXiv), full-text access
- **Framework/Library Patterns** (100% confidence) - Production code from real projects
- **Performance Optimization** (95% confidence) - Advanced patterns with production examples

### Use WebSearch for:
- **Breaking News & Current Events** (95% confidence) - Better synthesis and comprehensive coverage
- **Regulatory/Legal Information** (90% confidence) - Systematic multi-jurisdictional coverage
- **Consumer Product Research** (90% confidence) - Product comparisons, reviews, shopping
- **Local Business Information** (85% confidence) - Restaurants, services, local recommendations
- **General Research Queries** (80% confidence) - Broad overviews and narrative synthesis

### Key Differences:
- **Cost:** Exa = $0.01/query (0.005 search + 0.005 content), WebSearch = free
- **Speed:** WebSearch = 2-4s, Exa = 5-6s (includes full content extraction)
- **Content:** Exa returns full article text, WebSearch returns summaries
- **Code Quality:** Exa is exceptional (10+ real examples), WebSearch is basic

### Hybrid Strategy (Best Results):
For complex technical queries requiring both breadth and depth:
1. Use **WebSearch** for conceptual overview and current landscape
2. Use **Exa** for deep code examples and implementation details
3. **ROI:** At $100/hr developer rate, Exa breaks even if it saves >36 seconds. Typical savings: 10-30 minutes for code queries

### Critical Discovery:
Exa **fails badly** on consumer/shopping queries (returns dealership tools instead of articles). It's optimized for technical/research content, not general consumer information.

### Tools Available:
- `mcp__exa__web_search_exa` - General web search (5 results default)
- `mcp__exa__get_code_context_exa` - **BEST for code** - Returns production code snippets with "dynamic" token allocation

### Decision Rule:
**If query contains code/API/library/framework names → Use Exa**
**If query is about news/shopping/local/general info → Use WebSearch**
**If complex technical topic → Use both in parallel**
</exa>