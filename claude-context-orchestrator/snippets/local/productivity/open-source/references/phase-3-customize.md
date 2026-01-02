# Phase 3: Customization & Extension

## Customization Layers

```
Layer 4: System Integration    │ Alfred, Raycast, shell aliases
Layer 3: Workflows & Automation│ Scripts, hooks, pipelines
Layer 2: Behavior & Features   │ Flags, options, plugins
Layer 1: Appearance            │ Themes, colors, fonts
```

Work bottom-up: appearance → behavior → workflows → integration.

---

## Layer 1: Appearance

### Aesthetic Consistency Goal

All tools should feel like one unified environment.

```bash
# Document your standards (~/.config/style-guide.md)
Colors: Catppuccin Mocha / Dracula / etc.
Font: JetBrains Mono / Fira Code
Key bindings: Vim-style
Prompt: Minimal, git-aware
```

### Theme Systems

**Base16/Catppuccin** - Many tools support these:
```bash
# bat
bat --list-themes | grep -i catppuccin

# delta (in ~/.gitconfig)
[delta]
    syntax-theme = Catppuccin-mocha
```

### Nerd Fonts (Icons)

```bash
brew tap homebrew/cask-fonts
brew install --cask font-jetbrains-mono-nerd-font
# Configure in terminal: Preferences → Font
```

---

## Layer 2: Behavior & Features

### Flag Standardization

Create aliases that normalize common operations:

```bash
# ~/.zshrc
alias ls='eza -la --icons --group-directories-first'
alias cat='bat --style=plain --paging=never'
alias grep='rg --smart-case'
alias find='fd'
alias diff='delta'
alias du='dust'
alias top='btop'
```

### Config File Locations (XDG)

```bash
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_CACHE_HOME="$HOME/.cache"

# For non-compliant tools, symlink:
ln -s ~/.config/tool ~/.toolrc
```

---

## Layer 3: Workflows & Automation

### Shell Functions

```bash
# Git + GitHub workflow
pr() {
  git push -u origin HEAD
  gh pr create --fill --web
}

# Project scaffolding
mkproject() {
  mkdir -p "$1"/{src,tests,docs}
  cd "$1" && git init
  echo "# $1" > README.md
}

# Interactive search + edit
fif() {
  rg --line-number "$1" |
    fzf --preview 'bat --highlight-line {2} {1}' \
        --bind 'enter:become($EDITOR {1} +{2})'
}
```

### Git Hooks

```bash
# Global hooks
git config --global core.hooksPath ~/.config/git/hooks
mkdir -p ~/.config/git/hooks

# Example: prevent direct commits to main
cat > ~/.config/git/hooks/pre-commit << 'EOF'
#!/bin/sh
branch=$(git symbolic-ref --short HEAD)
if [ "$branch" = "main" ]; then
  echo "Direct commits to main not allowed"
  exit 1
fi
EOF
chmod +x ~/.config/git/hooks/pre-commit
```

---

## Layer 4: System Integration

### Alfred/Raycast

```bash
# Alfred script filter (JSON output)
query="$1"
my-tool search "$query" | jq '{items: map({title: ., arg: .})}'
```

```bash
# Raycast script command
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title My Tool
# @raycast.mode silent
my-tool "$1"
```

### Keyboard Shortcuts (macOS)

Karabiner-Elements for system-wide shortcuts:
```json
{
  "description": "Hyper+T opens Terminal",
  "from": {"key_code": "t", "modifiers": {"mandatory": ["hyper"]}},
  "to": [{"shell_command": "open -a 'Ghostty'"}]
}
```

### launchd Services

```xml
<!-- ~/Library/LaunchAgents/com.user.tool.plist -->
<plist version="1.0">
<dict>
    <key>Label</key><string>com.user.tool</string>
    <key>ProgramArguments</key>
    <array><string>/usr/local/bin/tool</string><string>--daemon</string></array>
    <key>RunAtLoad</key><true/>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.user.tool.plist
```

---

## Debugging Customizations

```bash
# Check if tool sees your config
which tool                    # Right binary?
tool config                   # Built-in dump?

# Trace shell integration
zsh -x -c 'eval "$(tool init zsh)"'

# Common issues
# - TERM not set → export TERM=xterm-256color
# - Wrong font → Install Nerd Font
# - Slow startup → Profile: time zsh -i -c exit
```
