# Documentation Tutorial Skill - Code-First UI & Content Requirements

**Status**: ✅ Updated for Code-First Approach
**Last Updated**: October 2025
**User Feedback**: "I like this much more" - Hands-on, code-first direction confirmed

---

## Executive Summary

The documentation-tutorial skill builds interactive, hands-on tutorials from technical documentation. This document captures the definitive **code-first** UI and content requirements that prioritize executable examples over conceptual explanations.

**Core Philosophy**: Get developers running real code in under 5 minutes. No fluff, no "learning objectives," no conceptual intros. Just code that works.

---

## Content Requirements

### ✅ What MUST Be Included

#### 1. Real, Executable Code Examples
- **Requirement**: All code is copy-paste ready, runs immediately as-is
- **Why**: Developers want to work code first, theory later
- **How to Verify**: Copy any code block, paste into terminal/IDE, it runs
- **Example**: `curl -X POST http://127.0.0.1:8080/v1/memories -H "Content-Type: application/json" -d '{...}'`

#### 2. Actual API Endpoints
- **Requirement**: Use real endpoints from documentation (not `<placeholder>` or `http://localhost:3000`)
- **Why**: Developers need to know exactly which URL to hit
- **How to Verify**: Endpoint matches documentation exactly
- **Example**: `POST /v1/memories` not `POST /memories` or `POST /api/memories`

#### 3. Real Request & Response Payloads
- **Requirement**: Show actual JSON structures from documentation, with real field names and realistic values
- **Why**: Developers copy JSON to understand structure and test immediately
- **How to Verify**: Request/response JSON matches documentation; includes realistic data (names, IDs, field values)
- **Example**:
  ```json
  {
    "user_id": "patient_123",
    "interaction_type": "symptom_report",
    "content": "Patient reported headache and fatigue"
  }
  ```
  NOT: `{"user_id": "xxx", "data": "..." }`

#### 4. Action-Oriented Section Names
- **Requirement**: Section titles describe WHAT YOU'LL DO, not what you'll learn
- **Why**: Developers scan for actionable sections, not concepts
- **How to Verify**: Sections use imperative verbs (Setup, Call, API, Implement) not passive nouns (Understanding, Learning, Concepts)
- **Example**: "⚙️ Setup & Install" or "🚀 First API Call" ✓
  NOT: "Understanding Installation" or "Learning API Concepts" ✗

#### 5. Quick Start (< 5 minutes)
- **Requirement**: First section gets users to running code in under 5 minutes
- **Why**: Developers evaluate tools by trying them, not reading docs
- **How to Verify**: First section has installation command + one verification curl + success response
- **Example**: Copy command → Run → See response → "It works!"

#### 6. Real-World Workflow Scenarios
- **Requirement**: Show complete workflows with multiple API calls connected
- **Why**: Isolated examples don't show how things actually work together
- **How to Verify**: Workflow shows 3-5 connected API calls; each shows input/output; user can accomplish real task
- **Example**: Store symptom → Search memories → Generate response (healthcare bot example)

#### 7. Step-by-Step API Call Chains
- **Requirement**: For workflows, show how data flows between API calls
- **Why**: Developers need to understand request/response connection, not just isolated calls
- **How to Verify**: Each workflow step shows: Input Data → API Call → Response → Next Step Context
- **Example**:
  ```
  STEP 1: Store User Symptom
  POST /v1/memories with patient_id="patient_123"
  Response: memory_id="mem_456"

  STEP 2: Search Related Memories
  GET /v1/search?user_id=patient_123&query="headache"
  Response: [related memories...]

  STEP 3: Use Results
  [Show how results feed into agent response]
  ```

### ❌ What Must NOT Be Included

- ❌ **Conceptual explanations** - No "Understanding X" sections (max 1 paragraph if necessary)
- ❌ **Learning objectives** - No "After this section you'll understand..."
- ❌ **Key takeaways checklists** - No "What you learned" sections
- ❌ **Placeholder syntax** - No `<endpoint>` or `{value}` - use actual values
- ❌ **Simplified code examples** - Show actual code from docs, not "clean" versions
- ❌ **High-level summaries** - Never paraphrase; show real code instead
- ❌ **Theoretical scenarios** - Only real use cases from documentation

---

## UI Requirements

### Layout Architecture

