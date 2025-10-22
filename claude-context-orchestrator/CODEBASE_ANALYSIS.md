# Claude Context Orchestrator - Comprehensive Codebase Structure

**Version**: 3.0.0  
**Type**: Hybrid Claude Code Plugin (Agent Skills + Deterministic Snippets)  
**Author**: Fucheng Warren Zhu (wzhu@college.harvard.edu)

---

## Executive Summary

The **claude-context-orchestrator** is a sophisticated, production-grade Claude Code plugin that orchestrates two complementary context injection systems:

1. **Agent Skills** (11 skills total) - Model-invoked capabilities with progressive disclosure
2. **Deterministic Snippets** (26 snippet files) - Hook-based regex pattern matching for always-on context

This hybrid architecture provides both intelligent, on-demand context (skills) and predictable, rule-based context (snippets) working seamlessly together. The plugin is both a production system and a meta-framework—it provides tools to manage itself while offering reusable infrastructure.

---

## Directory Structure Overview

```
claude-context-orchestrator/
├── .claude-plugin/                 # Plugin manifest
│   └── plugin.json                # Declares plugin to Claude Code
├── skills/                         # Agent Skills (11 total)
│   ├── ANTHROPIC_SKILLS_LICENSE   # Apache 2.0 license
│   ├── ANTHROPIC_SKILLS_NOTICE    # Attribution notice
│   ├── README.md                  # Skills documentation
│   ├── building-artifacts/        # Anthropic skill: React/Tailwind/shadcn artifacts
│   ├── building-mcp/              # Anthropic skill: MCP server development
│   ├── testing-webapps/           # Anthropic skill: Playwright web testing
│   ├── theming-artifacts/         # Anthropic skill: Professional artifact theming
│   ├── managing-skills/           # Meta-skill: Overall skill management
│   ├── managing-snippets/         # Meta-skill: Snippet CRUD operations
│   ├── creating-skills/           # Meta-skill (referenced by managing-skills)
│   ├── reading-skills/            # Meta-skill (referenced by managing-skills)
│   ├── updating-skills/           # Meta-skill (referenced by managing-skills)
│   ├── deleting-skills/           # Meta-skill (referenced by managing-skills)
│   ├── using-claude/              # Warren's custom skill: Claude best practices
│   ├── using-codex/               # Warren's custom skill: Code search patterns
│   ├── searching-deeply/          # Warren's custom skill: Advanced search
│   ├── making-clearer/            # Warren's custom skill: Clarity patterns
│   └── generating-tts/            # Warren's custom skill: Text-to-speech
├── snippets/                       # Snippet configurations (26 total)
│   ├── making-clearer.md          # Clarity patterns
│   ├── generating-html-compact.md # HTML generation
│   ├── local/                     # User-specific snippets (not in marketplace)
│   │   ├── documentation/
│   │   ├── calendar/
│   │   ├── development/
│   │   ├── utilities/
│   │   ├── project-mgmt/
│   │   ├── learning-spanish.md
│   │   ├── output-formats/
│   │   ├── communication/
│   │   ├── productivity/
│   │   ├── coding-style-guides/
│   │   └── ...
│   └── ...
├── commands/                       # Slash commands
│   ├── create-snippet.md           # Symlink to skill reference
│   ├── delete-snippet.md           # Symlink to skill reference
│   ├── read-snippets.md            # Symlink to skill reference
│   ├── update-snippet.md           # Symlink to skill reference
│   ├── local/                      # User-specific commands (gitignored)
│   ├── backups/                    # Archived old commands
│   └── .archive/                   # Further archived items
├── hooks/                          # Hook configuration
│   └── hooks.json                 # UserPromptSubmit hook config
├── scripts/                        # Python infrastructure (4 core utilities)
│   ├── snippet_injector.py         # UserPromptSubmit hook handler
│   ├── snippets_cli.py             # Snippet CRUD CLI tool
│   ├── standardize_patterns.py     # Regex pattern utilities
│   ├── config.json                 # Base snippet configuration
│   └── config.local.json           # Local overrides (gitignored)
├── templates/                      # Reusable templates
│   └── html/
│       ├── base-template.html      # Complete HTML template with CSS/JS
│       └── examples.md             # Component examples
├── bin/                            # Installation/setup scripts
│   ├── install.sh                  # Global CLI installation
│   ├── uninstall.sh                # Cleanup script
│   └── setup.py                    # Python package setup
├── tests/                          # Test suite
│   ├── run_all_tests.sh            # Master test runner
│   ├── conftest.py                 # Pytest configuration
│   ├── unit/                       # Unit tests (3 files)
│   │   ├── test_snippets_cli.py
│   │   ├── test_config_paths.py
│   │   └── test_snippet_injector.py
│   ├── integration/                # Integration tests (2 files)
│   │   ├── test_snippets_cli_integration.py
│   │   └── test_skill_snippets.py
│   ├── validation/                 # Format/pattern validation
│   │   ├── test_format_compliance.sh
│   │   ├── test_pattern_matching.py
│   │   └── test_file_structure.sh
│   ├── personal/                   # User-specific tests
│   │   └── warren/nvim_test.sh
│   ├── README.md                   # Testing documentation
│   └── REORGANIZATION_SUMMARY.md   # Test suite notes
├── docs/                           # Comprehensive documentation (11 files)
│   ├── INDEX.md                    # Complete documentation index
│   ├── getting-started.md          # Overview and concepts
│   ├── installation.md             # Setup instructions
│   ├── quickstart.md               # Get running quickly
│   ├── configuration.md            # Snippets and skills config
│   ├── commands-reference.md       # All slash commands
│   ├── template-pattern.md         # Creating skills with templates
│   ├── multi-config-guide.md       # Managing multiple configs
│   └── troubleshooting.md          # Common issues
├── static/                         # UI assets
│   └── *.png                       # Screenshots for README
├── output/                         # Generated outputs (gitignored)
├── claude_html/                    # Claude Code generated HTML (gitignored)
├── LICENSE                         # MIT License (with Apache 2.0 notice)
├── README.md                       # Main user documentation
├── CHANGELOG.md                    # Version history
├── MIGRATION_GUIDE.md              # v1→v2 upgrade path
├── CLAUDE.md                       # Project-specific Claude Code instructions
└── .gitignore                      # Version control exclusions
```

