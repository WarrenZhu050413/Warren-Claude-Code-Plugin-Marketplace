# ASCII Diagram Best Practices

Essential principles for effective ASCII diagrams based on 2024 research analyzing 507 real-world diagrams.

## Core Requirements

**Monospace font mandatory** - 2:1 aspect ratio ensures vertical/horizontal alignment
**<72 character width** - Prevents cutoff in plaintext rendering (emails, terminals, code comments)
**Grid-based alignment** - Each character occupies same space

## Character Selection

### Maximum Compatibility (Basic ASCII)
```
Borders:       | - +
Corners:       + (sharp)  / \ (round)
Arrows:        < > ^ v
Connections:   + (junction)
Dashed:        : (vertical)  = (horizontal)
```

### Enhanced (Unicode Box Drawing)
```
Borders:       ┌ ┐ └ ┘ ─ │
Junctions:     ├ ┤ ┬ ┴ ┼
Double:        ═ ║ ╔ ╗ ╚ ╝
Arrows:        ← ↑ → ↓ ↔
```

**Rule:** Use basic ASCII for maximum compatibility (code comments, email). Use Unicode for modern documentation.

## Common Patterns

### Box Structures
```
Simple:           Rounded:          Double:
+-------+         /-------\         ╔═══════╗
| Title |         | Title |         ║ Title ║
+-------+         \-------/         ╚═══════╝
```

### Connections
```
Arrows:           Trees:            Flow:
A ---> B          root              Start
                  ├── child1          ↓
A <--- B          └── child2        Process
                                      ↓
A <--> B                            End
```

### Tables
```
+------+--------+----------+
| Col1 | Col2   | Col3     |
+------+--------+----------+
| A    | Data   | Value    |
| B    | More   | Another  |
+------+--------+----------+
```

### Nested/Hierarchical
```
+-------------------------+
| Container               |
| +-----+    +----------+ |
| | Box |    | Another  | |
| +-----+    +----------+ |
+-------------------------+
```

### Flowchart Example
```
    Start
      |
      v
+----------+
| Process  |
+----------+
      |
      v
   <Decision>  --No--> End
      |
     Yes
      |
      v
   Action
```

## DITAA Enhancements

When using DITAA (DIagrams Through Ascii Art):

**Shape tags** (inside boxes):
- `{d}` - Document shape
- `{s}` - Storage/cylinder
- `{io}` - Input/output parallelogram

**Special features:**
- Use `/` and `\` for round corners
- Bullet points: ` o Item name` (space before o)
- Color codes: `cRGB` hex notation (e.g., `cF00` for red)

```
/---------\
| cGRE    |
| Success |
\---------/
```

## Layout Principles

**Spacing:**
- One space padding inside boxes
- Two spaces between adjacent elements
- Align vertically using columns

**Alignment:**
```
Good:                Bad:
+---+  +---+        +---+  +---+
| A |  | B |        |A|  |B|
+---+  +---+        +---+  +---+
```

**Line connections:**
```
Sharp turns:         Smooth transitions:
A ---+               A ---\
     |                    |
     +---> B               \---> B
```

## Common Mistakes

❌ Using proportional fonts (renders misaligned)
❌ Exceeding 72 characters (breaks in plaintext)
❌ Inconsistent spacing (hard to read)
❌ Missing alignment (looks unprofessional)
❌ Over-complexity (defeats purpose)

✅ Test in actual rendering environment
✅ Keep simple and focused
✅ Use consistent character styles
✅ Add labels/legend when needed
✅ Align elements on grid

## Tools

**Online editors:**
- ASCIIFlow - Interactive web-based editor
- Textik - Quick ASCII charts
- Markdeep - Render ASCII as SVG

**Command-line:**
- DITAA - Convert ASCII to PNG/SVG
- Graph-Easy - Generate from descriptions
- PlantUML - UML to ASCII

**Workflow:** Generate with tools → Hand-tune alignment → Version control with code

## Example: System Architecture

```
+------------+         +-------------+
| Frontend   |-------->| API Gateway |
| (React)    |<--------| (Node.js)   |
+------------+         +-------------+
                              |
                              v
                     +----------------+
                     | Database       |
                     | (PostgreSQL)   |
                     +----------------+
```

## Quick Reference

| Element | ASCII | Unicode | Use Case |
|---------|-------|---------|----------|
| Horizontal | `-` | `─` | Borders, connections |
| Vertical | `\|` | `│` | Borders, connections |
| Corner | `+` | `┌┐└┘` | Box corners |
| Junction | `+` | `├┤┬┴┼` | Line intersections |
| Arrow right | `>` | `→` | Directional flow |
| Arrow down | `v` | `↓` | Vertical flow |
| Dashed horiz | `=` | `┄` | Optional/weak connection |
| Dashed vert | `:` | `┊` | Optional/weak connection |

## Context-Specific Tips

**In code comments:** Use basic ASCII, keep <70 chars, test in actual IDE
**In Markdown:** Can use Unicode, consider code fences with syntax highlighting
**In emails:** Basic ASCII only, assume 72-char width limit
**In documentation:** Use DITAA or similar tools for professional rendering