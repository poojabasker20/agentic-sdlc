"""Spring Boot Java AST parser using Tree-Sitter.

Extracts controllers, endpoints, HTTP methods, DTOs (classes/records),
and validation annotations into a structured Markdown summary.
"""

import os
from typing import List, Optional
from tree_sitter import Language, Node, Parser
import tree_sitter_java as tsjava
from utils.github_publisher import GitHubPublisherService


class JavaCodeParser:
  """Parses Spring Boot Java files into a structured Markdown AST summary."""

  def __init__(self):
    self.language = Language(tsjava.language())
    self.parser = Parser(self.language)

  def _node_text(self, node: Node, source_bytes: bytes) -> str:
    return (
        source_bytes[node.start_byte : node.end_byte]
        .decode("utf-8", errors="ignore")
        .strip()
    )

  def _get_annotations(
      self, node: Node, source_bytes: bytes
  ) -> List[str]:
    annos = []
    for child in node.children:
      if child.type == "modifiers":
        for m in child.children:
          if m.type in ("annotation", "marker_annotation"):
            annos.append(self._node_text(m, source_bytes))
    return annos

  def parse_java_file(
      self, code_bytes: bytes, file_path: str
  ) -> Optional[str]:
    """Extracts classes, records, endpoints, fields, and annotations from Java code."""
    try:
      tree = self.parser.parse(code_bytes)
      root_node = tree.root_node
    except Exception:
      return None

    classes_info = []

    def traverse(node: Node):
      if node.type in (
          "class_declaration",
          "record_declaration",
          "interface_declaration",
          "enum_declaration",
      ):
        annotations = self._get_annotations(node, code_bytes)
        name_node = node.child_by_field_name("name")
        name = (
            self._node_text(name_node, code_bytes) if name_node else "Unknown"
        )
        kind = (
            "Record"
            if node.type == "record_declaration"
            else (
                "Interface"
                if node.type == "interface_declaration"
                else (
                    "Enum"
                    if node.type == "enum_declaration"
                    else "Class"
                )
            )
        )

        class_summary = [f"### {kind}: `{name}` (`{file_path}`)"]
        if annotations:
          class_summary.append(
              f"- **Annotations**: `{', '.join(annotations)}`"
          )

        methods, fields = [], []

        if node.type == "record_declaration":
          params_node = node.child_by_field_name("parameters")
          if params_node:
            record_params = self._node_text(params_node, code_bytes)
            fields.append(f"  - **Record Components**: `{record_params}`")

        body_node = node.child_by_field_name("body")
        if body_node:
          for child in body_node.children:
            if child.type == "method_declaration":
              m_annos = self._get_annotations(child, code_bytes)
              m_name_node = child.child_by_field_name("name")
              m_name = (
                  self._node_text(m_name_node, code_bytes)
                  if m_name_node
                  else "method"
              )
              params_node = child.child_by_field_name("parameters")
              params_str = (
                  self._node_text(params_node, code_bytes)
                  if params_node
                  else "()"
              )
              ret_node = child.child_by_field_name("type")
              ret_str = (
                  self._node_text(ret_node, code_bytes)
                  if ret_node
                  else ("[Constructor]" if m_name == name else "void")
              )

              http_anno = [
                  a
                  for a in m_annos
                  if any(
                      m in a
                      for m in [
                          "Mapping",
                          "GetMapping",
                          "PostMapping",
                          "PutMapping",
                          "DeleteMapping",
                      ]
                  )
              ]
              if http_anno:
                methods.append(
                    f"  - **Endpoint**: `{', '.join(http_anno)}` -> `{ret_str}"
                    f" {m_name}{params_str}`"
                )
              else:
                methods.append(
                    f"  - **Method**: `{ret_str} {m_name}{params_str}`"
                    f" (Annotations: `{', '.join(m_annos)}`)"
                )

            elif child.type == "constructor_declaration":
              c_annos = self._get_annotations(child, code_bytes)
              c_name_node = child.child_by_field_name("name")
              c_name = (
                  self._node_text(c_name_node, code_bytes)
                  if c_name_node
                  else name
              )
              params_node = child.child_by_field_name("parameters")
              params_str = (
                  self._node_text(params_node, code_bytes)
                  if params_node
                  else "()"
              )
              anno_str = f" (Annotations: `{', '.join(c_annos)}`)" if c_annos else ""
              methods.append(
                  f"  - **Constructor**: `{c_name}{params_str}`{anno_str}"
              )

            elif child.type == "field_declaration":
              f_annos = self._get_annotations(child, code_bytes)
              f_text = self._node_text(child, code_bytes)
              fields.append(
                  f"  - **Field**: `{f_text}` (Validation:"
                  f" `{', '.join(f_annos)}`)"
              )

            elif child.type == "enum_constant":
              e_name = self._node_text(child, code_bytes)
              fields.append(f"  - **Enum Constant**: `{e_name}`")

        if methods:
          class_summary.append("- **Methods / Endpoints**:")
          class_summary.extend(methods)
        if fields:
          class_summary.append("- **Fields / Components**:")
          class_summary.extend(fields)

        classes_info.append("\n".join(class_summary))

      for child in node.children:
        traverse(child)

    traverse(root_node)
    return "\n\n".join(classes_info) if classes_info else None