---

## 1. Core Plugin Architecture

### 1.1 Plugin Manifest

**File**: `.claude-plugin/plugin.json`

```json
{
  "name": "claude-context-orchestrator",
  "version": "3.0.0",
  "description": "Hybrid context management combining Agent Skills + deterministic snippets",
  "author": {
    "name": "Fucheng Warren Zhu",
    "email": "wzhu@college.harvard.edu"
  },
  "keywords": ["skills", "agent-skills", "snippets", "skill-management", ...],
  "license": "MIT",
  "commands": "./commands",
  "hooks": "./hooks/hooks.json"
}
```

**Key Points**:
- All paths are **relative** (Claude Code requirement)
- Follows **semantic versioning** (X.Y.Z)
- Plugin name is **kebab-case**
- Dual configuration: commands + hooks

---

## 2. Agent Skills System (Primary Feature)

### 2.1 What Are Agent Skills?

Agent Skills are **official Claude Code capabilities** that:
- Are **model-invoked** (Claude decides when to use them)
- Use **progressive disclosure** (keep main SKILL.md concise, reference external files)
- Support **natural language matching** via description keywords
- Enable **smart context injection** without regex or manual configuration

### 2.2 The 11 Skills

**Category 1: Meta-Skills for Skill Management (6 total)**

