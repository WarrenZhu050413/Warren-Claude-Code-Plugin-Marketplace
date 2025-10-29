#!/usr/bin/env python3
"""
Claude Agent SDK - Python Examples

This script demonstrates various patterns for using the Claude Agent SDK in Python.
Install: pip install claude-agent-sdk

Usage:
    python3 sdk-python-example.py <example_number>
    python3 sdk-python-example.py all
"""

import asyncio
import sys
from typing import Any

# Import Claude Agent SDK components
try:
    from claude_agent_sdk import (
        query,
        ClaudeSDKClient,
        ClaudeAgentOptions,
        tool,
        create_sdk_mcp_server,
        AgentDefinition
    )
    from anthropic.types import TextBlock
except ImportError:
    print("❌ Error: claude-agent-sdk not installed")
    print("Install with: pip install claude-agent-sdk")
    sys.exit(1)


# ==============================================================================
# Example 1: Simple One-Off Query
# ==============================================================================

async def example_1_simple_query():
    """
    Use query() for single-exchange interactions.
    Best for independent tasks that don't require conversation history.
    """
    print("📝 Example 1: Simple One-Off Query")
    print("=" * 50)

    async for message in query(
        prompt="What is the capital of France?",
        options=ClaudeAgentOptions(
            model="sonnet",  # Choose model based on task complexity
            permission_mode="bypassPermissions",
            allowed_tools=[]  # No tools needed
        )
    ):
        if message.type == "result":
            print(f"Answer: {message.result}")
            print(f"Cost: ${message.total_cost_usd:.6f}")

    print("\n✅ Example 1 complete\n")


# ==============================================================================
# Example 2: Continuous Conversation
# ==============================================================================

async def example_2_continuous_conversation():
    """
    Use ClaudeSDKClient for multi-turn interactions with memory.
    Best for follow-up questions and context-dependent logic.
    """
    print("📝 Example 2: Continuous Conversation")
    print("=" * 50)

    options = ClaudeAgentOptions(
        model="sonnet",
        permission_mode="bypassPermissions",
        allowed_tools=[]
    )

    async with ClaudeSDKClient(options=options) as client:
        # First question
        print("Question 1: Remember my name...")
        await client.query("Remember: my name is Alice and I like Python")

        async for message in client.receive_response():
            if message.type == "result":
                break

        # Follow-up - Claude remembers context
        print("\nQuestion 2: What's my name?")
        await client.query("What's my name and what do I like?")

        async for message in client.receive_response():
            if message.type == "assistant":
                for block in message.message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
            elif message.type == "result":
                print(f"\nCost: ${message.total_cost_usd:.6f}")
                break

    print("\n✅ Example 2 complete\n")


# ==============================================================================
# Example 3: Custom Tools with MCP
# ==============================================================================

