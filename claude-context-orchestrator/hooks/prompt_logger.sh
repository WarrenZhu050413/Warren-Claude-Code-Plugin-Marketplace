#!/bin/bash
# Prompt Logger Hook - stores all prompts to ~/.claude/prompts/{project}/prompts.jsonl
# Captures comprehensive metadata for analysis

INPUT=$(cat)

# Extract fields from hook input
PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
CWD=$(echo "$INPUT" | jq -r '.cwd // ""')

# Skip if no prompt
[ -z "$PROMPT" ] && exit 0

# Extract project name from cwd (last directory component)
if [ -n "$CWD" ]; then
  PROJECT=$(basename "$CWD")
else
  PROJECT="_unknown"
fi

# Create output directory
OUTPUT_DIR="$HOME/.claude/prompts/$PROJECT"
mkdir -p "$OUTPUT_DIR"

# === Basic Metrics ===
CHAR_COUNT=${#PROMPT}
WORD_COUNT=$(echo "$PROMPT" | wc -w | tr -d ' ')
LINE_COUNT=$(echo "$PROMPT" | wc -l | tr -d ' ')

# === Content Detection ===
# Check for code blocks (```...```)
if echo "$PROMPT" | grep -q '```'; then
  HAS_CODE_BLOCK=true
else
  HAS_CODE_BLOCK=false
fi

# Check for URLs
if echo "$PROMPT" | grep -qE 'https?://'; then
  HAS_URL=true
else
  HAS_URL=false
fi

# Check for file paths (absolute paths /..., home ~/..., relative ./..., or paths with extensions)
if echo "$PROMPT" | grep -qE '(^|[[:space:]])(\/[a-zA-Z0-9_./-]+|~\/[a-zA-Z0-9_./-]+|\.\/[a-zA-Z0-9_./-]+)' ; then
  HAS_FILE_PATH=true
else
  HAS_FILE_PATH=false
fi

# Check if prompt is a slash command
if echo "$PROMPT" | grep -qE '^/[a-zA-Z]'; then
  IS_SLASH_COMMAND=true
  SLASH_COMMAND=$(echo "$PROMPT" | grep -oE '^/[a-zA-Z0-9_-]+' | head -1)
else
  IS_SLASH_COMMAND=false
  SLASH_COMMAND=""
fi

# Check for question marks (likely a question)
if echo "$PROMPT" | grep -q '?'; then
  IS_QUESTION=true
else
  IS_QUESTION=false
fi

# === Prompt Hash (for dedup/tracking) ===
PROMPT_HASH=$(echo "$PROMPT" | md5 -q 2>/dev/null || echo "$PROMPT" | md5sum | cut -d' ' -f1)

# === Git Context ===
if [ -n "$CWD" ] && [ -d "$CWD/.git" ] || git -C "$CWD" rev-parse --git-dir >/dev/null 2>&1; then
  GIT_BRANCH=$(git -C "$CWD" branch --show-current 2>/dev/null || echo "")
  GIT_REPO=$(basename "$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "")
else
  GIT_BRANCH=""
  GIT_REPO=""
fi

# === System Context ===
HOSTNAME=$(hostname -s 2>/dev/null || hostname)
USERNAME=$(whoami)

# === Time Context ===
TIMESTAMP=$(date -Iseconds)
DAY_OF_WEEK=$(date +%A)
HOUR=$(date +%H)
TIMEZONE=$(date +%Z)

# === Build JSON and append ===
jq -n --compact-output \
  --arg ts "$TIMESTAMP" \
  --arg tz "$TIMEZONE" \
  --arg dow "$DAY_OF_WEEK" \
  --argjson hour "$HOUR" \
  --arg sid "$SESSION_ID" \
  --arg prompt "$PROMPT" \
  --arg hash "$PROMPT_HASH" \
  --arg cwd "$CWD" \
  --arg project "$PROJECT" \
  --argjson chars "$CHAR_COUNT" \
  --argjson words "$WORD_COUNT" \
  --argjson lines "$LINE_COUNT" \
  --argjson has_code "$HAS_CODE_BLOCK" \
  --argjson has_url "$HAS_URL" \
  --argjson has_path "$HAS_FILE_PATH" \
  --argjson is_question "$IS_QUESTION" \
  --argjson is_slash "$IS_SLASH_COMMAND" \
  --arg slash_cmd "$SLASH_COMMAND" \
  --arg git_branch "$GIT_BRANCH" \
  --arg git_repo "$GIT_REPO" \
  --arg hostname "$HOSTNAME" \
  --arg username "$USERNAME" \
  '{
    timestamp: $ts,
    timezone: $tz,
    day_of_week: $dow,
    hour: $hour,
    session_id: $sid,
    prompt: $prompt,
    prompt_hash: $hash,
    cwd: $cwd,
    project: $project,
    char_count: $chars,
    word_count: $words,
    line_count: $lines,
    has_code_block: $has_code,
    has_url: $has_url,
    has_file_path: $has_path,
    is_question: $is_question,
    is_slash_command: $is_slash,
    slash_command: (if $slash_cmd == "" then null else $slash_cmd end),
    git_branch: (if $git_branch == "" then null else $git_branch end),
    git_repo: (if $git_repo == "" then null else $git_repo end),
    hostname: $hostname,
    username: $username
  }' \
  >> "$OUTPUT_DIR/prompts.jsonl"

exit 0
