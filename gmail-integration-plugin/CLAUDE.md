# Gmail Integration Plugin

## Code Quality Standards

### Verification Requirements
- **Never claim completion without proof** - Run tests and show output before marking tasks complete
- **No hallucinated metrics** - Only state numbers ("95% coverage", "3 bugs fixed") with tool output as evidence
- **Verify before claiming** - "Feature complete" requires passing test suite output

### Pattern Enforcement
- **Read existing code first** - Use Read tool to examine similar files before implementing
- **Follow project conventions** - Match existing naming, error handling, and testing patterns
- **Don't create new patterns** - If similar structure exists, copy that approach

### Test Quality
- **Use realistic test data** - Avoid "foo", "bar", "test" placeholders
- **Match real-world usage** - Test data should reflect actual use cases
- **Prefer real implementations** - Only mock external APIs or slow resources with justification

### Command Execution
- **Use proper tools** - Read (not cat), Grep (not bash grep), Edit (not sed)
- **Use project runners** - `uv run pytest` (not bare `pytest`), `uv run python` (not bare `python`)
- **Run tests after changes** - Always verify code changes with test execution

### Communication
- **Ask when ambiguous** - Clarify requirements before implementing
- **Explain before changing** - Describe approach and get approval for structural changes
- **Show, don't tell** - Include file paths, commands, and tool output in explanations

### Git Workflow
- **Test before committing** - ALWAYS run full test suite after ANY code change (`make test`)
- **Rebuild before committing** - ALWAYS rebuild the project after changes (`make install` or `make dev`)
- **Commit after feature changes** - Always create a git commit after completing a feature, bug fix, or significant change
- **Descriptive commit messages** - Follow the project's commit message style (check git log for examples)
- **Include context** - Commit message should explain why the change was made, not just what changed

### Change Workflow (Required Steps)
1. **Make the change** - Implement feature or fix
2. **Test the change** - Run `make test` and show output
3. **Rebuild** - Run `make install` or `make dev` to rebuild
4. **Verify** - Test the feature manually if applicable
5. **Commit** - Create git commit with descriptive message

### Installation and Build Issues

**Stale Build Cache:**
- **Symptom:** `make install` doesn't show latest code changes
- **Cause:** Python's build system caches a wheel snapshot (non-editable installs)
- **Solution:** `make install` includes `clean` dependency to force fresh builds
- **Alternative:** Use `make dev` + `uv run gmail` for instant changes (no rebuild needed)

**When Global Install Doesn't Match `uv run`:**
- `uv run gmail` uses local source (after `uv sync` creates local environment)
- `gmail` (global) uses cached wheel in `~/.local/share/uv/tools/`
- If they differ, run `make install` to rebuild global tool

**Installation Modes:**
- **Production install:** `make install` - Builds cached wheel, requires reinstall after changes
- **Local environment:** `make dev` then `uv run gmail` - Always uses current source (recommended for development)
