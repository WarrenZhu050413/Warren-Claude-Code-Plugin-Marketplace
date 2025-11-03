# GmailLM CLI Enhancement Plan: Complete Implementation

**Status**: ✅ Plan Created & Documented
**Date**: 2025-10-30
**Focus**: Claude-Powered Email Agent with Preview-First Workflow

---

## Executive Summary

This plan outlines a comprehensive enhancement to gmaillm (Gmail CLI) to create an intelligent email management system combining:
1. **Preview-First Workflow**: Safe, transparent email operations
2. **Claude AI Integration**: Intelligent email analysis and automation
3. **Style-Based Composition**: Consistent, appropriate email tone
4. **Workflow Automation**: Autonomous yet controlled email processing

---

## Architecture

### Current State
- ✅ Functional Gmail CLI with send, read, list commands
- ✅ Email groups and styles system
- ✅ Workflow infrastructure (tokens, state management)
- ✅ 639 tests passing, solid codebase

### Enhancement Layers

```
Layer 1: User CLI Interface (gmaillm/cli.py)
├── send command (preview-first)
├── ask command (natural language queries)
├── workflow command (autonomous processing)
└── styles command (style management)

Layer 2: Commands Module (gmaillm/commands/)
├── send.py (enhanced with preview+confirm)
├── workflows.py (enhanced with Claude)
├── styles.py (style management)
├── groups.py (group management)
└── labels.py (label management)

Layer 3: Claude Agent Layer (gmaillm/agent.py) - NEW
├── ClaudeEmailAgent class
├── Email analysis
├── Question answering
├── Workflow orchestration
└── Style suggestions

Layer 4: Helpers (gmaillm/helpers/)
├── agent/ (NEW) - Claude integration
├── cli/ - UI/interaction
├── core/ - Paths, I/O
└── domain/ - Business logic
```

---

## Core Features

### Feature 1: Preview-First Email Sending

**Current**: Basic send functionality exists
**Enhancement**: Enforce preview-before-send pattern

**Behavior**:
```bash
gmaillm send --to user@example.com --subject "Hi" --body "Message"
```

**Flow**:
1. Show complete preview (To, CC, BCC, Subject, Body)
2. Apply style guidelines to body
3. Expand groups in recipients
4. Ask "Send this email? [y/N]:"
5. Wait for explicit confirmation
6. Send on "y"/"yes", cancel on "n"/"no"/empty

**Safety Features**:
- ✅ Preview ALWAYS shown
- ✅ Default is NO
- ✅ Requires explicit "y" or "yes"
- ✅ No auto-confirmation via pipes
- ✅ `--yolo` flag for power users

**Tests**: 10 tests written (test_send_preview_confirm.py)

### Feature 2: Claude-Powered Email History Queries

**New Feature**: Ask natural language questions about email

**Behavior**:
```bash
gmaillm ask "What did Angela say about the project?"
gmaillm ask "Summarize emails from Matt this month"
gmaillm ask "When is the next meeting scheduled?"
```

**Flow**:
1. Parse question using Claude
2. Generate search query
3. Search emails using gmaillm
4. Read full email content
5. Have Claude synthesize answer
6. Return annotated response

**Uses**:
- Full email history search
- Natural language understanding
- Multi-email synthesis
- Context-aware responses

### Feature 3: Workflow Automation with Claude

**Current**: Basic workflow infrastructure exists
**Enhancement**: Add Claude intelligence to workflows

**Behavior**:
```bash
gmaillm workflow run daily-digest
gmaillm workflow run urgent-reply
gmaillm workflow run archive-newsletters
```

**Flow**:
1. Load workflow definition (query + actions)
2. Execute search query
3. Claude analyzes emails
4. Claude generates suggested actions
5. Show preview of suggestions
6. User confirms
7. Execute actions autonomously

**Built-in Workflows**:
- `daily-digest`: Categorize and summarize inbox
- `urgent-reply`: Identify and draft replies
- `archive-newsletters`: Clean up newsletters
- `custom`: User-defined workflows

