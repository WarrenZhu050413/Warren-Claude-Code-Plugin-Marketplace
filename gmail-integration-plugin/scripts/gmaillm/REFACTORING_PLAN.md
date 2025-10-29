# Gmail CLI Refactoring Plan

**Status**: Phase 1 Complete (Validators Created)
**Date Started**: 2025-10-28
**Goal**: Modularize cli.py (1525 lines) into maintainable, testable modules

---

## Motivation

### Current Issues
1. **cli.py is too large** - 1525 lines, 41 functions, 3 classes
2. **Adding groups system** would push it to 2000+ lines
3. **Hard to navigate** - styles, config, labels mixed together
4. **Testing challenges** - everything in one file
5. **Inconsistent command structure** - some use plural, some singular

### Goals
1. Reduce cli.py from 1525 → ~500 lines
2. Separate concerns into logical modules
3. Make testing easier
4. Create consistent command structure
5. Add comprehensive groups management system

---

## Target Architecture

```
gmaillm/
├── cli.py                 # Main app + core commands (~500 lines)
│                          # verify, setup-auth, status, list, read, send, etc.
├── config.py              # Path management (already exists)
├── gmail_client.py        # API client (already exists)
├── models.py              # Data models (already exists)
├── formatters.py          # Output formatting (already exists)
├── utils.py               # Utilities (already exists)
├── setup_auth.py          # Auth setup (already exists)
│
├── commands/              # CLI command modules
│   ├── __init__.py
│   ├── labels.py          # gmail labels list/create/delete (~100 lines)
│   ├── groups.py          # gmail groups list/create/add/remove/validate (NEW, ~300 lines)
│   ├── styles.py          # gmail styles list/create/edit/validate (~400 lines)
│   └── config.py          # gmail config show/set/get (~150 lines)
│
├── validators/            # Validation logic
│   ├── __init__.py
│   ├── email.py           # Email/attachment/label validation ✅ DONE
│   ├── styles.py          # StyleLinter class ✅ DONE
│   └── groups.py          # GroupValidator class (NEW)
│
└── helpers/               # Helper utilities
    ├── __init__.py
    └── config.py          # Config loading/saving utilities
```

---

## Command Structure Improvements

### Before (Inconsistent)
```bash
gmail label create         # Singular
gmail styles list          # Plural
gmail config list-groups   # Hyphenated
```

### After (Consistent - All Plural)
```bash
# Labels
gmail labels list
gmail labels create <name>
gmail labels delete <name>

# Groups (NEW)
gmail groups list
gmail groups show <name>
gmail groups create <name>
gmail groups add <group> <email>
gmail groups remove <group> <email>
gmail groups delete <name>
gmail groups validate [name]
gmail groups validate-all

# Styles
gmail styles list
gmail styles show <name>
gmail styles create <name>
gmail styles edit <name>
gmail styles delete <name>
gmail styles validate [name]
gmail styles validate-all

# Config
gmail config show
gmail config get <key>
gmail config set <key> <value>
```

---

## Migration Phases

### ✅ Phase 1: Create Validator Modules (COMPLETE)

**Status**: ✅ Complete
**Files Created**:
- `gmaillm/validators/__init__.py`
- `gmaillm/validators/email.py` - Email validation functions
- `gmaillm/validators/styles.py` - StyleLinter class

**Tests Run**:
- ✅ Import validation
- ✅ Email validation logic
- ✅ StyleLinter instantiation

**Next**: Phase 2

---

### Phase 2: Create Helper Modules

**Estimate**: 30 minutes

#### 2.1 Create `helpers/config.py`

Extract from cli.py:
```python
# Functions to move:
- get_plugin_config_dir() → helpers/config.py
- load_json_config() → helpers/config.py
- load_email_groups() → helpers/config.py
- expand_email_groups() → helpers/config.py
- get_styles_dir() → helpers/config.py
- get_style_file_path() → helpers/config.py
- load_all_styles() → helpers/config.py
- extract_style_metadata() → helpers/config.py
- create_backup() → helpers/config.py
- create_style_from_template() → helpers/config.py
```

**Testing**:
```bash
uv run python -c "from gmaillm.helpers.config import get_plugin_config_dir; print(get_plugin_config_dir())"
```

---

### Phase 3: Create Command Modules

**Estimate**: 1.5 hours

#### 3.1 Create `commands/labels.py`

Extract from cli.py (lines 1040-1091):
```python
# Commands to move:
@label_app.command("create") → labels.create()
@label_app.command("list") → labels.list()

# Add new:
@label_app.command("delete") → labels.delete()  # NEW
```

**Testing**:
```bash
uv run gmail labels list
uv run gmail labels create test-label
```

#### 3.2 Create `commands/styles.py`

