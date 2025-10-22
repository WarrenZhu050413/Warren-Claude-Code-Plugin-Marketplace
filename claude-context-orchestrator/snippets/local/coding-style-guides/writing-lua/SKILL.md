---
description: Writing Neovim plugins with Lua - type safety, modular architecture, and best practices
SNIPPET_NAME: writing-lua
ANNOUNCE_USAGE: false
---

# Writing Neovim Plugins with Lua

## Core Principles

1. **Type Safety**: Use LuaCATS annotations everywhere
2. **Modular Architecture**: Single Responsibility Principle - one module, one purpose
3. **Thin Orchestration**: Keep init.lua under 400 lines - it coordinates, doesn't implement
4. **Lazy Loading**: Minimize startup impact
5. **User Choice**: Provide `<Plug>` mappings, not forced keymaps
6. **0-indexed Internally**: LSP-style coordinates, convert to 1-indexed only for storage
7. **Test-Driven**: Write tests using Plenary

## Module Organization (SRP)

**When to Extract a Module:**
- Code block > 150 lines with distinct purpose
- 3+ similar/duplicate functions
- Complex logic needing isolated testing
- Code that changes for different reasons

**Target Structure:**
```
lua/plugin-name/
├── init.lua          -- ~300 lines: setup, coordination, public API
├── operations.lua    -- Core business logic
├── display.lua       -- UI/rendering
├── config.lua        -- Configuration
└── utils.lua         -- Shared utilities
```

**What Belongs in init.lua:**
✅ Module requires, setup(), autocommands, keymap/command registration, public API (thin wrappers)

**What Does NOT Belong:**
❌ Complex logic (>10 lines/function), helper functions, data transformations, duplicate patterns

## Refactoring Patterns

### Extract Module
```lua
-- Before: Mixed concerns in init.lua (170 lines)
local function normalize_range() end
local function compute_visual_range() end
function M.add_annotation_from_visual()
  local range = compute_visual_range(...)
end

-- After: Extracted to visual.lua
-- lua/plugin-name/visual.lua
local M = {}
function M.normalize_range(bufnr, range) end
function M.compute_visual_range(bufnr, opts) end
return M

-- init.lua becomes thin
local visual = require('plugin-name.visual')
function M.add_annotation_from_visual()
  local range = visual.compute_visual_range(...)
  require('plugin-name.operations').add_annotation(range)
end
```

### Consolidate Duplicates
```lua
-- Bad: 4 nearly identical functions
function M.show_tldr() ... popup.show_tldr(anno) end
function M.show_vsplit() ... popup.open_vsplit(anno) end
function M.show_hsplit() ... popup.open_hsplit(anno) end
function M.show_large() ... popup.open_large(anno) end

-- Good: Single dispatcher
---@param view_mode "tldr"|"vsplit"|"hsplit"|"large"
function M.show_annotation(view_mode)
  local anno = get_annotation_at_cursor()
  local handlers = {
    tldr = function() popup.show_tldr(anno) end,
    vsplit = function() popup.open_vsplit(anno) end,
    hsplit = function() popup.open_hsplit(anno) end,
    large = function() popup.open_large(anno) end,
  }
  handlers[view_mode]()
end
```

## Type Safety with LuaCATS

```lua
---@class Range
---@field start {line: integer, column: integer}  -- 0-indexed
---@field ["end"] {line: integer, column: integer}  -- exclusive

---@class PluginConfig
---@field enabled boolean
---@field timeout integer

---@param opts PluginConfig?
---@return PluginConfig
local function setup(opts)
  return vim.tbl_deep_extend("force", default_config, opts or {})
end
```

## Configuration & Initialization

```lua
-- Work out-of-box with defaults (don't require setup())
local M = {}
local default_config = { enabled = true, timeout = 5000 }
M.config = vim.deepcopy(default_config)

---@param opts table?
function M.setup(opts)
  M.config = vim.tbl_deep_extend("force", M.config, opts or {})
end

-- Nested config access helper
---@param key string Dot-notation (e.g., "ui.border")
function M.get_value(key)
  local parts = vim.split(key, ".", { plain = true })
  local value = M.config
  for _, part in ipairs(parts) do
    value = value[part]
    if value == nil then return nil end
  end
  return value
end
```

## Lazy Loading

```lua
-- Bad: Load immediately
local heavy = require("heavy.module")

-- Good: Lazy-load on first use
local heavy
local function get_heavy()
  if not heavy then heavy = require("heavy.module") end
  return heavy
end

function M.action()
  local h = get_heavy()  -- Loads only when called
  h.do_something()
end
```

## Keymaps

