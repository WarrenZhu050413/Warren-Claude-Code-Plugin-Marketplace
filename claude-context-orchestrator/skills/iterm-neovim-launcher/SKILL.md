# iTerm2 Neovim Launcher Skill

**Purpose**: Create macOS scripts that open files in Neovim within the active iTerm2 window, handling automation reliably despite AppleScript limitations.

**Use this skill when**:
- Creating scripts to launch terminal applications from macOS GUI
- Debugging AppleScript iTerm2 automation issues
- Setting up file associations to open in terminal editors
- Working with iTerm2, tmux, or terminal-based workflows on macOS

---

## The Working Script

**Location**: `~/.local/bin/open-in-neovim`

```bash
#!/bin/bash
# Opens files in Neovim within the latest active iTerm2 window

FILE="$1"

# Guard: require file argument
if [[ -z "$FILE" ]]; then
    echo "Usage: open-in-neovim <file>"
    exit 1
fi

# Get absolute path
if [[ ! "$FILE" = /* ]]; then
    FILE="$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")"
fi

# Send command to iTerm2 using System Events (more reliable than write text)
osascript - "$FILE" <<'APPLESCRIPT'
on run argv
    set filePath to item 1 of argv
    set cmd to "nvim \"" & filePath & "\""

    tell application "iTerm"
        activate
        delay 0.2

        if (count of windows) = 0 then
            create window with default profile
            delay 0.3
        end if
    end tell

    tell application "System Events"
        keystroke cmd
        keystroke return
    end tell
end run
APPLESCRIPT

exit $?
```

**Setup**:
```bash
chmod +x ~/.local/bin/open-in-neovim
# Ensure ~/.local/bin is in PATH
```

---

## Critical Lessons Learned

### 1. **AppleScript String Escaping is Treacherous**

❌ **What Doesn't Work**: Passing complex command strings with nested quotes
```applescript
# This causes AppleEvent errors
set cmd to "tmux send-keys -t '{last}' 'nvim \"$FILE\"' Enter"
tell targetSession
    write text cmd
end tell
```

✅ **What Works**: Construct commands in AppleScript, not bash
```applescript
# Build the command in AppleScript
set filePath to item 1 of argv
set cmd to "nvim \"" & filePath & "\""
```

**Key Insight**: When passing data from bash to AppleScript, pass simple values (like file paths) and let AppleScript do the string construction.

---

### 2. **iTerm2's `write text` is Unreliable**

❌ **Fails Intermittently**:
```applescript
tell targetSession
    write text cmd  # AppleEvent handler failed (-10000)
end tell
```

**Symptoms**:
- Works sometimes, fails randomly
- Error: "iTerm got an error: AppleEvent handler failed. (-10000)"
- No clear pattern to failures
- Happens regardless of string escaping approach

✅ **Reliable Alternative**: Use `System Events` keystroke
```applescript
tell application "System Events"
    keystroke cmd      # Simulates typing
    keystroke return   # Simulates Enter key
end tell
```

**Why This Works**:
- Simulates actual keyboard input rather than using iTerm's API
- Works regardless of iTerm's internal state
- Independent of session, tmux, or shell state
- More robust across iTerm2 versions

---

### 3. **Passing Arguments to AppleScript via Heredoc**

✅ **Correct Pattern**:
```bash
osascript - "$ARG1" "$ARG2" <<'APPLESCRIPT'
on run argv
    set arg1 to item 1 of argv
    set arg2 to item 2 of argv
    # ... use args here
end run
APPLESCRIPT
```

**Critical Details**:
- Use `osascript -` to read from stdin
- Pass arguments BEFORE the heredoc
- Use **quoted heredoc** (`<<'APPLESCRIPT'`) to prevent bash expansion
- Access via `argv` in AppleScript's `on run` handler
- Items are 1-indexed: `item 1 of argv`, not `item 0`

❌ **Common Mistakes**:
```bash
# Don't put variables inside the heredoc expecting bash substitution
osascript <<APPLESCRIPT  # Unquoted = bash expands $vars
    set cmd to "$BASH_VAR"  # Won't work as expected
APPLESCRIPT

# Don't try to construct complex commands in bash then pass them
CMD="tmux send-keys 'nvim \"$FILE\"'"
osascript - "$CMD" <<'APPLESCRIPT'  # Too complex, escaping nightmare
```

---

