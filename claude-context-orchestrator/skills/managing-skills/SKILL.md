---
name: Managing Skills
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations. Adapted for Warren's system with snippet integration.
license: Complete terms in LICENSE.txt
---

# Managing Skills

**Attribution:** This skill is based on Anthropic's `skill-creator` from the [anthropic-agent-skills](https://github.com/anthropics/anthropic-agent-skills) repository, licensed under Apache License 2.0. This derivative work includes modifications for Warren's plugin system and snippet integration.

**Copyright:** Original work Copyright Anthropic. Modifications Copyright 2025 Warren Zhu.

**License:** Apache License 2.0 (see LICENSE.txt for complete terms)

---

## Warren's System Configuration

**Default Skill Location:**

All new skills for Warren's system should be created in:
```
~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/
```

**Other Skill Locations:**
- Personal: `~/.claude/skills/` (individual workflows)
- Project: `.claude/skills/` (team workflows, commit to git)
- Plugin: Plugin's `skills/` directory (distributable)

---

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks—they transform Claude from a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

**Metadata Quality:** The `name` and `description` in YAML frontmatter determine when Claude will use the skill. Be specific about what the skill does and when to use it. Use the third-person (e.g. "This skill should be used when..." instead of "Use this skill when...").

**Critical Format Rule:** Do NOT include overview sections or "When to Use This Skill" sections in the SKILL.md body. This information belongs ONLY in the YAML frontmatter description. The body should contain ONLY procedural instructions on how to use the skill.

**Incorrect format:**
```markdown
---
name: example
description: Brief description
---

# Example Skill Title

Overview paragraph explaining what the skill does.

## When to Use This Skill
- Use case 1
- Use case 2

## How to Use
Instructions here...
```

**Correct format:**
```markdown
---
name: example
description: Detailed description including what the skill does, when to use it (use case 1, use case 2, etc.), and what it provides. Use when working with X, Y, and Z operations.
---

## How to Use
Instructions here (no overview, no "when to use" section)...
```

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.

- **When to include**: For documentation that Claude should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Claude determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Claude produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables Claude to use files without loading them into context

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude (Unlimited*)

*Unlimited because scripts can be executed without reading into context window.

## Skill Creation Process

To create a skill, follow the "Skill Creation Process" in order, skipping steps only if there is a clear reason why they are not applicable.

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.

Conclude this step when there is a clear sense of the functionality the skill should support.

### Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:

1. Rotating a PDF requires re-writing the same code each time
2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill

Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:

1. Writing a frontend webapp requires the same boilerplate HTML/React each time
2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill

Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:

1. Querying BigQuery requires re-discovering the table schemas and relationships each time
2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill

To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.

### Step 3: Initializing the Skill

At this point, it is time to actually create the skill.

Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.

**For Warren's system**, create the skill directory manually in the default location:

```bash
# Create skill directory in Warren's plugin
mkdir -p ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/my-skill

# Create subdirectories as needed
mkdir -p ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/my-skill/scripts
mkdir -p ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/my-skill/references
mkdir -p ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/skills/my-skill/assets
```

**If using Anthropic's init_skill.py script** (for other systems):

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

The script creates a template with proper frontmatter and example directories.

After initialization, customize or remove the generated SKILL.md and example files as needed.

### Step 4: Edit the Skill

When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Claude to use. Focus on including information that would be beneficial and non-obvious to Claude. Consider what procedural knowledge, domain-specific details, or reusable assets would help another Claude instance execute these tasks more effectively.

#### Start with Reusable Skill Contents

To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.

Also, delete any example files and directories not needed for the skill. The initialization script creates example files in `scripts/`, `references/`, and `assets/` to demonstrate structure, but most skills won't need all of them.

#### Update SKILL.md

**Writing Style:** Write the entire skill using **imperative/infinitive form** (verb-first instructions), not second person. Use objective, instructional language (e.g., "To accomplish X, do Y" rather than "You should do X" or "If you need to do X"). This maintains consistency and clarity for AI consumption.

**Content Organization:**

1. **YAML Frontmatter (required):**
   - `name`: Skill identifier
   - `description`: Comprehensive description that includes:
     - What the skill does
     - When to use it (all use cases)
     - What it provides (features, capabilities)
     - Any pre-configured elements

