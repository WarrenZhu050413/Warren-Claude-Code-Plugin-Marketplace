# Test Suite

Comprehensive test suite for the claude-context-orchestrator plugin.

## Directory Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and shared fixtures
├── run_all_tests.sh         # Master test runner
│
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_snippets_cli.py
│   ├── test_snippet_injector.py
│   └── test_config_paths.py
│
├── integration/             # Integration tests (end-to-end workflows)
│   ├── test_snippets_cli_integration.py
│   └── test_skill_snippets.py
│
├── validation/              # Validation tests (file structure/format)
│   ├── test_file_structure.sh
│   ├── test_format_compliance.sh
│   └── test_pattern_matching.py
│
└── personal/                # Personal tests (gitignored)
    └── (Warren's test files)
```

## Running Tests

### Run All Tests
```bash
bash tests/run_all_tests.sh
```

### Run Specific Test Categories
```bash
# Validation tests only
bash tests/run_all_tests.sh validation

# Unit tests only
bash tests/run_all_tests.sh unit

# Integration tests only
bash tests/run_all_tests.sh integration
```

### Run Specific Test Files
```bash
# Run specific unit test
pytest tests/unit/test_snippets_cli.py -v

# Run specific integration test
pytest tests/integration/test_skill_snippets.py -v

# Run specific validation test
bash tests/validation/test_file_structure.sh
```

### Run with pytest options
```bash
# Run with verbose output
pytest tests/unit/ -v

# Run with output capture disabled (see print statements)
pytest tests/unit/ -s

# Run specific test method
pytest tests/unit/test_snippets_cli.py::TestSnippetManagerInit::test_init_with_empty_dirs -v

# Run tests matching a pattern
pytest tests/ -k "snippet" -v
```

## Test Categories

### Unit Tests (`unit/`)
Fast, isolated tests for individual components:
- **test_snippets_cli.py**: SnippetManager class, CRUD operations
- **test_snippet_injector.py**: Snippet injection logic, pattern matching
- **test_config_paths.py**: Configuration loading and merging

### Integration Tests (`integration/`)
End-to-end workflow tests:
- **test_snippets_cli_integration.py**: Full CLI workflows (create → update → delete)
- **test_skill_snippets.py**: Skills integration with snippet system

### Validation Tests (`validation/`)
File structure and format compliance:
- **test_file_structure.sh**: Directory structure validation
- **test_format_compliance.sh**: YAML frontmatter, naming conventions
- **test_pattern_matching.py**: Regex pattern validation

## Adding New Tests

### For Python tests (pytest):
1. Create test file in appropriate directory (unit/integration/validation)
2. Name file `test_*.py`
3. Use pytest fixtures from `conftest.py`
4. Run with `pytest tests/<category>/test_*.py`

### For Shell script tests:
1. Create test file in `validation/` directory
2. Name file `test_*.sh`
3. Make executable: `chmod +x test_*.sh`
4. Add to `run_all_tests.sh` if needed

## Requirements

- Python 3.7+
- pytest
- pytest-cov (optional, for coverage reports)

Install test dependencies:
```bash
pip install pytest pytest-cov
```

## Continuous Integration

The master test runner (`run_all_tests.sh`) is designed for CI/CD integration:
- Exit code 0 if all tests pass
- Exit code 1 if any tests fail
- Colored output for readability
- Summary statistics

## Coverage

Run tests with coverage report:
```bash
pytest tests/unit tests/integration --cov=scripts --cov-report=html
open htmlcov/index.html
```
