#!/bin/bash
# gh-status-dashboard: Generate comprehensive GitHub status overview

# What this script does
# =====================
# Creates a dashboard showing all your relevant GitHub activity:
# - Pull requests assigned to you (by state)
# - Issues assigned to you (by state)
# - Pull requests awaiting your review
# - Recently created/updated items
#
# Helps you quickly understand your current workload across all repos

# Usage
# =====
# ./gh-status-dashboard.sh [OPTIONS]
#
# Options:
#   --limit N        Show top N items (default: 10)
#   --json           Output as JSON
#   --no-color       Disable colored output
#
# Examples:
#   ./gh-status-dashboard.sh                  # Default dashboard
#   ./gh-status-dashboard.sh --limit 5        # Show top 5 items
#   ./gh-status-dashboard.sh --json           # JSON output for piping

# Dependencies
# ============
# - gh CLI (v2.0+)
# - jq (optional, for pretty JSON output)

set -e

# Configuration
LIMIT=10
OUTPUT_FORMAT="text"
USE_COLOR=true

# ANSI color codes
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --limit)
      LIMIT=$2
      shift 2
      ;;
    --json)
      OUTPUT_FORMAT="json"
      shift
      ;;
    --no-color)
      USE_COLOR=false
      shift
      ;;
    -h|--help)
      cat <<'HELP'
GitHub CLI Status Dashboard

Usage: gh-status-dashboard.sh [OPTIONS]

Options:
  --limit N       Show top N items (default: 10)
  --json          Output as JSON instead of text
  --no-color      Disable colored output
  -h, --help      Show this help message

Examples:
  ./gh-status-dashboard.sh              # Show your GitHub status
  ./gh-status-dashboard.sh --limit 5    # Show top 5 items
  ./gh-status-dashboard.sh --json       # JSON format for scripting
HELP
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Helper: disable colors if requested
if [ "$USE_COLOR" = false ]; then
  BOLD=''
  GREEN=''
  BLUE=''
  YELLOW=''
  RED=''
  NC=''
fi

# Helper: format output
print_header() {
  echo ""
  echo -e "${BOLD}${BLUE}=== $1 ===${NC}"
}

print_item() {
  local number=$1
  local title=$2
  local state=$3

  if [ "$state" = "OPEN" ]; then
    state_color=$GREEN
  elif [ "$state" = "DRAFT" ]; then
    state_color=$YELLOW
  else
    state_color=$RED
  fi

  echo -e "${state_color}#$number${NC} $title"
}

# Get data
if [ "$OUTPUT_FORMAT" = "json" ]; then
  # JSON output mode
  echo "{"

  echo '"your_prs": '
  gh pr list --assignee=@me --json number,title,state | jq . || echo "[]"
  echo ","

  echo '"your_issues": '
  gh issue list --assignee=@me --json number,title,state | jq . || echo "[]"
  echo ","

  echo '"review_requested": '
  gh pr list --search "is:open review:requested" --json number,title,author | jq . || echo "[]"

  echo "}"
else
  # Text output mode
  echo -e "${BOLD}GitHub Status Dashboard${NC}"
  echo "Generated: $(date)"

  # Your PRs
  print_header "Your Pull Requests"
  gh pr list --assignee=@me --limit=$LIMIT --json number,title,state \
    --jq '.[] | "\(.number) \(.title) (\(.state))"' || echo "None"

  # Your Issues
  print_header "Your Issues"
  gh issue list --assignee=@me --limit=$LIMIT --json number,title,state \
    --jq '.[] | "\(.number) \(.title) (\(.state))"' || echo "None"

  # Review Requested
  print_header "PRs Awaiting Your Review"
  gh pr list --search "is:open review:requested" --limit=$LIMIT \
    --json number,title,author \
    --jq '.[] | "\(.number) \(.title) (by \(.author.login))"' || echo "None"

  # Recently Updated
  print_header "Recently Updated (Last 7 Days)"
  gh pr list --search "is:open updated:>=7.days.ago" --limit=$LIMIT \
    --json number,title,updatedAt \
    --jq '.[] | "\(.number) \(.title) (updated: \(.updatedAt))"' || echo "None"

  echo ""
fi
