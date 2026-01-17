#!/bin/bash
# Integration test script for Google Drive Organizer

set -e  # Exit on error

echo "🧪 Running integration tests..."

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL=0
PASSED=0
FAILED=0

# Helper function
run_test() {
    local test_name="$1"
    shift

    echo -e "${YELLOW}Running: ${test_name}${NC}"

    if "$@"; then
        ((PASSED++))
        echo -e "${GREEN}✓ PASSED${NC} - ${test_name}"
    else
        ((FAILED++))
        echo -e "${RED}✗ FAILED${NC} - ${test_name}"
    fi

    ((TOTAL++))
}

# Test 1: Import test
test_import() {
    python3 -c "import sys; sys.path.insert(0, '.'); from src.config_manager import ConfigManager; from src.cli_interface import CLI; from src.main import main; print('✓ All imports successful')"
}

# Test 2: Config manager
test_config_manager() {
    python3 -c "import sys; sys.path.insert(0, '.'); from src.config_manager import ConfigManager; cm = ConfigManager(); cm.get('confidence_thresholds.auto_execute')"
}

# Test 3: CLI interface
test_cli_interface() {
    python3 -c "import sys; sys.path.insert(0, '.'); from src.cli_interface import CLI; cli = CLI(); cli is not None"
}

# Test 4: Main entry point
test_main_entry() {
    python3 -c "import sys; sys.path.insert(0, '.'); from src.main import main; main is not None"
}

# Run all tests
echo ""
echo "=== Running integration tests ==="
echo ""

run_test "Import all modules" test_import
run_test "Config manager functionality" test_config_manager
run_test "CLI interface loads" test_cli_interface
run_test "Main entry point exists" test_main_entry

# Run pytest test suite
echo ""
echo "=== Running pytest suite ==="
echo ""

if pytest tests/ -v --tb=short; then
    ((PASSED += $? == 0))
    echo -e "${GREEN}✓ Pytest suite passed${NC}"
else
    ((FAILED += 1))
    echo -e "${RED}✗ Pytest suite failed${NC}"
fi

((TOTAL++))

# Summary
echo ""
echo "=== Test Summary ==="
echo ""
echo -e "Total tests: ${TOTAL}"
echo -e "${GREEN}Passed: ${PASSED}${NC}"
echo -e "Failed: ${FAILED}${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠  Some tests failed${NC}"
    exit 1
fi
