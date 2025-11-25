# Testing Guide for gmaillm

This document provides instructions for running and writing tests for the gmaillm package.

## Table of Contents

- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Organization](#test-organization)
- [Writing Tests](#writing-tests)
- [Coverage Reports](#coverage-reports)
- [Continuous Integration](#continuous-integration)

---

## Setup

### Install Development Dependencies

First, install the test dependencies:

```bash
cd scripts/gmaillm
pip install -r requirements-dev.txt
```

This installs:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `pytest-asyncio` - Async test support
- `freezegun` - Time/date mocking

### Install Package in Development Mode

Install the package in editable mode:

```bash
pip install -e .
```

---

## Running Tests

### Run All Tests

```bash
# From the gmaillm directory
pytest

# Or with verbose output
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_utils.py
pytest tests/test_models.py
pytest tests/test_gmail_client.py
pytest tests/test_cli.py
```

### Run Specific Test Class or Function

```bash
# Run a specific test class
pytest tests/test_utils.py::TestParseEmailAddress

# Run a specific test function
pytest tests/test_utils.py::TestParseEmailAddress::test_parse_with_name
```

### Run Tests with Coverage

```bash
# Generate coverage report
pytest --cov=gmaillm --cov-report=html --cov-report=term

# Open HTML coverage report
open htmlcov/index.html
```

### Run Tests in Parallel (Faster)

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

---

## Test Organization

Tests are organized by module:

```
tests/
├── __init__.py           # Test package marker
├── conftest.py           # Shared fixtures and configuration
├── test_utils.py         # Tests for utils.py
├── test_models.py        # Tests for models.py
├── test_gmail_client.py  # Tests for gmail_client.py
└── test_cli.py           # Tests for cli.py
```

### Test Coverage by Module

| Module | Test File | Coverage Focus |
|--------|-----------|----------------|
| `utils.py` | `test_utils.py` | String parsing, encoding, MIME construction |
| `models.py` | `test_models.py` | Pydantic models, validation, markdown formatting |
| `gmail_client.py` | `test_gmail_client.py` | Gmail API interactions, mocked API calls |
| `cli.py` | `test_cli.py` | CLI argument parsing, command execution |

---

## Writing Tests

### Test Naming Conventions

- Test files: `test_<module>.py`
- Test classes: `Test<Feature>`
- Test functions: `test_<what_is_being_tested>`

**Example:**
```python
# tests/test_utils.py

class TestParseEmailAddress:
    """Tests for parse_email_address function."""

    def test_parse_with_name(self):
        """Test parsing email with name."""
        result = parse_email_address("John <john@example.com>")
        assert result == {"name": "John", "email": "john@example.com"}

    def test_parse_without_name(self):
        """Test parsing plain email."""
        result = parse_email_address("john@example.com")
        assert result == {"name": None, "email": "john@example.com"}
```

### Using Fixtures

Fixtures are defined in `conftest.py` and can be used in any test:

```python
def test_something(temp_dir, sample_email_groups):
    """Use fixtures provided by conftest.py."""
    # temp_dir is a temporary directory
    # sample_email_groups is sample test data
    assert "team" in sample_email_groups
```

### Mocking External Dependencies

Use `unittest.mock` for mocking Gmail API:

```python
from unittest.mock import Mock, patch

@patch("gmaillm.gmail_client.GmailClient")
def test_with_mock(mock_client):
    """Test with mocked Gmail client."""
    mock_client.list_emails.return_value = []
    # Test code here
```

### Testing CLI Commands

```python
def test_cli_command():
    """Test CLI command execution."""
    with patch("sys.argv", ["gmail", "verify"]):
        with patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_with(0)
```

### Parametrized Tests

Use `@pytest.mark.parametrize` for testing multiple inputs:

```python
@pytest.mark.parametrize("input,expected", [
    ("test@example.com", {"name": None, "email": "test@example.com"}),
    ("John <test@example.com>", {"name": "John", "email": "test@example.com"}),
])
def test_parse_variations(input, expected):
    """Test multiple input variations."""
    assert parse_email_address(input) == expected
```

---

## Coverage Reports

### Terminal Coverage

```bash
pytest --cov=gmaillm --cov-report=term-missing
```

Output:
```
---------- coverage: platform darwin, python 3.11.0 -----------
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
gmaillm/__init__.py            5      0   100%
gmaillm/cli.py               120     15    88%   45-52, 89-95
gmaillm/gmail_client.py      180     25    86%   123-145, 234-256
gmaillm/models.py             85      5    94%   156-160
gmaillm/utils.py              55      2    96%   78-79
--------------------------------------------------------
TOTAL                        445     47    89%
```

### HTML Coverage Report

```bash
pytest --cov=gmaillm --cov-report=html
open htmlcov/index.html
```

This generates an interactive HTML report showing:
- Line-by-line coverage
- Uncovered code highlighted
- Coverage percentage per file

### Coverage Thresholds

Fail tests if coverage drops below threshold:

```bash
pytest --cov=gmaillm --cov-fail-under=80
```

---

## Test Markers

Tests can be marked for categorization:

```python
@pytest.mark.unit
def test_unit_test():
    """Fast unit test."""
    pass

@pytest.mark.integration
def test_integration():
    """Test with external dependencies."""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Test that takes a long time."""
    pass
```

Run only specific markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

---

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        cd scripts/gmaillm
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        pip install -e .

    - name: Run tests with coverage
      run: |
        cd scripts/gmaillm
        pytest --cov=gmaillm --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

---

## Common Test Patterns

### Testing Pydantic Models

```python
from pydantic import ValidationError
import pytest

def test_model_validation():
    """Test model validation."""
    with pytest.raises(ValidationError):
        SendEmailRequest(to=[], subject="", body="")  # Invalid
```

### Testing Markdown Output

```python
def test_markdown_formatting():
    """Test markdown generation."""
    email = EmailSummary(...)
    markdown = email.to_markdown()
    assert "**Subject**" in markdown
    assert "From:" in markdown
```

### Testing File I/O

```python
def test_file_operations(tmp_path):
    """Test file read/write with temp directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert test_file.read_text() == "content"
```

---

## Troubleshooting

### Tests Fail Due to Missing Credentials

Tests should not require actual Gmail credentials. Ensure all Gmail API calls are mocked:

```python
@patch("gmaillm.gmail_client.build")
def test_without_credentials(mock_build):
    """Mock the API client."""
    mock_build.return_value = Mock()
    # Test code
```

### Import Errors

Ensure package is installed in development mode:

```bash
pip install -e .
```

### Slow Tests

Use markers to skip slow tests during development:

```bash
pytest -m "not slow"
```

---

## Best Practices

1. **Write tests first** (TDD approach when possible)
2. **Keep tests independent** - Each test should run in isolation
3. **Mock external dependencies** - Don't make real API calls in tests
4. **Use descriptive names** - Test function names should explain what's being tested
5. **Test edge cases** - Empty inputs, None values, invalid data
6. **Maintain high coverage** - Aim for 80%+ code coverage
7. **Keep tests fast** - Unit tests should run in milliseconds
8. **Use fixtures** - Share setup code via conftest.py
9. **Document complex tests** - Add docstrings explaining what's being tested
10. **Clean up resources** - Use fixtures with teardown for temporary files

---

## Test Checklist

When adding new features, ensure:

- [ ] Unit tests for new functions/methods
- [ ] Integration tests for API interactions
- [ ] Edge cases are covered
- [ ] Error handling is tested
- [ ] Documentation is updated
- [ ] Tests pass locally (`pytest`)
- [ ] Coverage remains above 80% (`pytest --cov`)
- [ ] No warnings or deprecations

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Pydantic Testing](https://docs.pydantic.dev/latest/concepts/testing/)
- [Google API Python Client Testing](https://github.com/googleapis/google-api-python-client)

---

**Last Updated:** 2025-10-28
