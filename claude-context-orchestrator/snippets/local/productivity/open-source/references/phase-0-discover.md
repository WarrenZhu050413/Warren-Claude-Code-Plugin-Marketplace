# Phase 0: Discovery & Selection

**The hardest phase.** Many similar tools exist with vastly different quality. Wrong choice = wasted time + migration pain later.

## Quick Evaluation Heuristics

| Signal | Good | Warning |
|--------|------|---------|
| Last commit | < 3 months | > 1 year |
| Open issues response | Maintainers engage | Crickets |
| Contributors | 5+ active | Solo dev only |
| Stars trend | Growing | Flat/declining |
| Breaking changes | Rare, documented | Frequent, chaotic |
| Documentation | Examples + API | "See source" |

## 10-Minute Health Check

```bash
REPO="owner/repo"

# 1. Basic stats
gh repo view $REPO --json stargazersCount,forkCount,openIssues,pushedAt

# 2. Recent commits
gh api repos/$REPO/commits --jq '.[0:5] | .[].commit.message'

# 3. Issue response time
gh issue list -R $REPO --state all --limit 20 --json number,createdAt,closedAt

# 4. Release frequency
gh release list -R $REPO --limit 10

# 5. Contributor count
gh api repos/$REPO/contributors --jq 'length'
```

## Evaluation Checklist (Fast)

```
□ Search: "{tool} vs" to find alternatives
□ Check star-history.com for trajectory
□ Read 3-5 recent issues - are maintainers responsive?
□ Look for "awesome-{category}" lists
□ Check if used by companies/projects you trust
□ Verify license (MIT/Apache = safe, GPL = viral)
□ Test: Can you run basic example in < 10 min?
```

## Red Flags

- **Overclaiming**: "10x faster!" without benchmarks
- **Vaporware**: Features listed but not implemented
- **Bus factor = 1**: Single maintainer, no succession
- **Dependency hell**: Pulls half of npm for simple task
- **Stale deps**: Security vulnerabilities in dependencies

## Tech Stack Considerations

Before adopting:
- Is this language/ecosystem one I want to maintain?
- Do I have tooling (debugger, LSP) for this stack?
- Will this fit with existing tools or create friction?

## Comparative Analysis Template

```markdown
| Criteria | Tool A | Tool B | Tool C |
|----------|--------|--------|--------|
| Stars | | | |
| Last commit | | | |
| Contributors | | | |
| Documentation | | | |
| Install complexity | | | |
| License | | | |
```

## "Will this exist in 2 years?"

**Positive:**
- Corporate backing (not over-reliance)
- Multiple maintainers with commit access
- Growing star count
- Active community channels

**Risk:**
- Solo maintainer
- Company pivoting away
- Competitor with momentum
- Frequent breaking changes

## Search Commands

```bash
# Find alternatives
gh search repos "awesome-{category}" --sort stars

# Compare candidates on star-history.com

# Quick test each
brew install <tool> && tldr <tool> && <quick-test>
```
