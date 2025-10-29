---
name: documentation-tutorial
description: Build hands-on, code-first tutorials from any primary source - technical documentation, codebases, APIs, tools, or other complex material. Extract real examples, working code, and concrete scenarios. Create tutorials using markdown (text-heavy summaries) or React artifacts (complex interactive workflows). Keywords - tutorial, codebase, API, hands-on, code-first, copy-paste, interactive, real examples, primary source
---

# Tutorial Developer from Primary Sources

Transform any primary source into hands-on, practical tutorials that prioritize real, working examples over conceptual explanations. Focus on what users need to *do*, not what they need to understand.

## Quick Decision Guide

**Step 1: Choose format**
- Text-heavy summary or CLI reference → Markdown
- Complex workflow with multiple steps → React Artifact

**Step 2: Follow the three pillars**
1. Real code/commands (not pseudocode)
2. Real use cases (concrete scenarios)
3. Mental model (one-sentence explanation)

## Core Principles

### The Three Pillars

Every tutorial must clearly answer:

1. **Real Code**: What's the actual code or command I run? (Copy-paste executable, no pseudocode)
2. **Real Use Cases**: When would I actually use this? (Concrete scenarios like "healthcare bot", not vague descriptions)
3. **Mental Model**: How does this work? (One-sentence explanation enabling independent problem-solving)

**Example:**
```
Mental Model: "AI generates interactive React components from natural language prompts, streaming in real-time."

Code:
curl -X POST https://api.thesys.dev/v1/ui/generate \
  -H "Authorization: Bearer sk-thesys-key" \
  -d '{"prompt": "Create a booking form", "model": "gpt-4"}'

Use Case: When you want users to book appointments without writing React,
send a prompt and stream the form directly into the page.
```

### Code-First Approach

- Lead with working examples, not theory
- Real endpoints (actual URLs, not `<placeholder>`)
- Exact payloads (complete JSON, not simplified)
- No high-level summaries unless essential
- Get users to running code within 5 minutes

## Systematic Workflow

### Phase 1: Extract from Primary Source

**Step 1: Identify Core Mental Model**

Answer: *"What's the one-sentence explanation that makes everything click?"*

Examples:
- API: "AI generates interactive UIs from prompts, streaming real-time"
- Tool: "PDFs are structured data; extract tables/text like CSV/JSON"
- Codebase: "Request flows through middleware → router → handler → response"

**Step 2: Find Real Examples**

Extract from docs/code:
- Working code (not pseudocode)
- CLI commands with actual flags
- API calls (curl + request/response)
- Config files, error cases

**Step 3: Extract Concrete Use Cases**

❌ **Wrong:** "Can be used for various applications like analytics, reporting, etc."

✅ **Right:**
1. **Analytics Dashboard**: User asks "show me sales by region" → AI generates chart
2. **Booking Flow**: Customer books appointment → form auto-generates with calendar
3. **Support Tickets**: Agent asks "show ticket queue" → interactive table generates

For each: What triggers it, what code is needed, what user sees, why it matters.

### Phase 2: Structure Tutorial

**Step 4: Plan Sections** (Action-oriented names)
- Section 1: "⚙️ Setup & Install" → Running in 5 minutes
- Section 2: "🚀 First API Call" → Verify it works
- Section 3: "🌐 Core Operations" → Major endpoints
- Section 4: "🐍 SDK Examples" → Language-specific code
- Section 5: "💾 Real Scenario" → Complete workflow

**Step 5: Plan Code Blocks**
- Copy-paste executable curl with real endpoint
- Tabs: cURL → Request Body → Response
- Real data values (names, dates, actual fields)
- Error cases if documented

**Step 6: Plan Workflow**
- Choose actual use case from documentation
- Break into 3-5 sequential API calls
- Show how responses flow into next step

### Phase 3: Implement

**Step 7: For React Artifacts**

Structure:
- Sidebar navigation (6-8 focused sections)
- Main content area with code blocks
- Copy buttons on all code
- Tabbed views (curl/request/response)