class ASTMapPublisher:
  """Generates AST Map from target source repo and commits the artifact to SDLC governance repo."""

  def __init__(
      self,
      github_token: Optional[str] = None,
      source_code_repo: Optional[str] = None,
      target_sdlc_repo: Optional[str] = None,
  ):
    token = github_token or os.getenv("GITHUB_TOKEN", "")
    src_repo = source_code_repo or os.getenv(
        "TARGET_CODEBASE_REPO", "owner/springboot-hello-world"
    )
    sdlc_repo = target_sdlc_repo or os.getenv(
        "SDLC_GOVERNANCE_REPO", "owner/agentic-sdlc"
    )

    # Publisher for committing AST_CODE_MAP.md to agentic-sdlc
    self.publisher = GitHubPublisherService(token, sdlc_repo)
    # Source publisher for scanning .java files from springboot-hello-world
    self.source_publisher = GitHubPublisherService(token, src_repo)
    self.parser = JavaCodeParser()

  def generate_and_commit_ast_map(
      self,
      source_branch: str = "main",
      target_branch: str = "main",
      artifact_path: str = "docs/architecture/AST_CODE_MAP.md",
  ) -> str:
    """Scans Java files in source repo, compiles Markdown AST, and commits to governance repo."""
    tree = self.source_publisher.repo.get_git_tree(
        source_branch, recursive=True
    )
    java_files = [
        element
        for element in tree.tree
        if element.path.endswith(".java") and element.type == "blob"
    ]

    if not java_files:
      return (
          f"No Java files found in `{self.source_publisher.repo.full_name}` on"
          f" branch `{source_branch}`."
      )

    summary_blocks = [
        f"# AST Code Map"
        f" (`{self.source_publisher.repo.full_name}` @ `{source_branch}`)\n",
        "> *Auto-generated artifact used by Agentic SDLC pipeline for context"
        " grounding.*\n",
    ]

    for file_element in java_files:
      file_content = self.source_publisher.repo.get_contents(
          file_element.path, ref=source_branch
      )
      code_bytes = file_content.decoded_content
      parsed_markdown = self.parser.parse_java_file(
          code_bytes, file_element.path
      )
      if parsed_markdown:
        summary_blocks.append(parsed_markdown)

    ast_map_content = "\n\n---\n\n".join(summary_blocks)
    commit_msg = "chore(ast): update AST code map artifact [skip ci]"

    action = self.publisher.commit_file(
        file_path=artifact_path,
        content=ast_map_content,
        commit_message=commit_msg,
        branch_name=target_branch,
    )
    return (
        f"Successfully {action} `{artifact_path}` on branch `{target_branch}`"
        f" in `{self.publisher.repo.full_name}`."
    )
