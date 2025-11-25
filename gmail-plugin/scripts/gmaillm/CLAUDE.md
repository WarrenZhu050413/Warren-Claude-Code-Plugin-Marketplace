# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Development Workflow (uv-based)
```bash
# Development setup
make dev              # Install with dev dependencies (editable mode)
uv sync --all-extras  # Alternative: sync dev environment

# Testing
make test             # Run full test suite with coverage
uv run pytest         # Run tests (use this for single test files)
uv run pytest tests/test_cli.py::test_verify  # Run specific test

# Code Quality
make lint             # Run ruff linting
make format           # Format code with ruff

# Production Installation
make install          # Install globally (non-editable)
uv tool install --force .  # Alternative: install as tool
```

### Running Single Tests
```bash
# Run specific test file
uv run pytest tests/test_utils.py

# Run specific test class
uv run pytest tests/test_utils.py::TestParseEmailAddress

# Run specific test function
uv run pytest tests/test_utils.py::TestParseEmailAddress::test_parse_with_name

# Run with verbose output and coverage
uv run pytest tests/test_cli.py -v --cov=gmaillm
```

### Package Management
**IMPORTANT**: This project uses `uv` for package management. Always use `uv run` for commands:
```bash
uv run gmail --help    # NOT: gmail --help (in dev mode)
uv run pytest          # NOT: pytest
uv run ruff check .    # NOT: ruff check .
```

## Architecture Overview

### Three-Layer Helper System
The codebase uses a structured helper organization (gmaillm/helpers/):

1. **Core Layer** (`helpers/core/`)
   - Low-level infrastructure (paths, I/O)
   - Examples: `paths.py`, `io.py`
   - Pure utilities with no business logic

2. **Domain Layer** (`helpers/domain/`)
   - Business logic (groups, styles)
   - Examples: `groups.py`, `styles.py`
   - Domain-specific operations

3. **CLI Layer** (`helpers/cli/`)
   - CLI-specific utilities (UI, interaction, validation)
   - Examples: `ui.py`, `interaction.py`, `validation.py`, `errors.py`, `typer_extras.py`
   - User-facing CLI patterns

### Modular Command Structure
Commands are separated into modules (gmaillm/commands/):
- `labels.py` - Label management (list, create, delete)
- `groups.py` - Email group management (list, create, add, remove, validate)
- `styles.py` - Email style management (list, show, create, edit, validate)
- `workflows.py` - Workflow management (list, run)
- `config.py` - Configuration management (show, get, set)

Main CLI file (`cli.py`) handles core email operations (verify, setup-auth, list, read, send, reply).

### Validation System
Validators are organized by domain (gmaillm/validators/):
- `email.py` - Email/attachment/label validation
- `styles.py` - StyleLinter class for style format validation
- `groups.py` - GroupValidator class for group validation
- `email_operations.py` - Email operation validators

### Configuration and Paths
All user configuration lives in `~/.gmaillm/`:
```
~/.gmaillm/
├── credentials.json       # OAuth2 credentials (secure, 0600)
├── oauth-keys.json        # OAuth2 client secrets (secure, 0600)
├── email-groups.json      # Email distribution groups
├── output-style.json      # Output formatting preferences
├── workflows.yaml         # Email workflow definitions
└── email-styles/          # Email style templates (*.md)
    ├── professional-formal.md
    ├── professional-friendly.md
    └── ...
```

**Security**: Credentials and OAuth keys have 0600 permissions. The `config.py` module manages all paths.

### Key Design Patterns

#### Email Style Format
Styles use YAML frontmatter + XML-like sections:
```markdown
---
name: "Style Name"
description: "When to use: Context description (30-200 chars)."
---

<examples>
Example 1
---
Example 2
</examples>

<greeting>
- "Hi [Name],"
</greeting>

<body>
- Guideline 1
</body>

<closing>
- "Best,"
</closing>

<do>
- Best practice 1
</do>

<dont>
- What to avoid
</dont>
```

**Required sections in strict order**: examples → greeting → body → closing → do → dont

#### Progressive Disclosure
The GmailClient uses progressive disclosure for LLM-friendly output:
- `summary` format: Essential fields only (subject, from, date, snippet)
- `full` format: Complete email with body, headers, attachments
- Pagination with `max_results` parameter
- Markdown-formatted output for easy LLM parsing