Extract from cli.py (lines 1208-1516):
```python
# Commands to move:
@styles_app.command("list") → styles.list()
@styles_app.command("show") → styles.show()
@styles_app.command("create") → styles.create()
@styles_app.command("edit") → styles.edit()
@styles_app.command("delete") → styles.delete()
@styles_app.command("validate") → styles.validate()
@styles_app.command("validate-all") → styles.validate_all()
```

**Testing**:
```bash
uv run gmail styles list
uv run gmail styles validate-all
```

#### 3.3 Create `commands/groups.py` (NEW)

New comprehensive groups management system:

```python
# Commands to implement:
@groups_app.command("list")
def list() -> None:
    """List all email distribution groups with member counts."""

@groups_app.command("show")
def show(name: str) -> None:
    """Show detailed information about a specific group."""

@groups_app.command("create")
def create(name: str, emails: List[str]) -> None:
    """Create a new email distribution group."""

@groups_app.command("add")
def add(group: str, email: str) -> None:
    """Add a member to an existing group."""

@groups_app.command("remove")
def remove(group: str, email: str) -> None:
    """Remove a member from a group."""

@groups_app.command("delete")
def delete(name: str, force: bool = False) -> None:
    """Delete an email distribution group."""

@groups_app.command("validate")
def validate(name: Optional[str] = None) -> None:
    """Validate group(s) for email format, duplicates, circular refs."""

@groups_app.command("validate-all")
def validate_all(fix: bool = False) -> None:
    """Validate all groups and optionally auto-fix issues."""
```

**Testing**:
```bash
uv run gmail groups list
uv run gmail groups create test-group --emails user1@example.com user2@example.com
uv run gmail groups add test-group user3@example.com
uv run gmail groups validate-all
```

#### 3.4 Create `commands/config.py`

Extract from cli.py (lines 1094-1206):
```python
# Commands to move:
@config_app.command("show") → config.show()
@config_app.command("edit-style") → config.edit_style()  # Deprecated
@config_app.command("edit-groups") → config.edit_groups()  # Deprecated

# Add new:
@config_app.command("get") → config.get()  # NEW
@config_app.command("set") → config.set()  # NEW
```

**Testing**:
```bash
uv run gmail config show
uv run gmail config get editor
```

---

### Phase 4: Create GroupValidator

**Estimate**: 45 minutes

Create `validators/groups.py`:

```python
from dataclasses import dataclass
from typing import Dict, List, Set, Optional

@dataclass
class GroupValidationError:
    """Represents a group validation error."""
    group_name: str
    error_type: str  # 'invalid_email', 'duplicate', 'circular_ref', 'missing_group'
    message: str
    details: Optional[Dict] = None

class GroupValidator:
    """Validator for email distribution groups."""

    def validate_group(self, name: str, emails: List[str]) -> List[GroupValidationError]:
        """Validate a single group."""
        errors = []

        # 1. Check email formats
        errors.extend(self._validate_email_formats(name, emails))

        # 2. Check for duplicates
        errors.extend(self._validate_duplicates(name, emails))

        return errors

    def validate_all_groups(self, groups: Dict[str, List[str]]) -> List[GroupValidationError]:
        """Validate all groups and check for circular references."""
        errors = []

        # Validate each group
        for name, emails in groups.items():
            if name.startswith("_"):
                continue
            errors.extend(self.validate_group(name, emails))

        # Check for circular references (#group1 → #group2 → #group1)
        errors.extend(self._check_circular_references(groups))

        return errors

    def _validate_email_formats(self, name: str, emails: List[str]) -> List[GroupValidationError]:
        """Check all emails are valid format."""

    def _validate_duplicates(self, name: str, emails: List[str]) -> List[GroupValidationError]:
        """Check for duplicate emails in a group."""

    def _check_circular_references(self, groups: Dict[str, List[str]]) -> List[GroupValidationError]:
        """Detect circular group references."""
```

**Testing**:
```python
# Test case 1: Valid group
validator = GroupValidator()
errors = validator.validate_group("test", ["user@example.com"])
assert len(errors) == 0

# Test case 2: Invalid email
errors = validator.validate_group("test", ["not-an-email"])
assert len(errors) == 1
assert errors[0].error_type == "invalid_email"

# Test case 3: Circular reference
groups = {
    "group1": ["#group2"],
    "group2": ["#group1"]
}
errors = validator.validate_all_groups(groups)
assert any(e.error_type == "circular_ref" for e in errors)
```

---

### Phase 5: Refactor cli.py

**Estimate**: 1 hour

#### 5.1 Update imports

```python
# At top of cli.py
from gmaillm.validators.email import (
    validate_email,
    validate_email_list,
    validate_attachment_paths,
    validate_label_name,
    validate_editor
)
from gmaillm.validators.styles import validate_style_name
from gmaillm.helpers.config import (
    get_plugin_config_dir,
    load_json_config,
    load_email_groups,
    expand_email_groups,
    # ... etc
)
from gmaillm.commands import labels, groups, styles, config as config_commands
```

#### 5.2 Register subcommands

