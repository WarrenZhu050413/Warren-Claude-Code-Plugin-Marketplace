---
name: "Tracking TODOs"
description: "Track TODOs in project-specific markdown files in ~/Desktop/TODO/."
---

# Tracking TODOs

When user mentions TODO, add-todo, or asks to view/retrieve TODOs:

## Retrieve/View TODOs

**When user asks to see TODOs:**
- "Show me my TODOs"
- "What's on my TODO list?"
- "List my pending tasks"
- "Check {ProjectName} TODOs"

**Actions:**
1. List available TODO files:
   ```bash
   ls ~/Desktop/TODO/*.md
   ```

2. For specific project:
   ```bash
   cat ~/Desktop/TODO/{ProjectName}TODO.md
   ```

3. For all TODOs (summary):
   ```bash
   grep -h "^-" ~/Desktop/TODO/*.md | sort | uniq
   ```

4. Search TODOs by keyword:
   ```bash
   grep -r "keyword" ~/Desktop/TODO/
   ```

**Present TODOs clearly:**
- Group by project
- Show category headers
- Highlight urgent/important items
- Count total pending items

## Add/Update TODOs

When user mentions adding a TODO:

## Analyze Context
- Identify task/issue/feature to track
- Identify project (e.g., Nabokov, A2A_Confucius)
- Determine category:
  - **New Features** - New functionality
  - **UI Improvements** - Interface enhancements
  - **Prompt Engineering Improvements** - LLM/AI improvements
  - **Bug Fixes** - Issues to fix
  - **Research** - Investigation tasks

## Check Files
- List files in `~/Desktop/TODO/`
- Naming: `{ProjectName}TODO.md` (e.g., `NabokovTODO.md`)
- Add to existing file or create new file

## Format
- Use bullet points with `-`
- Be specific and actionable
- Include relevant context

## Add/Update
**Existing file:**
- Read file first
- Find category section
- Append bullet under category

**New file:**
- Start with category header (`# New Features`)
- Add TODO as bullet point

## Example

```markdown
# New Features
- Implement feature X that does Y

# UI Improvements
- Fix layout issue with component A
```

## Usage Examples

**Retrieving TODOs:**
```
User: Show me my TODOs
→ [List all TODO files and display contents grouped by project]

User: What's pending for Nabokov project?
→ [Read and display TODO/NabokovTODO.md with category breakdown]

User: Search TODOs for "dark mode"
→ [grep -r "dark mode" ~/Desktop/TODO/]
```

**Adding TODOs:**
```
User: We need to add dark mode support to the sidebar
→ [Read TODO/NabokovTODO.md, add:]
- Add dark mode support to the sidebar
```

```
User: TODO: The new ProjectX needs a settings page
→ [Create TODO/ProjectXTODO.md:]
# New Features
- Create settings page for ProjectX
```

## Notes
- Always read TODO file before editing
- Use Edit tool for existing files
- Use Write tool for new files only
- Confirm after adding TODO
