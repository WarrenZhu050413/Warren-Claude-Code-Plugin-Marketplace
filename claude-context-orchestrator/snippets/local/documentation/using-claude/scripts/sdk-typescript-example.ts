#!/usr/bin/env node
/**
 * Claude Agent SDK - TypeScript Examples
 *
 * This script demonstrates various patterns for using the Claude Agent SDK in TypeScript.
 * Install: npm install @anthropic-ai/claude-agent-sdk zod
 *
 * Usage:
 *   npx ts-node sdk-typescript-example.ts <example_number>
 *   npx ts-node sdk-typescript-example.ts all
 */

import { query, ClaudeSDKClient, tool, createSdkMcpServer, AgentDefinition } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

// ==============================================================================
// Example 1: Simple One-Off Query
// ==============================================================================

async function example1SimpleQuery() {
  console.log('📝 Example 1: Simple One-Off Query');
  console.log('='.repeat(50));

  for await (const msg of query({
    prompt: "What is the capital of France?",
    options: {
      model: "sonnet",  // Choose model based on task complexity
      permissionMode: 'bypassPermissions',
      allowedTools: []  // No tools needed
    }
  })) {
    if (msg.type === 'result') {
      console.log(`Answer: ${msg.result}`);
      console.log(`Cost: $${msg.totalCostUsd.toFixed(6)}`);
    }
  }

  console.log('\n✅ Example 1 complete\n');
}

// ==============================================================================
// Example 2: Continuous Conversation
// ==============================================================================

async function example2ContinuousConversation() {
  console.log('📝 Example 2: Continuous Conversation');
  console.log('='.repeat(50));

  const client = new ClaudeSDKClient({
    model: "sonnet",
    permissionMode: 'bypassPermissions',
    allowedTools: []
  });

  try {
    // First question
    console.log('Question 1: Remember my name...');
    await client.query('Remember: my name is Bob and I like TypeScript');

    for await (const msg of client.receiveResponse()) {
      if (msg.type === 'result') break;
    }

    // Follow-up - Claude remembers context
    console.log('\nQuestion 2: What\'s my name?');
    await client.query('What\'s my name and what do I like?');

    for await (const msg of client.receiveResponse()) {
      if (msg.type === 'assistant') {
        const textContent = msg.message.content.filter(block => 'text' in block);
        textContent.forEach(block => {
          if ('text' in block) {
            console.log(`Claude: ${block.text}`);
          }
        });
      } else if (msg.type === 'result') {
        console.log(`\nCost: $${msg.totalCostUsd.toFixed(6)}`);
        break;
      }
    }
  } finally {
    await client.close();
  }

  console.log('\n✅ Example 2 complete\n');
}

// ==============================================================================
// Example 3: Custom Tools with MCP
// ==============================================================================

async function example3CustomTools() {
  console.log('📝 Example 3: Custom Tools with MCP');
  console.log('='.repeat(50));

  // Define custom tools with type-safe schemas
  const addTool = tool(
    'add',
    'Add two numbers',
    z.object({
      a: z.number(),
      b: z.number()
    }),
    async (args) => {
      const result = args.a + args.b;
      return {
        content: [{
          type: 'text' as const,
          text: `The sum of ${args.a} and ${args.b} is ${result}`
        }]
      };
    }
  );

  const multiplyTool = tool(
    'multiply',
    'Multiply two numbers',
    z.object({
      a: z.number(),
      b: z.number()
    }),
    async (args) => {
      const result = args.a * args.b;
      return {
        content: [{
          type: 'text' as const,
          text: `The product of ${args.a} and ${args.b} is ${result}`
        }]
      };
    }
  );

  // Create MCP server with custom tools
  const calculator = createSdkMcpServer({
    name: 'calculator',
    version: '1.0.0',
    tools: [addTool, multiplyTool]
  });

  const client = new ClaudeSDKClient({
    model: "sonnet",
    mcpServers: { 'calc': calculator },
    allowedTools: ['mcp__calc__add', 'mcp__calc__multiply'],
    permissionMode: 'bypassPermissions'
  });

  try {
    await client.query('What is 42 + 58? Then multiply the result by 2.');

    for await (const msg of client.receiveResponse()) {
      if (msg.type === 'assistant') {
        const textContent = msg.message.content.filter(block => 'text' in block);
        textContent.forEach(block => {
          if ('text' in block) {
            console.log(`Claude: ${block.text}`);
          }
        });
      } else if (msg.type === 'result') {
        console.log(`\nCost: $${msg.totalCostUsd.toFixed(6)}`);
        break;
      }
    }
  } finally {
    await client.close();
  }

  console.log('\n✅ Example 3 complete\n');
}