```
┌──────────────────────────────────────────────────────────┐
│             Interactive Code-First Tutorial              │
├─────────────────┬───────────────────────────────────────┤
│                 │                                        │
│   NAVIGATION    │         MAIN CONTENT AREA              │
│   (Left)        │         (Center)                       │
│                 │                                        │
│ ┌─────────────┐ │ ┌──────────────────────────────────┐ │
│ │ MemMachine  │ │ │ ⚙️ Setup & Install               │ │
│ │ Tutorial    │ │ │ Copy-paste command + verify curl │ │
│ ├─────────────┤ │ └──────────────────────────────────┘ │
│ │ ⚙️ Setup    │ │                                      │
│ ├─────────────┤ │ ┌──────────────────────────────────┐ │
│ │ 🚀 First    │ │ │ $ curl -X POST http://...        │ │
│ │   Call      │ │ │ -H "Content-Type: ..."           │ │
│ ├─────────────┤ │ │ -d '{...}'                       │ │
│ │ 🌐 REST API │ │ │                                  │ │
│ ├─────────────┤ │ │ [Copy] [Run]                     │ │
│ │ 🐍 Python   │ │ └──────────────────────────────────┘ │
│ │   SDK       │ │                                      │
│ ├─────────────┤ │ ┌──────────────────────────────────┐ │
│ │ 💾 Real     │ │ │ Endpoint: POST /v1/memories      │ │
│ │ Scenario    │ │ │ Status: 200 OK                   │ │
│ └─────────────┘ │ │ Use: Store patient preferences   │ │
│                 │ └──────────────────────────────────┘ │
│ Progress: ███░░ │                                      │
│                 │                                      │
└─────────────────┴───────────────────────────────────────┘
```

### Navigation Sidebar

- **Width**: 200-250px on desktop, collapsible on mobile
- **Style**: Dark background (slate-900)
- **Content**:
  - Skill/tutorial name (e.g., "MemMachine")
  - Subtitle (e.g., "Hands-On API Tutorial")
  - Section links with emojis (⚙️, 🚀, 🌐, 🐍, 💾)
  - Progress bar showing completion
- **Behavior**: Click to jump to section, smooth scroll

### Main Content Area

- **Width**: Responsive, max 900px
- **Padding**: 2-4rem vertical, 2rem horizontal
- **Background**: Dark theme (slate-950)
- **Text Color**: Light (slate-100/200)
- **Typography**:
  - Section heading: 24px bold, slate-100
  - Body text: 16px, slate-200, 1.6 line-height
  - Code text: 14px monospace, slate-100
  - Metadata: 12px, slate-400

### Code Block Component

**Critical Specifications**:

```
┌─────────────────────────────────────────┐
│ Python                    [Copy] [▶ Run] │
├─────────────────────────────────────────┤
│                                         │
│ import memmachine                       │
│ from memmachine import Memory            │
│                                         │
│ memory = Memory()                       │
│ memory.store(                           │
│     user_id="patient_123",              │
│     content="Symptom: headache"         │
│ )                                       │
│                                         │
└─────────────────────────────────────────┘
```

**Required Specifications**:
- ✅ **Background**: `#0f172a` (slate-950) - dark code theme
- ✅ **Text Color**: `#f1f5f9` (slate-100) - high contrast
- ✅ **LEFT-ALIGNED** (CRITICAL!) - Never center-aligned
- ✅ **Monospace Font**: Monaco, Menlo, or monospace fallback
- ✅ **Font Size**: 14px (0.875rem)
- ✅ **Line Height**: 1.5
- ✅ **Padding**: 16px (1rem) internal
- ✅ **Border**: 1px solid `#1e293b` (slate-800)
- ✅ **Border Radius**: 0.5rem
- ✅ **Syntax Highlighting**: Color-coded by language
- ✅ **Overflow**: Horizontal scroll (no wrapping)
- ✅ **Language Label**: Show in header (python, bash, json, etc.)
- ✅ **Copy Button**: Visible, clearly labeled
- ✅ **No Line Numbers**: (They break copy-paste UX)

**CSS Requirements**:
```css
.code-block {
  background-color: #0f172a;
  color: #f1f5f9;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #1e293b;
  font-family: Monaco, Menlo, monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  overflow-x: auto;
  text-align: left;  /* CRITICAL */
}

code {
  text-align: left;  /* CRITICAL */
  font-family: Monaco, Menlo, monospace;
}

pre {
  text-align: left;  /* CRITICAL */
}
```

### API Example Component

For API documentation with request/response:

```
┌──────────────────────────────────────┐
│ Add Memory              POST /memories │
├──────────────────────────────────────┤
│ [cURL] [Request] [Response]           │
├──────────────────────────────────────┤
│                                      │
│ $ curl -X POST \                     │
│   http://api.example.com/memories \  │
│   -H "Content-Type: application/json" │
│   -d '{                               │
│     "user_id": "patient_123",        │
│     "content": "Symptom: fever"      │
│   }'                                  │
│                                      │
│ [Copy]                               │
└──────────────────────────────────────┘
```

**Required Specifications**:
- ✅ **Tabs**: Switch between cURL, Request Body, Response
- ✅ **Endpoint Label**: Show HTTP method and path (POST /v1/memories)
- ✅ **Real Examples**: Exact from documentation, not simplified
- ✅ **Copy Buttons**: On each tab
- ✅ **Request/Response**: Show both input and output
- ✅ **Complete JSON**: No omissions (use ... for brevity only if doc shows it)

### Info Card Component

Show key details about each endpoint:

```
┌────────────────────────────────────┐
│ Endpoint: POST /v1/memories        │
│ HTTP Method: POST                  │
│ Auth: API Key (header)             │
│ Status: 200 OK                     │
│ Use Case: Store user interaction   │
└────────────────────────────────────┘
```

**Required Specifications**:
- ✅ Subtle background (darker than main, lighter than code)
- ✅ Key-value pairs for endpoint info
- ✅ Real HTTP method from docs
- ✅ Authentication requirements (if any)
- ✅ Success status code
- ✅ One-line use case description

---

## Interactive Features

### Copy-to-Clipboard Button

- **Trigger**: Click button
- **Visual Feedback**:
  - Button text: "Copy" → "✓ Copied!" (green) for 2 seconds → "Copy"
  - Highlight the code block briefly
- **Implementation**: Native Clipboard API
- **Requirement**: Works on all modern browsers

### Tabbed API Explorer

- **Tabs**: cURL | Request | Response
- **Behavior**: Click tab to switch views
- **Styling**: Clear indication of active tab
- **Copy**: Each tab has independent copy button

### Section Navigation

- **Sidebar Links**: Click to jump to section
- **Smooth Scroll**: Animate to section
- **Active Indicator**: Highlight current section
- **Mobile**: Collapsible drawer on small screens

### Progress Tracking

- **Progress Bar**: Visual bar showing completion %
- **Update Timing**: When user scrolls past section
- **Display**: Bar + percentage (e.g., "40% Complete")

---

## Visual Design

### Color Palette (Dark Theme)

```
Primary Background:   #0f172a (slate-950) - Code background
Secondary Background: #1e293b (slate-800) - Borders
Text Primary:         #f1f5f9 (slate-100) - Main text
Text Secondary:       #cbd5e1 (slate-300) - Secondary text
Accent:               #3b82f6 (blue-500)  - Links, highlights
Success:              #10b981 (green-500) - Checkmarks, success
Warning:              #f59e0b (amber-500) - Important notes
```

### Responsive Breakpoints

- **Mobile** (< 640px): Single column, sidebar collapsed, full-width code
- **Tablet** (640-1024px): Sidebar 150px, content adaptive
- **Desktop** (> 1024px): Sidebar 250px, content centered max 900px

---

## Content Flow Example

Here's how a complete endpoint should flow:

```
┌─────────────────────────────────────┐
│ Section Heading: Endpoint Name      │
│ One-line description of what it does │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Code Block (Tabs: cURL | Req | Res) │
│ [Copy button]                       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Info Card:                          │
│ Endpoint, Method, Auth, Status, Use │
└─────────────────────────────────────┘

(No "Learning Objective" box)
(No "Key Takeaways" box)
(No conceptual explanation)
```

---

## Quality Checklist (Before Finalizing)

### Code Quality
- [ ] All code blocks are copy-paste executable
- [ ] All endpoints are real (from documentation)
- [ ] Request/response JSON shows real structures, realistic data
- [ ] First section has users running code in <5 minutes
- [ ] No placeholder syntax (`<value>`, `{...}`, etc.)
- [ ] All SDKs show actual imports and real async/await if in docs

### Content Quality
- [ ] No "Learning Objectives" sections
- [ ] No "Key Takeaways" checklists
- [ ] No conceptual introductions (max 1 paragraph)
- [ ] Real-world scenarios show complete workflows (3-5 API calls)
- [ ] Each workflow step shows input/output and connections
- [ ] All code matches documentation exactly

