# Gmail & Google Calendar MCP Plugin for Claude Code

A comprehensive plugin that adds Gmail and Google Calendar automation capabilities to Claude Code using MCP (Model Context Protocol) servers and smart context injection.

## Quick Start

### 1. Install the Marketplace

First, add Warren's plugin marketplace to Claude Code:

```bash
/plugin marketplace add WZhu21/Warren-Claude-Code-Plugin-Marketplace
```

### 2. Install the Plugin

```bash
/plugin install gmail-gcal-mcp@warren
```

### 3. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project and enable Gmail API + Google Calendar API
3. Create OAuth 2.0 credentials (Web application)
4. Add redirect URI: `http://localhost:3000/oauth/callback`
5. Save your Client ID and Client Secret

See `examples/oauth-setup-guide.md` for detailed instructions.

### 4. Configure Your Project

Run the setup command in your project directory:

```bash
/setup-mcp
```

Or use the bash script:

```bash
cd /path/to/your/project
./setup-mcp.sh
```

### 5. Add Credentials

Edit your project's `.env` file:

```bash
GMAIL_CLIENT_ID=your_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret
GOOGLE_CALENDAR_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CALENDAR_CLIENT_SECRET=your_client_secret
```

### 6. Restart Claude Code

Your Gmail and Calendar automation is now ready!

## Usage

Simply mention keywords in your conversation:

**Email**:
```
"Send an email to john@example.com about the meeting"
"Search my inbox for messages from Sarah last week"
```

**Calendar**:
```
"Add a team meeting tomorrow at 2pm"
"What's on my calendar this week?"
```

The plugin automatically injects relevant context and uses MCP servers to interact with Gmail and Google Calendar.

## Slash Commands

### /read-snippets

Read and display Gmail and/or Google Calendar snippets.

```bash
/read-snippets              # Read all snippets (default)
/read-snippets mail         # Read only email snippet
/read-snippets gcal         # Read only calendar snippet
```

**Behavior**: Default reads ALL snippets. With arguments, filters to specific snippets. No confirmation needed.

### /create-snippet

Create a new Gmail or Google Calendar snippet.

```bash
/create-snippet mail with rules for professional emails
/create-snippet gcal with timezone PST
/create-snippet --force calendar add default duration 30 mins
```

**Behavior**: Asks for confirmation before creating (unless `-f` or `--force`).

### /update-snippet

Update an existing snippet.

```bash
/update-snippet mail add signature with title
/update-snippet gcal set default reminder to 15 minutes
/update-snippet --force email change style to casual
```

**Behavior**: Shows before/after comparison. Creates backup. Asks for confirmation (unless `-f` or `--force`).

### /delete-snippet

Delete a snippet with confirmation.

```bash
/delete-snippet mail
/delete-snippet gcal --force
```

**Behavior**: Shows content before deletion. Creates backup. Asks for confirmation (unless `-f` or `--force`).

### /setup-mcp

Set up MCP servers for the current project.

```bash
/setup-mcp                  # Setup in current directory
/setup-mcp --force          # Skip confirmation
/setup-mcp -f /path/to/project  # Setup in specific directory
```

**Behavior**: Creates `.mcp.json` and `.env.example`. Updates `.gitignore`. Asks for confirmation (unless `-f` or `--force`).

## Configuration

### Snippet Triggers

The plugin injects context automatically when you use these keywords:

**Email triggers**: `email`, `mail`, `e-mail`, `message`, `inbox`, `send to`, `send message`

**Calendar triggers**: `gcal`, `g-cal`, `google calendar`, `calendar`, `event`, `schedule`, `appointment`

### MCP Server Configuration

Each project gets a `.mcp.json` file configuring:
- Gmail MCP server (`@gongrzhe/server-gmail-autoauth-mcp`)
- Google Calendar MCP server (`@cocal/google-calendar-mcp`)

Both use OAuth 2.0 for secure authentication.

### Customization

**Modify snippets** in `~/.claude/snippets/snippets/`:
- `mail.md` - Email automation rules
- `gcal.md` - Calendar automation rules

**Add custom triggers** by editing `~/.claude/snippets/config.json`.

## Troubleshooting

### MCP Servers Not Loading

1. Ensure `.mcp.json` is in your project root
2. Check `.env` has valid credentials
3. Restart Claude Code
4. Check logs for MCP errors

### OAuth Authentication Fails

1. Verify credentials in Google Cloud Console
2. Ensure redirect URI is exactly: `http://localhost:3000/oauth/callback`
3. Check Gmail API and Calendar API are enabled
4. Add your email as a test user
5. Clear browser cookies

### Snippets Not Triggering

