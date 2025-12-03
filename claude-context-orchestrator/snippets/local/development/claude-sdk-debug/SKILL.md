---
name: "Claude SDK Debugging"
description: "Comprehensive guide for debugging Claude Agent SDK errors, TypedDict contracts, and internal SDK processing issues"
keywords: ["claude-sdk", "sdk-error", "mcp", "typeddict", "serialization", "json-error", "sdk-debugging"]
---

# Claude SDK Debugging Guide

## When to Use This

- SDK-related errors (Claude Agent SDK, MCP servers)
- JSON serialization errors involving SDK objects
- TypedDict mismatch errors
- SDK internal processing failures
- MCP server configuration errors

## Debugging Strategy

### 1. Get Full Error Traceback

**CRITICAL:** User-facing errors don't show root cause. Always check log files.

```bash
# Check error logs
tail -50 logs/errors.log

# Grep for specific error
grep "JSON serializable" logs/errors.log | tail -5

# Check recent errors
tail -100 logs/errors.log | grep -A 20 "ERROR"
```

**Why:** SDK errors surface deep in internal code. Full tracebacks show:
- Exact SDK file and line number where error occurred
- Complete call stack leading to the error
- Actual vs expected data structures

### 2. Locate SDK Source Code

Once you have the traceback, find the SDK source file:

```bash
# Find SDK files in virtual environment
find .venv/lib -name "subprocess_cli.py" -path "*/claude_agent_sdk/*"

# Or in global Python packages
find /Users/$USER/.local/lib -name "*sdk*"
```

**Read the SDK code at the failure point** to understand:
- What the SDK expects
- How it processes the data
- What checks it performs

### 3. Understand SDK Internal Processing

#### Example: McpSdkServerConfig Serialization

**Error:** `Object of type Server is not JSON serializable`

**Traceback shows:** `subprocess_cli.py:169` - `json.dumps({"mcpServers": servers_for_cli})`

**Read SDK source at line 154-169:**
```python
if isinstance(config, dict) and config.get("type") == "sdk":
    # For SDK servers, pass everything except the instance field
    sdk_config = {k: v for k, v in config.items() if k != "instance"}
    servers_for_cli[name] = sdk_config
else:
    servers_for_cli[name] = config

# Line 169: JSON serialization
json.dumps({"mcpServers": servers_for_cli})
```

**Root cause:** SDK strips `instance` field but only if:
1. `config.get("type") == "sdk"` (must have `type` key)
2. Checking `k != "instance"` (must use `instance` key, not `server`)

### 4. Common SDK Contracts

#### McpSdkServerConfig TypedDict

```python
# Correct structure
McpSdkServerConfig(
    type="sdk",        # SDK checks: config.get("type") == "sdk"
    name="server_name", # Server identifier
    instance=server     # SDK strips before JSON: k != "instance"
)

# Wrong - causes JSON serialization error
McpSdkServerConfig(
    server=server,  # Wrong key! SDK can't strip this
    name="name"      # Missing type="sdk"
)
```

**Why it matters:**
- TypedDict is just a dict at runtime - wrong keys don't error immediately
- Error surfaces later when SDK tries to process it
- SDK's internal logic depends on exact key names

#### ClaudeAgentOptions.mcp_servers

```python
# SDK expects dict[str, McpSdkServerConfig | McpStdioServerConfig | ...]
options = ClaudeAgentOptions(
    mcp_servers={
        "server_name": create_sdk_mcp_server(
            name="server_name",
            version="1.0.0",
            tools=[tool1, tool2]
        )
    }
)
```

### 5. SDK Bug Fix Checklist

When patching SDK bugs:

- [ ] **Fix original bug** (e.g., wrong parameter)
- [ ] **Match SDK contracts** (correct TypedDict keys)
- [ ] **Read SDK internal processing** (how SDK uses the return value)
- [ ] **Test downstream behavior** (not just immediate return)
- [ ] **Verify no new errors** (check logs after fix)
- [ ] **Document why** (comment referencing SDK source location)

#### Example: Patching create_sdk_mcp_server

```python
def patched_create_sdk_mcp_server(
    name: str,
    version: str = "1.0.0",  # Bug: SDK passes this to Server() which doesn't accept it
    tools: list[SdkMcpTool] | None = None,
) -> McpSdkServerConfig:
    """Patched version fixing bug #323."""
    from mcp.server import Server

    # FIX 1: Don't pass version to Server.__init__()
    # Original SDK bug: Server(name, version=version)
    server = Server(name)  # Correct: Server only accepts name

    # ... tool registration ...

    # FIX 2: Return with correct TypedDict keys
    # SDK subprocess_cli.py:154-159 expects these exact keys:
    # - type="sdk" for identification
    # - name for server name
    # - instance for Server object (stripped before JSON serialization)
    return McpSdkServerConfig(
        type="sdk",      # SDK checks config.get("type") == "sdk"
        name=name,       # Identifier
        instance=server  # SDK strips: k != "instance"
    )
```

### 6. Verification Strategy

After fixing SDK bugs:

```python
# 1. Verify immediate return
result = create_sdk_mcp_server(name="test", tools=[tool1])
assert result["type"] == "sdk"
assert result["name"] == "test"
assert "instance" in result

# 2. Verify SDK processing (simulate SDK's internal logic)
sdk_config = {k: v for k, v in result.items() if k != "instance"}
import json
json.dumps({"mcpServers": {"test": sdk_config}})  # Should not error

# 3. Test full workflow
options = ClaudeAgentOptions(mcp_servers={"test": result})
async with ClaudeSDKClient(options=options) as client:
    # Should successfully connect without JSON serialization errors
    pass
```

## Common Patterns

### Pattern 1: TypedDict Mismatch

**Symptom:** Error occurs in SDK internal code, not at return statement

**Cause:** Wrong TypedDict keys - runtime doesn't validate, fails downstream

**Solution:** Read SDK source to find exact keys it expects

### Pattern 2: JSON Serialization Errors

**Symptom:** `Object of type X is not JSON serializable`

**Cause:** SDK failed to strip non-serializable fields

**Solution:**
1. Check if SDK has stripping logic (like `k != "instance"`)
2. Verify your keys match SDK's strip conditions
3. Ensure identification keys are present (like `type="sdk"`)

### Pattern 3: SDK Parameter Bugs

**Symptom:** `TypeError: __init__() got unexpected keyword argument`

**Cause:** SDK passes parameters that underlying library doesn't accept

**Solution:**
1. Patch to remove unsupported parameters
2. But also verify SDK's processing still works
3. Match SDK's expected return structure

## Key Takeaways

1. **Always check full tracebacks** - User errors hide root cause
2. **Read SDK source** - Internal processing reveals requirements
3. **Match exact TypedDict keys** - Runtime doesn't validate structure
4. **Test downstream** - Fix original bug AND SDK's usage
5. **Document SDK source refs** - Future debugging and maintenance

## Quick Reference

```bash
# Find error in logs
tail -50 logs/errors.log

# Find SDK source
find .venv/lib -name "*subprocess_cli*"

# Verify TypedDict structure
python -c "from claude_agent_sdk import McpSdkServerConfig; print(McpSdkServerConfig.__required_keys__)"
```

## Related

- `.quibbler/rules.md` - "Check Full Error Tracebacks for SDK Failures"
- SDK Bug #323: https://github.com/anthropics/claude-agent-sdk-python/issues/323
- MCP Server Documentation: https://docs.claude.com/en/docs/agent-sdk/mcp