### UI Quality
- [ ] Code blocks are LEFT-ALIGNED (not centered) - CRITICAL
- [ ] Dark theme applied throughout (slate-950 backgrounds)
- [ ] Copy buttons visible and functional on all code
- [ ] Syntax highlighting working for all languages
- [ ] Tabs working for API examples
- [ ] Navigation links functional
- [ ] Responsive design works on mobile/tablet/desktop
- [ ] No broken links or 404 references
- [ ] Progress bar displays and updates

### Interactive Quality
- [ ] Copy-to-clipboard works in all browsers
- [ ] Section navigation jumps to correct location
- [ ] Tab switching works smoothly
- [ ] All buttons respond to clicks
- [ ] No console errors in dev tools
- [ ] Performance acceptable (< 2s load time)

### Accessibility
- [ ] Text contrast > 4.5:1 (dark theme)
- [ ] Keyboard navigation works (Tab key)
- [ ] Semantic HTML throughout
- [ ] Color not only indicator of information
- [ ] Code blocks readable without JavaScript

---

## Examples of What Works (Code-First)

### ✅ Good Section Title
```
⚙️ Setup & Install
🚀 First API Call
🌐 REST API (All Endpoints)
🐍 Python SDK Examples
💾 Real Scenario: Healthcare Bot
```

### ✅ Good Code Block (Copy-Paste Ready)
```bash
curl -X POST http://127.0.0.1:8080/v1/memories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "user_id": "patient_123",
    "interaction_type": "symptom_report",
    "content": "Patient reported headache and fatigue"
  }'
```
(Exact from documentation, immediately runnable)

### ✅ Good API Example (Tabs)
```
[cURL Tab] - Full curl command, copy-paste ready
[Request Tab] - Complete JSON, all fields
[Response Tab] - Real response from docs, shows what you'll get
```

### ✅ Good Real-World Workflow
```
STEP 1: Store Symptom
  Command: curl POST /memories with symptom data
  Response: memory_id, timestamp

STEP 2: Search Related
  Command: curl GET /search with memory_id
  Response: array of related memories

STEP 3: Generate Response
  Command: Use results in LLM prompt
  Result: Healthcare agent responds with relevant history
```

### ✅ Good Info Card
```
Endpoint: POST /v1/memories
HTTP Method: POST
Required Auth: API Key in header
Response: 200 OK with memory_id
Use: Store user interaction for later recall
```

---

## Examples of What Doesn't Work (Avoid!)

### ❌ Bad Section Title (Conceptual)
```
Learning About Setup
Understanding API Concepts
Key Concepts in REST
```

### ❌ Bad Code Block (Placeholder/Simplified)
```
memory = Memory()  # Simplified example
memory.store({"data": "..."})  # Use actual field names!
curl -X POST <endpoint> -d '<json>'  # Needs actual endpoint and JSON
```

### ❌ Bad Learning Objective Box
```
After this section, you'll understand:
- What an API endpoint is
- How request/response works
- How to use the REST API
```

### ❌ Bad "Key Takeaways"
```
☐ Concept 1: You learned what memory storage is
☐ Concept 2: How the API works
☐ Concept 3: When to use memories
```

### ❌ Bad Workflow (Isolated Endpoints)
```
POST /v1/memories with data
GET /v1/memories/id
DELETE /v1/memories/id
[Each shown separately, no connection shown]
```

---

## Maintenance & Updates

### When to Update Tutorial
1. **API changes** - New endpoints, response structure changes
2. **Code examples outdated** - Different SDKs, deprecated features
3. **New versions released** - Major version updates
4. **Real-world feedback** - "This curl doesn't work", "Missing endpoint"

### Update Process
1. Verify changes in updated documentation
2. Test all curl commands and SDK code
3. Update affected sections
4. Verify code still matches documentation exactly
5. Test workflow walkthroughs end-to-end
6. Commit with clear change notes

---

## Version Control

**Document Version**: 2.0 (Code-First)
**Last Updated**: October 2025
**Status**: ✅ Approved for Production

---

## Next Steps

This document serves as the **definitive specification** for creating code-first documentation tutorials.

- **For Users**: Follow these requirements when requesting tutorials
- **For Developers**: Implement tutorials matching these specs
- **For QA**: Validate against this checklist before release

---

*End of Code-First UI & Content Requirements*
