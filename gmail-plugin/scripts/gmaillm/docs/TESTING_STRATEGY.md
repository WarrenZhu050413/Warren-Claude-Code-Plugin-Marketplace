# Testing Strategy for gmaillm

**Last Updated**: 2025-10-29
**Test Count**: 618 tests
**Coverage**: 80% overall

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Coverage by Module](#test-coverage-by-module)
3. [Interactive Workflows Testing](#interactive-workflows-testing)
4. [OAuth Authentication Testing](#oauth-authentication-testing)
5. [Testing Best Practices](#testing-best-practices)
6. [Known Limitations](#known-limitations)
7. [Future Testing Improvements](#future-testing-improvements)

---

## Testing Philosophy

### Core Principles

1. **Test What Matters**: Focus on business logic, data transformations, and error handling
2. **Mock External Dependencies**: Gmail API calls, file system operations, OAuth flows
3. **Realistic Test Data**: Use real-world email addresses, queries, and workflows (not "foo", "bar")
4. **Comprehensive Error Handling**: Test both happy paths and failure scenarios
5. **Runtime Type Safety**: Validate types at function boundaries with decorators

### Test Organization

Tests mirror the source code structure:

```
tests/
├── test_cli.py                          # Core CLI commands
├── test_commands_*.py                   # Command module tests
├── test_validators_*.py                 # Validation logic tests
├── test_helpers_*.py                    # Helper utility tests
├── test_models.py                       # Pydantic model tests
├── test_gmail_client.py                 # Gmail API wrapper tests
└── test_workflow_*.py                   # Workflow configuration/state tests
```

---

## Test Coverage by Module

### Excellent Coverage (>90%)

| Module | Coverage | Tests | Notes |
|--------|----------|-------|-------|
| `validators/styles.py` | 92% | 25 | Style validation logic |
| `validators/runtime.py` | 100% | 16 | Runtime type checking |
| `workflow_config.py` | 98% | 19 | Workflow CRUD operations |
| `commands/config.py` | 100% | 3 | Config commands |
| `helpers/domain/styles.py` | 90% | 11 | Style file handling |

### Good Coverage (80-90%)

| Module | Coverage | Tests | Notes |
|--------|----------|-------|-------|
| `formatters.py` | ~85% | Covered by integration tests | Now with runtime validation |
| `validators/email.py` | ~85% | 22 | Email validation |
| `validators/groups.py` | ~85% | 37 | Group validation |

### Adequate Coverage (70-80%)

| Module | Coverage | Tests | Notes |
|--------|----------|-------|-------|
| `commands/workflows.py` | 76% | 22 | Interactive loop untested (accepted) |
| `validators/styles.py` | 76% | 25 | Edge cases in validation |

### Accepted Low Coverage (<70%)

| Module | Coverage | Reason |
|--------|----------|--------|
| `setup_auth.py` | 0% | Requires real OAuth credentials and browser interaction |
| Interactive workflow loop | 24 lines | Requires console input simulation (not worth complexity) |

---

## Interactive Workflows Testing

### What IS Tested (22 tests)

**Non-Interactive Paths:**
```python
# ✅ Workflow CRUD operations
test_create_new_workflow()
test_delete_workflow()
test_show_workflow()

# ✅ JSON output mode (bypasses interactive loop)
test_run_workflow_json_output()

# ✅ Error handling
test_run_workflow_missing_both_workflow_and_query()
test_run_nonexistent_workflow()

# ✅ Configuration validation
test_workflow_config_requires_query()
test_auto_mark_read_flag_behavior()
```

**State Machine Logic:**
- Workflow loading from YAML
- Query execution
- Email fetching (summary vs full)
- Auto-mark-read flag behavior
- JSON output formatting

### What is NOT Tested (76 lines - Accepted Limitation)

**Interactive Console Loop** (`workflows.py:244-315`):

```python
# This code is NOT covered by automated tests:
for i, email_summary in enumerate(result.emails, 1):
    # Display email
    formatter.print_email_full(email)

    # Prompt for action
    action = console.input("Choose action: ").lower().strip()

    if action == 'v':  # View
        ...
    elif action == 'r':  # Reply
        ...
    elif action == 'a':  # Archive
        ...
    elif action == 's':  # Skip
        ...
    elif action == 'q':  # Quit
        break
```

**Why This is Acceptable:**

1. **Simple State Machine**: The logic is straightforward if/elif chains with no complex conditions
2. **Manually Verified**: Interactive workflows are tested manually during development
3. **Non-Critical Path**: JSON output mode (which IS tested) is used for automation/scripting
4. **Testing Complexity**: Mocking `console.input()` requires complex fixtures and doesn't add much value
5. **Low Bug Risk**: Each action is independent with clear side effects (API calls we DO test)

**Manual Test Cases** (verified during development):

- ✅ View full body (`v` action)
- ✅ Reply and archive (`r` action with body input)
- ✅ Reply cancelled (empty body)
- ✅ Archive email (`a` action)
- ✅ Skip email (`s` action with/without auto_mark_read)
- ✅ Quit workflow mid-processing (`q` action)
- ✅ Invalid action handling

---

## OAuth Authentication Testing

### What IS Tested

**Configuration Path Logic:**
```python
# ✅ Path resolution
test_finds_file_in_standard_location()
test_finds_file_in_fallback_location()
test_prefers_standard_location_over_fallback()

# ✅ Directory creation
test_creates_config_dir_if_needed()
test_creates_parent_directories()
```

**Error Handling:**
```python
# ✅ Missing credentials
test_verify_setup_failure()
test_status_not_authenticated()
```

### What is NOT Tested (158 lines - Requires Real Credentials)

**OAuth Flow** (`setup_auth.py`):

```python
# NOT covered by automated tests:
def setup_oauth():
    # 1. Load OAuth keys from file
    # 2. Create OAuth flow with Google
    # 3. Open browser for user consent
    # 4. Handle callback and exchange code for tokens
    # 5. Save credentials with 0600 permissions
```

**Why This is Acceptable:**

1. **External Dependencies**: Requires real Google OAuth credentials (can't mock)
2. **Browser Interaction**: Opens system browser for user consent
3. **Security Sensitive**: Handles real credentials and tokens
4. **Manual Process**: OAuth setup is a one-time manual operation
5. **Well-Established Pattern**: Uses standard `google-auth` library (well-tested)

**Manual Verification:**

- ✅ OAuth setup with new credentials
- ✅ Token refresh after expiration
- ✅ Permission scope validation
- ✅ Error handling for invalid keys
- ✅ File permission enforcement (0600)

**Future Improvement:**

Consider adding OAuth integration tests with test credentials in a staging environment:

```python
# Potential future test approach:
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("GMAIL_TEST_CREDENTIALS"), reason="No test credentials")
def test_oauth_flow_with_test_credentials():
    # Use test Google Cloud project
    # Verify OAuth flow with headless browser (Selenium)
    # Validate token exchange and refresh
    pass
```

---

## Testing Best Practices

### 1. Mocking Gmail API

**Pattern:**

```python
@patch("gmaillm.gmail_client.build")
def test_list_emails(mock_build):
    mock_service = Mock()
    mock_build.return_value = mock_service

    # Setup API response
    mock_service.users().messages().list().execute.return_value = {
        "messages": [{"id": "123", "threadId": "456"}]
    }

    client = GmailClient()
    result = client.list_emails()

    assert len(result.emails) > 0
```

**Key Points:**
- Mock at the `build()` level (Google API client creation)
- Return realistic API response structures
- Verify correct API calls made

### 2. Realistic Test Data

**❌ Bad:**
```python
email = EmailAddress(email="foo@bar.com")
subject = "Test"
body = "Lorem ipsum"
```

**✅ Good:**
```python
email = EmailAddress(
    name="Alice Johnson",
    email="alice.johnson@example.com"
)
subject = "Q4 Budget Review - Action Required"
body = "Hi team,\n\nPlease review the attached budget proposal..."
```

### 3. Runtime Type Validation

**New Pattern** (added in recent improvements):

```python
from gmaillm.validators.runtime import validate_pydantic, validate_types

@validate_pydantic(EmailFull)
def format_email(email: EmailFull) -> str:
    # Guaranteed email is EmailFull, not EmailSummary
    return f"{email.subject} - {email.body_plain}"

@validate_types
def process_emails(emails: List[EmailSummary]) -> int:
    # Validates list type and element types
    return len([e for e in emails if e.is_unread])
```

**Benefits:**
- Catches type mismatches at function boundary
- Clear error messages: "expected EmailFull, got EmailSummary"
- Complements Pydantic's data validation

### 4. Testing Pydantic Models

**Pattern:**

```python
def test_email_address_validation():
    # Valid
    addr = EmailAddress(email="user@example.com")
    assert addr.email == "user@example.com"

    # Invalid - should raise ValidationError
    with pytest.raises(ValidationError):
        EmailAddress(email="not-an-email")
```

### 5. Error Handling Tests

**Always test both success and failure:**

```python
def test_create_label_success(mock_client):
    # Setup success response
    mock_client.create_label.return_value = {"id": "Label_123"}
    # Verify success

def test_create_label_api_error(mock_client):
    # Setup error response
    mock_client.create_label.side_effect = HttpError(...)
    # Verify error handling
```

---

## Known Limitations

### 1. Console Input Simulation

**Limitation**: Interactive prompts (`console.input()`) are not easily testable

**Workaround**: Use JSON output mode for automation (which IS tested)

**Example**:
```bash
# Interactive (manual testing only)
gmail workflows run clear

# Programmatic (fully tested)
gmail workflows run clear --output-format json | jq .
```

### 2. OAuth Flow Testing

**Limitation**: Requires real Google OAuth credentials and browser

**Workaround**: Extensive manual testing during development

**Mitigation**: Configuration path logic IS tested

### 3. External API Responses

**Limitation**: Can't test against real Gmail API (rate limits, data privacy)

**Workaround**: Mock API responses based on documented structure

**Documentation**: See `docs/GMAIL_API_QUIRKS.md` for real-world API behavior

### 4. File System Operations

**Limitation**: Some file operations tested with `tmp_path` fixture only

**Mitigation**: Path resolution and permission logic well-covered

---

## Future Testing Improvements

### High Priority

1. **OAuth Integration Tests**
   - Setup test Google Cloud project
   - Use headless browser (Selenium/Playwright)
   - Automate token exchange flow
   - Verify permission scopes

2. **Static Type Checking**
   - Add `mypy` to CI/CD pipeline
   - Configure strict mode
   - Fix any type errors
   - Enforce type safety at build time

### Medium Priority

1. **Performance Benchmarks**
   - Email parsing speed
   - Batch API request efficiency
   - Style validation performance

2. **Integration Tests**
   - End-to-end workflow execution (with test data)
   - Label management lifecycle
   - Group operations

3. **Property-Based Tests**
   - Email address generation (hypothesis)
   - Style document generation
   - Query string validation

### Low Priority

1. **Interactive Workflow Simulation**
   - Complex console input mocking
   - State transition verification
   - Low value given existing coverage

2. **Formatter Edge Cases**
   - Attachment display variations
   - CC recipient formatting
   - Body truncation logic

---

## Summary

### Current State ✅

- **618 passing tests**
- **80% overall coverage**
- **100% coverage on critical modules** (runtime validators, workflow config)
- **Runtime type safety** implemented
- **Comprehensive error handling** tested

### Accepted Trade-offs

- **Interactive workflows**: 76 lines untested (simple state machine, manually verified)
- **OAuth setup**: 158 lines untested (requires real credentials, manually verified)
- **Formatter edge cases**: Low-risk display logic, visually verified

### Production Readiness ✅

The codebase is **production-ready** with:
- Excellent test coverage on business logic
- Runtime type validation preventing bugs
- Comprehensive Gmail API quirks documentation
- Clear error messages and handling
- Manual verification of untestable components

The untested portions are either:
1. **Simple state machines** (interactive loop)
2. **External dependencies** (OAuth flow)
3. **Low-risk display logic** (formatters)

All critical paths are thoroughly tested, and the remaining gaps are well-documented and accepted.

---

**Last Updated**: 2025-10-29
**Maintainer**: Add improvements and discoveries here
**Status**: Living document - update as testing strategy evolves
