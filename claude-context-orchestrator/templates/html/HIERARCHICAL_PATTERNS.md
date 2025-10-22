# Hierarchical Information Organization Patterns

This document outlines various patterns for organizing large amounts of information in HTML templates, moving beyond simple continuous scrolling.

---

## Pattern 1: Sidebar Navigation (Implemented in v2)

**Best for**: Long-form content with clear sections and subsections

### Features:
- **Fixed sidebar** with hierarchical navigation
- **Smooth scrolling** to sections
- **Active section highlighting** using Intersection Observer
- **Collapsible subsections** for better organization
- **Mobile responsive** with hamburger menu
- **Scroll-to-top button** for easy navigation

### Structure:
```
Layout
├── Sidebar (280px, fixed)
│   ├── Section 1
│   │   ├── Subsection 1a
│   │   └── Subsection 1b
│   └── Section 2
└── Main Content (scrollable)
    ├── Section 1 content
    └── Section 2 content
```

### Key Code:
```javascript
// Smooth scroll + active highlighting
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        const section = document.getElementById(link.dataset.section);
        section.scrollIntoView({ behavior: 'smooth' });
    });
});

// Intersection Observer for active section
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            updateActiveNavLink(entry.target.id);
        }
    });
});
```

### CSS Variables:
```css
:root {
    --sidebar-width: 280px;
}

.sidebar {
    width: var(--sidebar-width);
    position: fixed;
    height: 100vh;
    overflow-y: auto;
}

.main-content {
    margin-left: var(--sidebar-width);
}
```

---

## Pattern 2: Collapsible Sections (Implemented in v2)

**Best for**: Dense information that users may want to selectively explore

### Features:
- **Accordion-style** collapsible sections
- **Smooth expand/collapse** transitions
- **Visual indicators** (arrows that rotate)
- **Default state** (open or closed)

### HTML Structure:
```html
<div class="collapsible open">
    <div class="collapsible-header">
        <div class="collapsible-title">Section Title</div>
        <div class="collapsible-icon">▼</div>
    </div>
    <div class="collapsible-content">
        <div class="collapsible-inner">
            <!-- Content here -->
        </div>
    </div>
</div>
```

### CSS:
```css
.collapsible-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.collapsible.open .collapsible-content {
    max-height: 5000px;
    padding: 1.5rem;
}

.collapsible-icon {
    transition: transform 0.3s;
}

.collapsible.open .collapsible-icon {
    transform: rotate(180deg);
}
```

### JavaScript:
```javascript
document.querySelectorAll('.collapsible-header').forEach(header => {
    header.addEventListener('click', function() {
        this.parentElement.classList.toggle('open');
    });
});
```

---

## Pattern 3: Multi-Tab Interface

**Best for**: Categorizing information into distinct, parallel topics

### Features:
- **Tab navigation** at section level
- **Persistent state** (optional, using localStorage)
- **Keyboard navigation** (arrow keys)
- **ARIA attributes** for accessibility

### HTML:
```html
<div class="tabs-container" data-tabs>
    <div class="tab-list" role="tablist">
        <button class="tab-button active" data-tab="tab1">Tab 1</button>
        <button class="tab-button" data-tab="tab2">Tab 2</button>
    </div>

    <div class="tab-panel active" id="tab1" role="tabpanel">
        Content 1
    </div>
    <div class="tab-panel" id="tab2" role="tabpanel">
        Content 2
    </div>
</div>
```

### Advanced: Nested Tabs
```html
<!-- Top-level tabs -->
<div class="tabs-container level-1">
    <div class="tab-panel active">
        <!-- Nested tabs within -->
        <div class="tabs-container level-2">
            <div class="tab-list">
                <button class="tab-button">Subtab 1</button>
                <button class="tab-button">Subtab 2</button>
            </div>
            ...
        </div>
    </div>
</div>
```

---

## Pattern 4: Table of Contents with Floating/Sticky TOC

**Best for**: Academic or documentation-style content

### Features:
- **Floating TOC** that follows scroll
- **Mini-map** showing current position
- **Click to jump** to sections
- **Progress indicator**

### HTML:
```html
<div class="floating-toc">
    <h3>Contents</h3>
    <ul>
        <li><a href="#section1" class="toc-link active">Section 1</a></li>
        <li><a href="#section2" class="toc-link">Section 2</a></li>
        <li class="indent">
            <a href="#section2a" class="toc-link">2.1 Subsection</a>
        </li>
    </ul>
    <div class="reading-progress">
        <div class="progress-bar" style="width: 25%"></div>
    </div>
</div>
```

### CSS:
```css
.floating-toc {
    position: fixed;
    top: 100px;
    right: 2rem;
    width: 220px;
    max-height: calc(100vh - 120px);
    overflow-y: auto;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
}

.toc-link.active {
    color: var(--accent);
    font-weight: 600;
}

.reading-progress {
    margin-top: 1rem;
    height: 4px;
    background: var(--muted);
    border-radius: 2px;
}

.progress-bar {
    height: 100%;
    background: var(--accent);
    transition: width 0.2s;
}
```

