# Library Research Guide

Quick reference for researching and selecting libraries during prototyping.

## Search Strategy Flowchart

```
Need feature X?
    ↓
1. Can I build it in < 30 lines?
   → YES: Don't use library
   → NO: Continue to step 2
    ↓
2. Search for solutions
   - WebSearch: "best [feature] library [framework] 2025"
   - Exa Code: "[framework] [feature] implementation examples"
    ↓
3. Found 2-3 candidates?
   → Compare them (see criteria below)
    ↓
4. Test the top choice
   → Works in < 15 min? Use it
   → Too complex/broken? Try next option
    ↓
5. Still nothing good?
   → Build it yourself
   → Or simplify the requirement
```

## Evaluation Criteria

### Quick Check (2 min per library)
```bash
# For npm packages
npm info <package-name>

Look for:
✅ Last publish: < 6 months ago
✅ Weekly downloads: > 10k (for popular features)
✅ Dependencies: < 10 (fewer is better)
✅ License: MIT or Apache 2.0
✅ TypeScript: Built-in types or @types/ available

❌ Warning signs:
- Last publish > 1 year ago
- Many open issues, few closed
- "deprecated" in description
- Requires lots of peer dependencies
```

### Deep Check (5 min if quick check passes)
```bash
# Check GitHub
1. Stars: > 1k for common features
2. Issues:
   - Response rate (maintainer active?)
   - Closed/Open ratio (> 2:1 good)
3. Last commit: < 3 months ideal
4. Contributors: > 5 (not single-maintainer)
5. Examples/demos: Exist and work?
```

### Bundle Size Check
```
Visit: https://bundlephobia.com/package/<package-name>

Acceptable sizes for prototypes:
- Utilities: < 10kb
- UI components: < 50kb
- Full editors: < 500kb
- Anything else: Question if you need it
```

## Common Feature Searches

### Rich Text / Markdown Editor
```bash
# Search queries
"react markdown editor wysiwyg 2025"
"best markdown editor component [framework]"
"lightweight rich text editor [framework]"

# What to look for
- Live preview support
- Custom toolbar options
- Export/import formats
- Syntax highlighting

# Alternatives to consider
- Full WYSIWYG editor (heavy)
- Markdown editor with preview (medium)
- Plain textarea with preview (light)
- CodeMirror / Monaco (code-focused)
```

### Diff Viewer
```bash
# Search queries
"visual diff component [framework]"
"side by side diff viewer [framework]"
"git diff ui component"

# What to look for
- Split/unified view toggle
- Line highlighting
- Syntax highlighting
- Word-level diffs

# Fallback
- Use a diffing algorithm library
- Render with custom CSS
```

### State Management
```bash
# Search queries
"[framework] state management 2025"
"zustand vs redux vs context"
"when to use state management library"

# Decision tree
- Simple app (< 5 components) → useState/useReducer
- Medium app (5-20 components) → Context API or Zustand
- Complex app (20+ components) → Redux Toolkit or Recoil

# For prototypes: Start simple, add later if needed
```

### Form Handling
```bash
# Search queries
"[framework] form library 2025"
"react hook form vs formik"
"form validation library"

# Decision tree
- Simple forms (1-3 fields) → Vanilla HTML + state
- Medium forms (4-10 fields) → Controlled components
- Complex forms (10+ fields, validation) → React Hook Form / Formik

# For prototypes: Keep it vanilla, add library if > 10 fields
```

### Data Fetching
```bash
# Search queries
"[framework] data fetching library"
"react query vs swr vs apollo"
"best way to fetch data [framework]"

# Decision tree
- Simple REST API → fetch / axios
- Need caching/refetching → React Query / SWR
- GraphQL → Apollo Client / urql

# For prototypes: Start with fetch, add library if you need:
  - Automatic refetching
  - Cache management
  - Optimistic updates
```

### Styling
```bash
# Search queries
"[framework] css framework 2025"
"tailwind vs styled-components vs css modules"
"css-in-js vs css modules"

# Decision tree
- Prototype (speed matters) → Vanilla CSS or inline styles
- Need consistency → CSS Modules or Tailwind
- Component library → Styled Components / Emotion
- Design system → Material-UI / Ant Design

# For prototypes: Vanilla CSS first, add framework if needed
```

## Search Query Templates

### General Pattern
```
"best [feature-type] library for [framework] [year]"
"[specific-library] vs [alternative] comparison"
"[feature-type] implementation [framework] example"
"lightweight [feature-type] component [framework]"
```

### For Code Examples
Use exa-code search:
```
"[framework] [feature] implementation example"
"how to use [library-name] with [framework]"
"[feature] tutorial [framework]"
```

### For Comparisons
```
"[library-a] vs [library-b] [year]"
"[library-name] alternatives"
"[library-name] reddit" (real user opinions)
"[library-name] bundle size"
```

## Red Flags

### In Search Results
- Many "how to fix" articles
- Lots of open issues on GitHub
- Tutorials only from > 2 years ago
- No clear documentation site
- Only works with specific versions

### In Documentation
- No getting started guide
- No examples
- Assumes lots of prior knowledge
- Inconsistent API
- Breaking changes in minor versions

### In Issues/Community
- Maintainer unresponsive
- Many unanswered questions
- Lots of "this doesn't work" issues
- People asking for alternatives
- Security issues ignored

## Decision Making

### Use native/simple if:
```javascript
// ❌ Don't import library for
- Date formatting (Intl.DateTimeFormat)
- HTTP requests (fetch API)
- Simple state (useState/useReducer)
- Basic validation (HTML5 + regex)
- Simple animations (CSS transitions)
```

### Use library if:
```javascript
// ✅ Consider library for
- Complex parsing (markdown, CSV)
- Diffing algorithms
- Rich text editing
- Code highlighting
- Complex animations
- Data visualization
```

## Research Time Budgets

- **Quick feature** (< 30 min to build): 0 min research → build it
- **Medium feature** (30 min - 2 hours): 10 min research → decide
- **Complex feature** (> 2 hours): 20 min research → pick best tool

If research takes > 20 minutes, you're overthinking it:
- Pick the most popular option
- Try it for 15 minutes
- If it doesn't work, try alternative

## Example Research Session

**Scenario**: Need visual diff for markdown editor

**Step 1: Initial search** (3 min)
```bash
WebSearch: "react visual diff component side by side"
Results:
- react-diff-viewer (6.2k stars)
- react-diff-view (3.1k stars)
- monaco-diff-editor (part of Monaco)
```

**Step 2: Quick comparison** (5 min)
```bash
npm info react-diff-viewer
# Last publish: 8 months ago (okay)
# Downloads: 45k/week (popular)
# Dependencies: 4 (good)

npm info react-diff-view
# Last publish: 1 year ago (warning)
# Downloads: 8k/week (less popular)
# Dependencies: 3 (good)

Monaco: Heavy (500kb+), overkill for simple diff
```

**Step 3: Check examples** (2 min)
- react-diff-viewer: Has live demo, looks good
- react-diff-view: Examples look more complex

**Decision**: Try react-diff-viewer first (most popular, good docs)

**Step 4: Test** (10 min)
```bash
npm install react-diff-viewer
# Create test component
# Works in 10 min → Keep it
```

**Total time**: 20 minutes from "need diff viewer" to "working implementation"

## Remember

> "Perfect is the enemy of good. Pick something reasonable and move forward. You can always swap libraries later if needed."

The goal is **working software**, not the perfect tech stack. Spend 80% of time building, 20% researching.
