#!/usr/bin/env python3
"""
Module 1: Basic MCP Server - Starter Code
TODO: Implement tools for analyzing git changes and suggesting PR templates
"""

import json
import os
import subprocess
from typing import Optional
from pathlib import Path

from fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("pr-agent")

# PR template directory (shared across all modules)
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Default PR templates
DEFAULT_TEMPLATES = {
    "bug.md": "Bug Fix",
    "feature.md": "Feature",
    "docs.md": "Documentation",
    "refactor.md": "Refactor",
    "test.md": "Test",
    "performance.md": "Performance",
    "security.md": "Security"
}

# Type mapping for PR templates
TYPE_MAPPING = {
    "bug": "bug.md",
    "fix": "bug.md",
    "feature": "feature.md",
    "enhancement": "feature.md",
    "docs": "docs.md",
    "documentation": "docs.md",
    "refactor": "refactor.md",
    "cleanup": "refactor.md",
    "test": "test.md",
    "testing": "test.md",
    "performance": "performance.md",
    "optimization": "performance.md",
    "security": "security.md"
}

# TODO: Replace these with your actual implementations

@mcp.tool()
async def analyze_file_changes( base_branch: str = "main",include_diff: bool = True, max_diff_lines: int = 500, working_directory: Optional[str] = None) -> str:
    """Get the full diff and list of changed files in the current git repository.   
    Args:
        base_branch: Base branch to compare against (default: main, type: string)
        include_diff: Include the full diff content (default: True, type: bool)
        max_diff_lines: Maximum number of lines to include in the diff (default: 500, type: integer)
        working_directory: Directory to run git commands in (default: current directory, type: string)
    """
    try:

        cwd = working_directory if working_directory else os.getcwd()
        cwd = find_git_root(Path(cwd)) or cwd
        print(f"Running git commands in: {cwd}")

        # Get the diff
        result = subprocess.run(
            ["git", "diff", "main", "--no-color"],
            encoding="utf-8",
            errors="replace",
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        
        diff_output = result.stdout
        diff_lines = diff_output.split('\n') if diff_output else []
        
        # Smart truncation if needed
        if len(diff_lines) > max_diff_lines:
            truncated_diff = '\n'.join(diff_lines[:max_diff_lines])
            truncated_diff += f"\n\n... Output truncated. Showing {max_diff_lines} of {len(diff_lines)} lines ..."
            diff_output = truncated_diff
        
        # Get list of changed files
        files_result = subprocess.run(
            ["git", "diff", "--name-status", f"{base_branch}"],
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )

        # Get summary statistics
        stats_result = subprocess.run(
            ["git", "diff", "--stat", f"{base_branch}"],
            capture_output=True,
            text=True,
            cwd=cwd
        )

        data = {
            "stats": stats_result.stdout,
            "total_lines": len(diff_lines),
            "diff": diff_output if include_diff else "Use include_diff=true to see diff",
            "files_changed": files_result.stdout
        }
        return json.dumps(data)
        
    except Exception as e:
        print(f"Error analyzing file changes: {e}")
        return json.dumps({"error": str(e)})


def find_git_root(start_path: Path) -> Path | None:
    path = start_path.resolve()
    for parent in [path] + list(path.parents):
        if (parent / ".git").exists():
            return parent


@mcp.tool()
async def get_pr_templates() -> str:
    """List available PR templates with their content."""
    templates = [
        {
            "filename": filename,
            "type": template_type,
            "content": (TEMPLATES_DIR / filename).read_text()
        }
        for filename, template_type in DEFAULT_TEMPLATES.items()
    ]
    
    return json.dumps(templates, indent=2)

@mcp.tool()
async def suggest_template(changes_summary: str, change_type: str) -> str:
    """Let Claude analyze the changes and suggest the most appropriate PR template.
    
    Args:
        changes_summary: Your analysis of what the changes do (type: string)
        change_type: The type of change you've identified (bug, feature, docs, refactor, test, etc.) (type: string)
    """
        # Get available templates
    templates_response = await get_pr_templates.fn()
    templates = json.loads(templates_response)
    
    # Find matching template
    template_file = TYPE_MAPPING.get(change_type.lower(), "feature.md")
    selected_template = next(
        (t for t in templates if t["filename"] == template_file),
        templates[0]  # Default to first template if no match
    )
    
    suggestion = {
        "recommended_template": selected_template,
        "reasoning": f"Based on your analysis: '{changes_summary}', this appears to be a {change_type} change.",
        "template_content": selected_template["content"],
        "usage_hint": "Claude can help you fill out this template based on the specific changes in your PR."
    }
    
    return json.dumps(suggestion, indent=2)
    


if __name__ == "__main__":
    mcp.run(transport="http",
    host="0.0.0.0",           # Bind to all interfaces
    port=8000,                # Custom port
    log_level="DEBUG")
    # mcp.run()