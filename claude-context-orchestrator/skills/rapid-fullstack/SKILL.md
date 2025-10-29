# Rapid Full-Stack Prototyping

Build working full-stack web apps quickly (1-4 hours). Design first, code second, test third.

## When to Use
- User says "WEBAPP", "PROTOTYPE", "full-stack app", or "build a web application"
- Need both backend API + frontend UI
- Want speed + quality

## What You'll Build
- **Stack**: React + Vite + RESTful API (FastAPI/Express) + SQLite
- **Timeline**: 1-4 hours from idea to working app
- **Output**: Polished, functional prototype with keyboard shortcuts and clean UI

## The 3-Step Process

### Step 1: Design (5-10 min)
Create a text-based design showing:

```
UI LAYOUT:
[Header with Logo, Nav, Actions]
[Main Content - Left Sidebar | Center Panel | Right Info]
[Footer with Status]

USER INTERACTIONS:
1. Click "New" → Opens editor
2. Type text → Updates state
3. Press ⌘S → Saves via API
4. Click "History" → Opens panel

DATA MODELS:
- Item: {id, content, created_at}
- Revision: {id, item_id, content, timestamp}

API ENDPOINTS:
GET  /api/items          → List all
POST /api/items          → Create new
GET  /api/items/:id      → Get one
PUT  /api/items/:id      → Update
GET  /api/history/:id    → Get revisions
```

### Step 2: Get Approval (30 sec)
Show the design → User says "looks good" → Start coding

