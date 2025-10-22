#!/usr/bin/env python3
"""
Component Assembler - Build artifacts from style-agnostic components
Enables true composability by separating structure, style, and behavior
"""

import json
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
from typing import List, Dict, Optional, Any
import re


class ComponentAssembler:
    """Assembles artifacts from structural components and style systems"""

    def __init__(self, style_system: str = "chinese-palette"):
        self.plugin_root = Path(__file__).parent.parent
        self.components_dir = self.plugin_root / "components" / "structural"
        self.styles_dir = self.plugin_root / "components" / "styles"
        self.behaviors_dir = self.plugin_root / "components" / "behaviors"
        self.style_system = style_system

        # Ensure directories exist
        self.components_dir.mkdir(parents=True, exist_ok=True)
        self.styles_dir.mkdir(parents=True, exist_ok=True)
        self.behaviors_dir.mkdir(parents=True, exist_ok=True)

    def list_components(self) -> List[str]:
        """List all available structural components"""
        if not self.components_dir.exists():
            return []

        return [
            f.stem for f in self.components_dir.glob("*.html")
        ]

    def list_styles(self) -> List[str]:
        """List all available style systems"""
        if not self.styles_dir.exists():
            return []

        return [
            f.stem for f in self.styles_dir.glob("*.css")
        ]

    def list_behaviors(self) -> List[str]:
        """List all available behavior scripts"""
        if not self.behaviors_dir.exists():
            return []

        return [
            f.stem for f in self.behaviors_dir.glob("*.js")
        ]

    def load_component(self, name: str) -> str:
        """Load a structural component template"""
        path = self.components_dir / f"{name}.html"

        if not path.exists():
            raise FileNotFoundError(f"Component not found: {name}")

        return path.read_text()

    def render_component(self, name: str, data: Dict[str, str]) -> str:
        """
        Render a component with data

        Args:
            name: Component name (e.g., "collapsible")
            data: Dictionary of placeholder -> value mappings

        Returns:
            Rendered HTML with all placeholders replaced
        """
        template = self.load_component(name)

        # Replace all {{PLACEHOLDER}} with values
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            template = template.replace(placeholder, str(value))

        return template

    def assemble_artifact(
        self,
        components: List[Dict[str, Any]],
        title: str,
        description: str = "",
        behaviors: Optional[List[str]] = None,
        custom_css: str = "",
        theme: str = "light"
    ) -> str:
        """
        Assemble a complete artifact from components

        Args:
            components: List of component definitions with 'type' and 'data' keys
            title: Page title
            description: Optional meta description
            behaviors: Optional list of behavior scripts to include
            custom_css: Optional custom CSS to inject
            theme: Default theme ("light" or "dark")

        Returns:
            Complete HTML artifact
        """
        behaviors = behaviors or []

        # Build HTML
        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="en" data-theme="' + theme + '">',
            "<head>",
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f"    <title>{title}</title>",
        ]

        if description:
            html_parts.append(f'    <meta name="description" content="{description}">')

        # Add style system
        style_path = self.styles_dir / f"{self.style_system}.css"
        if style_path.exists():
            html_parts.extend([
                "    <style>",
                "        /* Style System: " + self.style_system + " */",
                "        " + style_path.read_text(),
                "    </style>",
            ])

        # Add custom CSS
        if custom_css:
            html_parts.extend([
                "    <style>",
                "        /* Custom CSS */",
                "        " + custom_css,
                "    </style>",
            ])

        html_parts.extend([
            "</head>",
            "<body>",
            '    <div class="container">',
        ])

        # Add components
        for component_def in components:
            comp_type = component_def['type']
            comp_data = component_def.get('data', {})

            try:
                rendered = self.render_component(comp_type, comp_data)
                html_parts.append("        " + rendered)
            except FileNotFoundError:
                html_parts.append(f"        <!-- Component not found: {comp_type} -->")

        html_parts.append("    </div>")

        # Add behaviors
        for behavior in behaviors:
            behavior_path = self.behaviors_dir / f"{behavior}.js"
            if behavior_path.exists():
                html_parts.extend([
                    "    <script>",
                    "        // Behavior: " + behavior,
                    "        " + behavior_path.read_text(),
                    "    </script>",
                ])

        html_parts.extend([
            "</body>",
            "</html>",
        ])

        return "\n".join(html_parts)

    def from_yaml(self, yaml_path: str, output_path: Optional[str] = None) -> str:
        """
        Build artifact from YAML definition

        Args:
            yaml_path: Path to YAML definition file
            output_path: Optional output path (if None, returns HTML string)

        Returns:
            HTML artifact string
        """
        if not HAS_YAML:
            raise ImportError("PyYAML not installed. Use JSON format or install with: pip install pyyaml")

        with open(yaml_path) as f:
            config = yaml.safe_load(f)

        # Override style system if specified
        style = config.get('style', self.style_system)
        self.style_system = style

        # Build artifact
        html = self.assemble_artifact(
            components=config.get('components', []),
            title=config.get('title', 'Untitled'),
            description=config.get('description', ''),
            behaviors=config.get('behaviors', []),
            custom_css=config.get('custom_css', ''),
            theme=config.get('theme', 'light')
        )

        # Write if output specified
        if output_path:
            Path(output_path).write_text(html)

        return html

    def from_json(self, json_path: str, output_path: Optional[str] = None) -> str:
        """
        Build artifact from JSON definition

        Args:
            json_path: Path to JSON definition file
            output_path: Optional output path (if None, returns HTML string)

        Returns:
            HTML artifact string
        """
        with open(json_path) as f:
            config = json.load(f)

        # Override style system if specified
        style = config.get('style', self.style_system)
        self.style_system = style

        # Build artifact
        html = self.assemble_artifact(
            components=config.get('components', []),
            title=config.get('title', 'Untitled'),
            description=config.get('description', ''),
            behaviors=config.get('behaviors', []),
            custom_css=config.get('custom_css', ''),
            theme=config.get('theme', 'light')
        )

        # Write if output specified
        if output_path:
            Path(output_path).write_text(html)

        return html

    def extract_component_from_html(
        self,
        html_path: str,
        selector: str,
        output_name: str
    ) -> str:
        """
        Extract a component from existing HTML and save as structural template

        Args:
            html_path: Path to HTML file
            selector: CSS-like selector describing what to extract
            output_name: Name for the extracted component

        Returns:
            Path to extracted component
        """
        # TODO: Implement HTML parsing and extraction
        # This would parse HTML, find matching element, strip style classes,
        # add data attributes, identify placeholder patterns, save as template

        raise NotImplementedError("Component extraction coming soon!")