### Feature 4: Style System Integration

**Current**: Styles exist and work
**Enhancement**: Ensure every email uses appropriate style

**Styles**:
- `professional-formal`: Professors, clients, formal
- `professional-friendly`: Colleagues, team
- `casual-friendly`: Friends, informal
- `posts`: Brief broadcasts

**Auto-Detection**:
- Analyzes recipient (domain, history, context)
- Suggests appropriate style
- Can be overridden with `--style` flag
- Applied to preview and final email

---

## Implementation Phases

### Phase 1: Preview+Confirm Enhancement ✅ DONE
**TDD Status**: RED phase complete (10 tests written)

**Actions**:
- ✅ Write comprehensive tests (test_send_preview_confirm.py)
- ⏳ Enhance send command with preview formatting
- ⏳ Implement confirmation logic
- ⏳ Test all edge cases
- ⏳ Refactor and optimize
- ⏳ Commit changes

**Files Modified**:
- gmaillm/commands/send.py (enhance)
- tests/test_send_preview_confirm.py (new)

**Tests**: 10 new tests for preview+confirm workflow

### Phase 2: Claude Agent Integration ⏳ PENDING
**Files to Create**:
- gmaillm/agent.py (new)
- gmaillm/helpers/agent/claude.py (new)

**Components**:
- ClaudeEmailAgent class
- System prompt for email domain
- Tool integration (gmaillm commands)
- Response formatting

### Phase 3: Email History Querying ⏳ PENDING
**Files Modified**:
- gmaillm/cli.py (add ask command)
- gmaillm/commands/ask.py (new)

**Components**:
- Question parsing
- Search query generation
- Email synthesis
- Context management

### Phase 4: Workflow Enhancement ⏳ PENDING
**Files Modified**:
- gmaillm/commands/workflows.py (enhance)
- gmaillm/agent.py (integrate)

**Components**:
- Workflow execution with Claude
- Action generation
- Preview system
- Execution engine

### Phase 5: Documentation ⏳ PENDING
**Files Created**:
- /skills/gmaillm-advanced/SKILL.md ✅ DONE
- /skills/gmaillm-advanced/references/workflows.md (new)
- /skills/gmaillm-advanced/references/styles.md (new)

---

## Testing Strategy

### Test Coverage

**Unit Tests**:
- Preview generation and formatting
- Confirmation logic
- Style application
- Error handling

**Integration Tests**:
- Send with preview+confirm
- Ask queries (mocked Claude)
- Workflow execution
- Group expansion

**End-to-End Tests**:
- Full send flow
- Full ask flow
- Full workflow flow

**Current Status**: 639 tests passing, new tests ready

### TDD Workflow

Following Red-Green-Refactor-Commit cycle:

1. **RED**: Write failing tests ✅ DONE
2. **GREEN**: Implement minimum code needed
3. **REFACTOR**: Clean up and optimize
4. **COMMIT**: Save progress with descriptive message

---

## Key Design Decisions

### 1. Preview-First is Non-Negotiable
- Every email operation shows preview
- User must explicitly confirm
- No auto-confirmation via pipes
- `--yolo` flag for power users (send without confirmation)

### 2. Styles are Mandatory
- Every email uses a style
- Auto-detection from context
- Can be overridden explicitly
- Style guidelines shown in preview

### 3. Claude Assists, Doesn't Replace
- Agent analyzes and suggests
- User makes final decisions
- All actions previewed before execution
- Workflows need confirmation before running

### 4. Safety Over Speed
- Preview shown by default
- Confirmation required by default
- Clear error messages
- Audit trail of actions

---

## Success Criteria

✅ Users cannot accidentally send emails (preview required)
✅ All emails have appropriate style applied
✅ Claude agent answers questions about email history
✅ Workflows run with proper confirmation
✅ New users understand preview-first philosophy
✅ All 639+ tests pass
✅ Code quality maintained (lint, type checking)

---

## Git Workflow

