"""Style validation utilities for gmaillm."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import typer
import yaml
from rich.console import Console

console = Console()

# Style validation constants
STYLE_NAME_MIN_LENGTH = 3
STYLE_NAME_MAX_LENGTH = 50
STYLE_DESC_MIN_LENGTH = 30
STYLE_DESC_MAX_LENGTH = 200
INVALID_STYLE_CHARS = r'[/\\<>&"\'\`\s]'  # No slashes, spaces, or special chars
RESERVED_STYLE_NAMES = {'default', 'template', 'base', 'system'}
REQUIRED_STYLE_SECTIONS = ['examples', 'greeting', 'body', 'closing', 'do', 'dont']
STYLE_SECTION_ORDER = ['examples', 'greeting', 'body', 'closing', 'do', 'dont']
MIN_EXAMPLES = 1
MAX_EXAMPLES = 3
MIN_DO_ITEMS = 2
MIN_DONT_ITEMS = 2

# JSON Schema for programmatic style creation
STYLE_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["name", "description", "greeting", "body", "closing", "do", "dont"],
    "properties": {
        "name": {
            "type": "string",
            "minLength": STYLE_NAME_MIN_LENGTH,
            "maxLength": STYLE_NAME_MAX_LENGTH,
            "pattern": "^[a-z0-9-]+$",
            "description": "Style identifier (lowercase, hyphens only, no special chars or spaces)"
        },
        "description": {
            "type": "string",
            "minLength": STYLE_DESC_MIN_LENGTH,
            "maxLength": STYLE_DESC_MAX_LENGTH,
            "pattern": "^When to use:",
            "description": "Must start with 'When to use:' and describe the scenario (30-200 chars)"
        },
        "examples": {
            "type": "array",
            "minItems": MIN_EXAMPLES,
            "maxItems": MAX_EXAMPLES,
            "items": {
                "type": "string",
                "minLength": 10
            },
            "description": "1-3 complete email examples showing the style in action"
        },
        "greeting": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "string",
                "minLength": 1
            },
            "description": "List of greeting patterns (e.g., 'Dear {name}', 'Hi {name}')"
        },
        "body": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "string",
                "minLength": 1
            },
            "description": "List of body writing guidelines and principles"
        },
        "closing": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "string",
                "minLength": 1
            },
            "description": "List of closing patterns (e.g., 'Best regards', 'Sincerely')"
        },
        "do": {
            "type": "array",
            "minItems": MIN_DO_ITEMS,
            "items": {
                "type": "string",
                "minLength": 1
            },
            "description": "Best practices for this style (minimum 2 items)"
        },
        "dont": {
            "type": "array",
            "minItems": MIN_DONT_ITEMS,
            "items": {
                "type": "string",
                "minLength": 1
            },
            "description": "Things to avoid with this style (minimum 2 items)"
        }
    },
    "additionalProperties": False
}


def get_style_json_schema() -> Dict[str, Any]:
    """Return the JSON schema for style creation.

    Returns:
        Dictionary containing the JSON schema definition
    """
    return STYLE_JSON_SCHEMA


def get_style_json_schema_string(indent: int = 2) -> str:
    """Return formatted JSON schema for CLI help and documentation.

    Args:
        indent: Number of spaces for JSON indentation (default: 2)

    Returns:
        Pretty-printed JSON schema string
    """
    return json.dumps(STYLE_JSON_SCHEMA, indent=indent)


def validate_json_against_schema(json_data: Dict[str, Any]) -> List[str]:
    """Validate JSON data against the style schema.

    Args:
        json_data: Dictionary containing style data

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check required fields
    required_fields = STYLE_JSON_SCHEMA["required"]
    for field in required_fields:
        if field not in json_data:
            errors.append(f"Missing required field: '{field}'")

    # Validate name
    if "name" in json_data:
        name = json_data["name"]
        if not isinstance(name, str):
            errors.append(f"Field 'name' must be a string, got {type(name).__name__}")
        else:
            if len(name) < STYLE_NAME_MIN_LENGTH:
                errors.append(f"Field 'name' too short (min {STYLE_NAME_MIN_LENGTH} chars)")
            if len(name) > STYLE_NAME_MAX_LENGTH:
                errors.append(f"Field 'name' too long (max {STYLE_NAME_MAX_LENGTH} chars)")
            if not re.match(r'^[a-z0-9-]+$', name):
                errors.append(f"Field 'name' contains invalid characters (only lowercase, numbers, hyphens)")

    # Validate description
    if "description" in json_data:
        desc = json_data["description"]
        if not isinstance(desc, str):
            errors.append(f"Field 'description' must be a string, got {type(desc).__name__}")
        else:
            if not desc.startswith("When to use:"):
                errors.append("Field 'description' must start with 'When to use:'")
            if len(desc) < STYLE_DESC_MIN_LENGTH:
                errors.append(f"Field 'description' too short (min {STYLE_DESC_MIN_LENGTH} chars)")
            if len(desc) > STYLE_DESC_MAX_LENGTH:
                errors.append(f"Field 'description' too long (max {STYLE_DESC_MAX_LENGTH} chars)")

    # Validate array fields
    array_fields = {
        "examples": (MIN_EXAMPLES, MAX_EXAMPLES),
        "greeting": (1, None),
        "body": (1, None),
        "closing": (1, None),
        "do": (MIN_DO_ITEMS, None),
        "dont": (MIN_DONT_ITEMS, None)
    }

    for field, (min_items, max_items) in array_fields.items():
        if field in json_data:
            value = json_data[field]
            if not isinstance(value, list):
                errors.append(f"Field '{field}' must be an array, got {type(value).__name__}")
            else:
                if len(value) < min_items:
                    errors.append(f"Field '{field}' must have at least {min_items} item(s)")
                if max_items and len(value) > max_items:
                    errors.append(f"Field '{field}' must have at most {max_items} item(s)")

                # Check all items are strings
                for i, item in enumerate(value):
                    if not isinstance(item, str):
                        errors.append(f"Field '{field}[{i}]' must be a string, got {type(item).__name__}")
                    elif not item.strip():
                        errors.append(f"Field '{field}[{i}]' cannot be empty")

    # Check for unexpected fields
    allowed_fields = set(STYLE_JSON_SCHEMA["properties"].keys())
    extra_fields = set(json_data.keys()) - allowed_fields
    if extra_fields:
        errors.append(f"Unexpected fields: {', '.join(sorted(extra_fields))}")

    return errors


