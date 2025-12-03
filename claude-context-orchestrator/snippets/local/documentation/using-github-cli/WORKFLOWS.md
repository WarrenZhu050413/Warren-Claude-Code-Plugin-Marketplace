# GitHub CLI Workflows

Reusable automation scripts contributed from real problem-solving sessions.

## Index

### Performance & Status

- **gh-status-dashboard.sh** - Generate comprehensive GitHub status dashboard (PRs, issues, notifications across all repos)

### Bulk Operations

- **gh-bulk-label.sh** - Apply/remove labels from multiple issues/PRs matching criteria
- **gh-bulk-close.sh** - Close multiple issues/PRs matching search criteria

### Code Review

- **gh-review-queue.sh** - Show PRs waiting for your review, grouped by repo
- **gh-review-autoapprove.sh** - Auto-approve PRs matching criteria (use carefully!)

### Release & Deployment

- **gh-release-create.sh** - Create release with automatic changelog from commits
- **gh-release-publish.sh** - Publish draft releases across multiple repos

### Data Export

- **gh-export-issues.sh** - Export issues to CSV/JSON with full details
- **gh-export-prs.sh** - Export PRs to CSV with review stats

### Integration

- **gh-slack-notify.sh** - Send GitHub notifications to Slack
- **gh-discord-notify.sh** - Send GitHub notifications to Discord

---

## How to Contribute

When you use `gh` for a workflow in a session:

1. **Identify reusable pattern**: Is this workflow useful for future sessions?
2. **Create script** in this directory:
   ```bash
   cat > workflows/gh-descriptive-name.sh << 'EOF'
   #!/bin/bash
   # gh-descriptive-name: What this does
   # Purpose: Detailed explanation
   # Usage: ./gh-descriptive-name.sh [args]
   # Example: ./gh-descriptive-name.sh repo:anthropic/claude-code is:open

   # Your script here
   EOF
   chmod +x workflows/gh-descriptive-name.sh
   ```

3. **Document at top** (use comment block):
   - What it does (one line summary)
   - Purpose (detailed explanation)
   - Usage (with examples)
   - Dependencies (if any)

4. **Add to this index** with description and link

5. **Test locally** before committing

---

## Using Workflows

Copy to your PATH:
```bash
cp ~/.claude/skills/using-github-cli/workflows/gh-*.sh ~/.local/bin/
chmod +x ~/.local/bin/gh-*.sh
```

Or run directly:
```bash
bash ~/.claude/skills/using-github-cli/workflows/gh-status-dashboard.sh
```

---

## Workflow Template

```bash
#!/bin/bash
# gh-short-name: Brief description

# What this script does
# =====================
# Long description of purpose and use case

# Usage
# =====
# ./gh-short-name.sh [--flag] [args]
#
# Examples:
# ./gh-short-name.sh --help
# ./gh-short-name.sh "search-criteria"

# Dependencies
# ============
# - gh CLI (v2.0+)
# - jq (for JSON processing) [optional]

set -e

# Function: print help
help() {
  cat <<'HELP'
Usage: gh-short-name.sh [OPTIONS] [ARGS]

Options:
  -h, --help    Show this help
  --limit N     Limit results (default: 30)
  --repo REPO   Specify repo (default: current)

Examples:
  gh-short-name.sh --limit 50
  gh-short-name.sh --repo owner/repo

HELP
}

# Parse arguments
LIMIT=30
REPO=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      help
      exit 0
      ;;
    --limit)
      LIMIT=$2
      shift 2
      ;;
    --repo)
      REPO="-R $2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Main logic here
echo "Running workflow..."
```

---

## Last Updated

Create timestamp and contributor info when workflows are added.

---

**Contributing a workflow?** Add it here, document it well, and future sessions will benefit!
