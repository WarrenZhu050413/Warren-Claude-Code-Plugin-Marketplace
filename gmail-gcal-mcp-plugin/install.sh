#!/bin/bash

# Gmail & Google Calendar MCP Plugin Installer
# Installs snippets and MCP configuration for Claude Code

set -e  # Exit on error

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SNIPPETS_DIR="$CLAUDE_DIR/snippets"
CONFIG_FILE="$SNIPPETS_DIR/config.json"

echo "🚀 Installing Gmail & Google Calendar MCP Plugin for Claude Code..."
echo ""

# Check if Claude Code is installed
if [ ! -d "$CLAUDE_DIR" ]; then
    echo "❌ Error: Claude Code directory not found at $CLAUDE_DIR"
    echo "   Please install Claude Code first."
    exit 1
fi

# Create snippets directory if it doesn't exist
mkdir -p "$SNIPPETS_DIR/snippets"

# Copy snippet files
echo "📝 Installing snippets..."
cp -v "$PLUGIN_DIR/snippets/mail.md" "$SNIPPETS_DIR/snippets/"
cp -v "$PLUGIN_DIR/snippets/gcal.md" "$SNIPPETS_DIR/snippets/"

# Merge config entries
echo "⚙️  Updating snippet configuration..."
if [ ! -f "$CONFIG_FILE" ]; then
    # No config exists, create one with our mappings
    cp "$PLUGIN_DIR/config-snippets.json" "$CONFIG_FILE"
    echo "   Created new config.json"
else
    # Config exists, merge our mappings
    echo "   Merging with existing config.json"

    # Backup existing config
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "   Backup created: $CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"

    # Use jq to merge if available, otherwise manual instructions
    if command -v jq &> /dev/null; then
        jq -s '.[0].mappings += .[1].mappings | .[0]' "$CONFIG_FILE" "$PLUGIN_DIR/config-snippets.json" > "$CONFIG_FILE.tmp"
        mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
        echo "   ✅ Configuration merged successfully"
    else
        echo "   ⚠️  jq not installed - you'll need to manually merge config-snippets.json"
        echo "   Add the mappings from config-snippets.json to your $CONFIG_FILE"
    fi
fi

echo ""
echo "✅ Snippets installed successfully!"
echo ""
echo "📋 Next Steps:"
echo "   1. Run ./setup-mcp.sh in your project directory to configure MCP servers"
echo "   2. Get Google OAuth credentials: https://console.cloud.google.com"
echo "   3. Enable Gmail API and Google Calendar API"
echo "   4. Add credentials to .env file"
echo "   5. Restart Claude Code"
echo ""
echo "📖 Usage:"
echo "   • Type keywords like 'email', 'mail', 'calendar', 'gcal' in Claude Code"
echo "   • The context will automatically inject to help with Gmail/Calendar tasks"
echo ""
echo "🎉 Installation complete! See README.md for full documentation."
