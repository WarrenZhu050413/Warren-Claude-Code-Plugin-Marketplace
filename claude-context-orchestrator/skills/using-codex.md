# Codex CLI

Automate code, bash scripting, web research with clean output.

## Install

```bash
npm install -g @openai/codex
codex --version
```

## Config

`~/.codex/config.toml`:
```toml
model = "gpt-5-codex"
model_reasoning_effort = "high"
approval_policy = "never"
sandbox_mode = "workspace-write"
web_search = true
```

## Commands

**Interactive:** Real-time development
```bash
codex "Create a Python REST API"
```

**Exec:** Automation
```bash
codex exec "Task" --full-auto
```

---

## Bash Scripting

### Basic
```bash
#!/bin/bash
set -euo pipefail

cd /tmp/project
git init && git config user.email "bot@example.com" && git config user.name "Bot"

codex exec "Your task" --full-auto
```

### With Clean Output
```bash
codex exec "Your task" --full-auto --output-last-message /tmp/result.txt
cat /tmp/result.txt
```

### Idempotent
```bash
#!/bin/bash
set -euo pipefail

log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }
ensure_tool() { command -v "$1" >/dev/null || { log "install $1"; exit 1; }; }

case "${1:-help}" in
  bootstrap)
    ensure_tool jq
    [[ -f .ready ]] || { ./setup.sh && touch .ready; }
    ;;
  ci)
    for step in lint test build; do
      log "running $step"
      ./scripts/$step.sh || exit 1
    done
    ;;
  watch)
    ensure_tool entr
    find src -type f | entr -r bash -lc './scripts/test.sh'
    ;;
  *)
    printf 'usage: %s {bootstrap|ci|watch}\n' "$0" >&2; exit 64
    ;;
esac
```

### Git Checkpoint
```bash
#!/bin/bash
set -euo pipefail

git add . && git commit -m "Before Codex" || true

codex exec "Run tests and fix failures" --full-auto || {
  git reset --hard HEAD~1
  exit 1
}

git add . && git commit -m "Codex: Fixed" || true
```

### Batch
```bash
#!/bin/bash
for project in project1 project2 project3; do
  (
    cd "$project"
    git init && git config user.email "bot@example.com" && git config user.name "Bot" || true

    if codex exec "Update dependencies" --full-auto; then
      git add . && git commit -m "Updated" --allow-empty || true
      echo "✓ $project"
    else
      git reset --hard HEAD~1
      echo "✗ $project"
    fi
  )
done
```

---

## Web Search

Enable with `-c web_search=true`.

### Research with JSON
```bash
#!/bin/bash
cd /tmp/research
git init && git config user.email "bot@example.com"

task="Find top 3 bash patterns. Return ONLY valid JSON with: pattern, description, code_example."

codex exec "$task" \
  -c web_search=true \
  --full-auto \
  --output-last-message /tmp/result.json

cat /tmp/result.json | jq .
```

### View Searches
```bash
codex exec "Research bash best practices" \
  -c web_search=true \
  --full-auto \
  --json 2>/dev/null | \
  jq -r 'select(.type=="web_search") | .item.query'
```

### View Reasoning
```bash
codex exec "Research X" \
  -c web_search=true \
  --full-auto \
  --json 2>/dev/null | \
  jq -r 'select(.type=="reasoning") | .item.text'
```

---

## Output Control

**`--output-last-message FILE`** - Writes final answer to FILE only.

```bash
codex exec "Task" --full-auto --output-last-message /tmp/answer.txt
cat /tmp/answer.txt
```

Result:
- FILE: Clean plaintext answer
- STDOUT: 5 lines metadata
- STDERR: Empty

**`--json`** - JSONL events: thread.started, turn.started, reasoning, web_search, agent_message, turn.completed.

```bash
codex exec "Task" --full-auto --json 2>/dev/null | jq '.type' | sort | uniq -c
```

**Suppress console:** Redirect to /dev/null
```bash
codex exec "Task" --full-auto --output-last-message /tmp/answer.txt >/dev/null 2>&1
cat /tmp/answer.txt
```

**Save audit log + clean output:**
```bash
codex exec "Task" --full-auto \
  --output-last-message /tmp/answer.txt \
  --json >/tmp/audit.jsonl 2>&1
cat /tmp/answer.txt
```