### Step 3: Build (1-3 hours)
Use this stack (don't ask, just use):
- **Frontend**: React + Vite
- **Backend**: FastAPI (Python) or Express (Node)
- **Database**: SQLite
- **State**: useState + useEffect

Build in order:
1. Backend skeleton (30 min)
2. Core features (1-2 hours)
3. Polish + keyboard shortcuts (30 min)
4. Test with WEBTEST

---

## Rules for Claude

✅ **DO:**
- Design mock UI before any code
- Use React + RESTful API (default)
- Start coding immediately after approval
- Add keyboard shortcuts (⌘S, ⌘/, etc.)

❌ **DON'T:**
- Ask user to choose frameworks
- Skip the design phase
- Spend 30+ min researching simple features
- Build custom solutions for standard problems

## Core Principles

1. **Design Before Code** - Mock UI + interactions first, then build
2. **Use What You Know** - Familiar tools > "perfect" tools you don't know
3. **Single Source of Truth** - One state for each piece of data, sync explicitly
4. **Right Tool for Job** - Fighting a component's design? Wrong component
5. **Test Early** - Automated tests + real user feedback before launch

## Default Stack (Use This)

```
Frontend:  React + Vite
Backend:   FastAPI (Python) or Express (Node)
Database:  SQLite
State:     useState + useEffect
Styling:   Vanilla CSS
```

**Why?** Fast setup, familiar patterns, good docs, zero config database.

**When to deviate:**
- User explicitly requests different stack → use their choice
- User needs SEO/SSR → use Next.js instead of Vite
- User says "no code" → suggest Bubble/Retool (explain trade-offs)

## Choosing Libraries

**When to add a library:**
- ✅ Would take > 1 hour to build from scratch
- ✅ Well-maintained (updated in last 6 months)
- ✅ You need > 30% of its features

**When to build it yourself:**
- ✅ Can be done in < 30 lines of code
- ✅ Only need 10% of library features
- ✅ Fighting the library's design

**Quick research (spend max 15 min):**
```bash
# 1. Search
WebSearch: "best [feature] library react 2025"

# 2. Check npm
npm info [package-name]
# Look at: downloads/week, last publish, dependencies count

# 3. Test
# Try basic example - works in 15 min? Keep it. Doesn't? Try next option.
```

**Examples:**
```javascript
// ❌ Don't need library for:
fetch()              // axios is overkill
<textarea />         // don't force WYSIWYG when plain text works
Intl.DateTimeFormat  // moment.js is heavy

// ✅ Use library for:
<MarkdownEditor />   // complex parsing + preview
<DiffViewer />       // diff algorithm is non-trivial
<CodeEditor />       // syntax highlighting + LSP
```

## Project Structure

```
project/
├── backend/
│   ├── server.py          # FastAPI app
│   └── requirements.txt   # Python deps
├── frontend/
│   ├── src/
│   │   ├── App.jsx       # Main component
│   │   ├── App.css       # Styles
│   │   └── main.jsx      # Entry point
│   ├── package.json
│   └── vite.config.js    # Vite config with proxy
├── launcher-script        # CLI to start both servers
├── install.sh            # Setup script
└── README.md             # Documentation
```

## Build Workflow

### Phase 0: Design (15-30 min)
See "The 3-Step Process" above - create text-based design with UI layout, interactions, data models, and API endpoints. Show to user → get approval → start coding.

### Phase 1: Backend + Frontend Skeleton (30 min)

**Backend:**
```python
# Define models → Create CRUD endpoints → Test with curl
# FastAPI example:
@app.get("/api/items")
async def list_items(): ...

@app.post("/api/items")
async def create_item(item: Item): ...
```

**Frontend:**
```bash
npm create vite@latest my-app -- --template react
cd my-app && npm install
# Configure vite.config.js proxy to backend
# Test connection with /api/health endpoint
```

### Phase 2: Core Features (1-2 hours)
- Build one feature at a time
- useState for local state, useEffect for side effects
- Single source of truth (one canonical state, sync others from it)
- Test each feature before moving to next

### Phase 3: Polish (30 min)
```javascript
// Add keyboard shortcuts
useEffect(() => {
  const handleKeyDown = (e) => {
    if (e.metaKey) {
      if (e.key === 's') { e.preventDefault(); save(); }
      if (e.key === '/') { e.preventDefault(); showHelp(); }
    }
  };
  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, []);
```

- Add help modal (⌘/)
- Add button active states
- Add status feedback ("✓ Saved")
- Add tooltips with keyboard shortcuts

### Phase 4: Test (Use WEBTEST)
```bash
# Run automated tests
WEBTEST  # Triggers testing-webapps skill

# Manual checks:
# - All buttons work
# - Data persists after save
# - No console errors
# - Keyboard shortcuts work
```

## Common Mistakes

### 1. Multiple Sources of Truth
```javascript
// ❌ Bad: Three states for same data
const [editorContent, setEditorContent] = useState('');
const [diffContent, setDiffContent] = useState('');
const [previewContent, setPreviewContent] = useState('');

// ✅ Good: One source, sync to views
const [content, setContent] = useState('');
useEffect(() => {
  editorRef.current?.setContent(content);
}, [viewMode, content]);
```

### 2. Fighting Component Design
```javascript
// ❌ Bad: Complex CSS to hide UI elements
.editor .toolbar { display: none !important; }
.editor .tabs { visibility: hidden !important; }

// ✅ Good: Use simpler component
<textarea value={content} onChange={e => setContent(e.target.value)} />
```

### 3. Hardcoded Config
```javascript
// ❌ Bad
target: 'http://127.0.0.1:8765'

// ✅ Good
const port = process.env.VITE_BACKEND_PORT || '8765';
target: `http://127.0.0.1:${port}`
```

### 4. CORS Issues
```python
# ✅ FastAPI CORS setup
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Code Patterns

### Button States
```css
.btn { background: #007bff; transition: 0.2s; }
.btn:hover { background: #0056b3; }
.btn.active { background: #28a745; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
```

### Status Feedback
```javascript
const save = async () => {
  try {
    await saveToBackend();
    setStatus('✓ Saved');
    setTimeout(() => setStatus(''), 2000);
  } catch (error) {
    setStatus('❌ Error');
  }
};
```

### Help Modal
```jsx
{helpOpen && (
  <div className="modal" onClick={() => setHelpOpen(false)}>
    <div className="content" onClick={e => e.stopPropagation()}>
      <h3>⌨️ Shortcuts</h3>
      <kbd>⌘ S</kbd> Save
      <kbd>⌘ /</kbd> Help
    </div>
  </div>
)}
```

## Launcher Script

Create a simple script to start both servers:

```python
#!/usr/bin/env python3
import subprocess, webbrowser, time

# Start backend
backend = subprocess.Popen(
    ["uvicorn", "server:app", "--port", "8000"],
    cwd="./backend"
)

# Start frontend
frontend = subprocess.Popen(
    ["npm", "run", "dev"],
    cwd="./frontend"
)

time.sleep(2)
webbrowser.open("http://localhost:5173")

try:
    backend.wait()
except KeyboardInterrupt:
    backend.terminate()
    frontend.terminate()
```

Make executable: `chmod +x launcher`

## Quick Reference

### Testing Checklist
```bash
# Automated
WEBTEST  # Use testing-webapps skill

# Manual
- [ ] All buttons work
- [ ] Keyboard shortcuts (⌘S, ⌘/)
- [ ] Data persists
- [ ] No console errors
```

### When to Add a Feature
1. Solves real problem? ✓
2. Can be done simply? ✓
3. Fits core purpose? ✓

If any = no → defer it

### When to Refactor
- Code duplicated 3+ times
- Fighting component design
- Adding features getting harder

### View Modes Pattern
```jsx
const [viewMode, setViewMode] = useState('edit');
const [content, setContent] = useState('');

{viewMode === 'edit' && <Editor value={content} onChange={setContent} />}
{viewMode === 'diff' && <DiffView content={content} previous={prev} />}
{viewMode === 'preview' && <Preview content={content} />}
```

### Debugging
1. Console errors (browser + terminal)
2. Network tab (API responses)
3. React DevTools (state flow)
4. Use right component for the job?

### Success Criteria
- ✅ Core features work end-to-end
- ✅ Keyboard shortcuts (⌘S, ⌘/)
- ✅ No console errors
- ✅ Data persists
- ✅ Clean UI, no glitches

## Real Example: mdedit (3 hours total)

**Stack**: React + Vite + FastAPI + SQLite
**Features**: 4 view modes, version history, visual diff, keyboard shortcuts

**Key Decisions** (38 min research):
- FastAPI > Flask (type hints, async)
- SQLite > Postgres (zero config)
- Toast UI Editor for rich editing, but **textarea for diff mode** (fighting component = wrong tool)
- react-diff-viewer (GitHub-style, simple)
- marked for preview (lightweight)

**Lesson**: Don't fight components with CSS. Use simpler alternatives when needed.

---

## Key Reminders

**Design → Code → Test**
- Mock UI + interactions first
- Use defaults (React + RESTful)
- WEBTEST when done

**Red Flags:**
- Complex CSS hiding → wrong component
- Multiple states for same data → refactor
- Fighting a library → use different one
- > 30 min on one bug → rethink approach

**Best Prototypes Are:**
1. Fast (1-4 hours)
2. Simple (easy to change)
3. Polished (shortcuts + help)
4. Tested (no errors)

