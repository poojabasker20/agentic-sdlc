import logging
import os
from pathlib import Path
from typing import Any

from google.adk.tools import ToolContext
from google.genai import types

logger = logging.getLogger(__name__)


async def save_artifact(
    tool_context: ToolContext,
    content: str,
    filename: str,
    format: str = "markdown",
) -> dict[str, Any]:
    """
    Saves text content as an ADK artifact.

    This tool takes text input and saves it as an artifact using
    the configured ArtifactService. The artifact will be versioned automatically.

    Args:
        tool_context (ToolContext): The ADK tool context providing access to
                                   artifact service methods.
        content (str): The text content to save as an artifact.
        filename (str): The name for the artifact file. The agent should choose a descriptive name.
        format (str): The format of the content. Currently supported: 'markdown'. Defaults to 'markdown'.

    Returns:
        dict[str, Any]: A dictionary containing:
            - status (str): 'success' or 'error'
            - filename (str): The name of the created artifact
            - version (int): The version number assigned to the artifact (on success)
            - message (str): A descriptive message about the operation result
            - error (str, optional): Error details if the operation failed
    """
    try:
        if not content or not filename:
            return {
                "status": "error",
                "filename": filename,
                "message": "Content and filename needs to be provided",
                "error": "Missing required parameters",
            }

        if format.lower() == "markdown":
            mime_type = "text/markdown"
            if not filename.lower().endswith(".md"):
                filename = f"{filename}.md"
        else:
            mime_type = "text/plain"

        content_bytes = content.encode("utf-8")

        artifact = types.Part.from_bytes(
            data=content_bytes, mime_type=mime_type
        )

        version = await tool_context.save_artifact(
            filename=filename, artifact=artifact
        )

        logger.info(
            f"Successfully saved artifact '{filename}' as version {version}"
        )

        return {
            "status": "success",
            "filename": filename,
            "version": version,
            "message": (
                f"Successfully saved content to artifact '{filename}' (version {version})"
            ),
        }

    except ValueError as e:
        logger.error(f"ValueError: {e!s}")
        return {
            "status": "error",
            "filename": filename,
            "message": (
                "ArtifactService not configured. Ensure artifact_service is provided to the Runner."
            ),
            "error": str(e),
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e!s}")
        return {
            "status": "error",
            "filename": filename,
            "message": (
                "An unexpected error occurred while saving the artifact"
            ),
            "error": str(e),
        }


def save_local_artifact(
    content: str,
    filename: str,
    workspace_root: str,
    format: str = "markdown",
    track_in_git: bool = False,
) -> dict[str, Any]:
    """Saves text content to a local file within the workspace.

    Args:
        content (str): The text content to save.
        filename (str): The relative path or filename for the artifact.
        workspace_root (str): The root directory of the workspace.
        format (str): The format of the content. Currently supported:
          'markdown'. Defaults to 'markdown'.
        track_in_git (bool): If True, saves directly in workspace_root without
          gitignoring. If False, saves in .agent_artifacts/ and updates
          .gitignore. Defaults to False.

    Returns:
        dict[str, Any]: A dictionary containing status, filepath, tracked, and
        message.
    """
    try:
        if not content or not filename or not workspace_root:
            return {
                "status": "error",
                "filepath": filename or "",
                "tracked": track_in_git,
                "message": (
                    "Content, filename, and workspace_root must be provided"
                ),
                "error": "Missing required parameters",
            }

        if (
            format.lower() == "markdown"
            and not filename.lower().endswith(".md")
        ):
            filename = f"{filename}.md"

        if track_in_git:
            target_path = os.path.join(workspace_root, filename)
            abs_base = os.path.realpath(workspace_root)
        else:
            artifacts_dir = os.path.join(workspace_root, ".agent_artifacts")
            target_path = os.path.join(artifacts_dir, filename)
            abs_base = os.path.realpath(artifacts_dir)

        abs_target = os.path.realpath(target_path)
        try:
            if os.path.commonpath([abs_base, abs_target]) != abs_base:
                return {
                    "status": "error",
                    "filepath": filename,
                    "tracked": track_in_git,
                    "message": (
                        "Path traversal detected outside allowed base directory"
                    ),
                    "error": "Path traversal vulnerability prevented",
                }
        except ValueError:
            return {
                "status": "error",
                "filepath": filename,
                "tracked": track_in_git,
                "message": (
                    "Path traversal detected outside allowed base directory"
                ),
                "error": "Path traversal vulnerability prevented",
            }

        if not track_in_git:
            os.makedirs(artifacts_dir, exist_ok=True)
            gitignore_path = os.path.join(workspace_root, ".gitignore")
            present = False
            if os.path.exists(gitignore_path):
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped.startswith("#"):
                            continue
                        if stripped in (
                            ".agent_artifacts",
                            ".agent_artifacts/",
                            "/.agent_artifacts",
                            "/.agent_artifacts/",
                        ):
                            present = True
                            break
            if not present:
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    f.write("\n# Agent output artifacts\n.agent_artifacts/\n")

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

        abs_filepath = os.path.abspath(target_path)
        logger.info(
            f"Successfully saved local artifact '{filename}' to '{abs_filepath}'"
        )

        return {
            "status": "success",
            "filepath": abs_filepath,
            "tracked": track_in_git,
            "message": (
                f"Successfully saved local artifact to '{abs_filepath}'"
            ),
        }

    except Exception as e:
        logger.error(
            f"Unexpected error saving local artifact '{filename}': {e!s}"
        )
        return {
            "status": "error",
            "filepath": filename,
            "tracked": track_in_git,
            "message": (
                "An unexpected error occurred while saving the local artifact"
            ),
            "error": str(e),
        }