| Skill Name | Purpose | Main File Size |
|------------|---------|----------------|
| `managing-skills/` | Comprehensive guidance for skill management + best practices | 14.5 KB |
| `managing-snippets/` | CRUD operations for deterministic snippets | ~8 KB |
| `creating-skills/` | Step-by-step skill authoring instructions | Referenced files |
| `reading-skills/` | Listing, viewing, and inspecting skills | Referenced files |
| `updating-skills/` | Modifying and refining existing skills | Referenced files |
| `deleting-skills/` | Safe skill removal with backup strategies | Referenced files |

**Category 2: Anthropic Example Skills (4 total)**

Production-grade skills from [Anthropic's example-skills repository](https://github.com/anthropics/skills), Apache License 2.0:

| Skill Name | Purpose |
|------------|---------|
| `building-artifacts/` | Build complex HTML artifacts with React, Tailwind CSS, shadcn/ui |
| `building-mcp/` | Comprehensive MCP server development guide |
| `testing-webapps/` | Test local web applications using Playwright |
| `theming-artifacts/` | Professional artifact theming system |

**Category 3: Warren's Custom Skills (4 total)**

| Skill Name | Purpose |
|------------|---------|
| `using-claude/` | Claude best practices and patterns |
| `using-codex/` | Code search and codex patterns |
| `searching-deeply/` | Advanced search techniques |
| `making-clearer/` | Clarity and communication guidance |
| `generating-tts/` | Text-to-speech generation |

### 2.3 Skill Structure

Each skill has this standard structure:

```
skill-name/
├── SKILL.md              # Main skill file (< 500 lines, concise)
└── reference-files/      # Supporting documentation (optional)
    ├── creating.md       # Detailed guidance
    ├── reading.md
    ├── updating.md
    ├── deleting.md
    └── examples.md
```

**SKILL.md Format**:

```yaml
---
name: Creating Skills
description: Guides creation of new Agent Skills in Claude Code. Use when user asks to create, author, or write new skills. Include trigger terms: create, authoring, writing, new skill.
---

# Creating Skills

## Quick Start
[Brief overview - 50-100 lines]

## Step-by-Step
[Main instructions using progressive disclosure]

## See Also
- [creating.md](creating.md) for detailed guidance
- [examples.md](examples.md) for code examples
```

**Key Principles**:
1. **Conciseness** - Assume Claude is smart; only add what it doesn't know
2. **Progressive Disclosure** - Keep SKILL.md under 500 lines; reference external files
3. **Clear Descriptions** - Include what (capability), when (context), and why (trigger terms)
4. **File References** - Use `${CLAUDE_PLUGIN_ROOT}` environment variable

### 2.4 Description Format (Critical!)

```yaml
description: What the skill does. Use when [context] or when user mentions [trigger keywords].
```

**Example (good)**:
```
Extract text and tables from PDF files, fill forms, merge documents. 
Use when working with PDF files or when user mentions PDFs, forms, or document extraction.
```

**Example (bad)**:
```
Helps with documents
```

---

## 3. Deterministic Snippet System (Legacy, Still Active)

### 3.1 Overview

The snippet system provides **hook-based pattern matching** for reliable context injection:

- **Event**: `UserPromptSubmit` (fired on every user message)
- **Handler**: `snippet_injector.py` (Python script)
- **Matching**: Regex patterns against user prompts
- **Injection**: Matched content as `additionalContext`

**Why Both Systems?**
- **Skills**: Smart, model-invoked, on-demand
- **Snippets**: Reliable, always-on, predictable

### 3.2 Hook Configuration

**File**: `hooks/hooks.json`

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/snippet_injector.py"
          }
        ]
      }
    ]
  }
}
```

**Execution Flow**:
```
User submits prompt
    ↓
UserPromptSubmit event fires
    ↓
snippet_injector.py executes
    ↓
Loads merged config (config.json + config.local.json)
    ↓
Matches regex patterns against prompt
    ↓
Collects matching snippet files
    ↓
Returns JSON with additionalContext
    ↓
