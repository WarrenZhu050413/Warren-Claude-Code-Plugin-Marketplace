---
name: Building Artifacts
description: Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Artifacts are automatically saved to ~/Desktop/Artifacts directory. Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.
license: Complete terms in LICENSE.txt
---

# Artifacts Builder

**Stack**: React 18 + TypeScript + Vite + Parcel + Tailwind CSS + shadcn/ui

## Workflow

1. Initialize: `bash scripts/init-artifact.sh <project-name>`
2. Develop in generated project
3. Bundle: `bash scripts/bundle-artifact.sh` (run from project directory)
4. Share bundled HTML with user
5. Test only if needed (optional)

## Artifact Types

### Type 1: Complex Interactive Applications
Multi-component applications with state management and routing. Use React stack above.

### Type 2: Interactive Primary Source Artifacts
Explorable visualizations of documentation, papers, books. Use HTML with collapsibles and structured navigation (no React).

**Reference**: `primary-sources-reference.md`

**Use for**: Technical docs, research papers, books/textbooks, historical documents

## Design Guidelines

Avoid "AI slop": no excessive centered layouts, purple gradients, uniform rounded corners, or Inter font.

## Step 1: Initialize

```bash
bash scripts/init-artifact.sh <project-name>
```

**Location**: `~/Desktop/Artifacts/` (fallback: current directory)

**Creates**:
- React + TypeScript (Vite)
- Tailwind CSS 3.4.1 + shadcn/ui theming
- Path aliases (`@/`)
- 40+ shadcn/ui components + Radix UI dependencies
- Parcel configured (.parcelrc)
- Node 18+ compatibility

## Step 2: Develop

```bash
cd ~/Desktop/Artifacts/<project-name>
```

Edit generated files. See **Common Development Tasks** for guidance.

## Step 3: Bundle

```bash
bash scripts/bundle-artifact.sh
```

**Requirement**: `index.html` in project root

**Output**: `bundle.html` - self-contained artifact with inlined JavaScript, CSS, dependencies

**Process**:
- Installs: parcel, @parcel/config-default, parcel-resolver-tspaths, html-inline
- Creates `.parcelrc` with path alias support
- Builds with Parcel (no source maps)
- Inlines all assets

## Step 4: Share

Share `bundle.html` in conversation for user to view as artifact.

## Step 5: Testing (Optional)

Test only if requested or issues arise. Use available tools (Playwright, Puppeteer). Avoid upfront testing—adds latency.

## Reference

- shadcn/ui components: https://ui.shadcn.com/docs/components
