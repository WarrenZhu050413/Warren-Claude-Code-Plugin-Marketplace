# Complete OAuth Setup Guide

This guide walks you through getting Google OAuth credentials for the Gmail and Calendar MCP servers.

## Prerequisites

- Google account
- Access to Google Cloud Console

## Step-by-Step Guide

### 1. Access Google Cloud Console

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Sign in with your Google account

### 2. Create a New Project

1. Click on the project dropdown (top left, next to "Google Cloud")
2. Click "NEW PROJECT"
3. Fill in:
   - **Project name**: `Claude MCP Integration` (or your preferred name)
   - **Organization**: Leave as "No organization" (unless you have one)
4. Click "CREATE"
5. Wait for project creation (usually 10-30 seconds)
6. Select your new project from the dropdown

### 3. Enable Required APIs

#### Enable Gmail API

1. Click the hamburger menu (☰) → "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "ENABLE"
5. Wait for activation

#### Enable Google Calendar API

1. Go back to "Library" (or use back button)
2. Search for "Google Calendar API"
3. Click on "Google Calendar API"
4. Click "ENABLE"
5. Wait for activation

### 4. Configure OAuth Consent Screen

1. Click hamburger menu (☰) → "APIs & Services" → "OAuth consent screen"

2. **Choose User Type**:
   - **External**: If using personal Gmail (most common)
   - **Internal**: If using Google Workspace with organization
   - Click "CREATE"

3. **App Information**:
   - **App name**: `Claude Code MCP`
   - **User support email**: Select your email
   - **Developer contact**: Enter your email

4. **App Domain** (Optional):
   - Leave blank for now

5. **Scopes** (click "ADD OR REMOVE SCOPES"):
   - Search and add:
     - `Gmail API` → Select all Gmail scopes you need:
       - `.../auth/gmail.readonly` (read emails)
       - `.../auth/gmail.send` (send emails)
       - `.../auth/gmail.modify` (modify emails)
     - `Google Calendar API` → Select:
       - `.../auth/calendar` (manage calendar)
       - `.../auth/calendar.events` (manage events)
   - Click "UPDATE"

6. **Test Users** (for External apps):
   - Click "ADD USERS"
   - Add your email address(es)
   - These users can use the app while it's in testing mode

7. Click "SAVE AND CONTINUE" through remaining screens

### 5. Create OAuth Credentials

1. Click hamburger menu (☰) → "APIs & Services" → "Credentials"

2. Click "CREATE CREDENTIALS" → "OAuth client ID"

3. If prompted to configure consent screen, you may need to go back to step 4

4. **Application type**: Select "Web application"

5. **Name**: `Claude Code MCP Client`

6. **Authorized JavaScript origins** (Optional):
   - Add: `http://localhost:3000`

7. **Authorized redirect URIs** (CRITICAL):
   - Click "ADD URI"
   - Enter exactly: `http://localhost:3000/oauth/callback`
   - ⚠️ **This must match exactly** (no trailing slash)

8. Click "CREATE"

### 6. Save Your Credentials

A dialog appears with your credentials:

```
Client ID: 1234567890-abc123def456.apps.googleusercontent.com
Client Secret: GOCSPX-AbC123DeF456GhI789
```

**IMPORTANT**:
- Copy both values immediately
- Click "DOWNLOAD JSON" to save a backup
- Store securely - treat like a password

### 7. Add Credentials to Your Project

Navigate to your project and edit `.env`:

```bash
cd /path/to/your/project
nano .env  # or use your preferred editor
```

Add your credentials:

```bash
# Gmail MCP Server Configuration
GMAIL_CLIENT_ID=1234567890-abc123def456.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-AbC123DeF456GhI789

# Google Calendar MCP Server Configuration
GOOGLE_CALENDAR_CLIENT_ID=1234567890-abc123def456.apps.googleusercontent.com
GOOGLE_CALENDAR_CLIENT_SECRET=GOCSPX-AbC123DeF456GhI789
```

**Note**: You can use the same credentials for both services.

### 8. First-Time Authentication

When you first use the MCP servers:

1. Claude Code will open a browser window
2. Select your Google account
3. You'll see a warning: "Google hasn't verified this app"
   - This is normal for apps in testing mode
   - Click "Advanced" → "Go to Claude Code MCP (unsafe)"
4. Review permissions and click "Allow"
5. Browser will redirect to `localhost:3000/oauth/callback`
6. Authentication complete!

## Troubleshooting OAuth

### "redirect_uri_mismatch" Error

**Problem**: The redirect URI doesn't match

**Solution**:
1. Go to Google Cloud Console → Credentials
2. Click on your OAuth client
3. Verify "Authorized redirect URIs" shows exactly:
   ```
   http://localhost:3000/oauth/callback
   ```
4. No typos, no trailing slash, no `https`
5. Save changes and wait 5 minutes for propagation

### "Access Blocked: This app's request is invalid"

**Problem**: Missing or incorrect OAuth consent configuration

**Solution**:
1. Check OAuth consent screen is fully configured
2. Add your email as a test user
3. Ensure Gmail API and Calendar API are enabled
4. Wait 5-10 minutes after making changes

### "Invalid Client" Error

**Problem**: Client ID or Secret is wrong

**Solution**:
1. Double-check `.env` file has correct values
2. No extra spaces or quotes
3. Verify credentials in Google Cloud Console
4. Regenerate credentials if needed

### Can't See Google APIs in Library

**Problem**: Project not selected or APIs & Services not visible

**Solution**:
1. Ensure you selected your project (top dropdown)
2. Refresh the page
3. Try a different browser if issues persist

## Security Best Practices

1. **Never commit** credentials to git
   - The setup script adds `.env` to `.gitignore`

2. **Rotate credentials** periodically:
   - Delete old credentials
   - Create new ones
   - Update `.env`

3. **Limit scopes** to minimum needed:
   - Only request permissions you'll use

4. **Monitor usage**:
   - Check Google Cloud Console for unusual activity

5. **Use test users**:
   - Keep app in testing mode unless publishing

## Publishing Your App (Optional)

If you want to remove the "unverified app" warning:

1. Go to OAuth consent screen
2. Click "PUBLISH APP"
3. Follow Google's verification process
4. **Note**: Required for 100+ users, optional otherwise

For personal use, staying in testing mode is fine.

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Gmail API Scopes](https://developers.google.com/gmail/api/auth/scopes)
- [Calendar API Scopes](https://developers.google.com/calendar/api/auth)
- [OAuth Playground](https://developers.google.com/oauthplayground/) (test credentials)

## Quick Reference

**OAuth Redirect URI**: `http://localhost:3000/oauth/callback`

**Required APIs**:
- Gmail API
- Google Calendar API

**Required Scopes**:
- `https://www.googleapis.com/auth/gmail.*`
- `https://www.googleapis.com/auth/calendar`

---

**Need help?** Check the main README.md troubleshooting section or file an issue.
