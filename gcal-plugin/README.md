# Google Calendar Plugin

Add calendar events using natural language.

## Use Case

You want to quickly add events to Google Calendar without opening a browser. Say "Meeting with Sarah tomorrow at 3pm" and it gets added. The `/gcal` command teaches Claude how to use the CLI. The `/gcal:setup` command walks through authentication.

## Setup

1. Install the plugin:
   ```bash
   /plugin install gcal-plugin@warren-claude-code-plugin-marketplace
   ```

2. Install the CLI:
   ```bash
   uv tool install gcallm
   ```

3. Get OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/apis/credentials):
   - Enable Google Calendar API
   - Create Desktop app OAuth credentials
   - Save somewhere accessible

4. Configure:
   ```bash
   gcallm setup ~/path/to/oauth-keys.json
   claude mcp add gcal npx @anthropic/mcp-google-calendar -s local
   gcallm verify
   ```

## Usage

```bash
gcallm "Meeting with Sarah tomorrow at 3pm"
gcallm "Lunch Tuesday 12-1pm, Standup Wed-Fri 9:30am"
cat events.txt | gcallm
gcallm ask "What's on my calendar today?"
```

Run `/gcal` for the full command reference.

Hope you enjoy!