### 4. **Timing and Delays Matter**

✅ **Add small delays for reliability**:
```applescript
tell application "iTerm"
    activate
    delay 0.2  # Wait for iTerm to come to foreground

    if (count of windows) = 0 then
        create window with default profile
        delay 0.3  # Wait for window creation
    end if
end tell

tell application "System Events"
    keystroke cmd  # Now iTerm is guaranteed to be ready
end tell
```

**Why**:
- AppleScript commands are asynchronous
- `activate` doesn't guarantee the app is ready
- `create window` takes time to complete
- Without delays, keystrokes may be sent before window is active

---

### 5. **File Path Handling Best Practices**

```bash
# Always convert to absolute path
if [[ ! "$FILE" = /* ]]; then
    FILE="$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")"
fi
```

**Why**:
- Relative paths depend on current working directory
- When script is called from different contexts (Finder, terminal, file associations), `pwd` differs
- Absolute paths work regardless of where Neovim opens

**Handles**:
- Regular filenames: `file.txt`
- Paths with spaces: `my file.txt`
- Relative paths: `../other/file.txt`
- Already absolute: `/full/path/file.txt`

---

## Common AppleEvent Errors and Solutions

| Error Code | Message | Cause | Solution |
|------------|---------|-------|----------|
| -10000 | AppleEvent handler failed | iTerm's `write text` in bad state | Use System Events keystroke |
| -2741 | Syntax error: Expected """ but found unknown token | Unescaped quotes in strings | Use AppleScript string concatenation `&` |
| -1708 | Can't get item 1 of argv | No arguments passed to osascript | Pass args before heredoc: `osascript - "$ARG"` |

---

## Testing Methodology

**Progressive Testing Approach**:

```bash
# 1. Test basic iTerm communication
osascript <<'APPLESCRIPT'
tell application "iTerm"
    activate
    display dialog "iTerm is responding"
end tell
APPLESCRIPT

# 2. Test window/session access
osascript <<'APPLESCRIPT'
tell application "iTerm"
    activate
    set targetWindow to current window
    set targetSession to current session of targetWindow
    # If this works, iTerm API is accessible
end tell
APPLESCRIPT

# 3. Test write text (will likely fail)
osascript <<'APPLESCRIPT'
tell application "iTerm"
    tell current session of current window
        write text "echo test"
    end tell
end tell
APPLESCRIPT

# 4. Test System Events alternative (should work)
osascript <<'APPLESCRIPT'
tell application "iTerm"
    activate
    delay 0.2
end tell
tell application "System Events"
    keystroke "echo test"
    keystroke return
end tell
APPLESCRIPT

# 5. Test with actual file path via argv
osascript - "/tmp/test.md" <<'APPLESCRIPT'
on run argv
    set filePath to item 1 of argv
    set cmd to "nvim \"" & filePath & "\""

    tell application "iTerm"
        activate
        delay 0.2
    end tell

    tell application "System Events"
        keystroke cmd
        keystroke return
    end tell
end run
APPLESCRIPT
```

**Key Testing Insights**:
- Test in isolation before integrating
- Start simple, add complexity gradually
- Verify each layer works before moving up
- Test with edge cases: spaces, special chars, long paths

---

## Tmux Integration Considerations

**Original Goal**: Detect tmux and use `tmux send-keys`

**Reality**: Not necessary with `System Events` approach

```bash
# This was attempted but abandoned
if command -v tmux &>/dev/null && tmux list-sessions &>/dev/null 2>&1; then
    CMD="tmux send-keys -t '{last}' 'nvim \"$FILE\"' Enter"
else
    CMD="nvim \"$FILE\""
fi
```

**Why It Was Removed**:
- System Events keystroke simulates typing, which works in ANY shell state
- If you're in tmux, typing `nvim file` works naturally
- No need to detect or special-case tmux
- Simpler = more reliable

**When You WOULD Need Tmux Detection**:
- Opening files in a specific tmux pane (not current)
- Remote tmux sessions
- Scripted tmux workflows requiring precise pane targeting

---

## Setting Up File Associations (Optional)

Once the script works, you can set it as the default opener for file types.

**Using `duti`** (recommended):
```bash
# Install duti
brew install duti

# Create wrapper app (needed for macOS file associations)
# macOS file associations require .app bundles, not shell scripts

# Alternative: Use Automator to create app wrapper
# 1. Open Automator
# 2. New > Application
# 3. Add "Run Shell Script" action
# 4. Script: ~/.local/bin/open-in-neovim "$@"
# 5. Save as "NeovimLauncher.app"

# Set as default handler
duti -s com.your.neovim-launcher .md all
duti -s com.your.neovim-launcher .txt all
```

**Manual Testing**:
```bash
# Test from command line
open-in-neovim test.md

# Test with spaces
open-in-neovim "file with spaces.txt"

# Test with relative path
cd ~/Documents
open-in-neovim ../Desktop/file.md
```

---

## Debugging Checklist

When AppleScript iTerm automation fails:

- [ ] Is iTerm2 actually running?
- [ ] Does iTerm have at least one window open?
- [ ] Are you using quoted heredoc (`<<'APPLESCRIPT'`)?
- [ ] Are arguments passed BEFORE the heredoc?
- [ ] Did you try System Events instead of `write text`?
- [ ] Are there appropriate delays after `activate` and `create window`?
- [ ] Is the file path properly escaped with `\"`?
- [ ] Can you test the AppleScript in isolation (without bash)?
- [ ] Does the simple case work before adding complexity?

---

## Real-World Debugging Session Summary

**Problem Evolution**:
1. Initial script: Complex command construction with nested quotes → Syntax errors
2. Fixed escaping: Passed full command string → AppleEvent -10000 errors
3. Tried argv approach with `write text` → Still intermittent -10000 errors
4. Switched to System Events keystroke → Reliable, works consistently

**Time Investment**: ~6 iterations over debugging session

**Root Causes Identified**:
- iTerm2's AppleScript API (`write text`) is fundamentally unreliable
- String escaping with nested quotes is error-prone
- AppleScript timing issues need explicit delays

**Final Solution**:
- Simple file path via argv
- AppleScript string concatenation
- System Events keystroke simulation
- Small delays for reliability

---

## Key Takeaways

1. **System Events > Native iTerm API** for sending commands
2. **Pass simple values, construct complex strings in AppleScript**
3. **Always use quoted heredocs** for AppleScript embedding
4. **Add delays after UI operations** (activate, create window)
5. **Convert to absolute paths** to avoid working directory issues
6. **Test progressively** from simple to complex
7. **Don't trust "works once"** - test multiple times for intermittent issues

---

## Alternative Approaches Considered

### 1. Direct tmux send-keys (from outside iTerm)
```bash
tmux send-keys -t iterm-session "nvim '$FILE'" Enter
```
**Pros**: No AppleScript
**Cons**: Requires knowing exact session name, doesn't work if not in tmux

### 2. iTerm2 Python API
```python
import iterm2
# Use Python API to send commands
```
**Pros**: More programmatic control
**Cons**: Requires separate Python script, more dependencies

### 3. osascript with direct command
```bash
osascript -e 'tell application "iTerm" to tell current session...'
```
**Pros**: One-liner
**Cons**: Same `write text` reliability issues, harder to read

**Why System Events Won**: Simplest approach that actually works reliably.

---

## Usage Examples

```bash
# Basic usage
open-in-neovim README.md

# From different directory
cd /tmp
open-in-neovim ~/Documents/notes.txt

# With spaces
open-in-neovim "My Essay Draft.md"

# From GUI (Finder, file manager)
# - Right click file
# - Open With > open-in-neovim (if set up)

# From other applications
# - Called by external file managers
# - Git GUI tools
# - Note-taking apps with custom editors
```

---

## Permissions Note

**macOS Security**: System Events requires accessibility permissions

If you get permission errors:
1. System Preferences → Security & Privacy → Privacy tab
2. Select "Accessibility" from left sidebar
3. Add Terminal.app (if running from terminal)
4. Add the calling application (Finder, etc.)

**This is a one-time setup per calling application.**

---

## Summary

This skill documents hard-won knowledge about macOS AppleScript automation with iTerm2:

- **The Problem**: Opening files in terminal Neovim from macOS GUI
- **The Challenge**: AppleScript's unreliable iTerm API and string escaping nightmares
- **The Solution**: System Events keystroke simulation with proper timing
- **The Lesson**: Sometimes the "indirect" approach (simulating keystrokes) is more reliable than the "proper" API

Use this skill when building macOS automation that needs to interact with terminal applications. The patterns here apply beyond just Neovim - any terminal-based tool can use this approach.
