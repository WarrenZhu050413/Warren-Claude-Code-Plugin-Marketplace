# Interactive Components Library

**Purpose**: Copy-paste interactive HTML/CSS/JS components for building rich "Interactive Primary Source Artifacts" without React.

**Compatibility**: Works with both `base-template.html` and `base-template-tailwind.html`.

---

## Table of Contents

1. [Tabs Component](#tabs-component)
2. [Modal/Dialog](#modal-dialog)
3. [Toast Notifications](#toast-notifications)
4. [Data Table with Sorting](#data-table-with-sorting)
5. [Progress Indicator](#progress-indicator)
6. [Accordion (Enhanced)](#accordion-enhanced)
7. [Tooltip](#tooltip)
8. [Search Filter](#search-filter)
9. [Toggle Switch](#toggle-switch)
10. [Dropdown Menu](#dropdown-menu)

---

## Tabs Component

**Use Case**: Organize related content in multiple views without page navigation.

### HTML

```html
<div class="tabs-container" data-tabs>
    <!-- Tab Navigation -->
    <div class="tab-list" role="tablist">
        <button class="tab-button active" role="tab" aria-selected="true" aria-controls="tab1" data-tab="tab1">
            Tab 1
        </button>
        <button class="tab-button" role="tab" aria-selected="false" aria-controls="tab2" data-tab="tab2">
            Tab 2
        </button>
        <button class="tab-button" role="tab" aria-selected="false" aria-controls="tab3" data-tab="tab3">
            Tab 3
        </button>
    </div>

    <!-- Tab Panels -->
    <div class="tab-panel active" id="tab1" role="tabpanel">
        <h3>Tab 1 Content</h3>
        <p>This is the content for the first tab.</p>
    </div>

    <div class="tab-panel" id="tab2" role="tabpanel" hidden>
        <h3>Tab 2 Content</h3>
        <p>This is the content for the second tab.</p>
    </div>

    <div class="tab-panel" id="tab3" role="tabpanel" hidden>
        <h3>Tab 3 Content</h3>
        <p>This is the content for the third tab.</p>
    </div>
</div>
```

### CSS

```css
.tabs-container {
    margin: 12px 0;
}

.tab-list {
    display: flex;
    gap: 2px;
    border-bottom: 2px solid var(--chinese-red);
    margin-bottom: 8px;
}

.tab-button {
    background: rgba(139, 0, 0, 0.05);
    border: none;
    padding: 6px 12px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    color: var(--level-2);
    transition: all 0.2s ease;
    border-top: 2px solid transparent;
}

.tab-button:hover {
    background: rgba(139, 0, 0, 0.1);
}

.tab-button.active {
    background: var(--chinese-red);
    color: white;
    border-top-color: var(--chinese-gold);
    font-weight: 700;
}

.tab-panel {
    padding: 12px;
    background: var(--section-background);
    border: 1px solid var(--border-color-light);
}

.tab-panel[hidden] {
    display: none;
}
```

### JavaScript

```javascript
document.querySelectorAll('[data-tabs]').forEach(container => {
    const buttons = container.querySelectorAll('.tab-button');
    const panels = container.querySelectorAll('.tab-panel');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.dataset.tab;

            // Update buttons
            buttons.forEach(btn => {
                btn.classList.remove('active');
                btn.setAttribute('aria-selected', 'false');
            });
            button.classList.add('active');
            button.setAttribute('aria-selected', 'true');

            // Update panels
            panels.forEach(panel => {
                panel.classList.remove('active');
                panel.setAttribute('hidden', '');
            });
            const targetPanel = container.querySelector(`#${targetId}`);
            targetPanel.classList.add('active');
            targetPanel.removeAttribute('hidden');
        });
    });
});
```

---

## Modal/Dialog

**Use Case**: Display detailed information or confirmations without leaving the page.

### HTML

```html
<!-- Trigger Button -->
<button class="modal-trigger" data-modal="example-modal">
    Open Modal
</button>

<!-- Modal -->
<div class="modal" id="example-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
    <div class="modal-backdrop"></div>
    <div class="modal-content">
        <div class="modal-header">
            <h2 id="modal-title">Modal Title</h2>
            <button class="modal-close" aria-label="Close modal">&times;</button>
        </div>
        <div class="modal-body">
            <p>Modal content goes here. This can contain any HTML.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
                <li>Item 3</li>
            </ul>
        </div>
        <div class="modal-footer">
            <button class="modal-close">Close</button>
            <button class="button">Confirm</button>
        </div>
    </div>
</div>
```

### CSS

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

.modal.active {
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(2px);
}

.modal-content {
    position: relative;
    background: var(--card-background);
    border: 2px solid var(--chinese-red);
    border-radius: 4px;
    max-width: 600px;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    z-index: 10000;
}

.modal-header {
    padding: 12px 16px;
    border-bottom: 2px solid var(--chinese-red);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(139, 0, 0, 0.05);
}

.modal-header h2 {
    margin: 0;
    font-size: 18px;
}

.modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: var(--chinese-red);
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-close:hover {
    background: rgba(139, 0, 0, 0.1);
    border-radius: 50%;
}

.modal-body {
    padding: 16px;
}

.modal-footer {
    padding: 12px 16px;
    border-top: 1px solid var(--border-color-light);
    display: flex;
    justify-content: flex-end;
    gap: 8px;
}
```

### JavaScript

```javascript
document.querySelectorAll('.modal-trigger').forEach(trigger => {
    trigger.addEventListener('click', () => {
        const modalId = trigger.dataset.modal;
        const modal = document.getElementById(modalId);
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    });
});

document.querySelectorAll('.modal').forEach(modal => {
    const closeButtons = modal.querySelectorAll('.modal-close');
    const backdrop = modal.querySelector('.modal-backdrop');

    closeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        });
    });

    backdrop.addEventListener('click', () => {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    });
});

// ESC key to close
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
});
```

---

## Toast Notifications

**Use Case**: Provide user feedback for actions (success, error, warning).

### HTML

```html
<!-- Toast Container (add to body) -->
<div id="toast-container" class="toast-container"></div>

<!-- Trigger Examples -->
<button onclick="showToast('Success message!', 'success')">Show Success</button>
<button onclick="showToast('Error occurred!', 'error')">Show Error</button>
<button onclick="showToast('Warning message!', 'warning')">Show Warning</button>
```

### CSS

```css
.toast-container {
    position: fixed;
    top: 16px;
    right: 16px;
    z-index: 10001;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.toast {
    background: var(--card-background);
    border: 2px solid var(--border-color-medium);
    border-radius: 4px;
    padding: 12px 16px;
    min-width: 250px;
    max-width: 400px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    display: flex;
    align-items: center;
    gap: 12px;
    animation: slideIn 0.3s ease-out;
}

.toast.success {
    border-color: var(--jade-green);
}

.toast.error {
    border-color: var(--chinese-red);
}

.toast.warning {
    border-color: var(--chinese-gold);
}

.toast-icon {
    font-size: 20px;
    flex-shrink: 0;
}

.toast.success .toast-icon {
    color: var(--jade-green);
}

.toast.error .toast-icon {
    color: var(--chinese-red);
}

.toast.warning .toast-icon {
    color: var(--chinese-gold);
}

.toast-message {
    flex: 1;
    font-size: 13px;
}

.toast-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: var(--level-3);
    padding: 0;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOut {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}
```

### JavaScript

```javascript
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close">&times;</button>
    `;

    container.appendChild(toast);

    // Close button
    toast.querySelector('.toast-close').addEventListener('click', () => {
        removeToast(toast);
    });

    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => removeToast(toast), duration);
    }
}

function removeToast(toast) {
    toast.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => toast.remove(), 300);
}
```

---

## Data Table with Sorting

**Use Case**: Display tabular data with sortable columns.

### HTML

```html
<table class="sortable-table" data-sortable>
    <thead>
        <tr>
            <th data-sort="name">Name <span class="sort-arrow">↕</span></th>
            <th data-sort="age">Age <span class="sort-arrow">↕</span></th>
            <th data-sort="score">Score <span class="sort-arrow">↕</span></th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td data-value="Alice">Alice</td>
            <td data-value="25">25</td>
            <td data-value="95">95</td>
            <td><button>View</button></td>
        </tr>
        <tr>
            <td data-value="Bob">Bob</td>
            <td data-value="30">30</td>
            <td data-value="87">87</td>
            <td><button>View</button></td>
        </tr>
        <tr>
            <td data-value="Charlie">Charlie</td>
            <td data-value="22">22</td>
            <td data-value="92">92</td>
            <td><button>View</button></td>
        </tr>
    </tbody>