2. **Markdown Body (required):**
   - **Start directly with procedural sections** (e.g., "## Environment Setup", "## Helper Script Usage")
   - **Do NOT include:**
     - Title headers repeating the skill name
     - Overview/introduction paragraphs
     - "When to Use This Skill" sections
     - "What This Skill Provides" sections
   - **DO include:**
     - Setup instructions
     - Usage examples
     - Common operations
     - Workflow guidelines
     - References to bundled resources

**Example structure:**
```markdown
---
name: my-skill
description: [Complete description with all use cases and features]
---

## Environment Setup
[Setup instructions]

## Using the Helper Script
[How to use scripts/]

## Common Operations
[Examples and patterns]
```

All reusable skill contents (scripts, references, assets) should be referenced in the body so Claude knows how to use them.

### Step 5: Packaging a Skill

Once the skill is ready, it should be packaged into a distributable zip file that gets shared with the user. The packaging process automatically validates the skill first to ensure it meets all requirements:

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory specification:

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

The packaging script will:

1. **Validate** the skill automatically, checking:
   - YAML frontmatter format and required fields
   - Skill naming conventions and directory structure
   - Description completeness and quality
   - File organization and resource references

2. **Package** the skill if validation passes, creating a zip file named after the skill (e.g., `my-skill.zip`) that includes all files and maintains the proper directory structure for distribution.

If validation fails, the script will report the errors and exit without creating a package. Fix any validation errors and run the packaging command again.

**Note:** For Warren's system, skills are typically not packaged as zip files but remain in place within the plugin directory structure.

### Step 6: Iterate

After testing the skill, users may request improvements. Often this happens right after using the skill, with fresh context of how the skill performed.

**Iteration workflow:**
1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again

---

## Snippet Integration (Warren's System)

Skills in Warren's system can be enhanced with **snippet integration** for instant keyword activation. This allows skills to be triggered by specific keywords in user prompts, providing explicit control over when a skill loads.

### When to Add Snippet Integration

Add snippet integration when:
- Skill needs instant activation by specific keyword (e.g., "USE SKILL_NAME")
- Skill is used frequently in specific contexts
- Want to bypass automatic skill discovery and ensure deterministic loading

### How to Add Snippet Integration

1. **Read the managing-snippets skill** for detailed instructions on snippet management

2. **Add entry to config.local.json** at:
   ```
   ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/config.local.json
   ```

3. **Example snippet pattern:**
   ```json
   {
     "hooks": {
       "user-prompt-submit": {
         "enabled": true,
         "order": 0,
         "patterns": [
           {
             "regex": "\\bUSE MY-SKILL\\b",
             "command": "~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/scripts/read-skill.sh 'my-skill'"
           }
         ]
       }
     }
   }
   ```

4. **Test the snippet:**
   - Type "USE MY-SKILL" in a prompt
   - Verify the skill content loads

5. **Restart Claude Code** to activate the snippet

### Snippet vs. Automatic Discovery

**Automatic Discovery:**
- Claude decides when to load skill based on description
- More flexible, adapts to varied user phrasings
- Relies on good description metadata

**Snippet Activation:**
- User explicitly triggers skill with keyword
- Deterministic loading every time
- Useful for workflows where skill should always be active

**Recommendation:** Use both approaches together. Let automatic discovery handle most cases, and provide snippet keywords for power users who want explicit control.

---

## CHANGELOG

### Modified 2025-10-26 by Warren Zhu

**Changes made to derivative work:**

1. **Added Warren's system configuration** (Section: "Warren's System Configuration")
   - Specified default skill location for Warren's plugin
   - Listed alternative skill locations

2. **Modified Step 3: Initializing the Skill**
   - Added Warren-specific manual directory creation commands
   - Noted that Anthropic's init_skill.py is for other systems

3. **Modified Step 5: Packaging a Skill**
   - Added note that Warren's system doesn't typically use zip packaging
   - Skills remain in place within plugin directory

4. **Added Section: "Snippet Integration (Warren's System)"**
   - Explained when to add snippet integration
   - Provided instructions for adding snippets
   - Documented snippet vs. automatic discovery tradeoffs
   - Referenced managing-snippets skill for details

5. **Updated YAML frontmatter**
   - Modified description to mention Warren's system and snippet integration
   - Renamed skill from "skill-creator" to "Managing Skills"

6. **Added attribution, copyright, and license notices**
   - Acknowledged Anthropic as original author
   - Included Apache License 2.0 reference

**Original work attribution:**
- Source: https://github.com/anthropics/anthropic-agent-skills/tree/main/skill-creator
- License: Apache License 2.0
- Copyright: Anthropic

All other content remains unchanged from the original Anthropic skill-creator.
