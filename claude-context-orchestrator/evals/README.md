# Skill Evaluation Records

Session evaluation records tracking which skills were used.

## File Format

**Naming:** `{date}_{session_name}_{context}.md`

Example: `2025-10-22_main_database-optimization.md`

**Content:** Simple JSON block

```json
{
  "date": "2025-10-22",
  "session_name": "main",
  "context": "Implemented user authentication",
  "reproducible_prompt": "Add OAuth login to the app",
  "skills_invoked": [
    "using-github-cli",
    "building-artifacts",
    "document-skills:docx"
  ]
}
```

## Purpose

- Track which skills are used in sessions
- Identify skill patterns and effectiveness
- Create reproducible records with original prompts
- Build data for improving the skill system

## Creating Evals

The `reflecting-learnings` skill (USE reflect) creates eval files automatically during reflection sessions.

Manually create one by:
1. Copy the JSON template above
2. Fill in your session details
3. Save as `{date}_{session_name}_{context}.md`