</table>
```

### CSS

```css
.sortable-table th[data-sort] {
    cursor: pointer;
    user-select: none;
    position: relative;
}

.sortable-table th[data-sort]:hover {
    background: rgba(139, 0, 0, 0.15);
}

.sort-arrow {
    font-size: 10px;
    margin-left: 4px;
    opacity: 0.5;
}

.sortable-table th[data-sort].asc .sort-arrow::after {
    content: ' ▲';
    opacity: 1;
}

.sortable-table th[data-sort].desc .sort-arrow::after {
    content: ' ▼';
    opacity: 1;
}
```

### JavaScript

```javascript
document.querySelectorAll('[data-sortable]').forEach(table => {
    const headers = table.querySelectorAll('th[data-sort]');
    const tbody = table.querySelector('tbody');

    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.sort;
            const isAsc = header.classList.contains('asc');

            // Clear all sort indicators
            headers.forEach(h => h.classList.remove('asc', 'desc'));

            // Set new sort direction
            header.classList.add(isAsc ? 'desc' : 'asc');

            // Sort rows
            const rows = Array.from(tbody.querySelectorAll('tr'));
            rows.sort((a, b) => {
                const aVal = a.querySelector(`td[data-value]`).dataset.value;
                const bVal = b.querySelector(`td[data-value]`).dataset.value;

                // Try numeric comparison first
                const aNum = parseFloat(aVal);
                const bNum = parseFloat(bVal);

                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAsc ? bNum - aNum : aNum - bNum;
                }

                // Fall back to string comparison
                return isAsc
                    ? bVal.localeCompare(aVal)
                    : aVal.localeCompare(bVal);
            });

            // Reorder DOM
            rows.forEach(row => tbody.appendChild(row));
        });
    });
});
```

---

## Progress Indicator

**Use Case**: Show completion status for multi-step processes.

### HTML

```html
<div class="progress-bar" data-progress>
    <div class="progress-fill" style="width: 0%"></div>
    <div class="progress-label">0%</div>
