---
name: "Writing Lua"
description: "This snippet should be used when writing Neovim plugins with Lua, focusing on type safety, modular architecture, and best practices."
---

# Principles

- **Type Safety**: Use LuaCATS annotations everywhere
- **Modular Architecture**: Single Responsibility Principle - one module, one purpose
- **Thin Orchestration**: Keep init.lua under 400 lines - it coordinates, doesn't implement
- **Lazy Loading**: Minimize startup impact
- **User Choice**: Provide `<Plug>` mappings, not forced keymaps
- **0-indexed Internally**: LSP-style coordinates, convert to 1-indexed only for storage
- **Test-Driven**: Write tests using Plenary

## Module Organization

**Extract when:**
- Code block > 150 lines with distinct purpose
- 3+ similar/duplicate functions
- Complex logic needing isolated testing

**Target structure:**
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

## Type Annotations

```lua
---@class Range
---@field start {line: integer, column: integer}
---@field ["end"] {line: integer, column: integer}

---@param opts PluginConfig?
---@return PluginConfig
local function setup(opts)
  return vim.tbl_deep_extend("force", default_config, opts or {})
end
```

## Configuration

```lua
local M = {}
local default_config = { enabled = true, timeout = 5000 }
M.config = vim.deepcopy(default_config)

function M.setup(opts)
  M.config = vim.tbl_deep_extend("force", M.config, opts or {})
end
```

## Lazy Loading

```lua
local heavy
local function get_heavy()
  if not heavy then heavy = require("heavy.module") end
  return heavy
end

function M.action()
  get_heavy().do_something()
end
```

## Keymaps

```lua
vim.keymap.set("n", "<Plug>(plugin-action)", function()
  require("plugin").action()
end, { desc = "Plugin action" })
```

## Commands

```lua
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
-- 0-indexed internally (LSP-style)
local range = {
  start = { line = 0, column = 5 },
  ["end"] = { line = 0, column = 10 }
}

-- Convert to 1-indexed for storage
local function to_storage(range)
  return {
    start_line = range.start.line + 1,
    start_col = range.start.column,
    end_line = range["end"].line + 1,
    end_col = range["end"].column
  }
end
```

## Testing

```lua
describe("plugin", function()
  it("handles normal case", function()
    assert.are.equal("expected", plugin.function("input"))
  end)
end)

-- Dependency injection
M._http_get = function(url) return vim.fn.system("curl " .. url) end
function M.fetch() return M._http_get("https://api.example.com") end
```

## Error Handling

```lua
local function read_file(path)
  local ok, result = pcall(vim.fn.readfile, path)
  if not ok then return nil, "Failed to read: " .. path end
  return result, nil
end

local lines, err = read_file("config.json")
if err then
  vim.notify(err, vim.log.levels.ERROR)
  return
end
```

## Extmarks

```lua
local ns_id = vim.api.nvim_create_namespace("plugin-name")

function add_highlight(bufnr, line, col_start, col_end)
  return vim.api.nvim_buf_set_extmark(bufnr, ns_id, line, col_start, {
    end_col = col_end,
    hl_group = "PluginHighlight",
    right_gravity = true,
    end_right_gravity = false
  })
end

vim.api.nvim_set_hl(0, "PluginHighlight", { fg = "#FFD700", underline = true })
```

## Autocommands

```lua
local augroup = vim.api.nvim_create_augroup("PluginName", { clear = true })

vim.api.nvim_create_autocmd({ "BufReadPost", "BufNewFile" }, {
  group = augroup,
  callback = function(args) end,
  desc = "Initialize plugin"
})
```

## Performance

```lua
-- Cache expensive operations
local cache = {}
function M.get(key)
  if not cache[key] then cache[key] = expensive_op(key) end
  return cache[key]
end

-- Async with vim.schedule
vim.schedule(function() slow_computation() end)

-- Debounce
local timer
vim.api.nvim_create_autocmd("TextChanged", {
  callback = function()
    if timer then vim.fn.timer_stop(timer) end
    timer = vim.fn.timer_start(500, on_change)
  end
})
```

## Pitfalls

- **Monolithic init.lua**: Extract modules at 400-500 lines
- **Mark indexing**: Marks use 1-indexed lines, API uses 0-indexed
- **Buffer validity**: Always check `vim.api.nvim_buf_is_valid(buf)`
- **Global state**: Use module-local state
- **Blocking UI**: Never block main thread
- **Duplicate code**: Consolidate 3+ similar functions

## Checklist

- [ ] LuaCATS annotations on public functions
- [ ] init.lua < 400 lines
- [ ] No functions > 100 lines
- [ ] No duplicate patterns
- [ ] Modules follow SRP
- [ ] Deep merge for config
- [ ] Lazy loading for heavy deps
- [ ] Error handling (pcall or nil, err)
- [ ] 0-indexed internally, 1-indexed for storage
- [ ] Autocommands use groups
- [ ] Tests for core functionality
- [ ] `<Plug>` mappings