Claude receives prompt + injected snippets
```

### 3.3 Snippet Configuration

**Base Config**: `scripts/config.json`

```json
{
  "mappings": [
    {
      "name": "HTML",
      "pattern": "\\bHTML\\b|\\bhtml\\b",
      "snippet": ["../commands/HTML.md"],
      "enabled": true,
      "separator": "\n"
    },
    {
      "name": "making-clearer",
      "pattern": "\\b(CLEAR|CLARITY)\\b[.:;,]?",
      "snippet": ["../snippets/making-clearer.md"],
      "enabled": true,
      "separator": "\n"
    }
  ]
}
```

**Fields Explained**:
- `name`: Unique snippet identifier
- `pattern`: Regex pattern to match in user prompt
- `snippet`: Array of file paths (supports multi-file snippets)
- `enabled`: Boolean toggle to enable/disable
- `separator`: Text separator between multiple files

### 3.4 Multi-Configuration System

**Priority-Based Config Merging**:

```
config.json (priority 0 - base, committed)
    ↓
config.local.json (priority 100 - overrides, gitignored)
    ↓
config.{name}.json (priority 50 or custom - project-specific)
    ↓
Final merged configuration
```

**Higher priority configs override lower priority** when snippet names match.

**Benefits**:
- Team members share base config via git
- Personal snippets in `config.local.json` stay private
- Projects can have custom `config.{project}.json`

---

## 4. Commands System

### 4.1 Command Files

**Location**: `commands/`

**Structure**:
```
commands/
├── create-snippet.md  (symlink → ../skills/managing-snippets/creating.md)
├── delete-snippet.md  (symlink → ../skills/managing-snippets/deleting.md)
├── read-snippets.md   (symlink → ../skills/managing-snippets/reading.md)
├── update-snippet.md  (symlink → ../skills/managing-snippets/updating.md)
├── local/             (user-specific, not in marketplace)
├── backups/           (archived old commands)
└── .archive/          (further archived items)
```

### 4.2 Command File Format

**Required YAML Frontmatter**:

```markdown
---
description: Brief description (shows in /help)
---

# Command Title

## Arguments

Input: `$ARGUMENTS`

## Instructions

1. **Parse arguments** - Check for flags like `-f`, `--force`
2. **Ask for confirmation** - For destructive operations (unless forced)
3. **Execute action** - Perform the operation
4. **Confirm completion** - Give user feedback

## Example Usage

/my-command example input
/my-command --force another example
```

**Key Requirements**:
- ✅ MUST have YAML frontmatter with `description`
- ✅ MUST use `$ARGUMENTS` for user input
- ✅ Ask for confirmation for create/update/delete (unless `-f` flag)
- ✅ No confirmation needed for read-only operations
- ✅ Provide clear error messages and next steps

### 4.3 v2.0 Migration Strategy

Commands now **symlink to skills** for consistency:
- Maintains backward compatibility
- Reduces duplication
- Promotes skills as primary interface
- Legacy commands archived in `backups/`

---

## 5. Python Infrastructure

### 5.1 Core Scripts (Location: `scripts/`)

#### `snippet_injector.py` - Hook Handler

**Purpose**: Main `UserPromptSubmit` hook handler

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `load_merged_config()` | Load and merge all config*.json files by priority |
| Pattern matching loop | Regex-based snippet detection |
| Multi-file handling | Support snippets spanning multiple files |
| JSON I/O | Receive prompt via stdin, return JSON with matched content |

**Input** (stdin):
```json
{
  "prompt": "User's message text"
}
```

**Output** (stdout):
```json
{
  "additionalContext": "Injected snippet content"
}
```

**Key Features**:
- Graceful error handling (skips malformed configs)
- Priority-based merging
- Case-sensitive regex matching
- Custom separators between snippets
- Multi-config support

#### `snippets_cli.py` - Snippet Management CLI

**Purpose**: Rigid, testable CLI for snippet CRUD operations

**Core Classes**:

| Class | Purpose |
|-------|---------|
| `SnippetError` | Standardized error reporting |
| `SnippetManager` | Core business logic for CRUD |
| `SnippetValidator` | Validation rules and checks |
| `VerificationHasher` | Content integrity tracking |

**Main Commands**:

```bash
# List snippets with statistics
python3 snippets_cli.py --config config.json list --show-stats

