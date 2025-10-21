# Changelog

All notable changes to the claude-context-orchestrator plugin are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0] - 2025-10-21

### Breaking Changes
- **Renamed plugin**: `claude-code-skills-manager` → `claude-context-orchestrator`
  - Rationale: Better reflects the hybrid architecture combining Agent Skills (model-invoked) and deterministic snippets (hook-based pattern matching)
- **Directory renamed**: `claude-code-snippets-plugin/` → `claude-context-orchestrator/`

### Added - Anthropic Skills Integration
Integrated Agent Skills from [Anthropic's example-skills repository](https://github.com/anthropics/skills) under Apache License 2.0:

**Skills Included**:
- `building-artifacts` - React + Tailwind CSS + shadcn/ui artifact builder
- `building-mcp` - MCP server development guide
- `testing-webapps` - Playwright-based web application testing
- `theming-artifacts` - Professional artifact theming system

**Modifications Made**:
- ✅ Integrated into plugin structure without modifying skill functionality
- ✅ Added proper Apache 2.0 licensing (`skills/ANTHROPIC_SKILLS_LICENSE`)
- ✅ Created attribution notice (`skills/ANTHROPIC_SKILLS_NOTICE`)
- ✅ Documented skills in `skills/README.md`
- ✅ Preserved original LICENSE.txt in each skill directory

**Source**: https://github.com/anthropics/skills
**License**: Apache License 2.0
**Copyright**: © 2024-2025 Anthropic, PBC

### Added - Custom Meta-Skills for Skill Management
Created comprehensive CRUD (Create, Read, Update, Delete) capabilities for managing Agent Skills:

**New Skills**:
- `managing-skills/` - Overall skill management guidance and best practices
- `creating-skills/` - Step-by-step skill authoring instructions (CREATE)
- `reading-skills/` - Skill listing, viewing, and inspection (READ)
- `updating-skills/` - Skill modification and refinement guide (UPDATE)
- `deleting-skills/` - Safe skill removal with backup strategies (DELETE)
- `managing-snippets/` - CRUD operations for deterministic snippets

**Key Features**:
- Model-invoked via descriptive YAML frontmatter
- Progressive disclosure pattern (concise SKILL.md with reference files)
- Based on official Anthropic best practices
- Includes workflow examples and common patterns

**Command Integration**:
Created symlinks from `commands/` to skill CRUD files:
- `commands/create-snippet.md` → `skills/managing-snippets/creating.md`
- `commands/read-snippets.md` → `skills/managing-snippets/reading.md`
- `commands/update-snippet.md` → `skills/managing-snippets/updating.md`
- `commands/delete-snippet.md` → `skills/managing-snippets/deleting.md`

### Added - Additional Custom Skills
**Warren's Custom Skills**:
- `using-codex` - Codex MCP for deep analysis and research
- `using-claude` - Claude Code features and debugging
- `searching-deeply` - Advanced search strategies
- `making-clearer` - Simplification and clarity improvements

### Added - Licensing & Attribution
- Created main `LICENSE` file (MIT) with Apache 2.0 third-party notice
- Enhanced README acknowledgments with prominent Anthropic attribution
- Documented dual-licensing: MIT (main plugin) + Apache 2.0 (Anthropic skills)
- Added comprehensive attribution in `skills/ANTHROPIC_SKILLS_NOTICE`

### Changed - Project Reorganization

**Directory Structure**:
- Created `bin/` for installation scripts (moved from `scripts/`)
- Consolidated all documentation in `docs/` directory
- Reorganized tests into `tests/unit/`, `tests/integration/`, `tests/validation/`
- Personal tests moved to `tests/personal/` (gitignored)

**Documentation**:
- Moved `scripts/INSTALL.md` → `docs/installation.md`
- Moved `scripts/QUICKSTART.md` → `docs/quickstart.md`
- Added comprehensive "Documentation" section to README
- Updated `docs/INDEX.md` with all documentation files
- Created `tests/README.md` for test suite documentation

**Testing**:
- Moved all test files from `scripts/` to `tests/`
- Created pytest configuration (`tests/conftest.py`)
- Updated validation tests to match current structure
- Added comprehensive test documentation

**Configuration**:
- Updated `.gitignore` to exclude temp/output files
- Excluded archive directories (`commands/.archive/`, `commands/backups/`)
- Excluded pytest cache directories

### Changed - Version & Metadata
- Version bump: 2.0.0 → 3.0.0
- Updated plugin description to reflect hybrid architecture
- Enhanced README with hybrid system explanation
- Updated CLAUDE.md project overview

### Documentation
- Created `REORGANIZATION.md` - Project structure reorganization summary
- Created `tests/REORGANIZATION_SUMMARY.md` - Test suite reorganization details
- Updated README with links to all documentation
- Created this CHANGELOG.md

---

## [2.0.0] - 2025-10-16

### Changed
- Complete rewrite from hook-based snippet injection to Agent Skills-based system
- Renamed from "claude-code-snippets" to "claude-code-skills-manager"
- Added five meta-skills for skill management
- Based on official Anthropic best practices

### Removed
- Removed hook-based injection as primary system (moved to legacy support)

---

## [1.0.0] - 2025-10-12

### Added
- Initial release
- Hook-based snippet injection with regex patterns
- CLI tools for snippet management (`snippets_cli.py`)
- Template pattern for complex snippets
- 20+ example snippets
- UserPromptSubmit hook with pattern matching
- Base config + local config system

---

## Comparison: Anthropic Original vs. Current Implementation

### What Changed

**Original Anthropic Skills** (from github.com/anthropics/skills):
- Standalone SKILL.md files
- Designed for general Claude Code use
- Open source (Apache 2.0)

**Current Implementation** (claude-context-orchestrator):
- ✅ Preserved all original skill functionality
- ✅ Added CRUD meta-skills for skill management
- ✅ Integrated snippet management skills
- ✅ Created unified plugin structure
- ✅ Added proper licensing and attribution
- ✅ Enhanced with installation/documentation tools

### Key Additions

1. **CRUD Capability**: Added complete skill management workflow
   - Create: `creating-skills/SKILL.md` with templates and examples
   - Read: `reading-skills/SKILL.md` with listing and inspection
   - Update: `updating-skills/SKILL.md` with modification patterns
   - Delete: `deleting-skills/SKILL.md` with safe removal

2. **Snippet Management**: Bridged skills with legacy snippet system
   - `managing-snippets/` skill with CRUD operations
   - Command symlinks for backward compatibility
   - Hook-based injection for deterministic patterns

3. **Enhanced Structure**: Professional plugin organization
   - Tests organized by type (unit/integration/validation)
   - Documentation consolidated in `docs/`
   - Installation tools in `bin/`
   - Clear separation of concerns

### License Compliance

All Anthropic skills remain under **Apache License 2.0**:
- Original LICENSE.txt preserved in each skill directory
- Full license text in `skills/ANTHROPIC_SKILLS_LICENSE`
- Attribution notice in `skills/ANTHROPIC_SKILLS_NOTICE`
- Copyright preserved: © 2024-2025 Anthropic, PBC

Main plugin licensed under **MIT License**:
- Includes Apache 2.0 notice for third-party components
- Dual-licensing clearly documented

---

## Migration Notes

### From v2.0.0 to v3.0.0

**Plugin Name Change**:
```bash
# Old installation
/plugin install claude-code-skills-manager@warren-claude-code-plugin-marketplace

# New installation
/plugin install claude-context-orchestrator@warren-claude-code-plugin-marketplace
```

**No Breaking Changes**:
- All existing functionality preserved
- Skills work the same way
- Commands still available
- Snippets still inject

**New Features Available**:
- Anthropic skills (artifacts, MCP, testing, theming)
- Enhanced skill management
- Better documentation
- Improved test suite

### From v1.0.0 to v3.0.0

Major rewrite. See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for details.

---

## Attribution

**Anthropic Skills**:
- Source: https://github.com/anthropics/skills
- License: Apache License 2.0
- Copyright: © 2024-2025 Anthropic, PBC
- Skills: building-artifacts, building-mcp, testing-webapps, theming-artifacts

**Custom Skills & Plugin**:
- Author: Fucheng Warren Zhu
- License: MIT
- Repository: https://github.com/WarrenZhu050413/Warren-Claude-Code-Plugin-Marketplace

---

**Last Updated**: 2025-10-21
**Plugin Version**: 3.0.0