### Commits Follow Pattern

```
<type>(<scope>): <brief description>

<detailed explanation>

Tests: <number> passing
```

### Example Commits

```
Add: preview+confirm flow for email sending

- RED: Added 10 tests for preview-before-send
- GREEN: Enhanced send command with confirmation
- REFACTOR: Improved preview formatting

Tests: 649 passing
```

```
Add: Claude agent integration for email analysis

- RED: Added agent tests
- GREEN: Implemented ClaudeEmailAgent
- REFACTOR: Cleaned up tool integration

Tests: 670 passing
```

---

## File Structure (Final)

```
gmaillm/
├── agent.py (NEW)
├── cli.py (ENHANCED)
├── commands/
│   ├── send.py (ENHANCED)
│   ├── workflows.py (ENHANCED)
│   ├── ask.py (NEW)
│   ├── styles.py
│   ├── groups.py
│   └── labels.py
├── helpers/
│   ├── agent/ (NEW)
│   │   └── claude.py
│   ├── cli/
│   ├── core/
│   └── domain/
├── workflows/ (OPTIONAL)
│   ├── daily-digest.yaml
│   ├── urgent-reply.yaml
│   └── archive-newsletters.yaml
└── tests/
    ├── test_send_preview_confirm.py (NEW)
    ├── test_agent.py (NEW)
    ├── test_ask_command.py (NEW)
    └── ... (existing tests)
```

---

## Documentation

### User Documentation
- `/skills/gmaillm-advanced/SKILL.md` ✅ CREATED
- Purpose: Teach Claude (and users) how to use gmaillm
- Content: Commands, workflows, best practices, patterns

### Developer Documentation
- `GMAILLM_ENHANCEMENT_PLAN.md` ✅ THIS FILE
- Purpose: Guide implementation
- Content: Architecture, phases, design decisions

### In-Code Documentation
- Docstrings for all new functions
- Type hints throughout
- Comments for complex logic

---

## Next Steps (Immediate)

1. **Complete Phase 1** (Send preview+confirm):
   - Run tests to verify passing
   - Implement any missing pieces
   - Refactor for code quality
   - Commit with descriptive message

2. **Proceed to Phase 2** (Claude agent):
   - Create agent.py with ClaudeEmailAgent
   - Integrate Claude Agent SDK
   - Test with mocked Claude
   - Add to pipeline

3. **Continue through Phases 3-5**:
   - Each phase follows TDD cycle
   - All tests must pass
   - Code quality maintained
   - Commits after each phase

4. **Final verification**:
   - Run full test suite (target: 700+ tests)
   - Lint and type check
   - Manual end-to-end testing
   - Update documentation

---

## Timeline Estimate

- **Phase 1** (Preview+Confirm): 1-2 hours
- **Phase 2** (Claude Agent): 2-3 hours
- **Phase 3** (Ask Command): 1-2 hours
- **Phase 4** (Workflows): 2-3 hours
- **Phase 5** (Documentation): 1 hour
- **Testing & Validation**: 1-2 hours

**Total**: 8-13 hours for complete implementation

---

## Risk Mitigation

**Risk**: Breaking existing functionality
**Mitigation**: Comprehensive test coverage, careful refactoring

**Risk**: Claude API failures
**Mitigation**: Graceful error handling, fallback modes

**Risk**: Workflow infinite loops
**Mitigation**: Token expiry, max iteration limits, user confirmation

**Risk**: Over-complicated code
**Mitigation**: Clear separation of concerns, extensive tests, documentation

---

## Conclusion

This plan provides a structured, test-driven approach to enhancing gmaillm with Claude AI integration while maintaining safety and user control. The preview-first workflow ensures users maintain oversight, while Claude intelligence amplifies productivity.

**Current Status**: ✅ Plan complete, tests written, ready for implementation
**Next Action**: Execute Phase 1 (GREEN phase of TDD)

---

**Created**: 2025-10-30
**Version**: 1.0
**Status**: Ready for Implementation
