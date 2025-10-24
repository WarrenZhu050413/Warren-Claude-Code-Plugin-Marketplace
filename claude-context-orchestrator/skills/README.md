# Skills Directory

This directory contains Agent Skills for Claude Code, organized into two categories:

## 1. Custom Skills

Custom skills created for this project:

### Content Creation
- **documentation-tutorial** - Systematically analyze technical documentation and create interactive tutorials with exact quotes, code snippets, and feature demonstrations. Use when developing educational content from API docs, platform guides, or software documentation.

### Educational Tools
- **pedagogical-journey** - Create structured learning paths and educational progressions
- **using-claude** - Guide for using Claude effectively in various contexts

### Development & Scripting
- **writing-scripts** - Best practices for creating Python and Bash scripts
- **using-clis** - Guide for working with command-line interfaces

### Media & Content
- **generating-tts** - Guide for text-to-speech generation
- **fetching-images** - Tools and patterns for retrieving and processing images

### Analysis & Research
- **searching-deeply** - Deep web search and research methodology
- **reflecting-learnings** - Reflection and knowledge synthesis tools
- **using-codex** - Advanced code analysis and documentation tools

### Artifact Building
- **building-artifacts** - Create complex interactive artifacts (React, Vue, etc.)
- **building-mcp** - Build Model Context Protocol servers
- **theming-artifacts** - Professional theming and styling for artifacts

### Management Tools
- **managing-skills** - Comprehensive skill management guide
- **managing-snippets** - Snippet management and organization

## 2. Anthropic Example Skills

The following skills are from [Anthropic's example-skills repository](https://github.com/anthropics/skills) and are licensed under the Apache License 2.0:

- **testing-webapps** - Test local web applications using Playwright

## License Attribution

All Anthropic skills are licensed under the Apache License 2.0. See:
- **ANTHROPIC_SKILLS_LICENSE** - Full Apache 2.0 license text
- **ANTHROPIC_SKILLS_NOTICE** - Attribution and modification details

## Usage

These skills are automatically loaded when the claude-code-skills-manager plugin is installed. You can use any skill by mentioning it in your request to Claude Code.

Example:
```
Use the mcp-builder skill to help me create an MCP server for GitHub API integration
```

## Original Source

Anthropic skills copied from: https://github.com/anthropics/skills
- Original README: https://github.com/anthropics/skills/blob/main/README.md
- License: Apache 2.0
- Copyright: Anthropic, PBC

## Modifications

Skills have been integrated into this plugin structure without modifications to their functionality. The only changes are organizational (directory structure) to fit the Claude Code plugin system.
