# Phase 2: Learning Efficiently

**Man pages are reference docs, not tutorials.** Different approach needed.

## Learning Stack (Best to Worst)

| Source | When to Use | Command |
|--------|-------------|---------|
| **tldr** | First stop, practical examples | `tldr <tool>` |
| **cheat.sh** | Quick reference | `curl cheat.sh/<tool>` |
| **Getting Started** | If well-written | Official docs |
| **GitHub issues** | Real usage patterns | `gh issue list -R` |
| **YouTube/blogs** | Complex tools | Search |
| **Man pages** | Specific flag lookup | `man <tool>` |

## Learning Protocol

```bash
# 1. Get practical examples first
tldr <tool>
curl cheat.sh/<tool>

# 2. Try the happy path
<tool> --help | head -20

# 3. Find real configs from others
gh search code "filename:.<tool>rc" --limit 10

# 4. Experiment in isolation
cd $(mktemp -d) && <experiment>
```

## CLI Discovery Problem

CLIs are fundamentally different from GUIs—you can't "scan" the interface.

**Strategies:**
- `<tool> --help | less` → Read section headers first
- `<tool> help <subcommand>` → Drill into specific areas
- Shell completions → Reveal command structure
- Search "cheatsheet + tool name"

## Finding Real-World Configs

```bash
# Search GitHub for config files
gh search code "filename:.<tool>rc" --limit 20
gh search code "filename:config/<tool>" --limit 20

# Popular dotfile repos
gh search repos "dotfiles" --sort stars --limit 10

# Specific user's config
gh api repos/user/dotfiles/contents/.<tool>rc
```

## Understanding Command Structure

```bash
# Most CLI tools follow patterns:
<tool> <verb> <noun> [flags]
<tool> <noun> <verb> [flags]
<tool> [global-flags] <command> [command-flags]

# Discover structure
<tool> --help
<tool> help
<tool> commands  # If available
<tool> <tab><tab>  # With completions
```

## Building Mental Models

1. **What's the core abstraction?** (files, containers, streams, etc.)
2. **What are the main operations?** (CRUD, transform, connect)
3. **What's the typical workflow?** (init → config → run)
4. **What integrates with what?** (pipes, files, APIs)

## Common Patterns Across Tools

| Pattern | Examples |
|---------|----------|
| `init` | Create config/project |
| `config` | View/edit settings |
| `list/ls` | Show items |
| `add/new` | Create item |
| `rm/delete` | Remove item |
| `run/exec` | Execute |
| `--dry-run` | Preview without doing |
| `-v/--verbose` | More output |
| `-q/--quiet` | Less output |

## When Stuck

```bash
# Search issues for your error
gh search issues "<error message>" --repo owner/tool

# Check discussions
gh api repos/owner/tool/discussions --jq '.[0:5] | .[].title'

# Stack Overflow
# Search: "[tool-name] <your problem>"
```