# Define custom tools
@tool("add", "Add two numbers", {"a": float, "b": float})
async def add_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Add two numbers together"""
    result = args['a'] + args['b']
    return {
        "content": [{
            "type": "text",
            "text": f"The sum of {args['a']} and {args['b']} is {result}"
        }]
    }


@tool("multiply", "Multiply two numbers", {"a": float, "b": float})
async def multiply_tool(args: dict[str, Any]) -> dict[str, Any]:
    """Multiply two numbers"""
    result = args['a'] * args['b']
    return {
        "content": [{
            "type": "text",
            "text": f"The product of {args['a']} and {args['b']} is {result}"
        }]
    }


async def example_3_custom_tools():
    """
    Create in-process tools with the @tool decorator.
    Best for custom functionality and integrations.
    """
    print("📝 Example 3: Custom Tools with MCP")
    print("=" * 50)

    # Create MCP server with custom tools
    calculator = create_sdk_mcp_server(
        name="calculator",
        version="1.0.0",
        tools=[add_tool, multiply_tool]
    )

    options = ClaudeAgentOptions(
        model="sonnet",
        mcp_servers={"calc": calculator},
        allowed_tools=["mcp__calc__add", "mcp__calc__multiply"],
        permission_mode="bypassPermissions"
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("What is 42 + 58? Then multiply the result by 2.")

        async for message in client.receive_response():
            if message.type == "assistant":
                for block in message.message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
            elif message.type == "result":
                print(f"\nCost: ${message.total_cost_usd:.6f}")
                break

    print("\n✅ Example 3 complete\n")


# ==============================================================================
# Example 4: Model Selection
# ==============================================================================

async def example_4_model_selection():
    """
    Demonstrate choosing different models for different tasks.
    - Haiku: Simple, fast, cheap
    - Sonnet: General purpose (default)
    - Opus: Complex reasoning (highest intelligence)
    """
    print("📝 Example 4: Model Selection")
    print("=" * 50)

    tasks = [
        ("haiku", "What is 2 + 2?", "Simple arithmetic"),
        ("sonnet", "Explain what a Python decorator is", "General explanation"),
        # ("opus", "Design a distributed cache system", "Complex architecture")  # Commented to save cost
    ]

    for model, prompt, description in tasks:
        print(f"\n{description} ({model}):")
        print("-" * 40)

        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                model=model,
                permission_mode="bypassPermissions",
                allowed_tools=[],
                max_turns=1
            )
        ):
            if message.type == "result":
                print(f"Result: {message.result[:200]}...")  # Truncate for display
                print(f"Cost: ${message.total_cost_usd:.6f}")

    print("\n✅ Example 4 complete\n")


# ==============================================================================
# Example 5: Session Management
# ==============================================================================

async def example_5_session_management():
    """
    Resume, fork, and manage conversation sessions.
    Best for long-running workflows and branching conversations.
    """
    print("📝 Example 5: Session Management")
    print("=" * 50)

    # Create initial session
    session_id = None
    options = ClaudeAgentOptions(
        model="sonnet",
        permission_mode="bypassPermissions",
        allowed_tools=[]
    )

    print("Creating initial session...")
    async with ClaudeSDKClient(options=options) as client:
        await client.query("What is 10 + 5?")

        async for message in client.receive_response():
            if message.type == "system" and message.subtype == "init":
                session_id = message.session_id
                print(f"Session ID: {session_id}")
            elif message.type == "result":
                break

    # Resume session
    print("\nResuming session...")
    options_resume = ClaudeAgentOptions(
        resume=session_id,
        model="sonnet",
        permission_mode="bypassPermissions",
        allowed_tools=[]
    )

    async with ClaudeSDKClient(options=options_resume) as client:
        await client.query("What was the answer to my previous question?")

        async for message in client.receive_response():
            if message.type == "assistant":
                for block in message.message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
            elif message.type == "result":
                break

    print("\n✅ Example 5 complete\n")


# ==============================================================================
# Example 6: Programmatic Subagents
# ==============================================================================

async def example_6_programmatic_agents():
    """
    Define specialized subagents programmatically.
    Best for delegating different types of tasks to specialized agents.
    """
    print("📝 Example 6: Programmatic Subagents")
    print("=" * 50)

    # Define specialized agents
    agents = {
        "code_reviewer": AgentDefinition(
            description="Expert code reviewer that checks for bugs and best practices. Use when reviewing code.",
            tools=["Read", "Grep", "Glob"],
            prompt="""You are an expert code reviewer. Focus on:
            1. Security vulnerabilities
            2. Performance issues
            3. Code quality and best practices
            4. Test coverage
            Provide actionable feedback.""",
            model="sonnet"
        ),
        "explainer": AgentDefinition(
            description="Clear technical explainer. Use when explaining concepts.",
            tools=[],
            prompt="""You are a technical educator. Explain concepts clearly with:
            1. Simple examples
            2. Analogies when helpful
            3. Progressive complexity
            4. Practical applications""",
            model="sonnet"
        )
    }

    options = ClaudeAgentOptions(
        agents=agents,
        permission_mode="bypassPermissions",
        allowed_tools=["Task", "Read", "Grep", "Glob"],
        max_turns=3
    )

    async with ClaudeSDKClient(options=options) as client:
        # Claude will automatically select the appropriate agent
        await client.query("Explain what async/await does in Python")

        async for message in client.receive_response():
            if message.type == "assistant":
                for block in message.message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text[:300]}...")  # Truncate for display
            elif message.type == "result":
                print(f"\nCost: ${message.total_cost_usd:.6f}")
                break

    print("\n✅ Example 6 complete\n")


# ==============================================================================
# Example 7: Error Handling and Cost Monitoring
# ==============================================================================

async def example_7_error_handling():
    """
    Demonstrate error handling and cost monitoring.
    Best for production environments and cost-sensitive applications.
    """
    print("📝 Example 7: Error Handling and Cost Monitoring")
    print("=" * 50)

    total_cost = 0.0

    try:
        options = ClaudeAgentOptions(
            model="sonnet",
            permission_mode="bypassPermissions",
            max_turns=3,  # Prevent runaway execution
            allowed_tools=[]
        )

        async with ClaudeSDKClient(options=options) as client:
            await client.query("What is machine learning?")

            async for message in client.receive_response():
                if message.type == "result":
                    cost = message.total_cost_usd
                    total_cost += cost

                    # Check for errors
                    if message.subtype == "error_during_execution":
                        print("❌ Error occurred during execution")
                    elif message.subtype == "error_max_turns":
                        print("❌ Hit max turns limit")
                    else:
                        print(f"✅ Task completed successfully")
                        print(f"Cost: ${cost:.6f}")
                        print(f"Total cost so far: ${total_cost:.6f}")

                    break

    except Exception as e:
        print(f"❌ SDK error: {e}")

    print("\n✅ Example 7 complete\n")


# ==============================================================================
# Main Menu and Execution
# ==============================================================================

def show_menu():
    """Display available examples"""
    print("\nClaude Agent SDK - Python Examples")
    print("=" * 50)
    print("Select an example to run:")
    print("")
    print("  1) Simple One-Off Query")
    print("  2) Continuous Conversation")
    print("  3) Custom Tools with MCP")
    print("  4) Model Selection (Haiku/Sonnet/Opus)")
    print("  5) Session Management (Resume/Fork)")
    print("  6) Programmatic Subagents")
    print("  7) Error Handling and Cost Monitoring")
    print("  8) Run ALL examples")
    print("  q) Quit")
    print("")


async def run_all_examples():
    """Run all examples sequentially"""
    await example_1_simple_query()
    await example_2_continuous_conversation()
    await example_3_custom_tools()
    await example_4_model_selection()
    await example_5_session_management()
    await example_6_programmatic_agents()
    await example_7_error_handling()


async def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Non-interactive mode
        choice = sys.argv[1]
        if choice == "all":
            await run_all_examples()
        elif choice.isdigit() and 1 <= int(choice) <= 7:
            examples = [
                example_1_simple_query,
                example_2_continuous_conversation,
                example_3_custom_tools,
                example_4_model_selection,
                example_5_session_management,
                example_6_programmatic_agents,
                example_7_error_handling,
            ]
            await examples[int(choice) - 1]()
        else:
            print(f"Usage: {sys.argv[0]} [1-7|all]")
            sys.exit(1)
    else:
        # Interactive mode
        while True:
            show_menu()
            choice = input("Enter your choice: ").strip()

            if choice.lower() == 'q':
                print("Goodbye!")
                break
            elif choice == '8' or choice.lower() == 'all':
                await run_all_examples()
            elif choice.isdigit() and 1 <= int(choice) <= 7:
                examples = [
                    example_1_simple_query,
                    example_2_continuous_conversation,
                    example_3_custom_tools,
                    example_4_model_selection,
                    example_5_session_management,
                    example_6_programmatic_agents,
                    example_7_error_handling,
                ]
                await examples[int(choice) - 1]()
            else:
                print("Invalid choice. Please try again.")

            if choice.lower() != 'q':
                input("\nPress Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
