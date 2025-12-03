---
name: Prompt Engineering
description: Anthropic's official prompt engineering best practices. Use when optimizing prompts, debugging outputs, or improving response quality.
---

# Prompt Engineering

**Core Principle:** Treat context as finite. Find minimum high-signal tokens for maximum results.

---

## 7 Techniques (Priority Order)

### 1. Be Clear and Direct ⭐

Most impactful. Explicit instructions outperform implicit patterns.

**Principles:**
- Specify exact output format
- List all constraints explicitly
- Define success criteria upfront
- State critical requirements multiple ways (redundancy improves compliance)

**Example:**
```
Good: Extract customer_name, order_id, issue. Format: {"customer_name": "...", "order_id": "...", "issue": "..."}
Bad: Process this ticket.
```

---

### 2. Multishot Prompting (3-5 Examples)

**Impact:** +30% accuracy (Anthropic studies)
**Optimal:** 3-5 diverse examples (fewer = insufficient, more = diminishing returns)

**Criteria:** Relevant, diverse, clear, structured (use XML)

```xml
<examples>
<example><input>Find large files</input><output>find . -type f -size +100M</output></example>
<example><input>List all files</input><output>ls -lah</output></example>
<example><input>Count Python files</input><output>find . -name "*.py" | wc -l</output></example>
</examples>
```

---

### 3. Chain of Thought (CoT)

For complex reasoning only. Skip for simple tasks.

**Use for:** Multi-step analysis, problem-solving, complex reasoning
**Skip for:** Simple tasks, well-defined operations, direct lookups

```xml
<analysis>Your reasoning</analysis>
<final_answer>Your conclusion</final_answer>
```

---

### 4. XML Tags

Semantic structure for complex prompts.

**Benefits:** Clear boundaries, prevents confusion, enables referencing
**Use for:** Multi-section prompts, semantic separation
**Skip for:** Simple single-task prompts

```xml
<instructions>Task description</instructions>
<context>Background</context>
<examples>Samples</examples>
<input>Query</input>
<output_format>Expected format</output_format>
```

---

### 5. System Prompts

Assign role or perspective.

- Be specific about expertise domain
- Define constraints/focus areas
- Use for consistent perspective

```
You are a senior security auditor reviewing code for vulnerabilities.
Focus on: SQL injection, XSS, authentication flaws.
Ignore: Style issues, performance optimizations.
```

---

### 6. Prefilling

Guide output by starting Claude's response.

**Use for:** Forcing specific format (JSON, CSV), bypassing preambles

```
User: Generate JSON for this user data
Assistant: {
```

---

### 7. Prompt Chaining

Break complex tasks into sequential steps.

**Pattern:** Step 1 → output → Step 2 (uses output) → Step 3 (uses output)
**Benefits:** Clearer results, easier debugging, better accuracy, modular

---

## Context Engineering

From Anthropic's "Effective Context Engineering for AI Agents":

**System Prompts:** Right altitude (not too specific/vague), structure with `<background>`, `<instructions>`, `<tools>`, `<output>`, start minimal, add based on failures

**Tool Design:** Token-efficient returns, minimal overlap, clear purpose, unambiguous parameters

**Examples:** Curate diverse canonical examples, not exhaustive edge cases

**Dynamic Context:** Store lightweight identifiers (paths, URLs), load at runtime, enable progressive discovery

**Long Tasks:** Compaction (summarize near limits), note-taking (persist outside context), sub-agents (specialized, clean context)

---

## Anti-Patterns

1. **Context Pollution:** Overloading with irrelevant info → Fix: Only high-signal, task-relevant context
2. **Vague Instructions:** Assuming shared understanding → Fix: Make all requirements explicit
3. **Too Few Examples:** 1-2 insufficient → Fix: Use 3-5 diverse examples
4. **Minimal Guidance:** Under-specifying causes confusion → Fix: Clear, complete instructions even if verbose
5. **Unclear Tool Contracts:** Ambiguous purposes/parameters → Fix: Clear descriptions, explicit parameters, single responsibility

---

## Optimization Workflow

1. Define success → 2. Create tests → 3. Start simple (Technique #1) → 4. Test and measure → 5. Add techniques (#2, #3, #4) → 6. Validate → 7. Stop when satisfied (avoid over-optimization)

---

## Combining Techniques

Layer multiple techniques for best results:

```xml
<task>Generate bash commands with explanations</task>
<instructions>Output: command  # explanation | No markdown | Start with command</instructions>
<examples>
<example><input>find large files</input><output>find . -type f -size +100M  # Find files >100MB</output></example>
<example><input>list files</input><output>ls -lah  # List all files with details</output></example>
<example><input>compress PDFs</input><output>tar -czf pdfs.tar.gz *.pdf  # Compress all PDFs</output></example>
</examples>
<input>{user_query}</input>
```

---

## Quick Reference

- **Simple tasks:** #1 (Be Clear) → Done
- **Consistent output:** #1 + #2 (3 examples) → Done
- **Complex reasoning:** #1 + #2 + #3 (CoT) → Test

**Rule:** Start #1, add techniques in order until quality satisfactory

---

## Resources

- [Anthropic Prompt Engineering Guide](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview)
- [Context Engineering for Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Interactive Tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)

---

## When to Use

Optimizing prompts, enforcing formats, debugging outputs, designing complex prompts, building agents/tools, maximizing performance
