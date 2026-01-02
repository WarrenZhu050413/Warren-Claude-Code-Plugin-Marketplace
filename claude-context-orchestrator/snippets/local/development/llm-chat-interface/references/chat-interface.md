# Chat Interface Patterns

UI/UX patterns specific to LLM chat applications.

---

## User Configuration

**FR-2.1** Expose all settings in a settings UI panel - avoids hidden behaviors
**FR-2.2** Model type, system prompts, and input context should be viewable and configurable - increases customization and helps user's mental model
**FR-2.6** Theme selection (light/dark/system) - standard accessibility
**FR-2.7** Persist settings across browser sessions via localStorage

---

## Message Handling

**FR-3.1** Implement message queuing - users can submit while LLM is processing
**FR-3.2** Show messages immediately with "pending" status - provides instant feedback
**FR-3.3** Process queue FIFO - predictable ordering
**FR-3.4** Support cancelling in-flight requests but include partial response in context
**FR-3.5** Show "cancelled" status (not error) - cancelled is intentional

---

## Input Behavior

**FR-4.1** Keep input field always enabled (non-blocking) - disabled inputs feel unresponsive
**FR-4.2** Allow typing while LLM is processing - users can compose during response
**FR-4.3** Keep submit button always clickable (adds to queue if processing)
**FR-4.4** Button text indicates state ("Send" vs "Queued")
**FR-4.5** Use text editor with multi-line support - plain textarea lacks editing ergonomics

---

## Message Display

**FR-5.1** Render LLM responses as markdown (react-markdown) - models produce markdown naturally
**FR-5.2** User messages may render as plain text - simpler, users rarely use markdown
**FR-5.4** Show visual state indicators per message:

| State | Display |
|-------|---------|
| Pending | Dimmed, waiting indicator |
| Processing | Highlighted, animated indicator |
| Complete | Normal display |
| Error | Error styling with message |
| Cancelled | Distinct cancelled styling |

---

## API Communication

**FR-6.1** Use simple HTTP POST request/response - easier than WebSocket to implement/debug
**FR-6.2** Client-side history management - frontend stores messages in React state, sends full history with each request, backend stays stateless
**FR-6.3** Persist history to localStorage - survives page refresh
**FR-6.4** Show loading indicator during request
**FR-6.5** Truncate old messages when history exceeds token limit - frontend's responsibility

---

## Error Handling

**FR-7.1** Show user-friendly network error messages - raw errors confuse users
**FR-7.2** Handle API errors (5xx) with "try again later" message
**FR-7.3** Handle rate limits (429) with specific message
**FR-7.4** Preserve user's input on errors - losing a long prompt is frustrating
**FR-7.5** Offer retry for failed messages - one-click recovery

---

## UI/UX Patterns

**FR-8.1** Use Tailwind CSS - consistency with stack
**FR-8.2** Load frontend-design skill if available - elevates visual quality
**FR-8.4** Keyboard shortcuts:
- `Enter` to send
- `Shift+Enter` for newline
- `Escape` to cancel

**FR-8.5** Show loading states during async operations
**FR-8.6** On new messages: indicate arrival but stay at current scroll position (with option to disable) - auto-scrolling interrupts reading
**FR-8.7** Display total API cost when available (with option to disable)

---

## Checklist

Verification checklist for LLM chat interfaces:

- [ ] Tailwind CSS for styling
- [ ] Rich text input (CodeMirror/TipTap or multiline textarea)
- [ ] Frontend design skill loaded (if available)
- [ ] .gitignore from template
- [ ] Settings panel with model/prompt options exposed
- [ ] Client-side history (React state + localStorage)
- [ ] Simple HTTP POST for LLM requests (stateless backend)
- [ ] Message queuing (submit while processing)
- [ ] Non-blocking input (always enabled)
- [ ] Markdown rendering for LLM responses
- [ ] Visual message states (pending/processing/complete/error/cancelled)
- [ ] Cancel support for in-flight requests
- [ ] User-friendly error messages
- [ ] Keyboard shortcuts (Enter/Escape)
- [ ] Mobile responsive
- [ ] Makefile with serve/kill/restart/help
- [ ] Prompts as composable .txt files in `prompts/` directory
- [ ] E2E Playwright test for full user journey