### JavaScript:
```javascript
// Update progress based on scroll
window.addEventListener('scroll', () => {
    const winScroll = document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight -
                   document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    document.querySelector('.progress-bar').style.width = scrolled + '%';
});
```

---

## Pattern 5: Split-Pane Layout

**Best for**: Code examples, API docs, or side-by-side comparisons

### Features:
- **Resizable divider** between panes
- **Synchronized scrolling** (optional)
- **Independent scrolling** (default)

### HTML:
```html
<div class="split-pane-container">
    <div class="pane pane-left">
        <h2>Explanation</h2>
        <p>Content here...</p>
    </div>

    <div class="divider" draggable="true"></div>

    <div class="pane pane-right">
        <h2>Code Example</h2>
        <pre><code>...</code></pre>
    </div>
</div>
```

### CSS:
```css
.split-pane-container {
    display: flex;
    height: 100vh;
    gap: 0;
}

.pane {
    flex: 1;
    overflow-y: auto;
    padding: 2rem;
}

.divider {
    width: 4px;
    background: var(--border);
    cursor: col-resize;
    transition: background 0.2s;
}

.divider:hover {
    background: var(--accent);
}
```

### JavaScript (Resizable):
```javascript
let isDragging = false;
const divider = document.querySelector('.divider');
const leftPane = document.querySelector('.pane-left');

divider.addEventListener('mousedown', () => isDragging = true);

document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const containerWidth = document.querySelector('.split-pane-container').offsetWidth;
    const leftWidth = (e.clientX / containerWidth) * 100;
    leftPane.style.flex = `0 0 ${leftWidth}%`;
});

document.addEventListener('mouseup', () => isDragging = false);
```

---

## Pattern 6: Card Grid with Filtering

**Best for**: Portfolio, gallery, or resource collections

### Features:
- **Masonry or grid layout**
- **Filter by category**
- **Search functionality**
- **Sort options**

### HTML:
```html
<div class="filters">
    <button class="filter-btn active" data-filter="all">All</button>
    <button class="filter-btn" data-filter="ancient">Ancient</button>
    <button class="filter-btn" data-filter="modern">Modern</button>
</div>

<div class="card-grid">
    <div class="card" data-category="ancient">
        <h3>Aristotle</h3>
        <p>...</p>
    </div>
    <div class="card" data-category="modern">
        <h3>Russell</h3>
        <p>...</p>
    </div>
</div>
```

### CSS:
```css
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.card {
    transition: opacity 0.3s, transform 0.3s;
}

.card.hidden {
    opacity: 0;
    transform: scale(0.8);
    pointer-events: none;
    position: absolute;
}
```

### JavaScript:
```javascript
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const filter = this.dataset.filter;
        const cards = document.querySelectorAll('.card');

        cards.forEach(card => {
            if (filter === 'all' || card.dataset.category === filter) {
                card.classList.remove('hidden');
            } else {
                card.classList.add('hidden');
            }
        });

        // Update active button
        document.querySelectorAll('.filter-btn').forEach(b =>
            b.classList.remove('active'));
        this.classList.add('active');
    });
});
```

---

## Pattern 7: Timeline/Stepper Navigation

**Best for**: Historical content, tutorials, step-by-step guides

### Features:
- **Visual timeline** with clickable nodes
- **Current step highlighting**
- **Previous/next navigation**
- **Progress indication**

### HTML:
```html
<div class="timeline-nav">
    <div class="timeline-step active" data-step="1">
        <div class="step-marker">1</div>
        <div class="step-label">Ancient</div>
    </div>
    <div class="timeline-connector"></div>
    <div class="timeline-step" data-step="2">
        <div class="step-marker">2</div>
        <div class="step-label">Medieval</div>
    </div>
    <div class="timeline-connector"></div>
    <div class="timeline-step" data-step="3">
        <div class="step-marker">3</div>
        <div class="step-label">Modern</div>
    </div>
</div>

<div class="timeline-content">
    <div class="step-content active" data-step="1">
        Ancient content...
    </div>
    <div class="step-content" data-step="2">
        Medieval content...
    </div>
    <div class="step-content" data-step="3">
        Modern content...
    </div>
</div>
```

### CSS:
```css
.timeline-nav {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 2rem 0;
}

.timeline-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
}

.step-marker {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--muted);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    transition: all 0.3s;
}

.timeline-step.active .step-marker {
    background: var(--accent);
    color: white;
    transform: scale(1.2);
}

.timeline-connector {
    width: 100px;
    height: 2px;
    background: var(--border);
}
```

---

## Pattern 8: Modal/Drawer System

**Best for**: Detailed information that doesn't fit inline

### Features:
- **Click to open modal** with full content
- **Side drawer** for supplementary info
- **Close on overlay click**
- **Keyboard shortcuts** (ESC to close)

