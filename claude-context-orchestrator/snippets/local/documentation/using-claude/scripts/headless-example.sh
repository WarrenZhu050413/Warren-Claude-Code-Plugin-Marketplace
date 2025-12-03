#!/bin/bash
#
# Headless Claude Code Examples
#
# This script demonstrates various headless automation patterns for Claude Code.
# Use this as a reference for CI/CD, batch processing, and automated workflows.

set -e  # Exit on error

echo "🤖 Claude Code Headless Automation Examples"
echo "============================================="
echo ""

# ==============================================================================
# Example 1: Simple One-Shot Command
# ==============================================================================

example_1_oneshot() {
    echo "📝 Example 1: Simple One-Shot Command"
    echo "--------------------------------------"

    # Basic one-shot task
    claude -p "What is 2 + 2?"

    echo ""
    echo "✅ Example 1 complete"
    echo ""
}

# ==============================================================================
# Example 2: Structured JSON Output
# ==============================================================================

example_2_json_output() {
    echo "📝 Example 2: Structured JSON Output"
    echo "-------------------------------------"

    # Get JSON output for parsing
    echo "Running command with JSON output..."
    OUTPUT=$(claude --output-format "stream-json" -p "Calculate 10 + 5" 2>/dev/null | jq .)

    echo "Full JSON output:"
    echo "$OUTPUT"

    # Extract specific fields
    echo ""
    echo "Extracting result..."
    RESULT=$(echo "$OUTPUT" | jq -r 'select(.type == "result") | .result')
    echo "Result: $RESULT"

    # Extract cost
    echo ""
    echo "Extracting cost..."
    COST=$(echo "$OUTPUT" | jq -r 'select(.type == "result") | .total_cost_usd')
    echo "Cost: \$$COST USD"

    echo ""
    echo "✅ Example 2 complete"
    echo ""
}

# ==============================================================================
# Example 3: Session Continuation
# ==============================================================================

example_3_session_continuation() {
    echo "📝 Example 3: Session Continuation"
    echo "----------------------------------"

    # Start first task and capture session ID
    echo "Starting first task..."
    OUTPUT=$(claude --debug --output-format "stream-json" -p "Remember: my favorite color is blue" 2>&1)
    SESSION_ID=$(echo "$OUTPUT" | grep -o '"session_id":"[^"]*"' | head -1 | cut -d'"' -f4)

    echo "Session ID: $SESSION_ID"

    # Continue conversation with session ID
    echo ""
    echo "Continuing conversation..."
    claude -c "$SESSION_ID" -p "What's my favorite color?" 2>/dev/null

    echo ""
    echo "✅ Example 3 complete"
    echo ""
}

# ==============================================================================
# Example 4: Headless Automation with Permissions
# ==============================================================================

example_4_automation() {
    echo "📝 Example 4: Headless Automation (Bypass Permissions)"
    echo "-------------------------------------------------------"

    # Create test directory
    TEST_DIR=$(mktemp -d)
    echo "Test directory: $TEST_DIR"

    # Run automated task with bypassed permissions
    cd "$TEST_DIR"
    claude --permission-mode bypassPermissions \
           --max-turns 3 \
           -p "Create a file called 'hello.txt' with content 'Hello, World!'" 2>/dev/null

    # Verify file was created
    echo ""
    if [ -f "hello.txt" ]; then
        echo "✅ File created successfully!"
        echo "Content: $(cat hello.txt)"
    else
        echo "❌ File was not created"
    fi

    # Cleanup
    rm -rf "$TEST_DIR"

    echo ""
    echo "✅ Example 4 complete"
    echo ""
}

# ==============================================================================
# Example 5: Read-Only Analysis
# ==============================================================================

example_5_readonly() {
    echo "📝 Example 5: Read-Only Analysis"
    echo "--------------------------------"

    # Analyze codebase without making changes
    # Restrict to read-only tools
    claude --allowed-tools "Read,Grep,Glob" \
           --max-turns 3 \
           --output-format compact-text \
           -p "List all markdown files in the current directory" 2>/dev/null

    echo ""
    echo "✅ Example 5 complete"
    echo ""
}

# ==============================================================================
# Example 6: Batch Processing
# ==============================================================================

