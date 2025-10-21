# Skills Directory

This directory contains Agent Skills for Claude Code, organized into two categories:

## 1. Custom Skill Management Skills

These skills help manage and create other Agent Skills:

- **creating-skills** - Guide for creating new Agent Skills
- **deleting-skills** - Guide for safely removing Agent Skills
- **managing-skills** - Comprehensive skill management guide
- **reading-skills** - Guide for listing and viewing Agent Skills
- **updating-skills** - Guide for modifying existing Agent Skills

## 2. Anthropic Example Skills

The following skills are from [Anthropic's example-skills repository](https://github.com/anthropics/skills) and are licensed under the Apache License 2.0:

- **artifacts-builder** - Build complex HTML artifacts with React, Tailwind CSS, and shadcn/ui
- **mcp-builder** - Guide for creating high-quality MCP servers
- **webapp-testing** - Test local web applications using Playwright
- **theme-factory** - Style artifacts with professional themes

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