</div>

<button onclick="setProgress(document.querySelector('[data-progress]'), 75)">
    Set to 75%
</button>
```

### CSS

```css
.progress-bar {
    position: relative;
    width: 100%;
    height: 24px;
    background: rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color-medium);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--chinese-red), var(--chinese-gold));
    transition: width 0.4s ease;
}

.progress-label {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 11px;
    font-weight: 700;
    color: var(--level-1);
    text-shadow: 0 0 4px rgba(255, 255, 255, 0.8);
}
```

### JavaScript

```javascript
function setProgress(progressBar, percent) {
    const fill = progressBar.querySelector('.progress-fill');
    const label = progressBar.querySelector('.progress-label');

    const clampedPercent = Math.max(0, Math.min(100, percent));

    fill.style.width = `${clampedPercent}%`;
    label.textContent = `${clampedPercent}%`;
}

// Example: Animated progress
function animateProgress(progressBar, targetPercent, duration = 1000) {
    const startPercent = parseInt(progressBar.querySelector('.progress-fill').style.width) || 0;
    const startTime = Date.now();

    function update() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const currentPercent = startPercent + (targetPercent - startPercent) * progress;

        setProgress(progressBar, currentPercent);

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    update();
}
```

---

## Accordion (Enhanced)

**Use Case**: Same as existing collapsibles, but with nested support and icons.

### HTML

```html
<div class="accordion" data-accordion>
    <div class="accordion-item">
        <button class="accordion-header">
            <span class="accordion-icon">📁</span>
            <span>Section 1</span>
            <span class="accordion-arrow">▶</span>
        </button>
        <div class="accordion-content">
            <p>Content for section 1.</p>

            <!-- Nested accordion -->
            <div class="accordion-item">
                <button class="accordion-header">
                    <span class="accordion-icon">📄</span>
                    <span>Subsection 1.1</span>
                    <span class="accordion-arrow">▶</span>
                </button>
                <div class="accordion-content">
                    <p>Nested content.</p>
                </div>
            </div>
        </div>
    </div>

    <div class="accordion-item">
        <button class="accordion-header">
            <span class="accordion-icon">📁</span>
            <span>Section 2</span>
            <span class="accordion-arrow">▶</span>
        </button>
        <div class="accordion-content">
            <p>Content for section 2.</p>
        </div>
    </div>