example_6_batch_processing() {
    echo "📝 Example 6: Batch Processing"
    echo "------------------------------"

    # Create test files
    TEST_DIR=$(mktemp -d)
    echo "Test directory: $TEST_DIR"

    # Create sample files
    echo "def add(a, b): return a + b" > "$TEST_DIR/math.py"
    echo "def subtract(a, b): return a - b" > "$TEST_DIR/calc.py"

    # Process each file
    for file in "$TEST_DIR"/*.py; do
        echo ""
        echo "Processing: $(basename "$file")"
        claude --permission-mode bypassPermissions \
               --max-turns 2 \
               --output-format compact-text \
               -p "Explain what this code does: $(cat "$file")" 2>/dev/null | head -3
    done

    # Cleanup
    rm -rf "$TEST_DIR"

    echo ""
    echo "✅ Example 6 complete"
    echo ""
}

# ==============================================================================
# Example 7: CI/CD Code Review Pattern
# ==============================================================================

example_7_code_review() {
    echo "📝 Example 7: CI/CD Code Review Pattern"
    echo "---------------------------------------"

    # Simulate code review task
    REVIEW_OUTPUT=$(claude --permission-mode bypassPermissions \
                           --allowed-tools "Read,Grep,Glob" \
                           --max-turns 3 \
                           --output-format compact-text \
                           -p "Review the current directory structure and provide a brief summary" 2>/dev/null)

    echo "Code Review Summary:"
    echo "$REVIEW_OUTPUT" | head -10

    # Save to file
    echo "$REVIEW_OUTPUT" > /tmp/code_review.md
    echo ""
    echo "Full review saved to: /tmp/code_review.md"

    echo ""
    echo "✅ Example 7 complete"
    echo ""
}

# ==============================================================================
# Example 8: Cost Monitoring
# ==============================================================================

example_8_cost_monitoring() {
    echo "📝 Example 8: Cost Monitoring"
    echo "-----------------------------"

    # Run task and extract cost
    OUTPUT=$(claude --output-format "stream-json" \
                    -p "What is the capital of France?" 2>/dev/null)

    COST=$(echo "$OUTPUT" | jq -r 'select(.type == "result") | .total_cost_usd')
    INPUT_TOKENS=$(echo "$OUTPUT" | jq -r 'select(.type == "result") | .usage.input_tokens')
    OUTPUT_TOKENS=$(echo "$OUTPUT" | jq -r 'select(.type == "result") | .usage.output_tokens')

    echo "Task completed!"
    echo "Cost: \$$COST USD"
    echo "Input tokens: $INPUT_TOKENS"
    echo "Output tokens: $OUTPUT_TOKENS"

    echo ""
    echo "✅ Example 8 complete"
    echo ""
}

# ==============================================================================
# Example 9: Debug Mode Analysis
# ==============================================================================

example_9_debug_mode() {
    echo "📝 Example 9: Debug Mode Analysis"
    echo "---------------------------------"

    # Run with debug mode
    OUTPUT=$(claude --debug --output-format "stream-json" -p "Hello, Claude!" 2>&1)

    # Extract session ID
    SESSION_ID=$(echo "$OUTPUT" | grep -o '"session_id":"[^"]*"' | head -1 | cut -d'"' -f4)

    echo "Session ID: $SESSION_ID"
    echo ""
    echo "Debug logs location: ~/.claude/debug/$SESSION_ID/"

    # Show what's in debug logs
    if [ -d "$HOME/.claude/debug/$SESSION_ID" ]; then
        echo ""
        echo "Debug log files:"
        ls -lh "$HOME/.claude/debug/$SESSION_ID/"

        echo ""
        echo "First 5 lines of debug log:"
        head -5 "$HOME/.claude/debug/$SESSION_ID/"*
    fi

    echo ""
    echo "✅ Example 9 complete"
    echo ""
}

# ==============================================================================
# Example 10: Model Selection
# ==============================================================================

example_10_model_selection() {
    echo "📝 Example 10: Model Selection"
    echo "------------------------------"

    echo "Demonstrating different models for different tasks..."

    # Simple task with Haiku (fast and cheap)
    echo ""
    echo "1. Using Haiku for simple task:"
    claude --model haiku \
           --max-turns 1 \
           --output-format compact-text \
           -p "What is 2 + 2?" 2>/dev/null

    # Standard task with Sonnet (default)
    echo ""
    echo "2. Using Sonnet for general coding:"
    claude --model sonnet \
           --max-turns 2 \
           --output-format compact-text \
           -p "Explain what a for loop does in Python" 2>/dev/null | head -5

    # Complex task with Opus (highest intelligence)
    echo ""
    echo "3. Using Opus for complex reasoning:"
    echo "(Skipped in demo - use Opus for architecture design, code reviews, etc.)"

    echo ""
    echo "✅ Example 10 complete"
    echo ""
}

# ==============================================================================
# Main Menu
# ==============================================================================

show_menu() {
    echo "Select an example to run:"
    echo ""
    echo "  1) Simple One-Shot Command"
    echo "  2) Structured JSON Output"
    echo "  3) Session Continuation"
    echo "  4) Headless Automation (Bypass Permissions)"
    echo "  5) Read-Only Analysis"
    echo "  6) Batch Processing"
    echo "  7) CI/CD Code Review Pattern"
    echo "  8) Cost Monitoring"
    echo "  9) Debug Mode Analysis"
    echo " 10) Model Selection"
    echo " 11) Run ALL examples"
    echo "  q) Quit"
    echo ""
}

run_all_examples() {
    example_1_oneshot
    example_2_json_output
    example_3_session_continuation
    example_4_automation
    example_5_readonly
    example_6_batch_processing
    example_7_code_review
    example_8_cost_monitoring
    example_9_debug_mode
    example_10_model_selection
}

# ==============================================================================
# Main Script
# ==============================================================================

if [ $# -eq 0 ]; then
    # Interactive mode
    while true; do
        show_menu
        read -p "Enter your choice: " choice
        echo ""

        case $choice in
            1) example_1_oneshot ;;
            2) example_2_json_output ;;
            3) example_3_session_continuation ;;
            4) example_4_automation ;;
            5) example_5_readonly ;;
            6) example_6_batch_processing ;;
            7) example_7_code_review ;;
            8) example_8_cost_monitoring ;;
            9) example_9_debug_mode ;;
            10) example_10_model_selection ;;
            11) run_all_examples ;;
            q|Q) echo "Goodbye!"; exit 0 ;;
            *) echo "Invalid choice. Please try again."; echo "" ;;
        esac

        read -p "Press Enter to continue..."
        clear
    done
else
    # Non-interactive mode - run specific example
    case $1 in
        1) example_1_oneshot ;;
        2) example_2_json_output ;;
        3) example_3_session_continuation ;;
        4) example_4_automation ;;
        5) example_5_readonly ;;
        6) example_6_batch_processing ;;
        7) example_7_code_review ;;
        8) example_8_cost_monitoring ;;
        9) example_9_debug_mode ;;
        10) example_10_model_selection ;;
        all) run_all_examples ;;
        *) echo "Usage: $0 [1-10|all]"; exit 1 ;;
    esac
fi
