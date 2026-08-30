"""SDLC Plan Verifier Agent runner using google-genai and GitHub."""

import datetime
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
from google import genai
from google.genai import types
from schemas.plan_verifier_schema import PlanVerifierPayload
from tools.ast_traversal_tool import query_codebase_ast
from utils.github_publisher import GitHubPublisherService


class PlanVerifierAgent:

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
        / "sdlc-plan-verifier"
        / "SKILL.md"
    )
    if not skill_path.exists():
      skill_path = Path("skills/sdlc-plan-verifier/SKILL.md")

    with open(skill_path, "r", encoding="utf-8") as f:
      self.skill_instruction = f.read()

    project_id = (
        gcp_project_id
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCP_PROJECT")
        or os.getenv("GCLOUD_PROJECT")
    )
    location = os.getenv("GOOGLE_CLOUD_LOCATION") or os.getenv("GCP_LOCATION") or gcp_location

    if not project_id and not os.getenv("GEMINI_API_KEY"):
      try:
        import google.auth
        _, auth_project = google.auth.default()
        project_id = auth_project
      except Exception as auth_err:
        raise RuntimeError(
            f"Failed to detect Google Cloud credentials for Plan Verifier: {auth_err}"
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
    elif os.getenv("GEMINI_API_KEY"):
      try:
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        print("Initialized GenAI client with GEMINI_API_KEY")
      except Exception as e:
        raise RuntimeError(
            f"Failed to initialize GenAI client with GEMINI_API_KEY: {e}"
        ) from e
    else:
      raise ValueError("Neither Google Cloud Project ID nor GEMINI_API_KEY was provided.")

  def _invoke_llm(self, prompt: str) -> PlanVerifierPayload:
    candidate_models = ["gemini-3.7-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
    ast_context = query_codebase_ast()
    full_prompt = f"{prompt}\n\n[Codebase AST Context]:\n{ast_context}"

    errors = []
    for model_name in candidate_models:
      try:
        config = types.GenerateContentConfig(
            system_instruction=self.skill_instruction,
            response_mime_type="application/json",
            response_schema=PlanVerifierPayload,
            temperature=0.1,  # Strict, deterministic adversarial evaluation
        )
        response = self.genai_client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=config,
        )
        data = json.loads(response.text)
        print(f"Successfully audited Implementation Plan using model `{model_name}`")
        return PlanVerifierPayload(**data)
      except Exception as err:
        errors.append(f"{model_name}: {err}")
        print(f"Model `{model_name}` failed: {err}")
        continue

    raise RuntimeError(
        f"Plan verification audit failed across all candidate models. Errors: {'; '.join(errors)}"
    )

  def run_audit(
      self,
      story_id: str,
      subtask_id: str,
      plan_content: str,
      subtasks_content: str,
      story_content: str,
      context_docs: str,
      pr_number: Optional[int] = None,
  ) -> Dict[str, Any]:
    clean_story_id = re.sub(r"^story-?", "", story_id, flags=re.IGNORECASE).strip()
    norm_story_id = f"STORY-{clean_story_id.upper()}" if clean_story_id else story_id.upper()

    clean_subtask = re.sub(r"^subtask-?", "", subtask_id, flags=re.IGNORECASE).strip()
    norm_subtask_id = f"SUBTASK-{clean_subtask.upper()}" if clean_subtask else subtask_id.upper()

    branch_name = f"feature/plan-{norm_subtask_id.lower()}"
    report_file_path = f"docs/audits/{norm_subtask_id}-verifier-report.md"

    prompt = f"""
        [PLAN AUDIT] Perform Adversarial Audit on Implementation Blueprint
        Target Subtask ID: {norm_subtask_id}
        Parent Story ID: {norm_story_id}
        Target Codebase Repository: {self.target_codebase_repo}
        Audit Timestamp: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
        
        Implementation Plan under Review:
        {plan_content}
        
        Subtasks Plan:
        {subtasks_content}
        
        Parent User Story Specification:
        {story_content}
        
        Architecture & Governance Context:
        {context_docs}
        """

    payload: PlanVerifierPayload = self._invoke_llm(prompt)

    # Commit audit report artifact to branch
    commit_msg = f"docs({norm_subtask_id}-audit): save plan verification audit report"
    self.publisher.commit_file(
        file_path=report_file_path,
        content=payload.rendered_markdown,
        commit_message=commit_msg,
        branch_name=branch_name,
    )

    # Post comment / review status to PR if PR exists
    pr = None
    if pr_number:
      try:
        pr = self.publisher.repo.get_pull(pr_number)
      except Exception:
        pass
    if not pr:
      pr = self.publisher.get_open_pr_for_branch(branch_name)

    if pr:
      verdict_icon = "✅" if payload.overall_verdict == "PASSED" else "⚠️"
      comment_text = (
          f"### {verdict_icon} Plan Verification Audit: `{payload.overall_verdict}` (Score: {payload.verification_score}/100)\n\n"
          f"**Target Subtask:** `{norm_subtask_id}`\n\n"
          f"#### Assessment Summary\n{payload.executive_summary}\n\n"
          f"#### Verification Checklist\n"
          f"- [{'x' if payload.surgical_editing_compliant else ' '}] Surgical Boundaries (<10 files, <400 LOC)\n"
          f"- [{'x' if payload.dependency_dag_valid else ' '}] Dependency DAG Integrity\n"
          f"- [{'x' if payload.rollback_handling_valid else ' '}] Rollback & Failure States\n"
          f"- [{'x' if payload.ast_integrity_confirmed else ' '}] AST Path Integrity\n"
          f"- [{'x' if payload.bdd_coverage_complete else ' '}] 100% BDD Acceptance Criteria Coverage\n\n"
          f"Full audit report saved to [`{report_file_path}`](https://github.com/{self.publisher.repo.full_name}/blob/{branch_name}/{report_file_path})."
      )

      if payload.overall_verdict != "PASSED" and payload.remediation_action_plan:
        comment_text += "\n\n#### Required Remediation Items:\n"
        for idx, rem in enumerate(payload.remediation_action_plan, 1):
          comment_text += f"{idx}. {rem}\n"

      pr.create_issue_comment(comment_text)

    return {
        "status": payload.overall_verdict,
        "verdict": payload.overall_verdict,
        "score": payload.verification_score,
        "subtask_id": norm_subtask_id,
        "findings_count": len(payload.findings),
        "report_path": report_file_path,
    }