</div>
```

### CSS

```css
.accordion {
    margin: 8px 0;
}

.accordion-item {
    margin: 4px 0;
}

.accordion-header {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: rgba(139, 0, 0, 0.05);
    border: none;
    border-left: 3px solid var(--chinese-gold);
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    text-align: left;
    transition: all 0.2s ease;
}

.accordion-header:hover {
    background: rgba(139, 0, 0, 0.1);
}

.accordion-icon {
    font-size: 16px;
}

.accordion-arrow {
    margin-left: auto;
    font-size: 10px;
    color: var(--chinese-red);
    transition: transform 0.3s ease;
}

.accordion-item.open .accordion-arrow {
    transform: rotate(90deg);
}

.accordion-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
    padding: 0 12px;
    margin-left: 12px;
}

.accordion-item.open .accordion-content {
    max-height: 5000px;
    padding: 12px;
}
```

### JavaScript

```javascript
document.querySelectorAll('[data-accordion]').forEach(accordion => {
    accordion.querySelectorAll('.accordion-header').forEach(header => {
        header.addEventListener('click', function(e) {
            e.stopPropagation();
            const item = this.closest('.accordion-item');
            item.classList.toggle('open');
        });
    });
});
```

---

## Tooltip

**Use Case**: Provide contextual help text on hover.

### HTML

```html
<span class="tooltip-trigger" data-tooltip="This is helpful information">
    Hover me
</span>
```

### CSS

```css
.tooltip-trigger {
    position: relative;
    cursor: help;
    border-bottom: 1px dotted var(--chinese-gold);
}

.tooltip-trigger::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-8px);
    padding: 6px 10px;
    background: var(--ink-black);
    color: white;
    font-size: 11px;
    line-height: 1.3;
    white-space: nowrap;
    border-radius: 4px;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease, transform 0.2s ease;
    z-index: 1000;
}

.tooltip-trigger::before {
    content: '';
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 4px solid transparent;
    border-top-color: var(--ink-black);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease;
    z-index: 1000;
}

.tooltip-trigger:hover::after,
.tooltip-trigger:hover::before {
    opacity: 1;
}

.tooltip-trigger:hover::after {
    transform: translateX(-50%) translateY(-12px);
}
```

---

## Search Filter

**Use Case**: Filter lists or tables based on user input.

### HTML

```html
<input
    type="search"
    class="search-filter"
    data-filter-target="#filterable-list li"
    placeholder="Search items..."
>

<ul id="filterable-list" class="dense-list">
    <li><strong>Apple:</strong> A fruit</li>
    <li><strong>Banana:</strong> Another fruit</li>
    <li><strong>Carrot:</strong> A vegetable</li>
    <li><strong>Date:</strong> A sweet fruit</li>
</ul>
```

### CSS

```css
.search-filter {
    width: 100%;
    padding: 8px 12px;
    font-size: 13px;
    border: 2px solid var(--border-color-medium);
    border-radius: 4px;
    margin-bottom: 8px;
    background: var(--card-background);
    color: var(--ink-black);
}

.search-filter:focus {
    outline: none;
    border-color: var(--chinese-red);
}

