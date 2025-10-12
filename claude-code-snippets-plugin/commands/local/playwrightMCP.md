---
SNIPPET_NAME: playwrightMCP
ANNOUNCE_USAGE: true
---

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: playwrightMCP

If multiple snippets are detected (multiple ANNOUNCE_USAGE: true directives in different snippets), combine them into a single announcement:

📎 **Active Contexts**: snippet1, snippet2, snippet3

---

**VERIFICATION_HASH:** `6f2a46bb23bb36ab`

---
SNIPPET_NAME: playwrightMCP
ANNOUNCE_USAGE: true
---

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: playwrightMCP

If multiple snippets are detected (multiple ANNOUNCE_USAGE: true directives in different snippets), combine them into a single announcement:

📎 **Active Contexts**: snippet1, snippet2, snippet3

---

# Playwright MCP Server - Optimal Usage Guide

**VERIFICATION_HASH:** \`playwright-mcp-v1-a8f3d9c2\`

This guide provides comprehensive best practices for using Playwright MCP (Model Context Protocol) server for browser automation with AI assistants.

---

## Overview

Playwright MCP provides **structured accessibility snapshots** for browser automation, enabling AI to interact with web pages WITHOUT vision models. It's fast, deterministic, and LLM-friendly.

**Key Advantages:**
- 🚀 Fast & lightweight (no visual recognition needed)
- 🎯 Deterministic (structured accessibility data)
- 🌐 Cross-browser (Chromium, Firefox, WebKit)
- 🔧 Extensive tool set (20+ automation functions)

---

## Core MCP Tools Reference

### Navigation & Page Management

**\`browser_navigate\`** - Navigate to URL
\`\`\`typescript
await browser_navigate({ url: "https://example.com" })
\`\`\`

**\`browser_navigate_back\`** - Go back to previous page
\`\`\`typescript
await browser_navigate_back()
\`\`\`

**\`browser_close\`** - Close current page
\`\`\`typescript
await browser_close()
\`\`\`

**\`browser_tabs\`** - Manage browser tabs
\`\`\`typescript
// List tabs
await browser_tabs({ action: "list" })

// Create new tab
await browser_tabs({ action: "new" })

// Close tab by index
await browser_tabs({ action: "close", index: 1 })

// Select tab
await browser_tabs({ action: "select", index: 0 })
\`\`\`

---

### Inspection & Debugging

**\`browser_snapshot\`** - Capture accessibility snapshot (BEST for actions)
\`\`\`typescript
await browser_snapshot()
// Returns structured YAML with all interactive elements
// Use ref attribute from snapshot for precise element targeting
\`\`\`

**\`browser_take_screenshot\`** - Visual screenshot (for verification)
\`\`\`typescript
// Full page screenshot
await browser_take_screenshot({ 
  fullPage: true,
  type: "png" 
})

// Element screenshot
await browser_take_screenshot({ 
  element: "Submit button",
  ref: "e42",
  type: "jpeg"
})
\`\`\`

**\`browser_console_messages\`** - Get console logs
\`\`\`typescript
// All messages
await browser_console_messages()

// Errors only
await browser_console_messages({ onlyErrors: true })
\`\`\`

**\`browser_network_requests\`** - Monitor network activity
\`\`\`typescript
await browser_network_requests()
\`\`\`

---

### Element Interaction

**\`browser_click\`** - Click elements
\`\`\`typescript
// Basic click
await browser_click({ 
  element: "Submit button",
  ref: "e42"  // From snapshot
})

// Double-click
await browser_click({ 
  element: "File name",
  ref: "e18",
  doubleClick: true 
})

// Right-click
await browser_click({ 
  element: "Context menu trigger",
  ref: "e23",
  button: "right" 
})

// Click with modifier keys
await browser_click({ 
  element: "Link",
  ref: "e56",
  modifiers: ["Control"]  // ["Alt", "Control", "Meta", "Shift"]
})
\`\`\`

**\`browser_hover\`** - Hover over element
\`\`\`typescript
await browser_hover({ 
  element: "Dropdown trigger",
  ref: "e12" 
})
\`\`\`

**\`browser_drag\`** - Drag and drop
\`\`\`typescript
await browser_drag({
  startElement: "Draggable item",
  startRef: "e34",
  endElement: "Drop zone",
  endRef: "e56"
})
\`\`\`

---

### Form Interactions

**\`browser_type\`** - Type text into element
\`\`\`typescript
// Basic typing
await browser_type({ 
  element: "Username field",
  ref: "e8",
  text: "john.doe@example.com"
})

// Type slowly (character by character)
await browser_type({ 
  element: "Search input",
  ref: "e15",
  text: "playwright",
  slowly: true  // Triggers key handlers
})

// Type and submit
await browser_type({ 
  element: "Search box",
  ref: "e22",
  text: "test query",
  submit: true  // Presses Enter after typing
})
\`\`\`

**\`browser_press_key\`** - Press keyboard keys
\`\`\`typescript
// Single key
await browser_press_key({ key: "Enter" })
await browser_press_key({ key: "Escape" })
await browser_press_key({ key: "ArrowDown" })

// Key combinations (use modifiers in browser_click)
await browser_press_key({ key: "Control+Shift+L" })
\`\`\`

**\`browser_select_option\`** - Select dropdown option
\`\`\`typescript
// Single selection
await browser_select_option({ 
  element: "Country dropdown",
  ref: "e19",
  values: ["USA"]
})

// Multiple selections
await browser_select_option({ 
  element: "Multi-select",
  ref: "e31",
  values: ["option1", "option2", "option3"]
})
\`\`\`

**\`browser_fill_form\`** - Fill multiple fields at once
\`\`\`typescript
await browser_fill_form({
  fields: [
    { name: "Email", ref: "e10", type: "textbox", value: "user@example.com" },
    { name: "Password", ref: "e11", type: "textbox", value: "secretpass" },
    { name: "Remember me", ref: "e12", type: "checkbox", value: "true" },
    { name: "Country", ref: "e13", type: "combobox", value: "United States" }
  ]
})
\`\`\`

**\`browser_file_upload\`** - Upload files
\`\`\`typescript
// Single file
await browser_file_upload({ 
  paths: ["/absolute/path/to/file.pdf"] 
})

// Multiple files
await browser_file_upload({ 
  paths: [
    "/path/to/image1.jpg",
    "/path/to/image2.png"
  ]
})

// Cancel file chooser
await browser_file_upload({ paths: [] })
\`\`\`

---

### Advanced Interactions

**\`browser_evaluate\`** - Execute JavaScript
\`\`\`typescript
// Page-level script
await browser_evaluate({ 
  function: "() => document.title" 
})

// Element-level script
await browser_evaluate({ 
  element: "Product list",
  ref: "e45",
  function: "(element) => element.children.length" 
})

// Complex operations
await browser_evaluate({
  function: \`() => {
    const prices = Array.from(document.querySelectorAll('.price'));
    return prices.map(p => p.textContent);
  }\`
})
\`\`\`

**\`browser_handle_dialog\`** - Handle alerts/confirms/prompts
\`\`\`typescript
// Accept dialog
await browser_handle_dialog({ accept: true })

// Dismiss dialog
await browser_handle_dialog({ accept: false })

// Prompt with text
await browser_handle_dialog({ 
  accept: true,
  promptText: "My input value"
})
\`\`\`

**\`browser_wait_for\`** - Wait for conditions
\`\`\`typescript
// Wait for text to appear
await browser_wait_for({ text: "Loading complete" })

// Wait for text to disappear
await browser_wait_for({ textGone: "Spinner" })

// Wait for time
await browser_wait_for({ time: 2 })  // seconds
\`\`\`

**\`browser_resize\`** - Resize browser window
\`\`\`typescript
await browser_resize({ width: 1920, height: 1080 })
\`\`\`

---

## Best Practices

### 1. Always Start with Snapshot

**DO:**
\`\`\`typescript
// Step 1: Navigate
await browser_navigate({ url: "https://example.com" })

// Step 2: Get snapshot to see page structure
await browser_snapshot()

// Step 3: Use ref from snapshot for interactions
await browser_click({ element: "Login button", ref: "e42" })
\`\`\`

**DON'T:**
\`\`\`typescript
// ❌ Clicking without knowing page structure
await browser_click({ element: "Login", ref: "???" })
\`\`\`

---

### 2. Use Human-Readable Descriptions

**DO:**
\`\`\`typescript
await browser_click({ 
  element: "Submit button in contact form",
  ref: "e19"
})
\`\`\`

**DON'T:**
\`\`\`typescript
// ❌ Generic descriptions
await browser_click({ element: "button", ref: "e19" })
\`\`\`

---

### 3. Handle Async Operations with Waits

**DO:**
\`\`\`typescript
// Click button that triggers loading
await browser_click({ element: "Submit", ref: "e10" })

// Wait for result
await browser_wait_for({ text: "Success" })

// Take snapshot to verify
await browser_snapshot()
\`\`\`

**DON'T:**
\`\`\`typescript
// ❌ Assuming immediate response
await browser_click({ element: "Submit", ref: "e10" })
await browser_snapshot()  // Might snapshot too early!
\`\`\`

---

### 4. Check Console for Errors

**DO:**
\`\`\`typescript
// After critical operations
await browser_console_messages({ onlyErrors: true })
\`\`\`

---

### 5. Use Screenshots for Verification (not actions)

**DO:**
\`\`\`typescript
// Use snapshot for understanding structure
await browser_snapshot()

// Interact based on snapshot
await browser_click({ element: "Add to cart", ref: "e23" })

// Take screenshot to verify visually
await browser_take_screenshot({ type: "png" })
\`\`\`

**DON'T:**
\`\`\`typescript
// ❌ Don't use screenshots to decide actions
await browser_take_screenshot()  // This is for humans, not for deciding next steps
\`\`\`

---

### 6. Form Filling Best Practices

**Simple forms:**
\`\`\`typescript
// Individual fields for flexibility
await browser_type({ element: "Email", ref: "e8", text: "user@test.com" })
await browser_type({ element: "Password", ref: "e9", text: "pass123" })
await browser_click({ element: "Login", ref: "e10" })
\`\`\`

**Complex forms:**
\`\`\`typescript
// Batch fill for efficiency
await browser_fill_form({
  fields: [
    { name: "First Name", ref: "e5", type: "textbox", value: "John" },
    { name: "Last Name", ref: "e6", type: "textbox", value: "Doe" },
    { name: "Email", ref: "e7", type: "textbox", value: "john@example.com" },
    { name: "Country", ref: "e8", type: "combobox", value: "USA" },
    { name: "Newsletter", ref: "e9", type: "checkbox", value: "true" }
  ]
})
\`\`\`

---

### 7. Multi-Tab Management

\`\`\`typescript
// Save current work
const tabs = await browser_tabs({ action: "list" })

// Open new tab for research
await browser_tabs({ action: "new" })
await browser_navigate({ url: "https://docs.example.com" })

// Return to original tab
await browser_tabs({ action: "select", index: 0 })
\`\`\`

---

### 8. Error Recovery Pattern

\`\`\`typescript
// Attempt action
await browser_click({ element: "Submit", ref: "e42" })

// Check console for errors
const errors = await browser_console_messages({ onlyErrors: true })

// If errors, inspect current state
if (errors.length > 0) {
  await browser_snapshot()  // See what went wrong
  // Adjust strategy
}
\`\`\`

---

### 9. Network Monitoring

\`\`\`typescript
// Before critical action
await browser_click({ element: "Load data", ref: "e15" })

// Check network requests
const requests = await browser_network_requests()
// Verify expected API calls occurred
\`\`\`

---

## Common Workflows

### Login Flow
\`\`\`typescript
// 1. Navigate
await browser_navigate({ url: "https://app.example.com/login" })

// 2. Inspect
await browser_snapshot()

// 3. Fill credentials
await browser_type({ element: "Email field", ref: "e8", text: "user@example.com" })
await browser_type({ element: "Password field", ref: "e9", text: "password123" })

// 4. Submit
await browser_click({ element: "Login button", ref: "e10" })

// 5. Verify
await browser_wait_for({ text: "Dashboard" })
await browser_snapshot()
\`\`\`

---

### E2E Purchase Flow
\`\`\`typescript
// Navigate to product
await browser_navigate({ url: "https://store.com/product/123" })
await browser_snapshot()

// Add to cart
await browser_click({ element: "Add to cart", ref: "e23" })
await browser_wait_for({ text: "Added to cart" })

// Go to checkout
await browser_click({ element: "Checkout", ref: "e45" })
await browser_snapshot()

// Fill shipping info
await browser_fill_form({
  fields: [
    { name: "Full name", ref: "e10", type: "textbox", value: "John Doe" },
    { name: "Address", ref: "e11", type: "textbox", value: "123 Main St" },
    { name: "City", ref: "e12", type: "textbox", value: "New York" },
    { name: "ZIP", ref: "e13", type: "textbox", value: "10001" }
  ]
})

// Complete order
await browser_click({ element: "Place order", ref: "e50" })
await browser_wait_for({ text: "Order confirmed" })

// Verify
await browser_take_screenshot({ fullPage: true })
\`\`\`

---

### Data Extraction
\`\`\`typescript
// Navigate to data page
await browser_navigate({ url: "https://data.example.com/table" })

// Get structured data from snapshot
const snapshot = await browser_snapshot()

// Or extract via JavaScript
const data = await browser_evaluate({
  function: \`() => {
    const rows = Array.from(document.querySelectorAll('tr'));
    return rows.map(row => ({
      cells: Array.from(row.querySelectorAll('td')).map(td => td.textContent)
    }));
  }\`
})
\`\`\`

---

## Debugging Tips

### 1. Verbose Logging
Always check console after operations:
\`\`\`typescript
await browser_console_messages()
\`\`\`

### 2. Take Screenshots at Key Points
\`\`\`typescript
// Before action
await browser_take_screenshot({ filename: "before.png" })

// Perform action
await browser_click({ element: "Button", ref: "e10" })

// After action
await browser_take_screenshot({ filename: "after.png" })
\`\`\`

### 3. Inspect Snapshots Carefully
Look for:
- Element references (\`ref=eXX\`)
- Element states (disabled, hidden, etc.)
- Available interactions (clickable, editable, etc.)

### 4. Network Debugging
\`\`\`typescript
const requests = await browser_network_requests()
// Check for:
// - Failed requests (status 4xx, 5xx)
// - Missing resources
// - API call sequences
\`\`\`

---

## Performance Tips

1. **Batch Operations**: Use \`browser_fill_form\` instead of multiple \`browser_type\` calls
2. **Avoid Unnecessary Screenshots**: Use snapshots for decisions, screenshots only for verification
3. **Strategic Waits**: Use \`browser_wait_for\` instead of arbitrary delays
4. **Tab Management**: Close unused tabs to free resources

---

## Security Considerations

- ⚠️ Never log sensitive credentials
- 🔒 Use environment variables for secrets
- 🚫 Avoid \`browser_evaluate\` for untrusted input
- ✅ Verify SSL certificates in production

---

## Installation & Setup

### NPM Installation
\`\`\`bash
npm install -g @playwright/mcp
\`\`\`

### Claude Desktop Config
\`\`\`json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
\`\`\`

### Headless Mode
\`\`\`json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--headless"]
    }
  }
}
\`\`\`

---

## Key Differences: MCP vs Playwright Test API

| Feature | MCP Server | Playwright Test API |
|---------|------------|---------------------|
| Element Selection | Accessibility snapshot + ref | Selectors (CSS, text, role) |
| State Inspection | \`browser_snapshot()\` | \`page.screenshot()\`, locators |
| Async Handling | Explicit \`browser_wait_for()\` | Auto-waiting built-in |
| Multi-tab | \`browser_tabs()\` | \`context.pages()\` |
| Form Filling | \`browser_fill_form()\` | Individual \`fill()\` calls |

---

## Quick Reference Card

**Navigation:** \`browser_navigate\`, \`browser_navigate_back\`, \`browser_close\`
**Inspection:** \`browser_snapshot\`, \`browser_take_screenshot\`, \`browser_console_messages\`
**Interaction:** \`browser_click\`, \`browser_type\`, \`browser_hover\`, \`browser_drag\`
**Forms:** \`browser_fill_form\`, \`browser_select_option\`, \`browser_file_upload\`
**Advanced:** \`browser_evaluate\`, \`browser_wait_for\`, \`browser_handle_dialog\`
**Debugging:** \`browser_network_requests\`, \`browser_console_messages\`

---

## Remember

1. **Always snapshot first** - Know the page structure before acting
2. **Use ref from snapshot** - Precise element targeting
3. **Wait for async ops** - Don't assume immediate responses
4. **Human-readable descriptions** - Clear element identification
5. **Screenshots for verification** - Not for decision-making
6. **Check console** - Catch errors early
7. **Batch when possible** - Efficiency in form filling

---

**End of Playwright MCP Guide** | \`playwright-mcp-v1-a8f3d9c2\`