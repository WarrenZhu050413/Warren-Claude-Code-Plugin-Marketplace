# Installing Snippets CLI Globally

This guide shows you how to install the snippets CLI globally so you can run `snippets` from anywhere on your system.

## Quick Install (Recommended)

### Option 1: Shell Script Install (Simplest)

```bash
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts

# Install to /usr/local/bin (requires sudo)
./install.sh

# OR install to a custom directory (e.g., ~/bin)
./install.sh ~/bin
```

That's it! Now you can run:
```bash
snippets list
snippets create email --pattern "email" --content "..."
snippets validate
```

### Option 2: Python Package Install (Advanced)

```bash
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts

# Install in development mode (editable)
pip3 install -e .

# This creates the 'snippets' command globally
```

---

## Detailed Instructions

### Shell Script Method

**Pros:**
- Simple, no dependencies
- Easy to uninstall
- Works on any system

**Steps:**

1. **Navigate to the scripts directory:**
   ```bash
   cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts
   ```

2. **Run the install script:**
   ```bash
   ./install.sh
   ```

   This will:
   - Create a wrapper script at `/usr/local/bin/snippets`
   - Make it executable
   - Point it to your `snippets_cli.py`

3. **Verify installation:**
   ```bash
   which snippets
   # Should output: /usr/local/bin/snippets

   snippets --help
   # Should show the help message
   ```

**Custom Install Location:**

If you don't have sudo access or prefer a different location:

```bash
# Install to your home bin directory
./install.sh ~/bin

# Make sure ~/bin is in your PATH
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or source ~/.zshrc
```

### Python Package Method

**Pros:**
- Proper Python package
- Managed by pip
- Can specify dependencies

**Steps:**

1. **Navigate to the scripts directory:**
   ```bash
   cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts
   ```

2. **Install in editable mode:**
   ```bash
   pip3 install -e .
   ```

   The `-e` flag means "editable" - any changes to the source code will be immediately reflected without reinstalling.

3. **Verify installation:**
   ```bash
   which snippets
   # Should show path to pip's bin directory

   snippets --help
   ```

---

## Uninstalling

### Uninstall Shell Script Installation

```bash
cd /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts

./uninstall.sh

# OR if you installed to a custom directory
./uninstall.sh ~/bin
```

### Uninstall Python Package Installation

```bash
pip3 uninstall claude-snippets-cli
```

---

## Usage After Installation

Once installed, you can use `snippets` from anywhere:

```bash
# Create a snippet
snippets create email \
  --pattern "(email|mail)" \
  --description "Email helper" \
  --content "Email writing instructions..."

# List snippets
snippets list

# List with stats
snippets list --show-stats

# Update a snippet
snippets update email --pattern "email"

# Delete a snippet
snippets delete email --force

# Validate configuration
snippets validate

# Test a pattern
snippets test email "send an email"
```

### Specifying Config Location

By default, `snippets` uses the config in the scripts directory. To use a different config:

```bash
snippets --config /path/to/config.json list
```

Or set an environment variable:

```bash
# Add to ~/.bashrc or ~/.zshrc
export SNIPPETS_CONFIG="/path/to/config.json"

# Then use normally
snippets list
```

---

## Troubleshooting

### Command Not Found

If you get `command not found: snippets`:

1. **Check if it's installed:**
   ```bash
   ls -l /usr/local/bin/snippets
   # OR
   ls -l ~/bin/snippets
   ```

2. **Check if directory is in PATH:**
   ```bash
   echo $PATH | grep -o "/usr/local/bin"
   ```

3. **Add to PATH if needed:**
   ```bash
   echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Permission Denied

If you get permission denied when running install:

```bash
# Give execute permission
chmod +x install.sh

# Run with sudo if installing to /usr/local/bin
sudo ./install.sh
```

### Python Version Issues

If you get Python version errors:

```bash
# Check Python version
python3 --version

# Should be 3.7 or higher
# If not, install a newer Python version
```

---

## Advanced: Creating an Alias

Alternatively, you can create a shell alias without installing:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias snippets='python3 /Users/wz/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-code-snippets-plugin/scripts/snippets_cli.py'

# Reload shell
source ~/.bashrc  # or source ~/.zshrc

# Now use it
snippets list
```

**Pros:**
- No installation needed
- Easy to modify

**Cons:**
- Only works for your user
- Requires full path in alias

---

## Next Steps

After installation:

1. **Test the installation:**
   ```bash
   snippets validate
   ```

2. **Create your first snippet:**
   ```bash
   snippets create test --pattern "test" --description "Test snippet" --content "Hello world"
   ```

3. **List it:**
   ```bash
   snippets list test
   ```

4. **Clean up:**
   ```bash
   snippets delete test --force
   ```

Enjoy using snippets! 🎉
