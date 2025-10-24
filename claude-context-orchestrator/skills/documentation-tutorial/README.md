# Documentation Tutorial Skill

**Purpose**: Build hands-on, code-first tutorials from technical documentation. Extract real API endpoints, actual code examples, and working scenarios. Create interactive tutorials with copy-paste ready code, real request/response payloads, and step-by-step walkthroughs.

**Status**: ✅ Production Ready (Code-First Focus)

---

## Quick Start

### When to Use This Skill

Ask for the documentation-tutorial skill when you want to:

1. **Create hands-on API tutorials with real, working code**
   - "Build a tutorial from the MemMachine API docs - make it copy-paste ready"
   - "Create a step-by-step guide for Stripe API with real curl examples"

2. **Transform documentation into practical code walkthroughs**
   - "Turn the Kubernetes CLI docs into a hands-on tutorial with real commands"
   - "Make the GitHub API docs interactive with working cURL examples"

3. **Generate code-first learning paths with minimal fluff**
   - "Create a tutorial showing real API usage with actual request/response payloads"
   - "Build a guide that gets developers working code in 5 minutes"

4. **Build interactive guides focused on executable examples**
   - "Create a tutorial with real, copy-paste code and actual endpoints"
   - "Make a guide that shows what to do, not what to understand"

### Example Requests

```
"Build a code-first tutorial from this API documentation. Focus on
copy-paste executable code, real endpoints, and actual payloads.
No conceptual fluff - I want users running code in 5 minutes."

"Create a hands-on guide from this documentation. Show curl commands
with real endpoints, request/response JSON, and step-by-step workflows
using actual API calls."

"Transform this documentation into a practical tutorial with real
examples. Include setup instructions, first working API call, all
major endpoints with curl, and a complete real-world scenario."
```

---

## How It Works

The skill uses a **3-phase systematic workflow**:

### Phase 1: Code Extraction
- Find all real code examples in documentation (curl commands, SDKs, scripts)
- Extract actual API endpoints and request/response payloads
- Collect installation and setup commands
- Identify real-world workflow scenarios from docs
- Build a code inventory (not concept inventory)

### Phase 2: Tutorial Structure Design
- Plan action-oriented sections: Setup → First Call → Core Operations → SDK → Real Scenario
- Organize code blocks with tabs (curl | request | response)
- Design workflow walkthroughs showing how API calls connect
- Ensure all code is immediately executable (copy-paste ready)

### Phase 3: Interactive Artifact Creation
- Build React artifact with sidebar navigation and main content area
- Embed all code blocks with copy-to-clipboard functionality
- Create tabbed views for API examples (cURL + Request + Response)
- Add info cards showing endpoint, HTTP method, real use cases
- Dark theme with left-aligned monospace code

---

## Core Principles

The skill is built on three core principles:

### 1. ✓ Code-First, Not Conceptual
- Lead with working examples, not theory
- Every code block is copy-paste executable as-is
- Real endpoints (not `<placeholder>`), real data, real payloads
- Skip "what is X" unless essential - jump straight to "how to use X"

### 2. ✓ Interactive Code Exploration
- Show multiple views: cURL command + Request body + Response example
- Use real use cases from documentation (healthcare, CRM, not "test data")
- Complete workflows with all actual API calls shown step-by-step
- Display exactly what each API call returns

### 3. ✓ Minimal Friction, Maximum Practicality
- No conceptual fluff, no "learning objectives," no "key takeaways"
- Action-oriented section names: "⚙️ Setup & Install" not "Understanding Installation"
- Get developers to working code within 5 minutes
- Real, realistic data values throughout

---

## Output Format

The skill produces a **single interactive HTML file** (~300KB) containing:

✅ **Sidebar Navigation**
- Action-oriented section links (⚙️ Setup, 🚀 First Call, 🌐 REST API, etc.)
- Visual progress indicator
- Current section highlighting

✅ **Main Content Area**
- Section heading + one-line description
- Code blocks with copy-to-clipboard
- Tabbed interfaces for API examples (cURL | Request | Response)
- Info cards showing endpoint, HTTP method, real use cases
- Step-by-step workflow walkthroughs with actual API calls

✅ **Interactive Features**
- Copy button on every code block (copies to clipboard instantly)
- Tabs for exploring different views of API calls
- Dark theme optimized for code (slate-950 background)
- Left-aligned monospace code (NEVER centered)
- Responsive design for mobile/tablet/desktop
- Syntax highlighting by language (python, bash, json, etc.)

---

## Real-World Example

Here's what was created when testing with MemMachine documentation:

**Output Structure** - Pure hands-on focus:
1. **⚙️ Setup & Install** - Copy-paste installation command + verification curl (5 min)
2. **🚀 First API Call** - Real curl to `http://127.0.0.1:8080/v1/sessions` with response
3. **🌐 REST API** - Three endpoints (POST /memories, GET search, DELETE) with curl tabs
4. **🐍 Python SDK** - Actual working episodic_memory.add_memory_episode() code + async examples
5. **💾 Real Scenario** - Healthcare bot workflow: Store symptom → Search memories → Get response