# Create new snippet
python3 snippets_cli.py --config config.json create my-snippet \
  --pattern "my-pattern" --content "my-content"

# Update existing snippet
python3 snippets_cli.py --config config.json update my-snippet \
  --pattern "new-pattern"

# Delete snippet (with backup)
python3 snippets_cli.py --config config.json delete my-snippet --backup

# Validate patterns
python3 snippets_cli.py --config config.json validate
```

**Key Features**:
- Multi-config support (base + local + named)
- Backup and restore capabilities
- Validation against naming conventions
- Automatic verification hash computation
- Atomic operations (transaction-like behavior)

#### `standardize_patterns.py`

**Purpose**: Regex pattern validation and standardization utility

#### Installation Scripts (`bin/`)

| Script | Purpose |
|--------|---------|
| `install.sh` | Install CLI globally (symlink to PATH) |
| `uninstall.sh` | Remove CLI from system |
| `setup.py` | Python package configuration |

---

## 6. Templates System

### 6.1 Template Files

**Location**: `templates/html/`

```
templates/html/
├── base-template.html    # Complete HTML template with CSS/JS
└── examples.md           # Component examples and usage patterns
```

### 6.2 Using Templates in Skills

Skills reference templates via environment variable:

```markdown
**Base Template**: `${CLAUDE_PLUGIN_ROOT}/templates/html/base-template.html`

**Workflow:**
1. Read the base template
2. Replace `{{PLACEHOLDER}}` with actual content
3. Add custom content in designated sections
4. Reference examples.md for component patterns
```

**Benefits**:
- Separation of concerns (instructions ≠ templates)
- Reusability across skills
- Easy maintenance (update once, used everywhere)
- Consistent formatting and styling

---

## 7. Configuration Files

### 7.1 Key Configuration Overview

| File | Purpose | Location | Update Frequency |
|------|---------|----------|------------------|
| `plugin.json` | Plugin manifest | `.claude-plugin/` | Per version bump |
| `hooks.json` | Hook events | `hooks/` | Rarely (architecture change) |
| `config.json` | Base snippet config | `scripts/` | When adding snippets |
| `config.local.json` | Personal overrides | `scripts/` | Personal (gitignored) |
| `.gitignore` | VCS exclusions | Root | Per release |

### 7.2 Layered Configuration Pattern

```
Priority 0: config.json (base, committed)
         ↓ merged with
Priority 100: config.local.json (overrides, gitignored)
         ↓ merged with
Priority 50: config.{project}.json (project-specific, optional)
         ↓
Final merged configuration
```

**Resolution**: Higher priority configs override lower priority when names conflict.

---

## 8. Testing Infrastructure

### 8.1 Test Organization

**Location**: `tests/`

```
tests/
├── run_all_tests.sh                    # Master test runner
├── conftest.py                         # Pytest configuration
├── unit/                               # Unit tests (3 files)
│   ├── test_snippets_cli.py
│   ├── test_config_paths.py
│   └── test_snippet_injector.py
├── integration/                        # Integration tests (2 files)
│   ├── test_snippets_cli_integration.py
│   └── test_skill_snippets.py
├── validation/                         # Validation tests (3 files)
│   ├── test_format_compliance.sh
│   ├── test_pattern_matching.py
│   └── test_file_structure.sh
├── personal/                           # User-specific tests
│   └── warren/nvim_test.sh
├── README.md                           # Testing guide
└── REORGANIZATION_SUMMARY.md           # Notes on test suite
```

### 8.2 Test Categories

1. **Unit Tests** - Individual function behavior
   - Snippet CLI operations
   - Config path resolution
   - Hook injection logic

2. **Integration Tests** - Multiple components together
   - Full snippet CRUD workflow
   - Skill-snippet interaction

3. **Validation Tests** - Format and pattern correctness
   - SKILL.md format compliance
   - Regex pattern validity
   - Directory structure correctness

4. **Personal Tests** - User-specific validations
   - Warren's editor integration (nvim)

### 8.3 Running Tests

```bash
# Run all tests
./tests/run_all_tests.sh

