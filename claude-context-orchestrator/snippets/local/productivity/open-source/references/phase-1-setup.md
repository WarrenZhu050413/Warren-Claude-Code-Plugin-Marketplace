# Phase 1: Setup & Installation

## Pre-Setup Decisions

Most OSS requires decisions before/during setup:

1. **Installation method**: Package manager vs source vs container
2. **Configuration scope**: System-wide vs user vs project
3. **Secrets/credentials**: What external accounts/APIs needed?
4. **Integration points**: Shell, editor, other tools?

## Setup Pattern

```bash
# 1. Prefer package manager
brew install <tool>  # or apt, pacman, etc.

# 2. Check what config files were created
ls -la ~/.<tool>* ~/.config/<tool>

# 3. Locate example configs
<tool> --help | grep -i config
find /usr/share -name "*<tool>*" 2>/dev/null

# 4. Start with minimal config, add incrementally
```

## Common Gotchas

| Issue | Solution |
|-------|----------|
| Shell integration | Add `eval "$(tool init zsh)"` to rc file |
| PATH issues | Ensure binary location in PATH |
| Version conflicts | Check: system vs brew vs asdf version |
| Config precedence | Tool may read from multiple locations |

## Installation Methods Comparison

| Method | Pros | Cons |
|--------|------|------|
| **brew/apt** | Easy updates, deps handled | May be outdated |
| **Source** | Latest version, customize | Manual updates |
| **Docker** | Isolated, reproducible | Overhead, integration |
| **asdf/mise** | Version management | Extra tooling |

## Secrets & Credentials

```bash
# Check what's needed
<tool> --help | grep -iE 'api|key|token|auth'

# Common locations
~/.config/<tool>/credentials
~/.netrc
~/.aws/credentials
$TOOL_API_KEY environment variable
```

**Never commit secrets.** Use:
- `.env` files (gitignored)
- `op` (1Password CLI)
- `pass` (password store)
- Environment variables

## Shell Integration Patterns

```bash
# Common init patterns
eval "$(starship init zsh)"      # Prompt
eval "$(zoxide init zsh)"        # Smart cd
eval "$(fzf --zsh)"              # Fuzzy finder
eval "$(atuin init zsh)"         # Shell history
source <(tool completion zsh)    # Completions
```

## Post-Install Verification

```bash
# Verify installation
which <tool>
<tool> --version

# Verify config loaded
<tool> config  # If available

# Test basic functionality
<tool> --help | head -20
```

## Troubleshooting Setup

```bash
# Wrong binary?
which -a <tool>

# Config not loading?
<tool> --debug 2>&1 | grep -i config

# Shell integration broken?
zsh -x -c 'eval "$(tool init zsh)"' 2>&1 | head -50

# Permission issues?
ls -la $(which <tool>)
ls -la ~/.config/<tool>
```
