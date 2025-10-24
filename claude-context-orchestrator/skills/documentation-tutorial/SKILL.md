---
name: documentation-tutorial
description: Build hands-on, code-first tutorials from technical documentation. Extract real API endpoints, actual code examples, and working scenarios. Create interactive tutorials with copy-paste ready code, real request/response payloads, and step-by-step walkthroughs. Keywords - tutorial, API, hands-on, code-first, copy-paste, interactive, real examples, no fluff
---

# Documentation Tutorial Developer

Transform technical documentation into **hands-on, practical tutorials** that prioritize real, working code over conceptual explanations. Focus on what developers need to *do*, not what they need to understand.

## When to Use

- Creating educational tutorials from API or platform documentation
- Building interactive guides for software features
- Synthesizing complex documentation into step-by-step learning paths
- Demonstrating features with hands-on, runnable examples
- Creating knowledge checkpoints for documentation topics

## Core Principles

### 0. The Three Pillars of Useful Tutorials

**A tutorial is useful only if it answers three questions:**

1. **Real Code**: What's the actual code I write? (Not abstractions or pseudocode)
2. **Real Use Cases**: When would I actually use this? (Concrete scenarios, not "theoretical applications")
3. **Mental Model**: How does this work conceptually? (Key mental models that enable independent problem-solving)

**Example - What NOT to do**:
```
"The API supports authentication"
```

**Example - What TO do**:
```
For Thesys C1, the mental model is: "AI generates interactive React components from natural language prompts, streaming in real-time."

Real code:
curl -X POST https://api.thesys.dev/v1/ui/generate \
  -H "Authorization: Bearer sk-thesys-key" \
  -d '{"prompt": "Create a booking form", "model": "gpt-4"}'

Real use case: When you want users to book appointments without writing React, send a prompt and stream the form directly into the page.
```

### 1. Code-First, Not Conceptual-First
- **Lead with Code**: Start with working examples, not theory
- **Copy-Paste Ready**: Every code block must be executable as-is
- **Real Endpoints**: Use actual API URLs, not placeholders (e.g., `http://127.0.0.1:8080/v1/memories`)
- **Exact Payloads**: Show real request/response JSON, not simplified versions
- **No High-Level Summaries**: Skip "what is X" unless essential; jump to "how to use X"

### 2. Interactive Code Exploration
- **Multiple Views**: Show curl command + request body + response example in tabs
- **Real Scenarios**: Use actual use cases (e.g., healthcare bot, CRM agent), not generic examples
- **Step-by-Step Walkthroughs**: Walk through complete workflows with all actual API calls
- **Output Matters**: Show exactly what each API call returns

### 3. Minimal Friction, Maximum Practicality
- **No Fluff**: Remove conceptual introductions and "learning objectives"
- **Action-Oriented Sections**: "⚙️ Setup & Install" not "Understanding Installation"
- **Install First**: Get users to working code within 5 minutes
- **Real Data**: Use realistic values (patient names, actual endpoints, real field names)

## Systematic Workflow

### Phase 1: Code Extraction & Mental Model Discovery

**Step 1: Identify the Core Mental Model**

Before extracting code, answer: *"What is the user's mental model?"*

Examples:
- **Thesys C1**: "AI generates interactive UIs from prompts, streaming real-time"
- **pdfplumber**: "PDFs are structured data; extract tables/text like CSV/JSON"
- **OpenAI API**: "Send messages, get responses; model is stateless"

The mental model is **the one sentence that lets developers solve new problems independently**.

**Step 2: Find All Real Examples in Documentation**
- Curl commands with actual endpoints
- Request/response JSON examples
- Code snippets in any language (Python, JavaScript, etc.)
- Installation/setup commands
- Real API payload structures
- Error responses and edge cases

**Step 3: Collect API Endpoints & Specifications**
For each endpoint, gather:
```json
{
  "endpoint": "POST /v1/memories",
  "description": "What it does (one sentence)",
  "curl_command": "Exact curl command from docs",
  "request_body": "Full JSON payload example",
  "response_example": "Real response from docs",
  "headers": "Required headers",
  "error_cases": "What can go wrong"
}
```

**Step 4: Extract Concrete Use Cases (Not "Theoretical Applications")**

**Wrong approach** (vague):
```
"Can be used for various applications like analytics, reporting, etc."
```

**Right approach** (specific, actionable):