1. Check `~/.claude/snippets/config.json` has the mappings
2. Ensure snippet files exist in `~/.claude/snippets/snippets/`
3. Restart Claude Code after config changes

### Environment Variables Not Loading

1. Ensure `.env` is in project root (same directory as `.mcp.json`)
2. Verify no extra quotes or spaces in `.env`
3. Check `.env` is not being ignored by `.gitignore`

## Security

- **Never commit** `.env` files to git
- OAuth credentials stored locally in `.env`
- MCP servers handle authentication securely
- Emails are drafted for review before sending

## Uninstallation

```bash
/plugin uninstall gmail-gcal-mcp
```

Or manually:

```bash
# Remove snippets
rm ~/.claude/snippets/snippets/mail.md
rm ~/.claude/snippets/snippets/gcal.md

# Edit config.json to remove mappings

# Remove MCP configuration from projects
rm /path/to/project/.mcp.json
rm /path/to/project/.env
```

---

## Features

- **Gmail Integration**: Send, read, search, and manage emails directly from Claude Code
- **Google Calendar Integration**: Create, update, and manage calendar events
- **Smart Context Injection**: Automatically injects relevant context when you mention keywords
- **OAuth Authentication**: Secure authentication using Google OAuth 2.0
- **Slash Commands**: Manage snippets and MCP configuration with interactive commands
- **HTML Output**: Generate rich HTML documentation with the `/html` command

## What's Included

- **MCP Servers**:
  - `@gongrzhe/server-gmail-autoauth-mcp` - Gmail automation with auto-authentication
  - `@cocal/google-calendar-mcp` - Google Calendar integration

- **Smart Snippets**:
  - `mail.md` - Email handling context (triggered by: email, mail, message, inbox, send)
  - `gcal.md` - Calendar context (triggered by: gcal, calendar, event, schedule, appointment)

- **Slash Commands**:
  - `/create-snippet` - Create new Gmail or Calendar snippets
  - `/update-snippet` - Update existing snippets
  - `/delete-snippet` - Delete snippets with confirmation
  - `/read-snippets` - Read and display current snippets
  - `/setup-mcp` - Set up MCP servers for current project

- **Example Command**:
  - `HTML.md` - Generate compact, information-dense HTML output

## Architecture

```
┌─────────────────┐
│   Claude Code   │
│                 │
│  ┌───────────┐  │
│  │ Snippets  │  │  (Inject context when keywords detected)
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │MCP Servers│  │  (Gmail & Calendar APIs)
│  └───────────┘  │
└────────┬────────┘
         │
         │ OAuth 2.0
         ▼
┌─────────────────┐
│  Google APIs    │
│  • Gmail API    │
│  • Calendar API │
└─────────────────┘
```

## File Structure

```
gmail-gcal-mcp-plugin/
├── .claude-plugin/
│   └── plugin.json         # Plugin manifest
├── README.md                # This file
├── install.sh               # Legacy installer (use /plugin install instead)
├── setup-mcp.sh            # MCP server setup script
├── config-snippets.json    # Snippet configuration
├── commands/                # Slash commands
│   ├── create-snippet.md   # Create new snippets
│   ├── update-snippet.md   # Update existing snippets
│   ├── delete-snippet.md   # Delete snippets
│   ├── read-snippets.md    # Read snippet contents
│   ├── setup-mcp.md        # Setup MCP servers
│   └── examples/
│       └── HTML.md         # HTML output generation command
├── snippets/
│   ├── mail.md            # Email automation context
│   └── gcal.md           # Calendar automation context
└── examples/
    ├── usage-examples.md   # Detailed usage examples
    └── oauth-setup-guide.md  # OAuth setup walkthrough
```

## Contributing

Found a bug or have a feature request?

1. Check existing issues in the marketplace repository
2. Create detailed bug reports with:
   - Claude Code version
   - OS and Node.js version
   - Error messages
   - Steps to reproduce

## License

This plugin uses:
- [@gongrzhe/server-gmail-autoauth-mcp](https://www.npmjs.com/package/@gongrzhe/server-gmail-autoauth-mcp)
- [@cocal/google-calendar-mcp](https://www.npmjs.com/package/@cocal/google-calendar-mcp)

Check their respective licenses for usage terms.

## Support

- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [Plugin Marketplace Documentation](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Google OAuth 2.0 Setup Guide](https://developers.google.com/identity/protocols/oauth2)

## Changelog

### v1.0.0 (2025-10-10)
- Initial release
- Gmail integration with auto-auth
- Google Calendar integration
- Smart snippet context injection
- Slash commands for snippet management
- HTML output command
- Automated setup scripts

---

**Made with Claude Code**
