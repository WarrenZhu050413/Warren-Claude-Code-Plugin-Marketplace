"""Data models for snippets management."""

from typing import List, Optional, Union

from pydantic import BaseModel, Field


class SnippetMapping(BaseModel):
    """A snippet mapping entry in the configuration.

    Defines how a prompt pattern maps to snippet file(s).
    """
    pattern: str = Field(..., description="Regex pattern to match user prompts")
    snippet: Union[str, List[str]] = Field(..., description="Path(s) to snippet file(s)")
    priority: int = Field(default=0, description="Priority for pattern matching (higher = earlier)")
    announce: bool = Field(default=True, description="Whether to announce snippet injection")


class SnippetConfig(BaseModel):
    """Complete snippets configuration.

    Contains all snippet mappings loaded from config files.
    """
    mappings: List[SnippetMapping] = Field(default_factory=list, description="List of snippet mappings")


class SnippetInfo(BaseModel):
    """Information about a single snippet.

    Used for listing and displaying snippet details.
    """
    name: str = Field(..., description="Snippet name/identifier")
    path: str = Field(..., description="Full path to snippet file")
    category: Optional[str] = Field(None, description="Category (e.g., 'development', 'output-formats')")
    pattern: Optional[str] = Field(None, description="Regex pattern that triggers this snippet")
    priority: int = Field(default=0, description="Priority in matching order")
    announce: bool = Field(default=True, description="Whether snippet announces itself")


class CategoryInfo(BaseModel):
    """Information about a snippet category.

    Groups snippets by their directory structure.
    """
    name: str = Field(..., description="Category name")
    snippet_count: int = Field(..., description="Number of snippets in category")
    sample_paths: List[str] = Field(default_factory=list, description="Sample paths (up to 3)")

    @property
    def path(self) -> str:
        """Get first sample path for display purposes.

        Returns:
            First sample path or empty string if no samples
        """
        return self.sample_paths[0] if self.sample_paths else ""


class ConfigFileInfo(BaseModel):
    """Information about a configuration file.

    Tracks config file paths and their priority.
    """
    path: str = Field(..., description="Full path to config file")
    priority: int = Field(..., description="Priority (0=base, 100=local)")
    type: str = Field(..., description="Config type ('base' or 'local')")


class PathsResponse(BaseModel):
    """Response from the paths command.

    Shows configuration structure and available categories.
    """
    config_files: List[ConfigFileInfo] = Field(default_factory=list, description="Config files loaded")
    base_dir: str = Field(..., description="Base snippets directory")
    categories: List[CategoryInfo] = Field(default_factory=list, description="Discovered categories")


class SearchResult(BaseModel):
    """Result from searching snippets.

    Contains matching snippets and search metadata.
    """
    query: str = Field(..., description="Search query used")
    matches: List[SnippetInfo] = Field(default_factory=list, description="Matching snippets")
    total_searched: int = Field(..., description="Total number of snippets searched")


class ValidationError(BaseModel):
    """A validation error found in configuration.

    Used for reporting config validation issues.
    """
    snippet_path: Optional[str] = Field(None, description="Path to problematic snippet")
    pattern: Optional[str] = Field(None, description="Problematic pattern")
    error_type: str = Field(..., description="Type of error (e.g., 'missing_file', 'invalid_pattern')")
    message: str = Field(..., description="Human-readable error message")


class ValidationResult(BaseModel):
    """Result from configuration validation.

    Reports all validation errors found.
    """
    valid: bool = Field(..., description="Whether configuration is valid")
    errors: List[ValidationError] = Field(default_factory=list, description="List of errors found")
    warnings: List[str] = Field(default_factory=list, description="Non-critical warnings")
    total_mappings: int = Field(..., description="Total mappings checked")