# Run specific suite
pytest tests/unit/test_snippets_cli.py
pytest tests/integration/

# Run with coverage
pytest --cov=scripts tests/

# Run shell validation
./tests/validation/test_format_compliance.sh
./tests/validation/test_file_structure.sh
```

---

## 9. Documentation System

### 9.1 Documentation Files (11 Total)

**Location**: `docs/`

| File | Purpose | Audience |
|------|---------|----------|
| `INDEX.md` | Complete documentation index | Everyone |
| `getting-started.md` | Overview and basic concepts | New users |
| `installation.md` | Step-by-step setup | First-time installers |
| `quickstart.md` | Get running in 5 minutes | Impatient users |
| `configuration.md` | Configure snippets and skills | Power users |
| `commands-reference.md` | All slash commands | Advanced users |
| `template-pattern.md` | Creating skills with templates | Developers |
| `multi-config-guide.md` | Managing multiple configs | Teams |
| `troubleshooting.md` | Common issues and solutions | Stuck users |

### 9.2 Documentation Structure

Each guide follows this pattern:
1. **Overview** - What is this about?
2. **Concepts** - Key ideas and terminology
3. **Step-by-Step** - Procedural guidance
4. **Examples** - Concrete use cases
5. **Troubleshooting** - Common issues

---

## 10. Development & Deployment

### 10.1 Installation Scripts

**`bin/install.sh`**:
```bash
./install.sh              # Install to /usr/local/bin (may need sudo)
./install.sh ~/bin        # Install to custom directory (no sudo)
```

Creates wrapper script that invokes the Python CLI.

**`bin/uninstall.sh`**:
Removes the installed CLI from system PATH.

### 10.2 Development Workflow

**Adding a New Skill**:
1. Create directory: `skills/my-skill/`
2. Write `SKILL.md` with YAML frontmatter and description
3. Add reference files as needed (creating.md, examples.md)
4. Use `${CLAUDE_PLUGIN_ROOT}` for file references
5. Test with Claude by asking relevant questions
6. Update `plugin.json` version number
7. Commit and tag

**Adding a New Snippet**:
1. Add mapping to `config.json` (or `config.local.json`)
2. Write regex pattern
3. Create/reference snippet file
4. Test pattern matching with validation script
5. Use `snippets_cli.py` for CRUD operations
6. Commit with descriptive message

**Testing Locally**:
```bash
# Create test marketplace
/plugin marketplace add file:///absolute/path/to/marketplace

# Install plugin
/plugin install claude-context-orchestrator@test-marketplace

# Verify
/help | grep claude-context-orchestrator
```

### 10.3 Version Management

**Semantic Versioning** (X.Y.Z):
- X = Major (breaking changes)
- Y = Minor (new features, backward compatible)
- Z = Patch (bug fixes)

**Update Process**:
1. Update `.claude-plugin/plugin.json` version
2. Update `CHANGELOG.md` with changes
3. Commit with descriptive message
4. Create git tag `v{X.Y.Z}`
5. Push to remote

### 10.4 Publishing to Marketplace

1. Add entry to `../.claude-plugin/marketplace.json`
2. Update marketplace version
3. Ensure all tests pass
4. Verify README installation instructions
5. Create git tag
6. Push to GitHub

---

## 11. How Everything Fits Together

### 11.1 User Perspective: Asking Claude

**Scenario 1: Skill Activation**
```
User: "How do I create a new skill?"
    ↓
