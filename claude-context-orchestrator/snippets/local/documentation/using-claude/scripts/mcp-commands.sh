#!/bin/bash
#
# MCP Server Management Commands
#
# This script demonstrates common MCP server management operations.
# Use this as a reference for configuring and managing MCP servers.

set -e  # Exit on error

echo "🔧 Claude MCP Server Management Examples"
echo "=========================================="
echo ""

# ==============================================================================
# Example 1: List All MCP Servers
# ==============================================================================

example_1_list_servers() {
    echo "📝 Example 1: List All MCP Servers"
    echo "----------------------------------"

    echo "Listing all configured MCP servers..."
    claude mcp list

    echo ""
    echo "✅ Example 1 complete"
    echo ""
}

# ==============================================================================
# Example 2: Add Simple MCP Server
# ==============================================================================

example_2_add_simple_server() {
    echo "📝 Example 2: Add Simple MCP Server"
    echo "-----------------------------------"

    echo "Adding Playwright MCP server (local scope)..."
    claude mcp add playwright npx @playwright/mcp@latest -s local || echo "Server may already exist"

    echo ""
    echo "Verifying server was added..."
    claude mcp list | grep playwright && echo "✅ Playwright server added" || echo "❌ Failed to add server"

    echo ""
    echo "✅ Example 2 complete"
    echo ""
}

# ==============================================================================
# Example 3: Add MCP Server with JSON Config
# ==============================================================================

example_3_add_json_server() {
    echo "📝 Example 3: Add MCP Server with JSON Config"
    echo "---------------------------------------------"

    echo "Adding Playwright MCP with extension support..."
    claude mcp add-json playwright-ext '{
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--extension"
      ],
      "env": {
        "PLAYWRIGHT_MCP_EXTENSION_TOKEN": "demo-token"
      }
    }' -s local || echo "Server may already exist"

    echo ""
    echo "Getting server details..."
    claude mcp get playwright-ext || echo "Server not found"

    echo ""
    echo "✅ Example 3 complete"
    echo ""
}

# ==============================================================================
# Example 4: Add Exa (Web Search) MCP
# ==============================================================================

example_4_add_exa() {
    echo "📝 Example 4: Add Exa (Web Search) MCP"
    echo "--------------------------------------"

    echo "Note: This example requires a valid Exa API key"
    echo ""

    # Check if EXA_API_KEY is set
    if [ -z "$EXA_API_KEY" ]; then
        echo "⚠️  EXA_API_KEY environment variable not set"
        echo "To add Exa MCP, run:"
        echo "export EXA_API_KEY='your-api-key'"
        echo "claude mcp add exa \"https://mcp.exa.ai/mcp?exaApiKey=\$EXA_API_KEY\" -s global"
    else
        echo "Adding Exa MCP server (global scope)..."
        claude mcp add exa "https://mcp.exa.ai/mcp?exaApiKey=$EXA_API_KEY" -s global || echo "Server may already exist"

        echo ""
        echo "Verifying Exa server..."
        claude mcp list | grep exa && echo "✅ Exa server added" || echo "❌ Failed to add server"
    fi

    echo ""
    echo "✅ Example 4 complete"
    echo ""
}

# ==============================================================================
# Example 5: Add Filesystem MCP
# ==============================================================================

example_5_add_filesystem() {
    echo "📝 Example 5: Add Filesystem MCP"
    echo "--------------------------------"

    # Create a test directory
    TEST_DIR="/tmp/mcp-test"
    mkdir -p "$TEST_DIR"

    echo "Adding filesystem MCP for directory: $TEST_DIR"
    claude mcp add filesystem npx @modelcontextprotocol/server-filesystem "$TEST_DIR" -s local || echo "Server may already exist"

    echo ""
    echo "Verifying filesystem server..."
    claude mcp list | grep filesystem && echo "✅ Filesystem server added" || echo "❌ Failed to add server"

    echo ""
    echo "✅ Example 5 complete"
    echo ""
}

# ==============================================================================
# Example 6: Get Server Details
# ==============================================================================

example_6_get_server_details() {
    echo "📝 Example 6: Get Server Details"
    echo "--------------------------------"

    # Try to get details for playwright server
    echo "Getting details for 'playwright' server..."
    claude mcp get playwright || echo "Server not found"

    echo ""
    echo "✅ Example 6 complete"
    echo ""
}

# ==============================================================================
# Example 7: Remove MCP Server
# ==============================================================================

example_7_remove_server() {
    echo "📝 Example 7: Remove MCP Server"
    echo "-------------------------------"

    echo "⚠️  This example will remove the 'playwright-ext' server if it exists"
    echo ""

    # Remove the server we added in example 3
    echo "Removing 'playwright-ext' server..."
    claude mcp remove playwright-ext -s local || echo "Server not found or already removed"

    echo ""
    echo "Verifying removal..."
    claude mcp list | grep -q playwright-ext && echo "❌ Server still exists" || echo "✅ Server removed"

    echo ""
    echo "✅ Example 7 complete"
    echo ""
}

# ==============================================================================
# Example 8: Complete Playwright Setup with Config File
# ==============================================================================

