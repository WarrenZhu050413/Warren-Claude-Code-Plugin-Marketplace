---
description: Warren's Neovim configuration reference (~/.config/nvim) with LSP, plugins, and directory structure
SNIPPET_NAME: using-nvim
ANNOUNCE_USAGE: false
---

# Neovim Configuration

Warren's Neovim setup is at: ~/.config/nvim. Always refer to this setup for Neovim questions.

## Critical Rule: Check Local Configuration First

**BEFORE answering ANY Neovim question, you MUST:**
1. Read relevant config files from ~/.config/nvim/
2. Understand Warren's actual setup, plugins, and settings
3. Base answers on what's configured, not generic assumptions

## Directory Structure

```
~/.config/nvim/              # Main configuration root
├── init.lua                 # Entry point (or init.vim)
├── lua/
│   ├── plugins/             # Plugin configurations
│   │   ├── lsp.lua          # LSP config (pyright for Python)
│   │   ├── treesitter.lua   # Syntax highlighting
│   │   └── telescope.lua    # Fuzzy finder
│   ├── config/              # Custom settings
│   └── utils/               # Helper functions
└── after/                   # After-load scripts
```

## Standard Neovim Directories

- **Config**: ~/.config/nvim/ (main configuration)
- **Data**: ~/.local/share/nvim/ (plugins, state, shada)
- **Cache**: ~/.cache/nvim/ (temporary files, swap)
- **State**: ~/.local/state/nvim/ (persistent state)

## LSP & Plugin Management

- **Python LSP**: pyright (in ~/.config/nvim/lua/plugins/lsp.lua)
- **Auto venv**: checks venv/, .venv/, env/, virtualenv/, $VIRTUAL_ENV
- **Custom paths**: Create pyrightconfig.json with `extraPaths: ["."]`
- **Plugin specs**: ~/.config/nvim/lua/plugins/*.lua (lazy.nvim)
- **Plugin data**: ~/.local/share/nvim/lazy/ (installed plugins)
