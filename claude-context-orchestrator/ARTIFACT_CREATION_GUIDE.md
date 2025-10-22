# Simple Artifact Creation Guide

**TL;DR**: You have a simple Python tool that lets you create new artifacts from existing templates or artifacts without complex build processes.

## Quick Start

```bash
# See what's available
python3 scripts/artifact_manager.py list

# Create a new artifact from a template
python3 scripts/artifact_manager.py create base-template.html my-new-page.html "My Page Title"

# Create from an existing artifact
python3 scripts/artifact_manager.py create quibbler-system-diagram.html my-variation.html "My Variation"
```

---

## Understanding Your Artifact System

You have **two types** of artifacts:

### 1. Simple HTML Artifacts (Recommended for most cases)
- **Examples**: `my-new-doc.html`, `quibbler-system-diagram.html`
- **Pros**: No build process, instant creation, easy to edit
- **Cons**: Single file only (no component splitting)
- **Best for**: Documentation, guides, visual diagrams, educational content

### 2. React App Artifacts (Complex interactivity)
- **Examples**: `tts-concepts/`, `agent-platforms-comparison/`
- **Pros**: Full React ecosystem, component reuse, state management
- **Cons**: Requires build process, more complex setup
- **Best for**: Interactive applications, complex data visualizations

---

## Programmatic Access (For Claude)

The \`ArtifactManager\` class provides a Python API that I can use to help you:

\`\`\`python
from scripts.artifact_manager import ArtifactManager

# Initialize
manager = ArtifactManager()

# List all sources
sources = manager.list_all_sources()

# Create new artifact
result = manager.create_from_template(
    source_path="/path/to/template.html",
    new_name="my-artifact.html",
    title="My Custom Title"
)
\`\`\`

I can now easily create artifacts for you by:
1. Listing available templates
2. Selecting an appropriate one
3. Creating and customizing it
4. Opening it for you to view

**Example workflow:**
- You: "Create a Spanish culture guide"
- Me: I'll use the comprehensive template, customize it with Spanish content, embed images and TTS audio, and open it for you!

