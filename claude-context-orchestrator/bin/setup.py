#!/usr/bin/env python3
"""
Setup script for snippets CLI

This allows installing the snippets CLI globally and running it as 'snippets'
from anywhere on your system.

Installation:
    pip install -e /path/to/this/directory

Usage after installation:
    snippets create email --pattern "email" --content "..."
    snippets list
    snippets validate
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the version from the CLI file
VERSION = "2.0.0"

# Read README if it exists
readme_file = Path(__file__).parent.parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text()

setup(
    name="claude-snippets-cli",
    version=VERSION,
    description="CLI tool for managing Claude Code snippet configurations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Fucheng Warren Zhu",
    author_email="wzhu@college.harvard.edu",
    url="https://github.com/your-repo/claude-code-snippets-plugin",

    # Package configuration
    py_modules=["snippets_cli", "snippet_injector"],

    # Dependencies
    install_requires=[
        # No external dependencies - uses only stdlib
    ],

    # Python version requirement
    python_requires=">=3.7",

    # Entry points - creates the 'snippets' command
    entry_points={
        "console_scripts": [
            "snippets=snippets_cli:main",
        ],
    },

    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],

    # Keywords
    keywords="claude snippets cli tool code-injection productivity",

    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/your-repo/issues",
        "Source": "https://github.com/your-repo/",
    },
)