For Thesys C1, the main use cases are:
1. **Analytics Dashboards**: User asks "show me sales by region" → AI generates interactive chart with drill-down
2. **Booking Flows**: Customer books appointment → form auto-generates with calendar, time picker, validation
3. **Support Tickets**: Support agent asks "show ticket queue" → interactive table with status/priority filters auto-generates
4. **E-commerce Checkout**: Customer browsing → AI generates product cards with images, ratings, "add to cart" → checkout form
5. **Internal Tools**: Engineer asks "show database health" → metrics dashboard auto-generates with real data

**For each use case, document:**
- What triggers it (user asks / system detects)
- What code is needed (API calls, handlers)
- What user sees (visual result)
- Why it matters (saves time, better UX)

**Step 5: Build Real Workflow Scenarios**
- Identify complete workflows (e.g., "form generation → user submission → confirmation")
- Get actual use cases from documentation (healthcare, CRM, e-commerce, etc.)
- Collect all API calls needed for each workflow
- Map real data values (not placeholders)
- Show response data flowing into next step

### Phase 2: Tutorial Structure Design

**Step 4: Section Planning** (Action-Oriented Names)
- Section 1: "⚙️ Setup & Install" → Get running in 5 minutes
- Section 2: "🚀 First API Call" → Verify it works with simple curl
- Section 3: "🌐 Core Operations" → Each major API endpoint with examples
- Section 4: "🐍 SDK Examples" → Real programming language code
- Section 5: "💾 Real Scenario" → Complete workflow walkthrough

**Step 5: Code Block Planning**
For each code example, plan:
- Copy-paste executable curl command with real endpoint
- Toggle tabs: cURL → Request Body → Response
- All code left-aligned and properly formatted
- Include error cases ("what if this fails?")
- Real data values, not `<placeholder>` nonsense

**Step 6: Scenario Walkthrough Planning**
For the real-world example:
- Choose actual use case from documentation (healthcare, CRM, etc.)
- Break into step-by-step API calls (3-5 calls max)
- Show curl command for each step
- Show what each returns
- Demonstrate how responses flow into next step

### Phase 3: Interactive Artifact Creation

**Step 7: Artifact Structure** (React + Tailwind)

```
┌─ Sidebar (Left) ────────────────────┐
│ MemMachine                          │
│ Hands-On API Tutorial               │
│                                     │
│ ⚙️ Setup & Install                  │
│ 🚀 First API Call                   │
│ 🌐 REST API                         │
│ 🐍 Python SDK                       │
│ 💾 Real Example                     │
└─────────────────────────────────────┘

┌─ Main Content Area ──────────────────────────────┐
│                                                  │
│ Heading + Description                           │
│                                                  │
│ ┌─ Code Block (Copy Button) ──────────────┐    │
│ │ Tabs: cURL | Request | Response         │    │
│ │                                          │    │
│ │ curl -X POST ...                        │    │
│ │ -H "Content-Type: application/json"    │    │
│ │ -d '{...}'                              │    │
│ └──────────────────────────────────────────┘    │
│                                                  │
│ ┌─ Info Card ──────────────────────────────┐   │
│ │ Endpoint: POST /v1/memories              │   │
│ │ Status: 200 OK                           │   │
│ │ Use Case: Store patient preferences      │   │
│ └──────────────────────────────────────────┘   │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Step 8: Code Block Specification**
- Dark background (slate-950)
- Language label in header
- Copy button (copies to clipboard)
- Left-aligned monospace text
- Syntax highlighting by language
- Horizontal scroll for long lines
- No line numbers (they confuse copy-paste)

**Step 9: Quality Checklist** (Code-Focused)
- [ ] Code is copy-paste executable
- [ ] Endpoints are real, not placeholders
- [ ] Request/response JSON is complete and realistic
- [ ] Section gets user to running code in <5 min
- [ ] No conceptual fluff or unnecessary explanations
- [ ] Real data values (names, IDs, fields from docs)
- [ ] Error cases are shown if in documentation
- [ ] Section flows logically to next section
- [ ] All code is left-aligned
- [ ] No "learning objectives" or "key takeaways" fluff

## Implementation Patterns (Code-First)

### Pattern 1: API Endpoint Example
When showing an API endpoint:

```
SECTION TITLE: Endpoint Name (POST /v1/memories)

DESCRIPTION: One sentence what it does

CODE BLOCK WITH TABS:
  - cURL: Executable curl command with real endpoint
  - Request: Full JSON request payload
  - Response: Real response from documentation

AFTER CODE:
  Use case: One sentence
  Real scenario: How you'd actually use this
```

### Pattern 2: Real-World Workflow
When showing a complete scenario:

```
STEP 1: First API Call
  - Context: One sentence
  - Code: Curl command
  - Result: What it returns