// ==============================================================================
// Example 4: Model Selection
// ==============================================================================

async function example4ModelSelection() {
  console.log('📝 Example 4: Model Selection');
  console.log('='.repeat(50));

  const tasks: Array<['haiku' | 'sonnet' | 'opus', string, string]> = [
    ['haiku', 'What is 2 + 2?', 'Simple arithmetic'],
    ['sonnet', 'Explain what a TypeScript interface is', 'General explanation'],
    // ['opus', 'Design a distributed cache system', 'Complex architecture']  // Commented to save cost
  ];

  for (const [model, prompt, description] of tasks) {
    console.log(`\n${description} (${model}):`);
    console.log('-'.repeat(40));

    for await (const msg of query({
      prompt,
      options: {
        model,
        permissionMode: 'bypassPermissions',
        allowedTools: [],
        maxTurns: 1
      }
    })) {
      if (msg.type === 'result') {
        const truncated = msg.result.substring(0, 200);
        console.log(`Result: ${truncated}...`);
        console.log(`Cost: $${msg.totalCostUsd.toFixed(6)}`);
      }
    }
  }

  console.log('\n✅ Example 4 complete\n');
}

// ==============================================================================
// Example 5: Session Management
// ==============================================================================

async function example5SessionManagement() {
  console.log('📝 Example 5: Session Management');
  console.log('='.repeat(50));

  let sessionId: string | undefined;

  // Create initial session
  console.log('Creating initial session...');
  const client1 = new ClaudeSDKClient({
    model: "sonnet",
    permissionMode: 'bypassPermissions',
    allowedTools: []
  });

  try {
    await client1.query('What is 10 + 5?');

    for await (const msg of client1.receiveResponse()) {
      if (msg.type === 'system' && msg.subtype === 'init') {
        sessionId = msg.sessionId;
        console.log(`Session ID: ${sessionId}`);
      } else if (msg.type === 'result') {
        break;
      }
    }
  } finally {
    await client1.close();
  }

  // Resume session
  if (sessionId) {
    console.log('\nResuming session...');
    const client2 = new ClaudeSDKClient({
      resume: sessionId,
      model: "sonnet",
      permissionMode: 'bypassPermissions',
      allowedTools: []
    });

    try {
      await client2.query('What was the answer to my previous question?');

      for await (const msg of client2.receiveResponse()) {
        if (msg.type === 'assistant') {
          const textContent = msg.message.content.filter(block => 'text' in block);
          textContent.forEach(block => {
            if ('text' in block) {
              console.log(`Claude: ${block.text}`);
            }
          });
        } else if (msg.type === 'result') {
          break;
        }
      }
    } finally {
      await client2.close();
    }
  }

  console.log('\n✅ Example 5 complete\n');
}

// ==============================================================================
// Example 6: Programmatic Subagents
// ==============================================================================