Claude reads skill descriptions
    ↓
Matches "create" + "skill" keywords
    ↓
Claude loads creating-skills/SKILL.md
    ↓
Progressive disclosure: Claude loads reference files on demand
    ↓
Claude guides user through skill creation
```

**Scenario 2: Snippet Injection**
```
User: "Generate some HTML output"
    ↓
UserPromptSubmit hook fires
    ↓
snippet_injector.py runs
    ↓
Matches pattern "\\bHTML\\b"
    ↓
Injects HTML snippet as additional context
    ↓
Claude provides HTML-aware response
```

### 11.2 Developer Perspective: Adding Content

**Skill Development**:
```
Create skills/my-skill/SKILL.md
    ↓
Write YAML frontmatter with description + triggers
    ↓
Add content using progressive disclosure pattern
    ↓
Reference files with ${CLAUDE_PLUGIN_ROOT}
    ↓
Test by asking Claude relevant questions
    ↓
Commit and tag
```

**Snippet Development**:
```
Add entry to scripts/config.json
    ↓
Write regex pattern
    ↓
Reference snippet file path
    ↓
Test pattern with validation script
    ↓
Verify hook integration
    ↓
Commit
```

### 11.3 Maintenance Perspective: Quality & Support

**Regular Tasks**:
- Review snippet patterns for false positives
- Update skill descriptions for clarity
- Refine reference documentation
- Run full test suite before releases
- Keep CHANGELOG updated

**Quality Checks**:
```bash
./tests/run_all_tests.sh                    # All tests
./tests/validation/test_format_compliance.sh # Format
pytest tests/validation/test_pattern_matching.py # Patterns
```

---

## 12. Key Design Patterns

### 12.1 Progressive Disclosure

Skills keep SKILL.md concise (< 500 lines) and reference external files:

```markdown
# My Skill

[Overview: 50-100 lines]

## Advanced Topics
See [advanced.md](advanced.md) for complete API reference
See [examples.md](examples.md) for usage patterns
```

**Benefits**:
- Smaller token cost in SKILL.md
- Claude loads details only when needed
- Easier to maintain

### 12.2 Template Pattern

Separate instructions from reusable templates:

```
skills/my-skill/
├── SKILL.md              # Instructions only
└── reference/
    ├── template.html     # Reusable template
    └── examples.md       # Usage patterns
```

### 12.3 Multi-Configuration with Priority

Base + local + named configs with priority merging:

```
config.json (team shared)
    ↓ override
config.local.json (personal, gitignored)
    ↓ override
config.{project}.json (project-specific)
```

Benefits:
- **Team sharing** via base config
- **Personal customization** via local config
- **Project-specific** via named configs

### 12.4 Hybrid Architecture

Two complementary systems working together:

| Aspect | Skills | Snippets |
|--------|--------|----------|
| **Invocation** | Model-invoked | Always-on |
| **Matching** | Natural language | Regex patterns |
| **Loading** | Progressive | Full injection |
| **Use Case** | Smart context | Reliable safety nets |

---

## 13. File Naming Conventions

### 13.1 Skills

- **Directory**: `kebab-case-name/`
- **Main file**: `SKILL.md`
- **Supporting**: `reference-files.md`
- **Preferred form**: Gerund (verb + -ing)
  - ✅ "creating-skills", "building-artifacts"
  - ❌ "skill-creator", "artifacts-builder"

### 13.2 Snippets

- **File**: `kebab-case-name.md`
- **Short and memorable**: "html.md", "clarity.md"
- **In config**: `snippet[.local][.{name}].json`

### 13.3 Commands

- **File**: `kebab-case-command.md`
- **Descriptive**: "create-snippet.md", not "create.md"

### 13.4 Tests

- **File**: `test_*.py` or `*.sh`
- **Location**: `tests/{unit|integration|validation}/`
- **Naming**: Reflects what's tested

---

## 14. Licensing & Attribution

### 14.1 Main Plugin License

**MIT License** - See `LICENSE` file

### 14.2 Anthropic Skills License

**Apache License 2.0** for four Anthropic skills:
- building-artifacts
- building-mcp
- testing-webapps
- theming-artifacts

**Files**:
- `skills/ANTHROPIC_SKILLS_LICENSE` - Full Apache 2.0 text
- `skills/ANTHROPIC_SKILLS_NOTICE` - Attribution and modification details

### 14.3 Copyright

```
Copyright (c) 2024-2025 Anthropic, PBC.

