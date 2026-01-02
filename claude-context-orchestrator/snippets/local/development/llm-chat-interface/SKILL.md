---
name: llm-chat-interface
description: Guide for building full-stack LLM applications with Warren's preferred tech stack. Use when building chat interfaces, LLM-powered apps, or any application using claude-agent-sdk. Covers tech stack (React + TypeScript + Vite + Tailwind frontend, FastAPI + uv backend), SDK usage patterns, structured logging, and Makefile conventions. Load references as needed - chat-interface.md for chat UI patterns, realtime-streaming.md for SSE/activity streaming, storage-patterns.md for backend persistence. Keywords - LLM app, claude-agent-sdk, FastAPI, React, chat interface.
---

## Tech Stack

### Frontend

- React + TypeScript + Vite
- **Tailwind CSS** preferred over plain CSS files
- **Text editor**: CodeMirror or TipTap recommended over plain textarea
- react-markdown for LLM response rendering
- vitest + @testing-library/react for testing

### Backend

- FastAPI + uv + sse-starlette (for real-time streaming)
- Use pyproject.toml (modern, consolidates config)
- CORS: Include all potential dev ports (5173, 5174, 3000) - Vite bounces to alternate ports
- pytest + pytest-asyncio for testing
- Ruff for linting

### LLM Integration

