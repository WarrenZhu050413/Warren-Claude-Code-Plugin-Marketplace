# Real-Time Activity Streaming (SSE)

Patterns for showing intermediate agent activity (tool calls, thoughts, progress) in LLM applications.

---

## When to Use SSE

**Use when:**
- Long-running agent tasks
- Multi-step workflows
- Debugging/transparency features
- Users need visibility into agent progress

**Don't use when:**
- Simple request/response
- Latency matters more than visibility
- Single-turn completions

---

## Pattern: Early SSE Connection

Connect to SSE stream BEFORE making the API call to ensure no events are missed.

### Frontend

```typescript
// 1. Generate session_id BEFORE making API call
const sessionId = crypto.randomUUID().slice(0, 8);

// 2. Connect to SSE immediately
const eventSource = new EventSource(`/api/activity/${sessionId}`);
eventSource.onmessage = (e) => handleActivity(JSON.parse(e.data));
eventSource.onerror = (e) => console.error("SSE error", e);

// 3. Then make API call with the session_id
await fetch("/api/launch", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ session_id: sessionId, ...params }),
});
```

### Backend

```python
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

# Store queues per session
activity_queues: dict[str, asyncio.Queue] = {}

@router.get("/activity/{session_id}")
async def activity_stream(session_id: str):
    queue = asyncio.Queue()
    activity_queues[session_id] = queue

    async def generate():
        try:
            while True:
                event = await queue.get()
                if event.get("type") == "complete":
                    break
                yield {"data": json.dumps(event)}
        finally:
            # Cleanup when client disconnects
            activity_queues.pop(session_id, None)

    return EventSourceResponse(generate())

# Helper to emit events
async def emit(session_id: str, event_type: str, message: str, details: dict = None):
    if session_id in activity_queues:
        await activity_queues[session_id].put({
            "type": event_type,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        })
```

---

## Pattern: Phase-Based Activity UI

For multi-step workflows, group events into phases instead of flat timeline.

### Define Phases

```typescript
type Phase = 'init' | 'analysis' | 'building' | 'complete';

const PHASES: Record<Phase, { label: string; types: string[] }> = {
  init: {
    label: 'Initializing',
    types: ['session_start', 'setup']
  },
  analysis: {
    label: 'Analyzing',
    types: ['analyzing', 'analysis_complete']
  },
  building: {
    label: 'Building',
    types: ['builder_start', 'tool_use', 'builder_complete']
  },
  complete: {
    label: 'Complete',
    types: ['session_complete', 'session_error']
  },
};
```

### Status Icons

```typescript
function StatusIcon({ status }: { status: 'done' | 'active' | 'pending' | 'error' }) {
  switch (status) {
    case 'done': return <span className="text-green-400">✓</span>;
    case 'active': return <span className="text-amber-400 animate-pulse">●</span>;
    case 'error': return <span className="text-red-400">✗</span>;
    default: return <span className="text-gray-400">○</span>;
  }
}
```

Use text symbols (✓ ● ○ ✗) over emojis for professional look.

### UX Patterns

- Show progress bar with "Step N of M" - gives users context
- Expand/collapse phases - reduces visual noise
- "Show all X events" button per phase - progressive disclosure
- Click event to see full JSON details - enables debugging

---

## Event Types

Standard event types for LLM agent workflows:

```typescript
interface ActivityEvent {
  type: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

// Lifecycle events
type: "session_start"      // Session initialized
type: "session_complete"   // All work done
type: "session_error"      // Fatal error

// Analysis phase
type: "analyzing"          // Analysis in progress
type: "analysis_complete"  // Analysis results ready

// Builder phase
type: "builder_start"      // Individual builder starting
type: "tool_use"           // Tool being called
type: "builder_complete"   // Individual builder done
type: "builder_error"      // Builder failed
```

---

## Cleanup

Always handle SSE cleanup to prevent memory leaks:

### Frontend

```typescript
useEffect(() => {
  const eventSource = new EventSource(url);
  // ... handlers ...

  return () => {
    eventSource.close();
  };
}, [url]);
```

### Backend

```python
async def generate():
    try:
        while True:
            event = await queue.get()
            if event.get("type") == "complete":
                break
            yield {"data": json.dumps(event)}
    finally:
        # Always cleanup queue
        activity_queues.pop(session_id, None)
```

---

## Testing SSE

Use Playwright to capture and verify SSE events:

```python
# Capture network requests including SSE
network_logs = []
page.on("request", lambda req: network_logs.append(f"→ {req.method} {req.url}"))
page.on("response", lambda res: network_logs.append(f"← {res.status} {res.url}"))

# Verify SSE connection established
assert any("/activity/" in log for log in network_logs)
```