Anthropic skills included under Apache License 2.0.
Main plugin under MIT License.
```

---

## 15. Critical Files Reference

| File | Purpose | Maintainer |
|------|---------|-----------|
| `.claude-plugin/plugin.json` | Plugin manifest | Release manager |
| `hooks/hooks.json` | Hook config | Architect |
| `scripts/config.json` | Base snippets | Contributors |
| `scripts/snippet_injector.py` | Hook handler | Maintainer |
| `scripts/snippets_cli.py` | CLI tool | Maintainer |
| `README.md` | User docs | Contributors |
| `CHANGELOG.md` | Version history | Release manager |
| `skills/managing-skills/SKILL.md` | Main meta-skill | Contributors |

---

## 16. Best Practices

### 16.1 DO's ✅

- **Skills over snippets** for new functionality
- **Use `${CLAUDE_PLUGIN_ROOT}`** for file references
- **Personal overrides** in `config.local.json`
- **Progressive disclosure** (< 500 lines in SKILL.md)
- **Clear descriptions** with trigger keywords
- **Semantic versioning** (X.Y.Z)
- **Test before committing** (run full suite)

### 16.2 DON'Ts ❌

- **Absolute paths** in config files
- **Missing frontmatter** in commands
- **Not parsing `$ARGUMENTS`** in commands
- **No confirmation** for destructive operations
- **Hardcoded credentials** in source
- **Forgetting to restart** Claude Code after changes

---

## 17. Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Plugin System | Claude Code | Native plugin host |
| Skills | YAML + Markdown | Metadata + documentation |
| Snippets | JSON + Regex | Configuration + matching |
| Hooks | Python CLI | Event handling |
| Management | Python 3 | Snippet CRUD |
| Testing | Pytest + Bash | Validation |
| Documentation | Markdown | User guides |
| Version Control | Git | Source management |

---

## 18. Important Gotchas

### Common Mistakes
1. ❌ Absolute paths in config → Always use relative paths
2. ❌ Missing YAML frontmatter → Commands MUST have `---` blocks
3. ❌ Not parsing `$ARGUMENTS` → Commands MUST extract user input
4. ❌ No confirmation for delete → ALWAYS ask before destructive ops
5. ❌ Hardcoded credentials → Use `.env` (gitignored)
6. ❌ Not restarting Claude Code → Changes require reload

### Key Insights
- Skills are **model-invoked** (Claude decides when)
- Snippets are **always-on** (regex-based)
- Both systems coexist without conflict
- Config merging uses **priority-based override**
- Templates enable **reuse** across skills

---

## Summary

The **claude-context-orchestrator** is a sophisticated, professionally-architected system that:

1. **Provides production capabilities** through 11 Agent Skills
2. **Enables self-management** via meta-skills
3. **Maintains backward compatibility** through snippet injection
4. **Offers extensive tooling** (Python CLI, hooks, templates)
5. **Emphasizes documentation** (11 comprehensive guides)
6. **Ensures quality** (multi-level testing)
7. **Follows best practices** (semantic versioning, progressive disclosure, priority-based merging)

The hybrid architecture elegantly combines intelligent, model-invoked context (skills) with predictable, rule-based context (snippets) to provide both powerful capabilities and reliable safety nets.

