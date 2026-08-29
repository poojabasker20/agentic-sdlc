"""AST Traversal & Filtering Tool for Agentic SDLC Context Management."""

import os
from typing import Optional
from google.adk.tools import FunctionTool
from utils.github_publisher import GitHubPublisherService


class ASTTraversalTool:

  def __init__(self, ast_map_markdown: str):
    self.ast_map_markdown = ast_map_markdown

  def query_ast(
      self,
      class_name: Optional[str] = None,
      keyword: Optional[str] = None,
      component_type: Optional[str] = None,
  ) -> str:
    blocks = self.ast_map_markdown.split("\n\n---\n\n")
    matching_blocks = []

    for block in blocks:
      stripped = block.strip()
      # Skip document title / header block
      if stripped.startswith("# AST Code Map") or stripped.startswith("> *Auto-generated"):
        continue

      if class_name:
        clean_class = class_name.strip("`").lower()
        if (
            f"`{clean_class}`" not in block.lower()
            and f" {clean_class} " not in block.lower()
            and f": `{clean_class}`" not in block.lower()
        ):
          continue

      if component_type:
        c_type = component_type.lower().strip()
        kind_match = f"### {c_type.capitalize()}:" in block
        # Map common architectural component types to Spring annotations
        anno_map = {
            "controller": ("@restcontroller", "@controller"),
            "service": ("@service",),
            "repository": ("@repository",),
            "component": ("@component",),
            "configuration": ("@configuration",),
            "dto": ("record", "dto", "request", "response"),
            "entity": ("@entity", "@table", "@document"),
            "enum": ("### enum:",),
        }
        anno_match = False
        if c_type in anno_map:
          anno_match = any(term in block.lower() for term in anno_map[c_type])
        elif f"@{c_type}" in block.lower():
          anno_match = True

        if not (kind_match or anno_match):
          continue

      if keyword and keyword.lower() not in block.lower():
        continue

      matching_blocks.append(block)

    if not matching_blocks:
      return (
          f"No AST matches found for class='{class_name}',"
          f" keyword='{keyword}', type='{component_type}'."
      )

    return (
        f"### Filtered AST Context ({len(matching_blocks)} matches)\n\n"
        + "\n\n---\n\n".join(matching_blocks)
    )


@FunctionTool
def query_codebase_ast(
    class_name: Optional[str] = None,
    keyword: Optional[str] = None,
    component_type: Optional[str] = None,
) -> str:
  """Tool for agents to search class signatures, endpoints, and DTO fields from AST map on GitHub."""
  # 1. Try reading from memory cache / environment
  ast_map_text = os.getenv("ACTIVE_AST_MAP_CONTENT", "")

  # 2. Try reading from local file path if present
  if not ast_map_text:
    local_paths = [
        "docs/architecture/AST_CODE_MAP.md",
        "../docs/architecture/AST_CODE_MAP.md",
    ]
    for p in local_paths:
      if os.path.exists(p):
        try:
          with open(p, "r", encoding="utf-8") as f:
            ast_map_text = f.read()
          break
        except Exception:
          pass

  # 3. Fetch directly from agentic-sdlc on GitHub if not found locally
  if not ast_map_text:
    sdlc_repo = os.getenv("SDLC_GOVERNANCE_REPO", "owner/agentic-sdlc")
    token = os.getenv("GITHUB_TOKEN", "")
    target_branch = os.getenv("GITHUB_REF_NAME", "main")

    if token:
      try:
        publisher = GitHubPublisherService(
            github_token=token, repo_name=sdlc_repo
        )
        file_content = publisher.repo.get_contents(
            "docs/architecture/AST_CODE_MAP.md", ref=target_branch
        )
        ast_map_text = file_content.decoded_content.decode("utf-8")
      except Exception as e:
        return (
            f"Error fetching AST Code Map from `{sdlc_repo}` on GitHub:"
            f" {str(e)}"
        )

  if not ast_map_text:
    return "Error: AST Code Map is empty or could not be loaded from GitHub."

  traverser = ASTTraversalTool(ast_map_text)
  return traverser.query_ast(
      class_name=class_name, keyword=keyword, component_type=component_type
  )
