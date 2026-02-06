---
name: Session Handoff
description: Template for summarizing session state and context for continuity between Claude Code sessions. Use when ending a session or handing off work.
---

# Session Handoff Protocol

When this snippet is triggered, create a session handoff summary with the following structure:

## Handoff Summary Template

```markdown
# Session Handoff

## Goal
[What the user is trying to accomplish—the high-level objective]

## Achieved
[Bullet list of concrete accomplishments this session]
- ...
- ...

## Next Steps
[What should be done next, in order of priority]
1. ...
2. ...

## Key Context
[Important details a new session needs to know]
- Files modified: ...
- Decisions made: ...
- Blockers encountered: ...

## Open Questions
[Unresolved questions or decisions pending user input]
- ...
```

## Instructions

1. **Goal**: Capture the user's intent, not just the literal request
2. **Achieved**: Be specific—include file paths, function names, commits
3. **Next Steps**: Actionable items, ordered by priority/dependency
4. **Key Context**: Details that would be lost without explicit documentation
5. **Open Questions**: Anything requiring user input before continuing

## Output Location

Save the handoff to one of:
- `./claude_files/handoff-YYYY-MM-DD.md` (project-specific)
- Print inline if user prefers

## Usage

Trigger with `HANDOFF` keyword at end of session or when switching contexts.
