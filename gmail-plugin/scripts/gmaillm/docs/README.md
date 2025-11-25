# Documentation

Comprehensive guides for gmaillm features.

## User Guides

- **[Email Styles](email-styles.md)** - Creating and managing email writing styles
- **[Email Groups](email-groups.md)** - Managing email distribution groups

## Quick Links

### Email Styles

Learn how to create custom email styles with structured templates:

```bash
gmail styles list           # List all styles
gmail styles create my-style # Create new style
gmail styles show formal    # View style details
```

See [email-styles.md](email-styles.md) for complete guide.

### Email Groups

Learn how to create and manage email distribution groups:

```bash
gmail groups list                  # List all groups
gmail groups create team --emails user@example.com
gmail send --to #team --subject "Update"
```

See [email-groups.md](email-groups.md) for complete guide.

## Other Documentation

- **[README.md](../README.md)** - Installation and quick start
- **[TESTING.md](../TESTING.md)** - Test running and writing guide
- **[API_REFERENCE.md](../API_REFERENCE.md)** - Complete API documentation
- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and changes
- **[CLAUDE.md](../CLAUDE.md)** - Claude Code development guidance
