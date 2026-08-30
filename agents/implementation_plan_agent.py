"""Stage 3 Implementation Plan Generator Agent runner using google-genai and GitHub."""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
from google import genai
from google.genai import types
from schemas.implementation_plan_schema import ImplementationPlanPayload
from tools.ast_traversal_tool import query_codebase_ast
from utils.github_publisher import GitHubPublisherService


class ImplementationPlanGeneratorAgent:

  def __init__(
      self,
      github_token: Optional[str] = None,
      repo_name: Optional[str] = None,
      target_codebase_repo: Optional[str] = None,
      gcp_project_id: Optional[str] = None,
      gcp_location: str = "europe-west1",
  ):
    token = github_token or os.getenv("GITHUB_TOKEN", "")
    sdlc_repo = repo_name or os.getenv("SDLC_GOVERNANCE_REPO", "owner/agentic-sdlc")
    self.target_codebase_repo = (
        target_codebase_repo
        or os.getenv("TARGET_CODEBASE_REPO", "poojabasker20/springboot-hello-world")
    )

    self.publisher = GitHubPublisherService(token, sdlc_repo)

    skill_path = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / "sdlc-implementation-plan-generator"
        / "SKILL.md"
    )
    if not skill_path.exists():
      skill_path = Path("skills/sdlc-implementation-plan-generator/SKILL.md")

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
            f"Failed to detect Google Cloud credentials for Implementation Plan Generator: {auth_err}"
        ) from auth_err

    if project_id:
      try:
        self.genai_client = genai.Client(
            vertexai=True, project=project_id, location=location
        )
        print(f"Initialized Vertex AI GenAI client (project={project_id}, location={location})")
      except Exception as e:
        raise RuntimeError(
            f"Failed to initialize Vertex AI client with project='{project_id}' and location='{location}': {e}"
        ) from e
    else:
      raise ValueError("Neither Google Cloud Project ID nor GEMINI_API_KEY was provided.")

  def _invoke_llm(self, prompt: str) -> ImplementationPlanPayload:
    candidate_models = ["gemini-3.7-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
    ast_context = query_codebase_ast()
    full_prompt = f"{prompt}\n\n[Codebase AST Context]:\n{ast_context}"

    errors = []
    for model_name in candidate_models:
      try:
        config = types.GenerateContentConfig(
            system_instruction=self.skill_instruction,
            response_mime_type="application/json",
            response_schema=ImplementationPlanPayload,
            temperature=0.2,
        )
        response = self.genai_client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=config,
        )
        data = json.loads(response.text)
        print(f"Successfully generated Implementation Plan using model `{model_name}`")
        return ImplementationPlanPayload(**data)
      except Exception as err:
        errors.append(f"{model_name}: {err}")
        print(f"Model `{model_name}` failed: {err}")
        continue

    raise RuntimeError(
        f"Implementation Plan generation failed across all candidate models. Errors: {'; '.join(errors)}"
    )

  def run_stage(
      self,
      story_id: str,
      subtask_id: str,
      subtasks_content: str,
      story_content: str,
      context_docs: str,
  ) -> Dict[str, Any]:
    clean_story_id = re.sub(r"^story-?", "", story_id, flags=re.IGNORECASE).strip()
    norm_story_id = f"STORY-{clean_story_id.upper()}" if clean_story_id else story_id.upper()

    clean_subtask = re.sub(r"^subtask-?", "", subtask_id, flags=re.IGNORECASE).strip()
    norm_subtask_id = f"SUBTASK-{clean_subtask.upper()}" if clean_subtask else subtask_id.upper()

    branch_name = f"feature/plan-{norm_subtask_id.lower()}"
    file_path = f"implementation-plans/{norm_story_id}/{norm_subtask_id}/plan.md"

    if not story_content or not story_content.strip():
      raise FileNotFoundError(
          f"Parent User Story specification for '{norm_story_id}' is missing or empty. "
          f"Expected 'user-stories/{norm_story_id}.md'."
      )

    if not subtasks_content or not subtasks_content.strip():
      raise FileNotFoundError(
          f"Subtask plan for '{norm_story_id}' is missing or empty. "
          f"Expected 'tasks/{norm_story_id}/subtasks.md'."
      )

    existing_pr = self.publisher.get_open_pr_for_branch(branch_name)

    if not existing_pr:
      return self._run_create_mode(
          norm_story_id,
          norm_subtask_id,
          subtasks_content,
          story_content,
          context_docs,
          branch_name,
          file_path,
      )
    else:
      return self._run_revise_mode(
          existing_pr,
          norm_story_id,
          norm_subtask_id,
          subtasks_content,
          story_content,
          context_docs,
          branch_name,
          file_path,
      )

  def _run_create_mode(
      self,
      story_id: str,
      subtask_id: str,
      subtasks_content: str,
      story_content: str,
      context_docs: str,
      branch_name: str,
      file_path: str,
  ) -> Dict[str, Any]:
    self.publisher.create_branch_if_not_exists(branch_name, base_branch="main")

    prompt = f"""
        [CREATE MODE] Generate Detailed Technical Implementation Blueprint
        Target Subtask ID: {subtask_id}
        Parent Story ID: {story_id}
        Target Codebase Repository: {self.target_codebase_repo}
        
        Subtasks Plan:
        {subtasks_content}
        
        Parent User Story Specification:
        {story_content}
        
        Architecture & Governance Context:
        {context_docs}
        """

    payload: ImplementationPlanPayload = self._invoke_llm(prompt)

    commit_msg = f"docs({subtask_id}-plan): generate technical implementation blueprint"
    self.publisher.commit_file(
        file_path=file_path,
        content=payload.rendered_markdown,
        commit_message=commit_msg,
        branch_name=branch_name,
    )

    pr_body = (
        f"## Agentic SDLC - Stage 3: Implementation Blueprint\n\n"
        f"**Subtask ID:** `{payload.subtask_id}`\n"
        f"**Title:** {payload.subtask_title}\n"
        f"**Parent Story ID:** `{payload.parent_story_id}`\n"
        f"**Target Codebase:** `{payload.target_repository}`\n"
        f"**Estimated Scope:** {payload.estimated_scope}\n\n"
        f"### Executive Summary\n{payload.executive_summary}\n\n"
        f"### File Delta Matrix ({len(payload.affected_files_delta)} files)\n"
    )
    for af in payload.affected_files_delta:
      pr_body += f"- `{af.file_path}` (**{af.action}** - {af.layer_component}): {af.description_of_changes}\n"
    pr_body += f"\n---\nPlease review `{file_path}`."

    pr = self.publisher.create_pull_request(
        title=f"docs({subtask_id}-plan): detailed implementation blueprint",
        body=pr_body,
        head_branch=branch_name,
        base_branch="main",
    )

    return {
        "status": "AWAITING_HUMAN_REVIEW",
        "pr_number": pr.number,
        "pr_url": pr.html_url,
        "mode": "CREATE",
        "files_count": len(payload.affected_files_delta),
    }

  def _run_revise_mode(
      self,
      pr: Any,
      story_id: str,
      subtask_id: str,
      subtasks_content: str,
      story_content: str,
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
        [REVISE MODE] Refine Technical Implementation Blueprint for Subtask: {subtask_id}
        Parent Story ID: {story_id}
        Target Codebase Repository: {self.target_codebase_repo}
        
        Current Implementation Blueprint Markdown:
        {current_markdown}
        
        Subtasks Plan:
        {subtasks_content}
        
        Parent User Story Specification:
        {story_content}
        
        Reviewer Comments & Verifier Audit Feedback:
        {comments_str}
        
        Architecture & Governance Context:
        {context_docs}
        """

    payload: ImplementationPlanPayload = self._invoke_llm(prompt)

    commit_msg = (
        f"docs({subtask_id}-plan): update implementation blueprint based on review"
    )
    self.publisher.commit_file(
        file_path=file_path,
        content=payload.rendered_markdown,
        commit_message=commit_msg,
        branch_name=target_branch,
    )

    pr.create_issue_comment(
        "**Implementation Blueprint Updated Based on Feedback**\n\n"
        f"**Revision Summary:**\n{payload.revision_changelog or 'Incorporated requested revisions and audit findings.'}\n\n"
        f"Please review the latest commit on branch `{target_branch}`."
    )

    return {
        "status": "REVISED_AWAITING_REVIEW",
        "pr_number": pr.number,
        "pr_url": pr.html_url,
        "mode": "REVISE",
        "files_count": len(payload.affected_files_delta),
    }