example_8_complete_playwright_setup() {
    echo "📝 Example 8: Complete Playwright Setup with Config File"
    echo "--------------------------------------------------------"

    # Create a temporary config file
    CONFIG_FILE="/tmp/playwright-mcp-config.json"

    echo "Creating Playwright config file at: $CONFIG_FILE"
    cat > "$CONFIG_FILE" << 'EOF'
{
  "browser": "chrome",
  "launchOptions": {
    "channel": "chrome",
    "headless": false,
    "args": [
      "--disable-extensions"
    ]
  }
}
EOF

    echo ""
    echo "Config file contents:"
    cat "$CONFIG_FILE"

    echo ""
    echo "Adding Playwright MCP with config file..."
    claude mcp add-json playwright-configured "{
      \"command\": \"npx\",
      \"args\": [
        \"@playwright/mcp@latest\",
        \"--config\",
        \"$CONFIG_FILE\"
      ]
    }" -s local || echo "Server may already exist"

    echo ""
    echo "Verifying server configuration..."
    claude mcp get playwright-configured || echo "Server not found"

    echo ""
    echo "Cleaning up..."
    claude mcp remove playwright-configured -s local 2>/dev/null || true
    rm -f "$CONFIG_FILE"

    echo ""
    echo "✅ Example 8 complete"
    echo ""
}

# ==============================================================================
# Example 9: Import from Claude Desktop
# ==============================================================================

example_9_import_from_desktop() {
    echo "📝 Example 9: Import from Claude Desktop"
    echo "----------------------------------------"

    echo "Note: This only works on Mac and WSL"
    echo ""

    # Check if Claude Desktop config exists
    DESKTOP_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

    if [ -f "$DESKTOP_CONFIG" ]; then
        echo "Claude Desktop configuration found!"
        echo "Importing MCP servers from Claude Desktop..."
        claude mcp add-from-claude-desktop || echo "Import failed or no servers to import"

        echo ""
        echo "Listing imported servers..."
        claude mcp list
    else
        echo "⚠️  Claude Desktop configuration not found"
        echo "Expected location: $DESKTOP_CONFIG"
        echo ""
        echo "To use this feature, install Claude Desktop first:"
        echo "https://claude.ai/download"
    fi

    echo ""
    echo "✅ Example 9 complete"
    echo ""
}

# ==============================================================================
# Example 10: Reset Project Choices
# ==============================================================================

example_10_reset_project_choices() {
    echo "📝 Example 10: Reset Project Choices"
    echo "------------------------------------"

    echo "This command clears all stored project-scoped server approvals"
    echo ""

    # Reset project choices
    claude mcp reset-project-choices || echo "No project choices to reset"

    echo ""
    echo "✅ Example 10 complete"
    echo ""
}

# ==============================================================================
# Example 11: Check MCP Server Connection Status
# ==============================================================================

example_11_check_connection() {
    echo "📝 Example 11: Check MCP Server Connection Status"
    echo "-------------------------------------------------"

    echo "Listing servers with connection status..."
    claude mcp list

    echo ""
    echo "Looking for connected servers:"
    claude mcp list | grep "✓ Connected" || echo "No connected servers found"

    echo ""
    echo "Looking for disconnected servers:"
    claude mcp list | grep "✗ Disconnected" || echo "All servers connected!"

    echo ""
    echo "✅ Example 11 complete"
    echo ""
}

# ==============================================================================
# Main Menu
# ==============================================================================

show_menu() {
    echo "Select an example to run:"
    echo ""
    echo "  1) List All MCP Servers"
    echo "  2) Add Simple MCP Server (Playwright)"
    echo "  3) Add MCP Server with JSON Config"
    echo "  4) Add Exa (Web Search) MCP"
    echo "  5) Add Filesystem MCP"
    echo "  6) Get Server Details"
    echo "  7) Remove MCP Server"
    echo "  8) Complete Playwright Setup with Config File"
    echo "  9) Import from Claude Desktop"
    echo " 10) Reset Project Choices"
    echo " 11) Check MCP Server Connection Status"
    echo " 12) Run ALL examples"
    echo "  q) Quit"
    echo ""
}

run_all_examples() {
    example_1_list_servers
    example_2_add_simple_server
    example_3_add_json_server
    example_4_add_exa
    example_5_add_filesystem
    example_6_get_server_details
    example_7_remove_server
    example_8_complete_playwright_setup
    example_9_import_from_desktop
    example_10_reset_project_choices
    example_11_check_connection
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
            1) example_1_list_servers ;;
            2) example_2_add_simple_server ;;
            3) example_3_add_json_server ;;
            4) example_4_add_exa ;;
            5) example_5_add_filesystem ;;
            6) example_6_get_server_details ;;
            7) example_7_remove_server ;;
            8) example_8_complete_playwright_setup ;;
            9) example_9_import_from_desktop ;;
            10) example_10_reset_project_choices ;;
            11) example_11_check_connection ;;
            12) run_all_examples ;;
            q|Q) echo "Goodbye!"; exit 0 ;;
            *) echo "Invalid choice. Please try again."; echo "" ;;
        esac

        read -p "Press Enter to continue..."
        clear
    done
else
    # Non-interactive mode - run specific example
    case $1 in
        1) example_1_list_servers ;;
        2) example_2_add_simple_server ;;
        3) example_3_add_json_server ;;
        4) example_4_add_exa ;;
        5) example_5_add_filesystem ;;
        6) example_6_get_server_details ;;
        7) example_7_remove_server ;;
        8) example_8_complete_playwright_setup ;;
        9) example_9_import_from_desktop ;;
        10) example_10_reset_project_choices ;;
        11) example_11_check_connection ;;
        all) run_all_examples ;;
        *) echo "Usage: $0 [1-11|all]"; exit 1 ;;
    esac
fi