.filtered-hidden {
    display: none !important;
}
```

### JavaScript

```javascript
document.querySelectorAll('.search-filter').forEach(input => {
    const selector = input.dataset.filterTarget;
    const items = document.querySelectorAll(selector);

    input.addEventListener('input', function() {
        const query = this.value.toLowerCase();

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(query)) {
                item.classList.remove('filtered-hidden');
            } else {
                item.classList.add('filtered-hidden');
            }
        });
    });
});
```

---

## Toggle Switch

**Use Case**: Binary on/off controls.

### HTML

```html
<label class="toggle-switch">
    <input type="checkbox" data-toggle>
    <span class="toggle-slider"></span>
    <span class="toggle-label">Enable Feature</span>
</label>
```

### CSS

```css
.toggle-switch {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    user-select: none;
}

.toggle-switch input[type="checkbox"] {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-slider {
    position: relative;
    width: 40px;
    height: 20px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 20px;
    transition: background 0.3s ease;
}

.toggle-slider::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 16px;
    height: 16px;
    background: white;
    border-radius: 50%;
    transition: transform 0.3s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.toggle-switch input:checked + .toggle-slider {
    background: var(--jade-green);
}

.toggle-switch input:checked + .toggle-slider::after {
    transform: translateX(20px);
}

.toggle-label {
    font-size: 13px;
    font-weight: 500;
}
```

---

## Dropdown Menu

**Use Case**: Contextual actions or navigation.

### HTML

```html
<div class="dropdown" data-dropdown>
    <button class="dropdown-trigger">
        Actions ▼
    </button>
    <div class="dropdown-menu">
        <a href="#" class="dropdown-item">Edit</a>
        <a href="#" class="dropdown-item">Duplicate</a>
        <div class="dropdown-divider"></div>
        <a href="#" class="dropdown-item danger">Delete</a>
    </div>
</div>
```

### CSS

```css
.dropdown {
    position: relative;
    display: inline-block;
}

.dropdown-trigger {
    /* Uses existing button styles */
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    margin-top: 4px;
    background: var(--card-background);
    border: 2px solid var(--chinese-red);
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    min-width: 150px;
    z-index: 1000;
    display: none;
}

.dropdown.open .dropdown-menu {
    display: block;
}

.dropdown-item {
    display: block;
    padding: 8px 12px;
    font-size: 13px;
    color: var(--level-2);
    text-decoration: none;
    transition: background 0.2s ease;
}

.dropdown-item:hover {
    background: rgba(139, 0, 0, 0.1);
}

.dropdown-item.danger {
    color: var(--chinese-red);
    font-weight: 600;
}

.dropdown-divider {
    height: 1px;
    background: var(--border-color-light);
    margin: 4px 0;
}
```

### JavaScript

```javascript
document.querySelectorAll('[data-dropdown]').forEach(dropdown => {
    const trigger = dropdown.querySelector('.dropdown-trigger');

    trigger.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdown.classList.toggle('open');
    });

    // Close when clicking outside
    document.addEventListener('click', () => {
        dropdown.classList.remove('open');
    });
});
```

---

## Usage Guide

### Integration Steps

1. **Add HTML**: Copy the component HTML to your template
2. **Add CSS**: Paste the CSS into the `<style>` section or external stylesheet
3. **Add JavaScript**: Include the JS in your `<script>` section or external file
4. **Customize**: Adjust colors, sizes, and behavior to match your needs

### Best Practices

- **Progressive Enhancement**: Components work without JavaScript where possible
- **Accessibility**: All components include ARIA attributes
- **Responsive**: Components adapt to different screen sizes
- **Themeable**: Components use CSS variables for easy customization
- **Lightweight**: Pure HTML/CSS/JS, no dependencies

### Combining Components

You can nest and combine components:

```html
<!-- Modal with tabs -->
<div class="modal" id="tabbed-modal">
    <div class="modal-content">
        <div class="tabs-container" data-tabs>
            <!-- Tabs inside modal -->
        </div>
    </div>
</div>

<!-- Collapsible with table -->
<div class="collapsible">
    <div class="collapsible-header">Data Table</div>
    <div class="collapsible-content">
        <table class="sortable-table" data-sortable>
            <!-- Sortable table inside collapsible -->
        </table>
    </div>
</div>
```

---

**Last Updated**: 2025-10-21
**Compatibility**: Base Template v3.0+