- claude-agent-sdk (Anthropic's official agent SDK)
- Simple HTTP request/response preferred over WebSocket streaming
- Client-side history management - frontend stores conversation, sends full history, backend stays stateless
- Models: haiku (speed), opus (quality)

---

## Makefile Conventions

Provide a Makefile with standardized commands:

```makefile
.PHONY: help serve kill restart test lint

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

serve:  ## Start both frontend and backend
	@echo "Starting backend..."
	cd backend && uv run uvicorn main:app --port 8000 &
	@echo "Starting frontend..."
	cd frontend && npm run dev &
	@echo "Services started. Use 'make kill' to stop."

kill:  ## Stop all services
	@pkill -f "uvicorn main:app" 2>/dev/null || true
	@pkill -f "vite" 2>/dev/null || true
	@echo "Services stopped."

restart: kill serve  ## Restart all services

test:  ## Run all tests
	cd backend && uv run pytest
	cd frontend && npm test

lint:  ## Run linters
	cd backend && uv run ruff check .
	cd frontend && npm run lint
```

**Key principles:**
- `make help` as the default/documented entry point - shows all available commands
- `make serve` starts full stack with single command
- `make kill` cleanly stops services - no orphan processes
- Disable hot reload during development - prevents test flakiness
- Health endpoints return service identification for debugging:

```python
@router.get("/health")
async def health():
    return {"status": "healthy", "service": "your-service-name"}
```

---

## SDK Gotchas (claude-agent-sdk)

### Authentication

- **Local auth works automatically** - no API key needed when running locally
- Don't use raw `anthropic.Anthropic()` - it requires explicit API key
- Import: `from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage`

### Two Usage Patterns

**Pattern 1: Text-Only Mode** (for simple completions)

```python
options = ClaudeAgentOptions(
    model="claude-sonnet-4-20250514",
    system_prompt=system_prompt,
    max_turns=1,
    allowed_tools=[],  # Disables tools, forces text output
)

result_text = ""
async for message in query(prompt=prompt, options=options):
    if isinstance(message, ResultMessage):
        result_text = message.result or ""
```

**Pattern 2: Agent Mode** (for file operations, testing, iteration)

```python
options = ClaudeAgentOptions(
    model="claude-sonnet-4-20250514",
    system_prompt=system_prompt,
    max_turns=None,  # Unlimited turns
    cwd=str(working_dir),
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Glob", "Grep", "Write", "Edit", "WebFetch", "Bash"],
    add_dirs=[str(working_dir)],
)
```

### Tool Behavior (CRITICAL)

- **Tools enabled = different output**: When tools are available, Claude may USE them rather than OUTPUT text
- Example: "Create index.html" → Claude writes the file via Write tool, `ResultMessage.result` is empty
- To get text output, use `allowed_tools=[]`
- To let Claude create files, enable tools + set `cwd` and `permission_mode`

### Message Type Checking

```python
from claude_agent_sdk import (
    AssistantMessage, ResultMessage,
    TextBlock, ToolUseBlock, ToolResultBlock
)

async for message in query(prompt=prompt, options=options):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, ToolUseBlock):
                tool_name = block.name
                tool_input = block.input or {}
            elif isinstance(block, TextBlock):
                text = block.text
    elif isinstance(message, ResultMessage):
        result = message.result
```

**NEVER use attribute-based type checking** like `block.type == 'tool_use'` - fails silently.

### General Gotchas

1. **Never break early** from async generator - causes cancel scope errors
2. **Consume entire generator** even if you have the result
3. **Empty result with tools** - If `ResultMessage.result` is empty, Claude likely completed an action via tools

---

## LLM Output Validation (Early Return Pattern)

When LLM output requires parsing, validate before proceeding:

```python
# Parse structured output from LLM
analysis = await self._analyze_codebase(session_id, path, question)

# Log raw output for debugging
logger.info(
    "Analysis complete",
    session_id=session_id,
    analysis_length=len(analysis),
    analysis_preview=analysis[:500] if analysis else "EMPTY",
)

# Parse and validate
variants = parse_xml_tags(analysis, "variant")

logger.info("Parsed results", num_variants=len(variants))

# CRITICAL: Early return on validation failure
if len(variants) == 0:
    logger.error("No variants found", analysis_output=analysis[:1000])
    await activity_stream.emit(session_id, "session_error",
        "Analysis failed to produce results. Check logs.")
    return LaunchResponse(session_id=session_id, variants=[],
        error="Analysis produced no results")

# Only proceed if validation passed
await activity_stream.emit(session_id, "analysis_complete",
    f"Found {len(variants)} variants")
```

**Key principle:** Emit error event, then return early. Never continue a workflow with empty/invalid LLM output.

---

## Parsing Structured LLM Output

When LLMs output structured formats (XML, JSON), use proper parsing libraries:

### XML Output - Use ElementTree

**DON'T** use regex for XML parsing:
```python
# Fragile - breaks on whitespace, special chars, nested tags
for match in re.finditer(r'<(\w+)>(.*?)</\1>', response):
    axis = match.group(1)
    content = match.group(2)
```

**DO** use xml.etree.ElementTree:
```python
import xml.etree.ElementTree as ET

# Extract XML block from LLM response (may have surrounding text)
xml_match = re.search(r'<root>(.*?)</root>', response, re.DOTALL)
if not xml_match:
    logger.warning("No XML block found")
    return []

try:
    root = ET.fromstring(f"<wrapper>{xml_match.group(1)}</wrapper>")

    for item in root.findall('item'):
        data = {
            "id": item.get('id'),  # Attributes
            "name": item.findtext('name'),  # Child element text
        }
        # Dynamic child parsing
        for child in item:
            if child.text:
                data[child.tag] = child.text

except ET.ParseError as e:
    logger.warning(f"XML parse error: {e}")
    # Fallback to basic regex if needed
```

**Benefits:**
- Proper tree traversal for nested structures
- Automatic whitespace handling
- Clear errors on malformed XML
- Dynamic element discovery (no hardcoded tag names)

### JSON Output

```python
import json

# Clean markdown code blocks if present
clean = response.strip()
if clean.startswith("```"):
    clean = re.sub(r"^```(?:json)?\n?", "", clean)
    clean = re.sub(r"\n?```$", "", clean)

try:
    data = json.loads(clean)
except json.JSONDecodeError as e:
    logger.error(f"JSON parse error: {e}", raw_response=response[:500])
    return None
```

**Key principle:** LLMs produce text, not data structures. Always parse with proper libraries, log raw output on failure.

---

## Parallel Agent Operations

When running multiple agents in parallel with `asyncio.gather`:

```python
results = await asyncio.gather(*build_tasks, return_exceptions=True)

successful = 0
failed = 0
for i, result in enumerate(results):
    if isinstance(result, Exception):
        failed += 1
        logger.error("Build failed", variant_id=variants[i].id,
            error=str(result), error_type=type(result).__name__)
        variants[i].status = "error"
        # CRITICAL: Emit to activity stream so errors are visible
        await activity_stream.emit(session_id, "builder_error",
            f"[{variants[i].id}] Build failed: {str(result)[:200]}",
            details={"error": str(result)})
    else:
        successful += 1
        variants[i] = result

logger.info("All builds completed", successful=successful, failed=failed)
```

**Key principle:** Errors in `return_exceptions=True` are silent by default. Emit them to SSE stream for visibility.

---

## Structured Logging

Use structlog for LLM pipelines:

```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer() if sys.stdout.isatty()
            else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()
```

**What to log:**

```python
# Before LLM call
logger.info("Starting analysis", session_id=session_id, question=question[:100])

# After LLM call
logger.info("Analysis complete", result_length=len(result), has_expected_tags="<variant" in result)

# After parsing
logger.info("Parsed results", num_variants=len(variants))

# After parallel operations
logger.info("All builds completed", successful=successful_count, failed=failed_count)

# On errors
logger.error("Build failed", variant_id=variant.id, error=str(e), error_type=type(e).__name__)
```

**Always include context IDs** (session_id, variant_id, etc.) for log correlation.

---

## Prompt Management

Store prompts as composable .txt files:

```
prompts/
├── system.txt          # Base system prompt
├── format.txt          # Output format instructions
├── examples.txt        # Few-shot examples
└── shared/
    └── json-output.txt # Reusable JSON formatting
```

**Principles:**
- Load and compose at request time, not startup - allows changes without restart
- Wrap chunks in XML tags when composing: `<system>...</system>`, `<format>...</format>`
- Support template variables: `{user_input}`, `{history}`
- Name files by API route where used

---

## Testing Philosophy

- Test LLM apps end-to-end, not just frontend
- Verify responses are correct, not just that requests succeed
- Save logs to ./logs folder for debugging test failures
- For agent testing: choose 2-3 typical scenarios initially (tokens cost money)
- Exclude long-running agent tests from normal pytest runs
- Use Playwright for E2E with network/console capture

---

## Sample .gitignore

```gitignore
# Dependencies
node_modules/
.pnpm-store/

# Build output
dist/
build/
.vite/

# IDE
.idea/
*.swp
.vscode/

# Environment (NEVER commit API keys)
.env
.env.local
.anthropic_key
*.key

# Logs
logs/
*.log

# Testing
coverage/
.pytest_cache/
__pycache__/

# Cache
.eslintcache
.ruff_cache/

# Python
.venv/
venv/
.uv/

# Generated
*.tmp
.annotations/
```

---

## References

Load these as needed:

- **references/chat-interface.md** - Message handling, input behavior, UI/UX patterns for chat applications
- **references/realtime-streaming.md** - SSE patterns, early connection, phase-based activity UI
- **references/storage-patterns.md** - File-based vs SQL, JSONL for logs, JSON for config