**Step 8: Code Block Spec**
- Dark background, language label, copy button
- Left-aligned monospace, syntax highlighting
- No line numbers (confuses copy-paste)

**Step 9: Quality Check** (see checklist at end)

## Tutorial Patterns

### Pattern: API Endpoints
```
TITLE: Endpoint Name (POST /v1/endpoint)
DESCRIPTION: One sentence
CODE BLOCK: Tabs (cURL | Request | Response)
USE CASE: One sentence + real scenario
```

### Pattern: Complete Workflows
```
STEP 1: First API Call
  Context (1 sentence) → Code → Result
STEP 2: Second API Call
  Context (how previous flows here) → Code → Result
STEP 3: Final Outcome
```

### Pattern: Setup/Installation
```
PREREQUISITES: What they need
COMMAND: Full copy-paste command
VERIFY: One-line check
TROUBLESHOOTING: Common issues
```

### Pattern: SDK Examples
```
LANGUAGE: Python/JavaScript/etc
CODE: Full working function (imports, async/await, error handling)
RUN IT: How to execute
OUTPUT: Expected result
```

### Pattern: Sidebar Navigation
- 6-8 focused sections (not monolithic)
- Emoji + action verbs: "⚙️ Setup", "🚀 First Call"
- Reduces cognitive load, improves completion

### Pattern: Copy Buttons
- One-click copy-to-clipboard (right corner)
- Visual feedback when copied (checkmark, 2 seconds)
- 3x higher code execution rate

### Pattern: Mental Models First
- Present one-sentence model after first working example
- Place in colored box: "💡 How This Works"
- Enables independent problem-solving

### Pattern: Progressive Disclosure
- Section 1: Minimum to get running
- Section 2: Simplest successful request
- Section 3-4: Core operations, multiple languages
- Section 5: Complete multi-step workflow
- Section 6: Advanced features
- Section 7: Troubleshooting

### Pattern: Concrete Use Cases
```
## Common Use Cases

1. **Analytics Dashboard** (5 min read)
   You want users to ask "show me Q3 revenue"
   → AI generates interactive chart

2. **Booking Form** (7 min read)
   You need booking flow without React
   → AI generates form with calendar

[Pick your use case →]
```

Benefit: Users self-select relevant tutorial path.

### Pattern: Troubleshooting
- Color-coded sections (red=critical, yellow=common)
- For each: Problem → Root cause → Solution → Code
- Include CORS, auth failures, timeouts

## Quality Checklist

**Three Pillars:**
- [ ] Real code (copy-paste executable: curl, Python, JavaScript)
- [ ] Real use cases (3-5 concrete scenarios, not "theoretical")
- [ ] Mental model (one-sentence explanation)

**Code Quality:**
- [ ] Real endpoints (no `<placeholder>`)
- [ ] Real data (Sarah Chen, 2025-11-15, actual field names)
- [ ] Tabs: cURL + Request + Response
- [ ] Left-aligned, properly formatted

**Structure:**
- [ ] First section: Running code in <5 minutes
- [ ] 6-8 focused sections with navigation
- [ ] Complete workflow (form → submit → confirm)
- [ ] Multiple languages (Python, JavaScript, HTTP)

**Content:**
- [ ] Mental model within first 2 examples
- [ ] No conceptual fluff or "learning objectives"
- [ ] Real-world scenario shows data flowing
- [ ] Troubleshooting with real problems

**Interactive (for React artifacts):**
- [ ] Copy buttons on all code
- [ ] Users can complete real task after tutorial

## Real Examples

### Example 1: Mail Command (Markdown)
**Why Markdown:** CLI reference with many commands

**Structure:** Basic Sending → Advanced Options → Interactive Mode → Reading Mail → Configuration → Gmail Integration → Quick Reference

**Key Features:** Copy-paste commands, real config files, organized by workflow

### Example 2: Thesys C1 API (React Artifact)
**Why React:** Complex API needing interactive tabs/navigation

