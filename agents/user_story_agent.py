"""Stage 1 User Story Refiner Agent runner using google-genai and GitHub."""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
from google import genai
from google.genai import types
from schemas.user_story_schema import UserStoryPayload
from tools.ast_traversal_tool import query_codebase_ast
from utils.github_publisher import GitHubPublisherService

logger = logging.getLogger(__name__)


class UserStoryRefinerAgent:

  def __init__(
      self,
      github_token: Optional[str] = None,
      repo_name: Optional[str] = None,
      gcp_project_id: Optional[str] = None,
      gcp_location: str = "global",
  ):
    token = github_token or os.getenv("GITHUB_TOKEN", "")
    sdlc_repo = repo_name or os.getenv("SDLC_GOVERNANCE_REPO", "owner/agentic-sdlc")

    self.publisher = GitHubPublisherService(token, sdlc_repo)

    skill_path = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / "sdlc-user-story-refiner"
        / "SKILL.md"
    )
    if not skill_path.exists():
      skill_path = Path("skills/sdlc-user-story-refiner/SKILL.md")

    with open(skill_path, "r", encoding="utf-8") as f:
      self.skill_instruction = f.read()

    project_id = (
        gcp_project_id
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCP_PROJECT")
        or os.getenv("GCLOUD_PROJECT")
    )
    location = os.getenv("GOOGLE_CLOUD_LOCATION") or os.getenv("GCP_LOCATION") or gcp_location

    if not project_id:
      try:
        import google.auth
        _, auth_project = google.auth.default()
        project_id = auth_project
      except Exception as auth_err:
        raise RuntimeError(
            f"Failed to detect Google Cloud credentials for GenAI agent: {auth_err}"
        ) from auth_err

    if project_id:
      try:
        self.genai_client = genai.Client(
            vertexai=True, project=project_id, location=location
        )
        logger.info(
            "Initialized Vertex AI GenAI client (project=%s, location=%s)",
            project_id,
            location,
        )
      except Exception as e:
        raise RuntimeError(
            f"Failed to initialize Vertex AI client with project='{project_id}' and location='{location}': {e}"
        ) from e
    else:
      raise ValueError("Neither Google Cloud Project ID nor GEMINI_API_KEY was provided.")

  def _invoke_llm(self, prompt: str) -> UserStoryPayload:
    candidate_models = [ "gemini-3.7-flash"]
    ast_context = query_codebase_ast()
    full_prompt = f"{prompt}\n\n[Codebase AST Context]:\n{ast_context}"

    errors = []
    for model_name in candidate_models:
      try:
        config = types.GenerateContentConfig(
            system_instruction=self.skill_instruction,
            response_mime_type="application/json",
            response_schema=UserStoryPayload,
            temperature=0.2,
        )
        response = self.genai_client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=config,
        )
        data = json.loads(response.text)
        logger.info(
            "Successfully generated User Story using model `%s`", model_name
        )
        return UserStoryPayload(**data)
      except Exception as err:
        errors.append(f"{model_name}: {err}")
        logger.warning("Model `%s` failed: %s", model_name, err)
        continue

    raise RuntimeError(
        f"User Story generation failed across all candidate models. Errors: {'; '.join(errors)}"
    )

  def run_stage(
      self, story_id: str, pm_goal: str, context_docs: str
  ) -> Dict[str, Any]:
    clean_id = re.sub(r"^story-?", "", story_id, flags=re.IGNORECASE).strip()
    norm_story_id = f"STORY-{clean_id.upper()}" if clean_id else story_id.upper()
    branch_name = f"feature/story-{clean_id.lower()}" if clean_id else f"feature/{story_id.lower()}"
    file_path = f"user-stories/{norm_story_id}.md"

    existing_pr = self.publisher.get_open_pr_for_branch(branch_name)

    if not existing_pr:
      return self._run_create_mode(
          norm_story_id, pm_goal, context_docs, branch_name, file_path
      )
    else:
      return self._run_revise_mode(
          existing_pr, norm_story_id, pm_goal, context_docs, branch_name, file_path
      )

  def _run_create_mode(
      self,
      story_id: str,
      pm_goal: str,
      context_docs: str,
      branch_name: str,
      file_path: str,
  ) -> Dict[str, Any]:
    self.publisher.create_branch_if_not_exists(branch_name, base_branch="main")

    prompt = f"""
        [CREATE MODE] Generate initial User Story for ID: {story_id}
        
        PM Goal:
        {pm_goal}
        
        Parsed Architecture & Governance Context:
        {context_docs}
        """

    payload: UserStoryPayload = self._invoke_llm(prompt)

    commit_msg = f"docs({story_id}): generate initial user story specification"
    self.publisher.commit_file(
        file_path=file_path,
        content=payload.rendered_markdown,
        commit_message=commit_msg,
        branch_name=branch_name,
    )

    pr_body = (
        f"## Agentic SDLC - Stage 1: User Story Draft\n\n"
        f"**Story ID:** `{payload.story_id}`\n"
        f"**Title:** {payload.title}\n\n"
        f"### Overview\n"
        f"**As a** {payload.persona}\n"
        f"**I want to** {payload.action}\n"
        f"**So that** {payload.benefit}\n\n"
        f"---\n"
        f"Please review `{file_path}` and leave comments on open questions."
    )

    pr = self.publisher.create_pull_request(
        title=f"docs({story_id}): {payload.title}",
        body=pr_body,
        head_branch=branch_name,
        base_branch="main",
    )

    return {
        "status": "AWAITING_HUMAN_REVIEW",
        "pr_number": pr.number,
        "pr_url": pr.html_url,
        "mode": "CREATE",
    }

  def _run_revise_mode(
      self,
      pr: Any,
      story_id: str,
      pm_goal: str,
      context_docs: str,
      branch_name: str,
      file_path: str,
  ) -> Dict[str, Any]:
    target_branch = pr.head.ref or branch_name
    comments = self.publisher.fetch_pr_comments(pr)
    if not comments:
      return {"status": "NO_NEW_COMMENTS", "pr_number": pr.number}

    current_file = self.publisher.repo.get_contents(
        file_path, ref=target_branch
    )
    current_markdown = current_file.decoded_content.decode("utf-8")

    comments_str = "\n".join(f"- {c}" for c in comments)

    prompt = f"""
        [REVISE MODE] Refine existing User Story for ID: {story_id}
        
        PM Goal:
        {pm_goal}
        
        Current Story Markdown:
        {current_markdown}
        
        Human PR Reviewer Comments:
        {comments_str}
        
        Architecture & Governance Context:
        {context_docs}
        """

    payload: UserStoryPayload = self._invoke_llm(prompt)

    commit_msg = (
        f"docs({story_id}): update user story based on PR review feedback"
    )
    self.publisher.commit_file(
        file_path=file_path,
        content=payload.rendered_markdown,
        commit_message=commit_msg,
        branch_name=target_branch,
    )

    pr.create_issue_comment(
        "🤖 **User Story Updated Based on Feedback**\n\n"
        f"**Revision Summary:**\n{payload.revision_changelog or 'Incorporated requested updates.'}\n\n"
        f"Please review the latest commit on branch `{target_branch}`."
    )

    return {
        "status": "REVISED_AWAITING_REVIEW",
        "pr_number": pr.number,
        "pr_url": pr.html_url,
        "mode": "REVISE",
    }
