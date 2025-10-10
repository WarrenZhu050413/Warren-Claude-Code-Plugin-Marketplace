#!/bin/bash

# MCP Setup Script for Claude Code
# This script sets up Gmail and Google Calendar MCP servers for any project

echo "🚀 Setting up MCP servers for Claude Code..."

# Check if we're in a git repository or a project directory
if [ ! -d ".git" ] && [ ! -f "package.json" ] && [ ! -f "requirements.txt" ]; then
    read -p "⚠️  This doesn't look like a project directory. Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create .claude directory if it doesn't exist
mkdir -p .claude

# Create .mcp.json file
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "gmail": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@gongrzhe/server-gmail-autoauth-mcp"],
      "env": {
        "GMAIL_CLIENT_ID": "${GMAIL_CLIENT_ID}",
        "GMAIL_CLIENT_SECRET": "${GMAIL_CLIENT_SECRET}",
        "GMAIL_REDIRECT_URI": "http://localhost:3000/oauth/callback"
      }
    },
    "google-calendar": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@cocal/google-calendar-mcp"],
      "env": {
        "GOOGLE_CALENDAR_CLIENT_ID": "${GOOGLE_CALENDAR_CLIENT_ID}",
        "GOOGLE_CALENDAR_CLIENT_SECRET": "${GOOGLE_CALENDAR_CLIENT_SECRET}",
        "GOOGLE_CALENDAR_REDIRECT_URI": "http://localhost:3000/oauth/callback"
      }
    }
  }
}
EOF

echo "✅ Created .mcp.json configuration file"

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    cat > .env.example << 'EOF'
# Gmail MCP Server Configuration
GMAIL_CLIENT_ID=your_gmail_client_id_here
GMAIL_CLIENT_SECRET=your_gmail_client_secret_here

# Google Calendar MCP Server Configuration
GOOGLE_CALENDAR_CLIENT_ID=your_calendar_client_id_here
GOOGLE_CALENDAR_CLIENT_SECRET=your_calendar_client_secret_here
EOF
    echo "✅ Created .env.example file"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found. To complete setup:"
    echo "   1. Copy .env.example to .env"
    echo "   2. Add your Google OAuth credentials"
    echo ""
    read -p "Would you like to create .env from .env.example now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ Created .env file - please add your credentials"
    fi
fi

# Add .env to .gitignore if it exists and .env isn't already there
if [ -f ".gitignore" ]; then
    if ! grep -q "^\.env$" .gitignore; then
        echo "" >> .gitignore
        echo "# Environment variables" >> .gitignore
        echo ".env" >> .gitignore
        echo "✅ Added .env to .gitignore"
    fi
fi

echo ""
echo "🎉 MCP setup complete!"
echo ""
echo "Next steps:"
echo "1. Get Google OAuth credentials from https://console.cloud.google.com"
echo "2. Enable Gmail API and Google Calendar API"
echo "3. Add credentials to your .env file or set as environment variables"
echo "4. Restart Claude Code to load the new MCP servers"
echo ""
echo "The MCP servers will be available in Claude Code after restart."