#### CLI Confirmation Pattern
Commands use consistent confirmation patterns (from `helpers/cli/interaction.py`):
```python
from gmaillm.helpers.cli import confirm_or_force, show_operation_preview

# Show preview and get confirmation (unless --force)
show_operation_preview("Delete style", f"Style: {name}")
if not confirm_or_force(force):
    console.print("[yellow]Cancelled.[/yellow]")
    raise typer.Exit(0)
```

## Critical Implementation Details

### Name Collision Avoidance
**IMPORTANT**: `cli.py` defines a function called `list()` for email listing. This shadows Python's built-in `list()`.

**Solution**: Always use `builtins.list()` when you need the built-in:
```python
import builtins

# Wrong (calls email list command):
styles = list(styles_dir.glob("*.md"))

# Correct (uses built-in):
styles = builtins.list(styles_dir.glob("*.md"))
```

This was discovered via test failures where `list()` tried to initialize GmailClient unexpectedly.

### Test Organization
Tests mirror the source structure:
- `test_cli.py` - Main CLI commands (verify, list, read, send)
- `test_commands_*.py` - Command module tests (groups, labels)
- `test_helpers_*.py` - Helper utility tests
- `test_validators_*.py` - Validator tests
- `test_gmail_client.py` - GmailClient API wrapper tests
- `test_models.py` - Pydantic model validation tests

**Testing Pattern**: Mock Gmail API calls, never require real credentials:
```python
@patch("gmaillm.gmail_client.build")
def test_something(mock_build):
    mock_build.return_value = Mock()
    # Test code here
```

### Typer Rich Markup Mode
The CLI uses Rich markup mode (enabled in `cli.py`):
```python
app = typer.Typer(
    rich_markup_mode="rich",  # Enable Rich markup in docstrings
    cls=HelpfulGroup,          # Show help when required args missing
)
```

Docstrings support Rich formatting:
```python
@app.command()
def send() -> None:
    """Send an email.

    [bold cyan]EXAMPLES[/bold cyan]:
      [dim]$[/dim] gmail send --to user@example.com --subject "Test"
    """
```

### JSON Schema Migration
Project recently migrated from JSON Schema draft-07 to 2020-12. All Pydantic models use:
```python
from pydantic import BaseModel

class MyModel(BaseModel):
    model_config = {"json_schema_mode": "validation"}
    # Fields...
```

## Common Gotchas

1. **Always use `uv run`** for commands in development mode
2. **Use `builtins.list()`** when converting iterables to lists in `cli.py`
3. **Mock Gmail API calls** in tests - never require real credentials
4. **Style validation requires strict section order** - examples, greeting, body, closing, do, dont
5. **Config paths** - All user data in `~/.gmaillm/`, never in plugin directories
6. **Test coverage** - Maintain 80%+ coverage, use `make test` to verify
7. **HelpfulGroup** - Custom Typer group that shows help when subcommands are missing

## Adding New Commands

### Pattern for New Command Modules
1. Create module in `gmaillm/commands/` (e.g., `new_feature.py`)
2. Define Typer app with HelpfulGroup:
   ```python
   import typer
   from gmaillm.helpers.cli import HelpfulGroup

   app = typer.Typer(
       name="feature",
       help="Feature management",
       cls=HelpfulGroup,
       rich_markup_mode="rich",
   )
   ```
3. Add commands with Rich-formatted docstrings
4. Import and register in `cli.py`:
   ```python
   from gmaillm.commands import new_feature
   app.add_typer(new_feature.app, name="feature")
   ```
5. Create tests in `tests/test_commands_new_feature.py`
6. Update CHANGELOG.md with changes

### Pattern for New Validators
1. Create validator in `gmaillm/validators/` (e.g., `new_domain.py`)
2. Use Pydantic models for data validation
3. Provide detailed error messages with suggestions
4. Add tests in `tests/test_validators_new_domain.py`

## Documentation Standards

### User-Facing Documentation
- **README.md** - Installation, setup, quick start
- **TESTING.md** - Test running and writing guide
- **STYLES.md** - Complete email styles documentation
- **API_REFERENCE.md** - Full API documentation
- **PLUGIN_CREDENTIALS.md** - Credential setup for plugin mode

### Developer Documentation
- **CHANGELOG.md** - All changes with detailed explanations
- **REFACTORING_PLAN.md** - Architectural changes and migration plans
- **CLAUDE.md** (this file) - Claude Code guidance

### Commit Messages
Follow git log style:
```
type(scope): Brief description

- Detailed change 1
- Detailed change 2
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
Scopes: `cli`, `gmaillm`, `tests`, `styles`, etc.
