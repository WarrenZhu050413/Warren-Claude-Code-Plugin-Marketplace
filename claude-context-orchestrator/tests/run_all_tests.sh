#!/usr/bin/env bash
# Master test runner - executes all tests
#
# Usage:
#   ./run_all_tests.sh              # Run all tests
#   ./run_all_tests.sh unit         # Run only unit tests
#   ./run_all_tests.sh integration  # Run only integration tests
#   ./run_all_tests.sh validation   # Run only validation tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "              CLAUDE CONTEXT ORCHESTRATOR TEST SUITE"
echo "========================================================================"
echo ""

# Track results
PASSED=0
FAILED=0
CATEGORY="${1:-all}"

# Helper function to run a test suite
run_test() {
    local name="$1"
    local command="$2"

    echo ""
    echo -e "${BLUE}Running $name...${NC}"
    echo "------------------------------------------------------------------------"

    if eval "$command"; then
        echo -e "${GREEN}✓ $name passed${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ $name failed${NC}"
        ((FAILED++))
        return 1
    fi
}

# Validation Tests (shell scripts)
run_validation_tests() {
    echo ""
    echo "========================================================================"
    echo "                      VALIDATION TESTS"
    echo "========================================================================"

    run_test "File Structure" "bash tests/validation/test_file_structure.sh"
    run_test "Format Compliance" "bash tests/validation/test_format_compliance.sh"
    run_test "Pattern Matching" "python3 tests/validation/test_pattern_matching.py"
}

# Unit Tests (pytest)
run_unit_tests() {
    echo ""
    echo "========================================================================"
    echo "                        UNIT TESTS"
    echo "========================================================================"

    run_test "Unit Tests" "pytest tests/unit/ -v"
}

# Integration Tests (pytest)
run_integration_tests() {
    echo ""
    echo "========================================================================"
    echo "                     INTEGRATION TESTS"
    echo "========================================================================"

    run_test "Integration Tests" "pytest tests/integration/ -v"
}

# Run tests based on category
case "$CATEGORY" in
    validation)
        run_validation_tests
        ;;
    unit)
        run_unit_tests
        ;;
    integration)
        run_integration_tests
        ;;
    all|*)
        run_validation_tests
        run_unit_tests
        run_integration_tests
        ;;
esac

# Summary
echo ""
echo "========================================================================"
echo "                           TEST SUMMARY"
echo "========================================================================"
echo ""
echo "Test Suites: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}, $((PASSED + FAILED)) total"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo "========================================================================"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo "========================================================================"
    exit 1
fi