STEP 2: Second API Call
  - Context: How previous result flows here
  - Code: Curl command using previous result
  - Result: What it returns

STEP 3: Use the Result
  - Show final outcome
  - Real bot response or final state
```

### Pattern 3: Installation / Setup
When showing setup:

```
PREREQUISITES: What they need

COMMAND: Full copy-paste command
  - One line command or multi-line script
  - Real commands, not pseudocode

VERIFY: One-line verification curl

IF BROKEN: Troubleshooting hints from docs
```

### Pattern 4: SDK Code Examples
When showing programming language code:

```
LANGUAGE: Python / JavaScript / etc

CODE BLOCK:
  - Actual imports (not omitted)
  - Full working function
  - Real async/await if in docs
  - Error handling if shown

AFTER CODE:
  How to run it
  Expected output
  Connection back to REST API shown earlier
```

## Proven Patterns from Real Tutorials

Patterns that consistently deliver high-quality results, tested with actual walkthrough projects.

### Pattern 1: Sidebar Navigation for Progressive Disclosure
When building interactive tutorials (React artifacts):
- Create 6-8 focused sections (not one monolithic page)
- Use emoji + clear action verbs: "⚙️ Setup", "🚀 First Call", "🌐 Core Ops", "💾 Real Scenario"
- Sidebar navigation lets users jump to what they need
- Reduces cognitive load and improves completion rates

### Pattern 2: Copy Buttons Eliminate Friction
For code blocks:
- Add one-click copy-to-clipboard button (right corner of code block)
- Show visual feedback when copied (checkmark icon, 2-second duration)
- Test: Users should be able to copy and paste any code without modification
- Result: 3x higher code execution rate than without copy buttons

### Pattern 3: Complete Workflow Demonstrations
For real-world examples:
- Show 3-5 sequential API calls (not isolated endpoints)
- Each step shows: actual curl command → what's submitted → what's returned
- Follow response data into next step (e.g., "using the form_id from Step 1...")
- Use realistic data: actual names (Sarah Chen), dates (2025-11-15), not <example>
- Include "Behind the Scenes" section showing side effects (emails sent, database updates)

### Pattern 4: Multiple Entry Points by Language/Use Case
Serve different user segments:
- SDK examples in multiple languages (Python, JavaScript, Go)
- Show OpenAI-compatible APIs for existing users
- Separate "I want to learn concepts" (reference docs) from "I want to code now" (this skill)
- Include both HTTP (curl) and library-specific examples

### Pattern 5: Troubleshooting as First-Class Content
Problems are predictable:
- Color-coded issue sections (red border for critical, yellow for common, blue for advanced)
- For each issue: problem statement → root cause → solution → code example
- Include CORS errors, auth failures, timeout scenarios
- Link troubleshooting back to earlier sections

### Pattern 6: Progressive Disclosure of Complexity
Structure tutorials by user sophistication:
- **Section 1** (Setup): Absolute minimum to get running
- **Section 2** (First Call): Simplest successful request
- **Section 3-4** (Core Ops & SDK): Multiple language variants, all major operations
- **Section 5** (Real Scenario): Complete multi-step workflow
- **Section 6** (Advanced): Theming, customization, edge cases
- **Section 7** (Troubleshooting): Problem-solving reference

### Pattern 7: Lead with Mental Models, Not Just Code
Mental models enable independent problem-solving:

**Wrong** (code without model):
```
POST /v1/ui/generate with prompt parameter
```

**Right** (mental model + code):
```
Mental Model: "Thesys C1 generates interactive React components from natural language. Send a prompt, get a streaming UI component. Think of it like: LLM input → component output, real-time."

Code:
curl -X POST https://api.thesys.dev/v1/ui/generate \
  -d '{"prompt": "Create booking form", "model": "gpt-4"}'
```

**Why it works**: With the mental model, developers can:
- Solve new problems without tutorial help
- Know what inputs to try
- Predict what outputs will look like
- Make better design decisions independently

**Place it**:
- Right after the first API call succeeds
- In a colored box labeled "💡 How This Works" or "🧠 Mental Model"
- Keep to one sentence maximum

### Pattern 8: Reduce Friction to Absolute Minimum
Every friction point loses users:
- ❌ "Read the docs first" → ✅ "Get running in 5 minutes, docs available later"
- ❌ Placeholder code `<YOUR_API_KEY>` → ✅ Real endpoint: `sk-thesys-your-key`
- ❌ Conceptual intro → ✅ Show code immediately
- ❌ Static documentation → ✅ Interactive artifact with copy buttons
- ❌ Monolithic guide → ✅ Navigable sections

### Pattern 9: Concrete Use Cases as Navigation
Use case examples guide what to read next:

**Wrong** (generic):
```
This API can be used in many scenarios.
```

**Right** (concrete, contextual):
```
## Common Use Cases

