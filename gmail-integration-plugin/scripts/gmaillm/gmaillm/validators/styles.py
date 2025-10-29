"""Style validation utilities for gmaillm."""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

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