### HTML:
```html
<!-- Trigger -->
<button class="open-modal" data-modal="philosopher-detail">
    Learn more about Aristotle
</button>

<!-- Modal -->
<div class="modal" id="philosopher-detail">
    <div class="modal-overlay"></div>
    <div class="modal-content">
        <button class="modal-close">&times;</button>
        <h2>Aristotle</h2>
        <p>Detailed content...</p>
    </div>
</div>
```

### CSS:
```css
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 9999;
}

.modal.open {
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
}

.modal-content {
    position: relative;
    background: var(--card);
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
    border-radius: 12px;
    padding: 2rem;
    z-index: 1;
}
```

### JavaScript:
```javascript
// Open modal
document.querySelectorAll('.open-modal').forEach(btn => {
    btn.addEventListener('click', function() {
        const modalId = this.dataset.modal;
        document.getElementById(modalId).classList.add('open');
    });
});

// Close on overlay or close button
document.querySelectorAll('.modal-overlay, .modal-close').forEach(el => {
    el.addEventListener('click', function() {
        this.closest('.modal').classList.remove('open');
    });
});

// Close on ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.open').forEach(modal =>
            modal.classList.remove('open'));
    }
});
```

---

## Choosing the Right Pattern

| Use Case | Recommended Pattern | Why |
|----------|---------------------|-----|
| Long-form article with clear sections | Sidebar Navigation + Collapsible | Easy navigation, reduces scrolling |
| Tutorial or guide | Timeline/Stepper | Shows progress, logical flow |
| API documentation | Split-Pane | Code alongside explanation |
| Academic paper | Floating TOC + Progress | Traditional structure, clear position |
| Resource collection | Card Grid + Filters | Visual browsing, easy filtering |
| Multi-topic content | Multi-Tab | Parallel organization |
| Dense reference material | Sidebar + Collapsible + Modal | Maximum organization flexibility |

---

## Combination Patterns

The most effective approach often **combines multiple patterns**:

### Example: Enhanced Documentation
```
Sidebar Navigation (main sections)
├── Section 1
│   └── Collapsible subsections
│       └── Modal for detailed examples
├── Section 2
└── Floating TOC (on right side)
```

### Example: Educational Content
```
Timeline/Stepper (top level)
├── Step 1: Ancient
│   ├── Tabs (Aristotle, Epicurus, Stoics)
│   └── Collapsible details
└── Step 2: Medieval
    └── Split-pane (text + diagrams)
```

---

## Implementation in v2 Template

The `example-complete-happiness-v2.html` implements:

✅ **Sidebar Navigation** - Fixed left sidebar with sections/subsections
✅ **Collapsible Sections** - All major content in expandable accordions
✅ **Smooth Scrolling** - Click nav links to jump to sections
✅ **Active Highlighting** - Current section highlighted in nav
✅ **Scroll-to-Top** - Button appears after scrolling
✅ **Mobile Responsive** - Hamburger menu on mobile
✅ **Intersection Observer** - Automatic active section detection

---

## Best Practices

1. **Progressive Disclosure**: Show overview first, details on demand
2. **Persistent Navigation**: Keep primary nav always accessible
3. **Visual Hierarchy**: Use size, color, spacing to indicate importance
4. **Keyboard Navigation**: Support arrow keys, tab, enter, escape
5. **State Management**: Remember user's position (scroll, open sections)
6. **Performance**: Lazy-load heavy content below fold
7. **Accessibility**: ARIA labels, semantic HTML, focus management
8. **Mobile-First**: Design for small screens, enhance for large

---

## Mermaid Diagram Flash Prevention

The v2 template fixes the Mermaid diagram flash issue by:

1. **Storing original content** before initialization:
```javascript
const mermaidContent = new Map();
document.querySelectorAll('.mermaid').forEach((el, i) => {
    mermaidContent.set(i, el.textContent);
});
```

2. **Re-rendering without page reload**:
```javascript
themeToggle.addEventListener('click', () => {
    // Update theme
    initMermaid(newTheme);

    // Restore original content
    mermaidElements.forEach((el, i) => {
        el.textContent = mermaidContent.get(i);
        el.removeAttribute('data-processed');
    });

    // Re-run Mermaid
    mermaid.run({ nodes: document.querySelectorAll('.mermaid') });
});
```

This prevents the flash by:
- Not reloading the entire page
- Quickly replacing SVG with original text
- Immediately re-rendering with new theme

---

## Audio Display Enhancement

Enhanced audio controls with:

```css
.audio-container {
    background: hsl(var(--card));
    border: 2px solid hsl(var(--accent) / 0.3); /* Clear border */
    border-radius: 12px;
    padding: 1.5rem;
}

.audio-label {
    font-weight: 600;
    color: hsl(var(--accent));
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.audio-label::before {
    content: '🔊'; /* Visual indicator */
    font-size: 1.2rem;
}

audio {
    width: 100%;
    height: 40px; /* Ensure minimum height */
}
```

Audio files can be generated using:
```bash
/tts "Your text here" --output ./audio/filename.wav
```

---

**Last Updated**: 2025-01-21
**Author**: Claude
**Template Version**: v2
