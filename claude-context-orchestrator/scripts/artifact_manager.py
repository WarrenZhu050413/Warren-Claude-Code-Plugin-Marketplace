#!/usr/bin/env python3
"""
Simple Artifact Manager - Programmatic API for Claude
Manages artifact creation, listing, and template access
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import shutil

class ArtifactManager:
    """Manages artifacts and templates for simplified creation workflow"""

    def __init__(self):
        self.home = Path.home()
        self.artifacts_dir = self.home / "Desktop" / "Artifacts"
        self.plugin_root = Path(__file__).parent.parent
        self.templates_dir = self.plugin_root / "templates" / "html"

        # Ensure artifacts directory exists
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def list_all_sources(self) -> Dict[str, List[Dict[str, str]]]:
        """
        List all available templates and artifacts that can be used as sources

        Returns:
            Dictionary with 'templates' and 'artifacts' keys containing lists of sources
        """
        sources = {
            "templates": [],
            "artifacts": []
        }

        # Plugin templates
        if self.templates_dir.exists():
            # Base template
            base_template = self.templates_dir / "base-template.html"
            if base_template.exists():
                sources["templates"].append({
                    "name": "base-template.html",
                    "path": str(base_template),
                    "type": "base",
                    "lines": self._count_lines(base_template),
                    "description": "Foundation template with full styling system"
                })

            # Example templates
            examples_dir = self.templates_dir / "examples"
            if examples_dir.exists():
                for template in sorted(examples_dir.glob("*.html")):
                    sources["templates"].append({
                        "name": template.name,
                        "path": str(template),
                        "type": "example",
                        "lines": self._count_lines(template),
                        "description": self._extract_title(template)
                    })

        # Existing artifacts
        if self.artifacts_dir.exists():
            # Standalone HTML artifacts
            for artifact in sorted(self.artifacts_dir.glob("*.html")):
                sources["artifacts"].append({
                    "name": artifact.name,
                    "path": str(artifact),
                    "type": "standalone",
                    "lines": self._count_lines(artifact),
                    "description": self._extract_title(artifact)
                })

            # React project bundles
            for project_dir in sorted(self.artifacts_dir.iterdir()):
                if project_dir.is_dir():
                    bundle = project_dir / "bundle.html"
                    if bundle.exists():
                        sources["artifacts"].append({
                            "name": f"{project_dir.name}/bundle.html",
                            "path": str(bundle),
                            "type": "react-bundle",
                            "lines": self._count_lines(bundle),
                            "description": f"React project: {project_dir.name}"
                        })

        return sources

    def create_from_template(
        self,
        source_path: str,
        new_name: str,
        title: Optional[str] = None,
        overwrite: bool = False
    ) -> Dict[str, str]:
        """
        Create a new artifact from a template or existing artifact

        Args:
            source_path: Path to template or artifact to use as source
            new_name: Name for the new artifact (with or without .html)
            title: Optional title to replace {{TITLE}} placeholder
            overwrite: Whether to overwrite existing file

        Returns:
            Dictionary with creation status and paths
        """
        # Ensure .html extension
        if not new_name.endswith('.html'):
            new_name = f"{new_name}.html"

        source = Path(source_path)
        if not source.exists():
            return {
                "success": False,
                "error": f"Source file not found: {source_path}"
            }

        output_path = self.artifacts_dir / new_name

        # Check if exists
        if output_path.exists() and not overwrite:
            return {
                "success": False,
                "error": f"File already exists: {output_path}. Use overwrite=True to replace."
            }

        # Read source content
        content = source.read_text()

        # Replace title if provided
        if title and "{{TITLE}}" in content:
            content = content.replace("{{TITLE}}", title)

        # Write to new artifact
        output_path.write_text(content)

        return {
            "success": True,
            "path": str(output_path),
            "name": new_name,
            "lines": self._count_lines(output_path),
            "source": source_path
        }

    def get_source_by_name(self, name: str) -> Optional[str]:
        """
        Find a template or artifact path by name

        Args:
            name: Name of template or artifact (e.g., "base-template.html")

        Returns:
            Full path to the source, or None if not found
        """
        sources = self.list_all_sources()

        # Check templates
        for template in sources["templates"]:
            if template["name"] == name:
                return template["path"]

        # Check artifacts
        for artifact in sources["artifacts"]:
            if artifact["name"] == name:
                return artifact["path"]

        return None

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, 'r') as f:
                return sum(1 for _ in f)
        except:
            return 0

    def _extract_title(self, file_path: Path) -> str:
        """Extract title from HTML file"""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if '<title>' in line:
                        title = line.split('<title>')[1].split('</title>')[0]
                        return title.strip()
        except:
            pass
        return "No title found"

    def print_sources(self):
        """Pretty print all available sources"""
        sources = self.list_all_sources()

        print("\n" + "="*80)
        print("📦 AVAILABLE TEMPLATES")
        print("="*80)
        for template in sources["templates"]:
            print(f"\n  {template['name']}")
            print(f"  ├─ Type: {template['type']}")
            print(f"  ├─ Lines: {template['lines']}")
            print(f"  ├─ Description: {template['description']}")
            print(f"  └─ Path: {template['path']}")

        print("\n" + "="*80)
        print("🎨 EXISTING ARTIFACTS")
        print("="*80)
        if sources["artifacts"]:
            for artifact in sources["artifacts"]:
                print(f"\n  {artifact['name']}")
                print(f"  ├─ Type: {artifact['type']}")
                print(f"  ├─ Lines: {artifact['lines']}")
                print(f"  ├─ Description: {artifact['description']}")
                print(f"  └─ Path: {artifact['path']}")
        else:
            print("\n  No artifacts found in ~/Desktop/Artifacts/")

        print("\n" + "="*80 + "\n")


# CLI Interface
if __name__ == "__main__":
    import sys

    manager = ArtifactManager()

    if len(sys.argv) == 1 or sys.argv[1] == "list":
        # List all sources
        manager.print_sources()

    elif sys.argv[1] == "create":
        # Create new artifact from source
        if len(sys.argv) < 4:
            print("Usage: python artifact_manager.py create <source_name> <new_name> [title]")
            sys.exit(1)

        source_name = sys.argv[2]
        new_name = sys.argv[3]
        title = sys.argv[4] if len(sys.argv) > 4 else None

        # Find source
        source_path = manager.get_source_by_name(source_name)
        if not source_path:
            print(f"❌ Source not found: {source_name}")
            print("\nAvailable sources:")
            manager.print_sources()
            sys.exit(1)

        # Create artifact
        result = manager.create_from_template(source_path, new_name, title)

        if result["success"]:
            print(f"\n✅ Artifact created successfully!")
            print(f"   📁 {result['path']}")
            print(f"   📝 {result['lines']} lines")
            print(f"   🎯 Source: {result['source']}")
        else:
            print(f"\n❌ Error: {result['error']}")

    elif sys.argv[1] == "json":
        # Output as JSON for programmatic use
        sources = manager.list_all_sources()
        print(json.dumps(sources, indent=2))

    else:
        print("Usage:")
        print("  python artifact_manager.py list              - List all templates and artifacts")
        print("  python artifact_manager.py create <src> <new> [title] - Create new artifact")
        print("  python artifact_manager.py json              - Output sources as JSON")
