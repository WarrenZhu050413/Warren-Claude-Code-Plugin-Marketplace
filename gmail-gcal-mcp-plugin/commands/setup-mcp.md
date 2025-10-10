---
description: Set up Gmail and Google Calendar MCP servers for current project
---

# Setup MCP Servers

Set up Gmail and Google Calendar MCP servers for the current project.

## Arguments

Input: `$ARGUMENTS`

## Instructions

1. **Parse the arguments**:
   - Check if `$ARGUMENTS` contains `-f` or `--force` flag
   - Check if `$ARGUMENTS` specifies a directory path (default to current directory)
   - Extract any OAuth credentials if provided

2. **Verify current directory**:
   - Check if current directory is a valid project (has .git, package.json, or similar)
   - If not, warn the user
   - If `-f` or `--force`, skip this check

3. **Check for existing configuration**:
   - Look for existing `.mcp.json` in the target directory
   - Look for existing `.env` file
   - If they exist, ask what to do (unless forced):
     - Overwrite
     - Merge
     - Cancel

4. **Ask for confirmation** (UNLESS `-f` or `--force` flag is present):
   - Show what will be created:
     - `.mcp.json` with Gmail and Calendar MCP servers
     - `.env.example` template
     - `.env` (if requested)
   - Show the target directory
   - Ask: "Set up MCP servers in this directory? (yes/no)"
   - If no, abort
   - If yes, proceed

5. **Create .mcp.json**:
   - Use the template from the plugin's `setup-mcp.sh`
   - Write to target directory
   - Confirm creation

6. **Create .env.example**:
   - Create template with placeholder credentials
   - Write to target directory

7. **Handle .env file**:
   - If `.env` doesn't exist, ask if user wants to create it
   - If yes, copy from `.env.example`
   - If user provided credentials in `$ARGUMENTS`, populate them
   - Otherwise, leave as placeholders

8. **Update .gitignore**:
   - Check if `.gitignore` exists
   - If yes, check if `.env` is already listed
   - If not, ask to add it (unless forced)
   - Add `.env` to `.gitignore`

9. **Provide next steps**:
   - Show the user what was created
   - Remind them to:
     - Get OAuth credentials from Google Cloud Console
     - Add credentials to `.env`
     - Restart Claude Code
   - Link to OAuth setup guide

## Example Usage

```
/setup-mcp
/setup-mcp --force
/setup-mcp -f /path/to/project
/setup-mcp with existing credentials
```

## Notes

- Always ask for confirmation unless `-f` or `--force` is provided
- Never overwrite existing files without permission
- Always update .gitignore to protect .env
- Provide clear next steps after setup
- Link to documentation for OAuth setup
