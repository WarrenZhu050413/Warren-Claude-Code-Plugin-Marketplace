---
name: Building MCP
description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
license: Complete terms in LICENSE.txt
---

# MCP Server Development Guide

Create high-quality MCP servers that enable LLMs to effectively interact with external services. Quality is measured by how well LLMs accomplish real-world tasks using the provided tools.

---

# Process

## Phase 1: Research and Planning

### 1.1 Agent-Centric Design Principles

**Build for Workflows:** Create high-impact workflow tools, not API wrappers. Consolidate operations (e.g., `schedule_event` checks availability AND creates event).

**Optimize for Context:** Return high-signal info, not dumps. Offer "concise"/"detailed" options. Use human-readable IDs.

**Actionable Errors:** Guide agents to correct usage: "Try filter='active_only'". Make errors educational.

**Natural Subdivisions:** Tool names reflect human thinking. Group with consistent prefixes. Design around workflows.

**Evaluation-Driven:** Create realistic scenarios early. Iterate based on agent performance.

### 1.2 Study Documentation

**Load these in order:**
1. MCP Protocol: `https://modelcontextprotocol.io/llms-full.txt`
2. [📋 MCP Best Practices](./reference/mcp_best_practices.md)
3. **For Python:** `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md` + [🐍 Python Guide](./reference/python_mcp_server.md)
4. **For Node/TypeScript:** `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` + [⚡ TypeScript Guide](./reference/node_mcp_server.md)

### 1.3 Study API Documentation

Read ALL: API reference, auth, rate limits, pagination, errors, endpoints, parameters, data models. Use web search and WebFetch.

### 1.4 Create Implementation Plan

**Tool Selection:** List valuable endpoints. Prioritize common use cases. Consider tool combinations.

**Shared Utilities:** API request patterns, pagination/filtering/formatting helpers, error handling.

**Input/Output:** Validation (Pydantic/Zod), consistent formats (JSON/Markdown), detail levels (Detailed/Concise), scale planning, character limits (25k tokens).

**Error Handling:** Graceful failures, actionable LLM-friendly messages, rate limits, timeouts, auth errors.

---

## Phase 2: Implementation

### 2.1 Set Up Project

**Python:** Single `.py` or modules. MCP SDK. Pydantic validation.

**Node/TypeScript:** Project structure (`package.json`, `tsconfig.json`). MCP SDK. Zod validation.

### 2.2 Core Infrastructure First

Create shared utilities: API helpers, error handling, response formatting (JSON/Markdown), pagination, auth/tokens.

### 2.3 Implement Tools

**Input Schema:** Pydantic/Zod with constraints (min/max, regex, ranges). Clear descriptions with examples.

**Descriptions:** Summary, purpose, parameter types with examples, return schema, usage examples, error handling with next steps.

**Logic:** Use shared utilities (DRY). Async/await for I/O. Error handling. Multiple formats (JSON/Markdown). Respect pagination. Check limits, truncate.

**Annotations:** `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`.

### 2.4 Language-Specific Best Practices

**Python ([🐍 Guide](./reference/python_mcp_server.md)):** MCP SDK, Pydantic v2 with `model_config`, type hints, async/await, organized imports, constants.

**Node/TypeScript ([⚡ Guide](./reference/node_mcp_server.md)):** `server.registerTool`, Zod `.strict()`, strict mode, no `any`, explicit `Promise<T>`, build config.

---

## Phase 3: Review and Refine

### 3.1 Code Quality

Check: DRY (no duplication), composability (shared logic), consistency (similar formats), error handling (all calls), type safety (full coverage), documentation (comprehensive).

### 3.2 Test and Build

**Important:** MCP servers are long-running (stdio/http). Direct runs hang indefinitely.

**Safe testing:** Evaluation harness (recommended), tmux, or timeout (`timeout 5s python server.py`).

**Python:** `python -m py_compile your_server.py`. Test in tmux or via harness.

**Node/TypeScript:** `npm run build`. Verify `dist/index.js`. Test in tmux or via harness.

### 3.3 Quality Checklist

See [🐍 Python Guide](./reference/python_mcp_server.md) or [⚡ TypeScript Guide](./reference/node_mcp_server.md).

---

## Phase 4: Create Evaluations

**Load [✅ Evaluation Guide](./reference/evaluation.md) for complete guidelines.**

### 4.1 Create 10 Questions

Process: Tool inspection → content exploration (READ-ONLY) → question generation → answer verification.

### 4.2 Requirements

Each question: Independent, read-only, complex (multiple tool calls), realistic, verifiable (single answer), stable.

### 4.3 Format

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
</evaluation>
```

---

# Reference Files

**Core:** MCP Protocol (`https://modelcontextprotocol.io/llms-full.txt`), [📋 Best Practices](./reference/mcp_best_practices.md)

**SDK:** Python (`https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`), TypeScript (`https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`)

**Implementation:** [🐍 Python](./reference/python_mcp_server.md), [⚡ TypeScript](./reference/node_mcp_server.md)

**Evaluation:** [✅ Guide](./reference/evaluation.md)