def create_style_from_json(json_data: Dict[str, Any], output_path: Path) -> None:
    """Create style markdown file from JSON data.

    Args:
        json_data: Dictionary containing style data (must be valid against schema)
        output_path: Path where the style file should be written

    Raises:
        ValueError: If JSON data is invalid
    """
    # Validate JSON data
    validation_errors = validate_json_against_schema(json_data)
    if validation_errors:
        raise ValueError(f"Invalid JSON data:\n" + "\n".join(f"  - {err}" for err in validation_errors))

    # Build markdown content
    lines = []

    # YAML frontmatter
    lines.append("---")
    lines.append(f"name: \"{json_data['name']}\"")
    lines.append(f"description: \"{json_data['description']}\"")
    lines.append("---")
    lines.append("")

    # Examples section
    lines.append("<examples>")
    lines.append("")
    examples = json_data.get("examples", [])
    lines.append("\n\n---\n\n".join(examples))
    lines.append("")
    lines.append("</examples>")
    lines.append("")

    # Greeting section
    lines.append("<greeting>")
    lines.append("")
    for item in json_data["greeting"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("</greeting>")
    lines.append("")

    # Body section
    lines.append("<body>")
    lines.append("")
    for item in json_data["body"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("</body>")
    lines.append("")

    # Closing section
    lines.append("<closing>")
    lines.append("")
    for item in json_data["closing"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("</closing>")
    lines.append("")

    # Do section
    lines.append("<do>")
    lines.append("")
    for item in json_data["do"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("</do>")
    lines.append("")

    # Dont section
    lines.append("<dont>")
    lines.append("")
    for item in json_data["dont"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("</dont>")

    # Write to file
    content = "\n".join(lines)
    output_path.write_text(content)


def validate_style_name(name: str) -> None:
    """Validate style name for file system safety.

    Args:
        name: Style name to validate

    Raises:
        typer.Exit: If style name is invalid
    """
    if len(name) == 0:
        console.print("[red]Error: Style name cannot be empty[/red]")
        raise typer.Exit(code=1)

    if len(name) < STYLE_NAME_MIN_LENGTH:
        console.print(f"[red]Error: Style name too short (min {STYLE_NAME_MIN_LENGTH} characters)[/red]")
        raise typer.Exit(code=1)

    if len(name) > STYLE_NAME_MAX_LENGTH:
        console.print(f"[red]Error: Style name too long (max {STYLE_NAME_MAX_LENGTH} characters)[/red]")
        raise typer.Exit(code=1)

    if re.search(INVALID_STYLE_CHARS, name):
        console.print("[red]Error: Style name contains invalid characters (no spaces or special chars)[/red]")
        raise typer.Exit(code=1)

    if name.lower() in RESERVED_STYLE_NAMES:
        console.print(f"[red]Error: '{name}' is a reserved name[/red]")
        raise typer.Exit(code=1)


@dataclass
class StyleLintError:
    """Represents a style validation error."""
    section: str
    message: str
    line: Optional[int] = None

    def __str__(self) -> str:
        """Format error message."""
        if self.line:
            return f"[{self.section}] Line {self.line}: {self.message}"
        return f"[{self.section}] {self.message}"


class StyleLinter:
    """Linter for email style files with strict XML format validation."""

    def lint(self, content: str) -> List[StyleLintError]:
        """Run all linting checks on style content.

        Args:
            content: Style file content to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # 1. Check YAML frontmatter
        errors.extend(self._lint_frontmatter(content))

        # 2. Check XML sections exist
        errors.extend(self._lint_sections_exist(content))

        # 3. Check XML sections order
        errors.extend(self._lint_sections_order(content))

        # 4. Check section content
        errors.extend(self._lint_section_content(content))

        # 5. Check formatting
        errors.extend(self._lint_formatting(content))

        return errors

    def lint_and_fix(self, content: str) -> Tuple[str, List[StyleLintError]]:
        """Run linting and auto-fix formatting issues.

        Args:
            content: Style file content to validate and fix

        Returns:
            Tuple of (fixed_content, remaining_errors)
        """
        fixed_content = content

        # Auto-fix trailing whitespace
        lines = fixed_content.split('\n')
        fixed_lines = [line.rstrip() for line in lines]
        fixed_content = '\n'.join(fixed_lines)

        # Auto-fix list item spacing
        fixed_content = re.sub(r'^-([^ ])', r'- \1', fixed_content, flags=re.MULTILINE)

        # Run lint on fixed content
        errors = self.lint(fixed_content)

        # Filter out errors that were fixed
        remaining_errors = [
            err for err in errors
            if 'trailing whitespace' not in err.message.lower()
            and 'list syntax' not in err.message.lower()
        ]

        return fixed_content, remaining_errors

    def _lint_frontmatter(self, content: str) -> List[StyleLintError]:
        """Validate YAML frontmatter."""
        errors = []

        if not content.startswith('---'):
            errors.append(StyleLintError('frontmatter', 'Missing YAML frontmatter'))
            return errors

        try:
            end_idx = content.index('\n---\n', 3)
            frontmatter_text = content[3:end_idx]

            metadata = yaml.safe_load(frontmatter_text)

            # Check required fields
            if 'name' not in metadata:
                errors.append(StyleLintError('frontmatter', 'Missing "name" field'))
            else:
                name = metadata['name']
                if len(name) < STYLE_NAME_MIN_LENGTH:
                    errors.append(StyleLintError('frontmatter', f'Name too short (min {STYLE_NAME_MIN_LENGTH} chars)'))
                if len(name) > STYLE_NAME_MAX_LENGTH:
                    errors.append(StyleLintError('frontmatter', f'Name too long (max {STYLE_NAME_MAX_LENGTH} chars)'))

            if 'description' not in metadata:
                errors.append(StyleLintError('frontmatter', 'Missing "description" field'))
            else:
                desc = metadata['description']
                if not desc.startswith('When to use:'):
                    errors.append(StyleLintError('frontmatter', 'Description must start with "When to use:"'))
                if len(desc) < STYLE_DESC_MIN_LENGTH:
                    errors.append(StyleLintError('frontmatter', f'Description too short (min {STYLE_DESC_MIN_LENGTH} chars)'))
                if len(desc) > STYLE_DESC_MAX_LENGTH:
                    errors.append(StyleLintError('frontmatter', f'Description too long (max {STYLE_DESC_MAX_LENGTH} chars)'))

            # Check for extra fields
            allowed_fields = {'name', 'description'}
            extra_fields = set(metadata.keys()) - allowed_fields
            if extra_fields:
                errors.append(StyleLintError('frontmatter', f'Unexpected fields: {", ".join(extra_fields)}'))

        except ValueError:
            errors.append(StyleLintError('frontmatter', 'Invalid YAML frontmatter (missing closing ---)'))
        except yaml.YAMLError as e:
            errors.append(StyleLintError('frontmatter', f'Invalid YAML syntax: {e}'))

        return errors

    def _lint_sections_exist(self, content: str) -> List[StyleLintError]:
        """Check that all required sections exist."""
        errors = []

        for section in REQUIRED_STYLE_SECTIONS:
            if f'<{section}>' not in content:
                errors.append(StyleLintError(section, f'Missing required section: <{section}>'))
            elif f'</{section}>' not in content:
                errors.append(StyleLintError(section, f'Section not properly closed: <{section}>'))

        return errors

    def _lint_sections_order(self, content: str) -> List[StyleLintError]:
        """Check that sections appear in correct order (STRICT)."""
        errors = []

        section_positions = {}
        for section in REQUIRED_STYLE_SECTIONS:
            match = re.search(f'<{section}>', content)
            if match:
                section_positions[section] = match.start()

        # Check STRICT order
        prev_pos = -1
        for section in STYLE_SECTION_ORDER:
            if section in section_positions:
                pos = section_positions[section]
                if pos < prev_pos:
                    errors.append(StyleLintError(section, f'Section <{section}> out of order (must follow {STYLE_SECTION_ORDER})'))
                prev_pos = pos

        return errors

    def _lint_section_content(self, content: str) -> List[StyleLintError]:
        """Validate content within each section."""
        errors = []

        for section in REQUIRED_STYLE_SECTIONS:
            section_content = self._extract_section_content(content, section)
            if section_content is None:
                continue  # Already caught by _lint_sections_exist

            if not section_content.strip():
                errors.append(StyleLintError(section, f'Section <{section}> is empty'))
                continue

            # Section-specific validation
            if section == 'examples':
                examples = [ex.strip() for ex in section_content.split('---') if ex.strip()]
                if len(examples) < MIN_EXAMPLES:
                    errors.append(StyleLintError(section, f'Must have at least {MIN_EXAMPLES} example(s)'))
                if len(examples) > MAX_EXAMPLES:
                    errors.append(StyleLintError(section, f'Too many examples (max {MAX_EXAMPLES})'))

            elif section in ['greeting', 'body', 'closing', 'do', 'dont']:
                lines = [line for line in section_content.split('\n') if line.strip()]
                list_items = [line for line in lines if line.strip().startswith('-')]

                if len(list_items) == 0:
                    errors.append(StyleLintError(section, f'Section <{section}> must contain list items'))

                if section in ['do', 'dont'] and len(list_items) < 2:
                    min_items = MIN_DO_ITEMS if section == 'do' else MIN_DONT_ITEMS
                    errors.append(StyleLintError(section, f'Section <{section}> must have at least {min_items} items'))

                # Check list formatting
                for i, line in enumerate(lines):
                    if line.strip().startswith('-'):
                        if not line.startswith('- '):
                            errors.append(StyleLintError(section, f'Invalid list syntax (use "- " with space)', line=i+1))

        return errors

    def _extract_section_content(self, content: str, section: str) -> Optional[str]:
        """Extract content between <section> and </section>."""
        match = re.search(f'<{section}>(.*?)</{section}>', content, re.DOTALL)
        if match:
            return match.group(1)
        return None

    def _lint_formatting(self, content: str) -> List[StyleLintError]:
        """Check general formatting issues."""
        errors = []

        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Check trailing whitespace
            if line != line.rstrip():
                errors.append(StyleLintError('formatting', f'Trailing whitespace', line=i+1))

        return errors