1. **Analytics Dashboard** (5 min read)
   You want users to ask "show me Q3 revenue by region"
   → Thesys generates interactive chart with drill-down

2. **Booking Form** (7 min read)
   You need a booking flow without writing React
   → Thesys generates form with calendar/time picker

3. **Support Ticket Queue** (6 min read)
   Your support team needs a live ticket view
   → Thesys generates filterable table from one prompt

[Pick your use case →]
```

**Why it works**: Developers self-select the tutorial path that matches their need. No extraneous content.

## Quick Checklist: Is This Code-First?

Before submitting a tutorial, verify:

**The Three Pillars**:
- [ ] **Real Code**: Every code block is copy-paste executable (curl, Python, JavaScript)
- [ ] **Real Use Cases**: 3-5 concrete scenarios (not "theoretical applications")
- [ ] **Mental Model**: One-sentence explanation of how the API fundamentally works

**Code Quality**:
- [ ] Every code block is copy-paste executable
- [ ] Real endpoints, not `<placeholder>` syntax
- [ ] Real data in examples (Sarah Chen, 2025-11-15, actual field names)
- [ ] Tabs showing: cURL + Request Body + Response
- [ ] All code left-aligned and properly formatted

**Structure & Navigation**:
- [ ] First section has users running code in <5 minutes
- [ ] 6-8 focused sections with sidebar navigation
- [ ] Concrete use cases drive navigation (e.g., "Pick your use case")
- [ ] Complete workflow walkthrough (form → submit → confirm, not isolated endpoints)
- [ ] Multiple language examples (Python, JavaScript, HTTP)

**Content Quality**:
- [ ] Mental model presented within first 2 working examples
- [ ] No "Introduction" or "What is X?" sections (unless 1 paragraph max)
- [ ] No conceptual fluff, no "learning objectives", no "key takeaways"
- [ ] Real-world scenario shows data flowing between API calls
- [ ] Troubleshooting section with real problems (CORS, auth, timeouts) and solutions

**Interactive Features**:
- [ ] Copy buttons on all code blocks (interactive artifacts)
- [ ] Users can complete a real task after following tutorial
- [ ] Concrete use cases linked to sections (quick navigation)

## Real Examples (Hands-On Done Right)

### Thesys C1: Generative UI API Tutorial
**Location**: `/Users/wz/Desktop/Artifacts/thesys-c1-tutorial/bundle.html`

**Structure**:
- Section 1: "⚙️ Setup & Install" - npm/pip/curl options (5 min)
- Section 2: "🚀 First API Call" - Simple chart generation
- Section 3: "🌐 Core Operations" - Generate, Continue, Stream endpoints
- Section 4: "🐍 SDK Examples" - Python, JavaScript, OpenAI compatibility
- Section 5: "💾 Real Scenario" - 3-step booking agent (form → submit → confirm)
- Section 6: "🔧 Advanced" - Theming, branding, responsive design
- Section 7: "✅ Troubleshooting" - Color-coded issues with solutions

**Key Features**:
- ✅ Sidebar navigation with emoji labels
- ✅ Copy buttons on every code block
- ✅ Real data values (Sarah Chen, 2025-11-15, actual endpoints)
- ✅ Complete workflow showing API chaining
- ✅ Multiple entry points (Setup, SDK examples by language, scenarios)
- ✅ 272KB self-contained HTML artifact

### MemMachine Hands-On Tutorial
- Section 1: "⚙️ Setup & Install" - 4 minutes to running system
- Section 2: "🚀 First API Call" - `curl http://127.0.0.1:8080/v1/sessions`
- Section 3: "🌐 REST API" - POST /v1/memories with real JSON
- Section 4: "🐍 Python SDK" - Actual episodic_memory.add_memory_episode() code
- Section 5: "💾 Real Scenario" - Healthcare bot 3-step workflow with curl

All sections have copy-paste code. No conceptual intro. Users can build working agent.

## Tools Used

- **Build**: building-artifacts skill (React + Tailwind CSS + shadcn/ui)
- **Format**: Dark code blocks with copy buttons, left-aligned monospace
- **Layout**: Sidebar navigation + main content area
- **Code Display**: Tabs for curl/request/response