**Code Quality**:
- All curl commands use actual endpoints (not `<localhost>` placeholders)
- Request/response JSON shows real structures with patient names, actual field names
- Python code copied exactly from docs with full imports and error handling
- Every code block copy-paste executable immediately

---

## Technical Stack

- **Build**: React + TypeScript + Tailwind CSS + shadcn/ui
- **Output**: Single self-contained HTML bundle.html
- **Code Theme**: Dark slate-950 background with syntax highlighting
- **Copy Function**: Native Clipboard API with visual feedback
- **Bundling**: Parcel (zero config, single-file output)

---

## Key Features

### Copy-Paste Ready Code ✓
All code examples are real, executable, from documentation. No `<placeholder>` syntax, no pseudocode, no "simplified versions." Just real, working code.

### Tabbed API Explorer ✓
Switch between views:
- **cURL tab**: Full curl command (ready to run)
- **Request tab**: JSON request body (copy to use in code)
- **Response tab**: Real response example (shows what you'll get)

### Action-Oriented Structure ✓
- Sections named for what you'll DO: "Setup & Install", "First API Call", "REST API"
- Not named for what you'll LEARN: "Understanding Setup", "Learning Concepts"
- Each section progresses logically to the next
- Users can complete real tasks after each section

### Developer-Optimized UX ✓
- Left-aligned code blocks (NOT centered - critical for readability)
- Dark theme reduces eye strain during extended coding sessions
- Copy button on every code block
- Monospace font with syntax highlighting by language
- Horizontal scroll for long lines (no awkward wrapping)

---

## Best Practices for Using This Skill

### ✓ Choose Documentation With Real Code Examples
The best tutorials come from docs that include real examples:
- **Best**: API Quickstart guides with curl examples
- **Good**: Reference documentation with code samples
- **Avoid**: Conceptual/overview documentation without examples

### ✓ Request Code-First Focus
Be explicit about your priorities:
- "Make this copy-paste ready - I want to run code immediately"
- "Use real API endpoints and payloads, not simplified examples"
- "Focus on how to use it, not how it works"

### ✓ Test Code Examples Before Using
While the skill extracts code from documentation:
- Try running a few curl commands
- Copy-paste SDK code and verify imports work
- Report if anything doesn't match the docs

### ✓ Request Workflow Walkthroughs
If the docs have real use cases, ask for them:
- "Show a complete workflow from start to finish"
- "Include actual API call sequences (not just single endpoints)"
- "Use a real scenario from your docs"

---

## Troubleshooting

### "I got too many conceptual introductions"
**Solution**: Request the skill extract from Quickstart/Getting Started sections instead of Introduction pages. Introductions summarize concepts; Quickstarts show actual code.

### "Code blocks are centered instead of left-aligned"
**Solution**: This is a rendering bug. The artifact should use `text-align: left` on all code blocks. Report this and it will be fixed immediately - code alignment matters for developer UX.

### "Missing some API endpoints"
**Solution**: The skill can only include code that's in the documentation. If an endpoint isn't documented with examples, it won't appear in the tutorial. You can request sections be added for undocumented features.

### "Need more workflow examples"
**Solution**: Request "real scenario" sections. Ask for complete workflows that show multiple API calls connected together (e.g., "store data → search → retrieve → use in response").

---

## Success Criteria

A code-first tutorial is successful when it:

1. ✓ **Copy-Paste Ready**: All code is immediately executable (curl works as-is, SDK imports work)
2. ✓ **Real Endpoints**: Uses actual URLs and payloads from documentation (no placeholders)
3. ✓ **Code Accuracy**: All examples match documentation exactly
4. ✓ **Quick Start**: First section gets users running code in <5 minutes
5. ✓ **No Fluff**: No learning objectives, no conceptual summaries, no "key takeaways"
6. ✓ **Real Data**: Examples use realistic values (patient names, actual field names, not "test")
7. ✓ **Complete Workflows**: Real scenarios show how API calls connect, step by step
8. ✓ **Interactive Tabs**: API examples show cURL + Request + Response in accessible tabs
9. ✓ **Dark Theme Code**: Readable code blocks with proper syntax highlighting
10. ✓ **User Can Do**: After following tutorial, user can accomplish real task with the API

---

## File Structure

```
documentation-tutorial/
├── SKILL.md              # Code-first methodology & patterns
├── README.md             # This file - quick start & usage
├── IMPLEMENTATION_NOTES.md  # Technical architecture & debugging
├── SESSION_SUMMARY.md    # Real-world testing & validation
└── [bundle.html]         # Generated interactive tutorial (single file)
```

---

## Support & Feedback

Questions or issues?

1. **Want to understand how it works?** → Read SKILL.md (Phase 1, 2, 3 workflow)
2. **Need technical details?** → Check IMPLEMENTATION_NOTES.md (Architecture, patterns, debugging)
3. **Curious about real usage?** → Review SESSION_SUMMARY.md (MemMachine tutorial, iteration process)
4. **Report specific issues** → Include: documentation URL + what went wrong

---

## License

This skill is custom-created for this project. Tutorials generated by this skill respect and maintain the original documentation's license and authorship.

---

**Version**: 2.0 (Code-First Focus)
**Last Updated**: October 2025
**Status**: Production Ready - Optimized for hands-on, copy-paste code tutorials
