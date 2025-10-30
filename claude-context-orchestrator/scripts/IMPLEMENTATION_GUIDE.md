# Snippets CLI v2.0 Implementation Guide

## Status

✅ RED Phase: Tests written and failing
✅ Setup: pyproject.toml and Makefile created
✅ GREEN Phase: Implementation complete (14/14 tests passing)
✅ REFACTOR Phase: Code cleaned up, linting passed
⏳ COMMIT Phase: Ready to commit

## What's Been Done

1. **Created pyproject.toml** - Configured for `uv tool install`
2. **Created Makefile** - Inspired by gmail CLI with dev/install/test targets
3. **Written comprehensive tests** - `test_snippets_cli_v2.py` with 14 tests (all passing)
4. **Implemented paths command** - Shows available snippet categories with filtering
5. **Refactored create command** - Takes source file + destination path with validation
6. **Enhanced search** - Multi-level search across name/pattern/description with priority ranking
7. **Auto-detect TTY** - Interactive mode in terminal, non-interactive when piped
8. **Cleaned up code** - Fixed all linting issues, passed ruff checks

## Implementation Steps (GREEN Phase)

### Step 1: Add `paths` Command

In `snippets_cli.py`, around line 1117 after subparsers definition:

```python
# paths
paths_parser = subparsers.add_parser("paths", help="Show available snippet locations")
paths_parser.add_argument("filter", nargs="?", help="Filter categories by keyword")
```

In `SnippetManager` class, add method:

```python
def show_paths(self, filter_term: str = None) -> Dict:
    """Show available snippet locations and categories"""
    categories = {
        "communication": "Email, reports, writing templates",
        "documentation": "Guides, references, how-tos",
        "development": "Code patterns, debugging workflows",
        "productivity": "Workflow automation, task management",
        "output-formats": "Formatting styles, templates"
    }

    if filter_term:
        categories = {
            k: v for k, v in categories.items()
            if filter_term.lower() in k.lower() or filter_term.lower() in v.lower()
        }

    return {
        "base_dir": str(self.snippets_dir),
        "categories": [
            {
                "name": name,
                "description": desc,
                "path": f"snippets/local/{name}/"
            }
            for name, desc in categories.items()
        ]
    }
```

In `main()`, add handler (around line 1240):

```python
elif args.command == "paths":
    filter_term = getattr(args, 'filter', None)
    data = manager.show_paths(filter_term)

    if args.output == "json":
        print(json.dumps(data, indent=2))
    else:
        # Format for terminal
        print("\nAvailable snippet locations:\n")
        print(f"Base directory: {data['base_dir']}\n")
        print("Categories:")
        for cat in data["categories"]:
            print(f"  {cat['name']}/")
            print(f"    {cat['description']}")
            print(f"    Path: {cat['path']}\n")
```

### Step 2: Refactor `create` Command

Replace the existing `create` command parser (around line 1119) with:

```python
# create
create_parser = subparsers.add_parser("create", help="Create new snippet from file")
create_parser.add_argument("source_file", help="Source SKILL.md file")
create_parser.add_argument("destination_path", help="Destination path (snippets/local/<category>/<name>/SKILL.md)")
create_parser.add_argument("--pattern", help="Override pattern from frontmatter")
create_parser.add_argument("--force", action="store_true", help="Overwrite if exists")
```

In `SnippetManager`, replace `create()` with:

```python
def create_from_file(self, source_file: str, destination_path: str,
                     pattern_override: str = None, force: bool = False) -> Dict:
    """
    Create snippet from source file to destination path.

    Validates:
    - Source file exists and has valid frontmatter
    - Pattern format (from frontmatter or override)
    - Destination is within snippets directory
    - Destination doesn't exist (unless force)

    Returns dict with creation details
    """
    import yaml

    # 1. Validate source file
    source_path = Path(source_file).expanduser().resolve()
    if not source_path.exists():
        raise SnippetError("FILE_ERROR", f"Source file not found: {source_file}")

    # 2. Read and validate YAML frontmatter
    content = source_path.read_text()
    if not content.startswith("---"):
        raise SnippetError(
            "MISSING_FRONTMATTER",
            "Source file must start with YAML frontmatter:\n"
            "---\n"
            "name: \"Snippet Name\"\n"
            "description: \"Description\"\n"
            "pattern: \"\\\\b(PATTERN)\\\\b[.,;:!?]?\"\n"
            "---"
        )

    # Extract frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise SnippetError("INVALID_FRONTMATTER", "Malformed YAML frontmatter")

    frontmatter = yaml.safe_load(parts[1])
    if not frontmatter:
        raise SnippetError("EMPTY_FRONTMATTER", "YAML frontmatter is empty")

    # Extract required fields
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    pattern = pattern_override or frontmatter.get("pattern", "")

    if not name:
        raise SnippetError("MISSING_NAME", "Frontmatter must include 'name' field")
    if not description:
        raise SnippetError("MISSING_DESCRIPTION", "Frontmatter must include 'description' field")
    if not pattern:
        raise SnippetError("MISSING_PATTERN", "Frontmatter must include 'pattern' field or use --pattern flag")

    # 3. Validate pattern
    self._validate_pattern(pattern)

    # 4. Validate destination path
    dest_path = Path(destination_path)

    # Check it's within snippets directory
    try:
        # Make dest_path relative to config directory for comparison
        rel_dest = dest_path if not dest_path.is_absolute() else dest_path.relative_to(self.config_path.parent)
        if not str(rel_dest).startswith("snippets/local/"):
            raise ValueError("Not in snippets/local/")
    except (ValueError, OSError):
        raise SnippetError(
            "INVALID_DESTINATION",
            f"Destination must be within snippets/local/ directory\n"
            f"Expected format: snippets/local/<category>/<name>/SKILL.md\n"
            f"Got: {destination_path}\n\n"
            f"Run 'snippets paths' to see available categories."
        )

    # 5. Extract snippet name from path
    # snippets/local/development/my-snippet/SKILL.md -> my-snippet
    path_parts = dest_path.parts
    if len(path_parts) < 4:
        raise SnippetError(
            "INVALID_DESTINATION_STRUCTURE",
            f"Destination must follow: snippets/local/<category>/<name>/SKILL.md\n"
            f"Got: {destination_path}"
        )

    snippet_name = path_parts[-2]  # Parent directory name

    # 6. Check destination doesn't exist
    full_dest_path = self.snippets_dir.parent / dest_path
    if full_dest_path.exists() and not force:
        raise SnippetError(
            "DESTINATION_EXISTS",
            f"Destination already exists: {destination_path}\n\n"
            f"Use --force to overwrite"
        )

    # 7. Create destination directory
    full_dest_path.parent.mkdir(parents=True, exist_ok=True)

    # 8. Copy file to destination
    shutil.copy2(source_path, full_dest_path)

    # 9. Register in config.local.json
    target_config = self._get_target_config()

    # Remove existing entry if force
    if force:
        target_config["mappings"] = [
            m for m in target_config["mappings"]
            if m.get("name") != snippet_name
        ]

    # Add new entry
    target_config["mappings"].append({
        "name": snippet_name,
        "pattern": pattern,
        "snippet": [str(dest_path)],
        "separator": "\n",
        "enabled": True
    })

    self._save_config()

    return {
        "name": snippet_name,
        "pattern": pattern,
        "destination": str(destination_path),
        "source": str(source_file),
        "registered": True
    }
```

Update `main()` create handler (around line 1240):

```python
elif args.command == "create":
    data = manager.create_from_file(
        args.source_file,
        args.destination_path,
        getattr(args, 'pattern', None),
        getattr(args, 'force', False)
    )

    if args.output == "json":
        print(json.dumps({"success": True, "data": data}, indent=2))
    else:
        print(f"\n✓ Snippet created successfully!")
        print(f"  Name: {data['name']}")
        print(f"  Pattern: {data['pattern']}")
        print(f"  Destination: {data['destination']}")
        print(f"\nTest it: Type trigger keyword in a new prompt")
```

### Step 3: Remove Old Commands

Delete these subparsers (around lines 1142-1173):
- `update_parser`
- `delete_parser`
- `test_parser`
- `priority_parser` (set-priority)

Delete these command handlers in `main()` (around lines 1281-1312):
- `elif args.command == "update":`
- `elif args.command == "delete":`
- `elif args.command == "test":`
- `elif args.command == "set-priority":`

### Step 4: Remove Unused Flags

Remove from global options (around lines 1101-1114):
- `--config-name`
- `--use-base-config`
- `-v / --verbose`
- `-k / --keyword` (search is now built into list)

### Step 5: Enhanced Search

In `SnippetManager.list()`, add description search:

```python
def list(self, name: str = None, show_content: bool = False,
         show_stats: bool = False, show_source: bool = True, search_term: str = None) -> Dict:
    """List snippets with optional search across name/pattern/description"""
    snippets = []

    for mapping in self.config["mappings"]:
        snippet_files = mapping["snippet"]

        # Extract snippet name
        if "name" in mapping:
            snippet_name = mapping["name"]
        else:
            snippet_name = Path(snippet_files[0]).stem

        # Filter by name if specified
        if name and snippet_name != name:
            continue

        # Enhanced search across name, pattern, description
        if search_term:
            search_lower = search_term.lower()

            # Check name match (exact or contains)
            name_match = search_lower in snippet_name.lower()

            # Check pattern match
            pattern = mapping["pattern"]
            pattern_match = False
            pattern_match_obj = re.search(r'\(([^)]+)\)', pattern)
            if pattern_match_obj:
                pattern_content = pattern_match_obj.group(1)
                pattern_match = any(
                    search_lower in alt.lower()
                    for alt in pattern_content.split('|')
                )

            # Check description match (read from file)
            description_match = False
            for snippet_file in snippet_files:
                snippet_path = self.snippets_dir.parent / snippet_file
                if snippet_path.exists():
                    try:
                        file_content = snippet_path.read_text()
                        if file_content.startswith("---"):
                            parts = file_content.split("---", 2)
                            if len(parts) >= 3:
                                import yaml
                                frontmatter = yaml.safe_load(parts[1])
                                if frontmatter:
                                    desc = frontmatter.get("description", "")
                                    if search_lower in desc.lower():
                                        description_match = True
                                        break
                    except:
                        pass

            # Skip if no matches
            if not (name_match or pattern_match or description_match):
                continue

            # Determine match type for priority
            if snippet_name.lower() == search_lower:
                match_type = "exact"
                match_priority = 1
            elif name_match:
                match_type = "name"
                match_priority = 2
            elif pattern_match:
                match_type = "pattern"
                match_priority = 3
            else:
                match_type = "description"
                match_priority = 4
        else:
            match_type = None
            match_priority = 999

        snippet_info = {
            "name": snippet_name,
            "pattern": mapping["pattern"],
            "files": snippet_files,
            "file_count": len(snippet_files),
            "separator": mapping.get("separator", "\n"),
            "enabled": mapping.get("enabled", True),
            "alternatives": self._count_alternatives(mapping["pattern"]),
            "match_priority": match_priority,
        }

        if match_type:
            snippet_info["match_type"] = match_type

        # ... rest of existing code ...

        snippets.append(snippet_info)

    # Sort by match priority (lower = better)
    snippets.sort(key=lambda x: x.get("match_priority", 999))

    result = {"snippets": snippets}
    # ... rest of existing code ...
    return result
```

### Step 6: Update Default Command Logic

In `preprocess_args()` (around line 1033), update to treat first positional as search term:

```python
def preprocess_args(args):
    """Treat first positional arg as search term for list command"""
    subcommands = {'create', 'paths', 'list', 'validate'}

    # Find first positional arg
    for i, arg in enumerate(args):
        # Skip flags
        if arg.startswith('-'):
            continue

        # Found positional - if not a subcommand, it's a search term
        if arg not in subcommands:
            # Insert 'list' before search term
            return args[:i] + ['list', arg] + args[i+1:]
        else:
            # It's a subcommand
            return args

    # No positional args - default to list
    return args + ['list']
```

In `main()`, update list command handler to use search:

```python
elif args.command == "list":
    # Get search term from positional arg if provided
    search_term = args.name if hasattr(args, 'name') else None

    data = manager.list(search_term=search_term)

    # Auto-detect TTY mode
    is_tty = sys.stdout.isatty()

    if args.output == "json" or not is_tty:
        # Non-interactive mode
        print(json.dumps(data, indent=2))
    else:
        # Interactive mode
        snippets = data.get("snippets", [])
        if not snippets:
            print("No snippets found.")
        else:
            selected_idx = interactive_select(snippets, operation="edit", base_dir=snippets_dir.parent)
            if selected_idx is not None:
                snippet = snippets[selected_idx]
                file_path = Path(snippet['files'][0])
                if not file_path.is_absolute():
                    file_path = snippets_dir.parent / file_path

                print(f"\nOpening {file_path} in $EDITOR...")
                if open_in_editor(file_path):
                    print("Saved.")
```

## Testing the Implementation

After implementing these changes:

```bash
cd scripts
make dev           # Setup dev environment
uv run pytest test_snippets_cli_v2.py -v   # Run tests
```

All tests should pass (GREEN phase).

## Next Steps

1. Run linter: `make lint`
2. Format code: `make format`
3. Run all tests: `make test`
4. Install globally: `make install`
5. Test command: `snippets paths`, `snippets docker`, `snippets validate`

## Commit Message

```
Refactor: Simplify snippets CLI to paths/create/search/validate

- RED: Wrote comprehensive test suite (14 tests)
- RED: Confirmed tests fail for new functionality
- GREEN: Implemented paths command to show snippet locations
- GREEN: Refactored create to accept source + destination files
- GREEN: Removed update/delete/test/set-priority commands
- GREEN: Enhanced search across name/pattern/description
- GREEN: Auto-detect TTY for interactive mode
- REFACTOR: Simplified flags (removed 5 unused flags)
- REFACTOR: Extracted helpers for validation

BREAKING: Update/delete commands removed - edit files directly

Setup: Added pyproject.toml and Makefile for `uv tool install`

Tests: 14 passing
```