async function example6ProgrammaticAgents() {
  console.log('📝 Example 6: Programmatic Subagents');
  console.log('='.repeat(50));

  // Define specialized agents
  const agents: Record<string, AgentDefinition> = {
    'code_reviewer': {
      description: 'Expert code reviewer that checks for bugs and best practices. Use when reviewing code.',
      tools: ['Read', 'Grep', 'Glob'],
      prompt: `You are an expert code reviewer. Focus on:
1. Security vulnerabilities
2. Performance issues
3. Code quality and best practices
4. Test coverage
Provide actionable feedback.`,
      model: 'sonnet'
    },
    'explainer': {
      description: 'Clear technical explainer. Use when explaining concepts.',
      tools: [],
      prompt: `You are a technical educator. Explain concepts clearly with:
1. Simple examples
2. Analogies when helpful
3. Progressive complexity
4. Practical applications`,
      model: 'sonnet'
    }
  };

  const client = new ClaudeSDKClient({
    agents,
    permissionMode: 'bypassPermissions',
    allowedTools: ['Task', 'Read', 'Grep', 'Glob'],
    maxTurns: 3
  });

  try {
    await client.query('Explain what promises do in JavaScript');

    for await (const msg of client.receiveResponse()) {
      if (msg.type === 'assistant') {
        const textContent = msg.message.content.filter(block => 'text' in block);
        textContent.forEach(block => {
          if ('text' in block) {
            const truncated = block.text.substring(0, 300);
            console.log(`Claude: ${truncated}...`);
          }
        });
      } else if (msg.type === 'result') {
        console.log(`\nCost: $${msg.totalCostUsd.toFixed(6)}`);
        break;
      }
    }
  } finally {
    await client.close();
  }

  console.log('\n✅ Example 6 complete\n');
}

// ==============================================================================
// Example 7: Error Handling and Cost Monitoring
// ==============================================================================

async function example7ErrorHandling() {
  console.log('📝 Example 7: Error Handling and Cost Monitoring');
  console.log('='.repeat(50));

  let totalCost = 0;

  try {
    const client = new ClaudeSDKClient({
      model: "sonnet",
      permissionMode: 'bypassPermissions',
      maxTurns: 3,  // Prevent runaway execution
      allowedTools: []
    });

    try {
      await client.query('What is machine learning?');

      for await (const msg of client.receiveResponse()) {
        if (msg.type === 'result') {
          const cost = msg.totalCostUsd;
          totalCost += cost;

          // Check for errors
          if (msg.subtype === 'error_during_execution') {
            console.log('❌ Error occurred during execution');
          } else if (msg.subtype === 'error_max_turns') {
            console.log('❌ Hit max turns limit');
          } else {
            console.log('✅ Task completed successfully');
            console.log(`Cost: $${cost.toFixed(6)}`);
            console.log(`Total cost so far: $${totalCost.toFixed(6)}`);
          }

          break;
        }
      }
    } finally {
      await client.close();
    }
  } catch (error) {
    console.error(`❌ SDK error: ${error}`);
  }

  console.log('\n✅ Example 7 complete\n');
}

// ==============================================================================
// Main Menu and Execution
// ==============================================================================

function showMenu() {
  console.log('\nClaude Agent SDK - TypeScript Examples');
  console.log('='.repeat(50));
  console.log('Select an example to run:');
  console.log('');
  console.log('  1) Simple One-Off Query');
  console.log('  2) Continuous Conversation');
  console.log('  3) Custom Tools with MCP');
  console.log('  4) Model Selection (Haiku/Sonnet/Opus)');
  console.log('  5) Session Management (Resume/Fork)');
  console.log('  6) Programmatic Subagents');
  console.log('  7) Error Handling and Cost Monitoring');
  console.log('  8) Run ALL examples');
  console.log('  q) Quit');
  console.log('');
}

async function runAllExamples() {
  await example1SimpleQuery();
  await example2ContinuousConversation();
  await example3CustomTools();
  await example4ModelSelection();
  await example5SessionManagement();
  await example6ProgrammaticAgents();
  await example7ErrorHandling();
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length > 0) {
    // Non-interactive mode
    const choice = args[0];
    if (choice === 'all') {
      await runAllExamples();
    } else if (/^[1-7]$/.test(choice)) {
      const examples = [
        example1SimpleQuery,
        example2ContinuousConversation,
        example3CustomTools,
        example4ModelSelection,
        example5SessionManagement,
        example6ProgrammaticAgents,
        example7ErrorHandling,
      ];
      await examples[parseInt(choice) - 1]();
    } else {
      console.log(`Usage: ${process.argv[1]} [1-7|all]`);
      process.exit(1);
    }
  } else {
    // Interactive mode (simplified for TypeScript)
    console.log('Interactive mode not implemented in TypeScript version.');
    console.log(`Usage: ${process.argv[1]} [1-7|all]`);
    console.log('\nExample: npx ts-node sdk-typescript-example.ts 1');
  }
}

main().catch(console.error);
