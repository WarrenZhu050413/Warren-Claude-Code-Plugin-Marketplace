---
description: Track TODOs in project-specific markdown files in ~/Desktop/TODO/
SNIPPET_NAME: tracking-todos
ANNOUNCE_USAGE: false
---

# Tracking TODOs

When the user mentions TODO or add-todo in conversation, you should:

## 1. Analyze the Context
- Review the current conversation to understand what task/issue/feature needs to be tracked
- Identify the project this TODO relates to (e.g., Nabokov, A2A_Confucius, etc.)
- Determine the appropriate category:
  - **New Features** - New functionality to implement
  - **UI Improvements** - User interface enhancements
  - **Prompt Engineering Improvements** - LLM/AI improvements
  - **Bug Fixes** - Issues to fix
  - **Research** - Investigation tasks
  - Or create a new category if needed

## 2. Check Existing TODO Files
- List files in `~/Desktop/TODO/` to see existing TODO files
- Naming convention: `{ProjectName}TODO.md` (e.g., `NabokovTODO.md`)
- If a relevant project file exists, add to it
- If not, create a new file following the naming convention

## 3. Format the TODO
- TODOs are added as **bullet points** using `-` or numbered lists
- Keep the format consistent with existing TODOs in that file
- Be specific and actionable
- Include relevant context or details from the conversation

## 4. Add or Update the File
**To add to existing file:**
- Read the file first to see the structure
- Find the appropriate category section
- Append your bullet point under that category
- If the category doesn't exist, add it

**To create new file:**
- Follow the structure of existing TODO files
- Start with category headers (e.g., `# New Features`)
- Add your TODO as a bullet point under the appropriate category

## 5. Example Format

```markdown
# New Features

- Implement feature X that does Y
- Add ability to Z when user does W

# UI Improvements

- Fix layout issue with component A
- Improve accessibility for B
```

## Example Usage

**Conversation:**
```
User: We need to add dark mode support to the sidebar
Assistant: [Reads TODO/NabokovTODO.md, finds UI Improvements section, adds:]
- Add dark mode support to the sidebar
```

**Conversation:**
```
User: TODO: The new ProjectX needs a settings page
Assistant: [Creates TODO/ProjectXTODO.md with:]
# New Features

- Create settings page for ProjectX
```

## Important Notes
- Always **read** the TODO file first before editing
- Use the **Edit** tool to append to existing files
- Use the **Write** tool only for new files
- Confirm with user after adding the TODO
- Keep formatting consistent with existing TODOs
