# Storage Patterns

Backend storage decisions for LLM applications.

---

## Philosophy

Start with simple file-based storage over SQL databases during prototyping:

- Easier to debug - open in editor, use `tail -f`, `jq`
- Git-friendly - meaningful diffs
- No setup - no DB server, migrations, ORM
- Portable - copy files to share state

Migrate to SQLite/Postgres when you need:
- Cross-record queries
- Concurrent writes
- Entity relationships

---

## File Format Selection

### JSONL (JSON Lines)

Best for: **Append-only logs** (conversations, events, audit trails)

```
{"timestamp": "2024-01-15T10:30:00Z", "event": "message_sent", "user_id": "123"}
{"timestamp": "2024-01-15T10:30:05Z", "event": "response_received", "tokens": 450}
```

**Benefits:**
- One JSON object per line
- Can `tail -f` to watch in real-time
- Append without reading entire file
- Easy to grep/filter

**Reading:**
```python
def read_jsonl(path: Path) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

def append_jsonl(path: Path, record: dict):
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")
```

### JSON

Best for: **Configuration and state snapshots**

```json
{
  "model": "claude-sonnet-4",
  "temperature": 0.7,
  "system_prompt": "You are a helpful assistant..."
}
```

**Benefits:**
- Human-readable
- Git-friendly diffs
- Standard format

**Reading:**
```python
def read_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)

def write_json(path: Path, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
```

### Plain Text (.txt)

Best for: **Prompts and templates**

```
prompts/
├── system.txt
├── format.txt
└── shared/
    └── json-output.txt
```

**Benefits:**
- Easy to edit
- No parsing overhead
- Clear git diffs

---

## Directory Structure

```
data/
├── sessions/           # Per-session state (JSON)
│   ├── abc123.json
│   └── def456.json
├── logs/               # Event logs (JSONL)
│   ├── events.jsonl
│   └── errors.jsonl
├── config/             # App configuration (JSON)
│   └── settings.json
└── prompts/            # Prompt templates (TXT)
    ├── system.txt
    └── format.txt
```

---

## When to Migrate to SQL

**Stay with files when:**
- Prototyping / MVP
- Single-user or low concurrency
- Data is naturally hierarchical (sessions, conversations)
- Need to manually inspect/edit data

**Migrate to SQL when:**
- Need queries across many records ("find all sessions with errors")
- Multiple processes writing simultaneously
- Need relationships between entities
- Data grows beyond what fits in memory

---

## Persistence Patterns

### Explicit Save (Recommended for Prototyping)

Save on every user action - simpler to debug:

```python
@router.post("/settings")
async def update_settings(settings: Settings):
    write_json(SETTINGS_PATH, settings.dict())
    return {"status": "saved"}
```

### Auto-save with Debounce (Optional)

For frequent updates, debounce to reduce I/O:

```typescript
const debouncedSave = useMemo(
  () => debounce((data) => saveToStorage(data), 1000),
  []
);
```

---

## Common Gotchas

1. **File locking** - Use atomic writes for concurrent access:
   ```python
   import tempfile
   import shutil

   def atomic_write(path: Path, data: str):
       with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=path.parent) as f:
           f.write(data)
           temp_path = f.name
       shutil.move(temp_path, path)
   ```

2. **Large files** - Stream JSONL instead of loading all:
   ```python
   def stream_jsonl(path: Path):
       with open(path) as f:
           for line in f:
               if line.strip():
                   yield json.loads(line)
   ```

3. **Missing directories** - Create on write:
   ```python
   path.parent.mkdir(parents=True, exist_ok=True)
   ```
