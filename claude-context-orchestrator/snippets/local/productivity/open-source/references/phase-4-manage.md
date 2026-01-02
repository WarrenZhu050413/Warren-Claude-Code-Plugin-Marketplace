# Phase 4: Portfolio Management

## The OSS Inventory Problem

You likely have 50+ OSS tools. Questions that matter:
- Which need updates?
- Which configs are in dotfiles?
- Which have vulnerabilities?
- Which do you actually use?

## Management Tools

| Tool | Purpose |
|------|---------|
| **brew bundle** | Declarative macOS packages |
| **chezmoi/stow** | Dotfile management |
| **asdf/mise** | Runtime version management |
| **topgrade** | Update everything at once |

## Dotfiles Strategy

```
~/dotfiles/
├── Brewfile              # All packages
├── .zshrc                # Shell config
├── .config/
│   ├── tool1/
│   ├── tool2/
│   └── ...
└── install.sh            # Bootstrap
```

### Minimum Viable Dotfiles

1. Package list (Brewfile)
2. Shell config (.zshrc)
3. Editor config
4. Git config

### Brewfile Pattern

```ruby
# ~/dotfiles/Brewfile
tap "homebrew/cask-fonts"

# CLI tools
brew "bat"
brew "eza"
brew "fd"
brew "fzf"
brew "ripgrep"
brew "zoxide"

# Apps
cask "ghostty"
cask "raycast"

# Fonts
cask "font-jetbrains-mono-nerd-font"
```

```bash
# Install everything
brew bundle --file=~/dotfiles/Brewfile

# Generate from current
brew bundle dump --file=~/dotfiles/Brewfile
```

## Update Strategy

```bash
# Weekly: Quick updates
brew update && brew upgrade
topgrade  # If using

# Monthly: Audit
brew cleanup
brew doctor
# Review: tools not used in 3 months? Remove.

# On breaking changes
brew info <tool>  # Check version
# Visit releases page for changelog
```

## Handling Breaking Updates

```bash
# 1. Check what changed
brew info <tool>

# 2. Rollback if needed
brew uninstall <tool>
brew install <tool>@<version>

# 3. Pin to prevent future breaks
brew pin <tool>

# 4. Or migrate config based on changelog
```

## Version Pinning

```bash
# Brew
brew pin <package>      # Prevent upgrades
brew unpin <package>    # Allow upgrades

# asdf/mise
mise use tool@1.2.3     # Pin version
mise local tool@1.2.3   # Project-specific
```

## Portfolio Audit Checklist

Monthly review:

```
□ Run brew update && brew upgrade
□ Check for security advisories
□ Review tools installed but unused
□ Update dotfiles repo
□ Test dotfiles on fresh install (VM)
□ Clean caches: brew cleanup, ~/.cache
```

## Tracking What You Have

```bash
# All brew packages
brew list

# Explicitly installed (not deps)
brew leaves

# Casks (GUI apps)
brew list --cask

# With versions
brew list --versions

# GitHub CLI extensions
gh extension list
```

## Dotfile Managers

### chezmoi (Recommended)

```bash
chezmoi init
chezmoi add ~/.zshrc
chezmoi cd  # Enter dotfiles repo
chezmoi apply  # Apply to new machine
```

### GNU Stow

```bash
cd ~/dotfiles
stow zsh      # Symlinks zsh/.zshrc to ~/.zshrc
stow -D zsh   # Remove symlinks
```

## Disaster Recovery

```bash
# Bootstrap script pattern
#!/bin/bash
set -e

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install packages
brew bundle --file=~/dotfiles/Brewfile

# Apply dotfiles
chezmoi init --apply $GITHUB_USER

# Shell integrations (run manually after)
echo "Run: source ~/.zshrc"
```

## When to Remove Tools

Remove if:
- Not used in 3+ months
- Superseded by better alternative
- Causing conflicts
- Security concerns

```bash
brew uninstall <tool>
# Also remove from Brewfile
# Also remove config from dotfiles
```