```python
# Near bottom of cli.py, replace existing registrations:
app.add_typer(labels.app, name="labels")
app.add_typer(groups.app, name="groups")
app.add_typer(styles.app, name="styles")
app.add_typer(config_commands.app, name="config")
```

#### 5.3 Remove extracted code

Delete from cli.py:
- All validation functions (moved to validators/)
- All helper functions (moved to helpers/)
- All subcommand implementations (moved to commands/)
- Keep only: core commands (verify, status, list, read, send, etc.)

**Result**: cli.py ~500 lines (down from 1525)

---

### Phase 6: Update Tests

**Estimate**: 30 minutes

#### 6.1 Update test imports

```python
# tests/test_cli.py - update imports
from gmaillm.validators.email import validate_email
from gmaillm.validators.styles import StyleLinter
from gmaillm.helpers.config import load_email_groups
```

#### 6.2 Add new test files

Create:
- `tests/test_validators_email.py`
- `tests/test_validators_styles.py`
- `tests/test_validators_groups.py`
- `tests/test_commands_groups.py`

#### 6.3 Run full test suite

```bash
make test
```

---

### Phase 7: Update Documentation

**Estimate**: 30 minutes

#### 7.1 Update README.md

Add groups commands:
```markdown
## Groups Management

List all groups:
```bash
gmail groups list
```

Create a group:
```bash
gmail groups create team --emails alice@example.com bob@example.com
```

Add member:
```bash
gmail groups add team charlie@example.com
```

Validate groups:
```bash
gmail groups validate-all
```
```

#### 7.2 Update API_REFERENCE.md

Document all new groups commands with examples.

#### 7.3 Update CHANGELOG.md

```markdown
## [Unreleased]

### Changed
- **BREAKING**: Renamed `gmail label` → `gmail labels` for consistency
- Refactored CLI into modular structure for better maintainability
- Improved command organization and consistency

### Added
- Comprehensive groups management: `gmail groups list/create/add/remove/delete/validate`
- Group validation: detect invalid emails, duplicates, circular references
- `gmail config get/set` for programmatic configuration
- Auto-fix for group validation issues

### Deprecated
- `gmail config edit-groups` (use `gmail groups edit <name>` instead)
- `gmail config list-groups` (use `gmail groups list` instead)
```

---

## Testing Strategy

### Unit Tests
- Test each validator independently
- Test each command module independently
- Test helper functions

### Integration Tests
- Test full command workflows
- Test group expansion in send command
- Test validation in create/edit workflows

### Manual Testing
```bash
# Test core functionality still works
gmail status
gmail list
gmail send --to test@example.com --subject "Test" --body "Test"

# Test new groups system
gmail groups list
gmail groups create test user@example.com
gmail groups validate-all

# Test refactored commands
gmail labels list
gmail styles list
```

---

## Rollback Plan

If issues arise:

1. **Git branch**: All work on `refactor-cli-modular` branch
2. **Incremental commits**: Each phase is a separate commit
3. **Can revert**: `git revert <commit>` for specific phase
4. **Full rollback**: `git reset --hard main`

---

## Success Criteria

- [ ] All existing tests pass
- [ ] CLI loads without errors
- [ ] All core commands work (status, list, send, etc.)
- [ ] Groups commands work (list, create, validate)
- [ ] cli.py is < 600 lines
- [ ] Code coverage maintained or improved
- [ ] Documentation updated
- [ ] No breaking changes for users (except plural renaming)

---

## Timeline Estimate

| Phase | Estimate | Status |
|-------|----------|--------|
| Phase 1: Validators | 30 min | ✅ DONE |
| Phase 2: Helpers | 30 min | ⏸️ Paused |
| Phase 3: Commands | 1.5 hrs | ⏸️ Paused |
| Phase 4: GroupValidator | 45 min | ⏸️ Paused |
| Phase 5: Refactor cli.py | 1 hr | ⏸️ Paused |
| Phase 6: Tests | 30 min | ⏸️ Paused |
| Phase 7: Docs | 30 min | ⏸️ Paused |
| **Total** | **~5 hours** | **20% Complete** |

---

## Notes

- **Backward compatibility**: Deprecated commands show warnings but still work
- **Migration period**: Keep deprecated commands for 1-2 releases
- **User communication**: Document changes in CHANGELOG and README
- **Version bump**: This is a minor version (breaking changes minimal)

---

## Questions/Decisions

1. **Naming: Singular vs Plural?**
   - ✅ **Decision**: Use plural for all (labels, groups, styles)
   - Reasoning: Industry standard (aws, kubectl, docker)

2. **Breaking changes acceptable?**
   - ✅ **Decision**: Minimal breaking changes, deprecate old commands
   - Migration path: `label` → `labels` (can be done in v2.0)

3. **Keep old commands?**
   - ✅ **Decision**: Keep with deprecation warnings for 2 releases
   - Remove in v2.0

---

**Last Updated**: 2025-10-28
**Next Steps**: Resume at Phase 2 when ready