**Structure:** Setup (5min) → First Call → Core Operations → SDK Examples → Real Scenario → Advanced → Troubleshooting

**Key Features:** Sidebar navigation, copy buttons, tabbed views, real data, workflow chaining

## Academic Study Guides: Quote Integration

Same principle applies to academic primary sources (historical documents, philosophical texts, legal cases): transform into practical guide.

### Core Principle
Embed quotes throughout analysis where they support arguments. NOT collected at end.

### Pattern
```
Question → Quote → Interpretation → Quote → Synthesis

NOT: Question → Summary → All Quotes at End
```

### Example
```markdown
## Was Qianlong's Response Wise?

Qianlong defended sovereignty. He explained:

> "If other nations imitate your evil example... how could I possibly comply?"

His reasoning was sound: granting Britain privileges would force him to grant all nations the same.

However, his rejection showed complacency:

> "Strange and costly objects do not interest me."

By dismissing British technology, he missed intelligence-gathering opportunities.
```

### Debate Format
1. Clear position
2. 8-10 numbered arguments (each with quote evidence)
3. Rebuttals section
4. Conclusion

**Each argument:** Claim → Quote → Interpret → Connect to thesis

### Checklist
- [ ] Quotes embedded at point of analysis
- [ ] Every claim supported by quote
- [ ] Each quote followed by interpretation
- [ ] Creates "guide through sources"

## File Organization

**CRITICAL:** All tutorials follow this organization pattern:

### 1. Create in Central Tutorial Directory

```bash
# Organize by topic in ~/Desktop/Tutorial
mkdir -p ~/Desktop/Tutorial/{topic-name}

# Create tutorial file there
# Example: ~/Desktop/Tutorial/python-cli/typer-tutorial.md
```

**Topic categories:**
- `python-cli/` - CLI tools, Typer, Click, argparse
- `web-apis/` - API tutorials, REST, GraphQL
- `frontend/` - React, JavaScript, HTML/CSS
- `backend/` - Django, Flask, Node.js
- `devops/` - Docker, Kubernetes, CI/CD
- `databases/` - SQL, NoSQL, ORMs
- `tools/` - Git, GitHub, VS Code extensions
- `languages/` - Language-specific guides

### 2. Create Symlink in Current Directory

```bash
# From the project directory, create Tutorial/ directory
mkdir -p Tutorial

# Create symlink to specific tutorial
ln -s ~/Desktop/Tutorial/{topic-name}/{tutorial-name}.md Tutorial/{tutorial-name}.md

# Example:
cd /path/to/gmail-integration-plugin
mkdir -p Tutorial
ln -s ~/Desktop/Tutorial/python-cli/typer-tutorial.md Tutorial/typer-tutorial.md
```

### 3. Verify Structure

```bash
# Check symlink works
ls -la Tutorial/
# Should show: typer-tutorial.md -> ~/Desktop/Tutorial/python-cli/typer-tutorial.md

# Read through symlink
cat Tutorial/typer-tutorial.md
```

### Why This Pattern?

1. **Centralized tutorials** - All tutorials in one place (~/Desktop/Tutorial)
2. **Topic organization** - Easy to find related tutorials
3. **Project-specific access** - Symlink makes it available in current project
4. **Reusability** - Same tutorial can be symlinked from multiple projects
5. **Version control** - Symlinks don't clutter git repos (add `Tutorial/` to .gitignore)

### Workflow

When creating a tutorial:
1. Determine topic category
2. Create file in `~/Desktop/Tutorial/{topic}/`
3. Create `Tutorial/` directory in current project
4. Symlink from project to central location
5. Add `Tutorial/` to `.gitignore`

## Tools & Preview

**Build:** building-artifacts skill (React + Tailwind + shadcn/ui)
**Format:** Dark code blocks with copy buttons, monospace
**Layout:** Sidebar + main content

**Preview markdown tutorials:**
```bash
nvim -c "MarkdownPreview" /path/to/tutorial.md
```

Use direct commands (no aliases) for reproducibility.