# CLI Interface
if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Assemble artifacts from components")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List available resources')
    list_parser.add_argument('resource', choices=['components', 'styles', 'behaviors', 'all'])

    # Build command
    build_parser = subparsers.add_parser('build', help='Build artifact from definition')
    build_parser.add_argument('input', help='YAML or JSON definition file')
    build_parser.add_argument('-o', '--output', required=True, help='Output HTML file')
    build_parser.add_argument('-s', '--style', help='Override style system')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create artifact from components')
    create_parser.add_argument('--title', required=True, help='Artifact title')
    create_parser.add_argument('--components', required=True, help='Components as JSON')
    create_parser.add_argument('-o', '--output', required=True, help='Output HTML file')
    create_parser.add_argument('-s', '--style', default='chinese-palette', help='Style system')
    create_parser.add_argument('--behaviors', help='Behaviors as comma-separated list')

    args = parser.parse_args()

    assembler = ComponentAssembler()

    if args.command == 'list':
        if args.resource in ['components', 'all']:
            print("\n📦 Available Components:")
            for comp in assembler.list_components():
                print(f"  - {comp}")

        if args.resource in ['styles', 'all']:
            print("\n🎨 Available Styles:")
            for style in assembler.list_styles():
                print(f"  - {style}")

        if args.resource in ['behaviors', 'all']:
            print("\n⚡ Available Behaviors:")
            for behavior in assembler.list_behaviors():
                print(f"  - {behavior}")

    elif args.command == 'build':
        if args.style:
            assembler.style_system = args.style

        input_path = Path(args.input)
        if input_path.suffix == '.yaml' or input_path.suffix == '.yml':
            assembler.from_yaml(args.input, args.output)
        elif input_path.suffix == '.json':
            assembler.from_json(args.input, args.output)
        else:
            print("Error: Input must be .yaml, .yml, or .json")
            sys.exit(1)

        print(f"✅ Artifact created: {args.output}")

    elif args.command == 'create':
        components = json.loads(args.components)
        behaviors = args.behaviors.split(',') if args.behaviors else []

        assembler.style_system = args.style

        html = assembler.assemble_artifact(
            components=components,
            title=args.title,
            behaviors=behaviors
        )

        Path(args.output).write_text(html)
        print(f"✅ Artifact created: {args.output}")

    else:
        parser.print_help()
