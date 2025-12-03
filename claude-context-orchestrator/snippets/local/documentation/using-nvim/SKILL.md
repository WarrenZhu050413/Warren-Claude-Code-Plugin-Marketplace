---
name: "Using Nvim"
description: "Reference Warren's Neovim configuration (~/.config/nvim) with LSP, plugins, and directory structure."
---

# Using Nvim

Warren's Neovim: ~/.config/nvim

## Critical Rule

**BEFORE answering Neovim questions:**
1. Read config files from ~/.config/nvim/
2. Understand Warren's setup, plugins, settings
3. Base answers on actual config, not assumptions

## Directory Structure

```
~/.config/nvim/
├── init.lua                 # Entry point
├── lua/
│   ├── plugins/             # Plugin configs
│   │   ├── lsp.lua          # LSP (pyright)
│   │   ├── treesitter.lua   # Syntax
│   │   └── telescope.lua    # Fuzzy finder
│   ├── config/              # Custom settings
│   └── utils/               # Helpers
└── after/                   # After-load
```

## Standard Directories

- **Config**: ~/.config/nvim/
- **Data**: ~/.local/share/nvim/ (plugins, state, shada)
- **Cache**: ~/.cache/nvim/ (temp, swap)
- **State**: ~/.local/state/nvim/ (persistent)

## LSP & Plugins

- **Python LSP**: pyright (in lua/plugins/lsp.lua)
- **Auto venv**: checks venv/, .venv/, env/, virtualenv/, $VIRTUAL_ENV
- **Custom paths**: pyrightconfig.json with `extraPaths: ["."]`
- **Plugin specs**: lua/plugins/*.lua (lazy.nvim)
- **Plugin data**: ~/.local/share/nvim/lazy/
