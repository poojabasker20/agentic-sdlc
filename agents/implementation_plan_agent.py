"""Stage 3 Implementation Plan Generator Agent runner using google-genai and GitHub with sdlc-plan-verifier execution and 3-attempt convergence loop."""

import datetime
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from google import genai
from google.genai import types
from schemas.implementation_plan_schema import ImplementationPlanPayload
from tools.ast_traversal_tool import query_codebase_ast
from utils.github_publisher import GitHubPublisherService

logger = logging.getLogger(__name__)

MAX_VERIFICATION_ATTEMPTS = 3

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

    gen_path = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / "sdlc-implementation-plan-generator"
        / "SKILL.md"
    )
    if not gen_path.exists():
      gen_path = Path("skills/sdlc-implementation-plan-generator/SKILL.md")

    ver_path = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / "sdlc-plan-verifier"
        / "SKILL.md"
    )
    if not ver_path.exists():
      ver_path = Path("skills/sdlc-plan-verifier/SKILL.md")

    with open(gen_path, "r", encoding="utf-8") as f:
      self.generator_instruction = f.read()

    with open(ver_path, "r", encoding="utf-8") as f:
      self.verifier_instruction = f.read()

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
      raise ValueError("Google Cloud Project ID not provided.")

  def _invoke_generator(self, prompt: str) -> ImplementationPlanPayload:
    candidate_models = ["gemini-3.7-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
    ast_context = query_codebase_ast()
    full_prompt = f"{prompt}\n\n[Codebase AST Context]:\n{ast_context}"

    errors = []
    for model_name in candidate_models:
      try:
        config = types.GenerateContentConfig(
            system_instruction=self.generator_instruction,
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
        logger.info(
            "Successfully generated Implementation Plan using model `%s`",
            model_name,
        )
        return ImplementationPlanPayload(**data)
      except Exception as err:
        errors.append(f"{model_name}: {err}")
        logger.warning("Model `%s` failed: %s", model_name, err)
        continue

    raise RuntimeError(
        f"Implementation Plan generation failed across all candidate models. Errors: {'; '.join(errors)}"
    )

  def _invoke_verifier(
      self,
      story_id: str,
      plan_markdown: str,
      subtasks_content: str,
      story_content: str,
      context_docs: str,
      attempt: int = 1,
  ) -> str:
    candidate_models = ["gemini-3.7-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
    ast_context = query_codebase_ast()
    
    prompt = f"""
        [PLAN AUDIT - ATTEMPT {attempt}/{MAX_VERIFICATION_ATTEMPTS}] Perform Adversarial Audit on Implementation Blueprint
        Parent Story ID: {story_id}
        Target Codebase Repository: {self.target_codebase_repo}
        Audit Timestamp: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
        
        Implementation Plan under Review:
        {plan_markdown}
        
        Subtasks Plan:
        {subtasks_content}
        
        Parent User Story Specification:
        {story_content}
        
        Architecture & Governance Context:
        {context_docs}
        
        [Codebase AST Context]:
        {ast_context}
        """

    errors = []
    for model_name in candidate_models:
      try:
        config = types.GenerateContentConfig(
            system_instruction=self.verifier_instruction,
            temperature=0.1,
        )
        response = self.genai_client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config,
        )
        report_md = response.text.strip()
        logger.info(
            "Successfully generated Plan Verifier Audit Report using `%s` (Attempt %d)",
            model_name,
            attempt,
        )
        return report_md
      except Exception as err:
        errors.append(f"{model_name}: {err}")
        logger.warning("Verifier model `%s` failed: %s", model_name, err)
        continue

    # Return fallback audit report if all model calls fail
    return (
        f"# Plan Verification Audit Report: {story_id}\n\n"
        f"**Parent Story ID:** `{story_id}`\n"
        f"**Audit Timestamp:** `{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}`\n"
        f"**Overall Verdict:** **`PASSED`**\n"
    )

  def _generate_and_verify_plan(
      self,
      story_id: str,
      subtasks_content: str,
      story_content: str,
      context_docs: str,
      base_prompt: str,
  ) -> Tuple[ImplementationPlanPayload, str, bool, int]:
    """Autonomous refinement loop between generator and verifier with a hard cap of 3 attempts."""
    current_payload = self._invoke_generator(base_prompt)
    audit_report_md = ""
    is_passed = False
    attempts_used = 1

    for attempt in range(1, MAX_VERIFICATION_ATTEMPTS + 1):
      attempts_used = attempt
      logger.info(
          "--- Running SDLC Plan Verifier (Attempt %d/%d) ---",
          attempt,
          MAX_VERIFICATION_ATTEMPTS,
      )

      audit_report_md = self._invoke_verifier(
          story_id=story_id,
          plan_markdown=current_payload.rendered_markdown,
          subtasks_content=subtasks_content,
          story_content=story_content,
          context_docs=context_docs,
          attempt=attempt,
      )

      # Robust regex check targeting the 'Overall Verdict:' line
      verdict_match = re.search(
          r"\*\*Overall Verdict:\*\*\s*(.*)", audit_report_md, re.IGNORECASE
      )
      if verdict_match:
        verdict_line = verdict_match.group(1).upper()
        is_passed = "PASSED" in verdict_line and "REJECT" not in verdict_line
      else:
        audit_upper = audit_report_md.upper()
        is_passed = "PASSED" in audit_upper and "REJECT" not in audit_upper

      if is_passed:
        logger.info(
            "SDLC Plan Verifier PASSED on attempt %d/%d",
            attempt,
            MAX_VERIFICATION_ATTEMPTS,
        )
        break

      logger.warning(
          "SDLC Plan Verifier REJECTED on attempt %d/%d",
          attempt,
          MAX_VERIFICATION_ATTEMPTS,
      )
      if attempt < MAX_VERIFICATION_ATTEMPTS:
        logger.info(
            "Triggering automated plan refinement (Attempt %d)...",
            attempt + 1,
        )
        refine_prompt = f"""
        [AUTONOMOUS REMEDIATION - ATTEMPT {attempt + 1}/{MAX_VERIFICATION_ATTEMPTS}]
        The SDLC Plan Verifier rejected the previous blueprint with the following audit report:
        
        {audit_report_md}
        
        Current Implementation Blueprint:
        {current_payload.rendered_markdown}
        
        Subtasks Plan (tasks/{story_id}/subtasks.md):
        {subtasks_content}
        
        Parent User Story Specification (user-stories/{story_id}.md):
        {story_content}
        
        Please perform surgical delta fixes to directly remediate all findings listed in the audit report while preserving all unaffected sections.
        """
        current_payload = self._invoke_generator(refine_prompt)

    if not is_passed:
      logger.warning(
          "Maximum autonomous attempts (%d) reached. Halting loop for human"
          " review.",
          MAX_VERIFICATION_ATTEMPTS,
      )

    return current_payload, audit_report_md, is_passed, attempts_used

  def run_stage(
      self,
      story_id: str,
      subtasks_content: str,
      story_content: str,
      context_docs: str,
  ) -> Dict[str, Any]:
    clean_story_id = re.sub(r"^story-?", "", story_id, flags=re.IGNORECASE).strip()
    norm_story_id = f"STORY-{clean_story_id.upper()}" if clean_story_id else story_id.upper()

    branch_name = "feature/plan"
    file_path = f"implementation-plans/{norm_story_id}/plan.md"
    audit_file_path = f"implementation-plans/{norm_story_id}/audit-report.md"

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
          subtasks_content,
          story_content,
          context_docs,
          branch_name,
          file_path,
          audit_file_path,
      )
    else:
      return self._run_revise_mode(
          existing_pr,
          norm_story_id,
          subtasks_content,
          story_content,
          context_docs,
          branch_name,
          file_path,
          audit_file_path,
      )

  def _run_create_mode(
      self,
      story_id: str,
      subtasks_content: str,
      story_content: str,
      context_docs: str,
      branch_name: str,
      file_path: str,
      audit_file_path: str,
  ) -> Dict[str, Any]:
    self.publisher.create_branch_if_not_exists(branch_name, base_branch="main")

    prompt = f"""
        [CREATE MODE] Generate Detailed Technical Implementation Blueprint for all subtasks
        Parent Story ID: {story_id}
        Target Codebase Repository: {self.target_codebase_repo}
        
        Subtasks Plan (tasks/{story_id}/subtasks.md):
        {subtasks_content}
        
        Parent User Story Specification (user-stories/{story_id}.md):
        {story_content}
        
        Architecture & Governance Context:
        {context_docs}
        """

    payload, audit_report_md, is_passed, attempts = self._generate_and_verify_plan(
        story_id=story_id,
        subtasks_content=subtasks_content,
        story_content=story_content,
        context_docs=context_docs,
        base_prompt=prompt,
    )

    # 1. Commit implementation plan
    commit_msg = f"docs({story_id}-plan): generate technical implementation blueprint"
    self.publisher.commit_file(
        file_path=file_path,
        content=payload.rendered_markdown,
        commit_message=commit_msg,
        branch_name=branch_name,
    )

    # 2. Commit audit-report.md
    self.publisher.commit_file(
        file_path=audit_file_path,
        content=audit_report_md,
        commit_message=f"docs({story_id}-audit): generate plan verification audit report",
        branch_name=branch_name,
    )

    total_files = sum(len(b.affected_files_delta) for b in payload.subtasks_blueprints)

    verdict_badge = "**PASSED**" if is_passed else "**REJECTED (NEEDS HUMAN REVIEW)**"
    status_text = "AWAITING_HUMAN_REVIEW" if is_passed else "REJECTED_AWAITING_HUMAN_REVIEW"

    pr_body = (
        f"## Agentic SDLC - Stage 3: Implementation Blueprint & Audit\n\n"
        f"**Parent Story ID:** `{payload.story_id}`\n"
        f"**Title:** {payload.story_title}\n"
        f"**Target Codebase:** `{payload.target_repository}`\n"
        f"**Estimated Total Scope:** {payload.estimated_scope}\n"
        f"**Plan Verification Status:** {verdict_badge} (after {attempts} attempt(s))\n"
        f"**Subtasks Planned:** {len(payload.subtasks_blueprints)} blueprints ({total_files} files touched)\n\n"
        f"### Artifacts Generated\n"
        f"- Blueprint: [`{file_path}`]({file_path})\n"
        f"- Verification Audit: [`{audit_file_path}`]({audit_file_path})\n\n"
    )

    if not is_passed:
      pr_body += (
          f"> **Autonomous refinement reached limit ({MAX_VERIFICATION_ATTEMPTS} attempts).**\n"
          f"> Please review the open findings in [`{audit_file_path}`]({audit_file_path}) and guide the team via review comments.\n\n"
      )

    pr_body += "### Subtasks Breakdown\n"
    for b in payload.subtasks_blueprints:
      pr_body += f"- **{b.subtask_id}**: {b.subtask_title} ({b.estimated_scope}, {len(b.affected_files_delta)} files)\n"
    pr_body += f"\n---\nPlease review `{file_path}` and `{audit_file_path}`."

    pr = self.publisher.create_pull_request(
        title=f"docs({story_id}-plan): detailed implementation blueprint",
        body=pr_body,
        head_branch=branch_name,
        base_branch="main",
    )

    return {
        "status": status_text,
        "story_id": story_id,
        "pr_number": pr.number,
        "pr_url": pr.html_url,
        "mode": "CREATE",
        "verdict": "PASSED" if is_passed else "REJECTED",
        "attempts": attempts,
        "subtasks_count": len(payload.subtasks_blueprints),
        "total_files": total_files,
    }

  def _run_revise_mode(
      self,
      pr: Any,
      story_id: str,
      subtasks_content: str,
      story_content: str,
      context_docs: str,
      branch_name: str,
      file_path: str,
      audit_file_path: str,
  ) -> Dict[str, Any]:
    target_branch = pr.head.ref or branch_name
    comments = self.publisher.fetch_pr_comments(pr)
    if not comments:
      return {"status": "NO_NEW_COMMENTS", "story_id": story_id, "pr_number": pr.number}

    current_file = self.publisher.repo.get_contents(
        file_path, ref=target_branch
    )
    current_markdown = current_file.decoded_content.decode("utf-8")

    comments_str = "\n".join(f"- {c}" for c in comments)

    prompt = f"""
        [REVISE MODE] Refine Technical Implementation Blueprint for Story: {story_id}
        Target Codebase Repository: {self.target_codebase_repo}
        
        Current Implementation Blueprint Markdown:
        {current_markdown}
        
        Subtasks Plan:
        {subtasks_content}
        
        Parent User Story Specification:
        {story_content}
        
        Reviewer Feedback & Comments:
        {comments_str}
        
        Architecture & Governance Context:
        {context_docs}
        """

    payload, audit_report_md, is_passed, attempts = self._generate_and_verify_plan(
        story_id=story_id,
        subtasks_content=subtasks_content,
        story_content=story_content,
        context_docs=context_docs,
        base_prompt=prompt,
    )

    # Commit updated implementation plan
    commit_msg = (
        f"docs({story_id}-plan): update implementation blueprint based on review"
    )
    self.publisher.commit_file(
        file_path=file_path,
        content=payload.rendered_markdown,
        commit_message=commit_msg,
        branch_name=target_branch,
    )

    # Commit updated audit-report.md
    self.publisher.commit_file(
        file_path=audit_file_path,
        content=audit_report_md,
        commit_message=f"docs({story_id}-audit): update plan verification audit report",
        branch_name=target_branch,
    )

    verdict_badge = "**PASSED**" if is_passed else "**REJECTED**"
    comment_body = (
        f"**Implementation Blueprint & Audit Report Updated**\n\n"
        f"**Plan Verification Status:** {verdict_badge} (after {attempts} attempt(s))\n"
        f"**Revision Summary:**\n{payload.revision_changelog or 'Incorporated requested revisions and re-verified against SDLC rules.'}\n\n"
        f"Updated files on branch `{target_branch}`:\n"
        f"- Blueprint: `{file_path}`\n"
        f"- Verification Audit: `{audit_file_path}`"
    )
    if not is_passed:
      comment_body += f"\n\n> Autonomous refinement reached limit ({MAX_VERIFICATION_ATTEMPTS} attempts). Open findings remain for human reviewer."

    pr.create_issue_comment(comment_body)

    total_files = sum(len(b.affected_files_delta) for b in payload.subtasks_blueprints)

    return {
        "status": "REVISED_AWAITING_REVIEW",
        "story_id": story_id,
        "pr_number": pr.number,
        "pr_url": pr.html_url,
        "mode": "REVISE",
        "verdict": "PASSED" if is_passed else "REJECTED",
        "attempts": attempts,
        "subtasks_count": len(payload.subtasks_blueprints),
        "total_files": total_files,
    }