```lua
-- Provide <Plug> mappings (users choose their own keys)
vim.keymap.set("n", "<Plug>(plugin-action)", function()
  require("plugin").action()
end, { desc = "Plugin action" })

-- Document in README: vim.keymap.set("n", "<leader>p", "<Plug>(plugin-action)")
```

## User Commands

```lua
-- Use scoped commands with subcommands
local function dispatcher(opts)
  local cmds = { enable = enable, disable = disable, status = status }
  (cmds[opts.fargs[1]] or function()
    vim.notify("Unknown: " .. opts.fargs[1], vim.log.levels.ERROR)
  end)()
end

vim.api.nvim_create_user_command("Plugin", dispatcher, {
  nargs = "+",
  complete = function() return { "enable", "disable", "status" } end,
})
```

## Coordinates

```lua
-- Use 0-indexed (LSP-style) internally
---@type Range
local range = {
  start = { line = 0, column = 5 },   -- 0-indexed
  ["end"] = { line = 0, column = 10 }  -- exclusive
}

-- Convert to 1-indexed only for storage/display
local function to_storage(range)
  return {
    start_line = range.start.line + 1,  -- 1-indexed for JSON
    start_col = range.start.column,     -- Keep 0-indexed
    end_line = range["end"].line + 1,
    end_col = range["end"].column
  }
end
```

## Testing

```lua
-- Plenary test structure
describe("plugin", function()
  it("handles normal case", function()
    assert.are.equal("expected", plugin.function("input"))
  end)
end)

-- Dependency injection for testability
M._http_get = function(url) return vim.fn.system("curl " .. url) end
function M.fetch() return M._http_get("https://api.example.com") end
-- In tests: M._http_get = function() return '{"mock": "data"}' end
```

## Error Handling

```lua
---@return string[]? lines, string? error
local function read_file(path)
  local ok, result = pcall(vim.fn.readfile, path)
  if not ok then return nil, "Failed to read: " .. path end
  return result, nil
end

-- Usage
local lines, err = read_file("config.json")
if err then
  vim.notify(err, vim.log.levels.ERROR)
  return
end
```

## Extmarks

```lua
local ns_id = vim.api.nvim_create_namespace("plugin-name")

---@param bufnr integer
---@param line integer 0-indexed line
---@param col_start integer 0-indexed column
---@param col_end integer Exclusive end column
function add_highlight(bufnr, line, col_start, col_end)
  return vim.api.nvim_buf_set_extmark(bufnr, ns_id, line, col_start, {
    end_col = col_end,
    hl_group = "PluginHighlight",
    right_gravity = true,      -- Expand at start
    end_right_gravity = false  -- Don't expand at end
  })
end

vim.api.nvim_set_hl(0, "PluginHighlight", { fg = "#FFD700", underline = true })
```

## Autocommands

```lua
local augroup = vim.api.nvim_create_augroup("PluginName", { clear = true })

vim.api.nvim_create_autocmd({ "BufReadPost", "BufNewFile" }, {
  group = augroup,
  callback = function(args)
    -- Setup buffer
  end,
  desc = "Initialize plugin"
})
```

## Performance

```lua
-- 1. Cache expensive ops
local cache = {}
function M.get(key)
  if not cache[key] then cache[key] = expensive_op(key) end
  return cache[key]
end

-- 2. Use vim.schedule for async
vim.schedule(function() slow_computation() end)

-- 3. Debounce frequent events
local timer
vim.api.nvim_create_autocmd("TextChanged", {
  callback = function()
    if timer then vim.fn.timer_stop(timer) end
    timer = vim.fn.timer_start(500, on_change)
  end
})

-- 4. Local variables are 20x faster than globals
local getcwd = vim.fn.getcwd  -- Cache once
for i = 1, 1000000 do _ = getcwd() end  -- Fast
```

## Common Pitfalls

1. **Monolithic init.lua**: Extract modules at 400-500 lines
2. **Mark indexing**: Marks use 1-indexed lines, API uses 0-indexed
3. **Buffer validity**: Always check `vim.api.nvim_buf_is_valid(buf)`
4. **Global state**: Use module-local state
5. **Blocking UI**: Never block main thread with long ops
6. **Duplicate code**: Consolidate 3+ similar functions

## Code Review Checklist

- [ ] LuaCATS annotations on all public functions
- [ ] init.lua < 500 lines (preferably < 400)
- [ ] No functions > 100 lines
- [ ] No duplicate patterns (consolidate/extract)
- [ ] Modules follow SRP
- [ ] Deep merge for config (`vim.tbl_deep_extend`)
- [ ] Lazy loading for heavy deps
- [ ] Error handling (pcall or nil, err pattern)
- [ ] 0-indexed internally, 1-indexed for storage
- [ ] Autocommands use groups with clear = true
- [ ] Tests for core functionality
- [ ] `<Plug>` mappings, not hardcoded keys
