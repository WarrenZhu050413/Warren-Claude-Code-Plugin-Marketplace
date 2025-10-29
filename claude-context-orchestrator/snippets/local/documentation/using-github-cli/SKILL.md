---
name: Using GitHub CLI (gh)
description: Master GitHub CLI workflow for issues, repos, search, and APIs. Use when creating/reading GitHub issues, searching repos, querying GitHub data, or automating GitHub tasks. Focus: gotchas, key workflows with "look at past examples" pattern, practical APIs.
---

# Using GitHub CLI (gh)

Clear, focused guide to GitHub CLI gotchas and key workflows for issues, repos, search, and APIs.

---

## 🚨 Critical Gotchas

### 1. Search with Exclusions Needs `--`
```bash
# ❌ WRONG
gh search issues "my-query -label:bug"

# ✅ RIGHT
gh search issues -- "my-query -label:bug"
```
Shell interprets `-label:bug` as a flag without `--`.

### 2. JSON Output Requires Field Names
```bash
# ❌ WRONG
gh pr list --json

# ✅ RIGHT
gh pr list --json number,title,author
```
API must know which fields to fetch.

### 3. Repo Context Defaults to Current Directory
```bash
# ❌ WRONG - fails if not in repo
gh pr list

# ✅ RIGHT
gh pr list -R owner/repo
GH_REPO=owner/repo gh pr list
```

### 4. Token Scope Issues (Silent Failures)
Check your token scopes before automating:
```bash
gh auth status
# Needed: repo, read:org, gist, workflow, admin:public_key
```

### 5. API Placeholder Variables Don't Expand Env Vars
```bash
# ❌ WRONG
gh api /repos/$OWNER/$REPO/issues

# ✅ RIGHT - use gh placeholders
gh api /repos/{owner}/{repo}/issues
```

---

## 4 Key Workflows

### Workflow 1: CREATE ISSUE

**ALWAYS: Look at past examples in the repo first**

```bash
# Step 1: Search for similar issues (avoid duplicates)
gh search issues --repo anthropics/claude-code "your search terms" --limit 10

# Step 2: View format of 2-3 recent similar issues
gh issue view --repo anthropics/claude-code [issue-number]

# Step 3: Identify the pattern (sections, detail level, tone)
# Common patterns:
# - Feature requests: Problem → Proposed Solution → Example Usage
# - Bug reports: Description → Steps to Reproduce → Expected vs Actual
```

**Create Issue Using Learned Format**

```bash
gh issue create --repo anthropics/claude-code \
  --title "Clear, searchable title" \
  --body "$(cat <<'EOF'
## Problem / Description
[What you're trying to do or what's wrong]

## Example / Steps to Reproduce
[How to see the issue or use the feature]

## Additional Context
[Why this matters, related issues, etc.]
EOF
)"
```

**Key Points:**
- Search for duplicates BEFORE creating
- Look at 2-3 recent issues to understand format
- Match the repository's style, not a fixed template
- Include concrete examples, not vague descriptions
- Check available labels: `gh label list --repo anthropics/claude-code`

---

### Workflow 2: READ ISSUE

**Get full issue with comments**

```bash
# View issue with all comments
gh issue view --repo anthropics/claude-code [number] --comments

# Extract specific information
gh issue view --repo anthropics/claude-code [number] \
  --json title,body,state,author,labels

# List issues assigned to you
gh issue list --assignee=@me --json number,title,state
```

**Common Queries**

```bash
# Issues waiting on you
gh issue list --search 'is:open assignee:@me'

# Issues with specific label
gh issue list --search 'is:open label:bug' --limit 20

# Recent issues (last 7 days)
gh issue list --search 'is:open updated:>=7.days.ago' --limit 10
```

---

### Workflow 3: READ REPOSITORY INFO

**Get repo details**

```bash
# View repo metadata
gh repo view --repo anthropics/claude-code --json name,description,url

# Check recent issues/PRs
gh issue list --repo anthropics/claude-code --limit 10
gh pr list --repo anthropics/claude-code --limit 10

# View available labels
gh label list --repo anthropics/claude-code
```

**Find Repo Context**

```bash
# Get owner and repo from current directory
gh repo view --json owner,nameWithOwner

# Use in other commands
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
gh issue list --repo $REPO
```

---

### Workflow 4: SEARCH

**Search syntax (remember the `--`)**

```bash
# Search issues with filters
gh search issues -- "your query -label:wontfix" --limit 15

# Search specific repo with multiple criteria
gh search issues --repo anthropics/claude-code "is:open label:bug type:issue"

# Search code
gh search code "function main" --language python --limit 10

# Search repos
gh search repos "claude-code" --owner anthropics --limit 5
```

**Advanced Filters**

```bash
# Issues: is:open, is:closed, label:bug, author:username, assignee:@me
# PRs: is:open, is:draft, review:approved, review:requested
# More: https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests

# Examples
gh search issues -- "is:open label:enhancement -label:duplicate"
gh search issues -- "is:closed sort:updated-desc"
gh pr list --search 'is:open review:requested'
```

---

## Key API Commands

### Direct API Access (when `gh` commands aren't enough)

```bash
# Get user info
gh api user | jq '.login, .name'

# List issues with pagination
gh api --paginate /repos/{owner}/{repo}/issues | jq '.[] | .number'

# GraphQL query
gh api graphql -f query='{ viewer { name login } }'

# Create something
gh api -f title="New Issue" -f body="Description" /repos/{owner}/{repo}/issues
```

### Output Formatting

```bash
# JSON for scripting
gh issue list --json number,title,state

# Extract fields with jq
gh pr list --json author,title --jq '.[].author.login'

# Custom formatting (if needed)
gh pr list --json number,title \
  --template '{{range .}}#{{.number}}: {{.title}}{{"\n"}}{{end}}'
```

---

## When Things Go Wrong

```bash
# Check authentication
gh auth status

# Token scope issues
# ❌ Operations fail silently if scopes are missing
gh auth status  # Shows current scopes
# If missing, run: gh auth login --scopes repo,gist,workflow

# Enable debug output
GH_DEBUG=1 gh issue list

# Repository not found?
# Use -R flag: gh issue list -R owner/repo
```

---

## Contributing New Workflows

When you discover a useful automation pattern:

1. Save it to `~/.claude/skills/using-github-cli/workflows/gh-pattern-name.sh`
2. Add documentation comment at top
3. Update `WORKFLOWS.md` with description
4. Next session will have access to it!

See `WORKFLOWS.md` and `workflows/gh-status-dashboard.sh` for examples.