---

## Python

### Simple
```python
import subprocess

result = subprocess.run(
    ['codex', 'exec', 'Create test module', '--full-auto'],
    cwd='/tmp/project',
    capture_output=True,
    text=True
)

print(result.stdout)
```

### Wrapper
```python
from dataclasses import dataclass
from typing import Optional
import subprocess
import os

@dataclass
class CodexResult:
    returncode: int
    stdout: str
    stderr: str
    task: str

    @property
    def success(self) -> bool:
        return self.returncode == 0

class CodexCLI:
    def __init__(self, model="gpt-5-codex", web_search=False):
        self.model = model
        self.web_search = web_search

    def execute(self, task: str, cwd: Optional[str] = None) -> CodexResult:
        output_file = f"/tmp/codex-{os.urandom(4).hex()}.txt"

        cmd = [
            'codex', 'exec', task,
            '--full-auto',
            '-m', self.model,
            '--output-last-message', output_file
        ]

        if self.web_search:
            cmd.extend(['-c', 'web_search=true'])

        result = subprocess.run(
            cmd,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True
        )

        try:
            with open(output_file) as f:
                output = f.read()
            os.unlink(output_file)
        except:
            output = result.stdout

        return CodexResult(
            returncode=result.returncode,
            stdout=output,
            stderr=result.stderr,
            task=task
        )

# Usage
codex = CodexCLI(web_search=True)
result = codex.execute("Research X")
print(result.stdout)
```

---

## Flags

| Flag | Purpose |
|------|---------|
| `--full-auto` | Auto-approve, workspace-write sandbox |
| `-c web_search=true` | Enable web search |
| `--output-last-message FILE` | Write final answer to FILE |
| `--json` | Stream JSONL events |
| `-m, --model` | gpt-5 (fast), gpt-5-codex (code), o3 (powerful) |
| `-C, --cd` | Working directory |

---

## Patterns

**Research + JSON**
```bash
codex exec "Find X. Return JSON with: pattern, description, code." \
  -c web_search=true --full-auto --output-last-message /tmp/result.json
```

**Batch docs**
```bash
for module in auth utils data; do
  codex exec "Generate API docs for $module.py" \
    --full-auto --output-last-message "/tmp/${module}_docs.md"
done
```

**Research → Generate → Commit**
```bash
codex exec "Research Python testing best practices 2025" \
  -c web_search=true --full-auto --output-last-message /tmp/research.txt

codex exec "Using this research, generate test suite for module.py" --full-auto

git add . && git commit -m "Generated tests from latest best practices"
```

---

## Performance

| Task | Time | Success |
|------|------|---------|
| Simple | 30-60s | 99%+ |
| Web search | 60-120s | 95%+ |
| Complex | 120+s | 90%+ |

**Models:**
- `gpt-5`: Fast, cheap
- `gpt-5-codex`: Default, code-optimized
- `o3`: Powerful, slow

---

## Security

**Safe:**
- `workspace-write` sandbox (default)
- Git checkpoints before Codex
- Validate generated code

**Avoid:**
- `danger-full-access` without external sandboxing
- Running without git checkpoints
- Web search on untrusted domains

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `codex not found` | `npm install -g @openai/codex` |
| Not in trusted directory | `git init` in working directory |
| Web search returns nothing | Rephrase as task ("Find X"), not question |
| Too much output | Use `--output-last-message FILE` |
| Can't parse output | Use `--json` with `jq` |
| Auth failed | `codex login` or set `OPENAI_API_KEY` |

---

## Quick Reference

```bash
# Basic
codex exec "Task" --full-auto

# Web search
codex exec "Research X" -c web_search=true --full-auto

# Clean output
codex exec "Task" --full-auto --output-last-message /tmp/out.txt

# View searches
codex exec "Task" -c web_search=true --full-auto --json 2>/dev/null | \
  jq -r 'select(.type=="web_search") | .item.query'

# Token usage
codex exec "Task" --full-auto --json 2>/dev/null | \
  jq 'select(.type=="turn.completed") | .usage'

# Different model
codex exec "Task" -m o3 --full-auto

# Specific directory
codex exec "Task" -C /path/to/project --full-auto
```
